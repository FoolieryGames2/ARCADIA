from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from arcadia.core.artifact_envelope import ArtifactBasisRef, ArtifactEnvelope, RecipeId
from arcadia.core.canonical_json import JsonValue
from arcadia.core.config import StorageConfig
from arcadia.core.hashing import Sha256Digest, sha256_canonical_json, sha256_text
from arcadia.core.ids import AliasKind, CanonicalId, ScopedAlias
from arcadia.storage.artifact_repository import (
    MAX_TURN_ARTIFACT_REVISIONS,
    ArtifactConflictError,
    ArtifactNotFoundError,
    ArtifactRepository,
    ArtifactRepositoryError,
    ArtifactRepositoryFieldError,
    ArtifactRepositoryIntegrityError,
)
from arcadia.storage.connection import SQLiteConnectionFactory
from arcadia.storage.migrations import MigrationRunner
from arcadia.storage.transcript_repository import TranscriptRepository

NOW = datetime(2026, 8, 30, 12, 0, tzinfo=UTC)


def _factory(root: Path) -> SQLiteConnectionFactory:
    return SQLiteConnectionFactory(
        workspace_root=root,
        storage=StorageConfig(
            data_dir="data",
            database_name="artifacts.sqlite3",
            busy_timeout_ms=1000,
            require_fts5=True,
        ),
    )


def _repository(
    root: Path, *, project_id: CanonicalId | None = None
) -> ArtifactRepository:
    factory = _factory(root)
    with factory.connect() as connection:
        MigrationRunner().migrate(connection, applied_at=NOW)
    return ArtifactRepository(factory, project_id or CanonicalId.new())


def _turn(
    repository: ArtifactRepository, *, at: datetime = NOW
) -> CanonicalId:
    transcript = TranscriptRepository(repository.factory, repository.project_id)
    conversation_id = CanonicalId.new()
    turn_id = CanonicalId.new()
    transcript.create_conversation(conversation_id=conversation_id, created_at=at)
    transcript.append_user_turn(
        conversation_id=conversation_id,
        turn_id=turn_id,
        content="artifact authority fixture",
        created_at=at,
    )
    return turn_id


def _artifact(
    repository: ArtifactRepository,
    turn_id: CanonicalId,
    *,
    at: datetime = NOW,
    payload: JsonValue | None = None,
    recipe_id: RecipeId = RecipeId.INTENT,
    artifact_type: str = "INTENT",
    basis_refs: tuple[ArtifactBasisRef, ...] = (),
) -> ArtifactEnvelope:
    return ArtifactEnvelope.create(
        project_id=repository.project_id,
        turn_id=turn_id,
        recipe_id=recipe_id,
        artifact_type=artifact_type,
        short_id=ScopedAlias(turn_id, AliasKind.REQUIREMENT, 1),
        revision=1,
        project_version="0.1",
        contract_version="contract-v1",
        schema_version="schema-v1",
        recipe_version="recipe-v1",
        registry_version="registry-v1",
        runtime_identity_version="runtime-v1",
        created_at=at,
        payload={"value": "first"} if payload is None else payload,
        basis_refs=basis_refs,
    )


def _revision(
    source: ArtifactEnvelope,
    *,
    revision: int,
    at: datetime,
    payload: JsonValue,
    project_id: CanonicalId | None = None,
    turn_id: CanonicalId | None = None,
    recipe_id: RecipeId | None = None,
    artifact_type: str | None = None,
    basis_refs: tuple[ArtifactBasisRef, ...] = (),
    short_id_ordinal: int | None = None,
) -> ArtifactEnvelope:
    value = source.to_value()
    value["project_uuid"] = str(project_id or source.project_id)
    value["turn_uuid"] = str(turn_id or source.turn_id)
    value["recipe_id"] = (recipe_id or source.recipe_id).value
    value["artifact_type"] = artifact_type or source.artifact_type
    if short_id_ordinal is not None:
        value["short_id"] = f"R{short_id_ordinal:03d}"
    value["revision"] = revision
    value["created_at"] = at.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    value["basis_refs"] = [item.to_value() for item in basis_refs]
    value["payload"] = payload
    value["content_hash"] = sha256_canonical_json(payload).value
    unsigned = dict(value)
    unsigned.pop("artifact_hash")
    value["artifact_hash"] = sha256_canonical_json(unsigned).value
    return ArtifactEnvelope.from_value(value)


def test_repository_requires_current_migrated_schema(tmp_path: Path) -> None:
    factory = _factory(tmp_path)
    with factory.connect():
        pass
    repository = ArtifactRepository(factory, CanonicalId.new())
    with pytest.raises(ArtifactRepositoryError, match="schema is not current"):
        repository.load_latest(artifact_id=CanonicalId.new())


def test_repository_identity_is_strict_and_immutable(tmp_path: Path) -> None:
    factory = _factory(tmp_path)
    with pytest.raises(ArtifactRepositoryFieldError, match="factory"):
        ArtifactRepository(object(), CanonicalId.new())  # type: ignore[arg-type]
    with pytest.raises(ArtifactRepositoryFieldError, match="project_id"):
        ArtifactRepository(factory, "project")  # type: ignore[arg-type]
    repository = _repository(tmp_path)
    with pytest.raises(FrozenInstanceError):
        repository.project_id = CanonicalId.new()  # type: ignore[misc]


def test_store_first_revision_and_exact_loads(tmp_path: Path) -> None:
    repository = _repository(tmp_path)
    turn_id = _turn(repository)
    envelope = _artifact(repository, turn_id)

    stored = repository.store(envelope, expected_latest_revision=0)

    assert stored == envelope
    assert repository.load(artifact_id=envelope.artifact_id, revision=1) == envelope
    assert repository.load_latest(artifact_id=envelope.artifact_id) == envelope


def test_exact_retry_is_idempotent_even_after_head_expectation_is_stale(
    tmp_path: Path,
) -> None:
    repository = _repository(tmp_path)
    envelope = _artifact(repository, _turn(repository))
    repository.store(envelope, expected_latest_revision=0)

    assert repository.store(envelope, expected_latest_revision=0) == envelope
    with repository.factory.connect() as connection:
        row = connection.execute(
            "SELECT count(*) AS count FROM artifact_revisions"
        ).fetchone()
    assert row is not None and row["count"] == 1


@pytest.mark.parametrize("expected", [-1, True, 1])
def test_new_artifact_requires_exact_zero_head(tmp_path: Path, expected: int) -> None:
    repository = _repository(tmp_path)
    envelope = _artifact(repository, _turn(repository))
    error = (
        ArtifactRepositoryFieldError
        if type(expected) is bool or expected == -1
        else ArtifactConflictError
    )
    with pytest.raises(error):
        repository.store(envelope, expected_latest_revision=expected)


def test_store_requires_existing_project_turn_and_project_scope(tmp_path: Path) -> None:
    repository = _repository(tmp_path)
    missing_turn = CanonicalId.new()
    envelope = _artifact(repository, missing_turn)
    with pytest.raises(ArtifactNotFoundError, match="turn"):
        repository.store(envelope, expected_latest_revision=0)

    other = _repository(tmp_path, project_id=CanonicalId.new())
    other_turn = _turn(other, at=NOW + timedelta(seconds=1))
    other_envelope = _artifact(other, other_turn, at=NOW + timedelta(seconds=1))
    with pytest.raises(ArtifactConflictError, match="another project"):
        repository.store(other_envelope, expected_latest_revision=0)


def test_revisions_append_contiguously_under_optimistic_head(tmp_path: Path) -> None:
    repository = _repository(tmp_path)
    first = _artifact(repository, _turn(repository))
    repository.store(first, expected_latest_revision=0)
    second = _revision(
        first,
        revision=2,
        at=NOW + timedelta(seconds=1),
        payload={"value": "second"},
    )
    assert repository.store(second, expected_latest_revision=1) == second
    assert repository.load_latest(artifact_id=first.artifact_id) == second

    third = _revision(
        second,
        revision=3,
        at=NOW + timedelta(seconds=2),
        payload={"value": "third"},
    )
    with pytest.raises(ArtifactConflictError, match="expected artifact head"):
        repository.store(third, expected_latest_revision=1)
    skipped = _revision(
        second,
        revision=4,
        at=NOW + timedelta(seconds=2),
        payload={"value": "skipped"},
    )
    with pytest.raises(ArtifactConflictError, match="contiguously"):
        repository.store(skipped, expected_latest_revision=2)


@pytest.mark.parametrize("changed", ["turn", "recipe", "type"])
def test_revision_cannot_change_artifact_identity(
    tmp_path: Path, changed: str
) -> None:
    repository = _repository(tmp_path)
    first = _artifact(repository, _turn(repository))
    repository.store(first, expected_latest_revision=0)
    kwargs: dict[str, object] = {}
    if changed == "turn":
        kwargs["turn_id"] = _turn(repository, at=NOW + timedelta(seconds=1))
    elif changed == "recipe":
        kwargs["recipe_id"] = RecipeId.CONTEXT
    else:
        kwargs["artifact_type"] = "CONTEXT"
    changed_revision = _revision(
        first,
        revision=2,
        at=NOW + timedelta(seconds=2),
        payload={"value": "changed"},
        **kwargs,  # type: ignore[arg-type]
    )
    with pytest.raises(ArtifactConflictError, match="identity metadata"):
        repository.store(changed_revision, expected_latest_revision=1)


def test_same_revision_with_changed_content_conflicts(tmp_path: Path) -> None:
    repository = _repository(tmp_path)
    first = _artifact(repository, _turn(repository))
    repository.store(first, expected_latest_revision=0)
    changed = _revision(
        first,
        revision=1,
        at=NOW,
        payload={"value": "different"},
    )
    with pytest.raises(ArtifactConflictError, match="different immutable content"):
        repository.store(changed, expected_latest_revision=0)


def test_revision_cannot_change_alias_or_regress_time(tmp_path: Path) -> None:
    repository = _repository(tmp_path)
    first = _artifact(repository, _turn(repository))
    repository.store(first, expected_latest_revision=0)
    changed_alias = _revision(
        first,
        revision=2,
        at=NOW + timedelta(seconds=1),
        payload={"value": "changed alias"},
        short_id_ordinal=2,
    )
    with pytest.raises(ArtifactConflictError, match="alias identity"):
        repository.store(changed_alias, expected_latest_revision=1)
    regressed = _revision(
        first,
        revision=2,
        at=NOW - timedelta(seconds=1),
        payload={"value": "time regression"},
    )
    with pytest.raises(ArtifactConflictError, match="time precedes"):
        repository.store(regressed, expected_latest_revision=1)


def test_revision_gap_in_durable_history_fails_closed(tmp_path: Path) -> None:
    repository = _repository(tmp_path)
    first = _artifact(repository, _turn(repository))
    repository.store(first, expected_latest_revision=0)
    third = _revision(
        first,
        revision=3,
        at=NOW + timedelta(seconds=2),
        payload={"value": "gap"},
    )
    with repository.factory.connect() as connection:
        with connection.transaction():
            connection.execute(
                """
                INSERT INTO artifact_revisions VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    str(third.artifact_id),
                    3,
                    third.to_json(),
                    third.content_hash.value,
                    third.artifact_hash.value,
                    third.created_at,
                ),
            )
    with pytest.raises(ArtifactRepositoryIntegrityError, match="gap"):
        repository.load_latest(artifact_id=first.artifact_id)


def test_basis_refs_require_existing_exact_same_project_revision(tmp_path: Path) -> None:
    repository = _repository(tmp_path)
    turn_id = _turn(repository)
    basis = _artifact(repository, turn_id, artifact_type="SOURCE")
    repository.store(basis, expected_latest_revision=0)
    basis_ref = ArtifactBasisRef(basis.artifact_id, 1, basis.artifact_hash)
    dependent = _artifact(
        repository,
        turn_id,
        at=NOW + timedelta(seconds=1),
        recipe_id=RecipeId.CONTEXT,
        artifact_type="CONTEXT",
        basis_refs=(basis_ref,),
    )
    repository.store(dependent, expected_latest_revision=0)
    assert repository.load_latest(artifact_id=dependent.artifact_id) == dependent

    missing = ArtifactBasisRef(CanonicalId.new(), 1, sha256_text("missing"))
    invalid = _artifact(
        repository,
        turn_id,
        at=NOW + timedelta(seconds=2),
        artifact_type="INVALID_BASIS",
        basis_refs=(missing,),
    )
    with pytest.raises(ArtifactNotFoundError, match="basis"):
        repository.store(invalid, expected_latest_revision=0)


def test_basis_hash_mismatch_is_rejected_without_partial_identity(tmp_path: Path) -> None:
    repository = _repository(tmp_path)
    turn_id = _turn(repository)
    basis = _artifact(repository, turn_id, artifact_type="SOURCE")
    repository.store(basis, expected_latest_revision=0)
    wrong_ref = ArtifactBasisRef(basis.artifact_id, 1, sha256_text("wrong"))
    dependent = _artifact(
        repository,
        turn_id,
        at=NOW + timedelta(seconds=1),
        artifact_type="DEPENDENT",
        basis_refs=(wrong_ref,),
    )
    with pytest.raises(ArtifactConflictError, match="basis hash"):
        repository.store(dependent, expected_latest_revision=0)
    with pytest.raises(ArtifactNotFoundError):
        repository.load_latest(artifact_id=dependent.artifact_id)


def test_list_turn_is_chronological_bounded_and_recipe_scoped(tmp_path: Path) -> None:
    repository = _repository(tmp_path)
    turn_id = _turn(repository)
    intent = _artifact(repository, turn_id, at=NOW, artifact_type="INTENT")
    context = _artifact(
        repository,
        turn_id,
        at=NOW + timedelta(seconds=1),
        recipe_id=RecipeId.CONTEXT,
        artifact_type="CONTEXT",
    )
    repository.store(intent, expected_latest_revision=0)
    repository.store(context, expected_latest_revision=0)
    intent_two = _revision(
        intent,
        revision=2,
        at=NOW + timedelta(seconds=2),
        payload={"value": "revised"},
    )
    repository.store(intent_two, expected_latest_revision=1)

    assert repository.list_turn(turn_id=turn_id, limit=3) == (
        intent,
        context,
        intent_two,
    )
    assert repository.list_turn(
        turn_id=turn_id, limit=2, recipe_id=RecipeId.INTENT
    ) == (intent, intent_two)


@pytest.mark.parametrize("limit", [0, True, MAX_TURN_ARTIFACT_REVISIONS + 1])
def test_list_turn_limit_is_strictly_bounded(tmp_path: Path, limit: int) -> None:
    repository = _repository(tmp_path)
    with pytest.raises(ArtifactRepositoryFieldError, match="limit"):
        repository.list_turn(turn_id=CanonicalId.new(), limit=limit)


def test_reads_are_project_scoped_and_missing_is_explicit(tmp_path: Path) -> None:
    first = _repository(tmp_path)
    envelope = _artifact(first, _turn(first))
    first.store(envelope, expected_latest_revision=0)
    other = ArtifactRepository(first.factory, CanonicalId.new())
    with pytest.raises(ArtifactNotFoundError):
        other.load(artifact_id=envelope.artifact_id, revision=1)
    with pytest.raises(ArtifactNotFoundError):
        other.load_latest(artifact_id=envelope.artifact_id)


def test_durable_envelope_or_link_tampering_is_detected(tmp_path: Path) -> None:
    repository = _repository(tmp_path)
    turn_id = _turn(repository)
    basis = _artifact(repository, turn_id, artifact_type="SOURCE")
    repository.store(basis, expected_latest_revision=0)
    dependent = _artifact(
        repository,
        turn_id,
        at=NOW + timedelta(seconds=1),
        artifact_type="DEPENDENT",
        basis_refs=(ArtifactBasisRef(basis.artifact_id, 1, basis.artifact_hash),),
    )
    repository.store(dependent, expected_latest_revision=0)
    with repository.factory.connect() as connection:
        with connection.transaction():
            connection.execute(
                """
                UPDATE artifact_links SET basis_envelope_hash=?
                WHERE artifact_uuid=? AND artifact_revision=1
                """,
                (sha256_text("tampered").value, str(dependent.artifact_id)),
            )
    with pytest.raises(ArtifactRepositoryIntegrityError, match="basis link"):
        repository.load_latest(artifact_id=dependent.artifact_id)

    with repository.factory.connect() as connection:
        with connection.transaction():
            connection.execute(
                "UPDATE artifact_revisions SET envelope_json='{}' WHERE artifact_uuid=?",
                (str(basis.artifact_id),),
            )
    with pytest.raises(ArtifactRepositoryIntegrityError, match="canonical"):
        repository.load_latest(artifact_id=basis.artifact_id)


def test_durable_upstream_hash_tampering_invalidates_dependent_read(
    tmp_path: Path,
) -> None:
    repository = _repository(tmp_path)
    turn_id = _turn(repository)
    basis = _artifact(repository, turn_id, artifact_type="SOURCE")
    repository.store(basis, expected_latest_revision=0)
    dependent = _artifact(
        repository,
        turn_id,
        at=NOW + timedelta(seconds=1),
        artifact_type="DEPENDENT",
        basis_refs=(ArtifactBasisRef(basis.artifact_id, 1, basis.artifact_hash),),
    )
    repository.store(dependent, expected_latest_revision=0)
    with repository.factory.connect() as connection:
        with connection.transaction():
            connection.execute(
                "UPDATE artifact_revisions SET envelope_hash=? WHERE artifact_uuid=?",
                (sha256_text("tampered upstream").value, str(basis.artifact_id)),
            )
    with pytest.raises(ArtifactRepositoryIntegrityError, match="upstream basis"):
        repository.load_latest(artifact_id=dependent.artifact_id)


def test_store_and_read_arguments_are_strict(tmp_path: Path) -> None:
    repository = _repository(tmp_path)
    with pytest.raises(ArtifactRepositoryFieldError, match="envelope"):
        repository.store(object(), expected_latest_revision=0)  # type: ignore[arg-type]
    with pytest.raises(ArtifactRepositoryFieldError, match="artifact_id"):
        repository.load(artifact_id="artifact", revision=1)  # type: ignore[arg-type]
    with pytest.raises(ArtifactRepositoryFieldError, match="revision"):
        repository.load(artifact_id=CanonicalId.new(), revision=True)
    with pytest.raises(ArtifactRepositoryFieldError, match="recipe_id"):
        repository.list_turn(
            turn_id=CanonicalId.new(), limit=1, recipe_id="R1"  # type: ignore[arg-type]
        )


def test_repository_exposes_no_delete_or_overwrite_operation(tmp_path: Path) -> None:
    repository = _repository(tmp_path)
    assert not hasattr(repository, "delete")
    assert not hasattr(repository, "overwrite")
    assert not hasattr(repository, "save_file")


def test_hash_type_fixture_remains_typed() -> None:
    digest = sha256_text("typed")
    assert type(digest) is Sha256Digest
