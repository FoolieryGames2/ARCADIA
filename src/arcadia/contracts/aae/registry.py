"""Pre-version AAE contract registry for A.R.C.A.D.I.A. v0.1 Phase A1 review.

This module is intentionally non-dispatchable. It freezes the *shape* and candidate
semantic jurisdictions for joint review without pretending that schemas, inference
profiles, settings profiles/limits, or trust thresholds have already passed their later gates.
"""

from __future__ import annotations

from collections.abc import Mapping
from types import MappingProxyType
from typing import Final

from arcadia.contracts.aae.global_awareness import GLOBAL_AWARENESS_PRE_V1
from arcadia.contracts.aae.types import (
    AAEContractRecord,
    AuthorityClass,
    LocalKeyPolicy,
    RegistryStatus,
    RepairShape,
    SchemaRef,
    SpecialistAwareness,
)

REGISTRY_VERSION: Final = "AAE-REGISTRY-PRE-1"
GLOBAL_VERSION: Final = GLOBAL_AWARENESS_PRE_V1.version

# Core physical roster from the v0.1 build authority. These are semantic identities only;
# paths, hashes, live handles, residency, leases, and memory telemetry belong to A2.
PHYSICAL_ADAPTER_IDS: Final[tuple[str, ...]] = (
    "CONVERSATION_RESOLVER",
    "SPELL",
    "TERM_MEANING",
    "PROMPT_ANALYST",
    "INTENT_ORGANIZER",
    "CONVERSATIONAL_HOWARD",
    "EVIDENCE_SPECIALIST",
    "REQUIREMENT_ASSESSOR",
    "PLAN_COMPOSER",
    "EVIDENCE_RECONCILER",
    "RECONCILIATION_COMPOSER",
    "PERSISTENCE_ASSESSOR",
    "PERSISTENCE_COMPOSER",
    "COMPLETION_ASSESSOR",
    "COMPLETION_COMPOSER",
)

# Logical mode IDs are pre-version implementation candidates, not frozen public API names.
MODE_SCOPE_PROPOSAL: Final = "SCOPE_PROPOSAL"
MODE_SCOPE_VALIDATION: Final = "SCOPE_VALIDATION"
MODE_SPELL: Final = "SPELL_NORMALIZATION"
MODE_TERM_MEANING: Final = "TERM_MEANING"
MODE_PROMPT_ANALYSIS: Final = "PROMPT_ANALYSIS"
MODE_INTENT_ORGANIZER: Final = "INTENT_ORGANIZER"
MODE_HOWARD_INTENT_COMMENT: Final = "INTENT_COMMENT"
MODE_CONTEXT_EVIDENCE: Final = "CONTEXT_EVIDENCE_ASSESSMENT"
MODE_HOWARD_CONTEXT_LANE: Final = "CONTEXT_LANE_COMMENT"
MODE_HOWARD_CONTEXT_FINAL: Final = "CONTEXT_FINAL_SYNTHESIS"
MODE_REQUIREMENT_ASSESSOR: Final = "REQUIREMENT_ASSESSMENT"
MODE_PLAN_COMPOSER: Final = "PLAN_COMPOSITION"
MODE_EVIDENCE_RECONCILER: Final = "EVIDENCE_RECONCILIATION"
MODE_RECONCILIATION_COMPOSER: Final = "RECONCILIATION_COMPOSITION"
MODE_PERSISTENCE_ASSESSOR: Final = "PERSISTENCE_ASSESSMENT"
MODE_PERSISTENCE_COMPOSER: Final = "PERSISTENCE_COMPOSITION"
MODE_COMPLETION_ASSESSOR: Final = "COMPLETION_ASSESSMENT"
MODE_COMPLETION_COMPOSER: Final = "COMPLETION_COMPOSITION"
MODE_HOWARD_RESULT_COMMENT: Final = "RESULT_REQUIREMENT_COMMENT"
MODE_HOWARD_RESULT_FINAL: Final = "RESULT_FINAL_COMPOSE"


def _schema(contract_slug: str, direction: str) -> SchemaRef:
    return SchemaRef(
        schema_id=f"aae.{contract_slug}.{direction}",
        schema_version="PRE-1",
        frozen=False,
    )


def _repair() -> RepairShape:
    return RepairShape(allowed=True)


def _awareness(
    *,
    specialist: str,
    recipe: str,
    authority: AuthorityClass,
    purpose: str,
    input_origin: str,
    responsibilities: tuple[str, ...],
    forbidden: tuple[str, ...],
    next_consumers: tuple[str, ...],
) -> SpecialistAwareness:
    return SpecialistAwareness(
        specialist=specialist,
        recipe=recipe,
        authority=authority,
        purpose=purpose,
        input_origin=input_origin,
        responsibilities=responsibilities,
        forbidden_responsibilities=forbidden,
        next_consumers=next_consumers,
    )


def _contract(
    *,
    slug: str,
    mode: str,
    adapter: str,
    recipe_id: str,
    awareness: SpecialistAwareness,
    inputs: tuple[str, ...],
    refs: tuple[str, ...],
    local_prefixes: tuple[str, ...],
    response: str,
    enums: Mapping[str, tuple[str, ...]] | None,
    empty: str,
    uncertainty: str,
    forbidden_output: tuple[str, ...],
    validation: tuple[str, ...],
    consumers: tuple[str, ...],
    review_notes: tuple[str, ...] = (),
) -> AAEContractRecord:
    return AAEContractRecord(
        contract_id=f"aae.{slug}",
        contract_version="PRE-1",
        registry_status=RegistryStatus.PRE_VERSION,
        dispatch_enabled=False,
        global_awareness_version=GLOBAL_VERSION,
        specialist_mode_id=mode,
        physical_adapter_id=adapter,
        recipe_id=recipe_id,
        awareness=awareness,
        legal_input_artifact_classes=inputs,
        legal_authoritative_ref_namespaces=refs,
        origin_trust_policy_id=f"origin_trust.{mode.lower()}.pre1",
        local_key_policy=LocalKeyPolicy(allowed_prefixes=local_prefixes),
        input_schema=_schema(slug, "input"),
        output_schema=_schema(slug, "output"),
        response_contract_summary=response,
        semantic_enums={} if enums is None else enums,
        empty_output_meaning=empty,
        uncertainty_behavior=uncertainty,
        forbidden_output_fields_or_actions=forbidden_output,
        host_validation_rules=validation,
        repair=_repair(),
        next_legal_consumers=consumers,
        inference_profile_id=f"ip.{slug}.pre1",
        inference_profile_frozen=False,
        minimum_trust_level=None,
        settings_profile_id=f"settings.{mode.lower()}.pre1",
        context_projection_policy_id=f"projection.{mode.lower()}.pre1",
        review_notes=review_notes,
    )


_CONTRACTS: tuple[AAEContractRecord, ...] = (
    _contract(
        slug="r0.scope_proposal",
        mode=MODE_SCOPE_PROPOSAL,
        adapter="CONVERSATION_RESOLVER",
        recipe_id="R0",
        awareness=_awareness(
            specialist="Conversation Resolver / SCOPE_PROPOSAL",
            recipe="0 — Conversation Resolver",
            authority=AuthorityClass.SEMANTIC_ASSESSMENT,
            purpose=(
                "Determine whether the current turn is semantically sufficient without transcript "
                "retrieval, or request the minimum transcript scope needed to resolve conversational references."
            ),
            input_origin="Host current-turn envelope and transcript availability metadata only.",
            responsibilities=(
                "Assess only transcript-history sufficiency.",
                "Choose the minimum legitimate scope.",
                "Preserve unresolved reference need when current text cannot stand alone.",
            ),
            forbidden=(
                "Do not query semantic memory.",
                "Do not retrieve transcript yourself.",
                "Do not perform Intent decomposition, research, tools, persistence, or user response.",
            ),
            next_consumers=(
                "Host scope validator/retriever",
                "Host Conversation Packet freezer when no history is requested",
            ),
        ),
        inputs=("CURRENT_TURN_ENVELOPE", "TRANSCRIPT_AVAILABILITY_METADATA", "HOST_SCOPE_POLICY"),
        refs=("TURN_UUID", "CONVERSATION_UUID", "TRANSCRIPT_CURSOR"),
        local_prefixes=("SCOPE_",),
        response=(
            "Return only one JSON object with exactly these fields: mode, status, "
            "recent_exchange_count, target_terms, reason_codes. status must be one of "
            "SUFFICIENT_WITHOUT_HISTORY, REQUEST_RECENT, REQUEST_TARGETED. No prose or "
            "additional fields."
        ),
        enums={
            "proposal_outcome": (
                "SUFFICIENT_WITHOUT_HISTORY",
                "REQUEST_RECENT",
                "REQUEST_TARGETED",
            )
        },
        empty="Empty output is invalid; the proposal must select one explicit outcome.",
        uncertainty="Request bounded history rather than infer missing conversational reference meaning.",
        forbidden_output=(
            "semantic memory request",
            "Intent requirements",
            "tool request",
            "user-facing answer",
        ),
        validation=(
            "proposal outcome is legal",
            "requested scope stays within host policy bounds",
            "all copied current-turn identities match supplied values",
            "no authoritative identifier is invented",
        ),
        consumers=(
            "R0_HOST_SCOPE_VALIDATOR",
            "R0_HOST_RETRIEVER",
            "R0_CONVERSATION_PACKET_FREEZER",
        ),
        review_notes=(
            "R0 numeric retrieval bounds live in host policy/config, not model authority.",
        ),
    ),
    _contract(
        slug="r0.scope_validation",
        mode=MODE_SCOPE_VALIDATION,
        adapter="CONVERSATION_RESOLVER",
        recipe_id="R0",
        awareness=_awareness(
            specialist="Conversation Resolver / SCOPE_VALIDATION",
            recipe="0 — Conversation Resolver",
            authority=AuthorityClass.SEMANTIC_ASSESSMENT,
            purpose=(
                "Determine whether the exact retrieved transcript evidence is sufficient to resolve the "
                "current conversational reference within the allowed retrieval bound."
            ),
            input_origin="Current raw turn plus the exact frozen transcript slice returned by the host.",
            responsibilities=(
                "Assess sufficiency only.",
                "Identify which supplied transcript item resolves the latent reference when supported.",
                "Request another bounded transcript scope when still insufficient.",
            ),
            forbidden=(
                "Do not query semantic memory.",
                "Do not rewrite transcript text.",
                "Do not perform Intent, tools, persistence, or answer the user.",
            ),
            next_consumers=(
                "Host Conversation Packet freezer",
                "Host bounded transcript retriever",
            ),
        ),
        inputs=("CURRENT_RAW_TURN", "FROZEN_TRANSCRIPT_SLICE", "HOST_SCOPE_POLICY"),
        refs=("TURN_UUID", "TRANSCRIPT_TURN_UUID", "TRANSCRIPT_HASH"),
        local_prefixes=("SCOPE_",),
        response="One transcript sufficiency outcome with exact supplied evidence references and any bounded next-scope request.",
        enums={
            "validation_outcome": (
                "SUFFICIENT",
                "SUFFICIENT_WITHOUT_HISTORY",
                "NEEDS_MORE_RECENT",
                "NEEDS_TARGETED_HISTORY",
                "UNRESOLVABLE_WITH_TRANSCRIPT",
                "BOUND_EXHAUSTED",
            )
        },
        empty="Empty output is invalid; validation must preserve an explicit sufficient or unresolved state.",
        uncertainty="Use UNRESOLVABLE_WITH_TRANSCRIPT or BOUND_EXHAUSTED when the supplied transcript cannot safely resolve the reference.",
        forbidden_output=(
            "semantic-memory claim",
            "rewritten transcript",
            "Intent requirement",
            "user-facing answer",
        ),
        validation=(
            "validation outcome is legal",
            "all cited transcript items were supplied",
            "requested expansion stays within host bounds",
            "no evidence content is altered",
        ),
        consumers=("R0_CONVERSATION_PACKET_FREEZER", "R0_HOST_RETRIEVER"),
    ),
    _contract(
        slug="r1.spell",
        mode=MODE_SPELL,
        adapter="SPELL",
        recipe_id="R1",
        awareness=_awareness(
            specialist="Spell",
            recipe="1 — Intent",
            authority=AuthorityClass.SEMANTIC_PROPOSAL,
            purpose="Normalize only obvious spelling, punctuation, and capitalization defects while preserving the user's wording and intent.",
            input_origin="Current raw prompt from the frozen Conversation Packet.",
            responsibilities=(
                "Return a normalized prompt.",
                "Return genuine uncertainty about normalization rather than guessing.",
                "Preserve wording and style as much as possible.",
            ),
            forbidden=(
                "Do not paraphrase.",
                "Do not interpret references or inspect history.",
                "Do not create requirements, use Context, invoke tools, or answer the user.",
            ),
            next_consumers=("Host normalization validator/source-span builder", "Term / Meaning"),
        ),
        inputs=("RAW_USER_PROMPT",),
        refs=(),
        local_prefixes=("EDIT_",),
        response="raw_prompt, normalized_prompt, spell_edits[], uncertain_corrections[].",
        enums=None,
        empty="No edits is valid: normalized_prompt may equal raw_prompt and edit/uncertainty arrays may be empty.",
        uncertainty="Place uncertain corrections in the uncertainty structure; do not silently substitute a speculative repair.",
        forbidden_output=(
            "paraphrase",
            "project meaning",
            "history claim",
            "requirement",
            "tool action",
        ),
        validation=(
            "raw_prompt exactly matches supplied prompt",
            "normalized_prompt is bounded text",
            "edit provenance refers only to supplied text spans",
            "no undeclared fields",
        ),
        consumers=("R1_HOST_NORMALIZATION_VALIDATOR", "R1_TERM_MEANING"),
    ),
    _contract(
        slug="r1.term_meaning",
        mode=MODE_TERM_MEANING,
        adapter="TERM_MEANING",
        recipe_id="R1",
        awareness=_awareness(
            specialist="Term / Meaning",
            recipe="1 — Intent",
            authority=AuthorityClass.SEMANTIC_PROPOSAL,
            purpose=(
                "Interpret terms and references in the current turn only far enough to make the prompt analyzable. "
                "Mark provisional or unresolved meanings instead of inventing them."
            ),
            input_origin=(
                "Raw + normalized prompt, Spell uncertainty, host linguistic/source map, and any explicitly "
                "supplied Recipe-0 transcript evidence."
            ),
            responsibilities=(
                "Identify literal terms, references, aliases, and lookup-worthy terms.",
                "Propose provisional meanings and preserve source refs.",
                "Mark unresolved meaning when the bounded packet is insufficient.",
            ),
            forbidden=(
                "Do not decide historical truth or query SQLite.",
                "Do not perform research, create requirements, select tools, persist state, or answer.",
            ),
            next_consumers=("Prompt Analyst",),
        ),
        inputs=(
            "RAW_USER_PROMPT",
            "NORMALIZED_PROMPT",
            "SPELL_UNCERTAINTY",
            "HOST_LINGUISTIC_MAP",
            "R0_TRANSCRIPT_EVIDENCE",
        ),
        refs=("SOURCE_SPAN", "TRANSCRIPT_TURN_UUID"),
        local_prefixes=("TERM_", "REF_"),
        response="Bounded term/reference meaning records, lookup-needed flags, confidence/uncertainty, and exact source references.",
        enums={"meaning_status": ("provisional", "unresolved")},
        empty="No special term records is valid when ordinary surface meaning is sufficient; the contract must still return a valid artifact.",
        uncertainty="Meaning remains provisional; unresolved history/project meaning is routed to later Context rather than guessed.",
        forbidden_output=(
            "authoritative historical truth",
            "SQLite query",
            "research result",
            "Rxxx",
            "tool selection",
        ),
        validation=(
            "source refs are present in supplied spans/evidence",
            "lookup-needed flags use schema-owned values",
            "no unsupported historical facts are introduced as host state",
            "no undeclared fields",
        ),
        consumers=("R1_PROMPT_ANALYST",),
        review_notes=(
            "The exact Meaning status vocabulary is still a schema-review item; 'provisional' is explicitly source-backed.",
        ),
    ),
    _contract(
        slug="r1.prompt_analysis",
        mode=MODE_PROMPT_ANALYSIS,
        adapter="PROMPT_ANALYST",
        recipe_id="R1",
        awareness=_awareness(
            specialist="Prompt Analyst",
            recipe="1 — Intent",
            authority=AuthorityClass.SEMANTIC_PROPOSAL,
            purpose="Identify the communicative structures actually present in the supplied prompt.",
            input_origin="Raw + normalized prompt, accepted Meaning artifact, and host source spans.",
            responsibilities=(
                "Identify topics, goals, tasks, statements, questions, directions, and approvals.",
                "Classify interaction mode, claims, unresolved items, and explicit control signals.",
                "Preserve request-vs-assertion distinctions and exact source spans.",
            ),
            forbidden=(
                "Do not create final Rxxx requirements or decide claim truth.",
                "Do not retrieve Context, select/execute tools, persist memory, or answer.",
            ),
            next_consumers=("Intent Organizer",),
        ),
        inputs=("RAW_USER_PROMPT", "NORMALIZED_PROMPT", "MEANING_ARTIFACT", "HOST_SOURCE_SPANS"),
        refs=("SOURCE_SPAN", "MEANING_LOCAL_REF"),
        local_prefixes=("TGT_", "CLAIM_", "UNRESOLVED_"),
        response="TGT and communication breakdown plus interaction_mode, important_claims, unresolved_items, and explicit control_signals.",
        enums={
            "interaction_mode": (
                "straightforward",
                "conversational",
                "exploratory",
                "playful",
                "joking",
                "ordering_or_directive",
                "excited",
                "upset_sad",
                "upset_disappointed",
                "upset_angry_external",
                "upset_angry_at_model",
            ),
            "control_signal": (
                "AFFIRM_PRIOR",
                "CORRECT_PRIOR",
                "REJECT_PRIOR",
                "UNDO_PRIOR_EFFECT",
                "CONTINUE_PRIOR_STATE",
                "NONE",
                "AMBIGUOUS_TARGET",
            ),
        },
        empty="Individual categories may be empty; the overall analysis artifact may not be omitted.",
        uncertainty="Classify ambiguity explicitly and preserve unresolved items; never turn uncertain communication into a fabricated fact.",
        forbidden_output=(
            "Rxxx allocation",
            "claim truth judgment",
            "tool selection",
            "memory retrieval",
            "user clarification action",
        ),
        validation=(
            "all source spans exist in supplied host span map",
            "enums are legal",
            "request and assertion fields do not silently collapse into each other",
            "no undeclared fields",
        ),
        consumers=("R1_INTENT_ORGANIZER",),
    ),
    _contract(
        slug="r1.intent_organizer",
        mode=MODE_INTENT_ORGANIZER,
        adapter="INTENT_ORGANIZER",
        recipe_id="R1",
        awareness=_awareness(
            specialist="Intent Organizer",
            recipe="1 — Intent",
            authority=AuthorityClass.SEMANTIC_COMPOSITION,
            purpose=(
                "Compose the authoritative-intent proposal from accepted Meaning and Prompt Analyst artifacts: "
                "what requirements exist, how they depend, what Context is needed, and whether capabilities, memory, or clarification are implicated."
            ),
            input_origin="Validated Meaning + Prompt Analyst artifacts, current-turn source refs, compact capability availability.",
            responsibilities=(
                "Create a minimal requirement proposal using local keys.",
                "Preserve literal constraints and dependencies.",
                "Identify Context needs, capability candidates, memory candidates, blockers, and clarification need.",
            ),
            forbidden=(
                "Do not execute or create tool request packets.",
                "Do not query memory, claim tool success, write SQLite, decide terminal Completion, or allocate authoritative Rxxx IDs.",
            ),
            next_consumers=(
                "Host Intent validator/ID allocator",
                "Optional Intent Howard presentation",
            ),
        ),
        inputs=(
            "MEANING_ARTIFACT",
            "PROMPT_ANALYSIS_ARTIFACT",
            "CURRENT_TURN_SOURCE_REFS",
            "CAPABILITY_AVAILABILITY",
        ),
        refs=("SOURCE_SPAN", "CAPABILITY_ID"),
        local_prefixes=("REQ_", "GROUP_", "CTX_NEED_", "MEM_CAND_"),
        response="Primary/secondary intent proposal, locally keyed requirements, dependencies/grouping, Context needs, capability candidates, memory candidates, blockers, clarification state, and copied control signals.",
        enums=None,
        empty="A valid artifact must explicitly represent the communicated need; authoritative Rxxx allocation is host-only after validation.",
        uncertainty="Prefer context_resolution_first when bounded Context may resolve an ambiguity; require user clarification only when the contract cannot safely proceed otherwise.",
        forbidden_output=(
            "Rxxx invented by model",
            "tool request packet",
            "execution_status other than not_executed semantic metadata",
            "SQLite mutation",
            "terminal status",
        ),
        validation=(
            "every proposed requirement has a unique local key",
            "local requirement dependency graph is acyclic",
            "capability candidates exist in supplied compact registry when claimed",
            "literal constraints/source refs are preserved",
            "no authoritative IDs are invented",
        ),
        consumers=(
            "R1_HOST_INTENT_VALIDATOR",
            "R1_HOST_ID_ALLOCATOR",
            "R1_HOWARD_INTENT_COMMENT",
            "R2_CONTEXT",
        ),
        review_notes=(
            "Exact Organizer output schema and clarification vocabulary remain for joint schema review.",
        ),
    ),
    _contract(
        slug="r1.howard_intent_comment",
        mode=MODE_HOWARD_INTENT_COMMENT,
        adapter="CONVERSATIONAL_HOWARD",
        recipe_id="R1",
        awareness=_awareness(
            specialist="Conversational Howard / Intent comment",
            recipe="1 — Intent",
            authority=AuthorityClass.PRESENTATION_ONLY,
            purpose="Express the accepted Intent naturally for optional debugging/UI without changing its semantics.",
            input_origin="Accepted host-normalized Intent projection only.",
            responsibilities=("Naturalize the already accepted Intent.",),
            forbidden=(
                "Do not add requirements, research, facts, memory, tools, blockers, or clarification.",
                "Do not alter literal constraints.",
            ),
            next_consumers=("Host presentation sink",),
        ),
        inputs=("ACCEPTED_INTENT_PROJECTION",),
        refs=("Rxxx", "SOURCE_SPAN"),
        local_prefixes=(),
        response="Presentation-only natural-language Intent comment grounded solely in accepted Intent.",
        enums=None,
        empty="Empty comment is permitted only if the host elects not to expose the optional presentation; if invoked for output, empty text is invalid.",
        uncertainty="Reflect accepted unresolved/blocker state exactly; do not resolve it conversationally.",
        forbidden_output=(
            "new requirement",
            "new fact",
            "research",
            "tool request",
            "memory claim",
            "Intent mutation",
        ),
        validation=(
            "no new Rxxx/reference is introduced",
            "protected literals remain exact",
            "comment contains no authority-changing fields",
        ),
        consumers=("R1_PRESENTATION_SINK",),
    ),
    _contract(
        slug="r2.evidence_specialist",
        mode=MODE_CONTEXT_EVIDENCE,
        adapter="EVIDENCE_SPECIALIST",
        recipe_id="R2",
        awareness=_awareness(
            specialist="Evidence Specialist",
            recipe="2 — Context",
            authority=AuthorityClass.SEMANTIC_ASSESSMENT,
            purpose="Against the selected Context split and current Intent need, judge what the supplied bounded evidence supports.",
            input_origin="Run/loop/lane identity, needed Intent refs, lane purpose, split definition, candidate evidence + metadata.",
            responsibilities=(
                "Judge every supplied candidate for relevance, support, staleness, conflict, scope, and usefulness.",
                "Preserve unresolved uncertainty and explicit conflict.",
            ),
            forbidden=(
                "Do not query SQLite, create evidence IDs, write memory, answer the user, change Intent or Split, self-validate, or claim tool success.",
            ),
            next_consumers=("Host Evidence validator", "Conversational Howard / Context lane"),
        ),
        inputs=(
            "CONTEXT_LANE",
            "CONTEXT_SPLIT",
            "INTENT_NEED_REFS",
            "EVIDENCE_CANDIDATES",
            "EVIDENCE_METADATA",
        ),
        refs=("Rxxx", "Ixxx", "Lxxx", "SPLIT_ID", "Exxx"),
        local_prefixes=("JUDGMENT_",),
        response="Complete per-candidate supports/contradicts/relevant/irrelevant/ambiguous judgments.",
        enums={
            "evidence_status": (
                "supports",
                "contradicts",
                "relevant",
                "irrelevant",
                "ambiguous",
            ),
        },
        empty="A no-match/no-candidates lane is a valid explicit semantic result; silent omission is not.",
        uncertainty="Prefer partial/conflict/unresolved/no_match over unsupported certainty.",
        forbidden_output=(
            "SQLite query",
            "new Exxx",
            "memory write",
            "Intent mutation",
            "tool-success claim",
            "user-facing answer",
        ),
        validation=(
            "lane and split IDs are supplied and version-correct",
            "all evidence refs were supplied",
            "support spans exist in referenced evidence",
            "candidate placement is non-contradictory",
            "semantic enums are legal",
        ),
        consumers=("R2_HOST_EVIDENCE_VALIDATOR", "R2_HOWARD_CONTEXT_LANE"),
    ),
    _contract(
        slug="r2.howard_context_lane",
        mode=MODE_HOWARD_CONTEXT_LANE,
        adapter="CONVERSATIONAL_HOWARD",
        recipe_id="R2",
        awareness=_awareness(
            specialist="Conversational Howard / Context lane",
            recipe="2 — Context",
            authority=AuthorityClass.SEMANTIC_COMPOSITION,
            purpose="Determine what Context should be carried forward from one validated Context lane.",
            input_origin="Relevant original Intent refs plus host-validated accepted/partial/conflict/unresolved evidence and lane purpose.",
            responsibilities=(
                "Create bounded Context-point proposals with explicit support refs.",
                "Use supported, inference, or unresolved mode honestly.",
                "Preserve conflict/unresolved state rather than flattening it.",
            ),
            forbidden=(
                "Do not retrieve, invent support, change Intent, erase conflicts, execute tools, persist, decide terminal Completion, or answer the user.",
            ),
            next_consumers=(
                "Host Context-point validator/ID allocator",
                "Host lane report freezer",
            ),
        ),
        inputs=("INTENT_REFS", "VALIDATED_LANE_EVIDENCE", "LANE_PURPOSE"),
        refs=("Ixxx", "Rxxx", "Dxxx", "Exxx"),
        local_prefixes=("CTX_",),
        response="Context-point proposals carrying statement, basis, and direct evidence_refs.",
        enums={"context_point_mode": ("supported", "inference", "unresolved")},
        empty="Zero promoted Context points can be valid when the lane legitimately establishes only no-match/unresolved state; that state must remain explicit.",
        uncertainty="Use inference/unresolved modes with support refs; never present inference as direct support.",
        forbidden_output=(
            "authoritative Cxxx allocation",
            "retrieval request outside host loop",
            "unsupported fact",
            "Intent mutation",
            "tool action",
            "terminal status",
        ),
        validation=(
            "every support ref was supplied and legal for the lane",
            "local Context keys are unique",
            "Context-point mode is legal",
            "conflicts/unresolved conditions are not silently erased",
            "host allocates Cxxx only after acceptance",
        ),
        consumers=(
            "R2_HOST_CONTEXT_POINT_VALIDATOR",
            "R2_HOST_CONTEXT_ID_ALLOCATOR",
            "R2_LANE_REPORT_FREEZER",
        ),
    ),
    _contract(
        slug="r2.howard_context_final",
        mode=MODE_HOWARD_CONTEXT_FINAL,
        adapter="CONVERSATIONAL_HOWARD",
        recipe_id="R2",
        awareness=_awareness(
            specialist="Conversational Howard / final Context synthesis",
            recipe="2 — Context",
            authority=AuthorityClass.SEMANTIC_COMPOSITION,
            purpose="Given original accepted Intent and all validated Context results, compose only the grounded working state the next recipe should receive.",
            input_origin="Original bounded Intent, optional narrow direct input, and all completed validated Context loop reports.",
            responsibilities=(
                "Preserve current subject/job, resolved references, relevant constraints, conflicts/unresolved, and source refs.",
                "Preserve explicit do-not-assume boundaries.",
            ),
            forbidden=(
                "Do not rewrite Intent, invent project facts, execute, persist, decide terminal Completion, or answer the user.",
            ),
            next_consumers=("Host Context validator/freezer", "Decision"),
        ),
        inputs=("ACCEPTED_INTENT", "NARROW_DIRECT_INPUT", "CONTEXT_LOOP_REPORTS"),
        refs=("Rxxx", "Ixxx", "Dxxx", "Exxx", "Cxxx", "LANE_REPORT_ID"),
        local_prefixes=("CTX_SUMMARY_",),
        response="Cross-context relationships, conflicts, unresolved items, and do-not-assume boundaries over accepted Cxxx only.",
        enums=None,
        empty="No additional Context facts can be valid for a self-contained turn, but the final Context artifact must still explicitly represent readiness/unresolved state.",
        uncertainty="Carry unresolved/conflict state forward exactly; do not choose a winner without supplied authority.",
        forbidden_output=(
            "Intent rewrite",
            "invented project fact",
            "tool action",
            "persistence",
            "terminal Completion",
            "user-facing answer",
        ),
        validation=(
            "all referenced Context/Intent/evidence artifacts are accepted and supplied",
            "Intent requirements are unchanged",
            "conflict/unresolved state is preserved",
            "final artifact is structurally ready before Decision handoff",
        ),
        consumers=("R2_HOST_CONTEXT_FREEZER", "R3_DECISION"),
        review_notes=(
            "The source trace contained a slice-specific 'no lane reports' phrase; this pre-version generalizes it to all completed validated loop reports.",
        ),
    ),
    _contract(
        slug="r3.requirement_assessor",
        mode=MODE_REQUIREMENT_ASSESSOR,
        adapter="REQUIREMENT_ASSESSOR",
        recipe_id="R3",
        awareness=_awareness(
            specialist="Requirement Assessor",
            recipe="3 — Decision",
            authority=AuthorityClass.SEMANTIC_ASSESSMENT,
            purpose="For one immutable requirement, decide whether it is ready for completion or requires work, persistence, or is blocked.",
            input_origin="One host-owned Rxxx, relevant accepted Context, capability availability.",
            responsibilities=(
                "Choose exactly one READY, WORK_REQUIRED, BLOCKED, or PERSISTENCE_REQUIRED disposition.",
                "Explain only the semantic reason and any needed work/evidence target.",
            ),
            forbidden=(
                "Do not execute or emit tool request syntax.",
                "Do not write SQLite, mutate Rxxx, make the cross-requirement graph, or assign terminal Completion status.",
            ),
            next_consumers=("Host assessment validator", "Plan Composer"),
        ),
        inputs=(
            "IMMUTABLE_REQUIREMENT",
            "RELEVANT_ACCEPTED_CONTEXT",
            "CAPABILITY_AVAILABILITY",
            "DECISION_TRIGGER",
        ),
        refs=("Rxxx", "Cxxx", "CAPABILITY_ID", "PRIOR_WORK_REF"),
        local_prefixes=("ASSESS_", "WORK_NEED_"),
        response="Per-requirement disposition, basis refs, need summary, work needs/evidence targets, blocker data, and post-work obligations.",
        enums={
            "disposition": ("READY", "WORK_REQUIRED", "BLOCKED", "PERSISTENCE_REQUIRED"),
            "block_reason": (
                "USER_INFORMATION_NEEDED",
                "MISSING_CONTEXT",
                "CAPABILITY_UNAVAILABLE",
                "INVALID_UPSTREAM_STATE",
            ),
            "work_origin": ("ORIGINAL", "DISCOVERY", "REPAIR"),
        },
        empty="Empty output is invalid; every in-scope requirement receives one explicit Decision disposition.",
        uncertainty="Use BLOCKED/MISSING_CONTEXT only when a legitimate path cannot be formed; minor uncertainty alone is not automatically a blocker.",
        forbidden_output=(
            "tool syntax",
            "receipt",
            "SQLite operation",
            "new Rxxx",
            "terminal status",
            "cross-requirement graph",
        ),
        validation=(
            "requirement ID exactly matches the one supplied",
            "basis refs exist and are in scope",
            "disposition and block reason are legal",
            "WORK_REQUIRED has at least one work need",
            "READY has no required work need",
            "BLOCKED includes block reason",
            "PERSISTENCE_REQUIRED does not request SQLite execution",
        ),
        consumers=("R3_HOST_ASSESSMENT_VALIDATOR", "R3_PLAN_COMPOSER"),
    ),
    _contract(
        slug="r3.plan_composer",
        mode=MODE_PLAN_COMPOSER,
        adapter="PLAN_COMPOSER",
        recipe_id="R3",
        awareness=_awareness(
            specialist="Plan Composer",
            recipe="3 — Decision",
            authority=AuthorityClass.SEMANTIC_COMPOSITION,
            purpose="Compose the smallest legitimate shared work graph from all validated requirement assessments.",
            input_origin="Validated per-R assessments, capability registry, scope, and any prior accepted work.",
            responsibilities=(
                "Merge only genuinely shared work.",
                "Produce local work keys for new work.",
                "Preserve blocked, ready, and persistence obligations.",
            ),
            forbidden=(
                "Do not execute capabilities, fabricate receipts, perform Persistence, allocate authoritative Wxxx IDs, or decide terminal Completion.",
            ),
            next_consumers=("Host graph/capability validator", "Host Wxxx allocator"),
        ),
        inputs=(
            "VALIDATED_REQUIREMENT_ASSESSMENTS",
            "CAPABILITY_REGISTRY_PROJECTION",
            "DECISION_SCOPE",
            "PRIOR_ACCEPTED_WORK",
        ),
        refs=("Rxxx", "Axxx", "Cxxx", "Wxxx", "CAPABILITY_ID"),
        local_prefixes=("WORK_", "EDGE_", "PERSIST_"),
        response="Minimal shared work graph proposal with locally keyed new work, requirement links, dependencies, capability targets, evidence targets, and preserved non-work obligations.",
        enums=None,
        empty="Zero new work is valid when assessments establish that no executable work is legitimate; READY/BLOCKED/PERSISTENCE_REQUIRED states must still be preserved.",
        uncertainty="Do not create speculative work merely to eliminate a blocker; preserve blocked state when prerequisites are missing.",
        forbidden_output=(
            "authoritative Wxxx allocation",
            "execution",
            "receipt",
            "SQLite",
            "terminal status",
        ),
        validation=(
            "every referenced assessment/requirement exists",
            "local work keys are unique",
            "graph is acyclic and dependencies are legal",
            "capability targets exist in supplied registry",
            "shared work merges only compatible goals/evidence targets",
            "blocked requirements receive no illegitimate executable work",
        ),
        consumers=(
            "R3_HOST_GRAPH_VALIDATOR",
            "R3_HOST_W_ID_ALLOCATOR",
            "R4_EXECUTION_HOST",
            "R6_PERSISTENCE",
        ),
        review_notes=(
            "Exact work-type/work-origin enum sets are intentionally deferred to the schema pass rather than partially copied here.",
        ),
    ),
    _contract(
        slug="r5.evidence_reconciler",
        mode=MODE_EVIDENCE_RECONCILER,
        adapter="EVIDENCE_RECONCILER",
        recipe_id="R5",
        awareness=_awareness(
            specialist="Evidence Reconciler",
            recipe="5 — Reconciliation",
            authority=AuthorityClass.SEMANTIC_ASSESSMENT,
            purpose="Determine what the exact returned evidence for one Wxxx establishes against its original evidence target.",
            input_origin="One Wxxx, its requirement refs/evidence target, immutable receipt/result refs, and relevant active Context.",
            responsibilities=(
                "Choose ESTABLISHED, PARTIAL, NOT_ESTABLISHED, or CONFLICT.",
                "Identify established claims with exact support, gaps/conflicts, material discoveries, Context-impact candidates, and execution basis.",
            ),
            forbidden=(
                "Do not create Rxxx, write SQLite, promote Context, assign terminal Completion, request tools, edit receipts, or invent operation outcomes.",
            ),
            next_consumers=("Host Evidence Finding validator/allocator", "Reconciliation Composer"),
        ),
        inputs=(
            "WORK_ITEM",
            "EVIDENCE_TARGET",
            "REQUIREMENT_REFS",
            "IMMUTABLE_EXECUTION_RECEIPTS",
            "RESULT_ITEMS",
            "RELEVANT_ACTIVE_CONTEXT",
            "HOST_SIGNAL_PACK",
        ),
        refs=("Wxxx", "Rxxx", "RECxxx", "RESULT_REF", "Cxxx"),
        local_prefixes=("EF_", "DISCOVERY_", "CTX_IMPACT_"),
        response="Evidence Finding proposal containing semantic_state, established claims/support refs, not-established targets, conflicts, material discoveries, Context impacts, and immutable execution basis.",
        enums={
            "semantic_state": ("ESTABLISHED", "PARTIAL", "NOT_ESTABLISHED", "CONFLICT"),
            "confidence_label": ("HIGH", "MEDIUM", "LOW"),
            "provenance_class": (
                "DIRECT_HOST_RECEIPT",
                "DIRECT_SOURCE_EVIDENCE",
                "MULTI_SOURCE_SUPPORT",
                "INFERENCE_FROM_EVIDENCE",
                "UNRESOLVED",
            ),
        },
        empty="No established claim is valid when the target is NOT_ESTABLISHED; an explicit semantic_state and gap basis are still required.",
        uncertainty="Preserve partial evidence, conflict, and missing evidence; no support ref means no promotable claim.",
        forbidden_output=(
            "new Rxxx",
            "SQLite",
            "Context promotion",
            "terminal status",
            "tool request",
            "receipt mutation",
        ),
        validation=(
            "work/requirement/receipt/result refs are supplied and legal",
            "semantic_state is legal",
            "every established claim has support refs",
            "conflict refs exist",
            "discovery candidates carry source refs",
            "no operation is claimed without immutable receipt basis",
        ),
        consumers=("R5_HOST_EF_VALIDATOR", "R5_HOST_EF_ALLOCATOR", "R5_RECONCILIATION_COMPOSER"),
    ),
    _contract(
        slug="r5.reconciliation_composer",
        mode=MODE_RECONCILIATION_COMPOSER,
        adapter="RECONCILIATION_COMPOSER",
        recipe_id="R5",
        awareness=_awareness(
            specialist="Reconciliation Composer",
            recipe="5 — Reconciliation",
            authority=AuthorityClass.SEMANTIC_COMPOSITION,
            purpose="Determine cross-work consequences of validated evidence findings without deciding terminal requirement status.",
            input_origin="Validated Evidence Findings, active Context, immutable requirement scope, and prior Reconciliation state.",
            responsibilities=(
                "Combine findings and preserve remaining gaps/conflicts.",
                "Distinguish material discovery from repair.",
                "Propose Context impact, Derived Need, repair, Persistence relevance, and legal next transition.",
            ),
            forbidden=(
                "Do not assign terminal SATISFIED/PARTIALLY_SATISFIED/BLOCKED/FAILED.",
                "Do not execute tools, write DB state, directly promote Context lanes, rewrite Intent, or mutate receipts.",
            ),
            next_consumers=("Host Reconciliation transition validator",),
        ),
        inputs=(
            "VALIDATED_EVIDENCE_FINDINGS",
            "ACTIVE_CONTEXT",
            "IMMUTABLE_REQUIREMENT_SCOPE",
            "PRIOR_RECONCILIATION_STATE",
        ),
        refs=("EFxxx", "Rxxx", "Wxxx", "Cxxx", "RECxxx", "DNxxx", "REPAIR_REQUEST_REF"),
        local_prefixes=("DN_", "CTX_IMPACT_", "REPAIR_", "PERSIST_CAND_"),
        response="Cross-work Reconciliation proposal with nonterminal posture flags, remaining gaps/conflicts, Context impacts, Derived Needs, repairs, persistence relevance, and next-transition recommendations.",
        enums={
            "posture_flag": (
                "NO_GAP_IDENTIFIED",
                "EVIDENCE_GAP_REMAINS",
                "CONFLICT_PRESENT",
                "CONTEXT_REENTRY_REQUIRED",
                "DISCOVERY_FOLLOWUP_REQUIRED",
                "REPAIR_REQUIRED",
                "PERSISTENCE_RELEVANT",
            ),
            "consequence_class": (
                "DISCOVERY",
                "REPAIR_NEEDED",
                "CONTEXT_UPDATE",
                "PERSISTENCE_RELEVANCE",
            ),
        },
        empty="No further action is a valid explicit outcome when NO_GAP_IDENTIFIED is supported; silent omission of in-scope requirements is invalid.",
        uncertainty="Keep conflict/gap states nonterminal and route bounded re-entry/repair only when supported.",
        forbidden_output=(
            "terminal Completion status",
            "tool call",
            "DB write",
            "direct Context promotion",
            "Intent rewrite",
            "receipt mutation",
        ),
        validation=(
            "all EF/requirement/context refs are supplied",
            "posture flags are legal and nonterminal",
            "Derived Need/repair/Context-impact local keys are unique",
            "every proposed transition is host-legal",
            "discovery is not mislabeled as repair",
        ),
        consumers=(
            "R5_HOST_TRANSITION_VALIDATOR",
            "R2_CONTEXT_REENTRY",
            "R3_DECISION_REENTRY",
            "R6_PERSISTENCE",
            "R7_COMPLETION",
        ),
    ),
    _contract(
        slug="r6.persistence_assessor",
        mode=MODE_PERSISTENCE_ASSESSOR,
        adapter="PERSISTENCE_ASSESSOR",
        recipe_id="R6",
        awareness=_awareness(
            specialist="Persistence Assessor",
            recipe="6 — Persistence",
            authority=AuthorityClass.SEMANTIC_ASSESSMENT,
            purpose="For one persistence obligation/candidate, determine the durable semantic consequence justified by the supplied frozen memory snapshot and provenance.",
            input_origin="One persistence item, authority class, provenance, relevant Context/Evidence Finding refs, bounded semantic-memory snapshot, and policy.",
            responsibilities=(
                "Judge durability and resolve entity identity.",
                "Propose semantic claims/relations and preserve change-vs-correction semantics.",
                "Recommend one item result while preserving ambiguity when identity is unresolved.",
            ),
            forbidden=(
                "Do not allocate permanent semantic UUIDs, execute SQL, mutate transcript/Rxxx, assign Completion, or perform unrelated memory lookup.",
            ),
            next_consumers=("Host Persistence Assessment validator", "Persistence Composer"),
        ),
        inputs=(
            "PERSISTENCE_ITEM",
            "ITEM_AUTHORITY_CLASS",
            "PROVENANCE",
            "RELEVANT_CONTEXT",
            "RELEVANT_EVIDENCE_FINDINGS",
            "FROZEN_MEMORY_SNAPSHOT",
            "PERSISTENCE_POLICY",
        ),
        refs=(
            "Rxxx",
            "Cxxx",
            "EFxxx",
            "ITEM_UUID",
            "MEMORY_ENTITY_UUID",
            "MEMORY_CLAIM_UUID",
            "MEMORY_SNAPSHOT_UUID",
        ),
        local_prefixes=("PA_", "NEW_ENTITY_", "CLAIM_PROPOSAL_"),
        response="Per-item durability judgment, entity resolution, semantic claim proposals, existing-claim relation, alias implications, recommended result, reason codes, and provenance refs.",
        enums={
            "item_authority_class": ("NORMATIVE", "ADVISORY"),
            "durability_judgment": ("DURABLE", "NOT_DURABLE", "POLICY_BLOCKED", "INSUFFICIENT"),
            "entity_resolution": (
                "MATCH_EXISTING",
                "CREATE_NEW",
                "IDENTITY_AMBIGUOUS",
                "NEEDS_MORE_MEMORY",
            ),
            "semantic_relation": (
                "SAME",
                "CHANGE",
                "CORRECTION",
                "REFINEMENT",
                "CONFLICT",
                "RETRACTION",
                "UNRELATED",
            ),
        },
        empty="Every supplied persistence item requires an explicit assessment; no silent drop is legal.",
        uncertainty="Use IDENTITY_AMBIGUOUS/NEEDS_MORE_MEMORY/INSUFFICIENT rather than creating duplicate entities or guessing identity.",
        forbidden_output=(
            "permanent semantic UUID",
            "SQL",
            "transcript mutation",
            "Rxxx mutation",
            "Completion status",
            "unbounded memory request",
        ),
        validation=(
            "item UUID/authority/provenance match supplied item",
            "memory snapshot identity/base commit are preserved",
            "all referenced memory entities/claims were supplied",
            "semantic enums are legal",
            "new records use local refs only",
            "no executable SQL appears",
        ),
        consumers=("R6_HOST_PA_VALIDATOR", "R6_PERSISTENCE_COMPOSER"),
    ),
    _contract(
        slug="r6.persistence_composer",
        mode=MODE_PERSISTENCE_COMPOSER,
        adapter="PERSISTENCE_COMPOSER",
        recipe_id="R6",
        awareness=_awareness(
            specialist="Persistence Composer",
            recipe="6 — Persistence",
            authority=AuthorityClass.SEMANTIC_COMPOSITION,
            purpose="Compose the smallest coherent atomic semantic mutation plan from all validated Persistence assessments.",
            input_origin="Validated Persistence Assessments, normative/advisory item lists, frozen memory base, and semantic policy.",
            responsibilities=(
                "Cover every normative obligation exactly once and explicitly disposition every advisory candidate.",
                "Combine duplicate semantic consequences where legitimate.",
                "Propose allowed semantic mutation operations with local temporary refs and transaction properties.",
            ),
            forbidden=(
                "Do not execute SQL, allocate permanent UUIDs, mutate upstream artifacts, or assign Completion status.",
            ),
            next_consumers=(
                "Host Persistence plan validator",
                "Host UUID allocator",
                "Atomic Persistence transaction host",
            ),
        ),
        inputs=(
            "VALIDATED_PERSISTENCE_ASSESSMENTS",
            "NORMATIVE_OBLIGATIONS",
            "ADVISORY_CANDIDATES",
            "FROZEN_MEMORY_BASE",
            "SEMANTIC_POLICY",
        ),
        refs=(
            "PAxxx",
            "ITEM_UUID",
            "Rxxx",
            "MEMORY_ENTITY_UUID",
            "MEMORY_CLAIM_UUID",
            "MEMORY_ALIAS_UUID",
            "MEMORY_CONFLICT_UUID",
        ),
        local_prefixes=("PP_", "NEW_E", "NEW_CLAIM_", "NEW_ALIAS_", "NEW_CONFLICT_"),
        response="Atomic semantic mutation plan with complete item_results, local new-entity refs, claim/alias/conflict/entity-merge mutations, transaction properties, provenance links, and diagnostics.",
        enums={
            "mutation_operation": (
                "CREATE_ENTITY",
                "CREATE_CLAIM",
                "SUPERSEDE_CLAIM",
                "RETRACT_CLAIM",
                "SET_CLAIM_CONTESTED",
                "ADD_ALIAS",
                "SET_ALIAS_STATUS",
                "CREATE_CONFLICT",
                "RESOLVE_CONFLICT",
                "MERGE_ENTITY",
                "NO_CHANGE",
            ),
            "advisory_disposition": ("SAVED", "IGNORED", "DEFERRED"),
            "plan_disposition": (
                "WRITE",
                "NO_CHANGE",
                "IGNORE",
                "DEFER",
                "BLOCKED",
                "POLICY_REJECT",
                "COALESCED",
            ),
        },
        empty="A no-change transaction can be valid, but every normative/advisory item must still receive explicit coverage/disposition.",
        uncertainty="Preserve ambiguous identity/conflict states; never force a merge or create a duplicate merely to complete the plan.",
        forbidden_output=(
            "SQL",
            "permanent UUID allocation",
            "upstream mutation",
            "Completion status",
            "silent obligation drop",
        ),
        validation=(
            "every normative obligation appears exactly once",
            "every advisory candidate receives explicit disposition",
            "all PA/memory refs exist",
            "local refs are unique and acyclic",
            "mutation operations are legal",
            "expected memory base commit is preserved",
            "no executable SQL appears",
        ),
        consumers=(
            "R6_HOST_PLAN_VALIDATOR",
            "R6_HOST_UUID_ALLOCATOR",
            "R6_ATOMIC_TRANSACTION_HOST",
            "R7_COMPLETION",
        ),
    ),
    _contract(
        slug="r7.completion_assessor",
        mode=MODE_COMPLETION_ASSESSOR,
        adapter="COMPLETION_ASSESSOR",
        recipe_id="R7",
        awareness=_awareness(
            specialist="Completion Assessor",
            recipe="7 — Completion",
            authority=AuthorityClass.SEMANTIC_ASSESSMENT,
            purpose="For one immutable Rxxx, determine its terminal standing from the authoritative closure bundle.",
            input_origin="One requirement plus its accepted Intent/Context/Decision/Execution/Reconciliation/Persistence outcome chain.",
            responsibilities=(
                "Choose exactly one SATISFIED, PARTIALLY_SATISFIED, BLOCKED, or FAILED status.",
                "Ground fulfilled/unmet components, blockers, failures, and user-facing guidance in supplied refs.",
            ),
            forbidden=(
                "Do not create new work, reopen recipes, execute tools, persist, invent facts, or write final user prose.",
            ),
            next_consumers=(
                "Host Completion Assessment validator/allocator",
                "Completion Composer",
            ),
        ),
        inputs=(
            "REQUIREMENT_CLOSURE_BUNDLE",
            "ALLOWED_TERMINAL_STATUSES",
            "COMPLETION_POLICY_SNAPSHOT",
        ),
        refs=("Rxxx", "Cxxx", "Wxxx", "RECxxx", "EFxxx", "PRC_REF", "DNxxx", "RRQ_REF"),
        local_prefixes=("CA_",),
        response="Per-R terminal_status plus fulfilled/unmet components, blockers, failure causes, and conflict refs.",
        enums={
            "terminal_status": ("SATISFIED", "PARTIALLY_SATISFIED", "BLOCKED", "FAILED"),
            "persistence_effect": (
                "REQUIRED_AND_COMMITTED",
                "REQUIRED_ALREADY_SATISFIED",
                "REQUIRED_BLOCKED",
                "REQUIRED_FAILED",
                "NOT_REQUIRED",
            ),
        },
        empty="Empty output is invalid; every immutable in-scope Rxxx receives one terminal standing.",
        uncertainty="Preserve blockers/failures/gaps exactly; PARTIALLY_SATISFIED requires genuine fulfilled material and a material remaining gap.",
        forbidden_output=(
            "new work",
            "recipe re-entry",
            "tool call",
            "persistence mutation",
            "new fact",
            "final response prose",
        ),
        validation=(
            "Rxxx exactly matches supplied closure bundle",
            "terminal status is legal",
            "all support/blocker/failure refs are reachable from closure bundle",
            "status consistency gates pass",
            "no new work/tool/SQLite/re-entry appears",
            "no final-response prose field appears",
        ),
        consumers=("R7_HOST_CA_VALIDATOR", "R7_HOST_CA_ALLOCATOR", "R7_COMPLETION_COMPOSER"),
    ),
    _contract(
        slug="r7.completion_composer",
        mode=MODE_COMPLETION_COMPOSER,
        adapter="COMPLETION_COMPOSER",
        recipe_id="R7",
        awareness=_awareness(
            specialist="Completion Composer",
            recipe="7 — Completion",
            authority=AuthorityClass.SEMANTIC_COMPOSITION,
            purpose="Compose the turn-level Final Standing proposal from already validated per-requirement Completion Assessments.",
            input_origin="All accepted Completion Assessments and the immutable requirement list.",
            responsibilities=(
                "Preserve each terminal status exactly.",
                "Establish overall posture, result focus, required disclosures, and shared user-facing facts/blockers/failures.",
            ),
            forbidden=(
                "Do not re-decide Completion Assessment statuses, drop requirements, invent facts, execute, persist, or write user-facing final prose.",
            ),
            next_consumers=(
                "Host Completion validator/freezer producing the Final Standing Packet",
            ),
        ),
        inputs=(
            "VALIDATED_COMPLETION_ASSESSMENTS",
            "IMMUTABLE_REQUIREMENT_LIST",
            "CROSS_REQUIREMENT_RELATIONSHIPS",
            "HOST_COVERAGE_SIGNALS",
            "COMPLETION_POLICY_SNAPSHOT",
        ),
        refs=("Rxxx", "CAxxx", "FACT_REF", "BLOCKER_REF", "FAILURE_REF"),
        local_prefixes=("CP_",),
        response="Presentation-only result focus, supported shared items, disclosure emphasis, protected-literal importance, and diagnostics; statuses remain host-owned inputs.",
        enums={"overall_turn_posture": ("ALL_SATISFIED", "MIXED", "BLOCKED", "FAILED")},
        empty="Empty output is invalid when any Rxxx exists; every immutable requirement must be covered exactly once.",
        uncertainty="Organization may expose mixed/blocker/failure posture but may not upgrade or downgrade a per-R status.",
        forbidden_output=(
            "status mutation",
            "dropped Rxxx",
            "invented fact",
            "execution",
            "persistence",
            "final prose",
        ),
        validation=(
            "every Rxxx is covered exactly once",
            "every CA ref exists",
            "every per-R terminal status exactly matches source CA",
            "overall posture is legal",
            "result refs originate in source CA artifacts",
            "no final prose/tool/SQL/Persistence mutation appears",
        ),
        consumers=("R7_HOST_COMPLETION_VALIDATOR", "R7_FINAL_STANDING_PACKET_FREEZER", "R8_RESULT"),
    ),
    _contract(
        slug="r8.howard_result_comment",
        mode=MODE_HOWARD_RESULT_COMMENT,
        adapter="CONVERSATIONAL_HOWARD",
        recipe_id="R8",
        awareness=_awareness(
            specialist="Conversational Howard / Result comment",
            recipe="8 — Result",
            authority=AuthorityClass.PRESENTATION_ONLY,
            purpose="Naturalize one frozen requirement standing without changing its status or facts.",
            input_origin="One result-comment packet projected from the Final Standing Packet.",
            responsibilities=(
                "State the frozen standing using only supplied allowed facts and disclosures.",
            ),
            forbidden=(
                "Do not mutate status, add facts, perform tools/persistence, expose internal implementation details, or override Literal Lock.",
            ),
            next_consumers=("Host result-comment validator",),
        ),
        inputs=("RESULT_COMMENT_PACKET", "DISCLOSURE_RULES", "LITERAL_LOCK"),
        refs=("Rxxx", "FSP_REF", "FACT_REF", "BLOCKER_REF", "FAILURE_REF"),
        local_prefixes=("RCM_",),
        response="Exactly one bounded comment string preserving frozen standing and authorized disclosures.",
        enums={"terminal_status": ("SATISFIED", "PARTIALLY_SATISFIED", "BLOCKED", "FAILED")},
        empty="If the host invokes this mode for a required comment, empty output is invalid.",
        uncertainty="Use only the frozen standing/facts; do not soften an unresolved blocker/failure into certainty.",
        forbidden_output=(
            "status change",
            "new fact",
            "tool action",
            "persistence",
            "internal implementation disclosure",
            "literal-lock override",
        ),
        validation=(
            "standing language is consistent with frozen status",
            "required disclosures are present",
            "must-not-claim rules pass",
            "protected literals are exact",
            "no new authoritative facts/refs appear",
        ),
        consumers=("R8_HOST_RESULT_COMMENT_VALIDATOR", "R8_HOWARD_RESULT_FINAL"),
    ),
    _contract(
        slug="r8.howard_result_final",
        mode=MODE_HOWARD_RESULT_FINAL,
        adapter="CONVERSATIONAL_HOWARD",
        recipe_id="R8",
        awareness=_awareness(
            specialist="Conversational Howard / final Result composition",
            recipe="8 — Result",
            authority=AuthorityClass.PRESENTATION_ONLY,
            purpose="Compose the final user-facing response from frozen standings while obeying all required disclosures and literal locks.",
            input_origin="Final Standing Packet projections, validated result comments, disclosure map, Literal Lock, response budget, and style/publication constraints.",
            responsibilities=(
                "Produce only final prose consistent with frozen statuses/facts.",
                "Honor mandatory disclosures and protected literal constraints.",
            ),
            forbidden=(
                "Do not alter statuses, invent facts, hide required disclosures, change locked literal text, claim unperformed tools/persistence, or expose internal pipeline state.",
            ),
            next_consumers=("Host final validator", "Publication host"),
        ),
        inputs=(
            "RAW_USER_PROMPT",
            "RESOLVED_REQUEST_PRESENTATION",
            "FINAL_STANDING_PROJECTION",
            "VALIDATED_RESULT_COMMENTS",
            "DISCLOSURE_MAP",
            "LITERAL_LOCK",
            "RESPONSE_BUDGET",
            "STYLE_POLICY",
            "PUBLICATION_CONSTRAINTS",
        ),
        refs=("FSP_REF", "RESULT_COMMENT_REF", "FACT_REF", "BLOCKER_REF", "FAILURE_REF"),
        local_prefixes=(),
        response="final_response_text only; host wraps validated text into the Result artifact and publication receipt.",
        enums=None,
        empty="Empty final_response_text is invalid for a publishable turn unless a separate deterministic host policy explicitly owns the response.",
        uncertainty="Communicate frozen uncertainty/blockers/failures faithfully; presentation cannot create certainty absent from Completion.",
        forbidden_output=(
            "status mutation",
            "new fact",
            "hidden required disclosure",
            "literal mutation",
            "tool/persistence claim",
            "internal pipeline state",
        ),
        validation=(
            "UTF-8/size gate passes",
            "forbidden internal-ID scan passes",
            "Literal Lock passes",
            "MUST_MENTION coverage passes",
            "must-not-claim rules pass",
            "terminal-standing language remains consistent",
            "response budget passes",
        ),
        consumers=("R8_HOST_FINAL_VALIDATOR", "R8_PUBLICATION_HOST"),
    ),
)


def _validate_pre_registry(records: tuple[AAEContractRecord, ...]) -> None:
    contract_ids = [record.contract_id for record in records]
    mode_ids = [record.specialist_mode_id for record in records]
    adapters = {record.physical_adapter_id for record in records}

    if len(records) != 20:
        raise RuntimeError(
            f"pre-version AAE registry must contain 20 logical modes, got {len(records)}"
        )
    if len(set(contract_ids)) != len(contract_ids):
        raise RuntimeError("duplicate AAE contract_id")
    if len(set(mode_ids)) != len(mode_ids):
        raise RuntimeError("duplicate specialist_mode_id")
    if adapters != set(PHYSICAL_ADAPTER_IDS):
        raise RuntimeError("physical adapter roster does not match the frozen core 15")

    for record in records:
        if record.registry_status is not RegistryStatus.PRE_VERSION:
            raise RuntimeError(
                f"{record.contract_id}: pre-version record unexpectedly marked frozen"
            )
        if record.dispatch_enabled or record.runtime_ready:
            raise RuntimeError(
                f"{record.contract_id}: pre-version registry must not permit dispatch"
            )
        if record.global_awareness_version != GLOBAL_VERSION:
            raise RuntimeError(f"{record.contract_id}: unknown Global Awareness version")
        if not record.input_schema.schema_id or not record.output_schema.schema_id:
            raise RuntimeError(
                f"{record.contract_id}: schema references are required even before freeze"
            )
        if not record.awareness.purpose or not record.awareness.next_consumers:
            raise RuntimeError(f"{record.contract_id}: incomplete Specialist Awareness")


_validate_pre_registry(_CONTRACTS)

AAE_REGISTRY_PRE_V1: Final[Mapping[str, AAEContractRecord]] = MappingProxyType(
    {record.specialist_mode_id: record for record in _CONTRACTS}
)


def get_contract(specialist_mode_id: str) -> AAEContractRecord:
    """Return one pre-version contract by logical mode, failing closed if unknown."""

    try:
        return AAE_REGISTRY_PRE_V1[specialist_mode_id]
    except KeyError as exc:
        raise KeyError(f"unknown AAE specialist mode: {specialist_mode_id}") from exc


def contracts_for_adapter(physical_adapter_id: str) -> tuple[AAEContractRecord, ...]:
    """Return all logical-mode contracts bound to one physical adapter identity."""

    return tuple(
        record
        for record in AAE_REGISTRY_PRE_V1.values()
        if record.physical_adapter_id == physical_adapter_id
    )
