from __future__ import annotations

from dataclasses import dataclass, field

import pytest

from arcadia.aa_runtime.invoker import SpecialistInvocation
from arcadia.contracts.aae.registry import (
    MODE_HOWARD_INTENT_COMMENT,
    MODE_INTENT_ORGANIZER,
    MODE_PROMPT_ANALYSIS,
    MODE_SPELL,
    MODE_TERM_MEANING,
)
from arcadia.core.canonical_json import JsonValue
from arcadia.core.ids import CanonicalId
from arcadia.recipes.r0.controller import ConversationPacket
from arcadia.recipes.r1.controller import Recipe1ControllerError, Recipe1IntentController


def _packet(prompt: str = "Fix my projet. Then save it.") -> ConversationPacket:
    return ConversationPacket.freeze(
        turn_id=CanonicalId.new(),
        conversation_id=CanonicalId.new(),
        raw_user_prompt=prompt,
        transcript_commit_seq=0,
        included_turns=(),
        unresolved_references=(),
        scope_status="SUFFICIENT_WITHOUT_HISTORY",
    )


def _spell() -> dict[str, JsonValue]:
    return {
        "mode": MODE_SPELL,
        "raw_prompt": "Fix my projet. Then save it.",
        "normalized_prompt": "Fix my project. Then save it.",
        "spell_edits": [
            {
                "start": 7,
                "end": 13,
                "source": "projet",
                "replacement": "project",
            }
        ],
        "uncertain_corrections": [],
    }


def _meaning(source_ref: str = "S001") -> dict[str, JsonValue]:
    return {
        "mode": MODE_TERM_MEANING,
        "terms": [
            {
                "term_key": "TERM_1",
                "source_ref": source_ref,
                "surface": "projet",
                "type_guess": "PROJECT",
                "current_use_guess": "The user refers to a project target.",
                "meaning_status": "provisional",
                "context_lookup_needed": True,
                "confidence": 0.6,
            }
        ],
        "unresolved_references": [],
    }


def _analysis() -> dict[str, JsonValue]:
    first = {"text": "project work", "source_refs": ["S001"]}
    second = {"text": "save result", "source_refs": ["S002"]}
    return {
        "mode": MODE_PROMPT_ANALYSIS,
        "topics": [first],
        "goals": [first, second],
        "tasks": [first, second],
        "statements": [],
        "questions": [],
        "directions": [first, second],
        "approvals": [],
        "interaction_mode": "ordering_or_directive",
        "important_claims": [],
        "unresolved_items": [],
        "control_signals": [],
    }


def _organizer(
    *,
    second_depends_on: list[JsonValue] | None = None,
    capability: str = "project_edit",
) -> dict[str, JsonValue]:
    return {
        "mode": MODE_INTENT_ORGANIZER,
        "primary_intent": "Edit the referenced project and save the result.",
        "secondary_intents": [],
        "requirements": [
            {
                "requirement_key": "REQ_1",
                "requested_outcome": "Fix the referenced project.",
                "constraints": [],
                "source_refs": ["S001"],
                "depends_on": [],
                "group": "PROJECT_WORK",
                "priority": 100,
                "context_needs": ["Resolve the referenced project target."],
                "capability_candidates": [capability],
                "memory_candidates": [],
            },
            {
                "requirement_key": "REQ_2",
                "requested_outcome": "Save the resulting project state.",
                "constraints": [],
                "source_refs": ["S002"],
                "depends_on": ["REQ_1"] if second_depends_on is None else second_depends_on,
                "group": "PROJECT_WORK",
                "priority": 90,
                "context_needs": [],
                "capability_candidates": ["project_save"],
                "memory_candidates": [],
            },
        ],
        "clarification_required": False,
        "context_resolution_first": True,
        "unresolved_blockers": ["Project target must be grounded by Context."],
        "control_signals": [],
    }


def _comment() -> dict[str, JsonValue]:
    return {
        "mode": MODE_HOWARD_INTENT_COMMENT,
        "comment": "I understand: fix the referenced project first, then save the result.",
    }


@dataclass(slots=True)
class ScriptedInvoker:
    outputs: dict[str, dict[str, JsonValue]]
    calls: list[tuple[str, JsonValue]] = field(default_factory=list)

    def invoke(self, *, mode: str, call_data: JsonValue) -> SpecialistInvocation:
        self.calls.append((mode, call_data))
        return SpecialistInvocation(
            attempt_id=CanonicalId.new(),
            mode=mode,
            call_data=call_data,
            output=self.outputs[mode],
        )


def _invoker(**overrides: dict[str, JsonValue]) -> ScriptedInvoker:
    outputs = {
        MODE_SPELL: _spell(),
        MODE_TERM_MEANING: _meaning(),
        MODE_PROMPT_ANALYSIS: _analysis(),
        MODE_INTENT_ORGANIZER: _organizer(),
        MODE_HOWARD_INTENT_COMMENT: _comment(),
    }
    outputs.update(overrides)
    return ScriptedInvoker(outputs)


def _capabilities() -> tuple[dict[str, JsonValue], ...]:
    return (
        {
            "capability_id": "project_edit",
            "capability_class": "PROJECT",
            "available": True,
        },
        {
            "capability_id": "project_save",
            "capability_class": "PROJECT",
            "available": True,
        },
    )


def test_recipe1_runs_five_isolated_modes_and_freezes_authoritative_intent() -> None:
    invoker = _invoker()
    controller = Recipe1IntentController(invoker=invoker)

    result = controller.run(packet=_packet(), capability_availability=_capabilities())

    assert [mode for mode, _ in invoker.calls] == [
        MODE_SPELL,
        MODE_TERM_MEANING,
        MODE_PROMPT_ANALYSIS,
        MODE_INTENT_ORGANIZER,
        MODE_HOWARD_INTENT_COMMENT,
    ]
    assert result.artifact.normalized_prompt == "Fix my project. Then save it."
    assert [span["span_ref"] for span in result.artifact.source_spans] == ["S001", "S002"]
    assert result.artifact.terms[0]["term_key"] == "T001"
    assert [item["requirement_ref"] for item in result.artifact.requirements] == ["R001", "R002"]
    assert result.artifact.requirements[1]["depends_on"] == ["R001"]
    assert result.intent_comment is not None
    assert len(result.invocations) == 5

    organizer_call = invoker.calls[3][1]
    assert type(organizer_call) is dict
    meaning = organizer_call["meaning_artifact"]
    assert type(meaning) is dict
    terms = meaning["terms"]
    assert type(terms) is list and type(terms[0]) is dict
    assert terms[0]["term_key"] == "T001"


def test_intent_comment_is_optional_and_never_part_of_machine_artifact() -> None:
    invoker = _invoker()
    result = Recipe1IntentController(invoker=invoker).run(
        packet=_packet(),
        capability_availability=_capabilities(),
        include_intent_comment=False,
    )

    assert result.intent_comment is None
    assert len(result.invocations) == 4
    assert MODE_HOWARD_INTENT_COMMENT not in [mode for mode, _ in invoker.calls]
    assert "intent_comment" not in result.artifact.to_value()


def test_meaning_cannot_cite_a_source_span_the_host_did_not_supply() -> None:
    invoker = _invoker(**{MODE_TERM_MEANING: _meaning("S999")})
    with pytest.raises(Recipe1ControllerError, match="unsupplied source ref S999"):
        Recipe1IntentController(invoker=invoker).run(
            packet=_packet(), capability_availability=_capabilities()
        )


def test_organizer_cannot_nominate_unknown_capability() -> None:
    invoker = _invoker(**{MODE_INTENT_ORGANIZER: _organizer(capability="made_up_tool")})
    with pytest.raises(Recipe1ControllerError, match="unknown capabilities"):
        Recipe1IntentController(invoker=invoker).run(
            packet=_packet(), capability_availability=_capabilities()
        )


def test_organizer_dependency_cycle_fails_closed() -> None:
    organizer = _organizer(second_depends_on=["REQ_1"])
    requirements = organizer["requirements"]
    assert type(requirements) is list and type(requirements[0]) is dict
    requirements[0]["depends_on"] = ["REQ_2"]
    invoker = _invoker(**{MODE_INTENT_ORGANIZER: organizer})

    with pytest.raises(Recipe1ControllerError, match="dependencies contain a cycle"):
        Recipe1IntentController(invoker=invoker).run(
            packet=_packet(), capability_availability=_capabilities()
        )


def test_model_cannot_allocate_authoritative_requirement_aliases() -> None:
    organizer = _organizer()
    requirements = organizer["requirements"]
    assert type(requirements) is list and type(requirements[0]) is dict
    requirements[0]["requirement_key"] = "R001"
    invoker = _invoker(**{MODE_INTENT_ORGANIZER: organizer})

    with pytest.raises(Recipe1ControllerError, match="outside the frozen REQ_ namespace"):
        Recipe1IntentController(invoker=invoker).run(
            packet=_packet(), capability_availability=_capabilities()
        )
