# A.R.C.A.D.I.A. v0.1 — Canonical Recipe Contract

**v0.1 integration status:** The detailed semantic recipe body below is carried forward from the final pre-v0.1 trust/recovery specification because R3 intentionally did not change semantic recipe ownership. It is now governed by the v0.1 common runtime/AAE/source/recovery/trace/performance contracts in this bundle.

**Conflict rule:** if this carried-forward body contains older wording about adapter loading, generic adapter runtime, source-quality being unresolved, trace retention, crash replay, global sampling, handwritten AAE framing, or model-call necessity, the v0.1 system documents `01`–`09` supersede that wording. Semantic recipe responsibilities, artifacts, edge cases, and tests remain authoritative unless explicitly superseded.

---

# A.R.C.A.D.I.A. — COMPLETION RECIPE
## Prototype Build Specification — Final Requirement Standing

**Project:** A.R.C.A.D.I.A. — Adaptive Runtime for Compartmentalized Agents, Decisions, Interaction & Automation  
**Recipe:** 7 — Completion  
**Date:** 2026-08-28  
**Status:** LOCKED PROTOTYPE BUILD DESIGN  
**Parent:** `ARCADIA_PERSISTENCE_RECIPE_PROTOTYPE_BUILD_SPEC_2026-08-28.md`  
**Upstream:** Recipe 0 Conversation Resolver, Recipe 1 Intent, Recipe 2 Context, Recipe 3 Decision, Recipe 4 Tool / Execution, Recipe 5 Reconciliation, Recipe 6 Persistence  
**Next stage:** Recipe 8 — Result  
**Purpose:** Define the exact host, model, provenance, graph, validation, terminal-status, failure, handoff, and test contracts used to compare the immutable user requirements against the authoritative state produced by all prior recipes and freeze the final standing of every `Rxxx` before conversational articulation begins.

---

> **CONFIRMED LOGIC INTEGRATION — R2 — 2026-08-28**  
> This R2 document integrates the confirmed trust/recovery logic locked after the AAE five-slice review: single-source AAE/runtime/training contracts, base-model baselining, full trace capture with a training-data firewall, packet-projection testing, aggregate loop telemetry, durable-provisional semantic Persistence with next-turn review, controlled user memory correction, deterministic-first semantic support, and mode-specific Howard evaluation.  
> **Source-quality / source-authority ranking is intentionally NOT defined by this update. It remains a separate required design lane.**


# 0. SOURCE BASELINE AND AUTHORITY

Completion is designed against the current A.R.C.A.D.I.A. checkpoint and Persistence specification.

The following upstream boundaries remain authoritative:

```text
Intent owns what the user communicated.
Context owns active grounded working state.
Decision owns planned work and persistence obligations.
Execution owns operation reality.
Reconciliation owns what returned work established.
Persistence Host owns durable semantic commit reality.
Completion alone owns terminal Rxxx standing.
Result owns user-facing articulation, not truth.
```

Completion does not reopen work.

Completion does not browse, execute, save, revise Context, mutate Intent, alter Persistence, or write final conversational prose.

Its job begins only after the turn has reached a stable pre-Completion state.

---

# 1. CORE QUESTION

Completion answers exactly:

> **Given the immutable requirement and the complete authoritative outcome chain for that requirement, what is its final standing for this turn?**

The prototype terminal vocabulary is frozen to:

```text
SATISFIED
PARTIALLY_SATISFIED
BLOCKED
FAILED
```

No upstream recipe may emit these as authoritative terminal `Rxxx` states.

No downstream Result model may change them.

---

# 2. POSITION IN THE FULL SPINE

```text
[0] CONVERSATION RESOLVER
       |
[1] INTENT
       |
[2] CONTEXT
       |
[3] DECISION
       |
[4] TOOL / EXECUTION
       |
[5] RECONCILIATION
       |
[6] PERSISTENCE
       |
       v
[7] COMPLETION
    requirement-by-requirement terminal standing
       |
       v
FINAL STANDING PACKET
       |
       v
[8] RESULT
    Conversational Howard articulation
       |
       v
HOST PUBLICATION
       |
       v
USER
```

Completion freezes semantic standing before any final conversational comment is generated.

---

# 3. WHY COMPLETION EXISTS

Earlier recipes answer narrower questions:

```text
Decision:
  What work is needed?

Execution:
  What happened operationally?

Reconciliation:
  What did that work establish?

Persistence:
  What durable semantic changes committed?
```

None of those alone answers:

```text
Did R001, as originally communicated, end this turn satisfied,
partially satisfied, blocked, or failed?
```

Completion is the closing ledger judge.

Without Completion, final conversational Howard would become a hidden terminal-status judge.

That is prohibited.

---

# 4. COMPLETION DOES NOT CREATE NEW REALITY

At Completion:

```text
what happened has happened
what evidence established has been established
what was saved is saved
what failed is recorded
what remains blocked remains blocked
```

Completion may not:

```text
call a tool
request another search
execute a repair
create a DNxxx
revise Context
re-enter Decision
write semantic memory
change a PRCxxx
change an EFxxx
rewrite an Rxxx
```

If unresolved work still legitimately requires another upstream loop, the turn has not reached Completion yet.

Completion only evaluates the stable authoritative record that exists.

---

# 5. TERMINAL STATUS SEMANTICS — LOCKED

## 5.1 SATISFIED

Use when the essential meaning of the requirement has been fulfilled for this turn and no material requirement-level gap remains.

Examples:

```text
requested information was established
required external action succeeded and was verified
required durable memory obligation committed or was already satisfied
required combination of information/action/persistence all resolved
```

`SATISFIED` does not mean every optional or advisory candidate succeeded.

Advisory Persistence failure alone does not make an unrelated user requirement unsatisfied.

## 5.2 PARTIALLY_SATISFIED

Use when:

```text
a material, useful portion of the requirement was fulfilled
AND
at least one material portion remains unmet
AND
the requirement cannot honestly be called fully satisfied for this turn
```

It is not a euphemism for failure.

It requires genuine partial fulfillment.

Example:

```text
user requested three independent facts;
two were established;
one could not be established.
```

## 5.3 BLOCKED

Use when the requirement cannot be completed because a required prerequisite is unavailable or unresolved and the architecture has reached a legitimate stopping point.

Examples:

```text
required user information missing
identity remains ambiguous after bounded resolution
capability unavailable
policy prevents required operation
required upstream condition has not been met
```

`BLOCKED` means the requirement is not complete, but the dominant reason is an external/prerequisite barrier rather than an attempted operation simply failing.

## 5.4 FAILED

Use when the requirement was legitimately attempted or processed but a required operation/recipe path failed and no valid remaining path completed the requirement in this turn.

Examples:

```text
required tool operation failed
required Persistence commit failed
required recipe repair exhausted
upstream integrity failure prevents a trustworthy completion
```

`FAILED` is not used merely because evidence was absent when the proper condition is `BLOCKED`.

---

# 6. TERMINAL STATUS IS TURN-SCOPED

A terminal Completion status closes the current turn.

It does not mean the underlying real-world goal can never change.

Example:

```text
R003 -> BLOCKED
reason = user must provide destination path
```

A later user turn may provide the path and create a new requirement with its own lifecycle.

Do not mutate old `R003` to pretend it was satisfied in the earlier turn.

Historical Completion remains immutable.

---

# 7. COMMUNICATION VS SEMANTIC SATISFACTION

Completion freezes semantic requirement standing before Result writes the final response.

For information requests, `SATISFIED` means:

```text
the system has the validated information necessary to fulfill the requirement
and the Result packet has an authorized user-facing representation of that information
```

Actual transport/publication is a separate host-owned Result step.

Therefore:

```text
Completion SATISFIED
!=
network/UI delivery receipt
```

The exact published response is written into transcript only after successful Result publication.

---

# 8. COMPLETION PROTOTYPE SPECIALISTS — LOCKED

The Completion prototype adds exactly **two new learned contracts**:

```text
[ADAPTER 1]
COMPLETION ASSESSOR
  one Rxxx at a time
  -> terminal standing proposal
       |
       v
HOST VALIDATION
       |
       v
CLEAR KV
       |
       v
[ADAPTER 2]
COMPLETION COMPOSER
  all validated per-Rxxx standings
  -> one coherent Final Standing Packet
```

No Completion critic adapter.

No Result adapter is counted here.

No graph adapter.

No status-rule adapter.

No persistence adapter.

The host owns deterministic mechanics.

---

# 9. KV / MODEL STATE RULE

Clear KV / attention at every Completion adapter boundary.

Adapters may remain loaded or warm.

Hidden state is never Completion memory.

Only explicit, validated artifacts cross specialist boundaries.

---

# 10. COMPLETION ARTIFACT NAMESPACES

Recommended turn-scoped trace aliases:

```text
CA001   Completion Assessment
CP001   Completion Plan / Final Standing Composition
FSP001  Final Standing Packet
```

All also receive host UUID-backed `artifact_uuid`.

`Rxxx` remains the authoritative requirement identity within its turn.

Completion does not allocate replacement requirement IDs.

---

# 11. COMPLETION INPUT CONTRACT

Completion receives a host-built turn closure envelope containing authoritative references to:

```text
turn_uuid
conversation_uuid
raw user prompt ref/hash

Intent
  immutable Rxxx records
  intent artifact UUID/revision/hash

Context
  final active Context snapshot UUID/hash
  final active lanes/points relevant to Rxxx
  valid unresolved/conflict state where relevant

Decision
  all requirement decisions/revisions relevant to Rxxx
  active/superseded Wxxx
  blockers
  persistence obligations
  work origins

Execution
  immutable TRQ/REC history
  explicit unexecuted-work states
  compilation failures
  operation failures/timeouts/rejections

Reconciliation
  EFxxx findings
  conflicts
  final requirement posture flags
  DN/CIP/RRQ lifecycle
  re-entry completion history
  remaining gap refs

Persistence
  normative obligation results
  advisory candidate results
  PRCxxx commit receipt
  memory commit sequence
  blocked/policy/failure results

host closure signals
provenance graph snapshot
canonical hashes
```

Completion does not receive one lossy prose summary in place of these references.

---

# 12. REQUIREMENT CLOSURE BUNDLE

Before Adapter 1 runs, the host builds one bounded `RequirementClosureBundle` per `Rxxx`.

Conceptual shape:

```text
requirement_closure_bundle
  bundle_uuid
  turn_uuid
  requirement_id
  requirement_artifact_uuid
  requirement_text
  requirement_type/flags if available

  context_refs[]
  decision_refs[]
  work_refs[]
  execution_refs[]
  reconciliation_refs[]
  persistence_refs[]

  established_user_facing_facts[]
  unresolved_material_gaps[]
  conflicts[]
  blockers[]
  failure_events[]

  host_closure_signals
  provenance_subgraph_hash
  bundle_hash
```

The Assessor sees the exact requirement plus only the relevant authoritative chain.

Do not flood every Assessor with the full turn.

---


# R2. COMMITTED-PROVISIONAL PERSISTENCE SEMANTICS

Completion judges whether the current-turn persistence operation actually committed, not whether a future turn has explicitly confirmed the semantic content.

For an explicit current-turn remember/update requirement:

```text
PRC execution_status = SUCCESS
transaction_standing = PROVISIONAL
```

is a real crash-safe semantic write and may satisfy the turn-scoped persistence obligation.

Completion must still preserve the distinction:

```text
COMMITTED_PROVISIONAL != CONFIRMED_EXPLICIT
```

A later user correction/undo creates a new turn and a compensating state transition. It does not retroactively rewrite the old Completion artifact or transcript.

If Persistence failed to commit, Completion must not treat a planned/provisional-intended write as success.

---

# 13. SQLITE ROLE IN COMPLETION

SQLite is used as the deterministic source for artifact lookup.

Completion Host may query the technical ledger for:

```text
all artifacts linked to Rxxx
all Wxxx attached to Rxxx
all receipts attached to those Wxxx
all EFxxx linked to those receipts/work items
all persistence obligations attached to Rxxx
all PRC results attached to those obligations
all re-entry artifacts subordinate to Rxxx
```

SQLite does not decide terminal status.

It assembles the closure record.

---

# 14. PROVENANCE GRAPH ROLE — NETWORKX RECOMMENDED

A host provenance graph may be built using `networkx`.

Nodes may represent:

```text
Rxxx
Context artifacts
Decision artifacts
Wxxx
TRQxxx
RECxxx
EFxxx
DNxxx
RRQxxx
Persistence obligations/candidates
PA/PP/PRC artifacts
```

Edges come from validated artifact links.

Use graph checks for:

```text
reachability
orphan evidence
orphan work
unknown support chains
unexpected cycles where the contract forbids them
persistence receipt reachability
requirement-linked evidence provenance
```

NetworkX never decides semantic satisfaction.

A path existing does not prove the requirement was fulfilled.

It only proves structural provenance is coherent.

---

# 15. SET-ALGEBRA CLOSURE SIGNALS

Use ordinary Python sets/dicts to derive exact mechanical facts.

Examples:

```text
required_work_ids
executed_work_ids
unexecuted_work_ids
failed_work_ids
reconciled_work_ids
established_work_ids
partial_work_ids
conflict_work_ids

required_persistence_obligations
resolved_persistence_obligations
failed_persistence_obligations
blocked_persistence_obligations
```

Mechanical differences:

```text
missing_execution =
  required_work_ids - executed_or_explicitly_unexecuted_ids

unreconciled_execution =
  executed_work_ids - reconciled_work_ids

unresolved_persistence =
  required_persistence_obligations - resolved_persistence_obligations
```

These are host signals.

They are not terminal statuses.

---

# 16. CLOSURE SIGNAL PACK

Recommended deterministic fields per requirement:

```text
work_expected_count
work_executed_count
work_unexecuted_count
work_failed_count
work_established_count
work_partial_count
work_conflict_count

remaining_gap_count
open_conflict_count
open_DN_count
open_RRQ_count

persistence_required_count
persistence_committed_count
persistence_no_change_count
persistence_blocked_count
persistence_failed_count

unknown_reference_count
provenance_reachability_pass
upstream_integrity_pass
```

The Assessor receives this along with semantic artifacts.

---

# 17. UPSTREAM INTEGRITY GATE

Before any Completion adapter call:

```text
Intent hash valid
Rxxx immutable artifact exists
final active Context hash valid
Decision history hashes valid
Execution receipts/unexecuted-state hashes valid
Reconciliation handoff hash valid
Persistence handoff hash valid
PRC hash valid if present
all cited artifact UUIDs exist
all requirement refs legal
all subordinate DN/RRQ refs resolve
all required re-entry loops are terminal
provenance graph builds successfully
closure bundle hash valid
```

Failure produces:

```text
COMPLETION_UPSTREAM_INTEGRITY_FAILURE
```

Do not ask a model to reason over corrupted closure state.

---

# 18. COMPLETION ASSESSOR — CORE QUESTION

> **For this exact immutable requirement, given the authoritative final Context, work/receipt history, reconciled findings, Persistence results, remaining gaps, blockers, failures, and host closure signals, what is the correct terminal standing for this turn?**

Allowed output status:

```text
SATISFIED
PARTIALLY_SATISFIED
BLOCKED
FAILED
```

No fifth normal terminal state exists in the prototype.

---

# 19. COMPLETION ASSESSOR INPUT

Recommended packet:

```text
completion_run_uuid
completion_policy_snapshot_uuid/hash

requirement_closure_bundle
  exact Rxxx
  final relevant Context
  relevant work history
  Execution outcomes
  Reconciliation findings/postures
  Persistence outcomes
  host closure signals
  provenance refs

allowed_terminal_statuses
```

No raw unrelated tool payload dump.

No unrelated requirements.

---

# 20. COMPLETION ASSESSOR OUTPUT

Recommended structure:

```text
completion_assessment
  assessment_short_id: CA001
  requirement_id
  terminal_status

  fulfilled_components[]
    component
    supporting_refs[]

  unmet_components[]
    component
    reason
    supporting_refs[]

  blockers[]
  failure_causes[]
  conflict_refs[]

  persistence_effect
    REQUIRED_AND_COMMITTED
    REQUIRED_ALREADY_SATISFIED
    REQUIRED_BLOCKED
    REQUIRED_FAILED
    NOT_REQUIRED

  user_facing_fact_refs[]
  user_facing_blocker_refs[]
  user_facing_failure_refs[]

  result_guidance
    must_report[]
    may_report[]
    must_not_claim[]

  reason_codes[]
  provenance_refs[]
```

The Assessor does not write final user prose.

---

# 21. COMPLETION ASSESSOR HOST VALIDATION

Host validates:

```text
JSON/schema
known CA ID
known Rxxx
terminal enum legal
all supporting refs exist
all refs reachable from requirement closure bundle
all claimed persistence refs legal
all claimed blockers/failures exist
no invented work/receipt/evidence refs
no Intent mutation
no Context mutation
no new work request
no tool call
no SQLite write
no new DN/RRQ
no final-response prose field
no status outside allowed vocabulary
no claim that Result was published
```

Host does not silently change one valid semantic terminal status to another.

---

# 22. SEMANTIC STATUS CONSISTENCY GATES

Deterministic code may reject impossible combinations.

Examples:

```text
SATISFIED
+ unmet material component explicitly marked essential
=> invalid

SATISFIED
+ required persistence obligation FAILED
=> invalid unless the obligation is proven unrelated to this Rxxx

BLOCKED
+ blocker refs empty
=> invalid

FAILED
+ no failure refs and only missing user prerequisite exists
=> suspicious/invalid under policy

PARTIALLY_SATISFIED
+ fulfilled_components empty
=> invalid
```

These are schema/consistency gates.

They do not replace the Assessor’s semantic judgment.

---

# 23. COMPLETION ASSESSOR REPAIR

Prototype default:

```text
maximum Completion Assessor repair attempts = 2
```

Repair packet:

```text
original bounded closure bundle
previous invalid structured output
exact host validation errors
```

Do not reprompt because the model validly returned an unpleasant status.

Reprompt only for invalid/illegal output.

After exhaustion:

```text
COMPLETION_ASSESSOR_REPAIR_EXHAUSTED
```

Affected requirement cannot receive a fabricated clean standing.

---

# 24. COMPLETION COMPOSER — CORE QUESTION

> **Given all validated per-requirement Completion Assessments, compose one coherent immutable final standing for the turn without changing any requirement-level terminal judgment.**

The Composer organizes.

It does not re-decide.

---

# 25. COMPLETION COMPOSER INPUT

```text
completion_run_uuid
turn_uuid
immutable Rxxx list
validated CAxxx assessments[]
cross-requirement relationship refs
shared findings where applicable
host coverage signals
completion policy snapshot/hash
```

All CA statuses are already validated.

---

# 26. COMPLETION COMPOSER OUTPUT

Recommended structure:

```text
completion_plan
  short_id: CP001
  turn_uuid

  requirement_standings[]
    requirement_id
    terminal_status
    completion_assessment_ref
    fulfilled_components[]
    unmet_components[]
    blockers[]
    failure_causes[]
    user_facing_fact_refs[]
    user_facing_blocker_refs[]
    user_facing_failure_refs[]
    result_guidance

  overall_turn_posture
  ordered_result_focus[]
  shared_user_facing_facts[]
  shared_blockers[]
  shared_failures[]
  disclosure_seed[]
  diagnostics[]
```

The requirement status must exactly match its source `CAxxx`.

---

# 27. OVERALL TURN POSTURE

Overall posture is a host/composer organizational field, not a replacement for per-Rxxx status.

Recommended values:

```text
ALL_SATISFIED
MIXED
BLOCKED
FAILED
```

Derivation policy:

```text
all Rxxx SATISFIED -> ALL_SATISFIED

mixed terminal statuses -> MIXED

all unresolved requirements primarily BLOCKED and none FAILED -> BLOCKED

all unresolved requirements FAILED with no material satisfied/partial outcome -> FAILED
```

Per-requirement statuses remain authoritative.

---

# 28. REQUIREMENT COVERAGE INVARIANT

Every immutable in-scope `Rxxx` must appear exactly once in the final Completion composition.

Invalid:

```text
R001
R002
R004
```

when Intent contained:

```text
R001
R002
R003
R004
```

This is a hard host gate.

Completion cannot drop an awkward requirement.

---

# 29. STATUS IMMUTABILITY THROUGH COMPOSITION

If:

```text
CA003:
R003 = BLOCKED
```

then:

```text
CP001:
R003 must = BLOCKED
```

Composer may not upgrade or downgrade it.

If it attempts to do so:

```text
COMPLETION_STATUS_MUTATION
```

and repair.

---

# 30. COMPLETION COMPOSER HOST VALIDATION

Host validates:

```text
schema
all Rxxx covered exactly once
all CA refs exist
all statuses exactly preserved
all result refs in source CA
no invented facts
no invented blockers/failures
overall posture legal
ordering only references known requirements
disclosure seeds reference user-facing fields
no final prose
no tool requests
no SQL
no Persistence mutation
no terminal-status rejudgment
```

---

# 31. COMPLETION COMPOSER REPAIR

Prototype default:

```text
maximum Completion Composer repair attempts = 2
```

Repair only malformed/illegal composition.

If exhausted:

```text
COMPLETION_COMPOSER_REPAIR_EXHAUSTED
```

Do not generate a Final Standing Packet from invalid composition.

---

# 32. FINAL STANDING PACKET — FSPxxx

After validated `CPxxx`, the host creates immutable `FSPxxx`.

Minimum structure:

```text
final_standing_packet
  artifact_uuid
  short_id: FSP001
  turn_uuid
  completion_run_uuid

  basis_hashes
    Intent
    final Context
    Decision history projection
    Execution
    Reconciliation
    Persistence

  requirement_standings[]
    Rxxx
    terminal_status
    user-facing requested outcome
    fulfilled components
    unmet components
    blockers
    failure causes
    user-facing fact refs
    user-facing blocker refs
    user-facing failure refs
    result guidance

  overall_turn_posture
  ordered_result_focus
  shared facts/blockers/failures

  disclosure_seed
  protected_literal_seed

  validation_summary
  packet_hash
```

`FSPxxx` is the sole semantic source of truth for Recipe 8 Result.

---

# 33. FINAL STANDING IMMUTABILITY

After `FSPxxx` validates:

```text
Rxxx terminal statuses are frozen.
```

Result may not:

```text
change them
reinterpret them into stronger success
hide a required blocker
claim failed Persistence succeeded
claim unestablished evidence was established
```

A later technical failure in Result publication does not rewrite Completion.

It creates Result/publication failure state.

---

# 34. USER-FACING FACT PROJECTION

Completion should not send the Result model raw technical internals when a bounded user-facing projection exists.

Example:

Technical chain:

```text
W004
TRQ004
REC004
EF003
PRC001
```

User-facing projection:

```text
fact_id: UF001
text_or_structured_value: "Version 4.2 is current."
source_refs: [EF003]
```

The user-facing projection is host/Completion bounded and provenance-backed.

It does not replace the original artifacts.

---

# 35. DISCLOSURE SEED

Completion emits structured seeds later used by Result Host.

Classes:

```text
MUST_MENTION
MAY_MENTION
DO_NOT_EXPOSE
```

Typical `MUST_MENTION`:

```text
material requested result
material partial limitation
blocker that prevents completion
required operation failure
required Persistence failure
user action needed
```

Typical `DO_NOT_EXPOSE` by default:

```text
internal REC/EF/PRC IDs
repair attempt internals
adapter names
hashes
schema diagnostics
SQLite transaction mechanics
```

Result Host finalizes the disclosure map.

---

# 36. PROTECTED LITERAL SEED

Completion may identify exact literals that Result must not casually alter:

```text
names
versions
dates
times
quantities
units
filenames
paths
URLs
project names
model names
hashes when user-facing
codes/identifiers when user-facing
```

These are forwarded to Result’s Literal Lock.

---

# 37. COMPLETION MODULE STACK

Recommended:

```text
sqlite3
dataclasses or pydantic
json / jsonschema
uuid
hashlib
enum
collections
typing
networkx
```

Optional:

```text
RapidFuzz
```

only for bounded artifact/entity lookup assistance where exact IDs are not available.

Completion should prefer exact UUID/ref relationships over fuzzy matching.

---

# 38. PYDANTIC VS JSON SCHEMA

Recommended split:

```text
Pydantic/dataclasses
  host internal typed models

JSON Schema
  adapter-facing envelopes
  logs/replay validation
```

If the existing runtime standardizes solely on JSON Schema + dataclasses, keep that consistency.

Do not add a library merely for fashion.

The invariant is typed deterministic validation.

---

# 39. COMPLETION POLICY SNAPSHOT

Use a versioned host-owned policy snapshot:

```text
completion_policy_snapshot_uuid
policy_version
terminal_status_definitions
essential_component_rules
result_disclosure_defaults
repair limits
graph validation settings
policy_hash
```

The policy snapshot is included in trace/provenance.

Adapters cannot alter it.

---

# 40. COMPLETION FAILURE CLASSES

Initial diagnostics:

```text
COMPLETION_UPSTREAM_INTEGRITY_FAILURE
INVALID_CLOSURE_BUNDLE
UNKNOWN_REQUIREMENT_REFERENCE
UNKNOWN_CONTEXT_REFERENCE
UNKNOWN_WORK_REFERENCE
UNKNOWN_RECEIPT_REFERENCE
UNKNOWN_EVIDENCE_REFERENCE
UNKNOWN_PERSISTENCE_REFERENCE
UNREACHABLE_SUPPORT_REFERENCE
ORPHAN_REQUIRED_WORK
UNRECONCILED_REQUIRED_WORK
UNRESOLVED_REQUIRED_PERSISTENCE
OPEN_REQUIRED_REENTRY
INVALID_TERMINAL_STATUS
INVALID_PARTIAL_WITH_NO_FULFILLMENT
INVALID_BLOCKED_WITH_NO_BLOCKER
INVALID_FAILED_WITH_NO_FAILURE
SATISFIED_WITH_MATERIAL_GAP
COMPLETION_ASSESSOR_REPAIR_EXHAUSTED
COMPLETION_REQUIREMENT_COVERAGE_FAILURE
COMPLETION_STATUS_MUTATION
COMPLETION_COMPOSER_REPAIR_EXHAUSTED
FINAL_STANDING_PACKET_VALIDATION_FAILED
```

---

# 41. EXAMPLE — FIND AND REMEMBER

User:

```text
"Find the latest version of X and remember it."
```

Intent:

```text
R001 = establish latest version
R002 = remember established version
```

Outcome:

```text
EF003 establishes version 4.2
PRC001 SUCCESS commits durable claim
```

Completion:

```text
R001 -> SATISFIED
R002 -> SATISFIED
```

Result later articulates both.

---

# 42. EXAMPLE — PERSISTENCE FAILS

Same user request.

Outcome:

```text
EF003 establishes version 4.2
PRC001 FAILED
```

Completion:

```text
R001 -> SATISFIED
R002 -> FAILED
```

Result must communicate both:

```text
version found
save did not complete
```

Howard may not collapse this into “Done.”

---

# 43. EXAMPLE — PARTIAL INFORMATION

User requests:

```text
"Give me the release date, price, and supported platforms."
```

Outcome:

```text
release date established
supported platforms established
price not established
no further valid source path remains in turn
```

Completion:

```text
R001 -> PARTIALLY_SATISFIED
```

with:

```text
fulfilled = date, platforms
unmet = price
```

---

# 44. EXAMPLE — BLOCKED USER INPUT

User:

```text
"Save the file there."
```

Resolved intent requires destination, but no destination can be established.

No execution occurs.

Completion:

```text
R001 -> BLOCKED
blocker = destination path required
```

Result asks/provides the concise next needed information.

---

# 45. EXAMPLE — EXECUTION FAILURE

User requires a file save.

Decision/work valid.

Execution attempts authorized save and receives definitive failure.

No alternate route succeeds.

Completion:

```text
R001 -> FAILED
```

Result reports that the save did not complete.

---

# 46. ZERO-WORK INFORMATIONAL ANSWER

Some requirements need no external tool.

If:

```text
Intent requirement is answerable from valid Context
Decision = READY
no material gaps
no Persistence requirement
```

Completion may return:

```text
SATISFIED
```

when the validated user-facing result is present in the closure bundle.

Result still must articulate that result to the user.

---

# 47. OPEN CONFLICT

If a requirement depends on a conflict that remains materially unresolved:

```text
two incompatible claims
no authority/freshness basis resolves them
```

Completion must not fabricate satisfaction.

Possible standing depends on what the user requested:

```text
PARTIALLY_SATISFIED
  if useful bounded answer can still be given with conflict disclosure

BLOCKED
  if the unresolved conflict prevents a legitimate answer
```

Assessor decides from exact requirement semantics.

---

# 48. ADVISORY PERSISTENCE DOES NOT CONTROL COMPLETION

If an advisory candidate fails to save:

```text
candidate result = FAILED
```

but the user never required Persistence, the primary Rxxx may still be:

```text
SATISFIED
```

Completion must distinguish:

```text
normative requirement obligation
vs
advisory system memory housekeeping
```

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


# R2A. CLOSURE-PACKET PROJECTION RECALL

The host must benchmark whether every Requirement Closure Bundle includes all artifacts required to reach the known correct standing. Missing required refs are host packet-construction failures, not adapter failures.

Completion trust testing must include `SUCCESS + PROVISIONAL`, explicit confirmation, later compensation history, and failed Persistence as distinct cases.

---

# 49. REQUIRED COMPLETION ACCEPTANCE TESTS

At minimum:

1. Single satisfied informational requirement.
2. Single satisfied verified external action.
3. Find + remember both satisfied.
4. Find satisfied + required remember failed.
5. Duplicate remember with Persistence `NO_CHANGE_NEEDED` still satisfies remember requirement.
6. Advisory Persistence failure does not falsely fail requirement.
7. Genuine partial result -> `PARTIALLY_SATISFIED`.
8. Partial status rejected when nothing was fulfilled.
9. Missing user prerequisite -> `BLOCKED`.
10. Tool failure -> `FAILED`.
11. Required Persistence policy rejection mapped correctly from requirement semantics.
12. Open evidence conflict preserved.
13. Context valid unresolved state considered.
14. Multiple Rxxx independently closed.
15. Shared Wxxx supports two requirements without merging statuses.
16. Superseded Decision work not treated as missing.
17. Unexecuted compilation failure included.
18. Discovery re-entry artifacts remain subordinate.
19. Open required RRQ prevents false satisfaction.
20. Open required DN/re-entry prevents premature Completion.
21. Host provenance graph detects orphan support.
22. Invented support ref rejected.
23. Requirement coverage exact.
24. Composer cannot mutate CA status.
25. Final Standing Packet hash reproducible.

---

# 50. ADVERSARIAL COMPLETION TESTS

1. Model marks SATISFIED despite required PRC failure.
2. Model marks SATISFIED while material gap exists.
3. Model marks BLOCKED without blocker.
4. Model marks FAILED when only missing user prerequisite exists.
5. Model marks PARTIAL with zero fulfilled components.
6. Model cites unrelated EF from another Rxxx.
7. Model cites artifact from another turn.
8. Model invents receipt.
9. Model invents semantic memory commit.
10. Model requests tool retry.
11. Model creates new DN.
12. Model edits original Rxxx.
13. Model edits Context.
14. Model writes user-facing answer prose instead of structured completion.
15. Composer drops Rxxx.
16. Composer duplicates Rxxx.
17. Composer changes BLOCKED to SATISFIED.
18. Composer creates unsupported shared fact.
19. Final packet contains unvalidated status.
20. Hash tamper after Completion.

---

# 51. TRAINING TARGET — COMPLETION ASSESSOR

Training examples should contrast:

```text
SATISFIED vs PARTIALLY_SATISFIED
BLOCKED vs FAILED
required Persistence vs advisory Persistence
successful Execution vs established evidence
established evidence vs user requirement fulfillment
valid unresolved Context vs invalid upstream Context
shared work vs shared outcome
```

Especially emphasize:

```text
operation success does not imply requirement success
Persistence candidate failure does not imply user requirement failure
missing prerequisite is not the same as attempted failure
```

---

# 52. TRAINING TARGET — COMPLETION COMPOSER

Training should cover:

```text
all-satisfied turns
mixed standing turns
partial + satisfied
blocked + satisfied
failed + satisfied
shared facts
shared blockers
ordered user-facing focus
strict status preservation
strict Rxxx coverage
minimal disclosure seeds
```

Composer training must punish status mutation.

---

# 53. TRACE CAPTURE

For every Completion adapter call retain:

```text
adapter role/version
base model identity
adapter identity/hash
input schema version
policy snapshot UUID/hash
closure bundle UUID/hash
provenance graph hash
host closure signal pack
raw structured model output
parsed model output
validation report
repair attempts
accepted artifact hash
latency/token metrics
```

No hidden chain-of-thought required.

---

# 54. EXACT RECOMMENDED SOURCE LAYOUT

```text
completion/
  __init__.py
  enums.py
  models.py
  schemas.py
  policy.py
  closure_repository.py
  closure_bundle.py
  closure_signals.py
  provenance_graph.py
  integrity.py
  assessor.py
  assessor_validation.py
  composer.py
  composer_validation.py
  final_standing.py
  handoff.py
  trace.py

prompts/
  completion_assessor.txt
  completion_composer.txt

schemas/
  completion_closure_bundle.schema.json
  completion_assessor_output.schema.json
  completion_plan.schema.json
  final_standing_packet.schema.json

tests/
  test_closure_bundle.py
  test_provenance_graph.py
  test_completion_assessor_validation.py
  test_completion_composer_validation.py
  test_completion_statuses.py
  test_completion_e2e.py
```

---

# 55. COMPLETION INVARIANTS — LOCKED

```text
CPL01. Original Rxxx remains immutable.

CPL02. Completion is the first and only recipe that assigns terminal Rxxx standing.

CPL03. Terminal vocabulary is SATISFIED / PARTIALLY_SATISFIED / BLOCKED / FAILED.

CPL04. Completion creates no new work.

CPL05. Completion calls no tools.

CPL06. Completion writes no semantic Persistence.

CPL07. Completion edits no upstream artifact.

CPL08. Every Rxxx is closed exactly once.

CPL09. One Completion Assessor judges one Rxxx at a time.

CPL10. Completion Composer may organize but may not change per-Rxxx status.

CPL11. Host graph/set/hash/schema checks surround model inference.

CPL12. Required Persistence outcome participates in requirement standing.

CPL13. Advisory Persistence does not become a hidden requirement.

CPL14. PARTIALLY_SATISFIED requires genuine fulfilled material.

CPL15. BLOCKED requires an actual blocker.

CPL16. FAILED requires an actual failure basis.

CPL17. SATISFIED cannot coexist with an essential unresolved material gap.

CPL18. Final Standing Packet is immutable after validation.

CPL19. Result receives final standing; Result never rejudges it.

CPL20. Publication/delivery state is separate from semantic Completion standing.

CPL21. Every model call is bounded and fresh-KV.

CPL22. Every support ref is provenance-validated.

CPL23. No terminal status is inferred from tool HTTP/receipt success alone.

CPL24. No final prose is generated inside Completion.

CPL25. Failure is recorded rather than disguised as clean completion.
```

---

# 56. FINAL COMPLETION FLOW

```text
PERSISTENCE HANDOFF
       |
       v
COMPLETION HOST INTEGRITY GATE
       |
       v
BUILD PROVENANCE GRAPH
       |
       v
FOR EACH Rxxx
  BUILD REQUIREMENT CLOSURE BUNDLE
       |
  BUILD HOST CLOSURE SIGNALS
       |
       v
  COMPLETION ASSESSOR
       |
       v
  HOST VALIDATION / bounded repair
       |
       v
  CAxxx
       |
       v
CLEAR KV
       |
       v
COMPLETION COMPOSER
       |
       v
HOST COVERAGE / STATUS-PRESERVATION VALIDATION
       |
       v
CPxxx
       |
       v
HOST FREEZES FSPxxx
       |
       v
RECIPE 8 — RESULT
```

---

# 57. PROTOTYPE BUILD GATE

Do not integrate Result until:

```text
all Completion acceptance tests pass
all adversarial tests pass
status coverage is exact
FSP hash reproducible
Composer cannot mutate statuses
support graph integrity is proven
```

---

# 58. FINAL DESIGN SUMMARY

```text
COMPLETION QUESTION
  Where does each original requirement finally stand?

NEW ADAPTERS
  1. Completion Assessor
  2. Completion Composer

HOST
  builds exact closure bundles
  uses SQLite
  validates provenance graph
  derives mechanical closure signals
  validates schemas/refs/status consistency
  freezes Final Standing Packet

TERMINAL STATUS
  SATISFIED
  PARTIALLY_SATISFIED
  BLOCKED
  FAILED

NO NEW WORK
NO TOOL EXECUTION
NO MEMORY WRITE
NO FINAL PROSE

OUTPUT
  immutable FSPxxx
  ready for conversational articulation
```

**END OF A.R.C.A.D.I.A. COMPLETION RECIPE PROTOTYPE BUILD SPECIFICATION — 2026-08-28**
