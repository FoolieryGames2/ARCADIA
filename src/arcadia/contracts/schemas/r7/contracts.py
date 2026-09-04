"""Frozen Completion assessor and presentation-compiler boundaries."""

from __future__ import annotations

from types import MappingProxyType
from typing import Final

from arcadia.contracts.aae.registry import (
    MODE_COMPLETION_ASSESSOR,
    MODE_COMPLETION_COMPOSER,
    get_contract,
)
from arcadia.contracts.schemas.common import (
    array_schema,
    compile_mode_schemas,
    enum_schema,
    label_schema,
    object_schema,
    ref_schema,
    refs_schema,
    strings_schema,
    text_schema,
)
from arcadia.core.canonical_json import JsonValue

_SUPPORTED_COMPONENT: Final = object_schema(
    {"statement": text_schema(minimum=1), "basis_refs": refs_schema(minimum=1)}
)
_CLOSURE_ITEM: Final = object_schema(
    {
        "statement": text_schema(minimum=1),
        "basis_refs": refs_schema(minimum=1),
        "kind": label_schema(),
    }
)

COMPLETION_ASSESSMENT_SCHEMAS: Final = compile_mode_schemas(
    MODE_COMPLETION_ASSESSOR,
    input_properties={
        "requirement_closure_bundle": object_schema(
            {
                "requirement_ref": ref_schema(),
                "requested_outcome": text_schema(minimum=1),
                "constraints": strings_schema(),
                "final_context": array_schema(_CLOSURE_ITEM),
                "work_outcomes": array_schema(_CLOSURE_ITEM),
                "reconciliation_findings": array_schema(_CLOSURE_ITEM),
                "persistence_outcomes": array_schema(_CLOSURE_ITEM),
                "remaining_gaps": array_schema(_CLOSURE_ITEM),
                "blockers": array_schema(_CLOSURE_ITEM),
                "failures": array_schema(_CLOSURE_ITEM),
                "closure_signals": array_schema(label_schema(), unique=True),
            }
        ),
        "allowed_terminal_statuses": array_schema(
            enum_schema(
                get_contract(MODE_COMPLETION_ASSESSOR).semantic_enums[
                    "terminal_status"
                ]
            ),
            minimum=4,
            maximum=4,
            unique=True,
        ),
        "completion_policy_snapshot": object_schema(
            {
                "essential_gap_blocks_satisfied": {"type": "boolean", "const": True},
                "failed_persistence_blocks_satisfied": {"type": "boolean", "const": True},
            }
        ),
    },
    output_properties={
        "terminal_status": enum_schema(
            get_contract(MODE_COMPLETION_ASSESSOR).semantic_enums["terminal_status"]
        ),
        "fulfilled_components": array_schema(_SUPPORTED_COMPONENT),
        "unmet_components": array_schema(_SUPPORTED_COMPONENT),
        "blockers": array_schema(_SUPPORTED_COMPONENT),
        "failure_causes": array_schema(_SUPPORTED_COMPONENT),
        "conflict_refs": refs_schema(),
    },
)

_VALIDATED_ASSESSMENT: Final = object_schema(
    {
        "completion_assessment_ref": ref_schema(),
        "requirement_ref": ref_schema(),
        "terminal_status": enum_schema(
            get_contract(MODE_COMPLETION_ASSESSOR).semantic_enums["terminal_status"]
        ),
        "fulfilled_refs": refs_schema(),
        "unmet_refs": refs_schema(),
        "blocker_refs": refs_schema(),
        "failure_refs": refs_schema(),
    }
)

COMPLETION_COMPOSITION_SCHEMAS: Final = compile_mode_schemas(
    MODE_COMPLETION_COMPOSER,
    input_properties={
        "validated_completion_assessments": array_schema(
            _VALIDATED_ASSESSMENT, minimum=1
        ),
        "immutable_requirement_refs": refs_schema(minimum=1),
        "cross_requirement_relationships": array_schema(_SUPPORTED_COMPONENT),
        "host_coverage_signals": object_schema(
            {
                "all_requirements_covered": {"type": "boolean", "const": True},
                "overall_turn_posture": enum_schema(
                    get_contract(MODE_COMPLETION_COMPOSER).semantic_enums[
                        "overall_turn_posture"
                    ]
                ),
            }
        ),
        "completion_policy_snapshot": object_schema(
            {"required_disclosure_classes": array_schema(label_schema(), unique=True)}
        ),
    },
    output_properties={
        "result_focus": array_schema(
            object_schema(
                {
                    "requirement_ref": ref_schema(),
                    "presentation_role": label_schema(),
                }
            )
        ),
        "shared_items": array_schema(_SUPPORTED_COMPONENT),
        "disclosure_emphasis": array_schema(
            object_schema(
                {
                    "source_ref": ref_schema(),
                    "emphasis": enum_schema(("MUST_REPORT", "MAY_REPORT")),
                }
            )
        ),
        "protected_literals": strings_schema(),
        "diagnostics": strings_schema(),
    },
)

R7_SCHEMAS: Final = MappingProxyType(
    {
        item.mode: item
        for item in (COMPLETION_ASSESSMENT_SCHEMAS, COMPLETION_COMPOSITION_SCHEMAS)
    }
)


class CompletionContractSemanticError(ValueError):
    """A Completion output contradicts its terminal standing."""


def require_consistent_completion_assessment(
    output: JsonValue, *, call_data: JsonValue
) -> JsonValue:
    COMPLETION_ASSESSMENT_SCHEMAS.require_valid_call(call_data)
    COMPLETION_ASSESSMENT_SCHEMAS.require_valid_output(output)
    assert type(output) is dict
    status = output["terminal_status"]
    fulfilled = output["fulfilled_components"]
    unmet = output["unmet_components"]
    blockers = output["blockers"]
    failures = output["failure_causes"]
    assert all(type(item) is list for item in (fulfilled, unmet, blockers, failures))
    if status == "SATISFIED" and (unmet or blockers or failures):
        raise CompletionContractSemanticError(
            "SATISFIED may not retain unmet, blocked, or failed components"
        )
    if status == "PARTIALLY_SATISFIED" and (not fulfilled or not unmet):
        raise CompletionContractSemanticError(
            "PARTIALLY_SATISFIED requires fulfilled and unmet components"
        )
    if status == "BLOCKED" and not blockers:
        raise CompletionContractSemanticError("BLOCKED requires a legitimate blocker")
    if status == "FAILED" and not failures:
        raise CompletionContractSemanticError("FAILED requires an actual failure basis")
    return output
