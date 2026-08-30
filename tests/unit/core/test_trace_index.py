from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
from datetime import UTC, datetime, timedelta

import pytest

from arcadia.core.artifact_envelope import RecipeId
from arcadia.core.config import TracingConfig
from arcadia.core.hashing import sha256_canonical_json, sha256_text
from arcadia.core.ids import CanonicalId
from arcadia.core.trace_index import (
    FirstPassStanding,
    RawDeletionReason,
    RawDeletionState,
    TraceConflictError,
    TraceDisabledError,
    TraceEventKind,
    TraceFieldError,
    TraceIndex,
    TraceIndexEvent,
    TraceIndexRecord,
    TraceIntegrityError,
    TracePolicy,
    TraceReference,
    TraceReferenceKind,
    TraceSliceKind,
    TraceTelemetry,
    TrainingState,
    ValidationStanding,
)

NOW = datetime(2026, 8, 30, 12, 0, tzinfo=UTC)


def _policy(**overrides: object) -> TracePolicy:
    values: dict[str, object] = {
        "enabled": True,
        "raw_trace_enabled": True,
        "raw_trace_retention_days": 30,
        "training_export_enabled": False,
    }
    values.update(overrides)
    return TracePolicy(**values)


def _record(
    *,
    policy: TracePolicy | None = None,
    kind: TraceSliceKind = TraceSliceKind.RAW_TURN,
    raw: bool = False,
    held_out: bool = False,
    parent_trace_ids: tuple[CanonicalId, ...] = (),
) -> TraceIndexRecord:
    selected = _policy() if policy is None else policy
    raw_id = CanonicalId.new() if raw else None
    kwargs: dict[str, object] = {}
    if kind in {
        TraceSliceKind.RECIPE_ARTIFACT,
        TraceSliceKind.LEARNED_CALL,
        TraceSliceKind.REPAIR_ATTEMPT,
        TraceSliceKind.REENTRY_SLICE,
        TraceSliceKind.PERSISTENCE_TRANSACTION,
        TraceSliceKind.COMPLETION,
        TraceSliceKind.RESULT_PUBLICATION,
    }:
        kwargs["recipe_id"] = RecipeId.INTENT
    if kind in {TraceSliceKind.LEARNED_CALL, TraceSliceKind.REPAIR_ATTEMPT}:
        call_id = CanonicalId.new()
        kwargs.update(
            {
                "specialist_id": CanonicalId.new(),
                "specialist_mode": "intent.organize",
                "base_model_hash": sha256_text("base"),
                "adapter_hash": sha256_text("adapter"),
                "aae_contract_hash": sha256_text("aae"),
                "schema_hash": sha256_text("schema"),
                "inference_profile_hash": sha256_text("profile"),
                "runtime_identity_hash": sha256_text("runtime"),
                "runtime_epoch": 1,
                "validation_standing": ValidationStanding.PASSED,
                "first_pass_standing": FirstPassStanding.VALID,
                "references": (
                    TraceReference(TraceReferenceKind.CALL, call_id),
                ),
            }
        )
    if kind is TraceSliceKind.REPAIR_ATTEMPT:
        kwargs["repair_count"] = 1
        kwargs["references"] = (
            TraceReference(TraceReferenceKind.CALL, call_id),
            TraceReference(TraceReferenceKind.ATTEMPT, CanonicalId.new()),
        )
    return TraceIndexRecord.create(
        policy=selected,
        project_id=CanonicalId.new(),
        conversation_id=CanonicalId.new(),
        turn_id=CanonicalId.new(),
        slice_kind=kind,
        created_at=NOW,
        parent_trace_ids=parent_trace_ids,
        raw_trace_id=raw_id,
        raw_payload_hash=sha256_text("encrypted payload") if raw else None,
        held_out=held_out,
        **kwargs,
    )


def _register(
    index: TraceIndex, record: TraceIndexRecord
) -> tuple[TraceIndex, object]:
    return index.register(record=record, occurred_at=NOW, expected_head=index.head_hash)


def test_policy_copies_config_and_has_canonical_hash() -> None:
    config = TracingConfig(
        enabled=True,
        raw_trace_enabled=False,
        raw_trace_retention_days=30,
        training_export_enabled=False,
    )
    policy = TracePolicy.from_config(config)

    assert policy.raw_trace_retention_days == 30
    assert policy.policy_hash == sha256_text(
        '{"enabled":true,"policy_version":1,"raw_trace_enabled":false,'
        '"raw_trace_retention_days":30,"training_export_enabled":false}'
    )


@pytest.mark.parametrize(
    "overrides",
    [
        {"enabled": 1},
        {"raw_trace_retention_days": 0},
        {"raw_trace_retention_days": 3651},
        {"enabled": False, "raw_trace_enabled": True},
        {"enabled": False, "raw_trace_enabled": False, "training_export_enabled": True},
    ],
)
def test_policy_rejects_invalid_or_contradictory_values(overrides: dict[str, object]) -> None:
    with pytest.raises(TraceFieldError):
        _policy(**overrides)


def test_record_is_fixed_low_content_metadata_and_hashable() -> None:
    record = _record()
    value = record.to_value()

    assert value["slice_kind"] == "RAW_TURN"
    assert value["raw_trace_available"] is False
    assert value["training_state"] == "NOT_SELECTED"
    assert "prompt" not in value
    assert "output" not in value
    assert record.record_hash == sha256_canonical_json(record.to_value())


def test_held_out_is_permanently_initialized_never_train() -> None:
    assert _record(held_out=True).training_state is TrainingState.NEVER_TRAIN


def test_record_factory_rejects_coerced_boolean_and_mutable_collections() -> None:
    common = {
        "policy": _policy(),
        "project_id": CanonicalId.new(),
        "conversation_id": CanonicalId.new(),
        "turn_id": CanonicalId.new(),
        "slice_kind": TraceSliceKind.RAW_TURN,
        "created_at": NOW,
    }
    with pytest.raises(TraceFieldError, match="held_out must be a boolean"):
        TraceIndexRecord.create(**common, held_out=1)
    with pytest.raises(TraceFieldError, match="immutable tuple"):
        TraceIndexRecord.create(**common, parent_trace_ids=[])
    with pytest.raises(TraceFieldError, match="immutable tuple"):
        TraceIndexRecord.create(**common, references=[])


def test_raw_capture_requires_policy_and_sets_rolling_deadline() -> None:
    record = _record(raw=True)

    assert record.raw_trace_available
    assert record.raw_deletion_state is RawDeletionState.AVAILABLE
    assert record.raw_retention_expires_at == "2026-09-29T12:00:00.000000Z"
    assert not record.retention_due(NOW + timedelta(days=29))
    assert record.retention_due(NOW + timedelta(days=30))

    with pytest.raises(TraceFieldError, match="does not permit"):
        _record(policy=_policy(raw_trace_enabled=False), raw=True)


def test_raw_uuid_and_hash_must_be_supplied_together() -> None:
    with pytest.raises(TraceFieldError, match="supplied together"):
        TraceIndexRecord.create(
            policy=_policy(),
            project_id=CanonicalId.new(),
            conversation_id=CanonicalId.new(),
            turn_id=CanonicalId.new(),
            slice_kind=TraceSliceKind.RAW_TURN,
            created_at=NOW,
            raw_trace_id=CanonicalId.new(),
        )


def test_learned_and_repair_slices_require_exact_identity_metadata() -> None:
    learned = _record(kind=TraceSliceKind.LEARNED_CALL)
    repair = _record(kind=TraceSliceKind.REPAIR_ATTEMPT)

    assert learned.specialist_id is not None
    assert learned.inference_profile_hash is not None
    assert repair.repair_count == 1
    assert {reference.kind for reference in repair.references} == {
        TraceReferenceKind.ATTEMPT,
        TraceReferenceKind.CALL,
    }

    with pytest.raises(TraceFieldError, match="specialist UUID"):
        replace(learned, specialist_id=None)
    with pytest.raises(TraceFieldError, match="call and attempt references"):
        replace(repair, references=())


def test_specialist_mode_rejects_content_like_free_text() -> None:
    with pytest.raises(TraceFieldError, match="canonical specialist mode"):
        replace(_record(kind=TraceSliceKind.LEARNED_CALL), specialist_mode="ignore all rules")


def test_non_learned_slice_cannot_claim_specialist_identity() -> None:
    with pytest.raises(TraceFieldError, match="cannot claim"):
        replace(_record(), specialist_id=CanonicalId.new(), specialist_mode="fake")


def test_cross_turn_lineage_requires_parent_and_parent_rules_are_strict() -> None:
    with pytest.raises(TraceFieldError, match="at least one parent"):
        _record(kind=TraceSliceKind.CROSS_TURN_LINEAGE)

    parent = CanonicalId.new()
    record = _record(
        kind=TraceSliceKind.CROSS_TURN_LINEAGE, parent_trace_ids=(parent,)
    )
    assert record.parent_trace_ids == (parent,)
    with pytest.raises(TraceIntegrityError, match="own parent"):
        replace(record, parent_trace_ids=(record.trace_id,))


def test_references_are_typed_unique_and_canonically_ordered() -> None:
    one = TraceReference(TraceReferenceKind.ARTIFACT, CanonicalId.new())
    two = TraceReference(TraceReferenceKind.OPERATION, CanonicalId.new())
    record = TraceIndexRecord.create(
        policy=_policy(),
        project_id=CanonicalId.new(),
        conversation_id=CanonicalId.new(),
        turn_id=CanonicalId.new(),
        slice_kind=TraceSliceKind.TOOL_EVIDENCE,
        created_at=NOW,
        references=(two, one),
    )
    assert record.references == tuple(
        sorted((one, two), key=lambda ref: (ref.kind.value, str(ref.target_id)))
    )
    with pytest.raises(TraceIntegrityError, match="unique"):
        replace(record, references=(one, one))


def test_telemetry_rejects_negative_or_coerced_metrics() -> None:
    with pytest.raises(TraceFieldError, match="nonnegative"):
        TraceTelemetry(input_tokens=-1)
    with pytest.raises(TraceFieldError, match="nonnegative"):
        TraceTelemetry(output_tokens=True)


def test_disabled_policy_refuses_registration() -> None:
    policy = _policy(enabled=False, raw_trace_enabled=False)
    index = TraceIndex.create(policy)

    with pytest.raises(TraceDisabledError):
        index.register(record=_record(policy=policy), occurred_at=NOW, expected_head=None)


def test_registration_is_immutable_hash_chained_and_policy_bound() -> None:
    policy = _policy()
    index = TraceIndex.create(policy)
    first_record = _record(policy=policy)
    second_record = _record(policy=policy)
    index, first = _register(index, first_record)
    index, second = _register(index, second_record)

    assert first.sequence == 1
    assert second.sequence == 2
    assert second.previous_event_hash == first.event_hash
    assert index.get(first_record.trace_id) == first_record
    assert index.head_hash == second.event_hash

    with pytest.raises(TraceIntegrityError, match="different trace policy"):
        index.register(
            record=_record(policy=_policy(raw_trace_retention_days=31)),
            occurred_at=NOW,
            expected_head=index.head_hash,
        )


def test_registration_rejects_dangling_parent_and_repair_call() -> None:
    policy = _policy()
    index = TraceIndex.create(policy)
    dangling = _record(policy=policy, parent_trace_ids=(CanonicalId.new(),))
    with pytest.raises(TraceIntegrityError, match="not registered"):
        _register(index, dangling)

    repair = _record(policy=policy, kind=TraceSliceKind.REPAIR_ATTEMPT)
    with pytest.raises(TraceIntegrityError, match="no registered learned-call"):
        _register(index, repair)


def test_registered_learned_call_can_parent_matching_repair() -> None:
    policy = _policy()
    index = TraceIndex.create(policy)
    learned = _record(policy=policy, kind=TraceSliceKind.LEARNED_CALL)
    index, _ = _register(index, learned)
    call_ref = next(
        reference
        for reference in learned.references
        if reference.kind is TraceReferenceKind.CALL
    )
    repair = _record(policy=policy, kind=TraceSliceKind.REPAIR_ATTEMPT)
    attempt_ref = next(
        reference
        for reference in repair.references
        if reference.kind is TraceReferenceKind.ATTEMPT
    )
    repair = replace(
        repair,
        project_id=learned.project_id,
        turn_id=learned.turn_id,
        references=tuple(
            sorted(
                (call_ref, attempt_ref),
                key=lambda ref: (ref.kind.value, str(ref.target_id)),
            )
        ),
    )

    index, _ = _register(index, repair)
    assert index.get(repair.trace_id) == repair


def test_event_time_cannot_precede_creation_or_move_backward() -> None:
    policy = _policy()
    index = TraceIndex.create(policy)
    record = _record(policy=policy)
    with pytest.raises(TraceIntegrityError, match="precede trace creation"):
        index.register(
            record=record,
            occurred_at=NOW - timedelta(seconds=1),
            expected_head=None,
        )
    index, _ = index.register(
        record=record,
        occurred_at=NOW + timedelta(seconds=3),
        expected_head=None,
    )
    later_record = replace(
        _record(policy=policy),
        created_at=(NOW + timedelta(seconds=1)).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
    )
    with pytest.raises(TraceIntegrityError, match="nondecreasing"):
        index.register(
            record=later_record,
            occurred_at=NOW + timedelta(seconds=2),
            expected_head=index.head_hash,
        )


def test_expected_head_and_revision_reject_stale_updates() -> None:
    index = TraceIndex.create(_policy())
    record = _record(policy=index.policy, raw=True)
    index, _ = _register(index, record)

    with pytest.raises(TraceConflictError, match="head"):
        index.pin_raw(
            trace_id=record.trace_id,
            expected_revision=1,
            occurred_at=NOW,
            expected_head=None,
        )
    with pytest.raises(TraceConflictError, match="revision"):
        index.pin_raw(
            trace_id=record.trace_id,
            expected_revision=2,
            occurred_at=NOW,
            expected_head=index.head_hash,
        )


def test_pin_survives_expiry_then_unpin_becomes_due() -> None:
    index = TraceIndex.create(_policy())
    record = _record(policy=index.policy, raw=True)
    index, _ = _register(index, record)
    index, pin = index.pin_raw(
        trace_id=record.trace_id,
        expected_revision=1,
        occurred_at=NOW + timedelta(days=1),
        expected_head=index.head_hash,
    )

    assert pin.event_kind is TraceEventKind.PINNED
    assert index.due_for_expiry(NOW + timedelta(days=31)) == ()
    index, unpin = index.unpin_raw(
        trace_id=record.trace_id,
        expected_revision=2,
        occurred_at=NOW + timedelta(days=31),
        expected_head=index.head_hash,
    )
    assert unpin.event_kind is TraceEventKind.UNPINNED
    assert index.due_for_expiry(NOW + timedelta(days=31)) == (record.trace_id,)


def test_expiry_confirmation_creates_safe_tombstone_after_deadline() -> None:
    index = TraceIndex.create(_policy())
    record = _record(policy=index.policy, raw=True)
    raw_id = record.raw_trace_id
    assert raw_id is not None
    index, _ = _register(index, record)

    with pytest.raises(TraceIntegrityError, match="has not elapsed"):
        index.confirm_raw_deleted(
            trace_id=record.trace_id,
            raw_trace_id=raw_id,
            expected_revision=1,
            reason=RawDeletionReason.RETENTION_EXPIRED,
            occurred_at=NOW + timedelta(days=29),
            expected_head=index.head_hash,
        )

    index, event = index.confirm_raw_deleted(
        trace_id=record.trace_id,
        raw_trace_id=raw_id,
        expected_revision=1,
        reason=RawDeletionReason.RETENTION_EXPIRED,
        occurred_at=NOW + timedelta(days=30),
        expected_head=index.head_hash,
    )
    tombstone = index.get(record.trace_id)

    assert event.event_kind is TraceEventKind.RAW_DELETION_CONFIRMED
    assert not tombstone.raw_trace_available
    assert tombstone.raw_trace_id is None
    assert tombstone.raw_payload_hash == record.raw_payload_hash
    assert tombstone.raw_deletion_state is RawDeletionState.TOMBSTONED
    assert tombstone.raw_deletion_reason is RawDeletionReason.RETENTION_EXPIRED


def test_owner_delete_can_remove_pinned_raw_but_confirmation_must_match() -> None:
    index = TraceIndex.create(_policy())
    record = _record(policy=index.policy, raw=True)
    raw_id = record.raw_trace_id
    assert raw_id is not None
    index, _ = _register(index, record)
    index, _ = index.pin_raw(
        trace_id=record.trace_id,
        expected_revision=1,
        occurred_at=NOW,
        expected_head=index.head_hash,
    )

    with pytest.raises(TraceIntegrityError, match="does not match"):
        index.confirm_raw_deleted(
            trace_id=record.trace_id,
            raw_trace_id=CanonicalId.new(),
            expected_revision=2,
            reason=RawDeletionReason.OWNER_DELETED,
            occurred_at=NOW,
            expected_head=index.head_hash,
        )
    index, _ = index.confirm_raw_deleted(
        trace_id=record.trace_id,
        raw_trace_id=raw_id,
        expected_revision=2,
        reason=RawDeletionReason.OWNER_DELETED,
        occurred_at=NOW,
        expected_head=index.head_hash,
    )
    assert index.get(record.trace_id).raw_deletion_reason is RawDeletionReason.OWNER_DELETED


def test_retention_expiry_cannot_delete_pinned_trace() -> None:
    index = TraceIndex.create(_policy())
    record = _record(policy=index.policy, raw=True)
    raw_id = record.raw_trace_id
    assert raw_id is not None
    index, _ = _register(index, record)
    index, _ = index.pin_raw(
        trace_id=record.trace_id,
        expected_revision=1,
        occurred_at=NOW,
        expected_head=index.head_hash,
    )

    with pytest.raises(TraceIntegrityError, match="cannot expire"):
        index.confirm_raw_deleted(
            trace_id=record.trace_id,
            raw_trace_id=raw_id,
            expected_revision=2,
            reason=RawDeletionReason.RETENTION_EXPIRED,
            occurred_at=NOW + timedelta(days=31),
            expected_head=index.head_hash,
        )


def test_replay_rejects_deletion_reorder_duplicate_and_unauthorized_change() -> None:
    index = TraceIndex.create(_policy())
    record = _record(policy=index.policy, raw=True)
    index, registered = _register(index, record)
    index, pinned = index.pin_raw(
        trace_id=record.trace_id,
        expected_revision=1,
        occurred_at=NOW,
        expected_head=index.head_hash,
    )

    with pytest.raises(TraceIntegrityError):
        TraceIndex(policy=index.policy, events=(pinned,))
    with pytest.raises(TraceIntegrityError):
        TraceIndex(policy=index.policy, events=(pinned, registered))
    with pytest.raises(TraceIntegrityError):
        TraceIndex(policy=index.policy, events=(registered, registered))

    changed = replace(pinned.record, revision=2, repair_count=1, raw_pinned=True)
    forged = TraceIndexEvent.create(
        sequence=2,
        event_kind=TraceEventKind.PINNED,
        occurred_at=NOW,
        record=changed,
        previous_event_hash=registered.event_hash,
    )
    with pytest.raises(TraceIntegrityError, match="unauthorized metadata"):
        TraceIndex(policy=index.policy, events=(registered, forged))


def test_event_content_tampering_and_noncanonical_transition_are_rejected() -> None:
    index = TraceIndex.create(_policy())
    record = _record(policy=index.policy, raw=True)
    index, event = _register(index, record)

    with pytest.raises(TraceIntegrityError, match="event_hash"):
        replace(event, occurred_at="2026-08-30T13:00:00.000000Z")
    with pytest.raises(TraceIntegrityError, match="must differ"):
        replace(event, event_id=record.trace_id)


def test_index_is_immutable_and_canonical_snapshot_has_no_raw_content() -> None:
    index = TraceIndex.create(_policy())
    record = _record(policy=index.policy, raw=True)
    index, event = _register(index, record)

    with pytest.raises(FrozenInstanceError):
        index.events = ()
    rendered = index.to_json()
    assert event.event_hash.value in rendered
    assert "encrypted payload" not in rendered
    assert '"training_state":"NOT_SELECTED"' in rendered
