from __future__ import annotations

from dataclasses import FrozenInstanceError, replace

import pytest

from arcadia.core.config import BudgetConfig
from arcadia.core.hashing import sha256_text
from arcadia.core.ids import CanonicalId
from arcadia.core.repair_policy import RepairBasis, RepairPolicy, RepairSession
from arcadia.core.work_budget import (
    BUDGET_EXHAUSTED_CODE,
    BudgetCharge,
    BudgetConflictError,
    BudgetDimension,
    BudgetEventKind,
    BudgetExhaustedError,
    BudgetFieldError,
    BudgetIntegrityError,
    BudgetLimits,
    WorkBudgetLedger,
)


def _limits(**overrides: int) -> BudgetLimits:
    values = {
        "max_model_calls": 4,
        "max_repairs_per_call": 2,
        "max_reentries": 2,
        "max_history_expansions": 2,
        "max_context_retrieval_expansions": 2,
        "max_decision_work_items": 4,
        "max_reconciliation_discovery_depth": 3,
        "max_side_effect_retries": 2,
        "max_compensations": 2,
        "max_total_model_input_tokens": 100,
        "max_total_model_output_tokens": 50,
    }
    values.update(overrides)
    return BudgetLimits(**values)


def _repair_session(limit: int = 2) -> tuple[RepairSession, object]:
    basis = RepairBasis.create(
        call_id=CanonicalId.new(),
        specialist_mode="intent.organize",
        inference_profile_id="intent.v1",
        inference_profile_hash=sha256_text("profile"),
        authoritative_packet={"task": "bounded"},
    )
    session = RepairSession.begin(policy=RepairPolicy(limit), basis=basis)
    session, attempt = session.authorize(
        previous_output={"bad": True},
        validation_error={"code": "SCHEMA_REJECTION"},
    )
    return session, attempt


def _grant_model(ledger: WorkBudgetLedger, *, input_tokens: int = 10, output: int = 5):
    return _grant_call(
        ledger,
        CanonicalId.new(),
        input_tokens=input_tokens,
        output=output,
    )


def _grant_call(
    ledger: WorkBudgetLedger,
    call_id: CanonicalId,
    *,
    input_tokens: int = 10,
    output: int = 5,
):
    return ledger.authorize_model_attempt(
        call_id=call_id,
        input_tokens=input_tokens,
        reserved_output_tokens=output,
        expected_head=ledger.head_hash,
    )


def test_limits_copy_all_config_v1_budget_fields_and_hash() -> None:
    values = _limits().to_value()
    values.pop("budget_version")
    config = BudgetConfig.model_validate(values)

    limits = BudgetLimits.from_config(config)

    assert limits.to_value()["max_model_calls"] == 4
    assert limits.limits_hash == _limits().limits_hash


def test_limits_reject_untyped_dimension_lookup() -> None:
    with pytest.raises(BudgetFieldError, match="BudgetDimension"):
        _limits().ceiling("model_calls")


@pytest.mark.parametrize("value", [-1, True, 1.5, "2"])
def test_limits_reject_negative_or_coerced_values(value: object) -> None:
    with pytest.raises(BudgetFieldError, match="nonnegative integer"):
        _limits(max_model_calls=value)


def test_zero_limits_explicitly_deny_work() -> None:
    zero = _limits(
        max_model_calls=0,
        max_repairs_per_call=0,
        max_reentries=0,
        max_history_expansions=0,
        max_context_retrieval_expansions=0,
        max_decision_work_items=0,
        max_reconciliation_discovery_depth=0,
        max_side_effect_retries=0,
        max_compensations=0,
        max_total_model_input_tokens=0,
        max_total_model_output_tokens=0,
    )
    ledger = WorkBudgetLedger.create(zero)

    with pytest.raises(BudgetExhaustedError) as exc:
        _grant_model(ledger, input_tokens=0, output=0)

    assert exc.value.dimension is BudgetDimension.MODEL_CALLS
    assert ledger.entries == ()


def test_model_grant_atomically_charges_call_and_reserved_tokens() -> None:
    ledger = WorkBudgetLedger.create(_limits())
    advanced, entry = _grant_model(ledger, input_tokens=30, output=20)

    assert ledger.usage.model_calls == 0
    assert advanced.usage.model_calls == 1
    assert advanced.usage.model_input_tokens == 30
    assert advanced.usage.model_output_tokens == 20
    assert entry.event_kind is BudgetEventKind.MODEL_ATTEMPT
    assert entry.previous_entry_hash is None
    assert advanced.head_hash == entry.entry_hash


@pytest.mark.parametrize(
    "overrides, first, second, dimension",
    [
        ({"max_model_calls": 1}, (0, 0), (0, 0), BudgetDimension.MODEL_CALLS),
        ({"max_total_model_input_tokens": 10}, (7, 0), (4, 0), BudgetDimension.MODEL_INPUT_TOKENS),
        ({"max_total_model_output_tokens": 10}, (0, 7), (0, 4), BudgetDimension.MODEL_OUTPUT_TOKENS),
    ],
)
def test_model_aggregate_exhaustion_is_atomic(
    overrides: dict[str, int],
    first: tuple[int, int],
    second: tuple[int, int],
    dimension: BudgetDimension,
) -> None:
    ledger = WorkBudgetLedger.create(_limits(**overrides))
    ledger, _ = _grant_model(ledger, input_tokens=first[0], output=first[1])
    before = ledger.to_json()

    with pytest.raises(BudgetExhaustedError) as exc:
        _grant_model(ledger, input_tokens=second[0], output=second[1])

    assert exc.value.code == BUDGET_EXHAUSTED_CODE
    assert exc.value.dimension is dimension
    assert exc.value.to_value()["code"] == "BUDGET_EXHAUSTED"
    assert ledger.to_json() == before


def test_repair_grant_consumes_repair_model_call_and_tokens() -> None:
    ledger = WorkBudgetLedger.create(_limits())
    session, attempt = _repair_session()
    ledger, _ = _grant_call(ledger, attempt.call_id, input_tokens=10, output=5)

    advanced, entry = ledger.authorize_repair_attempt(
        session=session,
        attempt=attempt,
        input_tokens=12,
        reserved_output_tokens=6,
        expected_head=ledger.head_hash,
    )

    assert advanced.usage.repair_attempts == 1
    assert advanced.usage.model_calls == 2
    assert advanced.usage.model_input_tokens == 22
    assert advanced.usage.model_output_tokens == 11
    assert entry.operation_id == attempt.attempt_id
    assert entry.repair_call_id == attempt.call_id
    assert entry.repair_ordinal == 1


def test_repair_requires_matching_policy_current_session_head_and_ordinal() -> None:
    ledger = WorkBudgetLedger.create(_limits())
    session, first = _repair_session()
    ledger, _ = _grant_call(ledger, first.call_id, input_tokens=0, output=0)

    with pytest.raises(BudgetIntegrityError, match="policy cap"):
        WorkBudgetLedger.create(_limits(max_repairs_per_call=1)).authorize_repair_attempt(
            session=session,
            attempt=first,
            input_tokens=0,
            reserved_output_tokens=0,
            expected_head=ledger.head_hash,
        )

    session, second = session.authorize(
        previous_output={"bad": "again"}, validation_error={"code": "STILL_BAD"}
    )
    with pytest.raises(BudgetIntegrityError, match="current repair-session head"):
        ledger.authorize_repair_attempt(
            session=session,
            attempt=first,
            input_tokens=0,
            reserved_output_tokens=0,
            expected_head=ledger.head_hash,
        )

    ledger, _ = ledger.authorize_repair_attempt(
        session=RepairSession(policy=session.policy, basis=session.basis, attempts=(first,)),
        attempt=first,
        input_tokens=0,
        reserved_output_tokens=0,
        expected_head=ledger.head_hash,
    )
    ledger, _ = ledger.authorize_repair_attempt(
        session=session,
        attempt=second,
        input_tokens=0,
        reserved_output_tokens=0,
        expected_head=ledger.head_hash,
    )
    assert ledger.repairs_remaining_for(first.call_id) == 0


def test_repair_is_also_blocked_by_aggregate_model_call_cap() -> None:
    ledger = WorkBudgetLedger.create(_limits(max_model_calls=1))
    session, attempt = _repair_session()
    ledger, _ = _grant_call(ledger, attempt.call_id, input_tokens=0, output=0)

    with pytest.raises(BudgetExhaustedError) as exc:
        ledger.authorize_repair_attempt(
            session=session,
            attempt=attempt,
            input_tokens=0,
            reserved_output_tokens=0,
            expected_head=ledger.head_hash,
        )

    assert exc.value.dimension is BudgetDimension.MODEL_CALLS


def test_repair_requires_prior_original_model_grant() -> None:
    ledger = WorkBudgetLedger.create(_limits())
    session, attempt = _repair_session()

    with pytest.raises(BudgetIntegrityError, match="no prior original"):
        ledger.authorize_repair_attempt(
            session=session,
            attempt=attempt,
            input_tokens=0,
            reserved_output_tokens=0,
            expected_head=None,
        )


def test_all_additive_work_dimensions_accumulate() -> None:
    ledger = WorkBudgetLedger.create(_limits())
    ledger, _ = ledger.authorize_reentry(operation_id=CanonicalId.new(), expected_head=None)
    ledger, _ = ledger.authorize_history_expansion(
        operation_id=CanonicalId.new(), expected_head=ledger.head_hash
    )
    ledger, _ = ledger.authorize_context_retrieval_expansion(
        operation_id=CanonicalId.new(), expected_head=ledger.head_hash
    )
    ledger, _ = ledger.authorize_decision_work(
        operation_id=CanonicalId.new(), work_items=3, expected_head=ledger.head_hash
    )
    ledger, _ = ledger.authorize_side_effect_retry(
        operation_id=CanonicalId.new(), expected_head=ledger.head_hash
    )
    ledger, _ = ledger.authorize_compensation(
        operation_id=CanonicalId.new(), expected_head=ledger.head_hash
    )

    assert ledger.usage.reentries == 1
    assert ledger.usage.history_expansions == 1
    assert ledger.usage.context_retrieval_expansions == 1
    assert ledger.usage.decision_work_items == 3
    assert ledger.usage.side_effect_retries == 1
    assert ledger.usage.compensations == 1


def test_reconciliation_depth_is_high_water_not_additive() -> None:
    ledger = WorkBudgetLedger.create(_limits(max_reconciliation_discovery_depth=3))
    ledger, _ = ledger.authorize_reconciliation_discovery(
        operation_id=CanonicalId.new(), depth=2, expected_head=None
    )
    ledger, _ = ledger.authorize_reconciliation_discovery(
        operation_id=CanonicalId.new(), depth=3, expected_head=ledger.head_hash
    )
    ledger, _ = ledger.authorize_reconciliation_discovery(
        operation_id=CanonicalId.new(), depth=1, expected_head=ledger.head_hash
    )

    assert ledger.usage.reconciliation_discovery_depth == 3
    assert ledger.remaining(BudgetDimension.RECONCILIATION_DISCOVERY_DEPTH) == 0
    with pytest.raises(BudgetExhaustedError):
        ledger.authorize_reconciliation_discovery(
            operation_id=CanonicalId.new(), depth=4, expected_head=ledger.head_hash
        )


@pytest.mark.parametrize(
    "method, limit_name",
    [
        ("authorize_reentry", "max_reentries"),
        ("authorize_history_expansion", "max_history_expansions"),
        ("authorize_context_retrieval_expansion", "max_context_retrieval_expansions"),
        ("authorize_side_effect_retry", "max_side_effect_retries"),
        ("authorize_compensation", "max_compensations"),
    ],
)
def test_single_work_dimensions_fail_at_zero(method: str, limit_name: str) -> None:
    ledger = WorkBudgetLedger.create(_limits(**{limit_name: 0}))

    with pytest.raises(BudgetExhaustedError):
        getattr(ledger, method)(operation_id=CanonicalId.new(), expected_head=None)

    assert ledger.entries == ()


def test_decision_work_rejects_zero_and_over_limit_atomically() -> None:
    ledger = WorkBudgetLedger.create(_limits(max_decision_work_items=2))

    with pytest.raises(BudgetFieldError, match="positive integer"):
        ledger.authorize_decision_work(
            operation_id=CanonicalId.new(), work_items=0, expected_head=None
        )
    with pytest.raises(BudgetExhaustedError):
        ledger.authorize_decision_work(
            operation_id=CanonicalId.new(), work_items=3, expected_head=None
        )
    assert ledger.entries == ()


def test_expected_head_prevents_stale_or_unexpected_grants() -> None:
    ledger = WorkBudgetLedger.create(_limits())
    with pytest.raises(BudgetConflictError):
        ledger.authorize_reentry(
            operation_id=CanonicalId.new(), expected_head=sha256_text("not empty")
        )
    ledger, _ = ledger.authorize_reentry(operation_id=CanonicalId.new(), expected_head=None)

    with pytest.raises(BudgetConflictError):
        ledger.authorize_reentry(operation_id=CanonicalId.new(), expected_head=None)


def test_operation_uuid_cannot_receive_two_grants() -> None:
    ledger = WorkBudgetLedger.create(_limits())
    operation_id = CanonicalId.new()
    ledger, _ = ledger.authorize_reentry(operation_id=operation_id, expected_head=None)

    with pytest.raises(BudgetIntegrityError, match="already has"):
        ledger.authorize_history_expansion(
            operation_id=operation_id, expected_head=ledger.head_hash
        )


def test_entries_are_contiguous_hash_chained_and_limit_bound() -> None:
    ledger = WorkBudgetLedger.create(_limits())
    ledger, first = ledger.authorize_reentry(operation_id=CanonicalId.new(), expected_head=None)
    ledger, second = ledger.authorize_compensation(
        operation_id=CanonicalId.new(), expected_head=ledger.head_hash
    )

    assert first.sequence == 1
    assert second.sequence == 2
    assert second.previous_entry_hash == first.entry_hash
    assert first.limits_hash == ledger.limits.limits_hash
    assert ledger.to_value()["entry_count"] == 2


def test_replay_rejects_deletion_reorder_duplicate_and_limit_change() -> None:
    ledger = WorkBudgetLedger.create(_limits())
    ledger, first = ledger.authorize_reentry(operation_id=CanonicalId.new(), expected_head=None)
    ledger, second = ledger.authorize_compensation(
        operation_id=CanonicalId.new(), expected_head=ledger.head_hash
    )

    with pytest.raises(BudgetIntegrityError):
        WorkBudgetLedger(limits=ledger.limits, entries=(second,))
    with pytest.raises(BudgetIntegrityError):
        WorkBudgetLedger(limits=ledger.limits, entries=(second, first))
    with pytest.raises(BudgetIntegrityError):
        WorkBudgetLedger(limits=ledger.limits, entries=(first, first))
    with pytest.raises(BudgetIntegrityError, match="different frozen limits"):
        WorkBudgetLedger(limits=_limits(max_reentries=3), entries=ledger.entries)


def test_entry_content_tampering_is_detected() -> None:
    ledger = WorkBudgetLedger.create(_limits())
    ledger, entry = ledger.authorize_reentry(operation_id=CanonicalId.new(), expected_head=None)

    with pytest.raises(BudgetIntegrityError, match="entry_hash"):
        replace(entry, operation_id=CanonicalId.new())
    with pytest.raises(BudgetFieldError, match="exactly one unit"):
        replace(entry, charges=(BudgetCharge(BudgetDimension.REENTRIES, 2),))
    with pytest.raises(BudgetIntegrityError, match="must differ"):
        replace(entry, entry_id=entry.operation_id)


def test_entry_rejects_wrong_event_shape_and_unsorted_or_duplicate_charges() -> None:
    ledger = WorkBudgetLedger.create(_limits())
    ledger, entry = _grant_model(ledger)

    with pytest.raises(BudgetFieldError, match="event kind"):
        replace(entry, event_kind=BudgetEventKind.REENTRY)
    with pytest.raises(BudgetFieldError, match="canonical dimension order"):
        replace(entry, charges=tuple(reversed(entry.charges)))
    duplicate = (entry.charges[0], entry.charges[0], *entry.charges[1:])
    with pytest.raises(BudgetFieldError, match="repeat"):
        replace(entry, charges=duplicate)


def test_state_is_immutable_and_has_no_refund_or_reset_api() -> None:
    ledger = WorkBudgetLedger.create(_limits())
    ledger, _ = ledger.authorize_reentry(operation_id=CanonicalId.new(), expected_head=None)

    with pytest.raises(FrozenInstanceError):
        ledger.entries = ()
    assert not hasattr(ledger, "refund")
    assert not hasattr(ledger, "reset")


def test_canonical_snapshot_contains_limits_usage_chain_and_head() -> None:
    ledger = WorkBudgetLedger.create(_limits())
    ledger, entry = _grant_model(ledger)
    rendered = ledger.to_json()

    assert entry.entry_hash.value in rendered
    assert ledger.limits.limits_hash.value in rendered
    assert '"model_calls":1' in rendered
