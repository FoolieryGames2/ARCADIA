---
title: "A.R.C.A.D.I.A. v0.1 — Canonical Recipe Contract"
project: "A.R.C.A.D.I.A."
version: "0.1-prototype"
checkpoint_date: "2026-08-29"
document_role: "recipe-contract"
source_path: "recipes/R3_DECISION_V0_1.md"
source_sha256: "ee3621034dd91f26782a4dc3608cd6083ff6b6df63843ee3cf277a3e7372b177"
source_bytes: 46193
source_integrity: "preserved"
tags:
  - "arcadia/v0-1"
  - "type/recipe"
  - "status/frozen"
aliases:
  - "R3_DECISION_V0_1.md"
  - "A.R.C.A.D.I.A. v0.1 — Canonical Recipe Contract"
---

> [!info] Obsidian navigation
> **Checkpoint role:** `recipe-contract`  
> **Frozen source:** `recipes/R3_DECISION_V0_1.md` · SHA-256 `ee3621034dd91f26…`  
> **Command center:** [[ARCADIA v0.1 - Command Center]]  
> **Connected:** [[01_ARCADIA_V0_1_FULL_PROJECT_CHECKPOINT]] · [[03_ARCADIA_V0_1_GLOBAL_CONTRACTS_AND_INVARIANTS]] · [[04_ARCADIA_V0_1_AAE_CONTRACT_REGISTRY_AND_SERIALIZATION]] · [[R2_CONTEXT_V0_1]] · [[R4_TOOL_EXECUTION_V0_1]] · [[ARCADIA_V0_1_FULL_PIPELINE_AAE_REFERENCE_5_SLICES]]

<!-- OBSIDIAN_LAYER_END — ORIGINAL SOURCE CONTENT BEGINS BELOW -->

# A.R.C.A.D.I.A. v0.1 — Canonical Recipe Contract

**v0.1 integration status:** The detailed semantic recipe body below is carried forward from the final pre-v0.1 trust/recovery specification because R3 intentionally did not change semantic recipe ownership. It is now governed by the v0.1 common runtime/AAE/source/recovery/trace/performance contracts in this bundle.

**Conflict rule:** if this carried-forward body contains older wording about adapter loading, generic adapter runtime, source-quality being unresolved, trace retention, crash replay, global sampling, handwritten AAE framing, or model-call necessity, the v0.1 system documents `01`–`09` supersede that wording. Semantic recipe responsibilities, artifacts, edge cases, and tests remain authoritative unless explicitly superseded.

---

# A.R.C.A.D.I.A. DECISION RECIPE
## Prototype Build Specification — Command-Window Reference
**Status:** LOCKED PROTOTYPE DESIGN  
**Scope:** DECISION ONLY  
**Date:** 2026-08-28  
**Parents:** `HOWARD_INTENT_RECIPE_PROTOTYPE_BUILD_SPEC_2026-08-28.md`, `HOWARD_CONTEXT_RECIPE_PROTOTYPE_BUILD_SPEC_2026-08-28.md`  
**Next Stage:** Tool / Execution Recipe  
**Purpose:** Archive-ready source-of-truth specification for implementing and independently testing A.R.C.A.D.I.A.'s Decision recipe. Decision receives the immutable Intent requirement backbone plus validated active Context, determines what work still needs to happen, and produces a validated work graph for Execution without performing any operation itself.

---

> **CONFIRMED LOGIC INTEGRATION — R2 — 2026-08-28**  
> This R2 document integrates the confirmed trust/recovery logic locked after the AAE five-slice review: single-source AAE/runtime/training contracts, base-model baselining, full trace capture with a training-data firewall, packet-projection testing, aggregate loop telemetry, durable-provisional semantic Persistence with next-turn review, controlled user memory correction, deterministic-first semantic support, and mode-specific Howard evaluation.  
> **Source-quality / source-authority ranking is intentionally NOT defined by this update. It remains a separate required design lane.**


# 0. CORE RULE

Decision answers one question:

> **Given the authoritative Intent requirements and the grounded Context currently active, what work actually needs to happen next?**

Intent remains the authority for what the user communicated.

Context remains the authority for what grounded state is currently available.

Decision is the first recipe allowed to convert those two things into an explicit downstream work plan.

Decision does **not** execute the plan.

The permanent requirement backbone remains:

```text
R001
R002
R003
...
```

Decision creates subordinate work IDs:

```text
W001
W002
W003
...
```

A `Wxxx` exists only because it serves one or more authoritative `Rxxx` requirements.

Decision may never create a replacement requirement merely because later evidence or planning exposed a more useful term or intermediate need.

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
EXECUTION / TOOLS
  Perform authorized work.
       |
       v
RECONCILIATION
  What did returned work actually establish?
       |
       v
PERSISTENCE
       |
       v
COMPLETION
       |
       v
RESULT
```

Decision is the boundary between:

```text
WHAT IS NEEDED
```

and:

```text
DOING IT
```

That boundary is strict.

---

# 2. DECISION MUST NOT REINTERPRET THE USER

Execution must never need to ask:

> "What did the user really want?"

That work is upstream.

Decision receives already-created authoritative requirement records and makes a plan against them.

Decision may identify that a requirement is blocked or insufficiently grounded. It may not silently rewrite the requirement into something easier to execute.

Invalid:

```text
R001:
Find current information about project X.

Decision silently changes it to:
Explain project X from memory.
```

Valid:

```text
R001:
Find current information about project X.

disposition:
WORK_REQUIRED

needed_work:
current external information retrieval
```

---

# 3. DECISION PROTOTYPE SPECIALISTS — LOCKED

The prototype uses exactly **two Decision adapters**.

```text
[ADAPTER 1]
REQUIREMENT ASSESSOR
       |
       v
per-requirement need records
       |
       v
[ADAPTER 2]
PLAN COMPOSER
       |
       v
shared work graph
```

There is no Decision critic adapter in the prototype.

There is no router adapter.

There is no tool-specific adapter.

The host performs every deterministic legality, schema, identity, graph, and authority check.

A learned critic may be considered later only if independent testing proves a recurring semantic failure class that deterministic validation cannot catch.

---

# 4. KV / MODEL STATE RULE

Clear model KV/attention state at every adapter boundary.

Adapters may remain loaded/warm if the runtime allows it.

Explicit structured artifacts survive.

Hidden adapter state does not.

```text
REQUIREMENT ASSESSOR
       |
       | structured assessment artifacts
       v
CLEAR KV
       |
       v
PLAN COMPOSER
       |
       | structured Decision handoff
       v
CLEAR KV
```

Each Decision run must be independently reproducible from the explicit packet supplied by the host.

---

# 5. ID NAMESPACE RULES

Existing upstream namespaces remain unchanged.

Recommended new namespaces:

```text
R001     authoritative Intent requirement
C001     Context point
L001     Context lane
DR001    Decision run
A001     Requirement assessment artifact
W001     Decision work item
DN001    Derived Need created downstream after discovery
TRQ001   Tool request created during Execution
REC001   Host tool receipt
```

Important collision rules:

```text
Txxx remains available to Intent term candidates.
Dxxx remains available to Context direct-input objects.
```

Therefore the Decision/Tool prototype must **not** reuse `Txxx` for tool requests or `Dxxx` for discoveries.

Human-readable IDs may be backed by host UUIDs.

The host owns all IDs.

Models may reference supplied IDs but may not mint authoritative IDs unless the host explicitly provides a temporary placeholder mechanism that is canonicalized before acceptance.

Prototype recommendation: the host allocates IDs before each specialist call where practical.

---

# 6. DECISION INPUT CONTRACT

Decision receives a bounded host-assembled packet.

Conceptual top-level input:

```text
DECISION_INPUT

turn
  turn_id

intent_basis
  intent_artifact_id
  intent_revision
  intent_hash
  authoritative requirements
  relevant source spans
  unresolved items
  interaction metadata when needed downstream

context_basis
  context_run_id
  context_version
  context_handoff_hash
  active Context lane revisions
  active Context points
  conflicts
  unresolved grounded state
  provenance references

capability_basis
  capability_registry_version
  capability summary / exact registry according to specialist stage

prior_decision_state
  optional on re-entry

reentry_basis
  optional
  trigger type
  trigger refs
  affected requirement IDs
  affected Context lane IDs

decision_scope
  exact Rxxx IDs permitted to change during this Decision run
```

The original Intent packet is never replaced by a summary.

Context is never flattened into a lossy free-form paragraph that discards lane provenance.

---

# 7. UPSTREAM INTEGRITY PRECHECK

Before any Decision adapter runs, host validation must confirm:

```text
turn ID exists
Intent artifact exists
Intent hash matches
Context handoff exists
Context hash matches
all in-scope Rxxx IDs exist
all supplied Cxxx refs exist
all active lane revisions are host-valid
no superseded Context revision is presented as active
capability registry version exists
Decision scope is non-empty unless a zero-scope diagnostic run is intentional
```

If upstream integrity fails, no model should be asked to "work around" the defect.

The host records a Decision-stage upstream failure and routes according to runtime policy.

---

# 8. ADAPTER 1 — REQUIREMENT ASSESSOR

## Core question

> **For this exact requirement, given the currently grounded Context, what is still needed before downstream stages can legitimately satisfy it?**

The Assessor works requirement-first.

It does not plan the whole turn at once.

---

# 9. REQUIREMENT ASSESSOR INPUT

For one requirement, supply only the bounded state needed to judge it.

Recommended input:

```text
assessment_id
turn_id
requirement
  requirement_id
  authoritative requirement text/structure
  source refs
  relevant Intent metadata

relevant_context
  selected active Context points
  conflict refs
  unresolved refs
  lane revision refs

capability_summary
  available work classes
  unavailable work classes when relevant
  persistence capability existence as a stage fact

prior_requirement_state
  optional on re-entry

trigger
  INITIAL
  CONTEXT_REVISION
  DISCOVERY
  REPAIR_RESULT
  DOWNSTREAM_RECONCILIATION
```

The host should not flood one requirement assessment with unrelated Context merely because it exists.

---

# 10. REQUIREMENT DISPOSITIONS — LOCKED PROTOTYPE VOCABULARY

Each in-scope requirement receives one current primary disposition:

```text
READY
WORK_REQUIRED
BLOCKED
PERSISTENCE_REQUIRED
```

These are Decision dispositions, not final Completion statuses.

They answer what must happen **next**.

---

# 11. READY

`READY` means no new external/runtime work is currently necessary for the requirement to proceed downstream.

Examples:

- Intent + Context already contain the needed grounded facts;
- the requirement is purely conversational and requires no tool;
- required prior work has already been reconciled into active Context;
- the requirement is ready for later Completion/Result judgment.

`READY` does **not** mean:

```text
SATISFIED
```

Only Completion later assigns terminal requirement status.

---

# 12. WORK_REQUIRED

`WORK_REQUIRED` means one or more observable runtime operations must occur before the requirement can be completed.

Examples:

```text
current external search
Wiki/reference lookup
Load File
Save File
a future application action
a future code execution lane
future specialist operation with an observable artifact
```

The Assessor describes the missing work semantically.

It does not execute it.

---

# 13. BLOCKED

`BLOCKED` means Decision cannot currently produce a legitimate executable path for the requirement.

Required block reason vocabulary:

```text
USER_INFORMATION_NEEDED
MISSING_CONTEXT
CAPABILITY_UNAVAILABLE
INVALID_UPSTREAM_STATE
```

Additional host-controlled reasons may be added later by versioned schema change.

Examples:

```text
BLOCKED / USER_INFORMATION_NEEDED
```

The user is the only source of a required missing value.

```text
BLOCKED / MISSING_CONTEXT
```

A specific Context lane is incomplete or invalid and should be repaired/re-entered.

```text
BLOCKED / CAPABILITY_UNAVAILABLE
```

The required work is understood but no registered current capability can perform it.

```text
BLOCKED / INVALID_UPSTREAM_STATE
```

The supplied requirement/Context basis is structurally unsafe.

Minor uncertainty is not automatically a blocker.

---

# 14. PERSISTENCE_REQUIRED

`PERSISTENCE_REQUIRED` means no ordinary Execution work is currently required and the remaining obligation belongs to the separate Persistence recipe.

Decision does not write SQLite.

Decision does not create a normal SQLite tool request.

If a requirement needs ordinary work first and durable persistence afterward, use:

```text
disposition: WORK_REQUIRED
post_work_obligations:
  - PERSISTENCE
```

After the work is reconciled, a scoped Decision re-entry may produce:

```text
disposition: PERSISTENCE_REQUIRED
```

This keeps the spine ordered.

---

# 15. REQUIREMENT ASSESSOR OUTPUT CONTRACT

Recommended conceptual output:

```json
{
  "assessment_id": "A001",
  "requirement_id": "R001",
  "disposition": "WORK_REQUIRED",
  "basis_refs": ["C004", "C007"],
  "need_summary": "Current external evidence is required to establish the requested fact.",
  "work_needs": [
    {
      "work_type": "CURRENT_EXTERNAL_INFORMATION",
      "goal": "Establish the current operating hours for the requested location.",
      "evidence_target": [
        "current hours",
        "correct location identity",
        "date/freshness appropriate to the request"
      ]
    }
  ],
  "block_reason": null,
  "block_detail": null,
  "post_work_obligations": [],
  "confidence": "high"
}
```

A `READY` output has an empty `work_needs` array.

A `BLOCKED` output must include `block_reason`.

A `PERSISTENCE_REQUIRED` output must not invent a SQLite operation.

---

# 16. REQUIREMENT ASSESSOR HARD PROHIBITIONS

The Assessor does not:

- execute tools;
- produce tool syntax;
- create host receipts;
- write SQLite;
- modify the authoritative `Rxxx`;
- create new `Rxxx` IDs;
- claim a requirement is terminally satisfied;
- merge requirements;
- build cross-requirement dependency graphs;
- fabricate missing Context;
- turn a downstream discovery into retroactive user Intent.

---

# 17. HOST VALIDATION AFTER EACH ASSESSMENT

Required deterministic checks:

```text
JSON parse
JSONSchema
assessment ID validity
requirement ID exact match
requirement is inside Decision scope
basis refs exist
basis refs are allowed for this assessment
allowed disposition enum
allowed block reason enum
WORK_REQUIRED has at least one work need
READY has no required work need
BLOCKED has block reason
PERSISTENCE_REQUIRED does not request SQLite execution
no unknown Rxxx IDs
bounded output size
```

Semantic disagreement is not the same as malformed output.

Host validation answers legality and structural integrity, not whether the model's planning judgment is philosophically ideal.

---

# 18. ASSESSOR REPAIR

A malformed assessment may receive a bounded surgical repair prompt.

Prototype hard limit:

```text
maximum repair attempts per model boundary: 2
```

Repair packet includes:

- original exact bounded input;
- previous invalid output;
- exact host validation errors;
- instruction to repair only the invalid artifact.

Examples of repairable errors:

```text
unknown Context ref
illegal disposition enum
missing block reason
missing evidence target
extra unsupported field under strict schema
```

Do not reprompt merely because the outcome is inconvenient.

A valid `BLOCKED` result is not a parser failure.

---

# 19. ADAPTER 2 — PLAN COMPOSER

## Core question

> **Across all validated in-scope requirement assessments, what is the smallest legitimate shared work graph that advances the requirements without losing requirement ownership?**

The Plan Composer sees validated assessment artifacts together.

It is allowed to reason across requirements.

This is where duplicate work can be merged.

---

# 20. PLAN COMPOSER INPUT

Recommended packet:

```text
turn_id
Decision run ID
Decision scope
Intent basis refs
Context handoff refs
validated requirement assessments
exact capability registry
prior active work state when re-entering
completed/superseded work refs when relevant
trigger / re-entry basis
```

The exact capability registry supplied here is host-owned runtime state.

The adapter learns how to interpret a registry.

It does not memorize which tools permanently exist.

---

# 21. CAPABILITY REGISTRY CONTRACT

Prototype registry should describe current capabilities explicitly.

Initial capability examples:

```text
google_search
wiki_lookup
load_file
save_file
```

SQLite persistence is represented as a downstream stage capability, not an ordinary Execution tool.

Recommended registry metadata:

```text
capability_id
capability_version
capability_class
work_types_supported
operation_kinds
read_or_write
side_effect_class
input_schema_ref
receipt_schema_ref
availability
restrictions
freshness_characteristics when relevant
```

Decision may select only currently registered and available capabilities.

Unknown capabilities are invalid.

---

# 22. WORK TYPE AND CAPABILITY ARE DIFFERENT

This distinction is locked.

Decision first identifies **what kind of work is needed**.

Then it identifies **which current capability can perform that work**.

Example:

```text
work_type:
CURRENT_EXTERNAL_INFORMATION

preferred_capability_id:
google_search
```

Do not train the adapter to equate:

```text
current information = Google
```

Future registries may add other search providers without retraining the semantic meaning of `CURRENT_EXTERNAL_INFORMATION`.

---

# 23. INITIAL WORK TYPE VOCABULARY

Recommended prototype values:

```text
CURRENT_EXTERNAL_INFORMATION
REFERENCE_INFORMATION
LOAD_EXTERNAL_FILE
SAVE_USER_FILE
```

This list is versioned and intentionally small.

Future recipes/capabilities may add work types without changing the requirement backbone.

SQLite is excluded.

---

# 24. WORK ITEMS

The Plan Composer creates `Wxxx` work items.

A work item represents one coherent runtime operation or one coherent observable specialist operation.

A work item is not every internal thought.

Create `Wxxx` for work such as:

```text
Google/search operation
Wiki lookup
Load File
Save File
future executable specialist job
```

Do not create `Wxxx` merely for:

```text
think about result
compare ideas internally
consider relevance
write final prose
```

Those belong to recipes that own those semantic functions.

---

# 25. WORK ITEM CONTRACT

Recommended work item shape:

```json
{
  "work_id": "W001",
  "requirement_ids": ["R001", "R003"],
  "assessment_refs": ["A001", "A003"],
  "work_origin": "ORIGINAL",
  "work_type": "CURRENT_EXTERNAL_INFORMATION",
  "goal": "Establish the current official operating hours.",
  "preferred_capability_id": "google_search",
  "query_hint": "official operating hours for [resolved entity] [requested date]",
  "input_refs": ["C004", "C009"],
  "dependency_work_ids": [],
  "parallel_group": "PG001",
  "side_effect_class": "READ_ONLY",
  "evidence_target": [
    "correct entity identity",
    "current operating hours",
    "freshness appropriate to requested date"
  ],
  "expected_receipt_class": "INFORMATION_RECEIPT",
  "post_work_obligations": []
}
```

`query_hint` is a semantic hint, not proof that execution occurred.

---

# 26. WORK ORIGIN VOCABULARY

Every work item records why it exists.

```text
ORIGINAL
REPAIR
DISCOVERY
```

### ORIGINAL

Directly planned from an original requirement and active Context.

### REPAIR

Created because prior attempted work was malformed, rejected, or failed in a way that justifies a new planned operation.

### DISCOVERY

Created because valid downstream evidence revealed a legitimate new need required to finish an existing requirement.

Discovery is **not** automatically repair.

---

# 27. MULTI-REQUIREMENT WORK MERGING

One work item may serve several requirements.

Example:

```text
R001: Find library hours.
R002: Determine whether it is open at 10 AM.
R003: Determine whether toddler access is allowed.
```

The Assessor may independently identify related information needs.

The Plan Composer may create:

```text
W001
serves:
  R001
  R002

W002
serves:
  R003
```

or one broader retrieval only if a single coherent operation can legitimately target all required evidence.

Do not duplicate operations simply because several `Rxxx` IDs exist.

Do not over-merge unrelated work merely to minimize tool count.

---

# 28. ONE REQUIREMENT MAY NEED MULTIPLE WORK ITEMS

Example:

```text
R001:
Compare current official information with a reference overview.
```

Decision may create:

```text
W001 -> current external search
W002 -> Wiki/reference lookup
```

Both serve `R001`.

This is normal.

---

# 29. DEPENDENCY GRAPH

Decision produces a graph, not merely a flat list.

Example:

```text
W001 Load File
   |
   +--> W002 Google search using value established by loaded file
   |
   +--> W003 Wiki lookup using value established by loaded file
```

Work item dependencies are logical requirements.

The host later decides actual scheduling.

The Plan Composer may propose:

```text
dependency_work_ids
parallel_group
```

The host validates graph legality.

---

# 30. DEPENDENCY GRAPH VALIDATION

Reject:

- cycles;
- self-dependency;
- unknown `Wxxx` refs;
- dependencies outside the authorized active Decision graph;
- a dependency on work already marked superseded-before-execution unless a new active work item replaces it;
- side-effect ordering that violates registered capability constraints.

Acyclicity is deterministic host logic.

---

# 31. PARALLELISM

Decision may mark independent work as parallelizable.

Example:

```text
W001 Google official source search
W002 Wiki reference lookup

parallel_group: PG001
```

The model does not command threads/processes.

The host decides whether resources and tool policies allow actual concurrency.

---

# 32. EVIDENCE TARGETS

Every information-producing work item must state what information/result would be useful enough for Reconciliation to judge.

Example:

```text
evidence_target:
  - current operating hours
  - correct Wellsburg library identity
  - source freshness appropriate to today
```

Do not use only:

```text
success = tool call returned HTTP 200
```

There are separate questions:

```text
EXECUTION QUESTION
Did the operation run and return a host receipt?

RECONCILIATION QUESTION
Did the returned evidence establish the target Decision needed?
```

Decision defines the target.

Execution reports what happened.

Reconciliation judges what it established.

---

# 33. SIDE-EFFECT CLASSIFICATION

Initial classes:

```text
READ_ONLY
EXTERNAL_WRITE
```

Examples:

```text
google_search -> READ_ONLY
wiki_lookup   -> READ_ONLY
load_file     -> READ_ONLY
save_file     -> EXTERNAL_WRITE
```

SQLite durable internal write is owned by Persistence, not Decision/Execution tools.

A work item with a side effect must trace to a legitimate `Rxxx` requirement or explicit post-work obligation.

The host rejects unrelated writes.

---

# 34. PLAN COMPOSER OUTPUT — DECISION HANDOFF

Recommended top-level shape:

```text
DECISION_HANDOFF

Decision metadata
  decision_run_id
  revision
  trigger
  scope

basis
  turn_id
  intent artifact/revision/hash
  context run/version/hash
  capability registry version

requirement_decisions
  one current record per in-scope Rxxx

work_items
  Wxxx records

graph
  dependencies
  parallel groups

blocked_requirements

persistence_obligations

validation_summary

provenance
```

---

# 35. REQUIREMENT COVERAGE INVARIANT

Every in-scope requirement must leave Decision accounted for.

Example:

```text
R001 -> READY
R002 -> W001
R003 -> W001 + W002
R004 -> BLOCKED / CAPABILITY_UNAVAILABLE
R005 -> PERSISTENCE_REQUIRED
```

No requirement may disappear because the planner forgot it.

This is a hard host gate.

---

# 36. PLAN COMPOSER HARD PROHIBITIONS

The Plan Composer does not:

- execute Google;
- execute Wiki;
- load files;
- save files;
- write SQLite;
- fabricate host receipts;
- claim a tool succeeded;
- change `Rxxx` text;
- create replacement `Rxxx` requirements;
- rewrite Context;
- declare terminal Completion status;
- produce the final user answer;
- invent unavailable tools;
- silently convert a discovered term into original Intent.

---

# 37. HOST VALIDATION AFTER PLAN COMPOSER

Minimum host gates:

```text
JSON parse
JSONSchema
Decision run ID
Decision scope
upstream hash integrity
requirement coverage
requirement ID validity
assessment ref validity
Context ref validity
work ID uniqueness
work origin enum
work type enum
capability registry validity
capability availability
work-type/capability compatibility
dependency graph validity
parallel group validity
side-effect authority
evidence target presence
receipt-class validity
post-work obligation validity
bounded output
safe_for_execution
```

Do not collapse this into one generic `valid` boolean in diagnostics.

Recommended diagnostics:

```text
host_valid
semantic_plan_status
safe_for_execution
```

---

# 38. DECISION REPAIR

Plan Composer structural failures receive a surgical repair packet.

Prototype hard limit:

```text
maximum repair attempts: 2
```

Examples:

```text
W004 references unknown R009
W002 selected unavailable capability
R003 is missing a disposition
W006 creates dependency cycle
W007 is EXTERNAL_WRITE but no requirement authorizes a write
```

The repair model receives:

- original bounded Plan Composer input;
- previous invalid output;
- exact host validation failures.

The host may make only deterministic mechanical repairs that cannot change semantics.

Examples allowed:

```text
calculate hash
assign host timestamp
canonicalize list ordering
remove exact duplicate reference
```

Examples not allowed:

```text
replace Google with Wiki because host thinks it is better
rewrite query meaning
invent a missing user goal
```

---

# 39. DECISION FAILURE CLASSES

Initial diagnostic vocabulary:

```text
INVALID_MODEL_OUTPUT
UNKNOWN_REQUIREMENT_REFERENCE
UNKNOWN_CONTEXT_REFERENCE
UNKNOWN_CAPABILITY
CAPABILITY_UNAVAILABLE
ILLEGAL_SIDE_EFFECT
DEPENDENCY_CYCLE
MISSING_REQUIREMENT_COVERAGE
UNRESOLVED_REQUIRED_GROUNDING
UPSTREAM_INTEGRITY_FAILURE
DECISION_REPAIR_EXHAUSTED
```

These are runtime/recipe states.

Completion later decides how they affect each requirement's terminal status.

---

# 40. NO-WORK DECISION IS A NORMAL PASS

A Decision run may produce zero work items.

Example:

```text
R001 -> READY
R002 -> READY

work_items: []
```

This is not a failure.

The pipeline may continue through a zero-operation Execution stage so stage accounting remains consistent.

---

# 41. DISCOVERY IS NOT INTENT

A term or fact discovered during valid downstream work was not necessarily communicated by the user.

Therefore it must not be appended to original Intent as though the user said it.

Use a **Derived Need** artifact.

Recommended namespace:

```text
DN001
DN002
...
```

Conceptual example:

```text
R001
  |
  v
W001 -> Google
  |
  v
REC001
  |
  v
Reconciliation discovers useful term "XYZ"
  |
  v
DN001
```

`DN001` remains subordinate to the original requirement.

---

# 42. DERIVED NEED CONTRACT — DOWNSTREAM INTERFACE

Decision does not create a Derived Need from raw tool output on its own.

That belongs to downstream Reconciliation.

Decision must be able to consume a validated `DNxxx` during scoped re-entry.

Recommended fields:

```text
derived_need_id
parent_requirement_ids
created_from_receipt_refs
created_from_context_refs
need_type
useful_term_or_gap
reason_needed
suggested_context_lane
persistence_relevance
status
```

The host validates every provenance reference before Decision receives it.

---

# 43. DISCOVERY LOOP

Canonical future loop:

```text
DECISION
   |
   v
EXECUTION
   |
   v
RECONCILIATION
   |
   | valid evidence exposes a new legitimate need
   v
DN001
   |
   v
HOST validates discovery packet
   |
   +--> reject -> not promoted
   |
   +--> accept
           |
           v
     CONTEXT lane creation/revision when grounding is needed
           |
           v
      HOWARD lane comment
           |
           v
     scoped DECISION re-entry
           |
           v
         new Wxxx
```

The loop is additive.

The original requirement survives unchanged.

---

# 44. OFFICIAL LANE PROMOTION + HOWARD COMMENT — LOCKED INTERFACE RULE

A proposed discovery/re-entry packet is not yet an official Context lane.

Promotion occurs only after host validation.

```text
PROPOSED RE-ENTRY / DISCOVERY PACKET
              |
              v
        HOST VALIDATION
              |
        +-----+-----+
        |           |
      reject      accept
                    |
                    v
           OFFICIAL LANE / REVISION
                    |
                    v
              HOWARD COMMENT
```

When accepted and promoted, the host must attach a bounded Howard lane comment.

Recommended conceptual metadata:

```text
lane_id
lane_revision
status: ACTIVE
parent_lane_id / superseded_revision when applicable
promotion_trigger: DISCOVERY | REPAIR | CONTEXT_UPDATE
trigger_refs
requirement_ids
Howard_comment
```

The Howard comment is human-readable provenance/commentary.

It is **not authority**.

It may explain:

- what new useful term/gap appeared;
- why this lane now exists;
- which `Rxxx` it serves;
- what prior lane it supersedes, if any.

It may not:

- create a requirement;
- claim an unreceived tool success;
- overwrite the user's request;
- become unsupported factual truth.

If host validation rejects the packet, no official lane and no official Howard lane comment are created.

---

# 45. SELECTIVE DECISION RE-ENTRY

Decision must support narrow reruns.

Input includes:

```text
decision_scope:
  [R002]
```

Only those requirements may receive new active Decision state.

Example:

```text
Initial DR001
R001 -> W001
R002 -> W002
R003 -> READY
```

Later evidence affects only `R002`.

```text
DR002 scope = [R002]
R002 -> W004
```

`R001` and `R003` remain untouched.

---

# 46. SUPERSEDED DECISION STATE

Old Decision artifacts are never deleted.

Example:

```text
DR001
R002 -> W002

DR002
R002 -> W004
```

If `W002` had not executed:

```text
W002 state:
SUPERSEDED_BEFORE_EXECUTION
```

If `W002` already executed, its receipt remains historical truth.

A new Decision cannot erase that execution.

---

# 47. EXECUTED RECEIPTS ARE IMMUTABLE FACTS

Decision may supersede planning.

Decision may not supersede the fact that an operation occurred.

Example:

```text
W002 executed
REC017 exists
```

Later Context changes may create new work.

They do not delete `REC017`.

If corrective/compensating work is required, create a new `Wxxx` explicitly.

---

# 48. REPAIR WORK VS DISCOVERED WORK

Keep these distinct in training, logging, and tests.

```text
REPAIR WORK
prior planned/attempted operation failed, was malformed, or was rejected

DISCOVERED WORK
valid operation returned useful information that legitimately exposed a new necessary step
```

Example repair:

```text
Save File rejected because destination argument was malformed.
```

Example discovery:

```text
Two valid searches reveal a newly identified canonical technical term needed for a narrower follow-up search.
```

Do not punish healthy discovery loops as planner errors.

---

# 49. USER INFORMATION BLOCKER

Decision should ask for user input only when the missing information is actually required and cannot be safely obtained from:

- existing Intent;
- active Context;
- an authorized information-producing tool;
- deterministic host state.

Decision itself does not directly converse with the user.

It records the blocker so Completion/Result/runtime interaction policy can handle it.

---

# 50. PERSISTENCE BOUNDARY

Decision may mark:

```text
PERSISTENCE_REQUIRED
```

or:

```text
post_work_obligations: [PERSISTENCE]
```

It does not decide the final SQLite operation type.

The later Persistence recipe owns:

```text
SHOULD SAVE?
   |
   v
NO_SAVE
SAVE_NEW
UPDATE_EXISTING
SUPERSEDE_EXISTING
```

Only host code writes SQLite.

---

# 51. PERMANENT TURN LEDGER ADDITIONS

Decision appends to the root turn ledger.

Recommended additions:

```text
DECISION_RUNS
  DR001
  DR002

REQUIREMENT_ASSESSMENTS
  A001
  A002

ACTIVE_DECISION_BY_REQUIREMENT

WORK_ITEMS
  W001
  W002

WORK_REQUIREMENT_LINKS

WORK_DEPENDENCIES

WORK_CONTEXT_LINKS

DECISION_VALIDATION

BLOCKERS

DERIVED_NEEDS
  appended later by downstream recipes

SUPERSEDED_DECISION_STATE
```

Nothing here replaces:

```text
REQUIREMENTS
  R001
  R002
```

---

# 52. HOST MODULES — RECOMMENDED FOUNDATION

Recommended Python foundation:

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
```

Useful optional support:

```text
networkx
```

`networkx` may be used for development graph validation/visualization, but a simple deterministic acyclic graph validator is sufficient for the prototype and avoids unnecessary dependency weight.

No NLP library is required inside Decision merely because Intent/Context use linguistic support.

---

# 53. RECOMMENDED SOURCE LAYOUT

```text
decision_prototype/
|
+-- decision_prototype.py
+-- README.md
|
+-- decision/
|   +-- models.py
|   +-- assessment.py
|   +-- composer.py
|   +-- capability_registry.py
|   +-- graph.py
|   +-- validation.py
|   +-- provenance.py
|   +-- hashing.py
|   +-- repair.py
|   +-- ledger.py
|
+-- schemas/
|   +-- decision_input.schema.json
|   +-- requirement_assessment.schema.json
|   +-- work_item.schema.json
|   +-- decision_handoff.schema.json
|   +-- derived_need_input.schema.json
|
+-- prompts/
|   +-- requirement_assessor.txt
|   +-- requirement_assessor_repair.txt
|   +-- plan_composer.txt
|   +-- plan_composer_repair.txt
|
+-- fixtures/
|   +-- capabilities.prototype.json
|   +-- examples/
|
+-- tests/
    +-- test_assessor.py
    +-- test_composer.py
    +-- test_requirement_coverage.py
    +-- test_graph.py
    +-- test_capability_validation.py
    +-- test_side_effect_authority.py
    +-- test_reentry.py
    +-- test_discovery_input.py
    +-- test_decision_end_to_end.py
```

---

# 54. JSONSCHEMA GATES

Strict schema gates should use `additionalProperties: false` where accidental field growth would weaken the contract.

Every model boundary:

```text
MODEL OUTPUT
     |
     v
JSON PARSE
     |
     v
JSONSCHEMA
     |
     v
REFERENCE VALIDATION
     |
     v
SEMANTIC-STRUCTURAL HOST CHECKS
     |
     v
SAFE FOR NEXT STAGE
```

---

# 55. COMMAND-WINDOW PROTOTYPE DISPLAY

Recommended compact development trace:

```text
[DECISION DR001]
Basis: Intent rev 1 / Context v1
Scope: R001 R002 R003

[ASSESS R001] WORK_REQUIRED
  need: current external information

[ASSESS R002] WORK_REQUIRED
  need: current external information

[ASSESS R003] READY

[COMPOSE]
  W001 -> R001,R002 -> google_search
  R003 -> READY

[VALIDATION]
  schema ........ PASS
  coverage ...... PASS
  refs .......... PASS
  capabilities .. PASS
  graph ......... PASS
  side effects .. PASS

Decision handoff: SAFE FOR EXECUTION
```

On scoped re-entry:

```text
[DECISION DR002 / DISCOVERY]
Scope: R002
Trigger: DN001
Prior active work preserved outside scope.
```

---

# 56. REQUIRED RUN ARTIFACTS / DEBUG TRACE

Record at minimum:

```text
Decision run ID
trigger
scope
Intent hash/revision
Context hash/version
capability registry version
exact Assessor inputs
exact Assessor outputs
Assessor adapter/version
repair attempts
exact Composer input
exact Composer output
Composer adapter/version
work graph
validation results by gate
latency by model boundary
KV clear confirmation
token counts
active/superseded Decision state
```

This is training/debug state, not ordinary conversational memory.

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


# R2A. AGGREGATE WORK / RE-ENTRY TELEMETRY

Decision contributes to a host-owned aggregate work-budget ledger per `Rxxx`.

Track at minimum:

```text
reentry_count_per_requirement
discovery_depth
repair_depth
total_model_calls_per_requirement
total_work_items_created_per_requirement
total_work_expansion
```

Existing per-stage prototype bounds remain authoritative. Before T4 shadow runtime, the host budget policy must also define finite aggregate ceilings and a deterministic `BUDGET_EXHAUSTED` degradation path. Budget exhaustion preserves accumulated receipts/findings and routes toward Completion as partial/blocked/failed state as appropriate; it never deletes history or fabricates success.

---

# 57. INDEPENDENT SLICE TESTING

Do not judge Decision only end-to-end.

Required independent targets:

```text
test_requirement_assessor
test_assessor_schema_repair
test_plan_composer
test_duplicate_work_merge
test_multi_requirement_work
test_multi_work_requirement
test_dependency_graph
test_parallel_group
test_side_effect_authority
test_no_work_path
test_blocked_paths
test_persistence_handoff
test_scoped_reentry
test_discovery_work
test_repair_work
test_decision_end_to_end
```

---

# 58. REQUIRED FAILURE TESTS

At minimum:

1. Assessor invents `R009`.
2. Assessor cites unknown `C999`.
3. Assessor returns `READY` while also emitting required work.
4. Assessor returns `BLOCKED` without reason.
5. Composer omits one in-scope requirement.
6. Composer invents a capability.
7. Composer selects disabled capability.
8. Composer creates dependency cycle.
9. Composer creates unauthorized Save File work.
10. Composer asks SQLite to execute directly.
11. Composer creates duplicate work unnecessarily.
12. Composer over-merges unrelated evidence targets.
13. Re-entry attempts to modify out-of-scope requirement.
14. Later Decision tries to erase executed receipt history.
15. Discovery term is incorrectly written into original Intent.
16. Discovery packet rejected by host but still becomes a lane.
17. Official promoted lane lacks Howard comment.
18. Howard comment attempts to become factual authority.

---

# 59. EXAMPLE A — DIRECT READY PATH

Incoming:

```text
R001:
Explain the difference between Save File and SQLite persistence.
```

Active Context already contains the architecture definitions.

Assessor:

```text
R001 -> READY
```

Composer:

```text
work_items: []
```

Decision passes.

No fake tool work is created.

---

# 60. EXAMPLE B — TWO GOOGLE WORK ITEMS

Incoming:

```text
R001:
Compare current official information with independent current reporting.
```

Assessor:

```text
WORK_REQUIRED
```

Composer:

```text
W001
work_type: CURRENT_EXTERNAL_INFORMATION
goal: establish official current information
preferred_capability: google_search

W002
work_type: CURRENT_EXTERNAL_INFORMATION
goal: establish independent current corroboration
preferred_capability: google_search

parallel_group: PG001
```

Two Google operations are legitimate because they have distinct evidence targets.

---

# 61. EXAMPLE C — DISCOVERY FOLLOW-UP

Initial:

```text
R001 -> W001 + W002
```

Execution returns:

```text
REC001
REC002
```

Reconciliation later identifies a new useful canonical term and produces:

```text
DN001
parent_requirement_ids: [R001]
created_from_receipt_refs: [REC001, REC002]
reason_needed: narrower term required to finish R001
```

Host validates `DN001`.

A new Context lane/revision is promoted if grounding is required and receives a Howard comment.

Decision re-entry:

```text
DR002
scope: [R001]
trigger: DN001
```

Composer creates:

```text
W003
work_origin: DISCOVERY
```

Original `R001` remains unchanged.

---

# 62. EXAMPLE D — REPAIR IS DIFFERENT

Initial Save File work:

```text
W004
work_origin: ORIGINAL
```

Execution later returns a host rejection because required destination data was malformed.

Reconciliation determines a corrected operation is justified.

Decision re-entry may create:

```text
W005
work_origin: REPAIR
replaces_unexecuted_or_failed_work_ref: W004
```

This is not a discovery.

---

# 63. ADAPTER SUCCESS CRITERIA

## Requirement Assessor passes when it consistently:

- preserves exact requirement identity;
- identifies no-work cases without compulsive tool use;
- identifies genuine missing work;
- distinguishes blockers from optional uncertainty;
- recognizes persistence-bound obligations;
- produces useful evidence targets;
- does not invent tools or results;
- does not rewrite Intent.

## Plan Composer passes when it consistently:

- preserves requirement coverage;
- merges duplicate work appropriately;
- keeps distinct work distinct;
- selects valid registered capabilities;
- constructs legal dependencies;
- recognizes safe parallelism;
- creates traceable `Wxxx` records;
- distinguishes original/repair/discovery work;
- does not execute or fabricate receipts.

---

# 64. PERFORMANCE PHILOSOPHY

Decision should be host-heavy and model-narrow.

Spend model inference on semantic judgments that deterministic code cannot safely replace.

Do not spend adapters on:

- ID generation;
- graph acyclicity;
- enum validation;
- capability existence checks;
- schema parsing;
- hash creation;
- stage routing.

Those belong to host code.

The two adapters should be independently trainable and independently measurable.

---

# 65. BUILD ORDER

Recommended prototype implementation order:

1. Define Decision dataclasses/internal models.
2. Define capability registry prototype.
3. Define Requirement Assessor input/output schemas.
4. Build host upstream integrity validator.
5. Build Assessor runner and bounded repair.
6. Create Assessor independent fixture suite.
7. Define work item and Decision handoff schemas.
8. Build work ID allocation.
9. Build Plan Composer runner.
10. Build requirement coverage validator.
11. Build capability compatibility validator.
12. Build dependency graph validator.
13. Build side-effect authority validator.
14. Build bounded Composer repair.
15. Build permanent turn-ledger append logic.
16. Add scoped Decision re-entry support.
17. Add `DNxxx` input interface only.
18. Add official-lane promotion metadata interface and Howard-comment requirement.
19. Add CLI/PowerShell trace.
20. Run independent slice tests.
21. Run Decision end-to-end tests.
22. Freeze Decision handoff contract before integrating Tool / Execution.

---

# 66. NON-GOALS FOR THIS PROTOTYPE

Do not implement inside Decision:

- Google execution;
- Wiki execution;
- file I/O execution;
- SQLite write logic;
- Reconciliation semantic judgment;
- final Context lane discovery generation;
- Completion terminal statuses;
- final user-facing Result generation;
- a third Decision critic adapter;
- tool-specific adapters;
- a dedicated query-builder adapter.

The interface for downstream discovery/re-entry is defined only so Decision can be built without later architectural breakage.

---

# 67. LOCKED DECISION DESIGN SUMMARY

```text
INPUT
  Immutable Intent requirements
  + active validated Context
  + current host capability registry

ADAPTER 1
  Requirement Assessor
  one Rxxx at a time
  -> READY / WORK_REQUIRED / BLOCKED / PERSISTENCE_REQUIRED

ADAPTER 2
  Plan Composer
  -> shared Wxxx work graph

HOST
  owns IDs
  validates schemas
  validates refs
  validates requirement coverage
  validates capability legality
  validates dependencies
  validates side-effect authority
  controls repair
  controls stage transition

DECISION OUTPUT
  validated executable work graph
  no operation has happened yet

DISCOVERY
  later downstream evidence may create DNxxx
  DNxxx never replaces original Intent
  validated promotion may create/revise a Context lane
  promoted official lane receives a Howard comment
  only affected Rxxx returns to Decision

PERSISTENCE
  only marked as obligation here
  SQLite write remains separate
```

---

# 68. BUILD PHILOSOPHY

Decision should become intelligent by being **precise**, not by becoming broad.

The Requirement Assessor asks a narrow semantic question about one requirement.

The Plan Composer asks a narrow cross-requirement optimization question.

The host owns everything that can be proved mechanically.

The turn ledger grows additively.

Requirements remain authoritative.

Plans may be superseded.

Executed receipts may not be erased.

Discoveries create traceable downstream needs rather than rewriting history.

When these invariants hold, Execution can remain deliberately ignorant of user intent and simply perform the exact authorized `Wxxx` work it receives.
