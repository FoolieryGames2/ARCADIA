"""Strict PRE-1 schemas and host semantic checks for Recipe 0 SCOPE_VALIDATION."""

from __future__ import annotations

from typing import Final

from arcadia.contracts.aae.registry import MODE_SCOPE_VALIDATION, get_contract
from arcadia.contracts.policies.schema_rules import require_fixed_top_level_output_shape
from arcadia.contracts.policies.vocabulary import MACHINE_LABEL_PATTERN_PRE_V1
from arcadia.core.canonical_json import JsonValue, strict_json_loads
from arcadia.core.hashing import Sha256Digest, sha256_text
from arcadia.core.validation import JSON_SCHEMA_DIALECT, StrictJsonSchema, compile_strict_schema

# Local PRE-version safety caps. These keep this executable contract bounded without
# claiming to complete/freeze the later shared settings profiles (TODO item 6).
PRE1_MAX_RAW_PROMPT_CHARS: Final = 65_536
PRE1_MAX_RETRIEVED_TURNS: Final = 64
PRE1_MAX_TURN_TEXT_CHARS: Final = 65_536
PRE1_MAX_REASON_CODES: Final = 16
PRE1_MAX_REASON_CODE_CHARS: Final = 64
PRE1_MAX_UNRESOLVED_REFERENCES: Final = 16
PRE1_MAX_UNRESOLVED_REFERENCE_CHARS: Final = 512

_CANONICAL_TOKEN_PATTERN: Final = r"^[A-Za-z0-9][A-Za-z0-9._:+/\-]{0,127}$"
_SHA256_PATTERN: Final = r"^sha256:[0-9a-f]{64}$"
_REASON_CODE_PATTERN: Final = MACHINE_LABEL_PATTERN_PRE_V1

_SCOPE_CONTRACT: Final = get_contract(MODE_SCOPE_VALIDATION)
_VALIDATION_OUTCOME: Final = _SCOPE_CONTRACT.semantic_enums["validation_outcome"]

_INPUT_SCHEMA_VALUE: Final[dict[str, object]] = {
    "$schema": JSON_SCHEMA_DIALECT,
    "type": "object",
    "additionalProperties": False,
    "required": [
        "mode",
        "turn_uuid",
        "conversation_uuid",
        "raw_user_prompt",
        "frozen_retrieved_turns",
        "host_policy_limits",
    ],
    "properties": {
        "mode": {"type": "string", "const": MODE_SCOPE_VALIDATION},
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
        "raw_user_prompt": {"type": "string", "maxLength": PRE1_MAX_RAW_PROMPT_CHARS},
        "frozen_retrieved_turns": {
            "type": "array",
            "minItems": 1,
            "maxItems": PRE1_MAX_RETRIEVED_TURNS,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "turn_uuid",
                    "turn_index",
                    "user_message",
                    "final_response",
                    "user_message_hash",
                    "final_response_hash",
                ],
                "properties": {
                    "turn_uuid": {
                        "type": "string",
                        "minLength": 1,
                        "maxLength": 128,
                        "pattern": _CANONICAL_TOKEN_PATTERN,
                    },
                    "turn_index": {"type": "integer", "minimum": 0},
                    "user_message": {
                        "type": "string",
                        "maxLength": PRE1_MAX_TURN_TEXT_CHARS,
                    },
                    "final_response": {
                        "type": "string",
                        "maxLength": PRE1_MAX_TURN_TEXT_CHARS,
                    },
                    "user_message_hash": {
                        "type": "string",
                        "pattern": _SHA256_PATTERN,
                    },
                    "final_response_hash": {
                        "type": "string",
                        "pattern": _SHA256_PATTERN,
                    },
                },
            },
        },
        "host_policy_limits": {
            "type": "object",
            "additionalProperties": False,
            "required": [
                "remaining_expansion_cycles",
                "max_total_injected_history_tokens",
            ],
            "properties": {
                "remaining_expansion_cycles": {"type": "integer", "minimum": 0},
                "max_total_injected_history_tokens": {"type": "integer", "minimum": 1},
            },
        },
    },
}

_OUTPUT_SCHEMA_VALUE: Final[dict[str, object]] = {
    "$schema": JSON_SCHEMA_DIALECT,
    "type": "object",
    "additionalProperties": False,
    "required": ["mode", "status", "reason_codes", "unresolved_references"],
    "properties": {
        "mode": {"type": "string", "const": MODE_SCOPE_VALIDATION},
        "status": {
            "type": "string",
            "enum": list(_VALIDATION_OUTCOME),
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
        "unresolved_references": {
            "type": "array",
            "maxItems": PRE1_MAX_UNRESOLVED_REFERENCES,
            "uniqueItems": True,
            "items": {
                "type": "string",
                "minLength": 1,
                "maxLength": PRE1_MAX_UNRESOLVED_REFERENCE_CHARS,
            },
        },
    },
}

SCOPE_VALIDATION_INPUT_SCHEMA: Final[StrictJsonSchema] = compile_strict_schema(
    schema_id=_SCOPE_CONTRACT.input_schema.schema_id,
    schema_version=_SCOPE_CONTRACT.input_schema.schema_version,
    schema=_INPUT_SCHEMA_VALUE,
)
SCOPE_VALIDATION_OUTPUT_SCHEMA: Final[StrictJsonSchema] = require_fixed_top_level_output_shape(
    compile_strict_schema(
        schema_id=_SCOPE_CONTRACT.output_schema.schema_id,
        schema_version=_SCOPE_CONTRACT.output_schema.schema_version,
        schema=_OUTPUT_SCHEMA_VALUE,
    )
)


class ScopeValidationSemanticError(ValueError):
    """Schema-valid SCOPE_VALIDATION data violates the bounded Recipe-0 contract."""


def _require_object(value: JsonValue, label: str) -> dict[str, JsonValue]:
    if type(value) is not dict:
        raise ScopeValidationSemanticError(f"{label} must be a JSON object")
    return value


def _require_frozen_turn_integrity(call_obj: dict[str, JsonValue]) -> None:
    current_turn_uuid = call_obj["turn_uuid"]
    turns = call_obj["frozen_retrieved_turns"]
    assert type(current_turn_uuid) is str
    assert type(turns) is list

    seen_turn_uuids: set[str] = set()
    previous_turn_index: int | None = None

    for index, raw_turn in enumerate(turns):
        turn = _require_object(raw_turn, f"frozen_retrieved_turns[{index}]")
        turn_uuid = turn["turn_uuid"]
        turn_index = turn["turn_index"]
        user_message = turn["user_message"]
        final_response = turn["final_response"]
        user_message_hash = turn["user_message_hash"]
        final_response_hash = turn["final_response_hash"]
        assert type(turn_uuid) is str
        assert type(turn_index) is int
        assert type(user_message) is str
        assert type(final_response) is str
        assert type(user_message_hash) is str
        assert type(final_response_hash) is str

        if turn_uuid == current_turn_uuid:
            raise ScopeValidationSemanticError(
                "frozen_retrieved_turns may contain only prior turns, not the current turn_uuid"
            )
        if turn_uuid in seen_turn_uuids:
            raise ScopeValidationSemanticError(
                "frozen_retrieved_turns may not repeat a turn_uuid"
            )
        seen_turn_uuids.add(turn_uuid)

        if previous_turn_index is not None and turn_index <= previous_turn_index:
            raise ScopeValidationSemanticError(
                "frozen_retrieved_turns must be in strictly increasing chronological turn_index order"
            )
        previous_turn_index = turn_index

        if sha256_text(user_message) != Sha256Digest(user_message_hash):
            raise ScopeValidationSemanticError(
                f"frozen_retrieved_turns[{index}] user_message_hash does not match exact text"
            )
        if sha256_text(final_response) != Sha256Digest(final_response_hash):
            raise ScopeValidationSemanticError(
                f"frozen_retrieved_turns[{index}] final_response_hash does not match exact text"
            )


def require_valid_scope_validation_call_data(call_data: JsonValue) -> JsonValue:
    """Require strict CALL_DATA and verify frozen transcript evidence integrity."""

    SCOPE_VALIDATION_INPUT_SCHEMA.require_valid(call_data)
    call_obj = _require_object(call_data, "scope validation CALL_DATA")
    _require_frozen_turn_integrity(call_obj)
    return call_data


def require_valid_scope_validation_output(
    output: JsonValue,
    *,
    call_data: JsonValue,
) -> JsonValue:
    """Require one legal validation verdict without allowing a dead-end expansion branch."""

    require_valid_scope_validation_call_data(call_data)
    SCOPE_VALIDATION_OUTPUT_SCHEMA.require_valid(output)

    output_obj = _require_object(output, "scope validation output")
    call_obj = _require_object(call_data, "scope validation CALL_DATA")
    policy = _require_object(call_obj["host_policy_limits"], "host_policy_limits")

    status = output_obj["status"]
    unresolved = output_obj["unresolved_references"]
    remaining_cycles = policy["remaining_expansion_cycles"]
    assert type(status) is str
    assert type(unresolved) is list
    assert type(remaining_cycles) is int

    if status in {"SUFFICIENT", "SUFFICIENT_WITHOUT_HISTORY"}:
        if unresolved:
            raise ScopeValidationSemanticError(
                f"{status} requires unresolved_references to be empty"
            )
    else:
        if not unresolved:
            raise ScopeValidationSemanticError(
                f"{status} requires at least one unresolved reference"
            )

    if status in {"NEEDS_MORE_RECENT", "NEEDS_TARGETED_HISTORY"} and remaining_cycles == 0:
        raise ScopeValidationSemanticError(
            "additional transcript scope cannot be requested when remaining_expansion_cycles is 0"
        )

    return output


def require_valid_scope_validation_output_json(
    payload: str,
    *,
    call_data: JsonValue,
) -> JsonValue:
    """Strictly parse a model response and require the complete validation contract."""

    parsed = strict_json_loads(payload)
    return require_valid_scope_validation_output(parsed, call_data=call_data)
