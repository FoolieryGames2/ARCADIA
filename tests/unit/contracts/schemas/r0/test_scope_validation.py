from __future__ import annotations

from copy import deepcopy

import pytest

from arcadia.contracts.aae.registry import get_contract
from arcadia.contracts.schemas.r0.scope_validation import (
    SCOPE_VALIDATION_INPUT_SCHEMA,
    SCOPE_VALIDATION_OUTPUT_SCHEMA,
    ScopeValidationSemanticError,
    require_valid_scope_validation_call_data,
    require_valid_scope_validation_output,
    require_valid_scope_validation_output_json,
)
from arcadia.core.canonical_json import DuplicateJsonKeyError, TrailingJsonContentError
from arcadia.core.hashing import sha256_text
from arcadia.core.validation import InstanceValidationError


def _turn(
    *,
    turn_uuid: str = "TURN-PRIOR-S2",
    turn_index: int = 101,
    user_message: str = "Give me the one-line Arcadia status.",
    final_response: str = "A.R.C.A.D.I.A. status line.",
) -> dict[str, object]:
    return {
        "turn_uuid": turn_uuid,
        "turn_index": turn_index,
        "user_message": user_message,
        "final_response": final_response,
        "user_message_hash": str(sha256_text(user_message)),
        "final_response_hash": str(sha256_text(final_response)),
    }


def _call_data(*, remaining_cycles: int = 2) -> dict[str, object]:
    return {
        "mode": "SCOPE_VALIDATION",
        "turn_uuid": "TURN-S2",
        "conversation_uuid": "CONV-001",
        "raw_user_prompt": "Say that exact line again.",
        "frozen_retrieved_turns": [_turn()],
        "host_policy_limits": {
            "remaining_expansion_cycles": remaining_cycles,
            "max_total_injected_history_tokens": 4096,
        },
    }


def _output(
    status: str,
    *,
    unresolved: list[str] | None = None,
) -> dict[str, object]:
    if unresolved is None:
        unresolved = [] if status == "SUFFICIENT" else ["that exact line"]
    return {
        "mode": "SCOPE_VALIDATION",
        "status": status,
        "reason_codes": ["REFERENCE_ASSESSMENT_COMPLETE"],
        "unresolved_references": unresolved,
    }


def test_schema_identity_matches_registry_pre_version_binding() -> None:
    contract = get_contract("SCOPE_VALIDATION")
    assert (SCOPE_VALIDATION_INPUT_SCHEMA.schema_id, SCOPE_VALIDATION_INPUT_SCHEMA.schema_version) == (
        contract.input_schema.schema_id,
        contract.input_schema.schema_version,
    )
    assert (SCOPE_VALIDATION_OUTPUT_SCHEMA.schema_id, SCOPE_VALIDATION_OUTPUT_SCHEMA.schema_version) == (
        contract.output_schema.schema_id,
        contract.output_schema.schema_version,
    )
    assert contract.input_schema.frozen is False
    assert contract.output_schema.frozen is False
    assert contract.dispatch_enabled is False


def test_reference_scope_validation_call_data_is_strict_and_integrity_valid() -> None:
    call_data = _call_data()
    assert SCOPE_VALIDATION_INPUT_SCHEMA.require_valid(call_data).valid
    assert require_valid_scope_validation_call_data(call_data) == call_data


def test_input_schema_rejects_unknown_fields_and_empty_retrieval() -> None:
    unknown = _call_data()
    unknown["semantic_memory"] = {"forbidden": True}
    with pytest.raises(InstanceValidationError):
        SCOPE_VALIDATION_INPUT_SCHEMA.require_valid(unknown)

    empty = _call_data()
    empty["frozen_retrieved_turns"] = []
    with pytest.raises(InstanceValidationError):
        SCOPE_VALIDATION_INPUT_SCHEMA.require_valid(empty)


def test_frozen_turn_hash_tamper_fails_closed() -> None:
    call_data = _call_data()
    turn = call_data["frozen_retrieved_turns"][0]  # type: ignore[index]
    turn["final_response"] = "tampered"  # type: ignore[index]
    with pytest.raises(ScopeValidationSemanticError, match="final_response_hash does not match"):
        require_valid_scope_validation_call_data(call_data)


def test_frozen_turns_must_be_prior_unique_and_chronological() -> None:
    current = _call_data()
    current["frozen_retrieved_turns"] = [_turn(turn_uuid="TURN-S2")]
    with pytest.raises(ScopeValidationSemanticError, match="prior turns"):
        require_valid_scope_validation_call_data(current)

    duplicate = _call_data()
    duplicate["frozen_retrieved_turns"] = [
        _turn(turn_uuid="TURN-A", turn_index=10),
        _turn(turn_uuid="TURN-A", turn_index=11),
    ]
    with pytest.raises(ScopeValidationSemanticError, match="repeat a turn_uuid"):
        require_valid_scope_validation_call_data(duplicate)

    reversed_order = _call_data()
    reversed_order["frozen_retrieved_turns"] = [
        _turn(turn_uuid="TURN-A", turn_index=11),
        _turn(turn_uuid="TURN-B", turn_index=10),
    ]
    with pytest.raises(ScopeValidationSemanticError, match="chronological"):
        require_valid_scope_validation_call_data(reversed_order)


@pytest.mark.parametrize(
    "status",
    [
        "SUFFICIENT",
        "NEEDS_MORE_RECENT",
        "NEEDS_TARGETED_HISTORY",
        "UNRESOLVABLE_WITH_TRANSCRIPT",
        "BOUND_EXHAUSTED",
    ],
)
def test_all_five_frozen_scope_validation_statuses_are_accepted(status: str) -> None:
    output = _output(status)
    assert require_valid_scope_validation_output(output, call_data=_call_data()) == output


def test_fixed_shape_rejects_unknown_or_missing_output_fields() -> None:
    extra = _output("SUFFICIENT")
    extra["recent_exchange_count"] = 1
    with pytest.raises(InstanceValidationError):
        SCOPE_VALIDATION_OUTPUT_SCHEMA.require_valid(extra)

    missing = _output("SUFFICIENT")
    del missing["unresolved_references"]
    with pytest.raises(InstanceValidationError):
        SCOPE_VALIDATION_OUTPUT_SCHEMA.require_valid(missing)


def test_sufficient_requires_no_unresolved_references() -> None:
    with pytest.raises(ScopeValidationSemanticError, match="SUFFICIENT requires"):
        require_valid_scope_validation_output(
            _output("SUFFICIENT", unresolved=["still unresolved"]),
            call_data=_call_data(),
        )


def test_non_sufficient_statuses_preserve_an_unresolved_reference() -> None:
    for status in (
        "NEEDS_MORE_RECENT",
        "NEEDS_TARGETED_HISTORY",
        "UNRESOLVABLE_WITH_TRANSCRIPT",
        "BOUND_EXHAUSTED",
    ):
        with pytest.raises(ScopeValidationSemanticError, match="requires at least one"):
            require_valid_scope_validation_output(
                _output(status, unresolved=[]),
                call_data=_call_data(),
            )


def test_more_scope_request_is_rejected_when_no_expansion_cycles_remain() -> None:
    for status in ("NEEDS_MORE_RECENT", "NEEDS_TARGETED_HISTORY"):
        with pytest.raises(ScopeValidationSemanticError, match="remaining_expansion_cycles is 0"):
            require_valid_scope_validation_output(
                _output(status),
                call_data=_call_data(remaining_cycles=0),
            )

    # Terminal unresolved outcomes remain honest and legal at the bound.
    assert require_valid_scope_validation_output(
        _output("BOUND_EXHAUSTED"),
        call_data=_call_data(remaining_cycles=0),
    )["status"] == "BOUND_EXHAUSTED"


def test_model_output_parser_keeps_strict_json_rejections() -> None:
    with pytest.raises(DuplicateJsonKeyError):
        require_valid_scope_validation_output_json(
            '{"mode":"SCOPE_VALIDATION","mode":"SCOPE_VALIDATION"}',
            call_data=_call_data(),
        )
    with pytest.raises(TrailingJsonContentError):
        require_valid_scope_validation_output_json(
            '{"mode":"SCOPE_VALIDATION"} trailing',
            call_data=_call_data(),
        )


def test_input_integrity_snapshot_example_does_not_depend_on_mutable_fixture_aliasing() -> None:
    original = _call_data()
    copied = deepcopy(original)
    assert require_valid_scope_validation_call_data(copied) == original
