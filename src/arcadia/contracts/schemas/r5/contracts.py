"""Frozen Reconciliation assessment and composition boundaries."""

from __future__ import annotations

from types import MappingProxyType
from typing import Final

from arcadia.contracts.aae.registry import (
    MODE_EVIDENCE_RECONCILER,
    MODE_RECONCILIATION_COMPOSER,
    get_contract,
)
from arcadia.contracts.schemas.common import (
    array_schema,
    compile_mode_schemas,
    enum_schema,
    label_schema,
    local_key_schema,
    object_schema,
    ref_schema,
    refs_schema,
    strings_schema,
    text_schema,
)
from arcadia.core.canonical_json import JsonValue

_REF_TEXT: Final = object_schema(
    {"ref": ref_schema(), "text": text_schema(minimum=1)}
)
_FINDING_ITEM: Final = object_schema(
    {
        "statement": text_schema(minimum=1),
        "support_refs": refs_schema(minimum=1),
        "confidence_label": enum_schema(
            get_contract(MODE_EVIDENCE_RECONCILER).semantic_enums["confidence_label"]
        ),
        "provenance_class": enum_schema(
            get_contract(MODE_EVIDENCE_RECONCILER).semantic_enums["provenance_class"]
        ),
    }
)
_GAP: Final = object_schema(
    {
        "target": text_schema(minimum=1),
        "reason": text_schema(minimum=1),
        "evidence_refs": refs_schema(),
    }
)
_CONFLICT: Final = object_schema(
    {"statement": text_schema(minimum=1), "evidence_refs": refs_schema(minimum=2)}
)

EVIDENCE_RECONCILIATION_SCHEMAS: Final = compile_mode_schemas(
    MODE_EVIDENCE_RECONCILER,
    input_properties={
        "work_item": object_schema(
            {"work_ref": ref_schema(), "goal": text_schema(minimum=1)}
        ),
        "evidence_target": strings_schema(minimum=1),
        "requirement_refs": refs_schema(minimum=1),
        "immutable_execution_receipts": array_schema(_REF_TEXT, minimum=1),
        "result_items": array_schema(_REF_TEXT),
        "relevant_active_context": array_schema(_REF_TEXT),
        "host_signal_pack": object_schema(
            {
                "verified_receipt_refs": refs_schema(minimum=1),
                "failed_receipt_refs": refs_schema(),
                "unknown_outcome_refs": refs_schema(),
            }
        ),
    },
    output_properties={
        "semantic_state": enum_schema(
            get_contract(MODE_EVIDENCE_RECONCILER).semantic_enums["semantic_state"]
        ),
        "established_claims": array_schema(_FINDING_ITEM),
        "not_established_targets": array_schema(_GAP),
        "conflicts": array_schema(_CONFLICT),
        "material_discoveries": array_schema(_FINDING_ITEM),
        "context_impacts": array_schema(_FINDING_ITEM),
        "immutable_execution_basis": refs_schema(minimum=1),
    },
)

_EVIDENCE_FINDING: Final = object_schema(
    {
        "finding_ref": ref_schema(),
        "work_ref": ref_schema(),
        "requirement_refs": refs_schema(minimum=1),
        "semantic_state": enum_schema(
            get_contract(MODE_EVIDENCE_RECONCILER).semantic_enums["semantic_state"]
        ),
        "statements": array_schema(_FINDING_ITEM),
        "gaps": array_schema(_GAP),
        "conflicts": array_schema(_CONFLICT),
    }
)
_CONSEQUENCE: Final = object_schema(
    {
        "consequence_key": local_key_schema(),
        "consequence_class": enum_schema(
            get_contract(MODE_RECONCILIATION_COMPOSER).semantic_enums[
                "consequence_class"
            ]
        ),
        "statement": text_schema(minimum=1),
        "source_refs": refs_schema(minimum=1),
    }
)

RECONCILIATION_COMPOSITION_SCHEMAS: Final = compile_mode_schemas(
    MODE_RECONCILIATION_COMPOSER,
    input_properties={
        "validated_evidence_findings": array_schema(_EVIDENCE_FINDING, minimum=1),
        "active_context": array_schema(_REF_TEXT),
        "immutable_requirement_scope": array_schema(_REF_TEXT, minimum=1),
        "prior_reconciliation_state": array_schema(_REF_TEXT),
    },
    output_properties={
        "posture_flags": array_schema(
            enum_schema(
                get_contract(MODE_RECONCILIATION_COMPOSER).semantic_enums[
                    "posture_flag"
                ]
            ),
            minimum=1,
            unique=True,
        ),
        "remaining_gaps": array_schema(_GAP),
        "conflicts": array_schema(_CONFLICT),
        "consequences": array_schema(_CONSEQUENCE),
        "recommended_transitions": array_schema(
            object_schema(
                {
                    "consequence_key": local_key_schema(),
                    "transition": label_schema(),
                }
            )
        ),
        "diagnostics": strings_schema(),
    },
)

R5_SCHEMAS: Final = MappingProxyType(
    {
        item.mode: item
        for item in (EVIDENCE_RECONCILIATION_SCHEMAS, RECONCILIATION_COMPOSITION_SCHEMAS)
    }
)


class ReconciliationContractSemanticError(ValueError):
    """A Reconciliation output contradicts its declared semantic state."""


def require_valid_evidence_finding(output: JsonValue, *, call_data: JsonValue) -> JsonValue:
    EVIDENCE_RECONCILIATION_SCHEMAS.require_valid_call(call_data)
    EVIDENCE_RECONCILIATION_SCHEMAS.require_valid_output(output)
    assert type(call_data) is dict and type(output) is dict
    state = output["semantic_state"]
    claims = output["established_claims"]
    gaps = output["not_established_targets"]
    conflicts = output["conflicts"]
    basis = output["immutable_execution_basis"]
    assert all(type(item) is list for item in (claims, gaps, conflicts, basis))
    if state == "ESTABLISHED" and not claims:
        raise ReconciliationContractSemanticError("ESTABLISHED requires a supported claim")
    if state == "NOT_ESTABLISHED" and not gaps:
        raise ReconciliationContractSemanticError(
            "NOT_ESTABLISHED requires a not-established target"
        )
    if state == "CONFLICT" and not conflicts:
        raise ReconciliationContractSemanticError("CONFLICT requires conflict evidence")
    raw_receipts = call_data["immutable_execution_receipts"]
    assert type(raw_receipts) is list and type(basis) is list
    supplied_receipts = {
        item["ref"]
        for item in raw_receipts
        if type(item) is dict
    }
    if not set(basis).issubset(supplied_receipts):
        raise ReconciliationContractSemanticError(
            "immutable execution basis must cite supplied receipts"
        )
    return output
