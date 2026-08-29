# A.R.C.A.D.I.A. v0.1 — Canonical Recipe Contract

**v0.1 integration status:** The detailed semantic recipe body below is carried forward from the final pre-v0.1 trust/recovery specification because R3 intentionally did not change semantic recipe ownership. It is now governed by the v0.1 common runtime/AAE/source/recovery/trace/performance contracts in this bundle.

**Conflict rule:** if this carried-forward body contains older wording about adapter loading, generic adapter runtime, source-quality being unresolved, trace retention, crash replay, global sampling, handwritten AAE framing, or model-call necessity, the v0.1 system documents `01`–`09` supersede that wording. Semantic recipe responsibilities, artifacts, edge cases, and tests remain authoritative unless explicitly superseded.

---

# A.R.C.A.D.I.A. — PERSISTENCE RECIPE
## Prototype Build Specification — Durable Semantic Memory

**Project:** A.R.C.A.D.I.A. — Adaptive Runtime for Compartmentalized Agents, Decisions, Interaction & Automation  
**Recipe:** 6 — Persistence  
**Date:** 2026-08-28  
**Status:** LOCKED PROTOTYPE BUILD DESIGN  
**Parent checkpoint:** `ARCADIA_FULL_PROJECT_CHECKPOINT_R2_2026-08-28.md`  
**Upstream recipes:** Recipe 0 Conversation Resolver, Recipe 1 Intent, Recipe 2 Context, Recipe 3 Decision, Recipe 4 Tool / Execution, Recipe 5 Reconciliation  
**Next stage:** Recipe 7 — Completion  
**Primary database:** `arcadia.sqlite3`

**Purpose:** Define the exact host, model, SQLite, identity, provenance, validation, supersession, failure, testing, and build contracts required to turn validated turn state into durable semantic memory without mixing semantic memory with conversation transcript or technical turn history.

---

> **CONFIRMED TRUST/RECOVERY INTEGRATION — R2 — 2026-08-28**  
> This R2 document integrates the confirmed trust/recovery logic locked after the AAE five-slice review: single-source AAE/runtime/training contracts, base-model baselining, full trace capture with a training-data firewall, packet-projection testing, aggregate loop telemetry, durable-provisional semantic Persistence with next-turn review, controlled user memory correction, deterministic-first semantic support, and mode-specific Howard evaluation.  
> **Source-quality / source-authority ranking is intentionally NOT defined by this update. It remains a separate required design lane.**


# 0. SOURCE BASELINE, AUTHORITY, AND SUPERSESSION POLICY

This specification is the canonical Recipe 6 implementation contract under the full R2 checkpoint.

The following upstream rules remain authoritative:

```text
Stored != injected.
Transcript != semantic memory.
Technical artifact identity != semantic entity identity.
Conversation resolution != Intent.
Context resolution != Intent mutation.
Decision plans work; Execution proves operation reality.
Execution success != semantic success.
Discovery != repair.
Discovery != new Intent.
Persistence obligation != persistence suggestion.
Receipt != claim of truth.
Human-readable IDs != global database identity.
Every durable artifact is traceable.
Every semantic write waits for Persistence.
```

This Persistence specification does not reopen or collapse Recipes 0–5.

Where this document adds a future-facing interface to an upstream recipe, the change is explicitly marked as a **Persistence Entry Patch**.

Primary entry patch:

```text
Intent may nominate memory candidates.
Context may ground those user-origin candidates.
Context may emit advisory persistence candidates for grounded user-provided state.

Reconciliation continues to emit advisory persistence candidates for validated
downstream/tool evidence.

Both remain advisory.
Neither writes SQLite.
```

This preserves the upstream input surface without giving Context or Reconciliation write authority.

---

# 1. CORE RULE

Persistence answers one question:

> **Given validated upstream turn state, existing durable semantic state, and explicit persistence authority, what durable semantic state should change, if anything?**

Persistence is not:

```text
conversation-history selection
general transcript storage
a second Context recipe
a second Reconciliation recipe
a tool executor
a final-answer generator
a terminal requirement judge
a free-form biography writer
a raw text archive
```

Persistence is the only recipe allowed to propose durable semantic mutations.

Only the **Persistence Host** may commit those mutations to SQLite.

---

# 2. POSITION IN THE FULL A.R.C.A.D.I.A. SPINE

```text
[0] CONVERSATION RESOLVER
    What transcript evidence is required?
              |
              v
[1] INTENT
    What did the user communicate?
              |
              v
[2] CONTEXT
    What grounded state do we have?
              |
              v
[3] DECISION
    What work needs to happen?
              |
              v
[4] TOOL / EXECUTION
    What operations actually occurred?
              |
              v
[5] RECONCILIATION
    What did returned work establish?
              |
              v
[6] PERSISTENCE
    What validated state should become durable semantic memory?
              |
              v
[7] COMPLETION
    Which Rxxx requirements are terminally resolved?
              |
              v
RESULT
```

Persistence is downstream of semantic reconciliation because raw tool output must never jump directly into durable memory.

Persistence is upstream of Completion because an explicit requirement such as:

```text
"Remember that..."
"Save this as a durable preference."
"Update what you know about..."
"Forget the old value."
```

is not complete until Persistence resolves the durable obligation.

---

# 3. AUTHORITY MODEL

| Layer | Owns | Must not own |
|---|---|---|
| Conversation Resolver | Minimum sufficient transcript scope | Semantic memory writes |
| Intent | What the user communicated | Durable truth |
| Context | Grounded working state | Durable commit |
| Decision | Persistence obligation recognition | Final memory mutation |
| Execution | External operation reality | SQLite semantic writes |
| Reconciliation | Meaning of execution evidence; downstream persistence relevance | Durable commit |
| Persistence Assessor | Per-item semantic memory judgment | SQL execution, IDs, commit |
| Persistence Composer | Cross-item semantic mutation plan | SQL execution, commit receipt |
| Persistence Host | Identity allocation, memory lookup, validation, transaction, commit sequence, receipt | Free-form semantic invention |
| Completion | Terminal requirement status | Rewriting memory history |

Core system rule:

> **Models judge bounded semantics. The host owns identity, retrieval, legality, schemas, hashes, state transitions, SQL, transactions, concurrency, and durable commit reality.**

---

# 4. THREE RETENTION DOMAINS REMAIN SEPARATE

## 4.1 Conversation transcript

Stores ordinary completed conversation:

```text
exact user message
exact final published A.R.C.A.D.I.A. response
```

Recipe 0 uses this later. Persistence does not choose which transcript turns exist.

## 4.2 Technical turn ledger

Stores:

```text
Recipe artifacts
Rxxx / Cxxx / Wxxx / TRQxxx / RECxxx / EFxxx / DNxxx
validation events
repair events
adapter identities
hashes
timings
debug/training captures
Persistence assessments/plans/receipts
```

This is provenance/debug/replay state. It is not ordinary conversational context.

## 4.3 Durable semantic memory

Stores only Persistence-approved semantic state:

```text
entities
claims
aliases/indexes
claim transitions
conflicts
entity merges
semantic provenance
memory transactions
```

A semantic memory record may cite transcript turns and technical artifacts. It never becomes the transcript itself.

---

# 5. PERSISTENCE ENTRY CONTRACT

Persistence receives one validated handoff containing:

```text
turn_uuid
conversation_uuid

Intent basis
  intent_artifact_uuid
  intent_hash
  authoritative Rxxx

active Context basis
  context_snapshot_uuid
  context_hash
  ready_for_next_stage = true
  active Cxxx refs
  memory snapshot refs used upstream if any

Decision basis
  decision_run_uuid
  decision_hash
  normative persistence obligations[]

Execution basis
  execution_run_uuid/hash
  immutable receipts/unexecuted states when relevant

Reconciliation basis
  reconciliation_run_uuid/hash
  validated EFxxx
  conflicts
  Context re-entry results
  advisory persistence candidates[]

Context-origin advisory persistence candidates[]
  grounded user-origin memory candidates

immutable provenance graph / artifact refs
canonical hash profile
host persistence policy snapshot
```

Persistence rejects the handoff before model inference if any mandatory upstream hash or reference is invalid.

---

# 6. TWO AUTHORITY-SEPARATED INPUT QUEUES

## 6.1 Normative persistence obligations

Origin:

```text
Decision disposition = PERSISTENCE_REQUIRED
or
Decision post_work_obligations contains PERSISTENCE
```

Typical cause:

```text
explicit "remember"
explicit "update what you know"
explicit "save this preference"
explicit "forget/retract this memory"
a user requirement whose remaining work is durable semantic state
```

Conceptual object:

```text
PERSISTENCE_OBLIGATION
obligation_uuid
requirement_ids[]
basis_refs[]
reason
requested_semantic_operation if explicit
state = PENDING
```

Every in-scope normative obligation must leave Persistence with one explicit result:

```text
COMMITTED
NO_CHANGE_NEEDED
REJECTED_BY_POLICY
BLOCKED
FAILED
```

Persistence may not silently ignore a normative obligation.

## 6.2 Advisory persistence candidates

Possible validated origins:

```text
CONTEXT
RECONCILIATION
```

Context candidates are grounded user-origin state. Reconciliation candidates are grounded downstream/tool evidence.

Conceptual object:

```text
PERSISTENCE_CANDIDATE
candidate_uuid
origin: CONTEXT | RECONCILIATION
requirement_ids[]
basis_refs[]
candidate_summary
candidate_kind
source_authority
reason_potentially_durable
suggested_action:
  CONSIDER_SAVE
  CONSIDER_UPDATE
  CONSIDER_SUPERSEDE
  CONSIDER_RETRACT
```

Every candidate may leave Persistence with:

```text
SAVED
UPDATED
SUPERSEDED
RETRACTED
IGNORED
DEFERRED
FAILED
```

A candidate is never a command.

---

# 7. PERSISTENCE ENTRY PATCH P6-01 — GROUNDED USER-ORIGIN CANDIDATES

The Intent design allows memory candidates.

Persistence now defines the concrete downstream path for ordinary user statements:

```text
USER:
"My favorite science-fiction author is Arthur C. Clarke."

        |
        v
INTENT
memory candidate nominated
        |
        v
CONTEXT
grounds what was actually asserted
source class = USER_ASSERTED
        |
        v
CONTEXT_PERSISTENCE_CANDIDATE
authority = ADVISORY
        |
        v
PERSISTENCE
decides SAVE / IGNORE / DEFER / etc.
```

Context does not write SQLite.

Context does not decide final semantic entity identity.

Context only emits a bounded candidate with provenance.

This prevents ordinary user-origin durable facts from being forced through Tool / Execution or Reconciliation merely to become eligible for memory.

---

# 8. EXPLICIT "REMEMBER" RULE

Explicit remember language changes authority, not truth.

Example:

```text
"Remember that my editor preference for this project is VS Code."
```

Correct effect:

```text
Intent creates requirement
Decision emits normative Persistence obligation
Persistence must resolve it explicitly
```

Incorrect effect:

```text
Persistence ignores it because automatic-save heuristic says "low importance."
```

Explicit remember does **not** bypass host policy, identity validation, schema validation, provenance, conflict handling, or transaction safety.

It means the obligation cannot be silently dropped.

---

# 9. PERSISTENCE PROTOTYPE SPECIALISTS — LOCKED

Exactly two new Persistence adapters:

```text
[ADAPTER 1]
PERSISTENCE ASSESSOR
       |
       v
validated per-item semantic memory assessment
       |
       v
CLEAR KV / ATTENTION
       |
       v
[ADAPTER 2]
PERSISTENCE COMPOSER
       |
       v
validated cross-item atomic mutation proposal
```

There is no Persistence critic adapter.
There is no SQL adapter.
There is no entity-only adapter.
There is no preference adapter.
There is no project-memory adapter.

The host performs deterministic retrieval, ID allocation, schema validation, policy validation, transaction simulation, SQL, concurrency checks, hashing, and receipts.

---

# 10. KV / MODEL STATE RULE

Clear model KV/attention state at every Persistence adapter boundary.

Adapters may remain loaded/warm.

Hidden model state is never durable memory.

Only explicit validated structured artifacts are authoritative cross-adapter state.

---

# 11. SEMANTIC MEMORY MODEL — CORE DESIGN

Prototype durable semantic memory uses:

```text
ENTITY
CLAIM
ALIAS / RETRIEVAL INDEX
PROVENANCE
TRANSACTION / TRANSITION HISTORY
```

The model is intentionally general.

Do not begin with dozens of domain-specific tables:

```text
people
dogs
projects
preferences
goals
favorite_foods
devices
software
```

Domain meaning is represented through typed entities and claims.

Specialized tables may be added later only when logs prove a real operational advantage.

---

# 12. TECHNICAL IDENTITY VS SEMANTIC IDENTITY

## 12.1 Technical artifact identity

Existing recipe artifacts use:

```text
artifact_uuid
turn_uuid
recipe_id
artifact_type
short_id
revision
```

Examples:

```text
R001
W001
REC001
EF001
```

Those IDs belong to turn processing.

## 12.2 Semantic identity

Persistent real/project concepts use separate durable semantic UUIDs:

```text
a particular dog
a particular person
A.R.C.A.D.I.A. project
Forever Space project
a specific file/artifact
a specific model/adapter
a stable preference subject
```

Semantic entity identity survives across turns.

Example:

```text
entity_uuid = 6f...
entity_short_id = E000001
entity_type = DOG
```

The UUID is authoritative.

`E000001` is a durable human-readable semantic alias for logs/debugging.

No `Rxxx`, `Cxxx`, `Wxxx`, or transcript turn becomes semantic entity identity.

---

# 13. ENTITY RECORD — STABLE OBJECT, MINIMAL SEMANTICS

An Entity represents the stable thing.

Recommended fields:

```text
entity_uuid
entity_short_id
entity_type
status
merged_into_entity_uuid
created_at
created_turn_uuid
created_memory_commit_seq
retired_at
```

Entity statuses:

```text
ACTIVE
MERGED
RETIRED
```

Mutable facts such as name, location, job, preference, current project state, or configuration normally belong in Claims, not mutable truth columns on the Entity row.

The Entity row says:

```text
E000001 = this particular dog
```

Claims say what is currently or historically true about it.

A host-maintained display label may exist as a retrieval/cache convenience, but it is not authoritative semantic truth.

---

# 14. CLAIM RECORD — DURABLE SEMANTIC ASSERTION

A Claim has:

```text
SUBJECT
PREDICATE
OBJECT
```

Example:

```text
E000001
name
"Bella"
```

Recommended fields:

```text
claim_uuid
claim_short_id
subject_entity_uuid
predicate
object_kind
object_value_json
object_search_text
claim_cardinality
source_authority
status
durability_class
observed_at
effective_from
effective_to
expires_at
created_at
created_turn_uuid
created_memory_commit_seq
```

Claim statuses:

```text
ACTIVE
CONTESTED
SUPERSEDED
RETRACTED
```

Meaning:

```text
ACTIVE
  current durable claim available to normal Context retrieval

CONTESTED
  durable unresolved conflict exists; do not present as clean current truth

SUPERSEDED
  replaced/refined/changed by later accepted state

RETRACTED
  explicitly withdrawn or invalidated; excluded from normal active retrieval
```

---

# 15. CLAIM OBJECT TYPES

Prototype object kinds:

```text
TEXT
NUMBER
BOOLEAN
DATETIME
ENTITY
```

Store typed object in canonical JSON.

Complex information should normally be decomposed into several Claims instead of opaque giant JSON blobs.

Avoid turning semantic memory into arbitrary document storage.

---

# 16. CLAIM CARDINALITY

Each Claim declares:

```text
SINGLE_CURRENT
MULTI_CURRENT
```

Examples:

```text
name -> usually SINGLE_CURRENT within relevant naming scope
current_job -> usually SINGLE_CURRENT
favorite_genres -> may be MULTI_CURRENT
project_uses_library -> may be MULTI_CURRENT
```

The model judges semantic class.

Host validates enum legality and consistency with supplied existing claims.

For `SINGLE_CURRENT`, a new incompatible current value must not commit while the old active value is silently left active.

It must become:

```text
NO_CHANGE
SUPERSEDE
CONTEST
or BLOCK
```

---

# 17. SOURCE AUTHORITY CLASSES

Prototype source classes:

```text
USER_ASSERTED
EXTERNALLY_ESTABLISHED
DERIVED
```

## USER_ASSERTED

The user directly stated the fact, preference, relationship, decision, or correction.

Example:

```text
"My dog's name is Bella."
```

No external search is required to validate a private user assertion as a user assertion.

## EXTERNALLY_ESTABLISHED

Supported by validated external/tool evidence that has passed Reconciliation and required Context grounding.

## DERIVED

A model-derived inference from supplied evidence.

Prototype rule:

> Advisory DERIVED claims are not automatically promoted to durable active fact.

They may be deferred/ignored, or saved later under an explicit policy or normative user-directed requirement that stores them explicitly as derived.

Never silently turn an inference about the user into a user-asserted fact.

---


# 17A. SOURCE CHANNEL / USER CONTROL PROVENANCE — R2 LOCK

`source_authority` continues to express epistemic authority:

```text
USER_ASSERTED
EXTERNALLY_ESTABLISHED
DERIVED
```

R2 adds a separate provenance dimension, `source_channel`, so direct user control is not confused with a different epistemic authority class.

Prototype channel values:

```text
CONVERSATION
DIRECT_USER_MEMORY_CONTROL
TOOL_EVIDENCE
SYSTEM_DERIVED
```

A correction made through the Memory Inspector is normally:

```text
source_authority = USER_ASSERTED
source_channel   = DIRECT_USER_MEMORY_CONTROL
```

This preserves the fact that the user directly controlled their own memory state without inventing a new truth-authority category.

---

# 18. PROVENANCE IS MANDATORY

Every durable semantic Claim must have provenance.

Minimum provenance can include:

```text
source turn UUID
source artifact UUID(s)
source requirement refs
source Context refs
source EF/REC refs when external
source persistence obligation/candidate ref
source authority class
source hashes
timestamp
```

No provenance means no promotable Claim.

Do not copy giant raw tool payloads into semantic memory. Reference immutable technical/evidence artifacts that already preserve them.

---

# 19. ALIASES ARE RETRIEVAL STRUCTURES, NOT PRIMARY TRUTH

Recommended alias fields:

```text
alias_uuid
entity_uuid
alias_text
normalized_alias
alias_kind
alias_status
source_claim_uuid
created_memory_commit_seq
retired_memory_commit_seq
```

Prototype kinds:

```text
NAME
NICKNAME
PROJECT_NAME
HISTORICAL_NAME
IDENTIFIER
USER_LABEL
```

Statuses:

```text
CURRENT
HISTORICAL
SEARCH_ONLY
RETIRED
```

After a real rename:

```text
Fred -> CURRENT
Bella -> HISTORICAL
```

After correcting a mistaken old name:

```text
Fred -> CURRENT
Bella -> SEARCH_ONLY
```

Claims remain semantic authority. Aliases are retrieval indexes derived from accepted semantic state.

---

# 20. SUPERSESSION IS APPEND + TRANSITION, NOT DESTRUCTIVE OVERWRITE

Never overwrite an old Claim in place to pretend it never existed.

Create a new Claim and a transition.

General path:

```text
M000001 ACTIVE
        |
        | new validated state
        v
M000002 ACTIVE

transition:
M000001 -> M000002
```

Old Claim status changes through the same atomic Persistence transaction.

Historical provenance remains addressable.

---

# 21. CHANGE VS CORRECTION — LOCKED DISTINCTION

This distinction is mandatory.

## 21.1 CHANGE

Example:

```text
"My dog's name is Bella."
...
"I changed my dog's name to Fred."
```

The old claim may have been true in an earlier interval.

Correct semantic result:

```text
E000001 remains the same dog.

M000001:
  predicate = name
  object = Bella
  status = SUPERSEDED
  transition_kind = CHANGE
  effective_to = rename time if known

M000002:
  predicate = name
  object = Fred
  status = ACTIVE

Alias Bella -> HISTORICAL
Alias Fred  -> CURRENT
```

## 21.2 CORRECTION

Example:

```text
"My dog's name is Bella."
...
"Actually I was wrong. Her name has always been Fred."
```

The old value should not be treated as historical truth.

Correct semantic result:

```text
M000001:
  Bella
  status = SUPERSEDED
  transition_kind = CORRECTION

M000002:
  Fred
  status = ACTIVE

Alias Fred  -> CURRENT
Alias Bella -> SEARCH_ONLY
```

No historical validity interval is inferred for Bella.

The technical ledger still preserves that Bella was previously asserted.

Semantic memory does not claim it was historically true.

---

# 22. CLAIM TRANSITION KINDS

Prototype transition vocabulary:

```text
CHANGE
CORRECTION
REFINEMENT
DUPLICATE_COLLAPSE
RETRACTION
CONFLICT_RESOLUTION
```

Definitions:

```text
CHANGE
  state actually changed over time

CORRECTION
  old claim was wrong/mistaken

REFINEMENT
  new claim is a more precise compatible replacement

DUPLICATE_COLLAPSE
  semantically duplicate claim removed from active view without changing truth

RETRACTION
  old claim explicitly withdrawn without a replacement

CONFLICT_RESOLUTION
  contested claims resolved in favor of a new/current disposition
```

Host validates enum and refs. Adapter semantics determine which kind applies.

---

# 23. TEMPORAL / FRESHNESS MODEL

A persistent fact can be durable enough to remember but still become stale.

Recommended fields:

```text
observed_at
effective_from
effective_to
expires_at
durability_class
```

Durability classes:

```text
STABLE
SEMI_STABLE
TIME_BOUNDED
EVENT_HISTORY
```

Examples:

```text
dog identity/name -> STABLE or SEMI_STABLE
project architecture decision -> SEMI_STABLE
today's operating hours -> TIME_BOUNDED
a release event that occurred -> EVENT_HISTORY
```

Context retrieval must not treat an expired `TIME_BOUNDED` claim as current truth merely because it remains historically stored.

Persistence may save a time-sensitive external claim only with suitable temporal metadata.

---

# 24. AUTOMATIC ADVISORY SAVE POLICY — CONSERVATIVE PROTOTYPE

Advisory candidates should generally be considered durable when they are specific, grounded, entity-resolvable, and plausibly useful across future turns.

High-value prototype categories:

```text
stable identity
stable relationship
explicit durable preference
project decision
project configuration
ongoing goal
ongoing constraint
named artifact identity
important user-established correction
important externally established project fact
durable workflow rule
```

Normally ignore or defer:

```text
conversational filler
one-off phrasing
transient emotional state
temporary immediate-task detail with no continuing use
raw copied web text
raw search result
unsupported inference
speculative user trait
duplicate existing memory
incidental noun/entity
short-lived external fact with no future value
```

A normative explicit remember obligation overrides the importance heuristic but not policy or truth/provenance rules.

---

# 25. SENSITIVE / SECRET MATERIAL POLICY HOOK

Persistence must have a host-owned policy snapshot.

At minimum the prototype rejects automatic semantic persistence of obvious credentials/secrets:

```text
passwords
authentication tokens
private keys
one-time codes
PINs
session secrets
```

Normative requests attempting to store prohibited secret material resolve:

```text
REJECTED_BY_POLICY
```

The model does not override host policy.

Other privacy/sensitivity categories may be added through versioned policy without changing the core Persistence architecture.

---

# 26. ENTITY RESOLUTION BEFORE WRITE

Persistence must not create a new Entity merely because a new name string appears.

Before Assessor inference, the host performs bounded memory lookup.

Example candidate:

```text
"My dog's name is Fred."
```

Host may retrieve candidate entities using:

```text
current aliases
historical aliases
search-only aliases
entity type
related active claims
recent semantic provenance
FTS result ranking
```

Assessor entity-resolution outcomes:

```text
MATCH_EXISTING
CREATE_NEW
IDENTITY_AMBIGUOUS
NEEDS_MORE_MEMORY
```

The model may not invent an existing entity UUID that was not supplied.

`CREATE_NEW` causes the host to allocate a new UUID only after the mutation plan validates.

---

# 27. MEMORY LOOKUP SNAPSHOT

Persistence reasoning uses a frozen host-produced semantic memory snapshot.

Recommended metadata:

```text
memory_snapshot_uuid
memory_base_commit_seq
captured_at
query intents
candidate entity UUIDs
candidate entity aliases
active claims
contested claims when relevant
recent claim transitions when relevant
provenance refs
record hashes
snapshot_hash
```

The model sees only bounded relevant memory.

It does not receive the entire semantic database.

---

# 28. BOUNDED MEMORY LOOKUP EXPANSION LOOP

When identity/current-state resolution is insufficient:

```text
ASSESSOR
  -> NEEDS_MORE_MEMORY
       |
       v
HOST validates bounded request
       |
       v
HOST retrieves additional semantic candidates
       |
       v
new frozen snapshot revision
       |
       v
ASSESSOR rerun
```

Prototype bounds:

```text
max_memory_lookup_expansion_cycles_per_item = 2
max_entity_candidates_per_lookup = 8
max_active_claims_per_candidate_entity = host-configured bounded limit
```

On exhaustion:

Normative item:

```text
BLOCKED
reason = IDENTITY_AMBIGUOUS
```

Advisory item:

```text
DEFERRED
reason = IDENTITY_AMBIGUOUS
```

Never create duplicate entities merely to avoid ambiguity.

---

# 29. ADAPTER 1 — PERSISTENCE ASSESSOR

Core question:

> **For this exact persistence obligation/candidate, against this exact frozen existing semantic-memory snapshot and provenance, what durable semantic consequence is justified?**

Assessor works one item at a time.

It does not compose the entire turn.

It does not execute SQL.

---

# 30. PERSISTENCE ASSESSOR INPUT

Recommended packet:

```text
persistence_run_uuid
turn_uuid
item_uuid
item_authority_class: NORMATIVE | ADVISORY
item_origin
requirement_ids[]
exact candidate/obligation content
source authority
basis/provenance refs
relevant active Context refs
relevant EF refs if external
memory_snapshot_uuid/hash
memory_base_commit_seq
bounded entity/claim candidates
host persistence policy summary/hash
```

No unrelated memory flooding.

---

# 31. PERSISTENCE ASSESSOR OUTPUT

Conceptual output:

```text
assessment_short_id: PA001
item_uuid
authority_class

durability_judgment:
  DURABLE
  NOT_DURABLE
  POLICY_BLOCKED
  INSUFFICIENT

entity_resolution:
  MATCH_EXISTING
  CREATE_NEW
  IDENTITY_AMBIGUOUS
  NEEDS_MORE_MEMORY

matched_entity_ref if supplied
proposed_entity_type if CREATE_NEW

semantic_claim_proposals[]
  subject_ref
  predicate
  object_kind
  object_value
  cardinality
  source_authority
  durability_class
  temporal metadata

existing_claim_disposition[]
  existing_claim_ref
  semantic_relation:
    SAME
    CHANGE
    CORRECTION
    REFINEMENT
    CONFLICT
    RETRACTION
    UNRELATED

alias_implications[]

recommended_item_result
reason_codes[]
provenance_refs[]
```

Assessor proposes semantics.

It does not allocate permanent semantic UUIDs.

---

# 32. ASSESSOR HOST VALIDATION

Host validates:

```text
JSON / schema
known item UUID
known requirement refs
known basis refs
known entity refs
known claim refs
all referenced memory rows belong to supplied snapshot
object type enum
claim cardinality enum
source authority enum
durability enum
transition relation enum
no SQL
no terminal Completion status
no transcript mutation
no invented Rxxx
no invented semantic UUID
provenance refs exist
policy-blocked material cannot be marked durable
bounded output
```

Host does not replace semantic judgment with its own preference.

---

# 33. ASSESSOR REPAIR

Prototype default:

```text
maximum Persistence Assessor repair attempts = 2
```

Repair packet contains:

```text
original bounded input
previous invalid output
exact validation errors
```

Do not reprompt because the model validly chose `NOT_DURABLE`, `DEFERRED`, or `BLOCKED`.

Only malformed/illegal output triggers repair.

---

# 34. ADAPTER 2 — PERSISTENCE COMPOSER

Core question:

> **Across all validated Persistence Assessments for this turn, what smallest coherent set of durable semantic mutations should be committed atomically while preserving entity identity, claim history, provenance, conflicts, and obligation coverage?**

Composer may:

```text
merge duplicate candidate effects
reuse one new Entity for several compatible claims
preserve separate entities when identity is not established
sequence claim supersessions
sequence alias changes
create conflict records
resolve explicit retractions
produce per-item resolution results
```

Composer may not execute SQL.

---

# 35. PERSISTENCE COMPOSER INPUT

```text
persistence_run_uuid
turn_uuid
memory_snapshot_uuid/hash
memory_base_commit_seq
validated PAxxx assessments[]
normative obligation list
advisory candidate list
host semantic policy snapshot/hash
existing active/contested claim refs cited by assessments
existing aliases cited by assessments
```

The Composer sees only validated Assessor artifacts.

---

# 36. MUTATION VOCABULARY — SEMANTIC PLAN

Prototype allowed semantic mutation operations:

```text
CREATE_ENTITY
CREATE_CLAIM
SUPERSEDE_CLAIM
RETRACT_CLAIM
SET_CLAIM_CONTESTED
ADD_ALIAS
SET_ALIAS_STATUS
CREATE_CONFLICT
RESOLVE_CONFLICT
MERGE_ENTITY
NO_CHANGE
```

`MERGE_ENTITY` is supported only under strict rules.

The Composer emits mutation intent, not SQL.

---

# 37. PERSISTENCE COMPOSER OUTPUT

Conceptual structure:

```text
persistence_plan_short_id: PP001
persistence_run_uuid
memory_base_commit_seq

item_results[]
  item_uuid
  authority_class
  planned_result
  supporting_assessment_refs

new_entity_proposals[]
  temp_entity_ref
  entity_type
  basis_refs

claim_mutations[]
alias_mutations[]
conflict_mutations[]
entity_merge_mutations[]

transaction_properties
  expected_base_commit_seq
  requires_commit: true|false

provenance_links[]
diagnostics[]
```

Temporary new-entity refs may be used inside the plan:

```text
NEW_E1
NEW_E2
```

The host replaces them with allocated UUIDs only after validation.

---

# 38. OBLIGATION COVERAGE INVARIANT

Every normative obligation must appear exactly once in `item_results`.

Valid:

```text
O1 -> COMMITTED
O2 -> NO_CHANGE_NEEDED
O3 -> BLOCKED
```

Invalid:

```text
O2 disappears because the Composer forgot it.
```

This is a hard host gate.

---

# 39. ADVISORY CANDIDATE COVERAGE

Every advisory candidate must receive explicit disposition in the prototype:

```text
C1 -> SAVED
C2 -> IGNORED
C3 -> DEFERRED
```

This makes training/evaluation measurable and prevents candidates from silently disappearing.

---

# 40. DUPLICATE CLAIM HANDLING

If a proposed Claim is semantically equivalent to an existing active claim:

```text
NO_CHANGE
```

Do not create infinite duplicate memories because the user repeated the fact.

A normative obligation may resolve:

```text
NO_CHANGE_NEEDED
```

because required durable state already exists.

Provenance may append additional support to the existing claim if useful and allowed by policy.

Do not manufacture a new Claim solely to prove the obligation ran.

---

# 41. SINGLE-CURRENT CLAIM UPDATE

Existing:

```text
E000001
M000001:
  name = Bella
  status = ACTIVE
  cardinality = SINGLE_CURRENT
```

New validated statement:

```text
"I changed my dog's name to Fred."
```

Plan:

```text
CREATE_CLAIM NEW_M1:
  subject = E000001
  predicate = name
  object = Fred

SUPERSEDE_CLAIM M000001
  transition_kind = CHANGE
  superseded_by = NEW_M1

SET_ALIAS_STATUS Bella -> HISTORICAL
ADD_ALIAS Fred -> CURRENT
```

All occur in one SQL transaction.

There must never be an externally visible half-state where both names are silently considered clean single-current truth.

---

# 42. CORRECTION UPDATE

Example:

```text
"Actually, Bella was a mistake. Her name has always been Fred."
```

Plan:

```text
CREATE_CLAIM Fred ACTIVE
SUPERSEDE Bella
transition_kind = CORRECTION
Bella alias -> SEARCH_ONLY
Fred alias -> CURRENT
```

Do not infer:

```text
Bella was historically the dog's real name.
```

---

# 43. MULTI-CURRENT CLAIM UPDATE

Example:

```text
E PROJECT
predicate = uses_library
cardinality = MULTI_CURRENT
```

Existing:

```text
PixiJS
```

New:

```text
Tone.js
```

Normally append:

```text
PixiJS ACTIVE
Tone.js ACTIVE
```

No supersession occurs merely because a second value exists.

---

# 44. CONFLICT HANDLING

Persistence must not silently flatten unresolved semantic conflict.

Example:

```text
existing external claim:
version = 4.1

new validated external evidence:
version = 4.2

evidence basis indicates sources genuinely conflict and freshness cannot resolve it
```

Possible result:

```text
M1 -> CONTESTED
M2 -> CONTESTED
CREATE_CONFLICT CF...
```

No clean current value is asserted until later evidence resolves the conflict.

Future resolution may:

```text
activate winner/new claim
supersede/retract conflicting claim(s)
RESOLVE_CONFLICT
transition_kind = CONFLICT_RESOLUTION
```

---

# 45. ENTITY CREATION

Create a new Entity only when:

```text
candidate clearly refers to a durable semantic subject
no supplied existing entity is a valid match
identity is sufficiently specific
creation is justified by a committed claim/relationship
```

Do not create entities for every noun.

An Entity should normally enter memory because at least one durable Claim about it is being committed.

Avoid empty orphan Entities.

---

# 46. ENTITY MERGE — DUPLICATE IDENTITY REPAIR

Sometimes two semantic Entities may later be established as the same real thing.

Prototype supports strict merge:

```text
one canonical entity remains ACTIVE
duplicate entity becomes MERGED
merged_into_entity_uuid points to canonical entity
merge event is append-only
historical claims remain attached to original entity UUIDs
future retrieval canonicalizes merged entity refs
new claims target canonical entity
merge graph must be acyclic
```

Do not destructively rewrite old claim rows merely to erase that duplicate identity once existed.

Automatic advisory entity merge is conservative.

Prefer merge when:

```text
user explicitly establishes identity
or
validated evidence makes identity unambiguous
```

Ambiguous similarity is not enough.

---

# 47. FORGET / RETRACT SEMANTICS

A user may explicitly request:

```text
"Forget that preference."
"Don't remember X anymore."
"That old fact is no longer something you should use."
```

This becomes a normative persistence obligation.

Default semantic action:

```text
RETRACT_CLAIM
```

Retracted claims are excluded from normal active Context retrieval.

Semantic forgetting is separate from transcript deletion.

Persistence does not delete conversation transcript.

A future product-level hard-purge/privacy operation may physically remove semantic values while retaining a minimal tombstone, but that is outside this prototype unless explicitly added by policy.

---

# 48. CURRENT MEMORY VIEW — R2 DURABLE-PROVISIONAL RULE

Normal future Context retrieval primarily sees semantic state whose originating transaction standing is:

```text
CONFIRMED_EXPLICIT
STABILIZED_NO_IMMEDIATE_CORRECTION
```

and whose claim/alias state is otherwise active/eligible.

Normal Context retrieval excludes as clean established truth:

```text
PROVISIONAL transaction effects
REVERTED_BY_USER_CONTROL transaction effects
SUPERSEDED claims as current truth
RETRACTED claims as current truth
SEARCH_ONLY aliases as asserted current labels
expired TIME_BOUNDED claims as clean current truth
```

`PROVISIONAL` state is durably stored for crash safety and provenance, but it is available only through the bounded provisional-review path until finalized.

Historical/debug retrieval may inspect every standing and transaction.

# 48A. CLEAN CONTEXT PROJECTION MUST MASK THE WHOLE PROVISIONAL DELTA

A provisional transaction may create a new claim **and** supersede or retract a previously eligible claim in the same atomic write. Normal Context must not simply filter out the new provisional row while leaving the provisional status mutation applied to the old row.

The SemanticMemoryReadRepository therefore builds a transaction-aware clean projection:

```text
CONFIRMED_EXPLICIT / STABILIZED_NO_IMMEDIATE_CORRECTION effects
  -> apply to clean Context view

PROVISIONAL effects
  -> mask the entire transaction delta
  -> expose the last eligible pre-provisional semantic state for affected targets

REVERTED_BY_USER_CONTROL effects
  -> do not expose the rejected provisional delta as clean truth
  -> expose state produced by the compensating transaction
```

Example:

```text
clean state before turn: version = 6.3.2
provisional transaction: supersede 6.3.2; create 6.4.1

normal Context before review:
  still sees 6.3.2 as the last eligible clean state

after stabilization/confirmation:
  sees 6.4.1

after rejection/undo compensation:
  sees the restored/corrected state from the compensation path
```

The simple SQL `semantic_active_claims` view is therefore a raw storage helper, **not** sufficient by itself for clean Context projection under R2. The repository must use transaction standing, mutation audit rows, and inverse/compensation metadata to construct the eligible view deterministically.

---

# 49. PERSISTENCE HOST — PRE-MODEL INTEGRITY GATE

Before Adapter 1 runs, host checks:

```text
turn UUID valid
Intent hash valid
Context hash valid
Context ready true
Decision hash valid
Reconciliation hash valid
all normative obligation refs valid
all advisory candidate refs valid
all EF refs valid when cited
all Context refs valid when cited
source-authority classification supplied
policy snapshot UUID/hash valid
canonical hash profile valid
memory repository available
```

Failure:

```text
PERSISTENCE_UPSTREAM_INTEGRITY_FAILURE
```

No semantic adapter call.

---

# 50. HOST MEMORY RETRIEVAL

Host provides repository functions conceptually equivalent to:

```text
search_entities(...)
resolve_alias(...)
get_entity(...)
get_active_claims(...)
get_contested_claims(...)
get_claim_transition_history(...)
get_claim_provenance(...)
get_memory_snapshot(...)
```

Adapters never execute SQL.

Recipe 0 never calls semantic-memory APIs.

Context may call read-only semantic retrieval through its own router/split contract.

Persistence uses read APIs for read-before-write identity and claim comparison.

---

# 51. HOST VALIDATION OF COMPOSER PLAN

Required gates:

```text
JSON / schema valid
persistence run UUID valid
memory base commit seq matches supplied snapshot
all normative obligations covered once
all advisory candidates disposed
all PA refs valid
all existing entity/claim/alias refs in supplied snapshot
all temporary new refs locally unique
no invented permanent semantic UUID
allowed mutation enums only
claim object types valid
cardinality valid
source authority valid
durability valid
temporal values valid
single-current consistency
supersession target exists and is eligible
transition target exists
alias target valid
conflict members valid
merge graph acyclic
merge target canonical and active
no transcript mutation
no technical ledger rewrite
no SQL text
no Completion status
no illegal secret persistence
all committed claims have provenance
transaction bounded
```

Host emits detailed validation diagnostics.

No single generic `valid=false` is sufficient for debug/training.

---

# 52. COMPOSER REPAIR

Prototype default:

```text
maximum Persistence Composer repair attempts = 2
```

Repair receives:

```text
original bounded Composer input
previous invalid plan
exact host validation failures
```

Examples:

```text
- Claim M00044 was not in the supplied memory snapshot.
- NEW_E2 is referenced but never proposed.
- SINGLE_CURRENT predicate leaves two ACTIVE values.
- Normative obligation O003 has no item result.
- Proposed alias status "OLD" is not allowed.
```

If still invalid:

```text
PERSISTENCE_COMPOSER_REPAIR_EXHAUSTED
```

No semantic transaction is committed.

---

# 53. HOST ID ALLOCATION

Permanent semantic UUIDs are host-owned.

Prototype:

```text
UUID4
```

Human-readable durable aliases:

```text
E000001   semantic Entity
M000001   semantic Claim
CF000001  semantic Conflict
```

Persistence trace short IDs may remain per-turn:

```text
PA001   Persistence Assessment
PP001   Persistence Plan
PRC001  Persistence Commit Receipt
```

Authoritative database identity remains UUID.

Do not allow a model to choose a permanent UUID.

---

# 54. SQLITE SEMANTIC TABLES — PROTOTYPE

The companion SQL file in this build bundle contains executable prototype DDL.

Core tables:

```text
semantic_entities
semantic_entity_aliases
semantic_claims
semantic_claim_transitions
semantic_conflicts
semantic_conflict_members
semantic_entity_merges
semantic_provenance
memory_transactions
memory_mutations
```

FTS indexes:

```text
semantic_entity_aliases_fts
semantic_claims_fts
```

`system_meta.memory_commit_seq` remains the host-owned semantic revision counter.

---

# 55. MEMORY COMMIT SEQUENCE

`memory_commit_seq` is monotonically increasing and host-owned.

Rules:

```text
no semantic change committed
  -> memory_commit_seq unchanged

successful atomic semantic transaction
  -> memory_commit_seq increments exactly once

failed/rolled-back transaction
  -> memory_commit_seq unchanged
```

Every created/changed semantic row records the commit sequence that produced the active transition.

Context records the memory commit sequence of any semantic snapshot it uses.

---

# 56. OPTIMISTIC CONCURRENCY / STALE SNAPSHOT RULE

Persistence semantic reasoning is based on:

```text
memory_base_commit_seq = N
```

Immediately before commit, host verifies current durable semantic state is still based on `N`.

If current sequence is no longer `N`:

```text
DO NOT COMMIT STALE PLAN
```

Correct path:

```text
STALE_MEMORY_SNAPSHOT
     |
     v
discard pending permanent ID allocations
     |
     v
retrieve new relevant memory snapshot
     |
     v
rerun affected assessment/composition
```

Prototype bound:

```text
max_stale_snapshot_retries = 1
```

If still stale:

```text
PERSISTENCE_CONCURRENCY_BLOCKED
```

This prevents one turn from overwriting newer semantic state.

---

# 57. ATOMIC TRANSACTION MODEL — DURABLY PROVISIONAL R2

All committable semantic mutations for a normal conversational turn are still applied atomically in SQLite.

A successful conversational semantic write is committed durably **with transaction standing `PROVISIONAL` by default**.

Conceptual sequence:

```text
BEGIN IMMEDIATE

verify base memory_commit_seq
allocate semantic short IDs/UUIDs
insert new entities/claims/transitions/aliases/conflicts/merges
insert provenance
insert memory transaction + mutations + compensation basis
set transaction standing = PROVISIONAL
increment memory_commit_seq
create commit-receipt basis

COMMIT
```

If any statement fails:

```text
ROLLBACK
```

No half-committed semantic memory.

`PROVISIONAL` is **not** RAM-ephemeral. It survives process failure and reboot. The distinction is semantic eligibility: it is withheld from normal Context truth projection until the next-turn review gate finalizes or reverses it.

Direct Memory Inspector operations may commit with `CONFIRMED_EXPLICIT` because the user has directly selected the memory operation and target.

Normative obligations preclassified `BLOCKED` or `REJECTED_BY_POLICY` do not prevent unrelated valid obligations from being included in the transaction.

# 58. TRANSACTION STANDING AND NEXT-TURN REVIEW — LOCKED

Transaction execution reality and semantic standing are separate.

Execution status:

```text
PENDING
COMMITTED
ROLLED_BACK
FAILED
```

Semantic standing for committed transactions:

```text
PROVISIONAL
STABILIZED_NO_IMMEDIATE_CORRECTION
CONFIRMED_EXPLICIT
REVERTED_BY_USER_CONTROL
```

Rules:

```text
PROVISIONAL
  durable in SQLite
  not injected as clean established Context

STABILIZED_NO_IMMEDIATE_CORRECTION
  next-turn policy window passed without a supported rejection/correction signal
  eligible for ordinary Context retrieval
  MUST NOT be described as explicit user confirmation

CONFIRMED_EXPLICIT
  user explicitly affirmed the prior state, or directly performed the memory edit in the Memory Inspector

REVERTED_BY_USER_CONTROL
  a later compensating transaction reversed/superseded the provisional effect
  original transaction/receipt remain historical facts
```

The next-turn review is host-owned and occurs before normal Context semantic-memory injection.

If the current prompt contains an explicit correction/reject/undo signal targeting the prior provisional transaction, the host applies a compensating Persistence transaction first. Corrected new content then proceeds through the normal recipe spine.

If the target is ambiguous, do not finalize and do not expose the provisional state as clean current truth.

# 59. COMMIT RECEIPT — R2

Persistence Host creates immutable `PRCxxx`.

Minimum fields:

```text
commit_receipt_uuid
short_id
persistence_run_uuid
turn_uuid
transaction_uuid
execution_status
transaction_standing
base_memory_commit_seq
result_memory_commit_seq
committed_mutation_count
created_entity_refs[]
created_claim_refs[]
transition_refs[]
alias_change_refs[]
conflict_refs[]
merge_refs[]
obligation_results[]
candidate_results[]
compensates_transaction_uuid if applicable
transaction_hash
verification
created_at
```

Execution statuses:

```text
SUCCESS
NO_CHANGE
FAILED
ROLLED_BACK
STALE_SNAPSHOT_BLOCKED
```

Only `SUCCESS` proves SQLite semantic writes committed.

For a normal conversation-origin semantic write, `SUCCESS + PROVISIONAL` is a real durable write and may satisfy a turn-scoped explicit remember obligation. It does **not** mean the user explicitly confirmed the semantic content.

# 60. PERSISTENCE HANDOFF TO COMPLETION — R2

Minimum handoff:

```text
persistence_artifact_uuid
persistence_run_uuid
turn_uuid
basis hashes
memory_base_commit_seq
memory_result_commit_seq

normative_obligation_results[]
advisory_candidate_results[]

validated assessment refs[]
validated plan ref

commit_receipt_ref if transaction attempted
transaction_standing if committed
semantic mutation refs[]
blocked items[]
policy rejections[]
failure diagnostics[]
handoff_hash
```

Persistence does not assign terminal `Rxxx` status.

A committed provisional write is distinguishable from explicit confirmation so Completion/Result cannot accidentally claim that the user confirmed it.

# 61. ZERO-CHANGE PATH

Persistence may legitimately produce no SQLite semantic mutation.

Examples:

```text
no obligations
no candidates
candidate ignored
explicit remember already exists exactly -> NO_CHANGE_NEEDED
candidate deferred due identity ambiguity
```

Correct result:

```text
requires_commit = false
memory_commit_seq unchanged
```

Do not create fake memory rows merely so Persistence "did something."

---

# 61. NORMATIVE OBLIGATION FAILURE SEMANTICS

## Policy rejection

```text
"Remember this password."
```

Result:

```text
REJECTED_BY_POLICY
```

## Identity ambiguity

```text
"Remember that Alex moved."
```

Multiple durable Alex entities, no disambiguation.

Result:

```text
BLOCKED
IDENTITY_AMBIGUOUS
```

## Commit failure

Valid plan, SQLite write fails.

Result:

```text
FAILED
```

Completion later decides how that affects original Rxxx.

Persistence does not pretend success.

---

# 62. ADVISORY CANDIDATE FAILURE SEMANTICS

Advisory candidates may safely resolve:

```text
IGNORED
DEFERRED
```

without failing the turn.

A commit failure affecting only advisory memory is reported honestly but does not automatically mean the user's primary conversational requirement failed.

Completion owns that judgment.

---

# 63. PERSISTENCE FAILURE CLASSES

Initial diagnostic vocabulary:

```text
PERSISTENCE_UPSTREAM_INTEGRITY_FAILURE
INVALID_PERSISTENCE_ITEM
INVALID_MEMORY_SNAPSHOT
INVALID_MODEL_OUTPUT
UNKNOWN_REQUIREMENT_REFERENCE
UNKNOWN_BASIS_REFERENCE
UNKNOWN_ENTITY_REFERENCE
UNKNOWN_CLAIM_REFERENCE
UNKNOWN_ALIAS_REFERENCE
UNKNOWN_CONFLICT_REFERENCE
PROVENANCE_REFERENCE_OUT_OF_SCOPE
MISSING_PROVENANCE
IDENTITY_AMBIGUOUS
ILLEGAL_PERMANENT_ID
INVALID_CLAIM_OBJECT
INVALID_CARDINALITY
INVALID_SOURCE_AUTHORITY
INVALID_DURABILITY_CLASS
INVALID_TEMPORAL_RANGE
SINGLE_CURRENT_CONFLICT_UNRESOLVED
INVALID_SUPERSESSION_TARGET
INVALID_TRANSITION
INVALID_ALIAS_TRANSITION
INVALID_CONFLICT_PLAN
ENTITY_MERGE_CYCLE
ILLEGAL_TRANSCRIPT_MUTATION
ILLEGAL_LEDGER_MUTATION
ILLEGAL_SQL
ILLEGAL_COMPLETION_STATUS
POLICY_BLOCKED
PERSISTENCE_ASSESSOR_REPAIR_EXHAUSTED
PERSISTENCE_COMPOSER_REPAIR_EXHAUSTED
STALE_MEMORY_SNAPSHOT
PERSISTENCE_CONCURRENCY_BLOCKED
SQLITE_TRANSACTION_FAILED
SQLITE_TRANSACTION_ROLLED_BACK
COMMIT_VERIFICATION_FAILED
```

---


# 63A. DIRECT USER MEMORY CONTROL / MEMORY INSPECTOR — LOCKED R2

The product must provide a first-class host-owned Memory Inspector so the user is never trapped behind the model's interpretation of their own durable state.

Normal UI capabilities should include:

```text
VIEW CURRENT STATE
VIEW HISTORY
CORRECT
EDIT
RETRACT / DELETE FROM CURRENT VIEW
ADD ALIAS
CHANGE ALIAS STATUS
MERGE ENTITY
RESTORE / COMPENSATE LAST REVERSIBLE MEMORY CHANGE
```

These are **not raw row edits**. The UI resolves the exact target UUIDs and sends a typed host operation through the Persistence repository/transaction layer.

Direct user memory control:

```text
does not require a model to decide whether the user is allowed to correct their own memory
still passes host schema/invariant/foreign-key/concurrency validation
creates immutable provenance and transaction history
uses compensating/superseding state changes instead of erasing history
```

Typical provenance:

```text
source_authority = USER_ASSERTED
source_channel = DIRECT_USER_MEMORY_CONTROL
```

Advanced external SQLite inspection may exist for development, but the normal application surface must preserve semantic invariants rather than inviting destructive manual row edits.

# 63B. COMPENSATION, NOT HISTORY ERASURE — LOCKED R2

Undo/correction never deletes the original committed transaction, receipt, or technical history.

A reversal is a new transaction linked with:

```text
compensates_transaction_uuid
compensation_reason
source_turn_uuid or direct-control event ref
```

The compensation transaction restores/supersedes semantic state using ordinary validated mutations. `memory_commit_seq` increments for the compensation because semantic state changed again.

---

# 64. PERSISTENCE INVARIANTS — LOCKED

```text
P01. Transcript storage is not semantic Persistence.
P02. Technical ledger identity is not semantic Entity identity.
P03. Persistence receives normative obligations and advisory candidates separately.
P04. Normative obligations must receive explicit results.
P05. Advisory candidates may be ignored or deferred.
P06. Context may nominate grounded user-origin advisory candidates.
P07. Reconciliation may nominate grounded downstream evidence candidates.
P08. Neither Context nor Reconciliation writes semantic SQLite state.
P09. Raw tool text never enters semantic memory directly.
P10. Every semantic Entity has a host-owned UUID.
P11. Every semantic Claim has a host-owned UUID.
P12. Mutable properties normally live as Claims, not mutable Entity truth columns.
P13. Claims preserve source authority.
P14. Every committed Claim has provenance.
P15. Old Claims are never destructively overwritten to hide history.
P16. Change and correction are distinct transition kinds.
P17. A real rename preserves historical alias state.
P18. A correction must not fabricate historical truth.
P19. Duplicate semantic claims normally produce NO_CHANGE.
P20. SINGLE_CURRENT claims may not silently leave incompatible active values.
P21. Genuine unresolved conflict is preserved.
P22. Derived inference is not silently promoted as user-asserted truth.
P23. Entity resolution occurs before new Entity creation.
P24. Models may not invent permanent semantic UUIDs.
P25. Models never execute SQL.
P26. Host validates every semantic mutation plan.
P27. Host owns memory_commit_seq.
P28. Commit is atomic.
P29. Failed transactions do not advance memory_commit_seq.
P30. Stale-snapshot plans are never committed.
P31. Persistence commit receipt is authority that semantic write happened.
P32. Persistence does not delete or choose conversation transcript history.
P33. Persistence does not declare terminal requirement satisfaction.
P34. Normal future Context retrieval excludes superseded/retracted claims as current truth.
P35. Every loop and repair path is bounded.
P36. Normal conversation-origin semantic transactions enter standing PROVISIONAL.
P37. Clean Context masks the entire PROVISIONAL delta and preserves the last eligible pre-provisional state.
P38. STABILIZED_NO_IMMEDIATE_CORRECTION is never represented as explicit user confirmation.
P39. User reject/correct/undo of provisional semantic state uses a compensating transaction; original receipts remain immutable.
P40. Direct Memory Inspector correction is a typed host operation with USER_ASSERTED + DIRECT_USER_MEMORY_CONTROL provenance.
P41. Transaction-standing history is auditable; current standing may not be changed without a standing event.
P42. Source-quality/evidence-authority ranking is outside Persistence R2 and remains a separate lane.
```

---

# 65. SQLITE STARTUP CONTRACT

Use shared database:

```text
arcadia.sqlite3
```

Startup pragmas:

```sql
PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;
PRAGMA busy_timeout = 5000;
```

Migration process:

```text
read schema version
apply ordered migration inside transaction
verify schema objects
update schema version only after success
abort Persistence writer startup if migration integrity fails
```

No adapter runs migrations.

---

# 66. PERSISTENCE REPOSITORY BOUNDARY

Recommended host repository split:

```text
SemanticMemoryReadRepository
SemanticMemoryWriteRepository
```

Recipes 0–5 never receive the write repository.

Context receives only read APIs through its router.

Persistence Host is the only runtime component with semantic write repository.

This makes authority enforceable in code rather than merely documented.

---

# 67. RECOMMENDED SOURCE LAYOUT

```text
persistence_prototype/
|
+-- persistence_prototype.py
+-- README.md
|
+-- persistence/
|   +-- __init__.py
|   +-- models.py
|   +-- enums.py
|   +-- schemas.py
|   +-- policy.py
|   +-- ids.py
|   +-- repository_read.py
|   +-- semantic_memory_view.py
|   +-- repository_write.py
|   +-- provisional_review.py
|   +-- standing.py
|   +-- compensation.py
|   +-- memory_inspector.py
|   +-- snapshot.py
|   +-- entity_search.py
|   +-- assessor.py
|   +-- assessor_validation.py
|   +-- composer.py
|   +-- composer_validation.py
|   +-- transaction.py
|   +-- commit_receipt.py
|   +-- handoff.py
|   +-- trace.py
|
+-- sql/
|   +-- 001_semantic_memory.sql
|
+-- prompts/
|   +-- persistence_assessor.txt
|   +-- persistence_composer.txt
|
+-- schemas/
|   +-- persistence_assessor_input.schema.json
|   +-- persistence_assessor_output.schema.json
|   +-- persistence_plan.schema.json
|   +-- persistence_handoff.schema.json
|   +-- persistence_commit_receipt.schema.json
|
+-- tests/
    +-- fixtures/
    +-- test_repository.py
    +-- test_semantic_memory_view.py
    +-- test_provisional_review.py
    +-- test_compensation.py
    +-- test_memory_inspector.py
    +-- test_entity_resolution.py
    +-- test_assessor_validation.py
    +-- test_composer_validation.py
    +-- test_supersession.py
    +-- test_aliases.py
    +-- test_conflicts.py
    +-- test_transactions.py
    +-- test_concurrency.py
    +-- test_persistence_e2e.py
```

---

# 68. RECOMMENDED HOST MODULES

Python standard library:

```text
sqlite3
json
dataclasses
uuid
hashlib
datetime
enum
typing
contextlib
re
```

Existing project/common modules should supply:

```text
canonical JSON hashing
artifact envelope
turn/artifact UUID validation
structured model runner
schema validation
trace capture
```

Optional:

```text
RapidFuzz
```

may assist entity alias candidate ranking.

It remains a retrieval signal, not semantic identity authority.

SQLite FTS5 is preferred for text candidate retrieval where available.

---

# 69. PERSISTENCE ASSESSOR SPECIALIST CONTRACT

Canonical instruction:

> Given exactly one validated persistence obligation or advisory candidate, its source authority and provenance, the relevant grounded turn state, a frozen bounded snapshot of existing semantic entities/claims/aliases, and host policy, determine only what durable semantic consequence is justified. Resolve whether the subject matches a supplied existing entity or clearly requires a new entity; identify durable claim structure; distinguish duplicate, change, correction, refinement, conflict, and retraction; preserve source authority and temporal meaning; request bounded additional memory only when necessary. Do not execute SQL, invent permanent IDs, rewrite transcript/Intent/Context, declare Completion status, or save unsupported inference as user truth.

---

# 70. PERSISTENCE COMPOSER SPECIALIST CONTRACT

Canonical instruction:

> Given validated per-item Persistence Assessments for the current turn and the exact frozen semantic-memory snapshot they were judged against, compose the smallest coherent semantic mutation plan. Preserve stable entity identity, claim history, provenance, cardinality, aliases, conflicts, change-vs-correction semantics, and explicit obligation coverage. Merge duplicate effects where legitimate and keep ambiguous identities separate. Emit only allowed semantic mutation operations with temporary refs for new records. Do not execute SQL, invent permanent UUIDs, alter transcript or technical history, bypass policy, or assign terminal requirement status.

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


# R2A. HIGH-CONSEQUENCE SEMANTIC ASSURANCE HOOK

Persistence Assessor remains the highest-consequence semantic boundary in the current design.

R2 does not allocate adapter #16. A policy-triggered orthogonal check may be introduced only if an existing independently validated specialist can examine a narrow failure mode under its native contract. The preferred second question is failure-seeking (for example entity-identity ambiguity or explicit correction language), not a duplicate `CHANGE/CORRECTION` classification.

Agreement does not prove truth. Supported disagreement blocks automatic semantic promotion and preserves uncertainty or requests user review.

---

# 71. TRAINING / DEBUG CAPTURE

For every Persistence adapter call retain:

```text
adapter role/version
base model identity
adapter identity/hash
input schema version
output schema version
exact bounded input artifact refs
memory snapshot UUID/hash
memory base commit seq
policy snapshot UUID/hash
raw model output
parsed output
validation report
repair inputs/outputs if any
latency/token metrics
accepted artifact hash
```

Do not require hidden chain-of-thought.

Train/evaluate against observable structured decisions and host validation outcomes.

---

# 72. ASSESSOR TRAINING TARGETS

Training data must cover:

```text
new stable entity
existing entity exact alias match
existing entity historical alias match
same name but different entity
ambiguous identity
request more memory
duplicate claim
single-current change
single-current correction
refinement
multi-current append
retraction
user preference
project configuration
ongoing goal
stable relationship
time-bounded external fact
expired external fact
external conflict
derived inference
advisory trivial statement
explicit remember
explicit forget
policy-blocked secret
```

Deliberately include near-neighbor contrasts:

```text
"I changed Bella's name to Fred."
vs
"I was wrong; her name has always been Fred."
```

because this distinction must be learned, not inferred from output schema alone.

---

# 73. COMPOSER TRAINING TARGETS

Training should cover:

```text
multiple candidates about one new entity
multiple existing entities in one turn
shared entity resolution across assessments
duplicate assessments collapsed
change + alias transition atomic plan
correction + search-only alias plan
multi-current additions
mixed normative/advisory results
one policy-blocked obligation plus valid other writes
conflict creation
conflict resolution
entity merge
no-change transaction
obligation coverage
candidate coverage
```

---

# 74. REQUIRED POSITIVE ACCEPTANCE TESTS

At minimum:

1. User asserts a new dog and name; one Entity and correct Claims are created.
2. Repeated identical fact produces no duplicate Claim.
3. `Bella -> Fred` with explicit rename creates `CHANGE`, historical alias, same Entity.
4. `Bella -> Fred` as correction creates `CORRECTION`, search-only old alias, same Entity.
5. Multi-current project library claim appends without superseding unrelated active value.
6. Explicit `remember` produces normative obligation result.
7. Explicit remember of already-active identical fact produces `NO_CHANGE_NEEDED`.
8. Ordinary durable preference candidate may save advisory state.
9. Trivial advisory candidate is ignored.
10. Derived inference is not automatically promoted as user assertion.
11. External validated durable fact cites EF/Context provenance.
12. Time-bounded claim receives expiry metadata.
13. Expired claim is excluded from clean current Context view.
14. Historical alias still resolves entity.
15. Corrected mistaken alias resolves only through search-only behavior.
16. Two same-name different entities do not merge automatically.
17. Identity ambiguity defers advisory candidate.
18. Identity ambiguity blocks normative obligation.
19. Multiple claims about one newly introduced entity share one allocated entity UUID.
20. Commit increments `memory_commit_seq` exactly once.
21. Zero-change run does not increment sequence.
22. SQLite failure rolls back all mutations.
23. Stale snapshot causes re-read/re-evaluation rather than stale commit.
24. Merge event preserves old Entity/Claim history.
25. Retracted claim disappears from normal active Context retrieval.

---

# 75. REQUIRED FAILURE / ADVERSARIAL TESTS

At minimum:

1. Assessor invents permanent Entity UUID.
2. Assessor references Entity not in snapshot.
3. Assessor references Claim not in snapshot.
4. Assessor creates claim with no provenance.
5. Assessor labels unsupported inference `USER_ASSERTED`.
6. Assessor emits SQL.
7. Assessor asks to edit transcript.
8. Assessor emits terminal `R001 SATISFIED`.
9. Composer drops a normative obligation.
10. Composer silently drops an advisory candidate without disposition.
11. Composer leaves two incompatible `SINGLE_CURRENT` ACTIVE claims.
12. Composer supersedes unknown Claim.
13. Composer uses invalid transition kind.
14. Composer treats correction as historical change.
15. Composer treats rename change as correction despite explicit change wording.
16. Composer creates alias for wrong Entity.
17. Composer invents permanent UUID.
18. Composer creates Entity merge cycle.
19. Composer attempts to merge ambiguous same-name entities.
20. Composer creates orphan Entity with no committed durable purpose.
21. Composer persists prohibited credential.
22. Commit plan based on stale `memory_commit_seq`.
23. Transaction partially fails.
24. Host verification finds expected Claim missing after commit attempt.
25. Model tries to increment `memory_commit_seq`.
26. Model tries to modify technical receipt.
27. Model tries to rewrite old raw evidence.
28. Reconciliation candidate cites raw tool result but no validated EF/Context path.
29. Context advisory candidate lacks user assertion provenance.
30. `DERIVED` advisory claim is automatically promoted despite prototype policy.

Every failure must produce explicit diagnostic.

No silent host repair may change semantic meaning.

---


# 75A. R2 REQUIRED RECOVERY / PROVISIONAL TESTS

At minimum:

1. Normal conversation-origin write commits durably as `PROVISIONAL`.
2. Process restart preserves the provisional transaction and receipt.
3. `PROVISIONAL` claim is not injected as clean established Context.
3a. When a provisional replacement supersedes an older eligible claim, clean Context still sees the older eligible state until review.
4. Next-turn explicit affirmation -> `CONFIRMED_EXPLICIT`.
5. Next-turn unrelated/neutral continuation -> `STABILIZED_NO_IMMEDIATE_CORRECTION`, never explicit-confirmation provenance.
6. Next-turn `that's wrong` with resolvable target -> compensating transaction before normal Context retrieval.
7. Next-turn `don't save that` -> original receipt preserved, semantic effect compensated.
8. Ambiguous undo target -> provisional standing remains and is excluded from clean Context.
9. Compensation increments `memory_commit_seq` once and links original transaction.
10. Memory Inspector correction bypasses model semantic arbitration but passes host invariants.
11. Memory Inspector merge cannot create cycle.
12. Direct-control provenance uses `USER_ASSERTED + DIRECT_USER_MEMORY_CONTROL`.
13. Completion can distinguish `SUCCESS + PROVISIONAL` from failed persistence.
14. Result never calls `STABILIZED_NO_IMMEDIATE_CORRECTION` an explicit user confirmation.
15. Runtime traces are not promoted into training data without approval.
16. Held-out provisional/correction fixtures never enter training.

---

# 76. EXAMPLE A — NEW DOG

Input:

```text
User:
"My dog's name is Bella."
```

Possible grounded Context candidate:

```text
candidate kind: STABLE_RELATIONSHIP / IDENTITY
source authority: USER_ASSERTED
```

Persistence lookup:

```text
no matching dog entity
```

Assessor:

```text
CREATE_NEW entity type DOG

claims:
  relationship_to_user = "pet"
  name = "Bella"
```

Composer:

```text
CREATE_ENTITY NEW_E1
CREATE_CLAIM relationship_to_user
CREATE_CLAIM name
ADD_ALIAS Bella CURRENT
```

Host allocates:

```text
E000001
M000001
M000002
```

Commit succeeds.

Future Context can retrieve Entity and active claims.

---

# 77. EXAMPLE B — DOG RENAME

Existing:

```text
E000001 DOG
M000002 name = Bella ACTIVE
```

User:

```text
"I changed my dog's name to Fred."
```

Entity resolution:

```text
MATCH_EXISTING E000001
```

Semantic relation:

```text
CHANGE
```

Atomic result:

```text
M000002 -> SUPERSEDED
NEW M000003 name = Fred ACTIVE
transition CHANGE
Bella alias -> HISTORICAL
Fred alias -> CURRENT
```

Same Entity survives.

---

# 78. EXAMPLE C — DOG NAME CORRECTION

Existing:

```text
E000001
name Bella ACTIVE
```

User:

```text
"No, I was wrong. Her name has always been Fred."
```

Semantic relation:

```text
CORRECTION
```

Result:

```text
Bella claim SUPERSEDED
Fred claim ACTIVE
Bella alias SEARCH_ONLY
Fred alias CURRENT
```

Persistence does not invent a historical Bella period.

---

# 79. EXAMPLE D — DUPLICATE REMEMBER

Existing:

```text
project A.R.C.A.D.I.A.
renderer preference = PixiJS
ACTIVE
```

User:

```text
"Remember that we're using PixiJS."
```

Normative obligation.

Assessor:

```text
SAME
```

Composer:

```text
NO_CHANGE
```

Obligation:

```text
NO_CHANGE_NEEDED
```

No new semantic Claim is required.

---

# 80. EXAMPLE E — ADVISORY IGNORE

User:

```text
"That was a weird sentence."
```

If it reaches Persistence advisory queue:

```text
durability = NOT_DURABLE
result = IGNORED
```

No memory write.

---

# 81. EXAMPLE F — EXTERNAL CONFLICT

Reconciliation establishes two current source claims that genuinely conflict.

Persistence does not choose whichever sentence sounds better.

Possible durable result:

```text
two CONTESTED claims
one OPEN conflict record
provenance to both evidence chains
```

Future Context sees conflict, not fabricated clean truth.

---

# 82. EXAMPLE G — EXPLICIT FORGET

Existing:

```text
M000080
preference = X
ACTIVE
```

User:

```text
"Forget that preference."
```

Normative obligation.

Persistence:

```text
RETRACT_CLAIM M000080
transition RETRACTION
```

Future normal Context retrieval excludes it.

Transcript remains separate.

---

# 83. PERFORMANCE PHILOSOPHY

Persistence should be host-heavy and model-narrow.

Model inference is spent on:

```text
durability judgment
entity identity judgment
claim decomposition
same/change/correction/refinement/conflict/retraction
semantic cardinality
cross-item coherent mutation composition
```

Host code handles:

```text
SQLite
FTS
exact retrieval
hashes
UUIDs
short IDs
schema validation
foreign keys
enum legality
snapshot isolation
commit sequence
transactionality
concurrency
provenance reference validation
repair limits
receipt generation
```

Do not spend model inference on deterministic mechanics.

Do not let deterministic code pretend to know semantic identity when it only has fuzzy string similarity.

---

# 84. EXACT R2 PROTOTYPE BUILD ORDER

Build the host/recovery substrate before learned Persistence authority.

## Phase P-A — R2 schema / deterministic foundation

```text
P-A01  Freeze R2 checkpoint + AAE contract versions.
P-A02  Apply ARCADIA_PERSISTENCE_SQLITE_SCHEMA_PROTOTYPE_R2_2026-08-28.sql.
P-A03  Implement semantic IDs, provenance, claim/alias/transition/conflict models.
P-A04  Implement memory_transactions, memory_mutations, inverse payloads, transaction targets.
P-A05  Implement memory_transaction_standing_events.
P-A06  Implement canonical JSON/hashes and transaction hashes.
P-A07  Prove migration, FK, WAL, rollback, and standing constraints without models.
```

Gate: schema executes cleanly and all deterministic invariants are testable.

## Phase P-B — Read repository / clean projection

```text
P-B01  Entity + alias lookup.
P-B02  Active/contested/transition/provenance retrieval.
P-B03  Frozen bounded memory snapshot builder.
P-B04  Transaction-aware clean Context projection.
P-B05  Mask entire PROVISIONAL deltas.
P-B06  Preserve last eligible pre-provisional state for affected targets.
P-B07  Exclude REVERTED provisional effects from clean truth.
P-B08  Verify Recipe 0 has no semantic-memory API access.
```

Gate: scripted `old -> provisional replacement` still returns the old eligible value to normal Context before review.

## Phase P-C — Host write / provisional lifecycle

```text
P-C01  Host-only write repository.
P-C02  Mutation implementations + provenance.
P-C03  Stale memory_commit_seq gate.
P-C04  Atomic transaction + verification.
P-C05  Normal conversation commit -> semantic_standing PROVISIONAL.
P-C06  Append INITIAL_PROVISIONAL_COMMIT standing event.
P-C07  Generate immutable PRC with execution_status + transaction_standing.
P-C08  Implement explicit affirmation -> CONFIRMED_EXPLICIT + standing event.
P-C09  Implement no-immediate-correction -> STABILIZED_NO_IMMEDIATE_CORRECTION + event.
P-C10  Implement reject/correct/undo compensation transaction.
P-C11  Link compensation with compensates_transaction_uuid.
P-C12  Prove original transaction/receipt remain immutable.
```

Gate: crash/restart preserves provisional state and review can deterministically finalize or compensate it.

## Phase P-D — Pre-Context provisional review + Memory Inspector

```text
P-D01  Accept validated Intent control signals.
P-D02  Resolve immediately-prior provisional transaction target.
P-D03  Hold ambiguous target; exclude provisional from clean Context.
P-D04  Run compensation before normal Context on explicit reject/correct/undo.
P-D05  Implement typed Memory Inspector VIEW/HISTORY/CORRECT/RETRACT/ALIAS/MERGE/RESTORE operations.
P-D06  Memory Inspector writes USER_ASSERTED + DIRECT_USER_MEMORY_CONTROL provenance.
P-D07  Preserve host validation, concurrency, and transaction invariants for direct controls.
```

Gate: user can correct their own memory without model permission and without raw row editing.

## Phase P-E — Persistence input / packet builder

```text
P-E01  Normalize normative obligations and advisory candidates separately.
P-E02  Validate provenance and authority classes.
P-E03  Bounded entity/claim candidate lookup.
P-E04  Frozen memory snapshot and hash.
P-E05  NEEDS_MORE_MEMORY bounded expansion counters.
P-E06  Packet-projection fixtures identify minimum required memory rows/refs.
```

## Phase P-F — Base GGUF baseline before adapter credit

Run the frozen Assessor and Composer evaluation suites using base GGUF + exact AAE + real host validators. Save first-pass/repair/semantic metrics.

## Phase P-G — Persistence Assessor

```text
P-G01  Generate runtime/training envelope from AAE contract registry.
P-G02  Implement Assessor runner + fresh KV.
P-G03  Implement schema/reference/authority validator.
P-G04  Implement exact bounded repair x2.
P-G05  Test identity, duplicate, change/correction, refinement, conflict, retraction, policy, ambiguity.
P-G06  Compare adapter against frozen base baseline on held-out suite.
```

## Phase P-H — Persistence Composer

```text
P-H01  Generate Composer envelope from same AAE registry.
P-H02  Validate obligation/candidate coverage.
P-H03  Validate temp refs, cardinality, transitions, aliases, conflicts, merge graph, provenance.
P-H04  Implement bounded repair x2.
P-H05  Compare adapter against frozen base baseline on held-out/adversarial suite.
```

## Phase P-I — Commit bridge

```text
P-I01  Translate validated semantic plan to host mutation objects.
P-I02  Recheck base memory_commit_seq.
P-I03  Allocate permanent IDs only after plan validation.
P-I04  Execute atomic provisional transaction.
P-I05  Verify rows + inverse data + transaction targets.
P-I06  Freeze PRC and Persistence handoff to Completion.
```

Gate: only PRC `SUCCESS` proves the write; normal conversation success carries standing `PROVISIONAL`.

## Phase P-J — Trust / recovery stress gate

Required cases include:

```text
new entity
duplicate claim
CHANGE vs CORRECTION
same-name different entity
identity ambiguity
explicit remember
no-change remember
explicit forget
external evidence provenance
conflict create/resolve
stale snapshot
SQLite rollback
policy-blocked secret
model invented UUID/SQL
provisional survives restart
provisional replacement preserves prior clean state
explicit affirmation confirms
neutral continuation stabilizes but does not confirm
reject/correct/undo compensates
ambiguous undo target holds provisional
Memory Inspector correction/merge/history
Completion sees SUCCESS + PROVISIONAL correctly
full replay from transcript + ledger + semantic transactions + standing events
```

Runtime traces remain raw evaluation/debug data until explicitly promoted through the training-data approval path. Held-out fixtures never enter training.


---

# 85. PROTOTYPE CONFIGURATION DEFAULTS

Freeze as configurable defaults:

```text
persistence_assessor_max_repairs = 2
persistence_composer_max_repairs = 2
max_memory_lookup_expansion_cycles_per_item = 2
max_entity_candidates_per_lookup = 8
max_stale_snapshot_retries = 1
semantic_memory_fts_candidate_limit = 8
sqlite_busy_timeout_ms = 5000
provisional_review_enabled = true
neutral_next_turn_semantic_standing = STABILIZED_NO_IMMEDIATE_CORRECTION
memory_inspector_enabled = true
```

`neutral_next_turn_semantic_standing` is a standing-policy outcome, not a claim of user affirmation. It must never map ordinary continuation to `CONFIRMED_EXPLICIT`.

Do not hard-code model context/token sizes into semantic contracts.

Use runtime configuration based on selected model.

---

# 86. NON-GOALS FOR THIS PROTOTYPE

Do not add:

```text
vector database
cloud database
graph database
automatic embedding store
one adapter per entity type
one adapter per memory category
background unsupervised memory rewriting
automatic user personality inference
raw transcript summarization into memory
raw web result -> SQLite
unbounded semantic-memory search
model-written SQL
destructive in-place claim overwrite
global memory cleanup model
Completion logic
final Result prose
```

SQLite + FTS5 + explicit Entity/Claim semantics are sufficient for this prototype.

Add complexity only when traces prove a specific bottleneck.

---

# 87. IMPLEMENTATION ACCEPTANCE CRITERIA — R2

Persistence prototype is ready to freeze when:

```text
[ ] Parent/global invariants still pass.
[ ] Context/Reconciliation cannot write semantic tables.
[ ] Recipe 0 cannot query semantic tables.
[ ] Persistence write repository is host-only.
[ ] Entity UUID survives across turns.
[ ] Claim UUID survives across turns.
[ ] Duplicate claim does not multiply.
[ ] Change and correction produce different transition history.
[ ] Historical aliases resolve correctly.
[ ] Search-only corrected aliases do not become asserted truth.
[ ] Conflicts remain visible.
[ ] Derived advisory inference is not silently promoted.
[ ] Explicit remember cannot disappear.
[ ] Explicit forget removes claim from normal active retrieval.
[ ] Normative obligations are fully accounted for.
[ ] Advisory candidates are fully dispositioned.
[ ] Provenance exists for every committed Claim.
[ ] No raw tool result bypasses Reconciliation/Context.
[ ] memory_commit_seq increments exactly once per successful semantic transaction.
[ ] Failed/rolled-back writes do not increment memory_commit_seq.
[ ] Stale memory snapshot cannot commit.
[ ] Permanent IDs are host-owned.
[ ] Model output cannot contain executable SQL.
[ ] Commit receipt proves actual semantic write.
[ ] Normal conversational writes commit as crash-safe PROVISIONAL state.
[ ] PROVISIONAL state is excluded from clean Context truth retrieval.
[ ] Next-turn review distinguishes explicit confirmation from no-immediate-correction stabilization.
[ ] User correction/undo produces compensation without erasing original receipts/history.
[ ] Memory Inspector preserves host invariants and provenance.
[ ] Completion receives Persistence results without Persistence assigning terminal Rxxx status.
[ ] Full trace is replayable from transcript + ledger + semantic transaction history.
[ ] Base GGUF baseline and adapter held-out evaluation are stored separately.
[ ] Runtime logs do not automatically become training data.
```

# 88. FINAL LOCKED PERSISTENCE FLOW — R2

```text
VALIDATED PRE-PERSISTENCE HANDOFF
       |
       +--> normative obligations[]
       +--> Context advisory candidates[]
       +--> Reconciliation advisory candidates[]
       +--> provenance graph
       |
       v
HOST INTEGRITY GATE
       |
       v
FOR EACH ITEM
  HOST MEMORY LOOKUP -> FROZEN SNAPSHOT -> PERSISTENCE ASSESSOR
       |                                      |
       |<------ bounded additional memory ----+
       v
VALIDATED PAxxx
       |
       v
CLEAR KV
       |
       v
PERSISTENCE COMPOSER
       |
       v
HOST VALIDATION + stale-seq check
       |
       v
ALLOCATE PERMANENT IDS
       |
       v
BEGIN IMMEDIATE
       |
       v
APPLY + VERIFY MUTATIONS
       |
       v
SET TRANSACTION STANDING = PROVISIONAL
       |
       v
INCREMENT memory_commit_seq ONCE
       |
       v
COMMIT
       |
       v
IMMUTABLE PRCxxx (SUCCESS + PROVISIONAL)
       |
       v
COMPLETION / RESULT FOR CURRENT TURN

NEXT USER TURN
       |
       v
INTENT CONTROL SIGNALS + PRIOR PROVISIONAL SUMMARY
       |
       +--> AFFIRM -> CONFIRMED_EXPLICIT
       |
       +--> NO REJECTION -> STABILIZED_NO_IMMEDIATE_CORRECTION
       |
       +--> CORRECT/REJECT/UNDO -> COMPENSATING PERSISTENCE TRANSACTION
       |
       +--> AMBIGUOUS -> HOLD PROVISIONAL / EXCLUDE FROM CLEAN CONTEXT
       |
       v
NORMAL CONTEXT RETRIEVAL
```

# 89. FINAL DESIGN SUMMARY — R2

```text
PERSISTENCE QUESTION
  What validated state should become durable semantic memory?

SEMANTIC MODEL
  stable Entity identity
  + append/supersede Claims
  + aliases
  + mandatory provenance
  + explicit transitions/conflicts/merges

NORMAL CONVERSATION WRITE
  SQLite COMMITTED
  + semantic standing PROVISIONAL
  + crash-safe
  + withheld from clean Context until next-turn review

NEXT-TURN REVIEW
  explicit affirmation -> CONFIRMED_EXPLICIT
  no immediate correction -> STABILIZED_NO_IMMEDIATE_CORRECTION
  reject/correct/undo -> compensating transaction
  ambiguous target -> hold provisional

USER CONTROL
  Memory Inspector is host-owned
  typed operations, not raw row edits
  direct user correction does not need model permission

HISTORY
  undo never erases receipts/transactions
  compensation is additive and traceable

ADAPTERS
  Persistence Assessor + Persistence Composer only
  no new critic adapter allocated

HOST
  owns UUIDs, policy, retrieval, validation, SQLite, transactions,
  provisional standing, compensation, commit sequence, receipts

CRITICAL DISTINCTIONS
  CHANGE != CORRECTION
  COMMITTED != EXPLICITLY_CONFIRMED
  STABILIZED_NO_IMMEDIATE_CORRECTION != USER_CONFIRMED

COMPLETION
  remains sole terminal Rxxx authority
```

---

# 90. NEXT IMPLEMENTATION / QUALIFICATION TARGET

Persistence design is no longer waiting on Completion; Recipes 7 and 8 are already specified in the R2 bundle.

Next work for this recipe is implementation and trust qualification:

```text
build R2 SQLite repository/migrations
build provisional review + compensation path
build Memory Inspector typed control surface
run base-GGUF baseline
train/evaluate Persistence Assessor
train/evaluate Persistence Composer
run provisional/correction/undo adversarial suite
run full-spine shadow traces before automatic trust
```

Source-quality / evidence-authority ranking remains a separate design lane and is not solved inside Persistence.


---

**END OF A.R.C.A.D.I.A. PERSISTENCE RECIPE PROTOTYPE BUILD SPECIFICATION — 2026-08-28**
