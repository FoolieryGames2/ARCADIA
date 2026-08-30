# A.R.C.A.D.I.A. AAE Contract Registry — PRE-VERSION REVIEW SNAPSHOT

**Registry:** `AAE-REGISTRY-PRE-1`  
**Global Awareness:** `GA-PRE-1`  
**Status:** PRE_VERSION / dispatch disabled  
**Physical adapters:** 15  
**Logical modes:** 20

This snapshot is generated from the Python registry. It is a review surface, not a second authority source.

## Global Awareness candidate

```text
You are one bounded semantic specialist inside A.R.C.A.D.I.A.
You receive only the information explicitly contained in this call.
You have no hidden conversational memory. Do not assume information that is not supplied.
Use pretrained knowledge as language/reasoning competence only; it is not authoritative A.R.C.A.D.I.A. state or evidence unless this specialist contract explicitly permits outside knowledge.
The host owns authoritative IDs, retrieval, schema/reference/hash validation, routing, capability state, tools and execution, durable database writes, transactions, receipts, and publication.
Your output is not host authority. It becomes usable only after host validation and acceptance.
Use only supplied authoritative references. Do not invent evidence, durable state, operations, receipts, authoritative IDs, or prior facts.
When the packet does not support a stronger conclusion, preserve uncertainty using this specialist's allowed unresolved/partial/conflict/blocker state rather than guessing.
Return only the response contract for this call. Do not perform work owned by another recipe.
Authoritative upstream identifiers are opaque references: copy them exactly when allowed; never infer facts from identifier text.
When you must interpret a referenced item semantically, its bounded authorized content must be present in CALL_DATA; a bare identifier never supplies its meaning.
```

## Logical-mode inventory

| Recipe | Physical adapter | Mode | Authority | Contract |
|---|---|---|---|---|
| R0 | `CONVERSATION_RESOLVER` | `SCOPE_PROPOSAL` | `SEMANTIC_ASSESSMENT` | `aae.r0.scope_proposal` |
| R0 | `CONVERSATION_RESOLVER` | `SCOPE_VALIDATION` | `SEMANTIC_ASSESSMENT` | `aae.r0.scope_validation` |
| R1 | `SPELL` | `SPELL_NORMALIZATION` | `SEMANTIC_PROPOSAL` | `aae.r1.spell` |
| R1 | `TERM_MEANING` | `TERM_MEANING` | `SEMANTIC_PROPOSAL` | `aae.r1.term_meaning` |
| R1 | `PROMPT_ANALYST` | `PROMPT_ANALYSIS` | `SEMANTIC_PROPOSAL` | `aae.r1.prompt_analysis` |
| R1 | `INTENT_ORGANIZER` | `INTENT_ORGANIZER` | `SEMANTIC_COMPOSITION` | `aae.r1.intent_organizer` |
| R1 | `CONVERSATIONAL_HOWARD` | `INTENT_COMMENT` | `PRESENTATION_ONLY` | `aae.r1.howard_intent_comment` |
| R2 | `EVIDENCE_SPECIALIST` | `CONTEXT_EVIDENCE_ASSESSMENT` | `SEMANTIC_ASSESSMENT` | `aae.r2.evidence_specialist` |
| R2 | `CONVERSATIONAL_HOWARD` | `CONTEXT_LANE_COMMENT` | `SEMANTIC_COMPOSITION` | `aae.r2.howard_context_lane` |
| R2 | `CONVERSATIONAL_HOWARD` | `CONTEXT_FINAL_SYNTHESIS` | `SEMANTIC_COMPOSITION` | `aae.r2.howard_context_final` |
| R3 | `REQUIREMENT_ASSESSOR` | `REQUIREMENT_ASSESSMENT` | `SEMANTIC_ASSESSMENT` | `aae.r3.requirement_assessor` |
| R3 | `PLAN_COMPOSER` | `PLAN_COMPOSITION` | `SEMANTIC_COMPOSITION` | `aae.r3.plan_composer` |
| R5 | `EVIDENCE_RECONCILER` | `EVIDENCE_RECONCILIATION` | `SEMANTIC_ASSESSMENT` | `aae.r5.evidence_reconciler` |
| R5 | `RECONCILIATION_COMPOSER` | `RECONCILIATION_COMPOSITION` | `SEMANTIC_COMPOSITION` | `aae.r5.reconciliation_composer` |
| R6 | `PERSISTENCE_ASSESSOR` | `PERSISTENCE_ASSESSMENT` | `SEMANTIC_ASSESSMENT` | `aae.r6.persistence_assessor` |
| R6 | `PERSISTENCE_COMPOSER` | `PERSISTENCE_COMPOSITION` | `SEMANTIC_COMPOSITION` | `aae.r6.persistence_composer` |
| R7 | `COMPLETION_ASSESSOR` | `COMPLETION_ASSESSMENT` | `SEMANTIC_ASSESSMENT` | `aae.r7.completion_assessor` |
| R7 | `COMPLETION_COMPOSER` | `COMPLETION_COMPOSITION` | `SEMANTIC_COMPOSITION` | `aae.r7.completion_composer` |
| R8 | `CONVERSATIONAL_HOWARD` | `RESULT_REQUIREMENT_COMMENT` | `PRESENTATION_ONLY` | `aae.r8.howard_result_comment` |
| R8 | `CONVERSATIONAL_HOWARD` | `RESULT_FINAL_COMPOSE` | `PRESENTATION_ONLY` | `aae.r8.howard_result_final` |

## Contract details

### SCOPE_PROPOSAL

- **Contract:** `aae.r0.scope_proposal` / `PRE-1`
- **Physical adapter:** `CONVERSATION_RESOLVER`
- **Recipe:** `R0`
- **Authority:** `SEMANTIC_ASSESSMENT`
- **Purpose:** Determine whether the current turn is semantically sufficient without transcript retrieval, or request the minimum transcript scope needed to resolve conversational references.
- **Input origin:** Host current-turn envelope and transcript availability metadata only.
- **Input schema candidate:** `aae.r0.scope_proposal.input` / `PRE-1` (unfrozen)
- **Output schema candidate:** `aae.r0.scope_proposal.output` / `PRE-1` (unfrozen)
- **Inference profile candidate:** `ip.r0.scope_proposal.pre1` (unfrozen)
- **Legal input classes:** `CURRENT_TURN_ENVELOPE`, `TRANSCRIPT_AVAILABILITY_METADATA`, `HOST_SCOPE_POLICY`
- **Legal authoritative refs:** `TURN_UUID`, `CONVERSATION_UUID`, `TRANSCRIPT_CURSOR`
- **Local key prefixes:** `SCOPE_`
- **Response contract:** One scope proposal outcome plus bounded recent/targeted scope request details when required.
- **Semantic enums:**
  - `proposal_outcome`: `SUFFICIENT_WITHOUT_HISTORY`, `REQUEST_RECENT`, `REQUEST_TARGETED`
- **Empty output:** Empty output is invalid; the proposal must select one explicit outcome.
- **Uncertainty:** Request bounded history rather than infer missing conversational reference meaning.
- **Responsibilities:**
  - Assess only transcript-history sufficiency.
  - Choose the minimum legitimate scope.
  - Preserve unresolved reference need when current text cannot stand alone.
- **Forbidden responsibilities:**
  - Do not query semantic memory.
  - Do not retrieve transcript yourself.
  - Do not perform Intent decomposition, research, tools, persistence, or user response.
- **Host validation candidates:**
  - proposal outcome is legal
  - requested scope stays within host policy bounds
  - all copied current-turn identities match supplied values
  - no authoritative identifier is invented
- **Next legal consumers:** `R0_HOST_SCOPE_VALIDATOR`, `R0_HOST_RETRIEVER`, `R0_CONVERSATION_PACKET_FREEZER`
- **Repair:** allowed=True; max_repairs=None; same packet + exact validation error + fresh context/sampler required
- **Review notes:**
  - R0 numeric retrieval bounds live in host policy/config, not model authority.

### SCOPE_VALIDATION

- **Contract:** `aae.r0.scope_validation` / `PRE-1`
- **Physical adapter:** `CONVERSATION_RESOLVER`
- **Recipe:** `R0`
- **Authority:** `SEMANTIC_ASSESSMENT`
- **Purpose:** Determine whether the exact retrieved transcript evidence is sufficient to resolve the current conversational reference within the allowed retrieval bound.
- **Input origin:** Current raw turn plus the exact frozen transcript slice returned by the host.
- **Input schema candidate:** `aae.r0.scope_validation.input` / `PRE-1` (unfrozen)
- **Output schema candidate:** `aae.r0.scope_validation.output` / `PRE-1` (unfrozen)
- **Inference profile candidate:** `ip.r0.scope_validation.pre1` (unfrozen)
- **Legal input classes:** `CURRENT_RAW_TURN`, `FROZEN_TRANSCRIPT_SLICE`, `HOST_SCOPE_POLICY`
- **Legal authoritative refs:** `TURN_UUID`, `TRANSCRIPT_TURN_UUID`, `TRANSCRIPT_HASH`
- **Local key prefixes:** `SCOPE_`
- **Response contract:** One transcript sufficiency outcome with exact supplied evidence references and any bounded next-scope request.
- **Semantic enums:**
  - `validation_outcome`: `SUFFICIENT`, `NEEDS_MORE_RECENT`, `NEEDS_TARGETED_HISTORY`, `UNRESOLVABLE_WITH_TRANSCRIPT`, `BOUND_EXHAUSTED`
- **Empty output:** Empty output is invalid; validation must preserve an explicit sufficient or unresolved state.
- **Uncertainty:** Use UNRESOLVABLE_WITH_TRANSCRIPT or BOUND_EXHAUSTED when the supplied transcript cannot safely resolve the reference.
- **Responsibilities:**
  - Assess sufficiency only.
  - Identify which supplied transcript item resolves the latent reference when supported.
  - Request another bounded transcript scope when still insufficient.
- **Forbidden responsibilities:**
  - Do not query semantic memory.
  - Do not rewrite transcript text.
  - Do not perform Intent, tools, persistence, or answer the user.
- **Host validation candidates:**
  - validation outcome is legal
  - all cited transcript items were supplied
  - requested expansion stays within host bounds
  - no evidence content is altered
- **Next legal consumers:** `R0_CONVERSATION_PACKET_FREEZER`, `R0_HOST_RETRIEVER`
- **Repair:** allowed=True; max_repairs=None; same packet + exact validation error + fresh context/sampler required

### SPELL_NORMALIZATION

- **Contract:** `aae.r1.spell` / `PRE-1`
- **Physical adapter:** `SPELL`
- **Recipe:** `R1`
- **Authority:** `SEMANTIC_PROPOSAL`
- **Purpose:** Normalize only obvious spelling, punctuation, and capitalization defects while preserving the user's wording and intent.
- **Input origin:** Current raw prompt from the frozen Conversation Packet.
- **Input schema candidate:** `aae.r1.spell.input` / `PRE-1` (unfrozen)
- **Output schema candidate:** `aae.r1.spell.output` / `PRE-1` (unfrozen)
- **Inference profile candidate:** `ip.r1.spell.pre1` (unfrozen)
- **Legal input classes:** `RAW_USER_PROMPT`
- **Legal authoritative refs:** none
- **Local key prefixes:** `EDIT_`
- **Response contract:** raw_prompt, normalized_prompt, spell_edits[], uncertain_corrections[].
- **Semantic enums:** none frozen in this pre-version
- **Empty output:** No edits is valid: normalized_prompt may equal raw_prompt and edit/uncertainty arrays may be empty.
- **Uncertainty:** Place uncertain corrections in the uncertainty structure; do not silently substitute a speculative repair.
- **Responsibilities:**
  - Return a normalized prompt.
  - Return genuine uncertainty about normalization rather than guessing.
  - Preserve wording and style as much as possible.
- **Forbidden responsibilities:**
  - Do not paraphrase.
  - Do not interpret references or inspect history.
  - Do not create requirements, use Context, invoke tools, or answer the user.
- **Host validation candidates:**
  - raw_prompt exactly matches supplied prompt
  - normalized_prompt is bounded text
  - edit provenance refers only to supplied text spans
  - no undeclared fields
- **Next legal consumers:** `R1_HOST_NORMALIZATION_VALIDATOR`, `R1_TERM_MEANING`
- **Repair:** allowed=True; max_repairs=None; same packet + exact validation error + fresh context/sampler required

### TERM_MEANING

- **Contract:** `aae.r1.term_meaning` / `PRE-1`
- **Physical adapter:** `TERM_MEANING`
- **Recipe:** `R1`
- **Authority:** `SEMANTIC_PROPOSAL`
- **Purpose:** Interpret terms and references in the current turn only far enough to make the prompt analyzable. Mark provisional or unresolved meanings instead of inventing them.
- **Input origin:** Raw + normalized prompt, Spell uncertainty, host linguistic/source map, and any explicitly supplied Recipe-0 transcript evidence.
- **Input schema candidate:** `aae.r1.term_meaning.input` / `PRE-1` (unfrozen)
- **Output schema candidate:** `aae.r1.term_meaning.output` / `PRE-1` (unfrozen)
- **Inference profile candidate:** `ip.r1.term_meaning.pre1` (unfrozen)
- **Legal input classes:** `RAW_USER_PROMPT`, `NORMALIZED_PROMPT`, `SPELL_UNCERTAINTY`, `HOST_LINGUISTIC_MAP`, `R0_TRANSCRIPT_EVIDENCE`
- **Legal authoritative refs:** `SOURCE_SPAN`, `TRANSCRIPT_TURN_UUID`
- **Local key prefixes:** `TERM_`, `REF_`
- **Response contract:** Bounded term/reference meaning records, lookup-needed flags, confidence/uncertainty, and exact source references.
- **Semantic enums:**
  - `meaning_status`: `provisional`, `unresolved`
- **Empty output:** No special term records is valid when ordinary surface meaning is sufficient; the contract must still return a valid artifact.
- **Uncertainty:** Meaning remains provisional; unresolved history/project meaning is routed to later Context rather than guessed.
- **Responsibilities:**
  - Identify literal terms, references, aliases, and lookup-worthy terms.
  - Propose provisional meanings and preserve source refs.
  - Mark unresolved meaning when the bounded packet is insufficient.
- **Forbidden responsibilities:**
  - Do not decide historical truth or query SQLite.
  - Do not perform research, create requirements, select tools, persist state, or answer.
- **Host validation candidates:**
  - source refs are present in supplied spans/evidence
  - lookup-needed flags use schema-owned values
  - no unsupported historical facts are introduced as host state
  - no undeclared fields
- **Next legal consumers:** `R1_PROMPT_ANALYST`
- **Repair:** allowed=True; max_repairs=None; same packet + exact validation error + fresh context/sampler required
- **Review notes:**
  - The exact Meaning status vocabulary is still a schema-review item; 'provisional' is explicitly source-backed.

### PROMPT_ANALYSIS

- **Contract:** `aae.r1.prompt_analysis` / `PRE-1`
- **Physical adapter:** `PROMPT_ANALYST`
- **Recipe:** `R1`
- **Authority:** `SEMANTIC_PROPOSAL`
- **Purpose:** Identify the communicative structures actually present in the supplied prompt.
- **Input origin:** Raw + normalized prompt, accepted Meaning artifact, and host source spans.
- **Input schema candidate:** `aae.r1.prompt_analysis.input` / `PRE-1` (unfrozen)
- **Output schema candidate:** `aae.r1.prompt_analysis.output` / `PRE-1` (unfrozen)
- **Inference profile candidate:** `ip.r1.prompt_analysis.pre1` (unfrozen)
- **Legal input classes:** `RAW_USER_PROMPT`, `NORMALIZED_PROMPT`, `MEANING_ARTIFACT`, `HOST_SOURCE_SPANS`
- **Legal authoritative refs:** `SOURCE_SPAN`, `MEANING_LOCAL_REF`
- **Local key prefixes:** `TGT_`, `CLAIM_`, `UNRESOLVED_`
- **Response contract:** TGT and communication breakdown plus interaction_mode, important_claims, unresolved_items, and explicit control_signals.
- **Semantic enums:**
  - `interaction_mode`: `straightforward`, `conversational`, `exploratory`, `playful`, `joking`, `ordering_or_directive`, `excited`, `upset_sad`, `upset_disappointed`, `upset_angry_external`, `upset_angry_at_model`
  - `control_signal`: `AFFIRM_PRIOR`, `CORRECT_PRIOR`, `REJECT_PRIOR`, `UNDO_PRIOR_EFFECT`, `CONTINUE_PRIOR_STATE`, `NONE`, `AMBIGUOUS_TARGET`
- **Empty output:** Individual categories may be empty; the overall analysis artifact may not be omitted.
- **Uncertainty:** Classify ambiguity explicitly and preserve unresolved items; never turn uncertain communication into a fabricated fact.
- **Responsibilities:**
  - Identify topics, goals, tasks, statements, questions, directions, and approvals.
  - Classify interaction mode, claims, unresolved items, and explicit control signals.
  - Preserve request-vs-assertion distinctions and exact source spans.
- **Forbidden responsibilities:**
  - Do not create final Rxxx requirements or decide claim truth.
  - Do not retrieve Context, select/execute tools, persist memory, or answer.
- **Host validation candidates:**
  - all source spans exist in supplied host span map
  - enums are legal
  - request and assertion fields do not silently collapse into each other
  - no undeclared fields
- **Next legal consumers:** `R1_INTENT_ORGANIZER`
- **Repair:** allowed=True; max_repairs=None; same packet + exact validation error + fresh context/sampler required

### INTENT_ORGANIZER

- **Contract:** `aae.r1.intent_organizer` / `PRE-1`
- **Physical adapter:** `INTENT_ORGANIZER`
- **Recipe:** `R1`
- **Authority:** `SEMANTIC_COMPOSITION`
- **Purpose:** Compose the authoritative-intent proposal from accepted Meaning and Prompt Analyst artifacts: what requirements exist, how they depend, what Context is needed, and whether capabilities, memory, or clarification are implicated.
- **Input origin:** Validated Meaning + Prompt Analyst artifacts, current-turn source refs, compact capability availability.
- **Input schema candidate:** `aae.r1.intent_organizer.input` / `PRE-1` (unfrozen)
- **Output schema candidate:** `aae.r1.intent_organizer.output` / `PRE-1` (unfrozen)
- **Inference profile candidate:** `ip.r1.intent_organizer.pre1` (unfrozen)
- **Legal input classes:** `MEANING_ARTIFACT`, `PROMPT_ANALYSIS_ARTIFACT`, `CURRENT_TURN_SOURCE_REFS`, `CAPABILITY_AVAILABILITY`
- **Legal authoritative refs:** `SOURCE_SPAN`, `CAPABILITY_ID`
- **Local key prefixes:** `REQ_`, `GROUP_`, `CTX_NEED_`, `MEM_CAND_`
- **Response contract:** Primary/secondary intent proposal, locally keyed requirements, dependencies/grouping, Context needs, capability candidates, memory candidates, blockers, clarification state, and copied control signals.
- **Semantic enums:** none frozen in this pre-version
- **Empty output:** A valid artifact must explicitly represent the communicated need; authoritative Rxxx allocation is host-only after validation.
- **Uncertainty:** Prefer context_resolution_first when bounded Context may resolve an ambiguity; require user clarification only when the contract cannot safely proceed otherwise.
- **Responsibilities:**
  - Create a minimal requirement proposal using local keys.
  - Preserve literal constraints and dependencies.
  - Identify Context needs, capability candidates, memory candidates, blockers, and clarification need.
- **Forbidden responsibilities:**
  - Do not execute or create tool request packets.
  - Do not query memory, claim tool success, write SQLite, decide terminal Completion, or allocate authoritative Rxxx IDs.
- **Host validation candidates:**
  - every proposed requirement has a unique local key
  - local requirement dependency graph is acyclic
  - capability candidates exist in supplied compact registry when claimed
  - literal constraints/source refs are preserved
  - no authoritative IDs are invented
- **Next legal consumers:** `R1_HOST_INTENT_VALIDATOR`, `R1_HOST_ID_ALLOCATOR`, `R1_HOWARD_INTENT_COMMENT`, `R2_CONTEXT`
- **Repair:** allowed=True; max_repairs=None; same packet + exact validation error + fresh context/sampler required
- **Review notes:**
  - Exact Organizer output schema and clarification vocabulary remain for joint schema review.

### INTENT_COMMENT

- **Contract:** `aae.r1.howard_intent_comment` / `PRE-1`
- **Physical adapter:** `CONVERSATIONAL_HOWARD`
- **Recipe:** `R1`
- **Authority:** `PRESENTATION_ONLY`
- **Purpose:** Express the accepted Intent naturally for optional debugging/UI without changing its semantics.
- **Input origin:** Accepted host-normalized Intent projection only.
- **Input schema candidate:** `aae.r1.howard_intent_comment.input` / `PRE-1` (unfrozen)
- **Output schema candidate:** `aae.r1.howard_intent_comment.output` / `PRE-1` (unfrozen)
- **Inference profile candidate:** `ip.r1.howard_intent_comment.pre1` (unfrozen)
- **Legal input classes:** `ACCEPTED_INTENT_PROJECTION`
- **Legal authoritative refs:** `Rxxx`, `SOURCE_SPAN`
- **Local key prefixes:** none
- **Response contract:** Presentation-only natural-language Intent comment grounded solely in accepted Intent.
- **Semantic enums:** none frozen in this pre-version
- **Empty output:** Empty comment is permitted only if the host elects not to expose the optional presentation; if invoked for output, empty text is invalid.
- **Uncertainty:** Reflect accepted unresolved/blocker state exactly; do not resolve it conversationally.
- **Responsibilities:**
  - Naturalize the already accepted Intent.
- **Forbidden responsibilities:**
  - Do not add requirements, research, facts, memory, tools, blockers, or clarification.
  - Do not alter literal constraints.
- **Host validation candidates:**
  - no new Rxxx/reference is introduced
  - protected literals remain exact
  - comment contains no authority-changing fields
- **Next legal consumers:** `R1_PRESENTATION_SINK`
- **Repair:** allowed=True; max_repairs=None; same packet + exact validation error + fresh context/sampler required

### CONTEXT_EVIDENCE_ASSESSMENT

- **Contract:** `aae.r2.evidence_specialist` / `PRE-1`
- **Physical adapter:** `EVIDENCE_SPECIALIST`
- **Recipe:** `R2`
- **Authority:** `SEMANTIC_ASSESSMENT`
- **Purpose:** Against the selected Context split and current Intent need, judge what the supplied bounded evidence supports.
- **Input origin:** Run/loop/lane identity, needed Intent refs, lane purpose, split definition, candidate evidence + metadata.
- **Input schema candidate:** `aae.r2.evidence_specialist.input` / `PRE-1` (unfrozen)
- **Output schema candidate:** `aae.r2.evidence_specialist.output` / `PRE-1` (unfrozen)
- **Inference profile candidate:** `ip.r2.evidence_specialist.pre1` (unfrozen)
- **Legal input classes:** `CONTEXT_LANE`, `CONTEXT_SPLIT`, `INTENT_NEED_REFS`, `EVIDENCE_CANDIDATES`, `EVIDENCE_METADATA`
- **Legal authoritative refs:** `Rxxx`, `Ixxx`, `Lxxx`, `SPLIT_ID`, `Exxx`
- **Local key prefixes:** `JUDGMENT_`
- **Response contract:** Per-candidate considered/accepted/partial/rejected/conflict/unresolved judgment plus lane semantic_status.
- **Semantic enums:**
  - `semantic_status`: `accepted`, `partial`, `no_match`, `conflict`, `unresolved`
  - `lane_status`: `completed`, `no_candidates`, `failed_validation`
- **Empty output:** A no-match/no-candidates lane is a valid explicit semantic result; silent omission is not.
- **Uncertainty:** Prefer partial/conflict/unresolved/no_match over unsupported certainty.
- **Responsibilities:**
  - Judge every supplied candidate for relevance, support, staleness, conflict, scope, and usefulness.
  - Preserve unresolved uncertainty and explicit conflict.
- **Forbidden responsibilities:**
  - Do not query SQLite, create evidence IDs, write memory, answer the user, change Intent or Split, self-validate, or claim tool success.
- **Host validation candidates:**
  - lane and split IDs are supplied and version-correct
  - all evidence refs were supplied
  - support spans exist in referenced evidence
  - candidate placement is non-contradictory
  - semantic enums are legal
- **Next legal consumers:** `R2_HOST_EVIDENCE_VALIDATOR`, `R2_HOWARD_CONTEXT_LANE`
- **Repair:** allowed=True; max_repairs=None; same packet + exact validation error + fresh context/sampler required

### CONTEXT_LANE_COMMENT

- **Contract:** `aae.r2.howard_context_lane` / `PRE-1`
- **Physical adapter:** `CONVERSATIONAL_HOWARD`
- **Recipe:** `R2`
- **Authority:** `SEMANTIC_COMPOSITION`
- **Purpose:** Determine what Context should be carried forward from one validated Context lane.
- **Input origin:** Relevant original Intent refs plus host-validated accepted/partial/conflict/unresolved evidence and lane purpose.
- **Input schema candidate:** `aae.r2.howard_context_lane.input` / `PRE-1` (unfrozen)
- **Output schema candidate:** `aae.r2.howard_context_lane.output` / `PRE-1` (unfrozen)
- **Inference profile candidate:** `ip.r2.howard_context_lane.pre1` (unfrozen)
- **Legal input classes:** `INTENT_REFS`, `VALIDATED_LANE_EVIDENCE`, `LANE_PURPOSE`
- **Legal authoritative refs:** `Ixxx`, `Rxxx`, `Dxxx`, `Exxx`
- **Local key prefixes:** `CTX_`
- **Response contract:** Locally keyed Context-point proposals carrying text, support_refs, and supported|inference|unresolved mode, plus unresolved items.
- **Semantic enums:**
  - `context_point_mode`: `supported`, `inference`, `unresolved`
- **Empty output:** Zero promoted Context points can be valid when the lane legitimately establishes only no-match/unresolved state; that state must remain explicit.
- **Uncertainty:** Use inference/unresolved modes with support refs; never present inference as direct support.
- **Responsibilities:**
  - Create bounded Context-point proposals with explicit support refs.
  - Use supported, inference, or unresolved mode honestly.
  - Preserve conflict/unresolved state rather than flattening it.
- **Forbidden responsibilities:**
  - Do not retrieve, invent support, change Intent, erase conflicts, execute tools, persist, decide terminal Completion, or answer the user.
- **Host validation candidates:**
  - every support ref was supplied and legal for the lane
  - local Context keys are unique
  - Context-point mode is legal
  - conflicts/unresolved conditions are not silently erased
  - host allocates Cxxx only after acceptance
- **Next legal consumers:** `R2_HOST_CONTEXT_POINT_VALIDATOR`, `R2_HOST_CONTEXT_ID_ALLOCATOR`, `R2_LANE_REPORT_FREEZER`
- **Repair:** allowed=True; max_repairs=None; same packet + exact validation error + fresh context/sampler required

### CONTEXT_FINAL_SYNTHESIS

- **Contract:** `aae.r2.howard_context_final` / `PRE-1`
- **Physical adapter:** `CONVERSATIONAL_HOWARD`
- **Recipe:** `R2`
- **Authority:** `SEMANTIC_COMPOSITION`
- **Purpose:** Given original accepted Intent and all validated Context results, compose only the grounded working state the next recipe should receive.
- **Input origin:** Original bounded Intent, optional narrow direct input, and all completed validated Context loop reports.
- **Input schema candidate:** `aae.r2.howard_context_final.input` / `PRE-1` (unfrozen)
- **Output schema candidate:** `aae.r2.howard_context_final.output` / `PRE-1` (unfrozen)
- **Inference profile candidate:** `ip.r2.howard_context_final.pre1` (unfrozen)
- **Legal input classes:** `ACCEPTED_INTENT`, `NARROW_DIRECT_INPUT`, `CONTEXT_LOOP_REPORTS`
- **Legal authoritative refs:** `Rxxx`, `Ixxx`, `Dxxx`, `Exxx`, `Cxxx`, `LANE_REPORT_ID`
- **Local key prefixes:** `CTX_SUMMARY_`
- **Response contract:** Final grounded Context synthesis preserving relevant facts, constraints, conflicts, unresolved items, source refs, and do-not-assume boundaries.
- **Semantic enums:** none frozen in this pre-version
- **Empty output:** No additional Context facts can be valid for a self-contained turn, but the final Context artifact must still explicitly represent readiness/unresolved state.
- **Uncertainty:** Carry unresolved/conflict state forward exactly; do not choose a winner without supplied authority.
- **Responsibilities:**
  - Preserve current subject/job, resolved references, relevant constraints, conflicts/unresolved, and source refs.
  - Preserve explicit do-not-assume boundaries.
- **Forbidden responsibilities:**
  - Do not rewrite Intent, invent project facts, execute, persist, decide terminal Completion, or answer the user.
- **Host validation candidates:**
  - all referenced Context/Intent/evidence artifacts are accepted and supplied
  - Intent requirements are unchanged
  - conflict/unresolved state is preserved
  - final artifact is structurally ready before Decision handoff
- **Next legal consumers:** `R2_HOST_CONTEXT_FREEZER`, `R3_DECISION`
- **Repair:** allowed=True; max_repairs=None; same packet + exact validation error + fresh context/sampler required
- **Review notes:**
  - The source trace contained a slice-specific 'no lane reports' phrase; this pre-version generalizes it to all completed validated loop reports.

### REQUIREMENT_ASSESSMENT

- **Contract:** `aae.r3.requirement_assessor` / `PRE-1`
- **Physical adapter:** `REQUIREMENT_ASSESSOR`
- **Recipe:** `R3`
- **Authority:** `SEMANTIC_ASSESSMENT`
- **Purpose:** For one immutable requirement, decide whether it is ready for completion or requires work, persistence, or is blocked.
- **Input origin:** One host-owned Rxxx, relevant accepted Context, capability availability.
- **Input schema candidate:** `aae.r3.requirement_assessor.input` / `PRE-1` (unfrozen)
- **Output schema candidate:** `aae.r3.requirement_assessor.output` / `PRE-1` (unfrozen)
- **Inference profile candidate:** `ip.r3.requirement_assessor.pre1` (unfrozen)
- **Legal input classes:** `IMMUTABLE_REQUIREMENT`, `RELEVANT_ACCEPTED_CONTEXT`, `CAPABILITY_AVAILABILITY`, `DECISION_TRIGGER`
- **Legal authoritative refs:** `Rxxx`, `Cxxx`, `CAPABILITY_ID`, `PRIOR_WORK_REF`
- **Local key prefixes:** `ASSESS_`, `WORK_NEED_`
- **Response contract:** Per-requirement disposition, basis refs, need summary, work needs/evidence targets, blocker data, post-work obligations, and confidence.
- **Semantic enums:**
  - `disposition`: `READY`, `WORK_REQUIRED`, `BLOCKED`, `PERSISTENCE_REQUIRED`
  - `block_reason`: `USER_INFORMATION_NEEDED`, `MISSING_CONTEXT`, `CAPABILITY_UNAVAILABLE`, `INVALID_UPSTREAM_STATE`
- **Empty output:** Empty output is invalid; every in-scope requirement receives one explicit Decision disposition.
- **Uncertainty:** Use BLOCKED/MISSING_CONTEXT only when a legitimate path cannot be formed; minor uncertainty alone is not automatically a blocker.
- **Responsibilities:**
  - Choose exactly one READY, WORK_REQUIRED, BLOCKED, or PERSISTENCE_REQUIRED disposition.
  - Explain only the semantic reason and any needed work/evidence target.
- **Forbidden responsibilities:**
  - Do not execute or emit tool request syntax.
  - Do not write SQLite, mutate Rxxx, make the cross-requirement graph, or assign terminal Completion status.
- **Host validation candidates:**
  - requirement ID exactly matches the one supplied
  - basis refs exist and are in scope
  - disposition and block reason are legal
  - WORK_REQUIRED has at least one work need
  - READY has no required work need
  - BLOCKED includes block reason
  - PERSISTENCE_REQUIRED does not request SQLite execution
- **Next legal consumers:** `R3_HOST_ASSESSMENT_VALIDATOR`, `R3_PLAN_COMPOSER`
- **Repair:** allowed=True; max_repairs=2; same packet + exact validation error + fresh context/sampler required

### PLAN_COMPOSITION

- **Contract:** `aae.r3.plan_composer` / `PRE-1`
- **Physical adapter:** `PLAN_COMPOSER`
- **Recipe:** `R3`
- **Authority:** `SEMANTIC_COMPOSITION`
- **Purpose:** Compose the smallest legitimate shared work graph from all validated requirement assessments.
- **Input origin:** Validated per-R assessments, capability registry, scope, and any prior accepted work.
- **Input schema candidate:** `aae.r3.plan_composer.input` / `PRE-1` (unfrozen)
- **Output schema candidate:** `aae.r3.plan_composer.output` / `PRE-1` (unfrozen)
- **Inference profile candidate:** `ip.r3.plan_composer.pre1` (unfrozen)
- **Legal input classes:** `VALIDATED_REQUIREMENT_ASSESSMENTS`, `CAPABILITY_REGISTRY_PROJECTION`, `DECISION_SCOPE`, `PRIOR_ACCEPTED_WORK`
- **Legal authoritative refs:** `Rxxx`, `Axxx`, `Cxxx`, `Wxxx`, `CAPABILITY_ID`
- **Local key prefixes:** `WORK_`, `EDGE_`, `PERSIST_`
- **Response contract:** Minimal shared work graph proposal with locally keyed new work, requirement links, dependencies, capability targets, evidence targets, and preserved non-work obligations.
- **Semantic enums:** none frozen in this pre-version
- **Empty output:** Zero new work is valid when assessments establish that no executable work is legitimate; READY/BLOCKED/PERSISTENCE_REQUIRED states must still be preserved.
- **Uncertainty:** Do not create speculative work merely to eliminate a blocker; preserve blocked state when prerequisites are missing.
- **Responsibilities:**
  - Merge only genuinely shared work.
  - Produce local work keys for new work.
  - Preserve blocked, ready, and persistence obligations.
- **Forbidden responsibilities:**
  - Do not execute capabilities, fabricate receipts, perform Persistence, allocate authoritative Wxxx IDs, or decide terminal Completion.
- **Host validation candidates:**
  - every referenced assessment/requirement exists
  - local work keys are unique
  - graph is acyclic and dependencies are legal
  - capability targets exist in supplied registry
  - shared work merges only compatible goals/evidence targets
  - blocked requirements receive no illegitimate executable work
- **Next legal consumers:** `R3_HOST_GRAPH_VALIDATOR`, `R3_HOST_W_ID_ALLOCATOR`, `R4_EXECUTION_HOST`, `R6_PERSISTENCE`
- **Repair:** allowed=True; max_repairs=2; same packet + exact validation error + fresh context/sampler required
- **Review notes:**
  - Exact work-type/work-origin enum sets are intentionally deferred to the schema pass rather than partially copied here.

### EVIDENCE_RECONCILIATION

- **Contract:** `aae.r5.evidence_reconciler` / `PRE-1`
- **Physical adapter:** `EVIDENCE_RECONCILER`
- **Recipe:** `R5`
- **Authority:** `SEMANTIC_ASSESSMENT`
- **Purpose:** Determine what the exact returned evidence for one Wxxx establishes against its original evidence target.
- **Input origin:** One Wxxx, its requirement refs/evidence target, immutable receipt/result refs, and relevant active Context.
- **Input schema candidate:** `aae.r5.evidence_reconciler.input` / `PRE-1` (unfrozen)
- **Output schema candidate:** `aae.r5.evidence_reconciler.output` / `PRE-1` (unfrozen)
- **Inference profile candidate:** `ip.r5.evidence_reconciler.pre1` (unfrozen)
- **Legal input classes:** `WORK_ITEM`, `EVIDENCE_TARGET`, `REQUIREMENT_REFS`, `IMMUTABLE_EXECUTION_RECEIPTS`, `RESULT_ITEMS`, `RELEVANT_ACTIVE_CONTEXT`, `HOST_SIGNAL_PACK`
- **Legal authoritative refs:** `Wxxx`, `Rxxx`, `RECxxx`, `RESULT_REF`, `Cxxx`
- **Local key prefixes:** `EF_`, `DISCOVERY_`, `CTX_IMPACT_`
- **Response contract:** Evidence Finding proposal containing semantic_state, established claims/support refs, not-established targets, conflicts, material discoveries, Context impacts, and immutable execution basis.
- **Semantic enums:**
  - `semantic_state`: `ESTABLISHED`, `PARTIAL`, `NOT_ESTABLISHED`, `CONFLICT`
  - `confidence_label`: `HIGH`, `MEDIUM`, `LOW`
  - `provenance_class`: `DIRECT_HOST_RECEIPT`, `DIRECT_SOURCE_EVIDENCE`, `MULTI_SOURCE_SUPPORT`, `INFERENCE_FROM_EVIDENCE`, `UNRESOLVED`
- **Empty output:** No established claim is valid when the target is NOT_ESTABLISHED; an explicit semantic_state and gap basis are still required.
- **Uncertainty:** Preserve partial evidence, conflict, and missing evidence; no support ref means no promotable claim.
- **Responsibilities:**
  - Choose ESTABLISHED, PARTIAL, NOT_ESTABLISHED, or CONFLICT.
  - Identify established claims with exact support, gaps/conflicts, material discoveries, Context-impact candidates, and execution basis.
- **Forbidden responsibilities:**
  - Do not create Rxxx, write SQLite, promote Context, assign terminal Completion, request tools, edit receipts, or invent operation outcomes.
- **Host validation candidates:**
  - work/requirement/receipt/result refs are supplied and legal
  - semantic_state is legal
  - every established claim has support refs
  - conflict refs exist
  - discovery candidates carry source refs
  - no operation is claimed without immutable receipt basis
- **Next legal consumers:** `R5_HOST_EF_VALIDATOR`, `R5_HOST_EF_ALLOCATOR`, `R5_RECONCILIATION_COMPOSER`
- **Repair:** allowed=True; max_repairs=1; same packet + exact validation error + fresh context/sampler required

### RECONCILIATION_COMPOSITION

- **Contract:** `aae.r5.reconciliation_composer` / `PRE-1`
- **Physical adapter:** `RECONCILIATION_COMPOSER`
- **Recipe:** `R5`
- **Authority:** `SEMANTIC_COMPOSITION`
- **Purpose:** Determine cross-work consequences of validated evidence findings without deciding terminal requirement status.
- **Input origin:** Validated Evidence Findings, active Context, immutable requirement scope, and prior Reconciliation state.
- **Input schema candidate:** `aae.r5.reconciliation_composer.input` / `PRE-1` (unfrozen)
- **Output schema candidate:** `aae.r5.reconciliation_composer.output` / `PRE-1` (unfrozen)
- **Inference profile candidate:** `ip.r5.reconciliation_composer.pre1` (unfrozen)
- **Legal input classes:** `VALIDATED_EVIDENCE_FINDINGS`, `ACTIVE_CONTEXT`, `IMMUTABLE_REQUIREMENT_SCOPE`, `PRIOR_RECONCILIATION_STATE`
- **Legal authoritative refs:** `EFxxx`, `Rxxx`, `Wxxx`, `Cxxx`, `RECxxx`, `DNxxx`, `REPAIR_REQUEST_REF`
- **Local key prefixes:** `DN_`, `CTX_IMPACT_`, `REPAIR_`, `PERSIST_CAND_`
- **Response contract:** Cross-work Reconciliation proposal with nonterminal posture flags, remaining gaps/conflicts, Context impacts, Derived Needs, repairs, persistence relevance, and next-transition recommendations.
- **Semantic enums:**
  - `posture_flag`: `NO_GAP_IDENTIFIED`, `EVIDENCE_GAP_REMAINS`, `CONFLICT_PRESENT`, `CONTEXT_REENTRY_REQUIRED`, `DISCOVERY_FOLLOWUP_REQUIRED`, `REPAIR_REQUIRED`, `PERSISTENCE_RELEVANT`
- **Empty output:** No further action is a valid explicit outcome when NO_GAP_IDENTIFIED is supported; silent omission of in-scope requirements is invalid.
- **Uncertainty:** Keep conflict/gap states nonterminal and route bounded re-entry/repair only when supported.
- **Responsibilities:**
  - Combine findings and preserve remaining gaps/conflicts.
  - Distinguish material discovery from repair.
  - Propose Context impact, Derived Need, repair, Persistence relevance, and legal next transition.
- **Forbidden responsibilities:**
  - Do not assign terminal SATISFIED/PARTIALLY_SATISFIED/BLOCKED/FAILED.
  - Do not execute tools, write DB state, directly promote Context lanes, rewrite Intent, or mutate receipts.
- **Host validation candidates:**
  - all EF/requirement/context refs are supplied
  - posture flags are legal and nonterminal
  - Derived Need/repair/Context-impact local keys are unique
  - every proposed transition is host-legal
  - discovery is not mislabeled as repair
- **Next legal consumers:** `R5_HOST_TRANSITION_VALIDATOR`, `R2_CONTEXT_REENTRY`, `R3_DECISION_REENTRY`, `R6_PERSISTENCE`, `R7_COMPLETION`
- **Repair:** allowed=True; max_repairs=2; same packet + exact validation error + fresh context/sampler required

### PERSISTENCE_ASSESSMENT

- **Contract:** `aae.r6.persistence_assessor` / `PRE-1`
- **Physical adapter:** `PERSISTENCE_ASSESSOR`
- **Recipe:** `R6`
- **Authority:** `SEMANTIC_ASSESSMENT`
- **Purpose:** For one persistence obligation/candidate, determine the durable semantic consequence justified by the supplied frozen memory snapshot and provenance.
- **Input origin:** One persistence item, authority class, provenance, relevant Context/Evidence Finding refs, bounded semantic-memory snapshot, and policy.
- **Input schema candidate:** `aae.r6.persistence_assessor.input` / `PRE-1` (unfrozen)
- **Output schema candidate:** `aae.r6.persistence_assessor.output` / `PRE-1` (unfrozen)
- **Inference profile candidate:** `ip.r6.persistence_assessor.pre1` (unfrozen)
- **Legal input classes:** `PERSISTENCE_ITEM`, `ITEM_AUTHORITY_CLASS`, `PROVENANCE`, `RELEVANT_CONTEXT`, `RELEVANT_EVIDENCE_FINDINGS`, `FROZEN_MEMORY_SNAPSHOT`, `PERSISTENCE_POLICY`
- **Legal authoritative refs:** `Rxxx`, `Cxxx`, `EFxxx`, `ITEM_UUID`, `MEMORY_ENTITY_UUID`, `MEMORY_CLAIM_UUID`, `MEMORY_SNAPSHOT_UUID`
- **Local key prefixes:** `PA_`, `NEW_ENTITY_`, `CLAIM_PROPOSAL_`
- **Response contract:** Per-item durability judgment, entity resolution, semantic claim proposals, existing-claim relation, alias implications, recommended result, reason codes, and provenance refs.
- **Semantic enums:**
  - `item_authority_class`: `NORMATIVE`, `ADVISORY`
  - `durability_judgment`: `DURABLE`, `NOT_DURABLE`, `POLICY_BLOCKED`, `INSUFFICIENT`
  - `entity_resolution`: `MATCH_EXISTING`, `CREATE_NEW`, `IDENTITY_AMBIGUOUS`, `NEEDS_MORE_MEMORY`
  - `semantic_relation`: `SAME`, `CHANGE`, `CORRECTION`, `REFINEMENT`, `CONFLICT`, `RETRACTION`, `UNRELATED`
- **Empty output:** Every supplied persistence item requires an explicit assessment; no silent drop is legal.
- **Uncertainty:** Use IDENTITY_AMBIGUOUS/NEEDS_MORE_MEMORY/INSUFFICIENT rather than creating duplicate entities or guessing identity.
- **Responsibilities:**
  - Judge durability and resolve entity identity.
  - Propose semantic claims/relations and preserve change-vs-correction semantics.
  - Recommend one item result while preserving ambiguity when identity is unresolved.
- **Forbidden responsibilities:**
  - Do not allocate permanent semantic UUIDs, execute SQL, mutate transcript/Rxxx, assign Completion, or perform unrelated memory lookup.
- **Host validation candidates:**
  - item UUID/authority/provenance match supplied item
  - memory snapshot identity/base commit are preserved
  - all referenced memory entities/claims were supplied
  - semantic enums are legal
  - new records use local refs only
  - no executable SQL appears
- **Next legal consumers:** `R6_HOST_PA_VALIDATOR`, `R6_PERSISTENCE_COMPOSER`
- **Repair:** allowed=True; max_repairs=2; same packet + exact validation error + fresh context/sampler required

### PERSISTENCE_COMPOSITION

- **Contract:** `aae.r6.persistence_composer` / `PRE-1`
- **Physical adapter:** `PERSISTENCE_COMPOSER`
- **Recipe:** `R6`
- **Authority:** `SEMANTIC_COMPOSITION`
- **Purpose:** Compose the smallest coherent atomic semantic mutation plan from all validated Persistence assessments.
- **Input origin:** Validated Persistence Assessments, normative/advisory item lists, frozen memory base, and semantic policy.
- **Input schema candidate:** `aae.r6.persistence_composer.input` / `PRE-1` (unfrozen)
- **Output schema candidate:** `aae.r6.persistence_composer.output` / `PRE-1` (unfrozen)
- **Inference profile candidate:** `ip.r6.persistence_composer.pre1` (unfrozen)
- **Legal input classes:** `VALIDATED_PERSISTENCE_ASSESSMENTS`, `NORMATIVE_OBLIGATIONS`, `ADVISORY_CANDIDATES`, `FROZEN_MEMORY_BASE`, `SEMANTIC_POLICY`
- **Legal authoritative refs:** `PAxxx`, `ITEM_UUID`, `Rxxx`, `MEMORY_ENTITY_UUID`, `MEMORY_CLAIM_UUID`, `MEMORY_ALIAS_UUID`, `MEMORY_CONFLICT_UUID`
- **Local key prefixes:** `PP_`, `NEW_E`, `NEW_CLAIM_`, `NEW_ALIAS_`, `NEW_CONFLICT_`
- **Response contract:** Atomic semantic mutation plan with complete item_results, local new-entity refs, claim/alias/conflict/entity-merge mutations, transaction properties, provenance links, and diagnostics.
- **Semantic enums:**
  - `mutation_operation`: `CREATE_ENTITY`, `CREATE_CLAIM`, `SUPERSEDE_CLAIM`, `RETRACT_CLAIM`, `SET_CLAIM_CONTESTED`, `ADD_ALIAS`, `SET_ALIAS_STATUS`, `CREATE_CONFLICT`, `RESOLVE_CONFLICT`, `MERGE_ENTITY`, `NO_CHANGE`
  - `advisory_disposition`: `SAVED`, `IGNORED`, `DEFERRED`
- **Empty output:** A no-change transaction can be valid, but every normative/advisory item must still receive explicit coverage/disposition.
- **Uncertainty:** Preserve ambiguous identity/conflict states; never force a merge or create a duplicate merely to complete the plan.
- **Responsibilities:**
  - Cover every normative obligation exactly once and explicitly disposition every advisory candidate.
  - Combine duplicate semantic consequences where legitimate.
  - Propose allowed semantic mutation operations with local temporary refs and transaction properties.
- **Forbidden responsibilities:**
  - Do not execute SQL, allocate permanent UUIDs, mutate upstream artifacts, or assign Completion status.
- **Host validation candidates:**
  - every normative obligation appears exactly once
  - every advisory candidate receives explicit disposition
  - all PA/memory refs exist
  - local refs are unique and acyclic
  - mutation operations are legal
  - expected memory base commit is preserved
  - no executable SQL appears
- **Next legal consumers:** `R6_HOST_PLAN_VALIDATOR`, `R6_HOST_UUID_ALLOCATOR`, `R6_ATOMIC_TRANSACTION_HOST`, `R7_COMPLETION`
- **Repair:** allowed=True; max_repairs=2; same packet + exact validation error + fresh context/sampler required

### COMPLETION_ASSESSMENT

- **Contract:** `aae.r7.completion_assessor` / `PRE-1`
- **Physical adapter:** `COMPLETION_ASSESSOR`
- **Recipe:** `R7`
- **Authority:** `SEMANTIC_ASSESSMENT`
- **Purpose:** For one immutable Rxxx, determine its terminal standing from the authoritative closure bundle.
- **Input origin:** One requirement plus its accepted Intent/Context/Decision/Execution/Reconciliation/Persistence outcome chain.
- **Input schema candidate:** `aae.r7.completion_assessor.input` / `PRE-1` (unfrozen)
- **Output schema candidate:** `aae.r7.completion_assessor.output` / `PRE-1` (unfrozen)
- **Inference profile candidate:** `ip.r7.completion_assessor.pre1` (unfrozen)
- **Legal input classes:** `REQUIREMENT_CLOSURE_BUNDLE`, `ALLOWED_TERMINAL_STATUSES`, `COMPLETION_POLICY_SNAPSHOT`
- **Legal authoritative refs:** `Rxxx`, `Cxxx`, `Wxxx`, `RECxxx`, `EFxxx`, `PRC_REF`, `DNxxx`, `RRQ_REF`
- **Local key prefixes:** `CA_`
- **Response contract:** Per-R terminal_status plus fulfilled/unmet components, blockers, failures, conflicts, persistence_effect, user-facing refs, result guidance, reason codes, and provenance.
- **Semantic enums:**
  - `terminal_status`: `SATISFIED`, `PARTIALLY_SATISFIED`, `BLOCKED`, `FAILED`
  - `persistence_effect`: `REQUIRED_AND_COMMITTED`, `REQUIRED_ALREADY_SATISFIED`, `REQUIRED_BLOCKED`, `REQUIRED_FAILED`, `NOT_REQUIRED`
- **Empty output:** Empty output is invalid; every immutable in-scope Rxxx receives one terminal standing.
- **Uncertainty:** Preserve blockers/failures/gaps exactly; PARTIALLY_SATISFIED requires genuine fulfilled material and a material remaining gap.
- **Responsibilities:**
  - Choose exactly one SATISFIED, PARTIALLY_SATISFIED, BLOCKED, or FAILED status.
  - Ground fulfilled/unmet components, blockers, failures, and user-facing guidance in supplied refs.
- **Forbidden responsibilities:**
  - Do not create new work, reopen recipes, execute tools, persist, invent facts, or write final user prose.
- **Host validation candidates:**
  - Rxxx exactly matches supplied closure bundle
  - terminal status is legal
  - all support/blocker/failure refs are reachable from closure bundle
  - status consistency gates pass
  - no new work/tool/SQLite/re-entry appears
  - no final-response prose field appears
- **Next legal consumers:** `R7_HOST_CA_VALIDATOR`, `R7_HOST_CA_ALLOCATOR`, `R7_COMPLETION_COMPOSER`
- **Repair:** allowed=True; max_repairs=2; same packet + exact validation error + fresh context/sampler required

### COMPLETION_COMPOSITION

- **Contract:** `aae.r7.completion_composer` / `PRE-1`
- **Physical adapter:** `COMPLETION_COMPOSER`
- **Recipe:** `R7`
- **Authority:** `SEMANTIC_COMPOSITION`
- **Purpose:** Compose the turn-level Final Standing proposal from already validated per-requirement Completion Assessments.
- **Input origin:** All accepted Completion Assessments and the immutable requirement list.
- **Input schema candidate:** `aae.r7.completion_composer.input` / `PRE-1` (unfrozen)
- **Output schema candidate:** `aae.r7.completion_composer.output` / `PRE-1` (unfrozen)
- **Inference profile candidate:** `ip.r7.completion_composer.pre1` (unfrozen)
- **Legal input classes:** `VALIDATED_COMPLETION_ASSESSMENTS`, `IMMUTABLE_REQUIREMENT_LIST`, `CROSS_REQUIREMENT_RELATIONSHIPS`, `HOST_COVERAGE_SIGNALS`, `COMPLETION_POLICY_SNAPSHOT`
- **Legal authoritative refs:** `Rxxx`, `CAxxx`, `FACT_REF`, `BLOCKER_REF`, `FAILURE_REF`
- **Local key prefixes:** `CP_`
- **Response contract:** Turn-level completion plan preserving every per-R standing exactly once, with overall posture, ordered result focus, shared facts/blockers/failures, disclosure seed, and diagnostics.
- **Semantic enums:**
  - `overall_turn_posture`: `ALL_SATISFIED`, `MIXED`, `BLOCKED`, `FAILED`
- **Empty output:** Empty output is invalid when any Rxxx exists; every immutable requirement must be covered exactly once.
- **Uncertainty:** Organization may expose mixed/blocker/failure posture but may not upgrade or downgrade a per-R status.
- **Responsibilities:**
  - Preserve each terminal status exactly.
  - Establish overall posture, result focus, required disclosures, and shared user-facing facts/blockers/failures.
- **Forbidden responsibilities:**
  - Do not re-decide Completion Assessment statuses, drop requirements, invent facts, execute, persist, or write user-facing final prose.
- **Host validation candidates:**
  - every Rxxx is covered exactly once
  - every CA ref exists
  - every per-R terminal status exactly matches source CA
  - overall posture is legal
  - result refs originate in source CA artifacts
  - no final prose/tool/SQL/Persistence mutation appears
- **Next legal consumers:** `R7_HOST_COMPLETION_VALIDATOR`, `R7_FINAL_STANDING_PACKET_FREEZER`, `R8_RESULT`
- **Repair:** allowed=True; max_repairs=2; same packet + exact validation error + fresh context/sampler required

### RESULT_REQUIREMENT_COMMENT

- **Contract:** `aae.r8.howard_result_comment` / `PRE-1`
- **Physical adapter:** `CONVERSATIONAL_HOWARD`
- **Recipe:** `R8`
- **Authority:** `PRESENTATION_ONLY`
- **Purpose:** Naturalize one frozen requirement standing without changing its status or facts.
- **Input origin:** One result-comment packet projected from the Final Standing Packet.
- **Input schema candidate:** `aae.r8.howard_result_comment.input` / `PRE-1` (unfrozen)
- **Output schema candidate:** `aae.r8.howard_result_comment.output` / `PRE-1` (unfrozen)
- **Inference profile candidate:** `ip.r8.howard_result_comment.pre1` (unfrozen)
- **Legal input classes:** `RESULT_COMMENT_PACKET`, `DISCLOSURE_RULES`, `LITERAL_LOCK`
- **Legal authoritative refs:** `Rxxx`, `FSP_REF`, `FACT_REF`, `BLOCKER_REF`, `FAILURE_REF`
- **Local key prefixes:** `RCM_`
- **Response contract:** One bounded natural-language requirement comment that preserves the frozen terminal standing and authorized disclosures.
- **Semantic enums:**
  - `terminal_status`: `SATISFIED`, `PARTIALLY_SATISFIED`, `BLOCKED`, `FAILED`
- **Empty output:** If the host invokes this mode for a required comment, empty output is invalid.
- **Uncertainty:** Use only the frozen standing/facts; do not soften an unresolved blocker/failure into certainty.
- **Responsibilities:**
  - State the frozen standing using only supplied allowed facts and disclosures.
- **Forbidden responsibilities:**
  - Do not mutate status, add facts, perform tools/persistence, expose internal implementation details, or override Literal Lock.
- **Host validation candidates:**
  - standing language is consistent with frozen status
  - required disclosures are present
  - must-not-claim rules pass
  - protected literals are exact
  - no new authoritative facts/refs appear
- **Next legal consumers:** `R8_HOST_RESULT_COMMENT_VALIDATOR`, `R8_HOWARD_RESULT_FINAL`
- **Repair:** allowed=True; max_repairs=None; same packet + exact validation error + fresh context/sampler required

### RESULT_FINAL_COMPOSE

- **Contract:** `aae.r8.howard_result_final` / `PRE-1`
- **Physical adapter:** `CONVERSATIONAL_HOWARD`
- **Recipe:** `R8`
- **Authority:** `PRESENTATION_ONLY`
- **Purpose:** Compose the final user-facing response from frozen standings while obeying all required disclosures and literal locks.
- **Input origin:** Final Standing Packet projections, validated result comments, disclosure map, Literal Lock, response budget, and style/publication constraints.
- **Input schema candidate:** `aae.r8.howard_result_final.input` / `PRE-1` (unfrozen)
- **Output schema candidate:** `aae.r8.howard_result_final.output` / `PRE-1` (unfrozen)
- **Inference profile candidate:** `ip.r8.howard_result_final.pre1` (unfrozen)
- **Legal input classes:** `RAW_USER_PROMPT`, `RESOLVED_REQUEST_PRESENTATION`, `FINAL_STANDING_PROJECTION`, `VALIDATED_RESULT_COMMENTS`, `DISCLOSURE_MAP`, `LITERAL_LOCK`, `RESPONSE_BUDGET`, `STYLE_POLICY`, `PUBLICATION_CONSTRAINTS`
- **Legal authoritative refs:** `FSP_REF`, `RESULT_COMMENT_REF`, `FACT_REF`, `BLOCKER_REF`, `FAILURE_REF`
- **Local key prefixes:** none
- **Response contract:** final_response_text only; host wraps validated text into the Result artifact and publication receipt.
- **Semantic enums:** none frozen in this pre-version
- **Empty output:** Empty final_response_text is invalid for a publishable turn unless a separate deterministic host policy explicitly owns the response.
- **Uncertainty:** Communicate frozen uncertainty/blockers/failures faithfully; presentation cannot create certainty absent from Completion.
- **Responsibilities:**
  - Produce only final prose consistent with frozen statuses/facts.
  - Honor mandatory disclosures and protected literal constraints.
- **Forbidden responsibilities:**
  - Do not alter statuses, invent facts, hide required disclosures, change locked literal text, claim unperformed tools/persistence, or expose internal pipeline state.
- **Host validation candidates:**
  - UTF-8/size gate passes
  - forbidden internal-ID scan passes
  - Literal Lock passes
  - MUST_MENTION coverage passes
  - must-not-claim rules pass
  - terminal-standing language remains consistent
  - response budget passes
- **Next legal consumers:** `R8_HOST_FINAL_VALIDATOR`, `R8_PUBLICATION_HOST`
- **Repair:** allowed=True; max_repairs=None; same packet + exact validation error + fresh context/sampler required

## Deliberately unresolved before freeze

- Exact JSON schemas are referenced but not yet frozen or dispatchable.
- Field/token/source-excerpt caps remain unset rather than guessed.
- Inference profiles are named candidates only; A2 will freeze full profile identity/hash.
- Minimum trust thresholds remain unset; no pre-version contract can dispatch.
- Some schema-level enum vocabularies intentionally remain deferred where the recipe prose did not freeze a complete set.
- Physical adapter runtime facts (path/hash/handle/residency/lease/memory) are intentionally absent from A1.
