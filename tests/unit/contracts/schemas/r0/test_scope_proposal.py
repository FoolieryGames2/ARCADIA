from __future__ import annotations

import pytest

from arcadia.contracts.aae.registry import get_contract
from arcadia.contracts.schemas.r0.scope_proposal import (
    PRE1_MAX_RAW_PROMPT_CHARS,
    SCOPE_PROPOSAL_INPUT_SCHEMA,
    SCOPE_PROPOSAL_OUTPUT_SCHEMA,
    ScopeProposalSemanticError,
    require_valid_scope_proposal_output,
    require_valid_scope_proposal_output_json,
)
from arcadia.core.canonical_json import DuplicateJsonKeyError, TrailingJsonContentError
from arcadia.core.validation import InstanceValidationError


def _call_data(
    *,
    prompt: str = "Say that exact line again.",
    max_recent: int = 20,
    completed_exchange_count: int = 101,
) -> dict[str, object]:
    return {
        "mode": "SCOPE_PROPOSAL",
        "turn_uuid": "TURN-S2",
        "conversation_uuid": "CONV-001",
        "raw_user_prompt": prompt,
        "current_transcript_metadata": {
            "transcript_commit_seq": completed_exchange_count,
            "completed_exchange_count": completed_exchange_count,
        },
        "host_policy_limits": {
            "max_contiguous_lookback_exchanges": max_recent,
            "max_targeted_candidate_turns_per_search": 8,
            "max_scope_expansion_cycles": 3,
            "max_total_injected_history_tokens": 4096,
        },
    }


def test_schema_identity_matches_registry_pre_version_binding() -> None:
    contract = get_contract("SCOPE_PROPOSAL")
    assert (SCOPE_PROPOSAL_INPUT_SCHEMA.schema_id, SCOPE_PROPOSAL_INPUT_SCHEMA.schema_version) == (
        contract.input_schema.schema_id,
        contract.input_schema.schema_version,
    )
    assert (SCOPE_PROPOSAL_OUTPUT_SCHEMA.schema_id, SCOPE_PROPOSAL_OUTPUT_SCHEMA.schema_version) == (
        contract.output_schema.schema_id,
        contract.output_schema.schema_version,
    )
    assert contract.input_schema.frozen is False
    assert contract.output_schema.frozen is False
    assert contract.dispatch_enabled is False


def test_reference_scope_proposal_call_data_is_strictly_valid() -> None:
    assert SCOPE_PROPOSAL_INPUT_SCHEMA.require_valid(_call_data()).valid


def test_input_schema_rejects_unknown_field_and_raw_prompt_cap() -> None:
    unknown = _call_data()
    unknown["semantic_memory"] = "forbidden"
    with pytest.raises(InstanceValidationError):
        SCOPE_PROPOSAL_INPUT_SCHEMA.require_valid(unknown)

    too_long = _call_data(prompt="x" * (PRE1_MAX_RAW_PROMPT_CHARS + 1))
    with pytest.raises(InstanceValidationError):
        SCOPE_PROPOSAL_INPUT_SCHEMA.require_valid(too_long)


@pytest.mark.parametrize(
    "output",
    [
        {
            "mode": "SCOPE_PROPOSAL",
            "status": "SUFFICIENT_WITHOUT_HISTORY",
            "recent_exchange_count": 0,
            "target_terms": [],
            "reason_codes": ["SELF_CONTAINED_PROMPT"],
        },
        {
            "mode": "SCOPE_PROPOSAL",
            "status": "REQUEST_RECENT",
            "recent_exchange_count": 1,
            "target_terms": [],
            "reason_codes": ["UNRESOLVED_DEICTIC_REFERENCE"],
        },
        {
            "mode": "SCOPE_PROPOSAL",
            "status": "REQUEST_TARGETED",
            "recent_exchange_count": 0,
            "target_terms": ["note-system rule"],
            "reason_codes": ["EXPLICIT_OLDER_REFERENCE"],
        },
    ],
)
def test_three_first_pass_outcomes_are_accepted(output: dict[str, object]) -> None:
    assert require_valid_scope_proposal_output(output, call_data=_call_data()) == output


@pytest.mark.parametrize(
    "output, match",
    [
        (
            {
                "mode": "SCOPE_PROPOSAL",
                "status": "SUFFICIENT_WITHOUT_HISTORY",
                "recent_exchange_count": 1,
                "target_terms": [],
                "reason_codes": ["SELF_CONTAINED_PROMPT"],
            },
            "neither recent nor targeted",
        ),
        (
            {
                "mode": "SCOPE_PROPOSAL",
                "status": "REQUEST_RECENT",
                "recent_exchange_count": 0,
                "target_terms": [],
                "reason_codes": ["UNRESOLVED_DEICTIC_REFERENCE"],
            },
            "recent_exchange_count >= 1",
        ),
        (
            {
                "mode": "SCOPE_PROPOSAL",
                "status": "REQUEST_TARGETED",
                "recent_exchange_count": 0,
                "target_terms": [],
                "reason_codes": ["EXPLICIT_OLDER_REFERENCE"],
            },
            "at least one bounded target term",
        ),
    ],
)
def test_schema_valid_but_semantically_inconsistent_outputs_fail(
    output: dict[str, object], match: str
) -> None:
    with pytest.raises(ScopeProposalSemanticError, match=match):
        require_valid_scope_proposal_output(output, call_data=_call_data())


def test_recent_request_cannot_exceed_host_policy() -> None:
    output = {
        "mode": "SCOPE_PROPOSAL",
        "status": "REQUEST_RECENT",
        "recent_exchange_count": 4,
        "target_terms": [],
        "reason_codes": ["UNRESOLVED_DEICTIC_REFERENCE"],
    }
    with pytest.raises(ScopeProposalSemanticError, match="exceeds host"):
        require_valid_scope_proposal_output(output, call_data=_call_data(max_recent=3))


def test_model_output_parser_keeps_strict_json_rejections() -> None:
    call_data = _call_data()
    with pytest.raises(DuplicateJsonKeyError):
        require_valid_scope_proposal_output_json(
            '{"mode":"SCOPE_PROPOSAL","mode":"SCOPE_PROPOSAL"}',
            call_data=call_data,
        )
    with pytest.raises(TrailingJsonContentError):
        require_valid_scope_proposal_output_json(
            '{"mode":"SCOPE_PROPOSAL"} trailing',
            call_data=call_data,
        )


def test_history_request_is_rejected_when_no_completed_exchange_exists() -> None:
    call_data = _call_data(completed_exchange_count=0)

    with pytest.raises(
        ScopeProposalSemanticError,
        match="history cannot be requested when completed_exchange_count is 0",
    ):
        require_valid_scope_proposal_output(
            {
                "mode": "SCOPE_PROPOSAL",
                "status": "REQUEST_RECENT",
                "recent_exchange_count": 1,
                "target_terms": [],
                "reason_codes": ["UNRESOLVED_REFERENCE"],
            },
            call_data=call_data,
        )

    with pytest.raises(
        ScopeProposalSemanticError,
        match="history cannot be requested when completed_exchange_count is 0",
    ):
        require_valid_scope_proposal_output(
            {
                "mode": "SCOPE_PROPOSAL",
                "status": "REQUEST_TARGETED",
                "recent_exchange_count": 0,
                "target_terms": ["adapter residency"],
                "reason_codes": ["TARGETED_PRIOR_TOPIC_REFERENCE"],
            },
            call_data=call_data,
        )


def test_recent_request_cannot_exceed_history_that_actually_exists() -> None:
    with pytest.raises(
        ScopeProposalSemanticError,
        match="recent_exchange_count exceeds completed_exchange_count",
    ):
        require_valid_scope_proposal_output(
            {
                "mode": "SCOPE_PROPOSAL",
                "status": "REQUEST_RECENT",
                "recent_exchange_count": 3,
                "target_terms": [],
                "reason_codes": ["UNRESOLVED_REFERENCE"],
            },
            call_data=_call_data(completed_exchange_count=2, max_recent=20),
        )
