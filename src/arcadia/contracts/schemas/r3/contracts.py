"""Architecturally frozen Requirement Assessor and Plan Composer boundaries."""

from __future__ import annotations

from types import MappingProxyType
from typing import Final

from arcadia.contracts.aae.registry import (
    MODE_PLAN_COMPOSER,
    MODE_REQUIREMENT_ASSESSOR,
    get_contract,
)
from arcadia.contracts.schemas.common import (
    array_schema,
    compile_mode_schemas,
    enum_schema,
    label_schema,
    local_key_schema,
    nullable,
    object_schema,
    ref_schema,
    refs_schema,
    strings_schema,
    text_schema,
    token_schema,
)
from arcadia.core.canonical_json import JsonValue

_CONTEXT_POINT: Final = object_schema(
    {
        "context_id": ref_schema(),
        "statement": text_schema(minimum=1),
        "basis": enum_schema(("supported", "inference", "unresolved")),
    }
)
_WORK_NEED_PROPOSAL: Final = object_schema(
    {
        "work_type": label_schema(),
        "goal": text_schema(minimum=1),
        "evidence_target": strings_schema(minimum=1),
    }
)
_BLOCKER: Final = object_schema(
    {
        "reason": enum_schema(
            get_contract(MODE_REQUIREMENT_ASSESSOR).semantic_enums["block_reason"]
        ),
        "detail": text_schema(minimum=1),
    }
)

REQUIREMENT_ASSESSMENT_SCHEMAS: Final = compile_mode_schemas(
    MODE_REQUIREMENT_ASSESSOR,
    input_properties={
        "requirement": object_schema(
            {
                "requirement_id": ref_schema(),
                "requested_outcome": text_schema(minimum=1),
                "constraints": strings_schema(),
            }
        ),
        "relevant_context": array_schema(_CONTEXT_POINT),
        "context_boundaries": object_schema(
            {
                "conflicts": strings_schema(),
                "unresolved": strings_schema(),
                "do_not_assume": strings_schema(),
            }
        ),
        "capability_availability": array_schema(
            object_schema(
                {
                    "capability_class": label_schema(),
                    "available": {"type": "boolean"},
                }
            )
        ),
        "prior_requirement_state": nullable(
            object_schema(
                {
                    "disposition": enum_schema(
                        get_contract(MODE_REQUIREMENT_ASSESSOR).semantic_enums["disposition"]
                    ),
                    "remaining_work": text_schema(minimum=1),
                    "work_origin": enum_schema(("ORIGINAL", "DISCOVERY", "REPAIR")),
                }
            )
        ),
        "reentry": nullable(
            object_schema(
                {
                    "trigger_ref": ref_schema(),
                    "work_origin": enum_schema(("ORIGINAL", "DISCOVERY", "REPAIR")),
                }
            )
        ),
    },
    output_properties={
        "disposition": enum_schema(
            get_contract(MODE_REQUIREMENT_ASSESSOR).semantic_enums["disposition"]
        ),
        "basis_refs": refs_schema(),
        "need_summary": text_schema(minimum=1),
        "work_needs": array_schema(_WORK_NEED_PROPOSAL),
        "post_work_obligations": strings_schema(),
        "blocker": nullable(_BLOCKER),
    },
)

_NORMALIZED_WORK_NEED: Final = object_schema(
    {
        "work_need_ref": ref_schema(),
        "work_type": label_schema(),
        "goal": text_schema(minimum=1),
        "evidence_target": strings_schema(minimum=1),
    }
)
_ASSESSMENT: Final = object_schema(
    {
        "requirement_ref": ref_schema(),
        "disposition": enum_schema(
            get_contract(MODE_REQUIREMENT_ASSESSOR).semantic_enums["disposition"]
        ),
        "basis_refs": refs_schema(),
        "need_summary": text_schema(minimum=1),
        "work_needs": array_schema(_NORMALIZED_WORK_NEED),
        "post_work_obligations": strings_schema(),
    }
)
_CAPABILITY: Final = object_schema(
    {
        "capability_id": token_schema(),
        "capability_class": label_schema(),
        "available": {"type": "boolean"},
        "effect": enum_schema(("READ_ONLY", "STATE_CHANGING")),
        "accepts": array_schema(label_schema(), unique=True),
        "produces": array_schema(label_schema(), unique=True),
    }
)
_PLAN_NODE: Final = object_schema(
    {
        "node_key": local_key_schema(),
        "requirement_refs": refs_schema(minimum=1),
        "work_need_refs": refs_schema(minimum=1),
        "goal": text_schema(minimum=1),
        "capability_id": token_schema(),
        "depends_on": array_schema(local_key_schema(), unique=True),
        "work_origin": enum_schema(("ORIGINAL", "DISCOVERY", "REPAIR")),
    }
)

PLAN_COMPOSITION_SCHEMAS: Final = compile_mode_schemas(
    MODE_PLAN_COMPOSER,
    input_properties={
        "assessments": array_schema(_ASSESSMENT, minimum=1),
        "capabilities": array_schema(_CAPABILITY),
        "prior_work": array_schema(
            object_schema(
                {
                    "work_ref": ref_schema(),
                    "goal": text_schema(minimum=1),
                    "work_origin": enum_schema(("ORIGINAL", "DISCOVERY", "REPAIR")),
                }
            )
        ),
        "reentry": nullable(
            object_schema({"trigger_ref": ref_schema(), "scope_refs": refs_schema(minimum=1)})
        ),
    },
    output_properties={"nodes": array_schema(_PLAN_NODE)},
)

R3_SCHEMAS: Final = MappingProxyType(
    {
        item.mode: item
        for item in (REQUIREMENT_ASSESSMENT_SCHEMAS, PLAN_COMPOSITION_SCHEMAS)
    }
)


class DecisionContractSemanticError(ValueError):
    """A Decision contract violates disposition or graph authority."""


def require_valid_requirement_assessment(
    output: JsonValue, *, call_data: JsonValue
) -> JsonValue:
    REQUIREMENT_ASSESSMENT_SCHEMAS.require_valid_call(call_data)
    REQUIREMENT_ASSESSMENT_SCHEMAS.require_valid_output(output)
    assert type(output) is dict
    disposition = output["disposition"]
    needs = output["work_needs"]
    blocker = output["blocker"]
    obligations = output["post_work_obligations"]
    assert type(disposition) is str and type(needs) is list and type(obligations) is list
    if disposition == "WORK_REQUIRED" and not needs:
        raise DecisionContractSemanticError("WORK_REQUIRED requires at least one work need")
    if disposition != "WORK_REQUIRED" and needs:
        raise DecisionContractSemanticError(f"{disposition} may not propose executable work")
    if disposition == "BLOCKED" and blocker is None:
        raise DecisionContractSemanticError("BLOCKED requires an allowed blocker")
    if disposition != "BLOCKED" and blocker is not None:
        raise DecisionContractSemanticError(f"{disposition} may not carry a blocker")
    if disposition == "READY" and obligations:
        raise DecisionContractSemanticError("READY may not retain a Persistence obligation")
    if disposition == "PERSISTENCE_REQUIRED" and not obligations:
        raise DecisionContractSemanticError(
            "PERSISTENCE_REQUIRED requires a post-work obligation"
        )
    return output


def require_valid_plan_graph(output: JsonValue, *, call_data: JsonValue) -> JsonValue:
    PLAN_COMPOSITION_SCHEMAS.require_valid_call(call_data)
    PLAN_COMPOSITION_SCHEMAS.require_valid_output(output)
    assert type(call_data) is dict and type(output) is dict
    nodes = output["nodes"]
    assessments = call_data["assessments"]
    capabilities = call_data["capabilities"]
    assert type(nodes) is list and type(assessments) is list and type(capabilities) is list
    node_keys = [node["node_key"] for node in nodes if type(node) is dict]
    if len(node_keys) != len(set(node_keys)):
        raise DecisionContractSemanticError("Plan node keys must be unique")
    legal_capabilities = {
        item["capability_id"]
        for item in capabilities
        if type(item) is dict and item["available"] is True
    }
    required_work_needs: set[JsonValue] = set()
    for assessment in assessments:
        if type(assessment) is not dict or assessment["disposition"] != "WORK_REQUIRED":
            continue
        work_needs = assessment["work_needs"]
        assert type(work_needs) is list
        required_work_needs.update(
            need["work_need_ref"] for need in work_needs if type(need) is dict
        )
    covered: list[JsonValue] = []
    dependencies: dict[str, list[str]] = {}
    for node in nodes:
        assert type(node) is dict and type(node["work_need_refs"]) is list
        if node["capability_id"] not in legal_capabilities:
            raise DecisionContractSemanticError("Plan selects an unavailable capability")
        covered.extend(node["work_need_refs"])
        key = node["node_key"]
        raw_dependencies = node["depends_on"]
        assert type(key) is str and type(raw_dependencies) is list
        dependencies[key] = [str(item) for item in raw_dependencies]
    if len(covered) != len(set(covered)) or set(covered) != required_work_needs:
        raise DecisionContractSemanticError(
            "Plan must cover every WORK_REQUIRED work need exactly once"
        )
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(key: str) -> None:
        if key in visiting:
            raise DecisionContractSemanticError("Plan dependency graph must be acyclic")
        if key in visited:
            return
        if key not in dependencies:
            raise DecisionContractSemanticError("Plan dependency references an unknown node")
        visiting.add(key)
        for dependency in dependencies[key]:
            visit(dependency)
        visiting.remove(key)
        visited.add(key)

    for raw_key in node_keys:
        assert type(raw_key) is str
        visit(raw_key)
    return output
