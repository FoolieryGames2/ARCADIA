from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from arcadia.core.canonical_json import JsonValue
from arcadia.core.config import StorageConfig
from arcadia.core.hashing import Sha256Digest, sha256_canonical_json, sha256_text
from arcadia.core.ids import CanonicalId
from arcadia.storage.connection import SQLiteConnectionFactory
from arcadia.storage.migrations import MigrationRunner
from arcadia.storage.registry_snapshots import (
    MAX_REGISTRY_SNAPSHOTS_PER_READ,
    RegistrySnapshot,
    RegistrySnapshotConflictError,
    RegistrySnapshotError,
    RegistrySnapshotFieldError,
    RegistrySnapshotIntegrityError,
    RegistrySnapshotNotFoundError,
    RegistrySnapshotRepository,
)

NOW = datetime(2026, 8, 30, 12, 0, tzinfo=UTC)


def _factory(root: Path) -> SQLiteConnectionFactory:
    return SQLiteConnectionFactory(
        workspace_root=root,
        storage=StorageConfig(
            data_dir="data",
            database_name="registries.sqlite3",
            busy_timeout_ms=1000,
            require_fts5=True,
        ),
    )


def _repository(
    root: Path, *, project_id: CanonicalId | None = None
) -> RegistrySnapshotRepository:
    factory = _factory(root)
    with factory.connect() as connection:
        MigrationRunner().migrate(connection, applied_at=NOW)
    return RegistrySnapshotRepository(factory, project_id or CanonicalId.new())


def _snapshot(
    repository: RegistrySnapshotRepository,
    *,
    kind: str = "AAE_CONTRACT",
    version: str = "aae-v1",
    at: datetime = NOW,
    value: dict[str, JsonValue] | None = None,
) -> RegistrySnapshot:
    return RegistrySnapshot.create(
        project_id=repository.project_id,
        registry_kind=kind,
        registry_version=version,
        contract_identity_version="contract-v1",
        schema_identity_version="schema-v1",
        recipe_identity_version="recipes-v1",
        registry_identity_version="registries-v1",
        runtime_identity_version="runtime-v1",
        snapshot={"entries": []} if value is None else value,
        created_at=at,
    )


def _replace_snapshot(
    source: RegistrySnapshot,
    *,
    snapshot: dict[str, JsonValue] | None = None,
    registry_kind: str | None = None,
    registry_version: str | None = None,
) -> RegistrySnapshot:
    value = source.to_value()
    if snapshot is not None:
        value["snapshot"] = snapshot
    if registry_kind is not None:
        value["registry_kind"] = registry_kind
    if registry_version is not None:
        value["registry_version"] = registry_version
    unsigned = dict(value)
    unsigned.pop("snapshot_hash")
    value["snapshot_hash"] = sha256_canonical_json(unsigned).value
    return RegistrySnapshot.from_value(value)


def test_repository_requires_current_migrated_schema(tmp_path: Path) -> None:
    factory = _factory(tmp_path)
    with factory.connect():
        pass
    repository = RegistrySnapshotRepository(factory, CanonicalId.new())
    with pytest.raises(RegistrySnapshotError, match="schema is not current"):
        repository.load(snapshot_id=CanonicalId.new())


def test_repository_identity_is_strict_and_immutable(tmp_path: Path) -> None:
    factory = _factory(tmp_path)
    with pytest.raises(RegistrySnapshotFieldError, match="factory"):
        RegistrySnapshotRepository(object(), CanonicalId.new())  # type: ignore[arg-type]
    with pytest.raises(RegistrySnapshotFieldError, match="project_id"):
        RegistrySnapshotRepository(factory, "project")  # type: ignore[arg-type]
    repository = _repository(tmp_path)
    with pytest.raises(FrozenInstanceError):
        repository.project_id = CanonicalId.new()  # type: ignore[misc]


def test_snapshot_create_is_canonical_hashed_and_immutable(tmp_path: Path) -> None:
    repository = _repository(tmp_path)
    source: dict[str, JsonValue] = {"z": 1, "a": {"enabled": True}}
    snapshot = _snapshot(repository, value=source)
    source["z"] = 9

    assert snapshot.snapshot_json == '{"a":{"enabled":true},"z":1}'
    assert snapshot.snapshot == {"a": {"enabled": True}, "z": 1}
    assert snapshot.to_json() == RegistrySnapshot.from_json(snapshot.to_json()).to_json()
    assert type(snapshot.snapshot_hash) is Sha256Digest
    with pytest.raises(FrozenInstanceError):
        snapshot.registry_version = "changed"  # type: ignore[misc]


def test_snapshot_property_returns_a_fresh_value(tmp_path: Path) -> None:
    snapshot = _snapshot(_repository(tmp_path), value={"nested": {"count": 1}})
    first = snapshot.snapshot
    nested = first["nested"]
    assert isinstance(nested, dict)
    nested["count"] = 2
    assert snapshot.snapshot == {"nested": {"count": 1}}


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("registry_kind", "aae-contract"),
        ("registry_kind", ""),
        ("registry_version", "bad version"),
        ("contract_identity_version", ""),
        ("schema_identity_version", "bad/version"),
        ("recipe_identity_version", True),
        ("registry_identity_version", "*"),
        ("runtime_identity_version", " runtime"),
    ],
)
def test_snapshot_rejects_noncanonical_kind_and_versions(
    tmp_path: Path, field: str, value: object
) -> None:
    repository = _repository(tmp_path)
    kwargs: dict[str, object] = {
        "project_id": repository.project_id,
        "registry_kind": "AAE_CONTRACT",
        "registry_version": "aae-v1",
        "contract_identity_version": "contract-v1",
        "schema_identity_version": "schema-v1",
        "recipe_identity_version": "recipes-v1",
        "registry_identity_version": "registries-v1",
        "runtime_identity_version": "runtime-v1",
        "snapshot": {"entries": []},
        "created_at": NOW,
    }
    kwargs[field] = value
    with pytest.raises(RegistrySnapshotFieldError):
        RegistrySnapshot.create(**kwargs)  # type: ignore[arg-type]


@pytest.mark.parametrize("value", [[], "registry", 1, True, None])
def test_snapshot_requires_top_level_json_object(
    tmp_path: Path, value: object
) -> None:
    repository = _repository(tmp_path)
    with pytest.raises(RegistrySnapshotFieldError, match="JSON object"):
        RegistrySnapshot.create(
            project_id=repository.project_id,
            registry_kind="AAE_CONTRACT",
            registry_version="aae-v1",
            contract_identity_version="contract-v1",
            schema_identity_version="schema-v1",
            recipe_identity_version="recipes-v1",
            registry_identity_version="registries-v1",
            runtime_identity_version="runtime-v1",
            snapshot=value,  # type: ignore[arg-type]
            created_at=NOW,
        )


def test_from_value_rejects_unknown_fields_and_hash_tampering(tmp_path: Path) -> None:
    snapshot = _snapshot(_repository(tmp_path))
    unknown = snapshot.to_value()
    unknown["authority"] = "invented"
    with pytest.raises(RegistrySnapshotFieldError, match="fields"):
        RegistrySnapshot.from_value(unknown)

    changed = snapshot.to_value()
    changed["snapshot"] = {"entries": ["changed"]}
    with pytest.raises(RegistrySnapshotIntegrityError, match="snapshot_hash"):
        RegistrySnapshot.from_value(changed)


def test_create_translates_non_json_nested_data_and_invalid_time(tmp_path: Path) -> None:
    repository = _repository(tmp_path)
    base = {
        "project_id": repository.project_id,
        "registry_kind": "AAE_CONTRACT",
        "registry_version": "aae-v1",
        "contract_identity_version": "contract-v1",
        "schema_identity_version": "schema-v1",
        "recipe_identity_version": "recipes-v1",
        "registry_identity_version": "registries-v1",
        "runtime_identity_version": "runtime-v1",
    }
    with pytest.raises(RegistrySnapshotFieldError, match="canonical input"):
        RegistrySnapshot.create(
            **base,  # type: ignore[arg-type]
            snapshot={"bad": object()},  # type: ignore[dict-item]
            created_at=NOW,
        )
    with pytest.raises(RegistrySnapshotFieldError, match="canonical input"):
        RegistrySnapshot.create(
            **base,  # type: ignore[arg-type]
            snapshot={"entries": []},
            created_at=NOW.replace(tzinfo=None),
        )


def test_from_json_requires_exact_canonical_json(tmp_path: Path) -> None:
    snapshot = _snapshot(_repository(tmp_path))
    with pytest.raises(RegistrySnapshotFieldError, match="Canonical JSON"):
        RegistrySnapshot.from_json(snapshot.to_json() + "\n")


def test_store_load_and_load_version_are_exact(tmp_path: Path) -> None:
    repository = _repository(tmp_path)
    snapshot = _snapshot(repository)

    assert repository.store(snapshot) == snapshot
    assert repository.load(snapshot_id=snapshot.snapshot_id) == snapshot
    assert repository.load_version(
        registry_kind="AAE_CONTRACT", registry_version="aae-v1"
    ) == snapshot


def test_exact_store_retry_is_idempotent(tmp_path: Path) -> None:
    repository = _repository(tmp_path)
    snapshot = _snapshot(repository)
    repository.store(snapshot)
    assert repository.store(snapshot) == snapshot
    with repository.factory.connect() as connection:
        row = connection.execute(
            "SELECT count(*) AS count FROM registry_snapshots"
        ).fetchone()
    assert row is not None and row["count"] == 1


def test_snapshot_uuid_cannot_change_immutable_content(tmp_path: Path) -> None:
    repository = _repository(tmp_path)
    original = _snapshot(repository)
    repository.store(original)
    changed = _replace_snapshot(original, snapshot={"entries": ["changed"]})
    with pytest.raises(RegistrySnapshotConflictError, match="UUID"):
        repository.store(changed)


def test_kind_version_is_immutable_within_project(tmp_path: Path) -> None:
    repository = _repository(tmp_path)
    first = _snapshot(repository)
    second = _snapshot(repository, value={"entries": ["different"]})
    repository.store(first)
    with pytest.raises(RegistrySnapshotConflictError, match="kind/version"):
        repository.store(second)


def test_same_kind_version_is_independent_across_projects(tmp_path: Path) -> None:
    first = _repository(tmp_path)
    second = RegistrySnapshotRepository(first.factory, CanonicalId.new())
    first_snapshot = _snapshot(first)
    second_snapshot = _snapshot(second)
    first.store(first_snapshot)
    second.store(second_snapshot)
    assert first.load_version(
        registry_kind="AAE_CONTRACT", registry_version="aae-v1"
    ) == first_snapshot
    assert second.load_version(
        registry_kind="AAE_CONTRACT", registry_version="aae-v1"
    ) == second_snapshot


def test_cross_project_snapshot_write_and_reads_are_rejected(tmp_path: Path) -> None:
    first = _repository(tmp_path)
    second = RegistrySnapshotRepository(first.factory, CanonicalId.new())
    snapshot = _snapshot(first)
    with pytest.raises(RegistrySnapshotConflictError, match="another project"):
        second.store(snapshot)
    first.store(snapshot)
    with pytest.raises(RegistrySnapshotNotFoundError):
        second.load(snapshot_id=snapshot.snapshot_id)
    with pytest.raises(RegistrySnapshotNotFoundError):
        second.load_version(
            registry_kind=snapshot.registry_kind,
            registry_version=snapshot.registry_version,
        )


def test_list_kind_is_bounded_chronological_and_project_scoped(tmp_path: Path) -> None:
    repository = _repository(tmp_path)
    first = _snapshot(repository, version="v1", at=NOW)
    second = _snapshot(repository, version="v2", at=NOW + timedelta(seconds=1))
    other_kind = _snapshot(
        repository,
        kind="CAPABILITY",
        version="v1",
        at=NOW + timedelta(seconds=2),
    )
    repository.store(second)
    repository.store(other_kind)
    repository.store(first)
    assert repository.list_kind(registry_kind="AAE_CONTRACT", limit=2) == (
        first,
        second,
    )
    assert repository.list_kind(registry_kind="AAE_CONTRACT", limit=1) == (first,)


@pytest.mark.parametrize("limit", [0, True, MAX_REGISTRY_SNAPSHOTS_PER_READ + 1])
def test_list_limit_is_strictly_bounded(tmp_path: Path, limit: int) -> None:
    repository = _repository(tmp_path)
    with pytest.raises(RegistrySnapshotFieldError, match="limit"):
        repository.list_kind(registry_kind="AAE_CONTRACT", limit=limit)


def test_missing_reads_are_explicit(tmp_path: Path) -> None:
    repository = _repository(tmp_path)
    with pytest.raises(RegistrySnapshotNotFoundError):
        repository.load(snapshot_id=CanonicalId.new())
    with pytest.raises(RegistrySnapshotNotFoundError):
        repository.load_version(
            registry_kind="AAE_CONTRACT", registry_version="missing"
        )


@pytest.mark.parametrize("column", ["snapshot_json", "snapshot_hash", "created_at"])
def test_durable_tampering_fails_closed(tmp_path: Path, column: str) -> None:
    repository = _repository(tmp_path)
    snapshot = _snapshot(repository)
    repository.store(snapshot)
    replacement = {
        "snapshot_json": '{"entries":["tampered"]}',
        "snapshot_hash": sha256_text("tampered").value,
        "created_at": "2026-99-99T99:99:99.999999Z",
    }[column]
    with repository.factory.connect() as connection:
        with connection.transaction():
            connection.execute(
                f"UPDATE registry_snapshots SET {column}=? WHERE snapshot_uuid=?",
                (replacement, str(snapshot.snapshot_id)),
            )
    with pytest.raises(RegistrySnapshotIntegrityError):
        repository.load(snapshot_id=snapshot.snapshot_id)


def test_strict_repository_arguments_and_no_activation_inference(tmp_path: Path) -> None:
    repository = _repository(tmp_path)
    with pytest.raises(RegistrySnapshotFieldError, match="snapshot"):
        repository.store(object())  # type: ignore[arg-type]
    with pytest.raises(RegistrySnapshotFieldError, match="snapshot_id"):
        repository.load(snapshot_id="snapshot")  # type: ignore[arg-type]
    with pytest.raises(RegistrySnapshotFieldError, match="registry_kind"):
        repository.load_version(registry_kind="aae", registry_version="v1")
    assert not hasattr(repository, "activate")
    assert not hasattr(repository, "latest")
    assert not hasattr(repository, "delete")
    assert not hasattr(repository, "overwrite")
