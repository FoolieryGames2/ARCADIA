"""Strict PRE-1 schemas and host semantic checks for Recipe 0 SCOPE_PROPOSAL."""

from __future__ import annotations

from typing import Final

from arcadia.contracts.aae.registry import MODE_SCOPE_PROPOSAL, get_contract
from arcadia.contracts.policies.schema_rules import require_fixed_top_level_output_shape
from arcadia.contracts.policies.vocabulary import MACHINE_LABEL_PATTERN_PRE_V1
from arcadia.core.canonical_json import JsonValue, strict_json_loads
from arcadia.core.validation import JSON_SCHEMA_DIALECT, StrictJsonSchema, compile_strict_schema

# These are PRE-version safety caps for the first executable A1 slice. They are
# deliberately local to this schema and do not complete/freeze its settings profile.
PRE1_MAX_RAW_PROMPT_CHARS: Final = 65_536
PRE1_MAX_TARGET_TERMS: Final = 8
PRE1_MAX_TARGET_TERM_CHARS: Final = 256
PRE1_MAX_REASON_CODES: Final = 16
PRE1_MAX_REASON_CODE_CHARS: Final = 64

_CANONICAL_TOKEN_PATTERN: Final = r"^[A-Za-z0-9][A-Za-z0-9._:+/\-]{0,127}$"
_REASON_CODE_PATTERN: Final = MACHINE_LABEL_PATTERN_PRE_V1

_SCOPE_CONTRACT: Final = get_contract(MODE_SCOPE_PROPOSAL)
_PROPOSAL_OUTCOME: Final = _SCOPE_CONTRACT.semantic_enums["proposal_outcome"]

_INPUT_SCHEMA_VALUE: Final[dict[str, object]] = {
    "$schema": JSON_SCHEMA_DIALECT,
    "type": "object",
    "additionalProperties": False,
    "required": [
        "mode",
        "turn_uuid",
        "conversation_uuid",
        "raw_user_prompt",
        "current_transcript_metadata",
        "host_policy_limits",
    ],
    "properties": {
        "mode": {"type": "string", "const": MODE_SCOPE_PROPOSAL},
        "turn_uuid": {
            "type": "string",
            "minLength": 1,
            "maxLength": 128,
            "pattern": _CANONICAL_TOKEN_PATTERN,
        },
        "conversation_uuid": {
            "type": "string",
            "minLength": 1,
            "maxLength": 128,
            "pattern": _CANONICAL_TOKEN_PATTERN,
        },
        "raw_user_prompt": {
            "type": "string",
            "maxLength": PRE1_MAX_RAW_PROMPT_CHARS,
        },
        "current_transcript_metadata": {
            "type": "object",
            "additionalProperties": False,
            "required": ["transcript_commit_seq", "completed_exchange_count"],
            "properties": {
                "transcript_commit_seq": {"type": "integer", "minimum": 0},
                "completed_exchange_count": {"type": "integer", "minimum": 0},
            },
        },
        "host_policy_limits": {
            "type": "object",
            "additionalProperties": False,
            "required": [
                "max_contiguous_lookback_exchanges",
                "max_targeted_candidate_turns_per_search",
                "max_scope_expansion_cycles",
                "max_total_injected_history_tokens",
            ],
            "properties": {
                "max_contiguous_lookback_exchanges": {"type": "integer", "minimum": 0},
                "max_targeted_candidate_turns_per_search": {"type": "integer", "minimum": 0},
                "max_scope_expansion_cycles": {"type": "integer", "minimum": 0},
                "max_total_injected_history_tokens": {"type": "integer", "minimum": 1},
            },
        },
    },
}

_OUTPUT_SCHEMA_VALUE: Final[dict[str, object]] = {
    "$schema": JSON_SCHEMA_DIALECT,
    "type": "object",
    "additionalProperties": False,
    "required": [
        "mode",
        "status",
        "recent_exchange_count",
        "target_terms",
        "reason_codes",
    ],
    "properties": {
        "mode": {"type": "string", "const": MODE_SCOPE_PROPOSAL},
        "status": {
            "type": "string",
            "enum": list(_PROPOSAL_OUTCOME),
        },
        "recent_exchange_count": {"type": "integer", "minimum": 0},
        "target_terms": {
            "type": "array",
            "maxItems": PRE1_MAX_TARGET_TERMS,
            "uniqueItems": True,
            "items": {
                "type": "string",
                "minLength": 1,
                "maxLength": PRE1_MAX_TARGET_TERM_CHARS,
            },
        },
        "reason_codes": {
            "type": "array",
            "minItems": 1,
            "maxItems": PRE1_MAX_REASON_CODES,
            "uniqueItems": True,
            "items": {
                "type": "string",
                "minLength": 1,
                "maxLength": PRE1_MAX_REASON_CODE_CHARS,
                "pattern": _REASON_CODE_PATTERN,
            },
        },
    },
}

SCOPE_PROPOSAL_INPUT_SCHEMA: Final[StrictJsonSchema] = compile_strict_schema(
    schema_id=_SCOPE_CONTRACT.input_schema.schema_id,
    schema_version=_SCOPE_CONTRACT.input_schema.schema_version,
    schema=_INPUT_SCHEMA_VALUE,
)
SCOPE_PROPOSAL_OUTPUT_SCHEMA: Final[StrictJsonSchema] = require_fixed_top_level_output_shape(
    compile_strict_schema(
        schema_id=_SCOPE_CONTRACT.output_schema.schema_id,
        schema_version=_SCOPE_CONTRACT.output_schema.schema_version,
        schema=_OUTPUT_SCHEMA_VALUE,
    )
)


class ScopeProposalSemanticError(ValueError):
    """The output is schema-valid but violates the bounded R0 proposal contract."""


def _require_object(value: JsonValue, label: str) -> dict[str, JsonValue]:
    if type(value) is not dict:
        raise ScopeProposalSemanticError(f"{label} must be a JSON object")
    return value


def require_valid_scope_proposal_output(
    output: JsonValue,
    *,
    call_data: JsonValue,
) -> JsonValue:
    """Require schema-valid output plus cross-field and host-policy consistency.

    The three first-pass outcomes are mutually exclusive scope strategies:
    no history, recent contiguous lookback, or targeted transcript search.
    """

    SCOPE_PROPOSAL_INPUT_SCHEMA.require_valid(call_data)
    SCOPE_PROPOSAL_OUTPUT_SCHEMA.require_valid(output)

    output_obj = _require_object(output, "scope proposal output")
    call_obj = _require_object(call_data, "scope proposal CALL_DATA")
    metadata = _require_object(
        call_obj["current_transcript_metadata"], "current_transcript_metadata"
    )
    policy = _require_object(call_obj["host_policy_limits"], "host_policy_limits")

    status = output_obj["status"]
    recent_count = output_obj["recent_exchange_count"]
    target_terms = output_obj["target_terms"]
    assert type(status) is str
    assert type(recent_count) is int
    assert type(target_terms) is list

    completed_exchange_count = metadata["completed_exchange_count"]
    max_recent = policy["max_contiguous_lookback_exchanges"]
    assert type(completed_exchange_count) is int
    assert type(max_recent) is int
    if recent_count > max_recent:
        raise ScopeProposalSemanticError(
            "recent_exchange_count exceeds host max_contiguous_lookback_exchanges"
        )

    if status in {"REQUEST_RECENT", "REQUEST_TARGETED"} and completed_exchange_count == 0:
        raise ScopeProposalSemanticError(
            "history cannot be requested when completed_exchange_count is 0"
        )

    if status == "SUFFICIENT_WITHOUT_HISTORY":
        if recent_count != 0 or target_terms:
            raise ScopeProposalSemanticError(
                "SUFFICIENT_WITHOUT_HISTORY must request neither recent nor targeted history"
            )
    elif status == "REQUEST_RECENT":
        if recent_count < 1:
            raise ScopeProposalSemanticError(
                "REQUEST_RECENT requires recent_exchange_count >= 1"
            )
        if recent_count > completed_exchange_count:
            raise ScopeProposalSemanticError(
                "recent_exchange_count exceeds completed_exchange_count"
            )
        if target_terms:
            raise ScopeProposalSemanticError(
                "REQUEST_RECENT may not also request targeted terms"
            )
    elif status == "REQUEST_TARGETED":
        if not target_terms:
            raise ScopeProposalSemanticError(
                "REQUEST_TARGETED requires at least one bounded target term"
            )
        if recent_count != 0:
            raise ScopeProposalSemanticError(
                "REQUEST_TARGETED may not also request a contiguous recent lookback"
            )
    else:  # pragma: no cover - schema enum makes this unreachable.
        raise ScopeProposalSemanticError(f"unsupported SCOPE_PROPOSAL status: {status}")

    return output


def require_valid_scope_proposal_output_json(
    payload: str,
    *,
    call_data: JsonValue,
) -> JsonValue:
    """Strictly parse a model response and require the complete proposal contract."""

    parsed = strict_json_loads(payload)
    return require_valid_scope_proposal_output(parsed, call_data=call_data)
