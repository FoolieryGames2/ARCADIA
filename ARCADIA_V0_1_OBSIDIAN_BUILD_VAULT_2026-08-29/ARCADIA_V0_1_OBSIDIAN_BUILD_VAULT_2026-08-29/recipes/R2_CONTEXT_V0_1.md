---
title: "A.R.C.A.D.I.A. v0.1 — Canonical Recipe Contract"
project: "A.R.C.A.D.I.A."
version: "0.1-prototype"
checkpoint_date: "2026-08-29"
document_role: "recipe-contract"
source_path: "recipes/R2_CONTEXT_V0_1.md"
source_sha256: "c345820c8911eeb09286108fa588d057cf6de0092235bd295a390b911d3bc0c0"
source_bytes: 56184
source_integrity: "preserved"
tags:
  - "arcadia/v0-1"
  - "type/recipe"
  - "status/frozen"
aliases:
  - "R2_CONTEXT_V0_1.md"
  - "A.R.C.A.D.I.A. v0.1 — Canonical Recipe Contract"
---

> [!info] Obsidian navigation
> **Checkpoint role:** `recipe-contract`  
> **Frozen source:** `recipes/R2_CONTEXT_V0_1.md` · SHA-256 `c345820c8911eeb0…`  
> **Command center:** [[ARCADIA v0.1 - Command Center]]  
> **Connected:** [[01_ARCADIA_V0_1_FULL_PROJECT_CHECKPOINT]] · [[03_ARCADIA_V0_1_GLOBAL_CONTRACTS_AND_INVARIANTS]] · [[04_ARCADIA_V0_1_AAE_CONTRACT_REGISTRY_AND_SERIALIZATION]] · [[R1_INTENT_V0_1]] · [[R3_DECISION_V0_1]] · [[07_ARCADIA_V0_1_SOURCE_POLICY_REGISTRY]] · [[ARCADIA_PERSISTENCE_SQLITE_SCHEMA_V0_1.sql]] · [[ARCADIA_V0_1_FULL_PIPELINE_AAE_REFERENCE_5_SLICES]]

<!-- OBSIDIAN_LAYER_END — ORIGINAL SOURCE CONTENT BEGINS BELOW -->

# A.R.C.A.D.I.A. v0.1 — Canonical Recipe Contract

**v0.1 integration status:** The detailed semantic recipe body below is carried forward from the final pre-v0.1 trust/recovery specification because R3 intentionally did not change semantic recipe ownership. It is now governed by the v0.1 common runtime/AAE/source/recovery/trace/performance contracts in this bundle.

**Conflict rule:** if this carried-forward body contains older wording about adapter loading, generic adapter runtime, source-quality being unresolved, trace retention, crash replay, global sampling, handwritten AAE framing, or model-call necessity, the v0.1 system documents `01`–`09` supersede that wording. Semantic recipe responsibilities, artifacts, edge cases, and tests remain authoritative unless explicitly superseded.

---

# HOWARD CONTEXT RECIPE
## Prototype Build Specification — PowerShell / Command-Window Reference
**Status:** CONTEXT PROTOTYPE SOURCE OF TRUTH  
**Scope:** CONTEXT ONLY  
**Date:** 2026-08-28  
**Parent:** `HOWARD_INTENT_RECIPE_PROTOTYPE_BUILD_SPEC_2026-08-28.md`  
**Purpose:** Archive-ready build reference for implementing and independently testing Howard's Context recipe as the direct continuation of the locked Intent prototype. This document defines Context's host authority, evidence loops, SQLite use, validation rules, model roles, data contracts, module ownership, adapter use, and final handoff. It deliberately stops at the Context boundary.

---

> **CONFIRMED LOGIC INTEGRATION — R2 — 2026-08-28**  
> This R2 document integrates the confirmed trust/recovery logic locked after the AAE five-slice review: single-source AAE/runtime/training contracts, base-model baselining, full trace capture with a training-data firewall, packet-projection testing, aggregate loop telemetry, durable-provisional semantic Persistence with next-turn review, controlled user memory correction, deterministic-first semantic support, and mode-specific Howard evaluation.  
> **Source-quality / source-authority ranking is intentionally NOT defined by this update. It remains a separate required design lane.**


# 0. CORE RULE

Context does **not** mean "go retrieve memory."

Context means:

> Receive the completed Intent state, preserve it, optionally enrich it with bounded direct input and validated persistent evidence, and produce a faithful structured snapshot for the next recipe without losing, silently rewriting, or inventing upstream information.

The minimum successful path is:

```text
INTENT PACKET
     |
     v
CONTEXT STAGE
     |
     v
ACCURATE STRUCTURED CONTEXT HANDOFF
```

SQLite retrieval is conditional.

```text
INTENT PACKET
     |
     +--> no persistent evidence needed
     |         |
     |         v
     |    no SQLite call
     |         |
     |         v
     |    preserve Intent + build Context handoff
     |
     +--> persistent evidence needed
               |
               v
        selected Context lane(s)
               |
               v
         SQLite evidence loops
               |
               v
        validated Context handoff
```

**No SQLite call is a normal PASS.**

Context has read authority over persistent evidence selected by the host. Context has **no implicit write authority**.

Durable save/write logic belongs to a separate host-controlled persistence path. A specialist may later propose information worth saving, but only program logic and validation may commit durable state. Context never writes something merely because a model considered it useful.

---

# 1. CONTEXT STARTS FROM INTENT, NOT FROM A BLANK MODEL

The completed Intent packet is the root turn ledger.

It persists through Context unchanged.

Context may append resolutions, evidence, conflicts, and derived Context points. It does not rewrite the original Intent artifact to pretend Intent knew later information from the beginning.

```text
ORIGINAL INTENT PACKET
        |
        | immutable reference / hash checked
        v
CONTEXT ENRICHMENT
        |
        +--> Context loop reports
        +--> Context resolutions
        +--> Howard Context interpretation
        |
        v
FINAL CONTEXT HANDOFF
```

Example:

```text
INTENT TERM CANDIDATE
T001
raw: "Mercury"
provisional_meaning: planet
confidence: medium
```

Later Context evidence may establish:

```text
CONTEXT RESOLUTION
T001
resolved_meaning: Mercury outboard motor
support_refs: E004, E007
status: supported
```

The original Intent interpretation remains visible.

This is required for:
- auditability;
- debugging;
- later training-data extraction;
- identifying where a misunderstanding entered the recipe;
- selective re-entry if later evidence changes the task.

---

# 2. HIGH-LEVEL CONTEXT PIPELINE

```text
COMPLETED INTENT PACKET
        |
        +-------------------------------+
        |                               |
        |                        OPTIONAL DIRECT
        |                        NARROW INPUT
        |                               |
        +---------------+---------------+
                        |
                        v
                HOST CONTEXT ROUTER
                        |
             determine needed split lanes
                        |
          +-------------+-------------+
          |                           |
     ZERO SQLITE                  ONE OR MORE
       LANES                      SQLITE LANES
          |                           |
          |                           v
          |                  HOST RETRIEVES CANDIDATES
          |                           |
          |                           v
          |                  [EVIDENCE SPECIALIST]
          |                           |
          |                     structured judgment
          |                           |
          |                           v
          |                    HOST VALIDATION
          |                           |
          |                +----------+----------+
          |                |                     |
          |             invalid                valid
          |                |                     |
          |          bounded repair              v
          |                              [HOWARD CONTEXT
          |                                COMMENTATOR]
          |                                     |
          |                               structured comment
          |                                     |
          |                                     v
          |                              HOST VALIDATION
          |                                     |
          |                                     v
          |                              FINISH LANE LOOP
          |                                     |
          +--------------------+----------------+
                               |
                               v
                      COLLECT LOOP REPORTS
                               |
                               v
                    [HOWARD CONTEXT SYNTHESIS]
                               |
                     structured overall snapshot
                               |
                               v
                      FINAL HOST VALIDATION
                               |
                               v
                       CONTEXT HANDOFF
```

The same Howard adapter may perform both:
- per-lane Context comments; and
- the final overall Context snapshot.

Its hidden KV state does not carry authority between calls. Explicit structured artifacts do.

---

# 3. CONTEXT INPUT CONTRACT

Context accepts three conceptually distinct input classes.

## 3.1 Required — Original Intent Packet

The completed Intent handoff from the locked Intent recipe.

Minimum Context-useful fields include:

```text
turn_id
intent_artifact_id
intent_revision
intent_hash
source spans
term candidates
primary_intent
secondary_intents
requirements
unresolved items
capability candidates
memory candidates
interaction metadata needed downstream
```

The full original packet remains available. Context may use a narrowed view for a particular lane, but the root packet is never discarded.

---

## 3.2 Optional — Direct Narrow Input

Context may receive extra material supplied directly by the host/upstream recipe.

This is **not SQLite retrieval**.

Examples may later include:
- a bounded attachment extract;
- a host-owned state snapshot;
- a narrow artifact payload;
- a structured result supplied by another source;
- an explicitly scoped piece of information needed for this Context invocation.

Default:

```text
direct_context_input: null
```

When present, it must retain:

```text
direct_input_id
source_kind
source_ref
raw_payload or structured payload
received_at
content_hash
metadata
```

Direct input does not automatically become durable memory and is never silently written to SQLite.

If semantic judgment is required, the host may place direct input into the same evidence-lane machinery with a distinct `source_kind`. If it is already a bounded authoritative host structure, the host may preserve it directly in the final handoff. In both cases provenance remains explicit.

---

## 3.3 Optional — SQLite Evidence

SQLite is queried only when the host determines that one or more Context lanes require persistent evidence.

SQLite is a source of durable program-owned records.

The model does not directly query SQLite.

```text
MODEL
  X
  | no SQL
  | no arbitrary DB access
  X
SQLITE
```

The host selects, retrieves, scopes, identifies, hashes, and packages candidate evidence before any specialist sees it.

---

# 4. MODEL / ADAPTER ALLOCATION

Context is intentionally stingy with adapter slots.

## New Context adapter

```text
1. EVIDENCE SPECIALIST
```

Core learned skill:

> Judge bounded supplied evidence against the current Intent requirement and selected Split Library contract; preserve source authority; detect relevance, staleness, partial support, conflict, and unresolved gaps; do not answer the user.

This is deliberately broader than "SQLite reader." SQLite is only one evidence source.

---

## Reused adapter

```text
HOWARD CONVERSATIONALIZER / HOWARD CONTEXT COMMENTATOR
```

The Intent Howard adapter is reused because the contract is still:

```text
STRUCTURED COMPLETED WORK
        ->
NATURAL HOWARD INTERPRETATION
```

In Context this output is **internal structured Context work**, not a direct Resident Chat response.

Howard is used:
- after a lane's evidence judgment passes host validation;
- once again after all lanes finish to produce the overall Context snapshot.

Reuse is allowed because the skill contract overlaps. If testing proves the Context synthesis job materially differs, that becomes evidence for a later candidate adapter decision. Do not allocate another adapter preemptively.

---

## No Context router adapter

Routing is host logic.

The program owns:
- which lanes run;
- which split definition governs each lane;
- which evidence candidates are supplied;
- when a lane terminates;
- which artifacts move downstream.

Do not spend an adapter on deterministic execution-graph control.

---

# 5. KV / MODEL STATE RULE

**Clear KV/attention cache at every model boundary and every adapter switch.**

Adapters may remain warm in RAM if the runtime allows it.

What persists is explicit structured state.

```text
EVIDENCE SPECIALIST
      |
      | output artifact
      v
CLEAR KV
      |
      v
HOWARD COMMENT
      |
      | output artifact
      v
CLEAR KV
```

Each Context lane is independently reproducible from its explicit inputs.

Howard's final overall snapshot must receive the explicit completed loop reports. It must not depend on hidden KV memory from previous Howard lane comments.

---

# 6. HOST AUTHORITY — LOCKED

The host has absolute authority over:

1. the identity and hash of the original Intent packet;
2. Context run IDs and revision state;
3. lane selection;
4. Split Library definitions and versions;
5. SQLite queries and scope filters;
6. which evidence was actually supplied;
7. timestamps and metadata read from storage;
8. evidence IDs and content hashes;
9. JSONSchema validation;
10. bounded retry/repair control;
11. loop termination;
12. final handoff assembly;
13. whether an artifact is safe to enter the next stage.

The host does **not** pretend to possess semantic intelligence it does not have.

The Evidence Specialist judges meaning/relevance.

Howard interprets validated evidence into Context.

The host validates legality, provenance, structural integrity, scope, and stage transitions.

---

# 7. VALID IS NOT THE SAME AS CORRECT

Do not collapse all validation into one boolean.

Use separate concepts.

Recommended minimum:

```text
host_valid
semantic_status
safe_for_next_stage
```

Example:

```json
{
  "host_valid": true,
  "semantic_status": "conflict",
  "safe_for_next_stage": true
}
```

A conflict can be a successful Context result.

Likewise:

```json
{
  "host_valid": true,
  "semantic_status": "no_match",
  "safe_for_next_stage": true
}
```

A correctly completed empty/no-match lane is not a failure.

### Initial semantic status vocabulary

```text
accepted
partial
no_match
conflict
unresolved
```

### Initial lane status vocabulary

```text
completed
no_candidates
failed_validation
```

### Howard Context point modes

```text
supported
inference
unresolved
```

Do not call an inference a supported fact.

---

# 8. SPLIT LIBRARY

The Evidence Specialist does not judge evidence in a vacuum.

Every Context lane is evaluated against a host-owned **Split Library definition**.

The Split Library is versioned source configuration.

It tells the host and specialist what kind of evidence matters for that lane.

Minimal conceptual definition:

```json
{
  "split_id": "project_continuity",
  "split_version": 1,
  "purpose": "Resolve prior project continuity needed by current Intent.",
  "allowed_source_kinds": [
    "durable_record",
    "direct_input"
  ],
  "allowed_scopes": [
    "current_resident",
    "current_project"
  ],
  "freshness_policy": "metadata_aware",
  "max_candidates": 12,
  "empty_result_is_valid": true
}
```

The exact lane/split catalog is intentionally extensible.

Do **not** freeze a giant universal Context lane list before field testing.

A split may define:
- purpose;
- eligible source classes;
- required scope;
- freshness expectations;
- maximum candidate count;
- whether empty results are valid;
- optional ranking hints;
- required metadata;
- specialist output restrictions.

The specialist may interpret the selected split. It may not invent, change, or select a different split.

---

# 9. AUTHORITY IS CONTEXTUAL, NOT ONE GLOBAL NUMBER

Do not build one universal `authority_score = 1..10` and assume it solves evidence precedence.

Different evidence is authoritative about different things.

Examples:

```text
current_intent
-> authoritative about what the user is asking now

host_state
-> authoritative about host-owned current state

durable_record
-> authoritative about what the program actually saved

operation_receipt
-> authoritative about what an operation returned

external_result
-> evidence from a retrieval/tool source

derived_interpretation
-> model-derived Context judgment

howard_comment
-> Howard's interpretation of validated evidence
```

The Split Library says which source/authority classes matter for a particular lane.

A SQLite record cannot override a new explicit user correction about what they mean now merely because the record is durable.

A Howard comment cannot override the stored record it was derived from.

---

# 10. SQLITE EVIDENCE CONTRACT

Context reads durable semantic records that have already passed program-owned Persistence logic **and are eligible for normal semantic projection**.

R2 rule: a newly committed conversational semantic transaction may be durably present in SQLite while its semantic standing is still `PROVISIONAL`. `PROVISIONAL` state is excluded from normal Context truth retrieval. It may be exposed only through the bounded provisional-review control path described below.

A saved record should expose enough host-owned metadata to support later Context judgment.

Recommended candidate-facing metadata:

```text
sqlite_record_id
source_kind
created_at
updated_at if available
scope
resident/project ownership if applicable
metadata/tags if applicable
payload
content_hash
```

When a Context lane retrieves candidates, the host assigns run-local evidence IDs:

```text
E001
E002
E003
...
```

Example:

```json
{
  "evidence_id": "E002",
  "sqlite_record_id": "ctx_8841",
  "source_kind": "durable_record",
  "created_at": "2026-08-27T21:18:02-04:00",
  "scope": "project/howard",
  "content_hash": "...",
  "payload": "...",
  "metadata": {}
}
```

Evidence IDs are immutable for that run/loop.

The model may only reference evidence that the host actually supplied.

---


# R2. PRE-CONTEXT PROVISIONAL-MEMORY REVIEW GATE — LOCKED

Durable-provisional Persistence creates a deliberate gate before normal semantic-memory injection on the next user turn.

If the immediately preceding completed turn produced one or more `PROVISIONAL` semantic transactions, the host evaluates the current validated Intent control signals before ordinary Context retrieval.

Canonical outcomes:

```text
explicit AFFIRM_PRIOR
  -> host finalizes prior transaction as CONFIRMED_EXPLICIT

CORRECT_PRIOR / REJECT_PRIOR / UNDO_PRIOR_EFFECT
  -> prior provisional state is NOT injected as established Context
  -> host invokes the Persistence direct-control compensation path
  -> immutable original transaction/receipt remain historical facts
  -> corrected current-turn content proceeds through the normal recipe spine

CONTINUE_PRIOR_STATE
  -> host may finalize as STABILIZED_NO_IMMEDIATE_CORRECTION
  -> this is not recorded as explicit user confirmation

NONE / unrelated neutral continuation
  -> host may finalize as STABILIZED_NO_IMMEDIATE_CORRECTION under versioned policy
  -> this is not recorded as explicit user confirmation

AMBIGUOUS_TARGET
  -> do not finalize the affected provisional transaction
  -> do not inject it as clean established Context
  -> use bounded conversation resolution / clarification as required
```

This gate does not give Context write authority. All reversal/finalization state changes are Persistence Host operations with immutable transaction history.

Normal Context retrieval may use:

```text
CONFIRMED_EXPLICIT
STABILIZED_NO_IMMEDIATE_CORRECTION
```

It must not silently treat `STABILIZED_NO_IMMEDIATE_CORRECTION` as if the user explicitly confirmed the fact.

---

# 11. FREEZE THE EVIDENCE SNAPSHOT

SQLite may change while Context is running.

Each loop therefore operates against a frozen retrieved evidence snapshot.

At retrieval time preserve:

```text
retrieved_at
database revision/snapshot marker if available
record IDs
record timestamps
record content hashes
split version
intent revision
```

For the prototype, exact row-content hashes plus retrieval timestamp are sufficient if the database does not expose a convenient revision marker.

A record changing after retrieval does not silently mutate the evidence already given to the specialist.

A later recipe/run may decide that the changed state requires a new Context pass.

---

# 12. HOST MODULES — CONTEXT FOUNDATION

## Core from the beginning

```text
jsonschema
dataclasses
uuid
hashlib
RapidFuzz
re
```

## Strongly useful

```text
ftfy
spaCy
```

## Selective/support use

```text
regex
difflib
```

---

# 13. MODULE OWNERSHIP

## `jsonschema`

Hard gate at every structured model boundary.

Use for:
- Intent-input validation at Context entry;
- lane request validation;
- candidate bundle validation;
- Evidence Specialist output validation;
- Howard lane-comment validation;
- final Context snapshot validation;
- final Context handoff validation.

It validates structure, not truth.

---

## `dataclasses`

Preferred internal representation for host-side Context objects.

Use objects such as:

```text
ContextRun
IntentReference
LaneRequest
SplitDefinition
EvidenceCandidate
EvidenceBundle
EvidenceJudgment
HowardLaneComment
ContextLoopReport
ContextSnapshot
ContextHandoff
ValidationReport
```

Avoid making the whole source tree a pile of untyped nested dictionaries.

---

## `uuid`

Use for:
- Context run IDs;
- lane loop IDs;
- direct input IDs;
- artifact IDs;
- repair attempt IDs;
- Context snapshot IDs.

Run-local short display aliases like `E001` may exist alongside UUID-backed internal IDs.

---

## `hashlib`

Use for:
- Intent packet integrity;
- direct-input payload integrity;
- SQLite evidence payload integrity;
- schema/version provenance;
- loop input/output provenance;
- final Context handoff hash;
- replay/cache safety.

Hash canonical serialized forms, not mutable pretty-printed console text.

---

## `RapidFuzz`

Use for deterministic candidate narrowing before model judgment.

Good uses:
- project names;
- resident names;
- note/artifact titles;
- aliases;
- typo-tolerant lookup hints;
- shortlist ranking against a bounded eligible candidate set.

RapidFuzz does **not** decide semantic truth.

Preferred flow:

```text
exact ID / exact canonical match
        |
        v
exact declared alias
        |
        v
bounded RapidFuzz shortlist
        |
        v
Evidence Specialist judgment
```

Do not dump a large SQLite table on the model when deterministic narrowing can reduce it first.

---

## `re`

Default regex engine for common structural work.

Use for:
- IDs;
- known field formats;
- timestamps;
- simple path/file patterns;
- bounded metadata parsing;
- exact support-span checks where appropriate;
- cheap structural filters.

Compile stable patterns once at startup.

---

## `regex`

Use only when standard `re` is insufficient.

Examples:
- advanced Unicode cases;
- overlapping matches;
- bounded fuzzy-regex use;
- advanced boundary requirements.

Do not use `regex` as a meaning engine.

---

## `ftfy`

Use for text normalization before comparison/search when encoding or Unicode damage exists.

Rule:

```text
preserve raw text
        +
create normalized comparison text
```

Never destroy the original evidence payload.

Do not silently hash only a transformed representation and lose provenance to the raw source.

---

## `spaCy`

Use as a lightweight deterministic linguistic assistant.

Useful for:
- entity candidates;
- noun chunks;
- lemmas;
- date/time/entity cues;
- project/person/object query hints;
- shallow reference-resolution hints;
- candidate retrieval terms.

spaCy supports routing and candidate generation.

It does **not** decide whether evidence is authoritative or semantically correct.

---

## `difflib`

Support/debug module.

Useful for:
- repair diagnostics;
- human-readable packet changes;
- comparing pre/post repair JSON;
- comparing Intent revisions later;
- explaining why a host repair occurred during development.

RapidFuzz remains the primary approximate-match workhorse.

---

# 14. INTERNAL OBJECTS VS JSON — LOCKED

The codebase should not become "JSON-looking code everywhere" internally merely because model boundaries need JSON.

Preferred rule:

```text
INTERNAL HOST STATE
-> Python dataclasses / typed objects

MODEL / FILE / LOG / REPLAY BOUNDARY
-> dict / JSON

BOUNDARY ENFORCEMENT
-> JSONSchema
```

JSON is appropriate for:
- model input/output contracts;
- saved traces;
- replay fixtures;
- source-of-truth schema files;
- CLI debug dumps;
- interoperability.

JSON is **not** required as the internal representation of every host object.

---

# 15. HOST PRE-LOOP VALIDATION

Before an Evidence Specialist call, the host must prove the loop is mechanically legal.

Required checks:

```text
Intent packet exists
Intent schema valid
Intent hash unchanged
Intent revision known
requested lane exists
selected split exists
split version known
candidate source classes allowed
candidate scopes allowed
candidate count within split maximum
candidate IDs unique
candidate hashes recorded
retrieval timestamp recorded
```

If no candidate qualifies and the split allows empty results:

```json
{
  "lane_status": "no_candidates",
  "host_valid": true,
  "semantic_status": "no_match",
  "safe_for_next_stage": true
}
```

No model call is required just to discover that the host retrieved nothing.

---

# 16. EVIDENCE SPECIALIST

## Core question

> "Against this selected Context split and current Intent need, what does the supplied evidence actually support?"

## Inputs

The specialist receives only bounded structured material:

```text
run / loop identity
current Intent references needed for this lane
lane purpose
selected Split Library definition
candidate evidence bundle
candidate metadata/timestamps
```

It does not receive arbitrary database access.

---

## Responsibilities

For every candidate, judge:
- relevant or irrelevant;
- direct or partial support;
- stale or currently usable;
- conflicting with another supplied source;
- insufficient to resolve the need;
- applicable to the current scope;
- likely useful for Howard's Context construction.

It may expose uncertainty.

It should prefer a bounded honest `unresolved` over confident invention.

---

## Initial output shape

```json
{
  "lane_id": "L003",
  "split_id": "project_continuity",
  "considered": ["E001", "E002", "E003"],
  "accepted": [
    {
      "evidence_id": "E002",
      "relevance": "direct",
      "support_spans": ["..."]
    }
  ],
  "partial": [],
  "rejected": [
    {
      "evidence_id": "E001",
      "reason": "stale"
    }
  ],
  "conflicts": [],
  "unresolved": [],
  "semantic_status": "accepted"
}
```

Exact schema may evolve during prototype implementation, but these responsibilities are frozen.

---

## Hard prohibitions

Evidence Specialist does not:
- query SQLite;
- add evidence records;
- invent evidence IDs;
- modify stored evidence;
- write memory;
- answer the Resident;
- change the Intent packet;
- change the Split Library;
- validate itself;
- claim operation/tool success;
- silently resolve unsupported conflicts.

---

# 17. HOST VALIDATION AFTER EVIDENCE SPECIALIST

After model output, validate mechanically.

Required checks:

```text
JSON parse PASS
JSONSchema PASS
known lane ID
known split ID
split version matches
all considered IDs were supplied
all accepted IDs were supplied
all partial IDs were supplied
all rejected IDs were supplied
no phantom evidence IDs
no evidence moved outside allowed scope
support spans occur in the referenced supplied evidence
allowed enum values only
array limits respected
no illegal duplicate/contradictory record placement
Intent hash/revision still matches loop input
```

Only then:

```text
safe_for_howard: true
```

The host is not claiming the semantic judgment is mathematically true.

The host is claiming:

> This is a structurally valid, provenance-grounded semantic judgment over exactly the evidence the specialist was authorized to inspect.

That distinction is mandatory.

---

# 18. HOWARD PER-LANE CONTEXT COMMENT

If the Evidence Specialist output passes host validation and the lane contains useful or meaningful status, Howard receives a bounded Context package.

Howard receives:

```text
relevant original Intent references
validated accepted evidence
validated partial evidence when useful
validated conflicts
validated unresolved items
lane purpose
```

Rejected evidence is not passed as normal positive evidence. A rejection may be summarized by the host when Howard needs to understand why a conflict/gap remains.

---

## Core question

> "What Context should be carried forward from this validated lane?"

Howard is not answering the Resident here.

---

## Recommended structured output

```json
{
  "lane_id": "L003",
  "context_points": [
    {
      "context_point_id": "C001",
      "text": "...",
      "support_refs": ["I004", "E002"],
      "mode": "supported"
    }
  ],
  "unresolved": []
}
```

Support reference namespaces should remain explicit.

Recommended convention:

```text
Ixxx -> Intent/source/requirement reference
Dxxx -> direct narrow input
Exxx -> retrieved evidence
Cxxx -> Howard-derived Context point
```

---

## Howard Context rules

Every factual Context point must carry support references.

If Howard makes a reasonable synthesis beyond explicit wording:

```text
mode: inference
```

If the evidence cannot establish the point:

```text
mode: unresolved
```

Howard may interpret.

Howard may not turn inference into host truth.

---

# 19. HOST VALIDATION AFTER HOWARD COMMENT

Required checks:

```text
JSON parse PASS
JSONSchema PASS
correct lane ID
context point IDs unique
all support refs exist
support refs come only from allowed lane inputs
no reference to phantom/rejected evidence as positive support
allowed point modes only
bounded output size
required unresolved conflict remains visible
no illegal change to original Intent artifact
```

The host cannot perfectly prove semantic entailment from a paraphrase.

Do not fake that capability.

The host's job is to ensure Howard's comment remains bounded, traceable, and honest about support mode.

---

# 20. CONTEXT LOOP REPORT

Each lane terminates with an explicit report.

Recommended conceptual shape:

```text
CONTEXT LOOP REPORT

run_id
loop_id
lane_id
split_id
split_version
intent_artifact_id
intent_revision
intent_hash
retrieved_at
candidate_ids
candidate_hashes
evidence_specialist_judgment
host_evidence_validation
howard_context_comment
host_howard_validation
semantic_status
lane_status
safe_for_next_stage
```

A lane with nothing useful still terminates cleanly.

Example:

```text
lane_id: project_history
lane_status: no_candidates
semantic_status: no_match
host_valid: true
safe_for_next_stage: true
```

"No relevant saved Context was found" is valid Context information.

---

# 21. FINAL HOWARD CONTEXT SYNTHESIS

After every requested lane terminates, Howard receives an explicit structured snapshot input.

Input includes:

```text
ORIGINAL INTENT PACKET / bounded referenced view
        +
OPTIONAL DIRECT NARROW INPUT
        +
ALL COMPLETED CONTEXT LOOP REPORTS
```

Howard then constructs the overall Context snapshot.

Core question:

> "Given the original Intent and every validated Context result, what grounded working state should the next recipe receive?"

---

## Recommended final snapshot sections

```text
current_subject
current_job
known_context_points
resolved_references
relevant_history
current_constraints
conflicts
unresolved_items
source_refs
important_do_not_assume items
```

The exact field names may evolve during implementation. The duties do not.

The final snapshot must distinguish:
- supported Context;
- inference;
- unresolved Context;
- conflict.

Howard's final snapshot is **derived Context**, not a replacement for its evidence.

---

# 22. FINAL HOST CONTEXT VALIDATION

Before Context declares completion, host checks:

```text
Original Intent artifact exists
Original Intent hash unchanged
Original Intent revision accounted for
Optional direct input accounted for or null
Every requested lane terminated
Every loop has legal status
Every accepted evidence ref exists
Every Howard Context ref exists
No phantom evidence refs
No required conflict disappeared
No unresolved item was silently converted to fact
Overall Howard snapshot references validated inputs only
Final Context schema valid
Final Context handoff hash generated
```

Then:

```text
ready_for_next_stage: true
```

If a lane fails bounded validation, the handoff may still exist but must explicitly carry the failed lane and `ready_for_next_stage` must follow host policy. Do not silently fabricate replacement Context.

---

# 23. FINAL CONTEXT HANDOFF — TWO-LAYER RULE

The downstream handoff preserves two layers.

```text
1. ORIGINAL INTENT
   unchanged authoritative upstream artifact

2. CONTEXT REPORT
   everything Context learned or derived later
```

Recommended conceptual structure:

```text
CONTEXT HANDOFF

context_run_id
context_version

intent
  artifact_id
  revision
  hash
  original packet or reference

direct_input
  null or explicit provenance-preserved payload

context_loops
  zero or more completed loop reports

context_snapshot
  Howard overall structured Context interpretation

validation
  host_valid
  safe_for_next_stage
  conflicts
  unresolved

provenance
  final_handoff_hash
  generated_at
```

Do not flatten Intent and Context into one rewritten blob.

---

# 24. NO-SQLITE PATH — LOCKED

If Context determines there is no need for SQLite, the first Intent packet still passes through Context.

```text
INTENT PACKET
      |
      v
HOST CONTEXT ROUTER
      |
      +--> sqlite_lanes = []
      |
      v
HOWARD OVERALL CONTEXT SNAPSHOT
      |
      v
FINAL HOST VALIDATION
      |
      v
CONTEXT HANDOFF
```

This path is important.

Context is not defined by retrieval.

Example handoff summary:

```text
sqlite_lanes: 0
context_loops: 0
intent_preserved: true
context_snapshot_present: true
ready_for_next_stage: true
```

---

# 25. OPTIONAL DIRECT-INPUT PATH — LOCKED OPEN INTERFACE

The prototype keeps a deliberate opening for narrow Context input that does not come from SQLite.

This path will not be needed on every pass.

```text
INTENT PACKET
     +
OPTIONAL DIRECT INPUT
     |
     v
CONTEXT
```

Rules:
- default is absent/null;
- provenance must be explicit;
- content hash required;
- never silently stored;
- never mislabeled as SQLite history;
- may be assigned to a lane if semantic evidence judgment is needed;
- may be preserved directly if it is already bounded host-owned structured state;
- final handoff identifies the source class clearly.

Do not overbuild this path before real inputs require more policy.

---

# 26. BOUNDED REPAIR / REPROMPT

A specialist output may be mechanically invalid.

Examples:

```text
bad JSON
unknown evidence ID
missing required field
illegal enum
support span not present in cited evidence
```

Use surgical repair instructions.

```text
OUTPUT
  |
  v
HOST VALIDATION
  |
  +--> PASS -> continue
  |
  +--> FAIL -> bounded repair prompt
                 |
                 v
             revalidate
```

Initial hard prototype limit:

```text
maximum repair attempts per model boundary: 2
```

After the limit:

```text
lane_status: failed_validation
safe_for_howard: false
```

Do not retry valid semantic outcomes such as:

```text
conflict
no_match
partial
unresolved
```

Those are Context results, not parser failures.

---

# 27. JSONSCHEMA GATES

Every model artifact crosses a host-owned schema gate.

```text
MODEL OUTPUT
     |
     v
JSON PARSE
     |
     v
JSONSCHEMA
     |
     +--> FAIL -> bounded repair
     |
     v
REFERENCE / PROVENANCE VALIDATION
     |
     +--> FAIL -> bounded repair
     |
     v
SAFE FOR NEXT STAGE
```

Recommended schema files:

```text
schemas/
  context_input.schema.json
  lane_request.schema.json
  evidence_bundle.schema.json
  evidence_judgment.schema.json
  howard_lane_comment.schema.json
  context_loop_report.schema.json
  context_snapshot.schema.json
  context_handoff.schema.json
```

Strict schemas are preferred at model boundaries.

Use `additionalProperties: false` where field expansion should be intentional rather than accidental.

---

# 28. PROVENANCE / ID NAMESPACES

Suggested readable namespaces:

```text
TURN / INTENT
I... or original Intent IDs such as S001, T001, R001, U001

DIRECT INPUT
D001, D002, ...

SQLITE / EVIDENCE
E001, E002, ...

CONTEXT POINTS
C001, C002, ...

LANE LOOPS
L001, L002, ...
```

Behind human-readable aliases, host UUIDs may provide collision-resistant identity.

Every derived point should be traceable backward.

```text
C004
  -> support_refs: I008, E002
```

No model-generated factual Context point should exist without explicit provenance mode and support references.

---

# 29. WHAT CONTEXT MAY REPAIR

Context may repair a provisional Intent interpretation when later evidence supports a different resolution.

Context does **not** mutate the original Intent artifact.

It appends a resolution.

Examples:
- named project identity;
- pronoun/reference target;
- which saved artifact the user meant;
- prior project state;
- previously stored preference relevant to the current job;
- stale-vs-current saved information.

A Context correction must identify:

```text
what Intent item is being resolved
what the new resolution is
what evidence supports it
whether the result is supported/inferred/unresolved
```

---

# 30. WHAT CONTEXT DOES NOT DO

Context does not:
- write SQLite;
- decide what should be permanently saved;
- execute tools;
- perform web search;
- perform load/search/tool operations belonging to later recipes;
- claim a tool succeeded;
- create operation receipts;
- answer the Resident directly;
- design the next recipe;
- silently update Intent history;
- treat Howard comments as host truth;
- treat RapidFuzz/spaCy/regex output as semantic authority;
- require SQLite on every turn;
- require direct narrow input on every turn.

---

# 31. DOWNSTREAM RE-ENTRY CONTRACT — R2 LOCKED

Downstream Reconciliation may discover materially necessary terms, entities, relationships, conflicts, or gaps.

Canonical route:

```text
DNxxx / CIPxxx
   -> host validation
   -> Context re-entry for affected lanes only
   -> proposed lane/revision
   -> Context semantic validation
   -> PROMOTION_PENDING_COMMENT
   -> Howard Context comment
   -> host comment validation
   -> ACTIVE revision
   -> selective Decision re-entry
```

Original accepted Intent and `Rxxx` are not revised by downstream discovery.

Unaffected validated Context lanes are preserved.

Execution/Reconciliation receipts remain immutable and are referenced as provenance; Context does not perform the tool work itself.

---

# 32. RECOMMENDED SOURCE LAYOUT

A Windows-friendly prototype can use a simple structure like:

```text
context_prototype/
|
+-- context_prototype.py
+-- README.md
|
+-- context/
|   +-- models.py
|   +-- router.py
|   +-- retrieval.py
|   +-- normalization.py
|   +-- validation.py
|   +-- provenance.py
|   +-- hashing.py
|   +-- repair.py
|
+-- splits/
|   +-- split_library.json
|
+-- schemas/
|   +-- context_input.schema.json
|   +-- lane_request.schema.json
|   +-- evidence_bundle.schema.json
|   +-- evidence_judgment.schema.json
|   +-- howard_lane_comment.schema.json
|   +-- context_loop_report.schema.json
|   +-- context_snapshot.schema.json
|   +-- context_handoff.schema.json
|
+-- prompts/
|   +-- evidence_specialist.txt
|   +-- howard_context_comment.txt
|   +-- howard_context_snapshot.txt
|
+-- samples/
|   +-- intent_packets/
|   +-- direct_inputs/
|   +-- sqlite/
|
+-- tests/
|   +-- test_context_entry.py
|   +-- test_router.py
|   +-- test_retrieval.py
|   +-- test_evidence_specialist.py
|   +-- test_howard_comment.py
|   +-- test_no_sqlite.py
|   +-- test_context_final.py
|
+-- runs/
    +-- <run-id>/
```

Exact filenames may change during implementation. Separation of responsibilities should remain.

---

# 33. POWERSHELL / COMMAND-WINDOW PROTOTYPE USE

## PowerShell

```powershell
PS C:\Howard\context_prototype> py .\context_prototype.py `
    --intent .\samples\intent_packets\sample_intent.json `
    --sqlite .\samples\sqlite\context_test.db
```

No-SQLite test:

```powershell
PS C:\Howard\context_prototype> py .\context_prototype.py `
    --intent .\samples\intent_packets\simple_turn.json `
    --no-sqlite
```

Optional direct-input test:

```powershell
PS C:\Howard\context_prototype> py .\context_prototype.py `
    --intent .\samples\intent_packets\artifact_turn.json `
    --direct-input .\samples\direct_inputs\artifact_extract.json `
    --sqlite .\samples\sqlite\context_test.db
```

## Command Prompt

```bat
C:\Howard\context_prototype> python context_prototype.py --intent samples\intent_packets\sample_intent.json --sqlite samples\sqlite\context_test.db
```

No-SQLite test:

```bat
C:\Howard\context_prototype> python context_prototype.py --intent samples\intent_packets\simple_turn.json --no-sqlite
```

The prototype should also accept interactive input later if useful, but file-driven deterministic replay is the priority for testing.

---

# 34. COMMAND-WINDOW DISPLAY

A future CLI runner should look approximately like:

```text
C:\Howard\context_prototype> python context_prototype.py --intent samples\intent.json --sqlite context_test.db

[CONTEXT RUN] 3f5a...
[INTENT] artifact=I-a92c... revision=1 hash=PASS
[DIRECT INPUT] none

[ROUTER] 2 context lanes requested

[L001] split=project_continuity
[RETRIEVE] 14 eligible -> 6 narrowed candidates
[EVIDENCE] PASS  0.61s  status=accepted
[HOST GATE] PASS  refs=PASS spans=PASS scope=PASS
[KV] cleared
[HOWARD] PASS  0.48s  context_points=2
[HOST GATE] PASS
[KV] cleared
[L001] COMPLETE

[L002] split=resident_saved_preference
[RETRIEVE] 0 eligible candidates
[L002] NO_CANDIDATES -> VALID NO_MATCH

[FINAL HOWARD] PASS  0.57s
[FINAL HOST GATE] PASS
[KV] cleared

[CONTEXT HANDOFF]
intent_preserved: true
sqlite_lanes: 2
completed_loops: 2
accepted_evidence: 2
conflicts: 0
unresolved: 1
ready_for_next_stage: true
handoff_hash: 7d31...
```

No-SQLite example:

```text
C:\Howard\context_prototype> python context_prototype.py --intent samples\simple_turn.json --no-sqlite

[CONTEXT RUN] 5c11...
[INTENT] hash=PASS
[ROUTER] 0 SQLite lanes requested
[SQLITE] SKIPPED -- normal path
[FINAL HOWARD] PASS
[FINAL HOST GATE] PASS

[CONTEXT HANDOFF]
intent_preserved: true
sqlite_lanes: 0
context_loops: 0
context_snapshot_present: true
ready_for_next_stage: true
```

Console formatting is a prototype reference, not a runtime UI contract.

---

# 35. RUN ARTIFACTS / DEBUG TRACE

Each prototype run should be replayable.

Recommended run folder:

```text
runs/<context_run_id>/
  00_input_intent.json
  01_direct_input.json              # only if present
  02_router_plan.json
  03_lane_L001_evidence_bundle.json
  04_lane_L001_evidence_output.json
  05_lane_L001_host_validation.json
  06_lane_L001_howard_comment.json
  07_lane_L001_howard_validation.json
  08_lane_L001_report.json
  ...
  90_final_howard_snapshot.json
  91_final_validation.json
  99_context_handoff.json
  run_manifest.json
```

`run_manifest.json` should record:

```text
context_run_id
prototype version
schema versions
split library version
Intent artifact ID/revision/hash
adapter IDs/versions
SQLite path/test database identity
start/end timestamps
repair counts
KV clear confirmations
final handoff hash
```

This is development/audit trace, not durable Resident memory.

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


# R2A. PACKET-PROJECTION RECALL IS A HOST BENCHMARK

The host must test not only model quality but whether it supplied the smallest **sufficient** packet.

For every fixture with a known correct semantic result, record the minimum required artifact set and assert that the packet builder included it.

Required metrics include:

```text
required_artifact_recall
irrelevant_artifact_rate
packet_token_count
missing_required_ref_failures
stale_or_wrong_revision_injection
```

A specialist that reasons correctly from an incomplete packet does not make the system correct. Packet-projection failures are host failures and are labeled separately from adapter failures.

---

# 36. INDEPENDENT SLICE TESTING

Do not combine Context into the larger matrix until its slices can be characterized independently.

Suggested tests:

```text
test_context_entry_integrity
test_no_sqlite_pass
test_direct_input_provenance
test_split_selection
test_sqlite_scope_filter
test_rapidfuzz_candidate_narrowing
test_evidence_snapshot_hashing
test_evidence_specialist
test_evidence_reference_validation
test_support_span_validation
test_conflict_preservation
test_stale_evidence_judgment
test_no_match_completion
test_howard_lane_comment
test_howard_support_refs
test_final_context_snapshot
test_final_handoff_integrity
test_bounded_repair
test_kv_clear_boundaries
test_context_end_to_end
```

Every test should record:
- exact Intent input;
- exact direct input if present;
- exact SQLite fixture/version;
- selected split/version;
- candidate bundle;
- specialist adapter/version;
- model output;
- schema pass/fail;
- provenance validation pass/fail;
- repair count;
- latency;
- token count;
- KV clear confirmation;
- human semantic judgment;
- known failure category.

---

# 37. REQUIRED FAILURE TESTS

The prototype must deliberately test bad outputs.

At minimum:

```text
phantom evidence ID
wrong lane ID
wrong split ID
support span not present
accepted evidence from wrong resident/project scope
stale evidence accepted without flag when split requires freshness awareness
Howard cites rejected evidence as supported fact
Howard creates unsupported factual Context point
Howard silently drops conflict
Howard upgrades inference to supported
Intent packet hash changed during Context
malformed JSON
extra illegal JSON fields
repair attempts exceed maximum
SQLite returns zero candidates
no SQLite requested
```

A validator that never fails is not a validator.

---

# 38. EXAMPLE A — NO SQLITE REQUIRED

## Incoming Intent

```text
PRIMARY_INTENT
Help rewrite a short paragraph the user just supplied.

REQUIREMENTS
R001 preserve meaning
R002 improve clarity

UNRESOLVED
none

CONTEXT_LOOKUP_NEEDED
false
```

## Context Router

```text
sqlite_lanes: []
direct_context_input: null
```

## Result

No evidence specialist call.

Howard receives the original Intent packet and constructs a minimal Context snapshot:

```text
CURRENT_JOB
Rewrite the supplied paragraph.

KNOWN_CONTEXT
Only current-turn material is needed.

HISTORICAL_CONTEXT
not requested / not needed

UNRESOLVED
none
```

Final Context handoff:

```text
intent_preserved: true
sqlite_lanes: 0
context_loops: 0
ready_for_next_stage: true
```

---

# 39. EXAMPLE B — SQLITE PROJECT CONTINUITY

## Incoming Intent

```text
USER REFERENT
"that adapter"

PRIMARY_INTENT
Continue working on the adapter discussed previously.

UNRESOLVED
U001: which adapter does "that adapter" refer to?

CLARIFICATION
context_resolution_first: true
```

## Router

```text
lane: project_continuity
split: project_continuity
```

## Host retrieval

```text
E001 -> old Candidate02 adapter note
E002 -> recent Candidate04 adapter state
E003 -> unrelated image adapter record
```

Each record includes timestamp, scope, source metadata, and hash.

## Evidence Specialist

```text
E001 -> partial/stale for current referent
E002 -> accepted/direct
E003 -> rejected/irrelevant
semantic_status -> accepted
```

## Host validation

Checks:

```text
E001/E002/E003 all supplied
support spans exist
scope legal
split correct
hashes unchanged
schema valid
```

## Howard Context comment

```text
C001
text: "The current prior-work referent is Candidate04, not the older Candidate02 state."
support_refs: U001, E002
mode: supported
```

## Loop report

```text
lane_status: completed
semantic_status: accepted
safe_for_next_stage: true
```

Original Intent `U001` remains visible. Context adds its resolution rather than rewriting history.

---

# 40. EXAMPLE C — CONFLICT IS A VALID RESULT

## Evidence

```text
E004: newer saved record says project target = alpha build
E005: older saved record says project target = beta build
```

If metadata or source authority does not establish a safe winner, Evidence Specialist may return:

```text
semantic_status: conflict
conflicts:
- E004 vs E005
unresolved:
- active target cannot be established safely
```

Host may validate this as:

```text
host_valid: true
safe_for_next_stage: true
```

Howard carries forward:

```text
C009
mode: unresolved
text: "Saved Context conflicts on the active target; do not assume alpha or beta yet."
support_refs: E004, E005
```

Context succeeds by preserving uncertainty.

---

# 41. EXAMPLE D — OPTIONAL DIRECT INPUT

## Inputs

```text
Intent packet
+
D001 direct narrow artifact extract
```

No SQLite may be needed.

Host records:

```text
D001 source_kind: direct_input
D001 content_hash: ...
D001 provenance: supplied by upstream program
```

If the content already has authoritative structured meaning, it may be included in Howard's final Context snapshot with its `D001` reference.

If the artifact needs semantic selection/judgment, the host may assign it to a normal Context lane and let the Evidence Specialist judge it under the selected split.

It remains `D001`, not an invented SQLite record.

---

# 42. ADAPTER / SPECIALIST SUCCESS CRITERIA

## Evidence Specialist passes when it consistently:
- accepts directly relevant evidence;
- rejects irrelevant evidence;
- detects partial evidence;
- detects obvious staleness when metadata matters;
- preserves conflicts;
- exposes unresolved gaps;
- references only supplied evidence IDs;
- obeys split boundaries;
- does not answer the Resident;
- does not narrate unrelated reasoning;
- does not invent storage state.

## Howard Context reuse passes when it consistently:
- converts validated lane work into concise useful Context points;
- preserves support references;
- labels inference honestly;
- preserves unresolved/conflict state;
- produces an accurate overall Context snapshot;
- does not change upstream Intent decisions without explicit Context resolution evidence;
- does not turn internal Context work into a direct Resident-facing answer.

If one of these contracts repeatedly fails in a way host logic cannot safely repair, that is evidence for a later training or adapter decision.

---

# 43. PERFORMANCE PHILOSOPHY

Do not send the model work deterministic modules can finish reliably.

Preferred flow:

```text
Intent requirement
      |
      v
host scope filter
      |
      v
exact ID / alias filters
      |
      v
RapidFuzz shortlist if earned
      |
      v
bounded candidate bundle
      |
      v
Evidence Specialist semantic judgment
```

Do not:

```text
SELECT * FROM memory
      |
      v
send everything to model
```

The model is the semantic judge, not the database engine.

---

# 44. CONTEXT PERSISTENCE PHILOSOPHY

Context packages are temporary working state.

```text
SQLITE / HOST SOURCES
       |
       v
CONTEXT RETRIEVAL
       |
       v
TEMPORARY CONTEXT PACKAGE
       |
       v
NEXT RECIPE
```

Context does not recursively save its own interpretations back into durable storage.

This avoids:

```text
saved fact
  -> model interpretation
      -> auto-saved interpretation
          -> later retrieved as fact
              -> reinterpreted
                  -> auto-saved again
```

Any future durable write must go through a separate explicit persistence decision, program validation, metadata/timestamp assignment, and commit path.

---

# 45. LOCKED CONTEXT DESIGN SUMMARY

```text
PARENT
locked Intent prototype packet

ROOT AUTHORITY
original Intent artifact persists unchanged

CONTEXT DEFINITION
accurate enrichment/handoff, not mandatory retrieval

SQLITE
conditional read only

SQLITE WRITE
not available to Context

NO-SQLITE PATH
normal PASS

DIRECT NARROW INPUT
optional, provenance-preserved, default null

NEW ADAPTER
1 Evidence Specialist

HOWARD
reuse Intent Howard adapter for lane comment + final Context synthesis

ROUTER
host-owned, no adapter

SPLIT LIBRARY
host-owned versioned Context lane contracts

EVIDENCE
host retrieves/scopes/hashes; model judges semantics

HOST VALIDATION
structure + provenance + scope + references + stage safety

SEMANTIC VALIDATION
specialist judgment, never confused with JSON/schema validity

RAPIDFUZZ
bounded candidate narrowing only

SPACY
retrieval/query hints only

FTFY
comparison normalization while raw source survives

RE / REGEX
structural parsing, not meaning authority

DATACLASSES
internal host objects

JSON
model/file/log/replay boundaries

JSONSCHEMA
hard gate at every model boundary

HASHLIB
integrity / replay / frozen evidence snapshots

UUID
stable run/artifact identity

DIFFLIB
repair/debug visibility

KV
clear at every model boundary / adapter switch

LOOP RESULT
accepted / partial / no_match / conflict / unresolved are all possible valid semantic outcomes

FINAL HANDOFF
original Intent + optional direct input + zero/more loop reports + Howard overall Context snapshot

DOWNSTREAM RE-ENTRY
later authoritative results may revise Intent and selectively rerun affected Context loops; not implemented here
```

---

# 46. BUILD PHILOSOPHY

Keep the Context specialist narrow.

Keep the host strong.

Use deterministic modules for mechanical work.

Use the Evidence Specialist for bounded human-meaning judgment.

Use Howard to turn validated evidence work into useful Context, not to invent the evidence graph.

Do not require SQLite when the Intent packet already contains enough information.

Do not let a convenient model output silently become durable state.

Do not collapse Intent, evidence, and Howard interpretation into one rewritten blob.

Do not call a schema-valid model output "true" merely because it parsed.

Do not discard conflicts or unresolved state just to make the handoff look complete.

Do not spend another adapter slot until independent testing proves a distinct learned skill is missing.

The goal of this prototype is not maximum intelligence in one call.

The goal is an **accurate, auditable, bounded Context handoff whose inputs, evidence, interpretation, uncertainty, and provenance remain visible all the way through the slice.**

**END OF CONTEXT PROTOTYPE BUILD SPEC**
