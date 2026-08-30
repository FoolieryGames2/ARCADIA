from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime, timedelta

import pytest

from arcadia.core.artifact_envelope import ArtifactEnvelope, RecipeId
from arcadia.core.canonical_json import canonical_json_dumps
from arcadia.core.hashing import sha256_bytes, sha256_canonical_json
from arcadia.core.ids import CanonicalId
from arcadia.core.ledger import (
    TECHNICAL_LEDGER_VERSION,
    LedgerConflictError,
    LedgerFieldError,
    LedgerIntegrityError,
    TechnicalTurnLedger,
)

CREATED = datetime(2026, 8, 29, 12, 0, 0, tzinfo=UTC)


def make_artifact(
    project_id: CanonicalId,
    turn_id: CanonicalId,
    *,
    artifact_type: str = "INTENT_PACKET",
    created_at: datetime = CREATED,
) -> ArtifactEnvelope:
    return ArtifactEnvelope.create(
        project_id=project_id,
        turn_id=turn_id,
        recipe_id=RecipeId.INTENT,
        artifact_type=artifact_type,
        revision=1,
        project_version="0.1-prototype",
        contract_version="intent-contract-v1",
        schema_version="intent-schema-v1",
        recipe_version="recipe-r1-v0.1",
        registry_version="aae-registry-v1",
        runtime_identity_version="phase0-test-double-v1",
        created_at=created_at,
        payload={"artifact_type": artifact_type},
    )


def make_two_entry_ledger() -> TechnicalTurnLedger:
    project_id = CanonicalId.new()
    turn_id = CanonicalId.new()
    empty = TechnicalTurnLedger.empty(project_id=project_id, turn_id=turn_id)
    first = empty.append(
        make_artifact(project_id, turn_id),
        appended_at=CREATED,
        expected_head_hash=None,
    )
    return first.append(
        make_artifact(project_id, turn_id, artifact_type="VALIDATION_EVENT"),
        appended_at=CREATED + timedelta(seconds=1),
        expected_head_hash=first.head_hash,
    )


def test_empty_ledger_is_canonical_and_round_trips() -> None:
    ledger = TechnicalTurnLedger.empty(
        project_id=CanonicalId.new(), turn_id=CanonicalId.new()
    )

    assert ledger.ledger_version == TECHNICAL_LEDGER_VERSION
    assert ledger.entries == ()
    assert ledger.head_hash is None
    assert ledger.to_value()["entry_count"] == 0
    assert TechnicalTurnLedger.from_json(ledger.to_json()) == ledger


def test_append_is_additive_immutable_and_hash_chained() -> None:
    project_id = CanonicalId.new()
    turn_id = CanonicalId.new()
    empty = TechnicalTurnLedger.empty(project_id=project_id, turn_id=turn_id)
    artifact1 = make_artifact(project_id, turn_id)
    first = empty.append(artifact1, appended_at=CREATED, expected_head_hash=None)
    artifact2 = make_artifact(project_id, turn_id, artifact_type="VALIDATION_EVENT")
    second = first.append(
        artifact2,
        appended_at=CREATED + timedelta(seconds=1),
        expected_head_hash=first.head_hash,
    )

    assert empty.entries == ()
    assert len(first.entries) == 1
    assert len(second.entries) == 2
    assert second.entries[0] == first.entries[0]
    assert second.entries[0].previous_entry_hash is None
    assert second.entries[1].previous_entry_hash == second.entries[0].entry_hash
    assert [entry.sequence for entry in second.entries] == [1, 2]
    assert second.artifacts() == (artifact1, artifact2)


def test_canonical_snapshot_round_trip_is_byte_stable() -> None:
    ledger = make_two_entry_ledger()
    rendered = ledger.to_json()

    assert rendered == canonical_json_dumps(ledger.to_value())
    assert TechnicalTurnLedger.from_json(rendered) == ledger
    assert TechnicalTurnLedger.from_bytes(rendered.encode()) == ledger
    assert TechnicalTurnLedger.from_json(rendered).to_json() == rendered


def test_append_requires_exact_current_head() -> None:
    ledger = make_two_entry_ledger()
    artifact = make_artifact(ledger.project_id, ledger.turn_id, artifact_type="REPAIR_EVENT")

    with pytest.raises(LedgerConflictError, match="head changed"):
        ledger.append(artifact, appended_at=CREATED + timedelta(seconds=2), expected_head_hash=None)
    with pytest.raises(LedgerConflictError, match="head changed"):
        ledger.append(
            artifact,
            appended_at=CREATED + timedelta(seconds=2),
            expected_head_hash=sha256_bytes(b"stale"),
        )

    empty = TechnicalTurnLedger.empty(project_id=ledger.project_id, turn_id=CanonicalId.new())
    with pytest.raises(LedgerConflictError, match="nonexistent"):
        empty.append(
            make_artifact(empty.project_id, empty.turn_id),
            appended_at=CREATED,
            expected_head_hash=sha256_bytes(b"unexpected"),
        )


def test_cross_project_and_turn_artifacts_are_rejected() -> None:
    ledger = TechnicalTurnLedger.empty(
        project_id=CanonicalId.new(), turn_id=CanonicalId.new()
    )

    with pytest.raises(LedgerFieldError, match="boundary"):
        ledger.append(
            make_artifact(CanonicalId.new(), ledger.turn_id),
            appended_at=CREATED,
            expected_head_hash=None,
        )
    with pytest.raises(LedgerFieldError, match="boundary"):
        ledger.append(
            make_artifact(ledger.project_id, CanonicalId.new()),
            appended_at=CREATED,
            expected_head_hash=None,
        )


def test_duplicate_artifact_revision_cannot_be_appended() -> None:
    project_id = CanonicalId.new()
    turn_id = CanonicalId.new()
    artifact = make_artifact(project_id, turn_id)
    first = TechnicalTurnLedger.empty(project_id=project_id, turn_id=turn_id).append(
        artifact, appended_at=CREATED, expected_head_hash=None
    )

    with pytest.raises(LedgerIntegrityError, match="already present"):
        first.append(
            artifact,
            appended_at=CREATED + timedelta(seconds=1),
            expected_head_hash=first.head_hash,
        )


def test_append_time_cannot_precede_artifact_or_move_backward() -> None:
    project_id = CanonicalId.new()
    turn_id = CanonicalId.new()
    empty = TechnicalTurnLedger.empty(project_id=project_id, turn_id=turn_id)
    artifact = make_artifact(project_id, turn_id)

    with pytest.raises(LedgerIntegrityError, match="before it was created"):
        empty.append(
            artifact,
            appended_at=CREATED - timedelta(seconds=1),
            expected_head_hash=None,
        )

    first = empty.append(
        artifact, appended_at=CREATED + timedelta(seconds=2), expected_head_hash=None
    )
    with pytest.raises(LedgerIntegrityError, match="backward"):
        first.append(
            make_artifact(project_id, turn_id),
            appended_at=CREATED + timedelta(seconds=1),
            expected_head_hash=first.head_hash,
        )


def test_entry_metadata_tampering_is_detected() -> None:
    ledger = make_two_entry_ledger()
    tampered = ledger.to_value()
    entries = tampered["entries"]
    assert isinstance(entries, list)
    first = entries[0]
    assert isinstance(first, dict)
    first["appended_at"] = "2026-08-29T12:00:01.000000Z"

    with pytest.raises(LedgerIntegrityError, match="entry_hash"):
        TechnicalTurnLedger.from_value(tampered)


def test_entry_artifact_tampering_is_detected_before_chain_acceptance() -> None:
    ledger = make_two_entry_ledger()
    tampered = ledger.to_value()
    entries = tampered["entries"]
    assert isinstance(entries, list)
    first = entries[0]
    assert isinstance(first, dict)
    artifact = first["artifact"]
    assert isinstance(artifact, dict)
    artifact["payload"] = {"fabricated": True}

    with pytest.raises(ValueError, match="content_hash"):
        TechnicalTurnLedger.from_value(tampered)


def test_deletion_reordering_and_broken_predecessor_are_detected() -> None:
    ledger = make_two_entry_ledger()

    deleted = ledger.to_value()
    deleted_entries = deleted["entries"]
    assert isinstance(deleted_entries, list)
    del deleted_entries[0]
    deleted["entry_count"] = 1
    deleted["head_hash"] = deleted_entries[0]["entry_hash"]  # type: ignore[index]
    with pytest.raises(LedgerIntegrityError, match="contiguous"):
        TechnicalTurnLedger.from_value(deleted)

    reordered = ledger.to_value()
    reordered_entries = reordered["entries"]
    assert isinstance(reordered_entries, list)
    reordered_entries.reverse()
    with pytest.raises(LedgerIntegrityError, match="contiguous"):
        TechnicalTurnLedger.from_value(reordered)

    broken = ledger.to_value()
    broken_entries = broken["entries"]
    assert isinstance(broken_entries, list)
    second = broken_entries[1]
    assert isinstance(second, dict)
    second["previous_entry_hash"] = sha256_bytes(b"wrong").value
    unsigned = dict(second)
    del unsigned["entry_hash"]
    second["entry_hash"] = sha256_canonical_json(unsigned).value  # type: ignore[arg-type]
    with pytest.raises(LedgerIntegrityError, match="predecessor"):
        TechnicalTurnLedger.from_value(broken)


def test_snapshot_count_and_head_tampering_are_detected() -> None:
    ledger = make_two_entry_ledger()
    wrong_count = ledger.to_value()
    wrong_count["entry_count"] = 99
    with pytest.raises(LedgerIntegrityError, match="entry_count"):
        TechnicalTurnLedger.from_value(wrong_count)

    wrong_head = ledger.to_value()
    wrong_head["head_hash"] = sha256_bytes(b"wrong").value
    with pytest.raises(LedgerIntegrityError, match="head_hash"):
        TechnicalTurnLedger.from_value(wrong_head)


def test_unknown_missing_noncanonical_and_invalid_utf8_fail_closed() -> None:
    ledger = make_two_entry_ledger()

    unknown = ledger.to_value()
    unknown["semantic_memory"] = []
    with pytest.raises(LedgerFieldError, match="unknown"):
        TechnicalTurnLedger.from_value(unknown)

    missing = ledger.to_value()
    del missing["turn_uuid"]
    with pytest.raises(LedgerFieldError, match="missing"):
        TechnicalTurnLedger.from_value(missing)

    pretty = ledger.to_json().replace(",", ", ", 1)
    with pytest.raises(LedgerFieldError, match="Canonical"):
        TechnicalTurnLedger.from_json(pretty)
    with pytest.raises(LedgerFieldError, match="Canonical"):
        TechnicalTurnLedger.from_bytes(pretty.encode())
    with pytest.raises(LedgerFieldError, match="UTF-8"):
        TechnicalTurnLedger.from_bytes(b"\xff")


def test_in_memory_type_coercion_is_rejected() -> None:
    ledger = make_two_entry_ledger()

    with pytest.raises(LedgerFieldError, match="entries"):
        replace(ledger, entries=list(ledger.entries))  # type: ignore[arg-type]
    with pytest.raises(LedgerFieldError, match="version"):
        replace(ledger, ledger_version=True)
    with pytest.raises(LedgerFieldError, match="artifact_id"):
        ledger.artifact_history(str(ledger.entries[0].artifact.artifact_id))  # type: ignore[arg-type]


def test_artifact_history_is_read_only_and_identity_specific() -> None:
    ledger = make_two_entry_ledger()
    target = ledger.entries[0].artifact.artifact_id

    assert ledger.artifact_history(target) == (ledger.entries[0].artifact,)
    assert ledger.artifact_history(CanonicalId.new()) == ()
