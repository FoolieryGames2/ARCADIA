---
title: "A.R.C.A.D.I.A. v0.1 — Canonical Recipe Contract"
project: "A.R.C.A.D.I.A."
version: "0.1-prototype"
checkpoint_date: "2026-08-29"
document_role: "recipe-contract"
source_path: "recipes/R5_RECONCILIATION_V0_1.md"
source_sha256: "11f0c17d5722f516c66ebcb1115b5b49d618dee0fabeba1109cbe82f22dae2fe"
source_bytes: 73437
source_integrity: "preserved"
tags:
  - "arcadia/v0-1"
  - "type/recipe"
  - "status/frozen"
aliases:
  - "R5_RECONCILIATION_V0_1.md"
  - "A.R.C.A.D.I.A. v0.1 — Canonical Recipe Contract"
---

> [!info] Obsidian navigation
> **Checkpoint role:** `recipe-contract`  
> **Frozen source:** `recipes/R5_RECONCILIATION_V0_1.md` · SHA-256 `11f0c17d5722f516…`  
> **Command center:** [[ARCADIA v0.1 - Command Center]]  
> **Connected:** [[01_ARCADIA_V0_1_FULL_PROJECT_CHECKPOINT]] · [[03_ARCADIA_V0_1_GLOBAL_CONTRACTS_AND_INVARIANTS]] · [[04_ARCADIA_V0_1_AAE_CONTRACT_REGISTRY_AND_SERIALIZATION]] · [[R4_TOOL_EXECUTION_V0_1]] · [[R6_PERSISTENCE_V0_1]] · [[07_ARCADIA_V0_1_SOURCE_POLICY_REGISTRY]] · [[ARCADIA_ST08_SOURCE_QUALITY_POLICY_LOCK_2026-08-29]] · [[ARCADIA_V0_1_FULL_PIPELINE_AAE_REFERENCE_5_SLICES]]

<!-- OBSIDIAN_LAYER_END — ORIGINAL SOURCE CONTENT BEGINS BELOW -->

# A.R.C.A.D.I.A. v0.1 — Canonical Recipe Contract

**v0.1 integration status:** The detailed semantic recipe body below is carried forward from the final pre-v0.1 trust/recovery specification because R3 intentionally did not change semantic recipe ownership. It is now governed by the v0.1 common runtime/AAE/source/recovery/trace/performance contracts in this bundle.

**Conflict rule:** if this carried-forward body contains older wording about adapter loading, generic adapter runtime, source-quality being unresolved, trace retention, crash replay, global sampling, handwritten AAE framing, or model-call necessity, the v0.1 system documents `01`–`09` supersede that wording. Semantic recipe responsibilities, artifacts, edge cases, and tests remain authoritative unless explicitly superseded.

---

# A.R.C.A.D.I.A. RECONCILIATION RECIPE
## Prototype Build Specification — Command-Window Reference
**Status:** LOCKED PROTOTYPE DESIGN  
**Scope:** RECONCILIATION ONLY  
**Date:** 2026-08-28  
**Parent:** `ARCADIA_TOOL_EXECUTION_PROTOTYPE_BUILD_SPEC_2026-08-28.md`  
**Upstream Contracts:** `HOWARD_INTENT_RECIPE_PROTOTYPE_BUILD_SPEC_2026-08-28.md`, `HOWARD_CONTEXT_RECIPE_PROTOTYPE_BUILD_SPEC_2026-08-28.md`, `ARCADIA_DECISION_RECIPE_PROTOTYPE_BUILD_SPEC_2026-08-28.md`  
**Next Stage:** Persistence Recipe  
**Purpose:** Archive-ready source-of-truth specification for implementing and independently testing A.R.C.A.D.I.A.'s Reconciliation recipe. Reconciliation receives immutable Execution receipts plus the work/evidence targets that caused those operations, determines what the returned work actually established, preserves conflict and provenance, creates validated discovery or repair artifacts when justified, and routes newly discovered terms or state back through Context without rewriting original Intent.

---

> **CONFIRMED LOGIC INTEGRATION — R2 — 2026-08-28**  
> This R2 document integrates the confirmed trust/recovery logic locked after the AAE five-slice review: single-source AAE/runtime/training contracts, base-model baselining, full trace capture with a training-data firewall, packet-projection testing, aggregate loop telemetry, durable-provisional semantic Persistence with next-turn review, controlled user memory correction, deterministic-first semantic support, and mode-specific Howard evaluation.  
> **Source-quality / source-authority ranking is intentionally NOT defined by this update. It remains a separate required design lane.**


# 0. CORE RULE

Reconciliation answers one question:

> **What did the work that actually occurred establish relative to the work that was requested?**

Decision defines what evidence or state was needed.

Execution establishes what operations actually happened and returns immutable host receipts.

Reconciliation compares those two realities.

Canonical chain:

```text
R001
  |
  v
W001
  |
  v
TRQ001
  |
  v
REC001
  |
  v
RECONCILIATION
  |
  +--> established finding
  +--> partial / missing evidence
  +--> conflict
  +--> Context impact proposal
  +--> DN001 discovery
  +--> repair request
  +--> persistence relevance
```

Reconciliation does **not** rewrite the user's request.

Reconciliation does **not** claim that unreceived work occurred.

Reconciliation does **not** write SQLite.

Reconciliation does **not** mark `Rxxx` requirements terminally satisfied.

---

# 1. POSITION IN THE FULL RECIPE SPINE

```text
INTENT
  What did the user communicate?
       |
       v
CONTEXT
  What grounded state do we have?
       |
       v
DECISION
  What work actually needs to happen?
       |
       v
TOOL / EXECUTION
  What operations actually occurred?
       |
       v
RECONCILIATION
  What did returned work actually establish?
       |
       +--> narrow Context re-entry when needed
       |       |
       |       v
       |    Decision -> Execution -> Reconciliation
       |
       v
PERSISTENCE
  Should validated durable state be committed?
       |
       v
COMPLETION
       |
       v
RESULT
```

Reconciliation is the semantic boundary between:

```text
RAW / NORMALIZED OPERATION RESULTS
```

and:

```text
GROUNDED CONSEQUENCES OF THOSE RESULTS
```

---

# 2. AUTHORITY MODEL

Authority remains compartmentalized.

```text
Intent
  authority for what the user communicated

Context
  authority for active grounded turn state

Decision
  authority for planned work and evidence targets

Execution Host
  authority for whether an operation occurred

Reconciliation
  semantic judge of what returned work established

Persistence Host
  authority for durable SQLite commit

Completion
  authority for terminal requirement status
```

A Reconciliation model may interpret evidence.

It may not manufacture authority belonging to another stage.

---

# 3. RECONCILIATION PROTOTYPE SPECIALISTS — LOCKED

The prototype uses exactly **two new Reconciliation adapters**.

```text
[ADAPTER 1]
EVIDENCE RECONCILER
       |
       v
per-Wxxx semantic findings
       |
       v
CLEAR KV
       |
       v
[ADAPTER 2]
RECONCILIATION COMPOSER
       |
       v
cross-work requirement-linked consequences
```

There is no Reconciliation critic adapter in the prototype.

There is no Reconciliation router adapter.

There is no tool-specific reconciliation adapter.

The existing Howard Context Commentator from the Context recipe may be reused **only after** a Context discovery/re-entry packet has been accepted and promoted into an official Context lane/revision.

That Howard call is not counted as a new Reconciliation adapter.

---

# 4. WHY TWO ADAPTERS

The two learned tasks are materially different.

## Adapter 1 — Evidence Reconciler

Narrow question:

> **For this exact `Wxxx`, given its evidence target and its exact receipts/results, what was actually established?**

It should not reason about the entire turn unless necessary.

## Adapter 2 — Reconciliation Composer

Cross-work question:

> **Taken together, what do the validated per-work findings imply for the affected `Rxxx` requirements, Context, follow-up work, repair path, and persistence relevance?**

Keeping these separate improves:

- training clarity;
- independent testing;
- failure localization;
- adapter switching discipline;
- smaller prompts;
- cleaner provenance;
- less accidental requirement rewriting.

---

# 5. KV / MODEL STATE RULE

Clear model KV/attention state at every adapter boundary.

Adapters may remain loaded/warm.

Hidden inference state is never authoritative turn memory.

```text
EVIDENCE RECONCILER
       |
       | EFxxx structured findings
       v
CLEAR KV
       |
       v
RECONCILIATION COMPOSER
       |
       | RCN handoff
       v
CLEAR KV
```

Every call must be independently reconstructible from host-supplied artifacts.

---

# 6. ID NAMESPACE RULES

Existing namespaces remain authoritative:

```text
R001      Intent requirement
C001      Context point
L001      Context lane
W001      Decision work item
TRQ001    Tool request
REC001    Host tool receipt
DN001     Derived Need / downstream discovery
```

Reconciliation adds recommended namespaces:

```text
RCN001    Reconciliation run
EF001     Evidence Finding
CIP001    Context Impact Proposal
RRQ001    Reconciliation Repair Request
```

Persistence candidate objects may carry host UUIDs rather than claiming Persistence's short-ID namespace; final semantic IDs remain Persistence Host-owned.

Do not reuse:

```text
Txxx      Intent term candidates
Dxxx      Context direct-input objects
RECxxx    host execution receipts
```

---

# 7. RECONCILIATION INPUT CONTRACT

Reconciliation receives a host-built bounded packet.

Minimum conceptual input:

```text
turn_id

intent_basis
  intent_artifact_id
  intent_revision
  intent_hash
  authoritative in-scope Rxxx records

context_basis
  active Context snapshot ID/hash
  active lane revisions relevant to scope
  Context point refs
  known conflicts/unresolved state

Decision_basis
  Decision run/revision/hash
  active Wxxx records
  evidence_target per Wxxx
  success criteria
  work_origin
  dependency refs
  requirement refs

Execution_basis
  Execution run/hash
  exact TRQxxx records
  exact immutable RECxxx records
  result-item refs/payloads
  raw outcome refs where allowed
  normalized provider payloads
  attempt history relevant to Wxxx

reconciliation_scope
  allowed Rxxx
  allowed Wxxx

host_signal_pack
  deterministic comparison signals
  optional
```

The host must not replace these artifacts with one lossy prose summary.

---

# 8. UPSTREAM INTEGRITY GATE

Before semantic reconciliation, the host verifies:

```text
Intent artifact/hash still matches
active Context refs exist
Decision handoff/hash matches
Wxxx exists and is active or historically executable
TRQxxx maps to Wxxx correctly
RECxxx maps to TRQxxx/Wxxx correctly
receipt hash passes
result-item hashes pass where present
requirement refs are legal
scope is legal
```

If upstream integrity fails, semantic adapters do not run on corrupted state.

Record an explicit Reconciliation runtime failure instead.

---

# 9. RECEIPT IMMUTABILITY

`RECxxx` is historical fact about Execution.

Reconciliation may interpret it.

It may not edit it.

Invalid:

```text
REC004.status = FAILED

Reconciliation rewrites:
REC004.status = SUCCESS
```

Valid:

```text
REC004.status = SUCCESS

EF008.semantic_state = NOT_ESTABLISHED
reason = provider ran successfully but returned no evidence meeting W003 target
```

Operation success and semantic success remain separate.

---

# 10. EXECUTION STATUS VS SEMANTIC STATUS

Execution statuses remain those defined by Tool / Execution, such as:

```text
SUCCESS
PARTIAL
NO_RESULT
FAILED
TIMEOUT
REJECTED_BEFORE_EXECUTION
CANCELLED
```

Reconciliation adds semantic work-level states:

```text
ESTABLISHED
PARTIAL
NOT_ESTABLISHED
CONFLICT
```

Example:

```text
REC001.execution_status = SUCCESS
EF001.semantic_state = NOT_ESTABLISHED
```

This is normal.

A tool may work perfectly while the evidence target remains unmet.

---

# 11. DETERMINISTIC-FIRST RECONCILIATION

Do not call an adapter for facts the host can establish mechanically.

Preferred path:

```text
RECxxx
   |
   v
HOST INTEGRITY CHECK
   |
   v
HOST NORMALIZATION / SIGNALS
   |
   +--> mechanically sufficient? -- yes --> deterministic EFxxx
   |
   +--> semantic judgment needed? -- yes --> Evidence Reconciler
```

Example — Save File:

```text
W004 target:
  save exact artifact to authorized path
  verified content hash required

REC008:
  execution_status: SUCCESS
  actual_path: expected path
  verification: PASS
  content_hash: expected hash
```

The host may produce an `ESTABLISHED` mechanical finding without model inference.

No semantic adapter is needed merely to restate verified receipt fields.

---

# 12. WHEN SEMANTIC RECONCILIATION IS REQUIRED

Semantic judgment is normally required for:

```text
Google/Search result relevance
Wiki result relevance
loaded file content meaning
multiple-source corroboration
conflicting evidence
partial evidence
new term/entity/concept importance
whether a new gap is materially necessary for Rxxx
whether a result changes active Context meaning
whether failed/rejected work justifies a planning repair
```

A capability registry or work record may expose a host hint such as:

```text
reconciliation_mode:
  DETERMINISTIC_RECEIPT
  SEMANTIC_EVIDENCE
  MIXED
```

This is routing metadata, not semantic truth.

---

# 13. HOST MODULES — RECONCILIATION FOUNDATION

## Core from the beginning

```text
json
jsonschema
dataclasses
uuid
hashlib
datetime
enum
collections
typing
re
RapidFuzz
```

## Strongly useful

```text
ftfy
spaCy
difflib
unicodedata
```

## Optional development/support

```text
regex
networkx
```

No module in this list has authority to declare semantic truth.

---

# 14. `jsonschema` OWNERSHIP

Use `jsonschema` as a hard structural gate at every model/file boundary.

Validate:

```text
Reconciliation input envelope
Evidence Signal Pack
Evidence Reconciler output
Evidence Finding record
Reconciliation Composer output
Derived Need DNxxx
Context Impact Proposal CIPxxx
Repair Request RRQxxx
Reconciliation handoff
Howard-comment promotion metadata interface
```

`jsonschema` validates structure.

It does not validate truth, relevance, or evidence quality.

---

# 15. `dataclasses` OWNERSHIP

Preferred host-side internal objects include:

```text
ReconciliationRun
ReconciliationScope
WorkEvidenceBundle
EvidenceSignalPack
EvidenceFinding
ConflictRecord
DerivedNeed
ContextImpactProposal
RepairRequest
PersistenceRelevanceCandidate
ReconciliationRequirementState
ReconciliationHandoff
ValidationReport
```

Use typed host objects internally.

Serialize to JSON only at model/log/replay boundaries.

---

# 16. `uuid` OWNERSHIP

Use UUID-backed internal IDs for:

```text
Reconciliation run
semantic adapter call
repair attempt
signal pack
finding artifact
Context impact proposal
repair request
persistence relevance candidate
handoff artifact
```

Readable aliases such as `RCN001`, `EF001`, `CIP001`, and `RRQ001` may coexist with internal UUIDs.

---

# 17. `hashlib` OWNERSHIP

Use hashes for:

```text
upstream artifact integrity
receipt integrity
result-item integrity
normalized comparison payloads
exact duplicate evidence detection
signal-pack integrity
model input/output provenance
Reconciliation handoff hash
replay safety
```

Preserve both:

```text
raw_payload_hash
normalized_comparison_hash
```

when normalization changes text.

Never replace the raw evidence solely with normalized text.

---

# 18. `ftfy` + `unicodedata` NORMALIZATION

Purpose:

```text
repair encoding damage
normalize Unicode for comparison
make equivalent text easier to compare
```

Required rule:

```text
RAW EVIDENCE SURVIVES
       +
NORMALIZED COMPARISON TEXT IS DERIVED
```

The normalized representation is a signal surface.

It is not a replacement source record.

---

# 19. `re` / `regex` OWNERSHIP

Use `re` for cheap structural extraction:

```text
Rxxx/Wxxx/TRQxxx/RECxxx refs
URLs/known identifiers where present
version patterns
simple dates/times
numbers/units
quoted terms
simple contradiction cues
known status tokens
```

Use optional `regex` only for cases where standard `re` is insufficient, such as:

```text
advanced Unicode boundaries
overlapping matches
specialized fuzzy-regex development experiments
```

Regex does not decide meaning.

---

# 20. RAPIDFUZZ OWNERSHIP

Use RapidFuzz for bounded similarity signals.

Good uses:

```text
possible same entity
possible alias
near-duplicate term
source title similarity
project/model/version naming similarity
candidate term deduplication
```

Example host signal:

```text
possible_same_entity:
  left: "Qwen2.5-Coder"
  right: "Qwen 2.5 Coder"
  similarity: 96.4
```

Do not convert that directly into:

```text
same_entity: true
```

unless a deterministic identifier establishes identity.

Semantic identity belongs to the Evidence Reconciler / Context when needed.

---

# 21. SPACY OWNERSHIP

spaCy is a deterministic linguistic signal assistant.

Useful outputs:

```text
named entity candidates
noun chunks
candidate technical terms
lemmas
relation candidates
negation cues
contrast cues
date/time/entity cues
shallow dependency relations
```

Example:

```text
source:
"The method uses QLoRA with NF4 quantization rather than conventional 16-bit LoRA training."

spaCy-assisted signals:
  candidate_terms:
    - QLoRA
    - NF4
    - quantization
    - LoRA training

  relation_candidates:
    - QLoRA -> uses -> NF4 quantization

  contrast_cues:
    - "rather than"
```

spaCy may not decide:

```text
QLoRA is true
QLoRA matters enough for DN001
R001 is satisfied
save QLoRA to SQLite
create a Context lane
```

Those remain semantic/host-governed actions.

---

# 22. `difflib` OWNERSHIP

Use `difflib` mainly for development and human-readable diagnostics.

Useful for:

```text
showing differences between two evidence fragments
showing pre/post model repair output
showing Context revision delta in debug logs
explaining exact text changes during normalization
```

RapidFuzz remains the preferred approximate-match signal generator.

---

# 23. `networkx` — OPTIONAL ONLY

Reconciliation naturally creates provenance graphs:

```text
R001
  -> W002
     -> TRQ003
        -> REC004
           -> DN001
              -> L004 rev2
```

The prototype does not require `networkx` for runtime correctness.

A simple deterministic reference validator is sufficient.

`networkx` may be useful for:

```text
debug visualization
cycle diagnostics in malformed provenance
show all descendants of REC004
show all artifacts serving R001
training/debug graph exports
```

Avoid unnecessary runtime dependency weight unless earned.

---


# R2. DETERMINISTIC-FIRST EVIDENCE PREPARATION — EXPANDED LOCK

Before Evidence Reconciler inference, deterministic code should remove every mechanical burden it can safely own while preserving raw evidence by reference.

Baseline helpers may perform:

```text
URL canonicalization
Unicode/text normalization for comparison
exact duplicate hashing
near-duplicate candidate detection
source-domain identity extraction
timestamp/date extraction
citation/source-span mapping
same-document detection
evidence clustering candidates
structured-field comparison
numeric comparison
date/time comparison
version-token extraction
lexical similarity
entity/alias candidate hints
contradiction-cue candidates
```

Optional embedding similarity may be used only as a candidate/signal surface. It is not semantic authority.

These helpers may say:

```text
same normalized URL
same content hash
numbers differ
likely near duplicate
possible same entity
possible contradiction cue
```

They may not say:

```text
R001 is satisfied
this source is trustworthy enough
this evidence proves the claim
a discovered term must become Context
```

Those remain semantic or host-policy judgments.

**Source-quality / source-authority ranking is intentionally outside this R2 update and remains a separate required design lane.**

---

# 24. EVIDENCE SIGNAL PACK

Before Adapter 1, the host may construct a bounded Evidence Signal Pack.

Recommended conceptual shape:

```text
signal_pack_id
work_id
requirement_ids
receipt_refs
raw_result_refs
normalized_text_refs

exact_duplicate_groups
near_duplicate_candidates
entity_candidates
term_candidates
relation_candidates
negation_cues
contrast_cues
number_date_unit_candidates
possible_alias_pairs
source/provenance metadata
host_execution_state_summary
```

Signals are observations.

They are not conclusions.

The exact raw evidence remains available by reference in the adapter packet.

---

# 25. DUPLICATE EVIDENCE DETECTION

Multiple search results do not automatically equal independent corroboration.

Host behavior:

```text
normalize safely
   |
   v
exact hash comparison
   |
   +--> exact duplicate
   |
   v
bounded similarity comparison
   |
   +--> likely near-duplicate signal
```

Example:

```text
REC001 result 2
REC004 result 1

normalized hashes equal

signal:
  evidence_independence = EXACT_DUPLICATE_CONTENT
```

The Evidence Reconciler can then avoid treating duplicated syndicated text as two independent semantic supports.

---

# 26. EVIDENCE BUNDLING

Adapter 1 should normally receive one coherent work-evidence bundle at a time.

Conceptual packet:

```text
W001
  requirement_ids
  goal
  evidence_target
  success_criteria
  work_origin

active relevant Context refs

TRQ refs for W001
REC refs for W001
exact result refs/payloads
host signal pack
```

Do not send unrelated turn history merely because it exists.

The original requirement text remains available.

---

# 27. ADAPTER 1 — EVIDENCE RECONCILER RESPONSIBILITY

The Evidence Reconciler determines:

```text
what the work actually established
what remains unestablished
whether evidence is partial
whether supplied evidence conflicts internally or with active Context
which exact evidence refs support each finding
whether important new terms/entities/concepts appeared
whether those discoveries are merely incidental or materially necessary
```

It does **not**:

```text
create a new Rxxx
write SQLite
promote Context lanes
mark Rxxx SATISFIED
request a tool directly
claim an operation occurred without RECxxx
```

---

# 28. EVIDENCE FINDING CONTRACT

Recommended `EFxxx` structure:

```text
evidence_finding_id
work_id
requirement_ids
semantic_state

established_claims
  - finding text
    support_refs
    confidence_label
    provenance_class

not_established
  - target/gap
    reason

conflicts
  - conflict description
    left_refs
    right_refs
    conflict_type

material_discovery_candidates
  - term/entity/concept
    source_refs
    why_it_may_matter

Context_impact_candidates
  - affected_context_refs/lanes
    reason

execution_basis
  receipt_refs
  execution_statuses

validation_metadata
```

`EFxxx` is subordinate to its `Wxxx` and ultimately its `Rxxx` requirements.

---

# 29. CONFIDENCE LABELS

Use coarse labels rather than fake numerical epistemic precision.

Recommended:

```text
HIGH
MEDIUM
LOW
```

Confidence is descriptive metadata for model/host downstream use.

It does not override source provenance or authority.

Do not treat `HIGH` as proof.

---

# 30. PROVENANCE CLASSES

Useful semantic provenance classes:

```text
DIRECT_HOST_RECEIPT
DIRECT_SOURCE_EVIDENCE
MULTI_SOURCE_SUPPORT
INFERENCE_FROM_EVIDENCE
UNRESOLVED
```

Every established semantic claim must reference the evidence supporting it.

No source ref means no promotable claim.

---


# R2A. CONDITIONAL SEMANTIC ASSURANCE HOOK — NO NEW ADAPTER

The baseline remains **15 unique adapter contracts**. R2 does not allocate an Evidence Critic or Persistence Critic adapter.

For policy-triggered high-consequence or ambiguous cases, the host may invoke an **orthogonal assurance check** only when an already-loaded, independently validated specialist can perform that check within its existing native contract. The second angle should search for a failure mode rather than simply repeat the same classification.

Preferred pattern:

```text
primary semantic assessment
      |
      v
orthogonal failure-seeking check
      |
      +--> no supported objection -> continue under ordinary host gates
      |
      +--> supported disagreement -> lower authority / preserve uncertainty /
                                    request more evidence or user review
```

Agreement never proves truth. Disagreement is the useful safety signal.

This hook must not be activated merely because another adapter is resident. It earns runtime use only after its own held-out/adversarial tests show that it adds independent error detection rather than correlated noise.

---

# 31. ADAPTER 1 HOST VALIDATION

After Evidence Reconciler output, the host checks:

```text
JSON/schema valid
known EFxxx/work IDs
known Rxxx refs
known RECxxx/result refs
support refs belong to allowed evidence bundle
no invented receipt
no invented Context ref
semantic_state enum valid
all established claims have support refs
conflict refs exist
material discovery candidates have source refs
scope obeyed
```

Host validation does not decide whether the model's semantic judgment is correct.

That is evaluated through independent tests/training and later cross-work composition.

---

# 32. ADAPTER 1 REPAIR

Recommended prototype behavior:

```text
initial Evidence Reconciler output
        |
        v
host validation
        |
     invalid
        |
        v
one bounded repair call
        |
        v
host validation
```

Repair packet contains:

```text
original bounded input
previous invalid output
exact validation failures
```

Example:

```text
- EF004 references unknown REC901.
- Established claim 2 has no support_refs.
- semantic_state "MOSTLY_GOOD" is not allowed.
```

Do not use vague `try again` repairs.

---

# 33. ADAPTER 2 — RECONCILIATION COMPOSER RESPONSIBILITY

The Composer receives validated `EFxxx` findings for the in-scope requirements plus active Context state.

It determines cross-work consequences:

```text
which findings combine
which evidence conflicts
which evidence target remains missing
whether a new term/entity/concept is materially necessary
whether Context must be revised
whether Decision must perform repair/follow-up work
whether durable-state consideration should be offered to Persistence
whether no further Reconciliation action is currently needed
```

It does not decide terminal requirement status.

---

# 34. REQUIREMENT-LEVEL RECONCILIATION POSTURE

For each in-scope requirement, the Composer may emit one or more nonterminal posture flags.

Recommended vocabulary:

```text
NO_GAP_IDENTIFIED
EVIDENCE_GAP_REMAINS
CONFLICT_PRESENT
CONTEXT_REENTRY_REQUIRED
DISCOVERY_FOLLOWUP_REQUIRED
REPAIR_REQUIRED
PERSISTENCE_RELEVANT
```

These are **not Completion statuses**.

Never emit:

```text
SATISFIED
FAILED
BLOCKED
PARTIAL
```

as terminal requirement outcomes from Reconciliation.

Completion owns that vocabulary.

---

# 35. RECONCILIATION COMPOSER OUTPUT CONTRACT

Recommended conceptual structure:

```text
reconciliation_run_id
reconciliation_revision
turn_id
scope
basis_hashes

work_findings
  EF001
  EF002
  ...

requirement_reconciliation
  R001
    posture_flags
    established_finding_refs
    remaining_gap_refs
    conflict_refs
    Context_impact_refs
    derived_need_refs
    repair_request_refs
    persistence_relevance_refs

Context_impact_proposals
Derived_needs
repair_requests
persistence_relevance_candidates

next_transition_recommendations
validation_metadata
handoff_hash
```

The host validates transitions before routing anything.

---

# 36. DISCOVERY IS NOT REPAIR

This distinction is locked.

## DISCOVERY

Valid work returned legitimate evidence that exposed a new necessary term, entity, relationship, distinction, or information gap.

Example:

```text
REC012 SUCCESS
results are valid
results reveal "NF4"
NF4 is materially needed to finish R001
```

Correct path:

```text
DN001
origin = DISCOVERY
```

## REPAIR

Prior planned/executed work was malformed, rejected, semantically wrong for its intended target, or otherwise needs correction rather than new discovery.

Example:

```text
W004 Save File
REC009 REJECTED_BEFORE_EXECUTION
reason: destination argument invalid
```

Correct path:

```text
RRQ001
origin = REPAIR
```

Do not label valid research expansion as failure.

Do not hide malformed work behind the word discovery.

---

# 37. DERIVED NEED `DNxxx` — LOCKED DISCOVERY ARTIFACT

A useful term discovered downstream was not necessarily communicated by the user.

Therefore Reconciliation may create a Derived Need rather than changing Intent.

Recommended fields:

```text
derived_need_id
parent_requirement_ids
created_from_work_refs
created_from_receipt_refs
created_from_evidence_finding_refs
created_from_context_refs
need_type

discovered_terms
  - term
    source_refs

discovered_entities
  - entity
    source_refs

discovered_relationships
  - relation
    source_refs

useful_term_or_gap
reason_needed
suggested_context_lane
persistence_relevance
status: PROPOSED
```

A `DNxxx` must remain subordinate to one or more original `Rxxx` requirements.

---

# 38. WHAT QUALIFIES AS A MATERIAL DISCOVERY

Do not create `DNxxx` for every new noun in a search result.

A discovery is material when the Composer judges that it is necessary or meaningfully useful to:

```text
finish an existing Rxxx
resolve an evidence gap
resolve a contradiction
identify the correct entity/version/artifact
perform a required downstream operation safely
explain why currently returned evidence is insufficient
identify durable state potentially relevant to the existing turn
```

Incidental trivia stays in evidence/result history and does not create recursive work.

---

# 39. MANDATORY DISCOVERY RE-ENTRY POINT — CONTEXT

**LOCKED RULE:**

> Any new term, entity, concept, relationship, identifier, or useful distinction that Reconciliation determines should enter the active recipe must re-enter at **Context** first.

It does not go directly to Decision.

It does not modify Intent.

Canonical path:

```text
RECxxx
   |
   v
RECONCILIATION
   |
   v
DN001
   |
   v
HOST VALIDATION
   |
   v
CONTEXT RE-ENTRY
   |
   v
selected affected Context lane(s)
   |
   v
new official Context revision if accepted
   |
   v
HOWARD COMMENT
   |
   v
DECISION RE-ENTRY
```

This is a hard compartment boundary.

---

# 40. WHY DISCOVERY DOES NOT RE-ENTER INTENT

Intent records what the user communicated.

A term discovered by Google/Wiki/File evidence is not retroactively something the user said.

Invalid:

```text
User never mentioned QLoRA.
Search discovers QLoRA.
Runtime edits original Intent:
R001 now says "research QLoRA".
```

Valid:

```text
R001 remains unchanged.
DN001 records that QLoRA was discovered while serving R001.
Context grounds QLoRA.
Decision may later create W003 from DN001.
```

Intent history remains trustworthy.

---

# 41. CONTEXT RE-ENTRY PACKET

Recommended packet from Reconciliation to Context:

```text
reentry_id
turn_id
reason: DISCOVERY | CONFLICT | CONTEXT_UPDATE
scope_requirement_ids
source_reconciliation_run_id
source_DN_refs
source_CIP_refs
source_EF_refs
source_REC_refs

new_material
  discovered_terms
  discovered_entities
  discovered_relationships
  evidence_gap
  conflict_summary

provenance_refs
suggested_affected_lane_ids_or_lane_purpose
active_context_snapshot_ref
```

Context receives the material **with provenance**, never as an unexplained naked term.

---

# 42. CONTEXT OWNS GROUNDING OF DISCOVERIES

Reconciliation may say:

> `QLoRA` is a materially relevant discovered term for `R001`.

Context determines:

```text
what QLoRA means in this turn
which lane it belongs to
whether supplied evidence grounds it
whether it conflicts with active Context
whether a new lane or revision is justified
which prior revision is superseded
```

Decision only sees the discovery after Context has produced accepted grounded state.

---

# 43. CONTEXT FUTURE-REENTRY PLACEHOLDER — SUPERSEDED INTERFACE NOTE

The earlier Context prototype intentionally contained only a future compatibility placeholder for downstream re-entry.

This Reconciliation spec locks the concrete A.R.C.A.D.I.A. behavior:

```text
DOWNSTREAM DISCOVERY
  -> DNxxx / CIPxxx
  -> Context re-entry
  -> Context lane/revision
```

Do **not** interpret the earlier placeholder as permission to rewrite original Intent with search-discovered terms.

Original Intent remains immutable except through its own explicitly versioned upstream mechanisms.

For this discovery path, Context re-entry is authoritative.

---

# 44. OFFICIAL LANE PROMOTION

A Reconciliation discovery packet is not itself an official Context lane.

Context acceptance alone also does not immediately make the revision fully active.

Downstream discovery promotion is finalized as a small host transaction:

```text
PROPOSED RE-ENTRY
      |
      v
CONTEXT PROCESSING
      |
      v
HOST VALIDATION
      |
  +---+---+
  |       |
reject   accept
          |
          v
PROMOTION_PENDING_COMMENT
          |
          v
HOWARD CONTEXT COMMENTATOR
          |
          v
HOST COMMENT VALIDATION
          |
     +----+----+
     |         |
   fail       pass
     |         |
 bounded      v
 repair    OFFICIAL ACTIVE
              CONTEXT LANE / REVISION
```

Rejected discovery packets remain historical proposals and never become active Context.

A downstream discovery revision must not be exposed to Decision as active Context while it is still `PROMOTION_PENDING_COMMENT`.

---

# 45. HOWARD COMMENT — MANDATORY ON DOWNSTREAM PROMOTION

**LOCKED RULE:**

> When a downstream Reconciliation discovery causes a Context lane to be created, revised, or superseded, Howard must add a bounded human-readable provenance comment before that downstream revision becomes officially `ACTIVE`.

The comment occurs after Context semantic acceptance but before promotion finalization.

```text
DN001 / CIP001
      |
      v
Context accepts semantics
      |
      v
PROMOTION_PENDING_COMMENT
      |
      v
HOWARD CONTEXT COMMENTATOR
      |
      v
comment validates
      |
      v
OFFICIAL ACTIVE LANE REVISION
```

The comment belongs to the Context lane/revision record.

It is not a Reconciliation truth source.

---

# 46. HOWARD COMMENT RESPONSIBILITY

The Howard comment should explain:

```text
what changed
what useful term/gap/conflict caused the change
which Rxxx requirement(s) the lane serves
which receipts/findings/discovery artifacts caused the re-entry
whether an older Context revision was superseded
that original Intent remains unchanged when appropriate
```

Example:

```text
Howard_comment:
"REC004 and REC005 introduced QLoRA and NF4 as relevant concepts needed to continue R002. Context accepted them into the adapter-training lane. This revision adds downstream-discovered grounding without replacing R002 or erasing the prior Context revision."
```

---

# 47. HOWARD COMMENT IS COMMENTARY, NOT AUTHORITY

Howard comment may not:

```text
create Rxxx
create DNxxx
claim an operation succeeded without RECxxx
turn inference into host fact
override Context evidence
write SQLite
change lane status
promote itself
```

The host validates its references and size.

If Howard comment generation or validation fails, the host records the failure explicitly and retries only under the bounded Context-comment repair policy. The revision remains `PROMOTION_PENDING_COMMENT` and must not continue to Decision as active Context. The host must not silently invent a comment in host prose.

---

# 48. HOWARD COMMENT ADAPTER REUSE

Do not train a third Reconciliation adapter merely for comments.

Reuse the existing Howard Context Commentator contract already established in the Context recipe.

It receives a bounded promotion packet such as:

```text
lane_id
new_revision
prior_revision_ref if any
promotion_trigger
requirement_ids
DN/CIP refs
REC/EF support refs
validated Context delta
```

Then produces a short structured comment.

Clear KV after the call.

---

# 49. CONTEXT IMPACT PROPOSAL `CIPxxx`

Not every Context change is a new discovered term.

Reconciliation may identify that returned evidence changes or conflicts with active Context directly.

Recommended `CIPxxx` fields:

```text
context_impact_proposal_id
requirement_ids
affected_context_refs
affected_lane_ids
source_EF_refs
source_REC_refs
impact_type
  NEW_GROUNDING
  CONTRADICTION
  STALENESS
  ENTITY_RESOLUTION
  VERSION_CHANGE
  RELATIONSHIP_CHANGE
proposed_delta_summary
reason
status: PROPOSED
```

Context decides whether/how this becomes an official revision.

---

# 50. CONFLICT PRESERVATION

Reconciliation must preserve disagreement rather than flattening it prematurely.

Example:

```text
REC001 -> source says version 2.4
REC002 -> source says version 2.5
```

Valid:

```text
EF001 semantic_state = CONFLICT
conflict:
  left_refs: [REC001:item3]
  right_refs: [REC002:item1]
  issue: current version disagrees
```

Invalid:

```text
model picks 2.5 because it sounds newer
```

unless provenance/timestamps/context justify that conclusion explicitly.

If active Context is affected, emit `CIPxxx` for Context re-entry.

---

# 51. REPAIR REQUEST `RRQxxx`

Reconciliation may request Decision repair when existing work should be replanned rather than expanded through discovery.

Recommended fields:

```text
repair_request_id
requirement_ids
failed_or_invalid_work_refs
receipt_refs
finding_refs
repair_reason
  MALFORMED_WORK
  WRONG_CAPABILITY_FOR_TARGET
  REJECTED_ARGUMENTS
  UNAUTHORIZED_SIDE_EFFECT_ATTEMPT
  SEMANTIC_TARGET_MISMATCH
  STALE_PLAN_AFTER_CONTEXT_CHANGE
requested_repair_scope
must_preserve_history: true
status: PROPOSED
```

The repair request does not create replacement work itself.

Decision owns new `Wxxx` creation.

---

# 52. WHAT IS NOT A RECONCILIATION REPAIR

Do not create `RRQxxx` for:

```text
transient provider transport reset already handled by Execution retry policy
new legitimate term discovered from valid evidence
one source simply returning no result when alternative work requires semantic planning
a requirement becoming newly interesting
routine Context promotion
```

Those have their own paths.

---

# 53. DECISION RE-ENTRY AFTER REPAIR

Correct path:

```text
RRQ001
   |
   v
HOST VALIDATION
   |
   v
DECISION RE-ENTRY
scope: affected Rxxx only
   |
   v
new Wxxx
work_origin: REPAIR
```

Old `Wxxx`, `TRQxxx`, and `RECxxx` remain historical.

Nothing is erased.

---

# 54. DECISION RE-ENTRY AFTER DISCOVERY

Correct discovery path is longer:

```text
DN001
   |
   v
CONTEXT RE-ENTRY
   |
   v
official Context lane/revision
   |
   v
Howard comment
   |
   v
DECISION RE-ENTRY
scope: affected Rxxx only
   |
   v
new Wxxx
work_origin: DISCOVERY
```

Decision never consumes an ungrounded raw search discovery directly.

---

# 55. ADDITIVE TURN LEDGER — LOCKED

Reconciliation grows the turn ledger.

It does not flatten or replace it.

```text
TURN
|
+-- Intent
|    +-- R001
|
+-- Context
|    +-- L001 rev1
|    +-- C001
|
+-- Decision
|    +-- W001
|    +-- W002
|
+-- Execution
|    +-- TRQ001 -> REC001
|    +-- TRQ002 -> REC002
|
+-- Reconciliation
|    +-- EF001
|    +-- EF002
|    +-- DN001
|
+-- Context Re-entry
|    +-- L001 rev2 ACTIVE
|    +-- Howard comment
|
+-- Decision Re-entry
|    +-- W003 DISCOVERY
|
+-- Execution
|    +-- TRQ003 -> REC003
|
+-- Reconciliation
     +-- EF003
```

Old artifacts remain addressable.

---

# 56. SUPERSESSION RULE

A new Context revision may supersede previous active Context working state.

It does not delete history.

A new Decision revision may supersede unexecuted plan state.

It does not delete executed receipts.

Reconciliation must preserve this distinction when composing consequences.

```text
SUPERSEDE ACTIVE INTERPRETATION
!=
ERASE HISTORICAL FACT
```

---

# 57. PERSISTENCE RELEVANCE

Reconciliation may identify that established evidence appears potentially durable.

It may emit a bounded persistence relevance candidate.

Example conceptual fields:

```text
candidate_uuid
requirement_ids
source_EF_refs
source_Context_refs if already promoted
candidate_summary
reason_potentially_durable
suggested_action_class:
  CONSIDER_SAVE
  CONSIDER_UPDATE
  CONSIDER_SUPERSEDE
```

This is advisory input to Persistence.

It is not a SQLite command.

---

# 58. PERSISTENCE SAFETY GATE

Do not let raw search text jump directly into SQLite merely because Reconciliation found it interesting.

Preferred eligibility:

```text
raw tool evidence
   |
   v
Reconciliation semantic finding
   |
   v
Context grounding/promotion when active turn state is affected
   |
   v
Persistence candidate references validated grounding/evidence
   |
   v
PERSISTENCE SHOULD SAVE?
```

Persistence owns:

```text
NO_SAVE
SAVE_NEW
UPDATE_EXISTING
SUPERSEDE_EXISTING
```

Host code owns the commit and receipt.

---

# 59. RECONCILIATION DOES NOT COMPLETE REQUIREMENTS

Even if every `Wxxx` finding is `ESTABLISHED`, Reconciliation does not emit:

```text
R001 -> SATISFIED
```

Why:

Completion must evaluate the entire authoritative requirement against:

```text
Intent
active Context
Decision/work history
Execution outcomes
Reconciliation findings
Persistence results if required
remaining blockers
```

Reconciliation may only say:

```text
R001 posture:
  NO_GAP_IDENTIFIED
```

That is nonterminal.

---

# 60. NO-FURTHER-ACTION PATH

A normal Reconciliation run may produce:

```text
all in-scope Wxxx findings validated
no Context re-entry
no DNxxx
no repair request
no persistence relevance
```

This is a clean pass.

The pipeline proceeds to Persistence.

Do not invent recursive work merely because Reconciliation ran.

---

# 61. INFORMATION-TOOL FAILURE HANDLING

Example:

```text
REC001 FAILED
REC002 SUCCESS
```

Reconciliation asks:

> Does the successful evidence still establish the target, or does a meaningful gap remain?

Possible outcomes:

```text
EF001 NOT_ESTABLISHED
EF002 ESTABLISHED
R001 posture NO_GAP_IDENTIFIED
```

or:

```text
R001 posture EVIDENCE_GAP_REMAINS
```

A failed operation does not automatically fail the turn.

---

# 62. NO-RESULT HANDLING

Example:

```text
REC009.execution_status = NO_RESULT
```

Reconciliation does not blindly cause another identical search.

It may determine:

```text
NOT_ESTABLISHED
```

Then Composer may:

```text
request discovery follow-up if new term/gap exists
request Decision repair if planning was wrong
or leave the gap for Completion if no legal useful work remains
```

Execution itself never loops semantically.

---

# 63. ACTION-TOOL FAILURE HANDLING

Example:

```text
Save File
REC015 FAILED
permission denied
```

Host truth remains:

```text
save did not succeed
```

Reconciliation may determine whether:

```text
repair planning is justified
alternate authorized destination exists in Context
requirement should simply proceed toward Completion with failure evidence
```

It may not claim the file exists.

---

# 64. SOURCE INDEPENDENCE SIGNALS

For multi-source research, Reconciliation should receive source/provenance metadata sufficient to distinguish:

```text
same source repeated
syndicated duplicate content
different pages from same publisher
independent sources
host-authoritative source
user/project file source
```

The host may provide independence signals.

The model still judges semantic corroboration.

Do not count URLs as independent evidence merely because their strings differ.

---

# 65. TERM / ENTITY DISCOVERY PIPELINE

Preferred pipeline:

```text
raw result payloads
      |
      v
ftfy/unicode comparison normalization
      |
      v
spaCy candidate terms/entities/relations
      |
      v
RapidFuzz candidate dedupe/alias signals
      |
      v
Evidence Reconciler
  "which of these actually matter to Wxxx?"
      |
      v
Reconciliation Composer
  "which materially require Context re-entry?"
      |
      v
DNxxx
```

This keeps deterministic modules useful without giving them semantic authority.

---

# 66. MULTIPLE DISCOVERED TERMS

A single `DNxxx` may carry multiple tightly related discovered terms when they belong to the same material need.

Example:

```text
DN004
parent_requirement_ids: [R001]
discovered_terms:
  - QLoRA
  - NF4
  - double quantization
reason_needed:
  these terms jointly define the newly exposed training method relevant to R001
```

Context decides whether they belong in:

```text
one lane revision
multiple lane revisions
or no promoted lane after validation
```

Do not force one `DNxxx` per noun.

---

# 67. CROSS-REQUIREMENT DISCOVERY

One valid discovery may serve multiple original requirements.

Example:

```text
DN005
parent_requirement_ids:
  - R002
  - R004
```

This is allowed only when the same discovery materially serves both requirements.

The host validates that all referenced requirements are in authorized scope.

---

# 68. DISCOVERY LOOP BOUNDS

Discovery must be recursive **but bounded**.

Prototype host policy should expose configurable limits such as:

```text
max_discovery_generations_per_requirement
max_active_DN_per_reconciliation_run
max_reconciliation_reentry_depth
```

Recommended prototype default philosophy:

```text
small finite limits
explicit diagnostic when exhausted
no silent infinite research loop
```

Do not encode unlimited recursion into adapter behavior.

When a bound is reached, record the unresolved state and allow Completion/Result to report it truthfully.

---

# 69. SELECTIVE RE-ENTRY

Only affected Context lanes and requirements re-enter.

Example:

```text
R001 -> no impact
R002 -> DN001 affects project-version lane
R003 -> no impact
```

Correct:

```text
Context re-entry scope: R002 / affected lane only
```

Incorrect:

```text
rerun all Context lanes
rerun all Decision requirements
repeat all searches
```

Selective re-entry is a core efficiency invariant.

---

# 70. CONTEXT RE-ENTRY MAY REJECT A DISCOVERY

Reconciliation's judgment that a term matters does not force Context to accept it as grounded state.

Possible Context outcomes:

```text
accepted and promoted
accepted but unresolved
conflict preserved
rejected as unsupported/irrelevant to lane
failed validation
```

Only accepted official lane/revision state proceeds as active Context.

Howard comment is attached only to official promoted lane/revision state produced by this downstream path.

---

# 71. RECONCILIATION HOST RESPONSIBILITIES

The host owns:

```text
RCN/EF/CIP/RRQ ID allocation
UUIDs
scope construction
upstream hash validation
receipt/result lookup
raw evidence preservation
normalization
signal generation
adapter packet construction
JSON/schema validation
reference validation
provenance validation
bounded repair loops
discovery loop counters
Context re-entry routing
Decision re-entry routing
stage transition legality
ledger append
active/superseded artifact tracking
handoff hashing
timestamps
```

The host does not silently replace semantic adapter judgments with its own preferences.

---

# 72. EVIDENCE RECONCILER MODEL RESPONSIBILITIES

Adapter 1 owns semantic judgments that deterministic code cannot safely prove:

```text
relevance to evidence target
meaning of returned text
partial vs complete evidence
semantic conflict
importance of newly appearing terms
which evidence supports which claim
whether active Context appears affected
```

It must remain bounded to the supplied work/evidence packet.

---

# 73. RECONCILIATION COMPOSER MODEL RESPONSIBILITIES

Adapter 2 owns:

```text
cross-work synthesis
shared evidence consequences
requirement-linked gap detection
material discovery decision
DNxxx proposal semantics
CIPxxx proposal semantics
RRQxxx proposal semantics
persistence relevance proposal
next-stage semantic routing recommendation
```

It cannot execute the routing itself.

---

# 74. HOST REPAIR VS MODEL REPAIR

The host may repair only deterministic mechanics that cannot change meaning.

Allowed:

```text
assign host ID
calculate timestamp/hash
canonicalize list ordering
remove exact duplicate refs
restore canonical enum casing when unambiguous under schema policy
```

Not allowed:

```text
change NOT_ESTABLISHED to ESTABLISHED
invent a missing support ref
invent DN001 because host thinks term is interesting
pick one side of a conflict
change repair into discovery
```

Semantic errors require bounded model repair or explicit failure.

---

# 75. ADAPTER 2 VALIDATION

Host checks:

```text
JSON/schema
RCN ID/revision
scope legality
all Rxxx refs exist
all EFxxx refs exist
all DNxxx provenance refs exist
all CIPxxx refs exist
all RRQxxx refs exist
no new Rxxx created
no Intent mutation
no direct tool request emitted
no SQLite command emitted
no terminal Completion status emitted
Context re-entry required for discovered new material
Howard comment not generated prematurely
```

---

# 76. ADAPTER 2 REPAIR

Same bounded pattern:

```text
initial Composer output
   |
   v
host validation
   |
invalid
   |
   v
one bounded repair call
   |
   v
host validation
```

If validation still fails:

```text
RECONCILIATION_REPAIR_EXHAUSTED
```

Record the failure against affected `Rxxx` scope.

Do not fabricate a clean handoff.

---

# 77. RECONCILIATION FAILURE CLASSES

Initial diagnostic vocabulary:

```text
UPSTREAM_INTEGRITY_FAILURE
INVALID_EVIDENCE_BUNDLE
INVALID_MODEL_OUTPUT
UNKNOWN_REQUIREMENT_REFERENCE
UNKNOWN_WORK_REFERENCE
UNKNOWN_RECEIPT_REFERENCE
UNKNOWN_CONTEXT_REFERENCE
SUPPORT_REFERENCE_OUT_OF_SCOPE
UNSUPPORTED_ESTABLISHED_CLAIM
INVALID_CONFLICT_REFERENCE
INVALID_DERIVED_NEED
INVALID_CONTEXT_IMPACT_PROPOSAL
INVALID_REPAIR_REQUEST
ILLEGAL_INTENT_MUTATION
ILLEGAL_DIRECT_TOOL_REQUEST
ILLEGAL_SQLITE_WRITE_REQUEST
ILLEGAL_COMPLETION_STATUS
DISCOVERY_BYPASSED_CONTEXT
HOWARD_COMMENT_PREMATURE
RECONCILIATION_REPAIR_EXHAUSTED
DISCOVERY_BOUND_EXHAUSTED
```

These are runtime/recipe diagnostics.

Completion later decides what they mean for terminal requirements.

---

# 78. RECONCILIATION HANDOFF

Minimum final handoff concept:

```text
reconciliation_artifact_id
reconciliation_run_id
reconciliation_revision
turn_id

basis
  intent_artifact_id/revision/hash
  context_snapshot_id/hash
  Decision run/revision/hash
  Execution run/hash

scope

Evidence_findings
requirement_reconciliation
Context_impact_proposals
Derived_needs
repair_requests
persistence_relevance_candidates

Context_reentry_events
Decision_reentry_events
promotion_refs_if_already_completed
Howard_comment_refs_if_already_completed

diagnostics
validation
handoff_hash
generated_at
```

The handoff is additive and provenance-rich.

---

# 79. PERMANENT TURN LEDGER ADDITIONS

Recommended ledger sections:

```text
RECONCILIATION_RUNS
EVIDENCE_FINDINGS
CONFLICT_RECORDS
DERIVED_NEEDS
CONTEXT_IMPACT_PROPOSALS
REPAIR_REQUESTS
PERSISTENCE_RELEVANCE_CANDIDATES
CONTEXT_REENTRY_EVENTS
RECONCILIATION_VALIDATION
ACTIVE_RECONCILIATION_BY_REQUIREMENT
SUPERSEDED_RECONCILIATION_STATE
HOWARD_COMMENT_REFS
```

These append to the turn.

They never replace `INTENT.REQUIREMENTS`.

---

# 80. TRAINING / DEBUG ARTIFACT CAPTURE

For every semantic Reconciliation adapter call, retain a debug/training artifact containing:

```text
adapter role/version
base model identity
adapter identity/hash
input schema version
output schema version
exact bounded input refs
host signal pack ref
raw model output
parsed output
validation report
repair attempt if any
latency/token metrics
final accepted artifact hash
```

Do not require hidden chain-of-thought capture.

Training should use explicit inputs/outputs and observable validation outcomes.

---

# 81. ADAPTER 1 TRAINING TARGETS

Evidence Reconciler training should cover:

```text
Google result relevance
Wiki result relevance
Load File content interpretation
one source fully establishes target
one source partially establishes target
successful tool but irrelevant result
no-result receipt
failed receipt plus successful corroborating receipt
conflicting numeric/version/date evidence
source duplication
alias/entity ambiguity
negation and contrast
new technical term appears but is incidental
new technical term is materially necessary
active Context contradicted by returned evidence
save-file deterministic case handed to model accidentally -> model should remain grounded
```

---

# 82. ADAPTER 2 TRAINING TARGETS

Reconciliation Composer training should cover:

```text
multiple EF findings combine cleanly
one failed Wxxx does not matter because another establishes target
true evidence gap remains
conflict requires Context re-entry
material discovery creates DNxxx
incidental discovery creates no DNxxx
multiple related terms grouped in one DNxxx
discovery serving multiple Rxxx
repair path vs discovery path
persistence relevance without SQLite write
no-further-action path
Context re-entry scoped narrowly
Decision repair scoped narrowly
never terminally complete Rxxx
never rewrite Intent
```

---

# 83. ADAPTER SUCCESS CRITERIA

## Evidence Reconciler passes when it consistently:

- distinguishes execution success from evidence establishment;
- stays within `Wxxx` evidence targets;
- cites exact supplied evidence refs;
- preserves conflict;
- recognizes partial evidence;
- uses host signals without treating them as truth;
- identifies material discoveries without noun-spamming;
- does not invent receipts or Context;
- does not complete requirements.

## Reconciliation Composer passes when it consistently:

- composes multiple findings correctly;
- creates `DNxxx` only when justified;
- sends discovered material to Context first;
- distinguishes discovery from repair;
- preserves additive history;
- scopes re-entry narrowly;
- proposes Context impact without overwriting Context;
- proposes persistence relevance without writing SQLite;
- avoids terminal `Rxxx` statuses;
- stops when no further semantic action is needed.

---

# 84. PERFORMANCE PHILOSOPHY

Reconciliation should be **host-heavy and model-selective**.

Spend adapter inference on:

```text
meaning
relevance
conflict
partial evidence
material discovery
cross-work consequences
```

Do not spend adapters on:

```text
hash verification
ID existence
receipt linkage
exact duplicate detection
schema validation
simple Save File receipt verification
normalization
regex extraction
simple alias similarity
loop counting
stage routing legality
```

The deterministic library layer exists specifically to reduce model burden.

---

# 85. RECOMMENDED SOURCE LAYOUT

```text
reconciliation_prototype/
|
+-- reconciliation_prototype.py
+-- README.md
|
+-- reconciliation/
|   +-- __init__.py
|   +-- models.py
|   +-- ids.py
|   +-- schemas.py
|   +-- validation.py
|   +-- provenance.py
|   +-- normalization.py
|   +-- url_canonicalization.py
|   +-- source_metadata.py
|   +-- timestamp_extract.py
|   +-- span_mapping.py
|   +-- evidence_grouping.py
|   +-- evidence_clustering.py
|   +-- duplicate_detection.py
|   +-- same_document.py
|   +-- structured_compare.py
|   +-- numeric_date_compare.py
|   +-- version_extract.py
|   +-- entity_alias_hints.py
|   +-- contradiction_cues.py
|   +-- linguistic_signals.py
|   +-- similarity.py
|   +-- deterministic_reconcile.py
|   +-- evidence_reconciler.py
|   +-- composer.py
|   +-- discovery.py
|   +-- context_impact.py
|   +-- repair.py
|   +-- context_reentry.py
|   +-- decision_reentry.py
|   +-- persistence_candidates.py
|   +-- howard_comment_interface.py
|   +-- ledger.py
|   +-- diagnostics.py
|   +-- handoff.py
|
+-- schemas/
|   +-- reconciliation_input.schema.json
|   +-- signal_pack.schema.json
|   +-- evidence_finding.schema.json
|   +-- reconciliation_composer_output.schema.json
|   +-- derived_need.schema.json
|   +-- context_impact_proposal.schema.json
|   +-- repair_request.schema.json
|   +-- reconciliation_handoff.schema.json
|
+-- fixtures/
|   +-- ...
|
+-- tests/
    +-- ...
```

Keep model runners thin.

Keep deterministic logic independently testable.

---

# 86. BUILD ORDER

Recommended prototype implementation order:

1. Define Reconciliation dataclasses and namespaces.
2. Define input/handoff schemas.
3. Build upstream integrity validator.
4. Build receipt/work evidence grouping.
5. Build raw + normalized evidence representation.
6. Add `ftfy` / Unicode normalization path while preserving raw evidence.
7. Add exact duplicate hashing.
8. Add bounded RapidFuzz similarity signals.
9. Add spaCy linguistic signal module.
10. Define Evidence Signal Pack schema.
11. Build deterministic receipt reconciliation path.
12. Define Evidence Reconciler input/output schemas.
13. Build Adapter 1 runner.
14. Build Adapter 1 host validation + one repair.
15. Create Adapter 1 independent fixture suite.
16. Define Composer input/output schemas.
17. Define `DNxxx` schema.
18. Define `CIPxxx` schema.
19. Define `RRQxxx` schema.
20. Build Adapter 2 runner.
21. Build Adapter 2 validation + one repair.
22. Build mandatory discovery -> Context re-entry router.
23. Build selective Context scope logic.
24. Build official promotion event interface.
25. Wire existing Howard Context Commentator for promoted downstream lanes.
26. Build Decision re-entry interfaces for discovery and repair.
27. Build persistence relevance candidate interface only.
28. Build discovery loop counters/limits.
29. Build additive ledger append logic.
30. Build final Reconciliation handoff.
31. Add CLI/PowerShell trace output.
32. Run deterministic module tests.
33. Run Adapter 1 tests.
34. Run Adapter 2 tests.
35. Run Context re-entry/Howard-comment tests.
36. Run end-to-end Reconciliation slice tests.
37. Freeze handoff contract before implementing Persistence.

---


# R2. TRUST, BASELINE, TRACE, AND CONTRACT-DRIFT LOCK

The prototype does not treat a structurally valid adapter output as earned semantic trust.

## R2.1 Trust qualification ladder

```text
T0  untrained / architecture-only
T1  fixture tests pass
T2  held-out semantic tests pass
T3  adversarial + composition tests pass
T4  shadow runtime; outputs logged but not authoritative
T5  limited authority under host gates
T6  production-authorized for this exact runtime identity
```

Trust attaches to the complete runtime identity, not merely an adapter name:

```text
base_model_hash
+ adapter_hash
+ AAE_contract_version
+ specialist_mode_contract_version
+ input_schema_version
+ output_schema_version
+ host_validation_version
```

Changing any component creates a new qualification target.

## R2.2 Base GGUF baseline is mandatory

Before adapter training is credited, run the exact frozen evaluation suite against:

```text
BASE GGUF
+ final AAE contract
+ real host packet builder
+ real validators
```

Record at minimum:

```text
schema accuracy
first-pass semantic accuracy
repair frequency
repaired semantic accuracy
hallucinated/unknown refs
uncertainty-state accuracy
latency
token counts
```

Then run the trained adapter against the **same held-out suite**. Adapter quality is measured as a delta from the frozen base baseline, not by impression.

## R2.3 Training/runtime single-source invariant

Training envelopes and runtime envelopes must be generated from the same machine-readable contract registry.

Do not maintain one prompt definition for training and a second manually copied definition for runtime.

The registry owns, at minimum:

```text
Global Awareness
Specialist Awareness
legal input artifact classes
input schema
output schema
legal enums
uncertainty behavior
repair shape
next consumer
contract version
```

## R2.4 Full trace and training-data firewall

Every model boundary preserves:

```text
exact AAE version
exact bounded packet
raw model output
parsed output
host validation result
repair packet/output when present
accepted artifact hash
adapter/base identities
latency/tokens
next-turn user correction/control signal when relevant
```

Runtime traces **do not automatically become training data**.

Required promotion path:

```text
RAW TRACE
  -> candidate extraction
  -> validation/review
  -> TRAINING_APPROVED
```

Held-out evaluation cases are separately tagged and must never enter training.

## R2.5 First-pass and repaired performance are separate metrics

Track independently:

```text
first_pass_structurally_valid
first_pass_semantically_correct
repaired_structurally_valid
repaired_semantically_correct
repair_exhausted
```

Repair is resilience. It must not camouflage weak first-pass behavior.


# R2B. RECONCILIATION-SPECIFIC TRUST FOCUS

Adversarial evaluation must over-sample:

```text
successful execution with irrelevant evidence
partial vs complete support
conflicting numbers/versions/dates
syndicated duplicates masquerading as corroboration
incidental vs material discovery
discovery vs repair
unsupported multi-source confidence
strong-looking structure with wrong semantic interpretation
```

Host signal preparation and Evidence Reconciler semantic accuracy are scored separately.

---

# 87. REQUIRED INDEPENDENT TESTS

At minimum:

```text
test_reconciliation_input_integrity
test_receipt_hash_validation
test_work_receipt_linkage
test_raw_text_preserved
test_ftfy_normalization_is_derived
test_exact_duplicate_hashing
test_rapidfuzz_signal_only
test_spacy_signal_only
test_signal_pack_schema
test_deterministic_save_reconcile
test_semantic_google_reconcile
test_semantic_wiki_reconcile
test_load_file_reconcile
test_partial_evidence
test_not_established
test_conflict
test_EF_support_refs
test_adapter1_repair
test_cross_work_composition
test_material_discovery
test_incidental_term_no_DN
test_multi_term_DN
test_cross_requirement_DN
test_context_impact_proposal
test_repair_request
test_discovery_not_repair
test_discovery_context_reentry
test_discovery_cannot_mutate_intent
test_discovery_cannot_bypass_context
test_official_lane_promotion
test_howard_comment_required_after_promotion
test_howard_comment_not_authority
test_rejected_reentry_no_official_comment
test_selective_reentry
test_persistence_relevance_no_sqlite_write
test_no_completion_status
test_no_further_action_path
test_additive_ledger
test_discovery_bound
test_reconciliation_end_to_end
```

---

# 88. REQUIRED FAILURE TESTS

At minimum:

1. Reconciliation receives unknown `W999`.
2. Receipt points to wrong work item.
3. Receipt hash fails.
4. Adapter cites nonexistent result item.
5. Adapter emits established claim with no support refs.
6. Adapter invents a new receipt.
7. Adapter changes receipt execution status.
8. Adapter treats duplicate syndicated evidence as independent proof without justification.
9. RapidFuzz similarity is treated as deterministic entity identity.
10. spaCy term candidate is automatically converted into `DNxxx` by host code.
11. New search term is inserted into original Intent.
12. `DNxxx` goes directly to Decision without Context re-entry.
13. Reconciliation directly creates a Context lane.
14. Context rejects re-entry but runtime marks lane active anyway.
15. Official downstream Context promotion has no Howard comment.
16. Howard comment is generated before Context acceptance.
17. Howard comment invents unsupported fact.
18. Howard comment changes `Rxxx`.
19. Composer emits `R001 SATISFIED`.
20. Composer issues Google request directly.
21. Composer requests SQLite write directly.
22. Repair path erases old `Wxxx`/`RECxxx`.
23. Discovery is incorrectly labeled repair.
24. Malformed work is incorrectly labeled discovery.
25. One affected lane causes all Context lanes to rerun.
26. Discovery recursion exceeds host bound but continues.
27. Save File failure is rewritten as success.
28. Successful Google execution with irrelevant pages is marked `ESTABLISHED` solely because status was SUCCESS.
29. Conflicting evidence is flattened without conflict record.
30. Reconciliation failure silently fabricates clean downstream state.

---

# 89. EXAMPLE A — GOOGLE SUCCESS, EVIDENCE ESTABLISHED

Decision:

```text
W001
requirement_ids: [R001]
evidence_target:
  current official library hours for requested date
```

Execution:

```text
TRQ001 -> Google
REC001.execution_status = SUCCESS
```

Evidence Reconciler:

```text
EF001
work_id: W001
semantic_state: ESTABLISHED
established_claims:
  - claim: official hours established for requested date
    support_refs: [REC001:item1]
```

Composer:

```text
R001 posture:
  NO_GAP_IDENTIFIED
```

No discovery loop is invented.

---

# 90. EXAMPLE B — GOOGLE SUCCESS, SEMANTIC FAILURE

```text
REC002.execution_status = SUCCESS
```

Returned pages are unrelated to the requested entity.

Correct:

```text
EF002.semantic_state = NOT_ESTABLISHED
not_established:
  - requested current hours
```

Incorrect:

```text
ESTABLISHED because Google returned HTTP success
```

---

# 91. EXAMPLE C — TWO GOOGLE SEARCHES, ONE DUPLICATE SOURCE

```text
W003 -> REC003
W004 -> REC004
```

Host comparison detects that one result fragment is exact duplicated syndicated content.

Signal pack:

```text
exact_duplicate_groups:
  - [REC003:item2, REC004:item1]
```

Evidence Reconciler uses this signal when assessing corroboration.

The duplicate signal is not itself a semantic verdict.

---

# 92. EXAMPLE D — MATERIAL TERM DISCOVERY

Initial:

```text
R002
  -> W005
  -> REC006 SUCCESS
```

Returned evidence establishes that `QLoRA` and `NF4` are materially necessary to finish `R002`.

Composer creates:

```text
DN001
parent_requirement_ids: [R002]
created_from_work_refs: [W005]
created_from_receipt_refs: [REC006]
created_from_evidence_finding_refs: [EF005]
discovered_terms:
  - QLoRA
  - NF4
reason_needed:
  returned evidence shows these concepts are necessary to resolve the training-method comparison required by R002
status: PROPOSED
```

Then:

```text
DN001
 -> host validation
 -> Context re-entry
 -> official lane/revision if accepted
 -> Howard comment
 -> Decision re-entry
 -> W006 work_origin DISCOVERY
```

`R002` remains unchanged.

---

# 93. EXAMPLE E — HOWARD COMMENT ON OFFICIAL PROMOTION

Context accepts the discovery semantically:

```text
lane_id: L_ADAPTER_TRAINING
revision: 3
status: PROMOTION_PENDING_COMMENT
promotion_trigger: DISCOVERY
trigger_refs:
  - DN001
  - EF005
  - REC006
requirement_ids:
  - R002
```

Howard Context Commentator adds:

```text
Howard_comment:
"Execution evidence introduced QLoRA and NF4 as relevant concepts needed to continue R002. Context accepted them into the adapter-training lane. This revision adds downstream-discovered grounding without replacing R002 or erasing the prior Context revision."
```

The host validates the comment, stores it with the lane revision, and only then changes the revision status to `ACTIVE`.

---

# 94. EXAMPLE F — CONTEXT CONFLICT

Active Context:

```text
C014:
current canonical project name = Foo Engine
```

Execution evidence:

```text
REC010:item1:
official source states project renamed Bar Engine
```

Evidence Reconciler:

```text
EF008.semantic_state = CONFLICT
```

Composer:

```text
CIP001
impact_type: ENTITY_RESOLUTION
affected_context_refs: [C014]
source_REC_refs: [REC010]
reason: returned official evidence conflicts with active canonical project name
```

Context decides the new active revision.

Reconciliation does not overwrite `C014` itself.

---

# 95. EXAMPLE G — REPAIR PATH

Decision:

```text
W009
work_origin: ORIGINAL
work_type: SAVE_USER_FILE
```

Execution:

```text
REC013.execution_status = REJECTED_BEFORE_EXECUTION
reason: malformed destination argument
```

Composer:

```text
RRQ001
requirement_ids: [R004]
failed_or_invalid_work_refs: [W009]
receipt_refs: [REC013]
repair_reason: REJECTED_ARGUMENTS
status: PROPOSED
```

Then:

```text
RRQ001
 -> Decision re-entry
 -> W010 work_origin REPAIR
```

No `DNxxx` is created.

---

# 96. EXAMPLE H — SAVE FILE DETERMINISTIC RECONCILIATION

```text
W010 target:
  save artifact A at path P with verified hash H

REC014:
  execution_status: SUCCESS
  actual_path: P
  verification: PASS
  content_hash: H
```

Host deterministic reconciler creates:

```text
EF010.semantic_state = ESTABLISHED
provenance_class = DIRECT_HOST_RECEIPT
```

No adapter call required.

---

# 97. EXAMPLE I — DISCOVERY REJECTED BY CONTEXT

Reconciliation proposes:

```text
DN004
term: "XYZ"
```

Context evaluates supplied evidence and rejects promotion as unsupported/incidental.

Correct ledger:

```text
DN004 status: REJECTED_AT_CONTEXT
no official active lane
no official downstream-promotion Howard comment
no Decision discovery work created from active Context
```

The proposal remains in history for debugging.

---

# 98. EXAMPLE J — PARTIAL TURN STILL READY LATER

```text
R001 has W001 and W002

EF001 = ESTABLISHED
EF002 = NOT_ESTABLISHED
```

Composer determines W002's missing evidence is nonessential because W001 established the actual evidence target required by R001.

Reconciliation posture:

```text
R001 -> NO_GAP_IDENTIFIED
```

This still does **not** mean:

```text
R001 SATISFIED
```

Completion decides that later.

---

# 99. CLI / COMMAND-WINDOW TRACE — RECOMMENDED

Prototype debug trace should remain readable.

Example:

```text
[RCN] run=RCN001 scope=R001,R002 upstream_hashes=PASS
[RCN] W001 receipts=1 mode=SEMANTIC_EVIDENCE
[SIGNAL] W001 terms=4 entities=1 duplicates=0 conflicts=0
[ADAPTER:EvidenceReconciler] W001 -> EF001 ESTABLISHED
[RCN] W002 receipts=2 mode=SEMANTIC_EVIDENCE
[SIGNAL] W002 terms=8 entities=2 exact_duplicates=1
[ADAPTER:EvidenceReconciler] W002 -> EF002 PARTIAL discovery_candidates=2
[ADAPTER:Composer] R002 -> DISCOVERY_FOLLOWUP_REQUIRED DN001
[HOST] DN001 validation=PASS
[REENTRY:Context] scope=R002 lane_hint=adapter_training
[CONTEXT] L004 rev2 PROMOTION_PENDING_COMMENT supersedes=rev1
[HOWARD_COMMENT] lane=L004 rev2 PASS
[CONTEXT] L004 rev2 ACTIVE
[REENTRY:Decision] trigger=DN001 scope=R002
[RCN] handoff_hash=... PASS
```

Do not print hidden model chain-of-thought.

---

# 100. RECONCILIATION INVARIANTS — LOCKED

```text
1. Rxxx remains authoritative and unchanged by downstream discovery.

2. RECxxx is immutable host evidence of operation reality.

3. Execution success is not semantic evidence success.

4. Reconciliation may interpret receipts; it may not edit them.

5. Deterministic host modules run before adapters where useful.

6. spaCy/RapidFuzz/ftfy/regex produce signals, not semantic authority.

7. Exactly two new Reconciliation adapters exist in the prototype.

8. Purely mechanical receipt outcomes may bypass adapters.

9. EFxxx findings must cite supplied evidence refs.

10. Conflict is preserved, not silently flattened.

11. Discovery is not repair.

12. DNxxx is subordinate to original Rxxx.

13. Material downstream discoveries re-enter at Context first.

14. Discovered terms never get silently appended to original Intent.

15. Reconciliation does not directly create/promote Context lanes.

16. Context owns grounding and official lane/revision promotion.

17. Every downstream-discovery Context revision must receive a validated Howard comment before it becomes officially ACTIVE.

18. Howard comment is commentary/provenance, not authority.

19. Decision receives discovery only after Context grounding/promotion.

20. Repair requests return to Decision without pretending they are discoveries.

21. Reconciliation never writes SQLite.

22. Persistence receives candidates; host Persistence owns commit.

23. Reconciliation never emits terminal Rxxx Completion status.

24. Re-entry is selective to affected requirements/lanes.

25. The turn ledger is additive; history is not erased.

26. Discovery recursion is bounded by host policy.

27. If validation/repair fails, record failure rather than fabricate clean state.
```

---

# 101. PROTOTYPE SPECIALIST CONTRACT — EVIDENCE RECONCILER

Canonical semantic instruction:

> Given one authorized work item, its original evidence target, the exact immutable host receipts/results produced for that work, relevant active Context, and host-generated deterministic signals, determine only what the returned work actually establishes. Preserve conflicts, partial evidence, missing evidence, and exact support references. Identify newly appearing terms/entities/concepts only as candidates and state whether they may materially matter. Do not rewrite Intent, create requirements, call tools, write persistence, promote Context, or declare terminal requirement satisfaction.

---

# 102. PROTOTYPE SPECIALIST CONTRACT — RECONCILIATION COMPOSER

Canonical semantic instruction:

> Given validated per-work Evidence Findings for the in-scope authoritative requirements and the active grounded Context state, determine the minimum legitimate downstream consequences. Preserve conflicts and history. Create a Derived Need only when valid downstream evidence exposed a materially necessary new term, entity, relationship, distinction, or gap. All such discovered material must route through Context before Decision. Create a repair request only when prior work requires correction rather than legitimate discovery. You may identify Context impact and persistence relevance, but you may not edit Intent, execute tools, write SQLite, promote Context, or assign terminal requirement status.

---

# 103. NON-GOALS FOR THIS PROTOTYPE

Do not turn Reconciliation into:

```text
a web browser
a tool executor
a second Decision planner
a second Context recipe
a persistence writer
a final-answer generator
a terminal Completion checker
a universal truth engine
a giant free-form summarizer
```

Do not add:

```text
third Reconciliation critic adapter
one adapter per evidence source
unbounded research loops
automatic SQLite learning
raw tool text -> Context with no validation
raw term -> Decision with no Context pass
```

---

# 104. LOCKED RECONCILIATION DESIGN SUMMARY

```text
PARENT
locked Tool / Execution handoff

CORE QUESTION
what did returned work actually establish?

NEW ADAPTERS
2
  Evidence Reconciler
  Reconciliation Composer

HOWARD
reuse existing Context Commentator only on accepted official downstream Context promotion

DETERMINISTIC MODULES
jsonschema, dataclasses, uuid, hashlib, datetime, enum, collections, typing, re, RapidFuzz

STRONGLY USEFUL
ftfy, spaCy, difflib, unicodedata

OPTIONAL
regex, networkx

WORK SEMANTIC STATES
ESTABLISHED / PARTIAL / NOT_ESTABLISHED / CONFLICT

PER-WORK ARTIFACT
EFxxx Evidence Finding

DISCOVERY ARTIFACT
DNxxx Derived Need

CONTEXT CHANGE PROPOSAL
CIPxxx

REPAIR ARTIFACT
RRQxxx

DISCOVERY RE-ENTRY
mandatory through Context first

INTENT
never rewritten merely because search/file evidence discovered a new term

OFFICIAL LANE PROMOTION
Context + host authority only

HOWARD COMMENT
mandatory during downstream-discovery promotion
revision remains PROMOTION_PENDING_COMMENT until comment validates
commentary only; never authority

PERSISTENCE
candidate only; no SQLite write

COMPLETION
not owned by Reconciliation

LEDGER
additive and provenance-preserving

LOOPS
selective and host-bounded
```

---

# 105. FINAL HANDOFF PRINCIPLE

Reconciliation is complete when the host can truthfully say:

> **For every in-scope work item, we preserved what actually happened, determined what the returned evidence established, recorded conflicts and gaps, routed any materially new discovered concepts through Context, requested repair only where prior work actually needed correction, preserved all provenance, and produced a validated nonterminal state for Persistence/Completion without inventing success.**

That is the Reconciliation boundary.
