"""Architecturally frozen Recipe 2 model boundaries."""

from __future__ import annotations

from types import MappingProxyType
from typing import Final

from arcadia.contracts.aae.registry import (
    MODE_CONTEXT_EVIDENCE,
    MODE_HOWARD_CONTEXT_FINAL,
    MODE_HOWARD_CONTEXT_LANE,
    get_contract,
)
from arcadia.contracts.schemas.common import (
    array_schema,
    compile_mode_schemas,
    enum_schema,
    object_schema,
    ref_schema,
    refs_schema,
    strings_schema,
    text_schema,
)
from arcadia.core.canonical_json import JsonValue

_CONTEXT_NEED: Final = object_schema(
    {"ref": ref_schema(), "statement": text_schema(minimum=1)}
)
_EVIDENCE_CANDIDATE: Final = object_schema(
    {"evidence_id": ref_schema(), "content": text_schema(minimum=1)}
)
_EVIDENCE_JUDGMENT: Final = object_schema(
    {
        "evidence_id": ref_schema(),
        "status": enum_schema(
            get_contract(MODE_CONTEXT_EVIDENCE).semantic_enums["evidence_status"]
        ),
        "finding": text_schema(minimum=1),
    }
)
_REQUIREMENT: Final = object_schema(
    {"requirement_ref": ref_schema(), "requested_outcome": text_schema(minimum=1)}
)
_CONTEXT_POINT: Final = object_schema(
    {
        "context_id": ref_schema(),
        "statement": text_schema(minimum=1),
        "basis": enum_schema(("supported", "inference", "unresolved")),
    }
)
_SYNTHESIS_ITEM: Final = object_schema(
    {"statement": text_schema(minimum=1), "context_refs": refs_schema(minimum=1)}
)

CONTEXT_EVIDENCE_SCHEMAS: Final = compile_mode_schemas(
    MODE_CONTEXT_EVIDENCE,
    input_properties={
        "context_need": _CONTEXT_NEED,
        "candidates": array_schema(_EVIDENCE_CANDIDATE, minimum=1),
    },
    output_properties={"judgments": array_schema(_EVIDENCE_JUDGMENT, minimum=1)},
)

CONTEXT_LANE_COMMENT_SCHEMAS: Final = compile_mode_schemas(
    MODE_HOWARD_CONTEXT_LANE,
    input_properties={
        "requirements": array_schema(_REQUIREMENT, minimum=1),
        "context_need": _CONTEXT_NEED,
        "validated_judgments": array_schema(_EVIDENCE_JUDGMENT, minimum=1),
    },
    output_properties={
        "context_points": array_schema(
            object_schema(
                {
                    "statement": text_schema(minimum=1),
                    "basis": enum_schema(("supported", "inference", "unresolved")),
                    "evidence_refs": refs_schema(minimum=1),
                }
            )
        )
    },
)

CONTEXT_FINAL_SYNTHESIS_SCHEMAS: Final = compile_mode_schemas(
    MODE_HOWARD_CONTEXT_FINAL,
    input_properties={
        "accepted_requirements": array_schema(_REQUIREMENT, minimum=1),
        "context_points": array_schema(_CONTEXT_POINT),
    },
    output_properties={
        "cross_context": array_schema(_SYNTHESIS_ITEM),
        "conflicts": array_schema(_SYNTHESIS_ITEM),
        "unresolved": array_schema(_SYNTHESIS_ITEM),
        "do_not_assume": strings_schema(),
    },
)

R2_SCHEMAS: Final = MappingProxyType(
    {
        item.mode: item
        for item in (
            CONTEXT_EVIDENCE_SCHEMAS,
            CONTEXT_LANE_COMMENT_SCHEMAS,
            CONTEXT_FINAL_SYNTHESIS_SCHEMAS,
        )
    }
)


class ContextContractSemanticError(ValueError):
    """A Recipe 2 value is schema-valid but violates supplied-reference authority."""


def require_complete_evidence_judgments(
    output: JsonValue, *, call_data: JsonValue
) -> JsonValue:
    CONTEXT_EVIDENCE_SCHEMAS.require_valid_call(call_data)
    CONTEXT_EVIDENCE_SCHEMAS.require_valid_output(output)
    assert type(call_data) is dict and type(output) is dict
    candidates = call_data["candidates"]
    judgments = output["judgments"]
    assert type(candidates) is list and type(judgments) is list
    supplied = [item["evidence_id"] for item in candidates if type(item) is dict]
    returned = [item["evidence_id"] for item in judgments if type(item) is dict]
    if len(returned) != len(set(returned)) or set(returned) != set(supplied):
        raise ContextContractSemanticError(
            "Evidence judgments must cover every supplied evidence ID exactly once"
        )
    return output
