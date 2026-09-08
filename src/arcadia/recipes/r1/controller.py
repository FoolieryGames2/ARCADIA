"""Host-owned Recipe 1 Intent orchestration over frozen PRE-1 learned contracts."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Final, cast

from arcadia.aa_runtime.invoker import SpecialistInvocation, SpecialistInvoker
from arcadia.contracts.aae.registry import (
    MODE_HOWARD_INTENT_COMMENT,
    MODE_INTENT_ORGANIZER,
    MODE_PROMPT_ANALYSIS,
    MODE_SPELL,
    MODE_TERM_MEANING,
)
from arcadia.contracts.schemas.r1.contracts import (
    INTENT_COMMENT_SCHEMAS,
    INTENT_ORGANIZER_SCHEMAS,
    PROMPT_ANALYSIS_SCHEMAS,
    SPELL_SCHEMAS,
    TERM_MEANING_SCHEMAS,
    IntentContractSemanticError,
    require_valid_spell_output,
)
from arcadia.core.canonical_json import JsonValue, canonical_json_dumps
from arcadia.core.hashing import Sha256Digest, sha256_canonical_json
from arcadia.core.ids import AliasAllocator, AliasKind, CanonicalId
from arcadia.recipes.r0.controller import ConversationPacket

_SENTENCE_CANDIDATE: Final = re.compile(r"[^.!?\n]+(?:[.!?]+(?=\s|$)|(?=\n|$))")
_INTERNAL_REF: Final = re.compile(r"\b[A-Z]{1,6}[0-9]{3,6}\b")


class Recipe1ControllerError(ValueError):
    """Recipe 1 host orchestration rejected a learned proposal or illegal handoff."""


def _object(value: JsonValue, label: str) -> dict[str, JsonValue]:
    if type(value) is not dict:
        raise Recipe1ControllerError(f"{label} must be an object")
    return value


def _array(value: JsonValue, label: str) -> list[JsonValue]:
    if type(value) is not list:
        raise Recipe1ControllerError(f"{label} must be an array")
    return value


def _source_spans(raw_prompt: str, allocator: AliasAllocator) -> tuple[dict[str, JsonValue], ...]:
    if not raw_prompt.strip():
        raise Recipe1ControllerError("Recipe 1 requires a nonempty raw user prompt")

    spans: list[dict[str, JsonValue]] = []
    for match in _SENTENCE_CANDIDATE.finditer(raw_prompt):
        start, end = match.span()
        while start < end and raw_prompt[start].isspace():
            start += 1
        while end > start and raw_prompt[end - 1].isspace():
            end -= 1
        if start == end:
            continue
        spans.append(
            {
                "span_ref": allocator.allocate(AliasKind.SOURCE_SPAN).text,
                "text": raw_prompt[start:end],
                "start": start,
                "end": end,
                "kind": "SOURCE_TEXT",
            }
        )

    if not spans:
        start = len(raw_prompt) - len(raw_prompt.lstrip())
        end = len(raw_prompt.rstrip())
        spans.append(
            {
                "span_ref": allocator.allocate(AliasKind.SOURCE_SPAN).text,
                "text": raw_prompt[start:end],
                "start": start,
                "end": end,
                "kind": "SOURCE_TEXT",
            }
        )
    return tuple(spans)


def _allowed_span_refs(spans: tuple[dict[str, JsonValue], ...]) -> frozenset[str]:
    return frozenset(str(span["span_ref"]) for span in spans)


def _require_source_refs(items: JsonValue, *, allowed: frozenset[str], label: str) -> None:
    for raw_item in _array(items, label):
        item = _object(raw_item, f"{label} item")
        refs = _array(item["source_refs"], f"{label}.source_refs")
        for raw_ref in refs:
            ref = str(raw_ref)
            if ref not in allowed:
                raise Recipe1ControllerError(f"{label} cites unsupplied source ref {ref}")


def _canonicalize_meaning(
    output: dict[str, JsonValue],
    *,
    allowed_spans: frozenset[str],
    allocator: AliasAllocator,
) -> dict[str, JsonValue]:
    terms = _array(output["terms"], "meaning.terms")
    unresolved = output["unresolved_references"]
    _require_source_refs(unresolved, allowed=allowed_spans, label="meaning.unresolved_references")

    local_keys: set[str] = set()
    accepted_terms: list[JsonValue] = []
    for raw_term in terms:
        term = _object(raw_term, "meaning term")
        local_key = str(term["term_key"])
        if local_key in local_keys:
            raise Recipe1ControllerError(f"duplicate Meaning local key {local_key}")
        if not (local_key.startswith("TERM_") or local_key.startswith("REF_")):
            raise Recipe1ControllerError(
                f"Meaning local key {local_key} is outside the frozen TERM_/REF_ namespace"
            )
        local_keys.add(local_key)
        source_ref = str(term["source_ref"])
        if source_ref not in allowed_spans:
            raise Recipe1ControllerError(f"Meaning term cites unsupplied source ref {source_ref}")
        accepted = dict(term)
        accepted["term_key"] = allocator.allocate(AliasKind.TERM_CANDIDATE).text
        accepted_terms.append(cast(JsonValue, accepted))

    accepted_artifact: dict[str, JsonValue] = {
        "terms": accepted_terms,
        "unresolved_references": unresolved,
    }
    TERM_MEANING_SCHEMAS.output.require_valid(
        {"mode": MODE_TERM_MEANING, **accepted_artifact}
    )
    return accepted_artifact


def _validate_prompt_analysis(
    output: dict[str, JsonValue], *, allowed_spans: frozenset[str]
) -> None:
    for name in (
        "topics",
        "goals",
        "tasks",
        "statements",
        "questions",
        "directions",
        "approvals",
        "important_claims",
        "unresolved_items",
    ):
        _require_source_refs(output[name], allowed=allowed_spans, label=f"analysis.{name}")
    for raw_signal in _array(output["control_signals"], "analysis.control_signals"):
        signal = _object(raw_signal, "analysis control signal")
        for raw_ref in _array(signal["source_refs"], "analysis.control_signals.source_refs"):
            ref = str(raw_ref)
            if ref not in allowed_spans:
                raise Recipe1ControllerError(
                    f"analysis control signal cites unsupplied source ref {ref}"
                )


def _require_acyclic_dependencies(dependencies: dict[str, tuple[str, ...]]) -> None:
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(key: str) -> None:
        if key in visited:
            return
        if key in visiting:
            raise Recipe1ControllerError("Intent requirement dependencies contain a cycle")
        visiting.add(key)
        for dependency in dependencies[key]:
            visit(dependency)
        visiting.remove(key)
        visited.add(key)

    for requirement_key in dependencies:
        visit(requirement_key)


def _canonicalize_requirements(
    organizer: dict[str, JsonValue],
    *,
    allowed_spans: frozenset[str],
    capability_availability: tuple[dict[str, JsonValue], ...],
    allocator: AliasAllocator,
    expected_control_signals: JsonValue,
) -> tuple[dict[str, JsonValue], ...]:
    if bool(organizer["clarification_required"]) and bool(organizer["context_resolution_first"]):
        raise Recipe1ControllerError(
            "clarification_required and context_resolution_first cannot both be true"
        )
    if canonical_json_dumps(organizer["control_signals"]) != canonical_json_dumps(
        expected_control_signals
    ):
        raise Recipe1ControllerError("Organizer must copy accepted Prompt Analyst control signals")

    known_capabilities = frozenset(str(item["capability_id"]) for item in capability_availability)
    raw_requirements = _array(organizer["requirements"], "organizer.requirements")
    keyed: dict[str, dict[str, JsonValue]] = {}
    dependencies: dict[str, tuple[str, ...]] = {}

    for raw_requirement in raw_requirements:
        requirement = _object(raw_requirement, "organizer requirement")
        key = str(requirement["requirement_key"])
        if not key.startswith("REQ_"):
            raise Recipe1ControllerError(
                f"Organizer requirement key {key} is outside the frozen REQ_ namespace"
            )
        if key in keyed:
            raise Recipe1ControllerError(f"duplicate Organizer requirement key {key}")
        source_refs = tuple(str(item) for item in _array(requirement["source_refs"], "source_refs"))
        if any(ref not in allowed_spans for ref in source_refs):
            raise Recipe1ControllerError(f"Organizer requirement {key} cites an unknown source ref")
        candidates = tuple(
            str(item) for item in _array(requirement["capability_candidates"], "capability_candidates")
        )
        unknown = sorted(set(candidates) - known_capabilities)
        if unknown:
            raise Recipe1ControllerError(
                f"Organizer requirement {key} proposed unknown capabilities {unknown}"
            )
        depends_on = tuple(str(item) for item in _array(requirement["depends_on"], "depends_on"))
        keyed[key] = requirement
        dependencies[key] = depends_on

    for key, depends_on in dependencies.items():
        if key in depends_on:
            raise Recipe1ControllerError(f"Organizer requirement {key} cannot depend on itself")
        missing = sorted(set(depends_on) - set(keyed))
        if missing:
            raise Recipe1ControllerError(
                f"Organizer requirement {key} depends on unknown local keys {missing}"
            )
    _require_acyclic_dependencies(dependencies)

    canonical_refs = {
        key: allocator.allocate(AliasKind.REQUIREMENT).text for key in keyed
    }
    accepted: list[dict[str, JsonValue]] = []
    for key, requirement in keyed.items():
        value = dict(requirement)
        value.pop("requirement_key")
        value["requirement_ref"] = canonical_refs[key]
        value["depends_on"] = [canonical_refs[dependency] for dependency in dependencies[key]]
        accepted.append(value)
    return tuple(accepted)


def _r0_transcript_evidence(packet: ConversationPacket) -> list[JsonValue]:
    evidence: list[JsonValue] = []
    for turn in packet.included_turns:
        evidence.append(
            {
                "turn_uuid": str(turn["turn_uuid"]),
                "user_message": str(turn["user_message"]),
                "final_response": str(turn["final_response"]),
            }
        )
    return evidence


@dataclass(frozen=True, slots=True)
class IntentArtifact:
    """Immutable host-accepted Recipe 1 handoff; presentation prose is excluded."""

    turn_id: CanonicalId
    conversation_id: CanonicalId
    conversation_packet_hash: Sha256Digest
    raw_prompt: str
    normalized_prompt: str
    source_spans: tuple[dict[str, JsonValue], ...]
    terms: tuple[dict[str, JsonValue], ...]
    unresolved_references: tuple[dict[str, JsonValue], ...]
    prompt_analysis: dict[str, JsonValue]
    primary_intent: str
    secondary_intents: tuple[str, ...]
    requirements: tuple[dict[str, JsonValue], ...]
    clarification_required: bool
    context_resolution_first: bool
    unresolved_blockers: tuple[str, ...]
    control_signals: tuple[dict[str, JsonValue], ...]
    artifact_hash: Sha256Digest

    @classmethod
    def freeze(
        cls,
        *,
        packet: ConversationPacket,
        normalized_prompt: str,
        source_spans: tuple[dict[str, JsonValue], ...],
        meaning_artifact: dict[str, JsonValue],
        prompt_analysis: dict[str, JsonValue],
        organizer: dict[str, JsonValue],
        requirements: tuple[dict[str, JsonValue], ...],
    ) -> IntentArtifact:
        terms = tuple(
            _object(item, "accepted meaning term")
            for item in _array(meaning_artifact["terms"], "accepted meaning terms")
        )
        unresolved_references = tuple(
            _object(item, "accepted unresolved reference")
            for item in _array(
                meaning_artifact["unresolved_references"], "accepted unresolved references"
            )
        )
        secondary = tuple(
            str(item) for item in _array(organizer["secondary_intents"], "secondary_intents")
        )
        blockers = tuple(
            str(item) for item in _array(organizer["unresolved_blockers"], "unresolved_blockers")
        )
        signals = tuple(
            _object(item, "accepted control signal")
            for item in _array(organizer["control_signals"], "control_signals")
        )
        value: dict[str, JsonValue] = {
            "turn_uuid": str(packet.turn_id),
            "conversation_uuid": str(packet.conversation_id),
            "conversation_packet_hash": packet.packet_hash.value,
            "raw_prompt": packet.raw_user_prompt,
            "normalized_prompt": normalized_prompt,
            "source_spans": list(source_spans),
            "terms": list(terms),
            "unresolved_references": list(unresolved_references),
            "prompt_analysis": prompt_analysis,
            "primary_intent": str(organizer["primary_intent"]),
            "secondary_intents": list(secondary),
            "requirements": list(requirements),
            "clarification_required": bool(organizer["clarification_required"]),
            "context_resolution_first": bool(organizer["context_resolution_first"]),
            "unresolved_blockers": list(blockers),
            "control_signals": list(signals),
        }
        return cls(
            turn_id=packet.turn_id,
            conversation_id=packet.conversation_id,
            conversation_packet_hash=packet.packet_hash,
            raw_prompt=packet.raw_user_prompt,
            normalized_prompt=normalized_prompt,
            source_spans=source_spans,
            terms=terms,
            unresolved_references=unresolved_references,
            prompt_analysis=prompt_analysis,
            primary_intent=str(organizer["primary_intent"]),
            secondary_intents=secondary,
            requirements=requirements,
            clarification_required=bool(organizer["clarification_required"]),
            context_resolution_first=bool(organizer["context_resolution_first"]),
            unresolved_blockers=blockers,
            control_signals=signals,
            artifact_hash=sha256_canonical_json(value),
        )

    def to_value(self) -> dict[str, JsonValue]:
        return {
            "turn_uuid": str(self.turn_id),
            "conversation_uuid": str(self.conversation_id),
            "conversation_packet_hash": self.conversation_packet_hash.value,
            "raw_prompt": self.raw_prompt,
            "normalized_prompt": self.normalized_prompt,
            "source_spans": list(self.source_spans),
            "terms": list(self.terms),
            "unresolved_references": list(self.unresolved_references),
            "prompt_analysis": self.prompt_analysis,
            "primary_intent": self.primary_intent,
            "secondary_intents": list(self.secondary_intents),
            "requirements": list(self.requirements),
            "clarification_required": self.clarification_required,
            "context_resolution_first": self.context_resolution_first,
            "unresolved_blockers": list(self.unresolved_blockers),
            "control_signals": list(self.control_signals),
            "artifact_hash": self.artifact_hash.value,
        }


@dataclass(frozen=True, slots=True)
class Recipe1Result:
    """Complete Recipe 1 result including non-authoritative presentation and call trace."""

    artifact: IntentArtifact
    intent_comment: str | None
    invocations: tuple[SpecialistInvocation, ...]


@dataclass(frozen=True, slots=True)
class Recipe1IntentController:
    """Run the frozen Recipe 1 specialist sequence with host validation between calls."""

    invoker: SpecialistInvoker

    def run(
        self,
        *,
        packet: ConversationPacket,
        capability_availability: tuple[dict[str, JsonValue], ...] = (),
        include_intent_comment: bool = True,
    ) -> Recipe1Result:
        allocator = AliasAllocator(packet.turn_id)
        invocations: list[SpecialistInvocation] = []

        spell_call: dict[str, JsonValue] = {
            "mode": MODE_SPELL,
            "raw_prompt": packet.raw_user_prompt,
        }
        SPELL_SCHEMAS.input.require_valid(spell_call)
        spell_invocation = self.invoker.invoke(mode=MODE_SPELL, call_data=spell_call)
        invocations.append(spell_invocation)
        spell_output = _object(spell_invocation.output, "Spell output")
        try:
            require_valid_spell_output(spell_output, call_data=spell_call)
        except IntentContractSemanticError as exc:
            raise Recipe1ControllerError(str(exc)) from exc
        normalized_prompt = str(spell_output["normalized_prompt"])

        spans = _source_spans(packet.raw_user_prompt, allocator)
        allowed_spans = _allowed_span_refs(spans)
        meaning_call: dict[str, JsonValue] = {
            "mode": MODE_TERM_MEANING,
            "raw_prompt": packet.raw_user_prompt,
            "normalized_prompt": normalized_prompt,
            "spell_uncertainties": spell_output["uncertain_corrections"],
            "host_linguistic_map": {"source_spans": list(spans)},
            "r0_transcript_evidence": _r0_transcript_evidence(packet),
        }
        TERM_MEANING_SCHEMAS.input.require_valid(meaning_call)
        meaning_invocation = self.invoker.invoke(mode=MODE_TERM_MEANING, call_data=meaning_call)
        invocations.append(meaning_invocation)
        meaning_output = _object(meaning_invocation.output, "Meaning output")
        TERM_MEANING_SCHEMAS.output.require_valid(meaning_output)
        meaning_artifact = _canonicalize_meaning(
            meaning_output,
            allowed_spans=allowed_spans,
            allocator=allocator,
        )

        analysis_call: dict[str, JsonValue] = {
            "mode": MODE_PROMPT_ANALYSIS,
            "raw_prompt": packet.raw_user_prompt,
            "normalized_prompt": normalized_prompt,
            "meaning_artifact": meaning_artifact,
            "host_source_spans": list(spans),
        }
        PROMPT_ANALYSIS_SCHEMAS.input.require_valid(analysis_call)
        analysis_invocation = self.invoker.invoke(mode=MODE_PROMPT_ANALYSIS, call_data=analysis_call)
        invocations.append(analysis_invocation)
        analysis_output = _object(analysis_invocation.output, "Prompt Analyst output")
        PROMPT_ANALYSIS_SCHEMAS.output.require_valid(analysis_output)
        _validate_prompt_analysis(analysis_output, allowed_spans=allowed_spans)

        organizer_call: dict[str, JsonValue] = {
            "mode": MODE_INTENT_ORGANIZER,
            "meaning_artifact": meaning_artifact,
            "prompt_analysis_artifact": analysis_output,
            "current_turn_source_refs": list(spans),
            "capability_availability": list(capability_availability),
        }
        INTENT_ORGANIZER_SCHEMAS.input.require_valid(organizer_call)
        organizer_invocation = self.invoker.invoke(
            mode=MODE_INTENT_ORGANIZER, call_data=organizer_call
        )
        invocations.append(organizer_invocation)
        organizer_output = _object(organizer_invocation.output, "Intent Organizer output")
        INTENT_ORGANIZER_SCHEMAS.output.require_valid(organizer_output)
        requirements = _canonicalize_requirements(
            organizer_output,
            allowed_spans=allowed_spans,
            capability_availability=capability_availability,
            allocator=allocator,
            expected_control_signals=analysis_output["control_signals"],
        )
        artifact = IntentArtifact.freeze(
            packet=packet,
            normalized_prompt=normalized_prompt,
            source_spans=spans,
            meaning_artifact=meaning_artifact,
            prompt_analysis=analysis_output,
            organizer=organizer_output,
            requirements=requirements,
        )

        comment: str | None = None
        if include_intent_comment:
            presentation_requirements: list[JsonValue] = []
            for requirement in requirements:
                presentation_requirements.append(
                    {
                        "requirement_ref": requirement["requirement_ref"],
                        "requested_outcome": requirement["requested_outcome"],
                        "source_refs": requirement["source_refs"],
                    }
                )
            comment_call: dict[str, JsonValue] = {
                "mode": MODE_HOWARD_INTENT_COMMENT,
                "accepted_intent_projection": {
                    "primary_intent": artifact.primary_intent,
                    "requirements": presentation_requirements,
                },
            }
            INTENT_COMMENT_SCHEMAS.input.require_valid(comment_call)
            comment_invocation = self.invoker.invoke(
                mode=MODE_HOWARD_INTENT_COMMENT, call_data=comment_call
            )
            invocations.append(comment_invocation)
            comment_output = _object(comment_invocation.output, "Intent comment output")
            INTENT_COMMENT_SCHEMAS.output.require_valid(comment_output)
            comment = str(comment_output["comment"])
            allowed_refs = allowed_spans | frozenset(
                str(requirement["requirement_ref"]) for requirement in requirements
            )
            leaked = sorted(set(_INTERNAL_REF.findall(comment)) - allowed_refs)
            if leaked:
                raise Recipe1ControllerError(
                    f"Intent comment introduced unsupplied internal references {leaked}"
                )

        return Recipe1Result(
            artifact=artifact,
            intent_comment=comment,
            invocations=tuple(invocations),
        )
