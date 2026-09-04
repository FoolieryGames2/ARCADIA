"""Frozen bounded conversational presentation contracts."""

from __future__ import annotations

from types import MappingProxyType
from typing import Final

from arcadia.contracts.aae.registry import (
    MODE_HOWARD_RESULT_COMMENT,
    MODE_HOWARD_RESULT_FINAL,
    get_contract,
)
from arcadia.contracts.schemas.common import (
    array_schema,
    compile_mode_schemas,
    enum_schema,
    object_schema,
    refs_schema,
    strings_schema,
    text_schema,
)
from arcadia.core.canonical_json import JsonValue

RESULT_REQUIREMENT_COMMENT_SCHEMAS: Final = compile_mode_schemas(
    MODE_HOWARD_RESULT_COMMENT,
    input_properties={
        "user_facing_request": text_schema(minimum=1),
        "terminal_status": enum_schema(
            get_contract(MODE_HOWARD_RESULT_COMMENT).semantic_enums["terminal_status"]
        ),
        "established_facts": strings_schema(),
        "unmet_components": strings_schema(),
        "blockers": strings_schema(),
        "failures": strings_schema(),
        "must_mention": strings_schema(),
        "may_mention": strings_schema(),
        "must_not_claim": strings_schema(),
        "protected_literals": strings_schema(),
        "target_comment_length": enum_schema(("concise", "standard")),
    },
    output_properties={"comment": text_schema(minimum=1, maximum=16_384)},
)

RESULT_FINAL_COMPOSE_SCHEMAS: Final = compile_mode_schemas(
    MODE_HOWARD_RESULT_FINAL,
    input_properties={
        "original_request": text_schema(minimum=1),
        "overall_posture": enum_schema(("ALL_SATISFIED", "MIXED", "BLOCKED", "FAILED")),
        "validated_comments": strings_schema(minimum=1),
        "must_mention": strings_schema(),
        "must_not_claim": strings_schema(),
        "protected_literals": strings_schema(),
        "response_budget": object_schema(
            {
                "presentation": enum_schema(("concise", "standard")),
                "max_characters": {"type": "integer", "minimum": 1, "maximum": 65_536},
            }
        ),
        "publication_constraints": object_schema(
            {
                "internal_ref_patterns": array_schema(text_schema(minimum=1), unique=True),
                "required_disclosure_refs": refs_schema(),
            }
        ),
    },
    output_properties={"final_response_text": text_schema(minimum=1)},
)

R8_SCHEMAS: Final = MappingProxyType(
    {
        item.mode: item
        for item in (RESULT_REQUIREMENT_COMMENT_SCHEMAS, RESULT_FINAL_COMPOSE_SCHEMAS)
    }
)


class ResultContractSemanticError(ValueError):
    """A Result draft violates deterministic disclosure or literal gates."""


def require_valid_result_text(output: JsonValue, *, call_data: JsonValue) -> JsonValue:
    RESULT_FINAL_COMPOSE_SCHEMAS.require_valid_call(call_data)
    RESULT_FINAL_COMPOSE_SCHEMAS.require_valid_output(output)
    assert type(call_data) is dict and type(output) is dict
    response = output["final_response_text"]
    budget = call_data["response_budget"]
    assert type(response) is str and type(budget) is dict
    if len(response) > budget["max_characters"]:  # type: ignore[operator]
        raise ResultContractSemanticError("final response exceeds host response budget")
    for literal in call_data["protected_literals"]:  # type: ignore[union-attr]
        if literal not in response:  # type: ignore[operator]
            raise ResultContractSemanticError(f"protected literal is missing: {literal}")
    for required in call_data["must_mention"]:  # type: ignore[union-attr]
        if required not in response:  # type: ignore[operator]
            raise ResultContractSemanticError(f"required disclosure is missing: {required}")
    return output
