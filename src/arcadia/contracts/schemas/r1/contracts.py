"""Frozen-shape Recipe 1 contracts; Intent authority remains host-validated."""

from __future__ import annotations

from types import MappingProxyType
from typing import Final

from arcadia.contracts.aae.registry import (
    MODE_HOWARD_INTENT_COMMENT,
    MODE_INTENT_ORGANIZER,
    MODE_PROMPT_ANALYSIS,
    MODE_SPELL,
    MODE_TERM_MEANING,
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
    token_schema,
)
from arcadia.core.canonical_json import JsonValue

_SPAN: Final = object_schema(
    {
        "span_ref": ref_schema(),
        "text": text_schema(minimum=1),
        "start": {"type": "integer", "minimum": 0},
        "end": {"type": "integer", "minimum": 0},
        "kind": label_schema(),
    }
)
_EDIT: Final = object_schema(
    {
        "start": {"type": "integer", "minimum": 0},
        "end": {"type": "integer", "minimum": 0},
        "source": text_schema(minimum=1),
        "replacement": text_schema(minimum=1),
    }
)
_UNCERTAIN_EDIT: Final = object_schema(
    {
        "start": {"type": "integer", "minimum": 0},
        "end": {"type": "integer", "minimum": 0},
        "source": text_schema(minimum=1),
        "candidates": strings_schema(minimum=1),
    }
)
_MEANING_RECORD: Final = object_schema(
    {
        "term_key": local_key_schema(),
        "source_ref": ref_schema(),
        "surface": text_schema(minimum=1),
        "type_guess": label_schema(),
        "current_use_guess": text_schema(minimum=1),
        "meaning_status": enum_schema(("provisional", "unresolved")),
        "context_lookup_needed": {"type": "boolean"},
        "confidence": {"type": "number", "minimum": 0, "maximum": 1},
    }
)
_COMMUNICATION_ITEM: Final = object_schema(
    {"text": text_schema(minimum=1), "source_refs": refs_schema(minimum=1)}
)

SPELL_SCHEMAS: Final = compile_mode_schemas(
    MODE_SPELL,
    input_properties={"raw_prompt": text_schema()},
    output_properties={
        "raw_prompt": text_schema(),
        "normalized_prompt": text_schema(),
        "spell_edits": array_schema(_EDIT),
        "uncertain_corrections": array_schema(_UNCERTAIN_EDIT),
    },
)

TERM_MEANING_SCHEMAS: Final = compile_mode_schemas(
    MODE_TERM_MEANING,
    input_properties={
        "raw_prompt": text_schema(),
        "normalized_prompt": text_schema(),
        "spell_uncertainties": array_schema(_UNCERTAIN_EDIT),
        "host_linguistic_map": object_schema({"source_spans": array_schema(_SPAN)}),
        "r0_transcript_evidence": array_schema(
            object_schema(
                {
                    "turn_uuid": token_schema(),
                    "user_message": text_schema(),
                    "final_response": text_schema(),
                }
            )
        ),
    },
    output_properties={
        "terms": array_schema(_MEANING_RECORD),
        "unresolved_references": array_schema(_COMMUNICATION_ITEM),
    },
)

PROMPT_ANALYSIS_SCHEMAS: Final = compile_mode_schemas(
    MODE_PROMPT_ANALYSIS,
    input_properties={
        "raw_prompt": text_schema(),
        "normalized_prompt": text_schema(),
        "meaning_artifact": object_schema(
            {
                "terms": array_schema(_MEANING_RECORD),
                "unresolved_references": array_schema(_COMMUNICATION_ITEM),
            }
        ),
        "host_source_spans": array_schema(_SPAN),
    },
    output_properties={
        "topics": array_schema(_COMMUNICATION_ITEM),
        "goals": array_schema(_COMMUNICATION_ITEM),
        "tasks": array_schema(_COMMUNICATION_ITEM),
        "statements": array_schema(_COMMUNICATION_ITEM),
        "questions": array_schema(_COMMUNICATION_ITEM),
        "directions": array_schema(_COMMUNICATION_ITEM),
        "approvals": array_schema(_COMMUNICATION_ITEM),
        "interaction_mode": enum_schema(
            get_contract(MODE_PROMPT_ANALYSIS).semantic_enums["interaction_mode"]
        ),
        "important_claims": array_schema(_COMMUNICATION_ITEM),
        "unresolved_items": array_schema(_COMMUNICATION_ITEM),
        "control_signals": array_schema(
            object_schema(
                {
                    "signal": enum_schema(
                        get_contract(MODE_PROMPT_ANALYSIS).semantic_enums["control_signal"]
                    ),
                    "source_refs": refs_schema(minimum=1),
                }
            )
        ),
    },
)

_REQUIREMENT_PROPOSAL: Final = object_schema(
    {
        "requirement_key": local_key_schema(),
        "requested_outcome": text_schema(minimum=1),
        "constraints": strings_schema(),
        "source_refs": refs_schema(minimum=1),
        "depends_on": array_schema(local_key_schema(), unique=True),
        "group": label_schema(),
        "priority": {"type": "integer", "minimum": 0, "maximum": 100},
        "context_needs": strings_schema(),
        "capability_candidates": array_schema(token_schema(), unique=True),
        "memory_candidates": strings_schema(),
    }
)

INTENT_ORGANIZER_SCHEMAS: Final = compile_mode_schemas(
    MODE_INTENT_ORGANIZER,
    input_properties={
        "meaning_artifact": object_schema(
            {
                "terms": array_schema(_MEANING_RECORD),
                "unresolved_references": array_schema(_COMMUNICATION_ITEM),
            }
        ),
        "prompt_analysis_artifact": PROMPT_ANALYSIS_SCHEMAS.output.schema_value(),
        "current_turn_source_refs": array_schema(_SPAN),
        "capability_availability": array_schema(
            object_schema(
                {
                    "capability_id": token_schema(),
                    "capability_class": label_schema(),
                    "available": {"type": "boolean"},
                }
            )
        ),
    },
    output_properties={
        "primary_intent": text_schema(minimum=1),
        "secondary_intents": strings_schema(),
        "requirements": array_schema(_REQUIREMENT_PROPOSAL, minimum=1),
        "clarification_required": {"type": "boolean"},
        "context_resolution_first": {"type": "boolean"},
        "unresolved_blockers": strings_schema(),
        "control_signals": array_schema(
            object_schema(
                {
                    "signal": enum_schema(
                        get_contract(MODE_PROMPT_ANALYSIS).semantic_enums["control_signal"]
                    ),
                    "source_refs": refs_schema(minimum=1),
                }
            )
        ),
    },
)

INTENT_COMMENT_SCHEMAS: Final = compile_mode_schemas(
    MODE_HOWARD_INTENT_COMMENT,
    input_properties={
        "accepted_intent_projection": object_schema(
            {
                "primary_intent": text_schema(minimum=1),
                "requirements": array_schema(
                    object_schema(
                        {
                            "requirement_ref": ref_schema(),
                            "requested_outcome": text_schema(minimum=1),
                            "source_refs": refs_schema(minimum=1),
                        }
                    ),
                    minimum=1,
                ),
            }
        )
    },
    output_properties={"comment": text_schema(minimum=1)},
)

R1_SCHEMAS: Final = MappingProxyType(
    {
        item.mode: item
        for item in (
            SPELL_SCHEMAS,
            TERM_MEANING_SCHEMAS,
            PROMPT_ANALYSIS_SCHEMAS,
            INTENT_ORGANIZER_SCHEMAS,
            INTENT_COMMENT_SCHEMAS,
        )
    }
)


class IntentContractSemanticError(ValueError):
    """A Recipe 1 value is schema-valid but violates a host-owned invariant."""


def require_valid_spell_output(output: JsonValue, *, call_data: JsonValue) -> JsonValue:
    SPELL_SCHEMAS.require_valid_call(call_data)
    SPELL_SCHEMAS.require_valid_output(output)
    assert type(call_data) is dict and type(output) is dict
    if output["raw_prompt"] != call_data["raw_prompt"]:
        raise IntentContractSemanticError("Spell raw_prompt must exactly match supplied text")
    raw = call_data["raw_prompt"]
    assert type(raw) is str
    for collection in (output["spell_edits"], output["uncertain_corrections"]):
        assert type(collection) is list
        for item in collection:
            assert type(item) is dict
            start, end = item["start"], item["end"]
            source = item["source"]
            assert type(start) is int and type(end) is int and type(source) is str
            if start > end or end > len(raw) or raw[start:end] != source:
                raise IntentContractSemanticError("Spell edit span must match supplied raw text")
    return output
