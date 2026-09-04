"""Frozen semantic Persistence assessment and planning boundaries."""

from __future__ import annotations

from types import MappingProxyType
from typing import Final

from arcadia.contracts.aae.registry import (
    MODE_PERSISTENCE_ASSESSOR,
    MODE_PERSISTENCE_COMPOSER,
    get_contract,
)
from arcadia.contracts.schemas.common import (
    HASH_PATTERN,
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
)
from arcadia.core.canonical_json import JsonValue

_MEMORY_ENTITY: Final = object_schema(
    {
        "entity_ref": ref_schema(),
        "canonical_name": text_schema(minimum=1),
        "aliases": strings_schema(),
    }
)
_MEMORY_CLAIM: Final = object_schema(
    {
        "claim_ref": ref_schema(),
        "entity_ref": ref_schema(),
        "predicate": text_schema(minimum=1),
        "value": text_schema(minimum=1),
        "standing": label_schema(),
    }
)
_ASSESSMENT_INPUT_ITEM: Final = object_schema(
    {
        "item_ref": ref_schema(),
        "authority_class": enum_schema(("NORMATIVE", "ADVISORY")),
        "statement": text_schema(minimum=1),
        "provenance_refs": refs_schema(minimum=1),
    }
)

PERSISTENCE_ASSESSMENT_SCHEMAS: Final = compile_mode_schemas(
    MODE_PERSISTENCE_ASSESSOR,
    input_properties={
        "persistence_item": _ASSESSMENT_INPUT_ITEM,
        "relevant_context": array_schema(
            object_schema({"ref": ref_schema(), "statement": text_schema(minimum=1)})
        ),
        "relevant_evidence_findings": array_schema(
            object_schema({"ref": ref_schema(), "statement": text_schema(minimum=1)})
        ),
        "frozen_memory_snapshot": object_schema(
            {
                "snapshot_ref": ref_schema(),
                "snapshot_hash": {"type": "string", "pattern": HASH_PATTERN},
                "memory_commit_seq": {"type": "integer", "minimum": 0},
                "entities": array_schema(_MEMORY_ENTITY),
                "claims": array_schema(_MEMORY_CLAIM),
            }
        ),
        "persistence_policy": object_schema(
            {
                "allow_new_entities": {"type": "boolean"},
                "allow_alias_changes": {"type": "boolean"},
                "max_more_memory_requests": {"type": "integer", "minimum": 0},
            }
        ),
    },
    output_properties={
        "durability_judgment": enum_schema(
            get_contract(MODE_PERSISTENCE_ASSESSOR).semantic_enums[
                "durability_judgment"
            ]
        ),
        "entity_resolution": enum_schema(
            get_contract(MODE_PERSISTENCE_ASSESSOR).semantic_enums["entity_resolution"]
        ),
        "matched_entity_ref": nullable(ref_schema()),
        "semantic_claims": array_schema(
            object_schema(
                {
                    "claim_key": local_key_schema(),
                    "entity_ref": nullable(ref_schema()),
                    "predicate": text_schema(minimum=1),
                    "value": text_schema(minimum=1),
                    "semantic_relation": enum_schema(
                        get_contract(MODE_PERSISTENCE_ASSESSOR).semantic_enums[
                            "semantic_relation"
                        ]
                    ),
                    "provenance_refs": refs_schema(minimum=1),
                }
            )
        ),
        "alias_implications": array_schema(
            object_schema(
                {
                    "alias": text_schema(minimum=1),
                    "entity_ref": nullable(ref_schema()),
                    "relation": label_schema(),
                }
            )
        ),
        "recommended_result": enum_schema(
            ("WRITE", "NO_CHANGE", "IGNORE", "DEFER", "BLOCKED", "POLICY_REJECT")
        ),
        "reason_codes": array_schema(label_schema(), minimum=1, unique=True),
        "provenance_refs": refs_schema(minimum=1),
    },
)

_VALIDATED_ASSESSMENT: Final = object_schema(
    {
        "assessment_ref": ref_schema(),
        "item_ref": ref_schema(),
        "authority_class": enum_schema(("NORMATIVE", "ADVISORY")),
        "recommended_result": enum_schema(
            ("WRITE", "NO_CHANGE", "IGNORE", "DEFER", "BLOCKED", "POLICY_REJECT")
        ),
        "semantic_claims": refs_schema(),
    }
)
_MUTATION: Final = object_schema(
    {
        "mutation_key": local_key_schema(),
        "operation": enum_schema(
            get_contract(MODE_PERSISTENCE_COMPOSER).semantic_enums[
                "mutation_operation"
            ]
        ),
        "target_ref": nullable(ref_schema()),
        "source_refs": refs_schema(minimum=1),
        "value": nullable(text_schema(minimum=1)),
    }
)

PERSISTENCE_COMPOSITION_SCHEMAS: Final = compile_mode_schemas(
    MODE_PERSISTENCE_COMPOSER,
    input_properties={
        "validated_assessments": array_schema(_VALIDATED_ASSESSMENT, minimum=1),
        "normative_obligation_refs": refs_schema(),
        "advisory_candidate_refs": refs_schema(),
        "frozen_memory_base": object_schema(
            {
                "snapshot_ref": ref_schema(),
                "snapshot_hash": {"type": "string", "pattern": HASH_PATTERN},
                "memory_commit_seq": {"type": "integer", "minimum": 0},
            }
        ),
        "semantic_policy": object_schema(
            {
                "allow_entity_merge": {"type": "boolean"},
                "allow_alias_changes": {"type": "boolean"},
            }
        ),
    },
    output_properties={
        "expected_memory_base_commit": {"type": "integer", "minimum": 0},
        "item_results": array_schema(
            object_schema(
                {
                    "item_ref": ref_schema(),
                    "assessment_ref": ref_schema(),
                    "disposition": enum_schema(
                        get_contract(MODE_PERSISTENCE_COMPOSER).semantic_enums[
                            "plan_disposition"
                        ]
                    ),
                    "effect_refs": array_schema(local_key_schema(), unique=True),
                }
            ),
            minimum=1,
        ),
        "new_entities": array_schema(
            object_schema(
                {
                    "entity_key": local_key_schema(),
                    "canonical_name": text_schema(minimum=1),
                    "source_refs": refs_schema(minimum=1),
                }
            )
        ),
        "mutations": array_schema(_MUTATION),
        "transaction_properties": object_schema(
            {
                "atomic": {"type": "boolean", "const": True},
                "stale_base_action": {"type": "string", "const": "ABORT_AND_REEVALUATE"},
            }
        ),
        "provenance_links": array_schema(
            object_schema({"item_ref": ref_schema(), "source_refs": refs_schema(minimum=1)})
        ),
        "diagnostics": strings_schema(),
    },
)

R6_SCHEMAS: Final = MappingProxyType(
    {
        item.mode: item
        for item in (PERSISTENCE_ASSESSMENT_SCHEMAS, PERSISTENCE_COMPOSITION_SCHEMAS)
    }
)


class PersistenceContractSemanticError(ValueError):
    """A Persistence plan violates item coverage or memory-base authority."""


def require_valid_persistence_plan(output: JsonValue, *, call_data: JsonValue) -> JsonValue:
    PERSISTENCE_COMPOSITION_SCHEMAS.require_valid_call(call_data)
    PERSISTENCE_COMPOSITION_SCHEMAS.require_valid_output(output)
    assert type(call_data) is dict and type(output) is dict
    base = call_data["frozen_memory_base"]
    results = output["item_results"]
    assessments = call_data["validated_assessments"]
    assert type(base) is dict and type(results) is list and type(assessments) is list
    if output["expected_memory_base_commit"] != base["memory_commit_seq"]:
        raise PersistenceContractSemanticError("Persistence plan changed the memory base commit")
    expected = [item["item_ref"] for item in assessments if type(item) is dict]
    actual = [item["item_ref"] for item in results if type(item) is dict]
    if len(actual) != len(set(actual)) or set(actual) != set(expected):
        raise PersistenceContractSemanticError(
            "Persistence plan must cover every input item exactly once"
        )
    normative = set(call_data["normative_obligation_refs"])  # type: ignore[arg-type]
    for result in results:
        assert type(result) is dict
        if result["item_ref"] in normative and result["disposition"] in {"IGNORE", "DEFER"}:
            raise PersistenceContractSemanticError(
                "Normative obligations may not be ignored or deferred"
            )
    return output
