# A.R.C.A.D.I.A. v0.1 — Canonical Recipe Contract

**v0.1 integration status:** The detailed semantic recipe body below is carried forward from the final pre-v0.1 trust/recovery specification because R3 intentionally did not change semantic recipe ownership. It is now governed by the v0.1 common runtime/AAE/source/recovery/trace/performance contracts in this bundle.

**Conflict rule:** if this carried-forward body contains older wording about adapter loading, generic adapter runtime, source-quality being unresolved, trace retention, crash replay, global sampling, handwritten AAE framing, or model-call necessity, the v0.1 system documents `01`–`09` supersede that wording. Semantic recipe responsibilities, artifacts, edge cases, and tests remain authoritative unless explicitly superseded.

---

# A.R.C.A.D.I.A. TOOL / EXECUTION RECIPE
## Prototype Build Specification — Command-Window Reference
**Status:** LOCKED PROTOTYPE DESIGN  
**Scope:** TOOL HANDOFF + EXECUTION ONLY  
**Date:** 2026-08-28  
**Parent:** `ARCADIA_DECISION_RECIPE_PROTOTYPE_BUILD_SPEC_2026-08-28.md`  
**Next Stage:** Reconciliation Recipe  
**Purpose:** Archive-ready source-of-truth specification for implementing and independently testing A.R.C.A.D.I.A.'s initial Tool / Execution layer. This stage accepts validated Decision work items, compiles narrow host-owned tool requests, invokes registered capabilities, creates immutable host receipts, and returns exact operation results downstream without deciding what those results ultimately mean.

---

> **CONFIRMED LOGIC INTEGRATION — R2 — 2026-08-28**  
> This R2 document integrates the confirmed trust/recovery logic locked after the AAE five-slice review: single-source AAE/runtime/training contracts, base-model baselining, full trace capture with a training-data firewall, packet-projection testing, aggregate loop telemetry, durable-provisional semantic Persistence with next-turn review, controlled user memory correction, deterministic-first semantic support, and mode-specific Howard evaluation.  
> **Source-quality / source-authority ranking is intentionally NOT defined by this update. It remains a separate required design lane.**


# 0. CORE RULE

Execution answers one question:

> **What actually happened when the host attempted the authorized work item?**

Decision says what should be attempted.

Execution performs the attempt.

The host—not a model—establishes whether an operation actually occurred.

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
HOST EXECUTES TOOL
  |
  v
REC001
```

A model may request an operation.

Only a host receipt establishes that the operation was attempted or completed.

---

# 1. POSITION IN THE FULL RECIPE SPINE

```text
INTENT
  |
  v
CONTEXT
  |
  v
DECISION
  |
  | validated Wxxx graph
  v
TOOL / EXECUTION
  |
  | immutable host receipts + returned payloads
  v
RECONCILIATION
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

Execution does not judge final requirement satisfaction.

It reports operation reality.

---

# 2. INITIAL TOOL SURFACE — LOCKED PROTOTYPE

The initial registered tool surface is:

```text
Google / Search
Wiki
Load File
Save File
```

SQLite is **not** an ordinary Tool / Execution capability in this prototype.

SQLite durable state belongs to the separate Persistence recipe.

Future capabilities may be added through the host capability registry without changing the core Tool / Execution contract.

---

# 3. ADAPTER COUNT — LOCKED

The Tool / Execution prototype uses:

```text
ZERO dedicated tool adapters
```

No Google adapter.

No Wiki adapter.

No Load File adapter.

No Save File adapter.

The two learned adapters belonging to this area are already in Decision:

```text
Requirement Assessor
Plan Composer
```

Tool execution is host-dominant.

A future general Tool Request Builder adapter is an optional candidate only if logs prove that Decision consistently identifies the right work while query/request construction remains a measurable semantic weakness.

Do not allocate that adapter in the prototype.

---

# 4. WHY TOOLS DO NOT GET ONE ADAPTER EACH

Tool availability and schemas are changing runtime facts.

They should live in host-supplied capability definitions rather than model weights.

Avoid adapter sprawl such as:

```text
Google adapter
Wiki adapter
File adapter
GitHub adapter
Weather adapter
Email adapter
...
```

A model should learn capability literacy and planning patterns.

The host should supply exact current capability state.

---

# 5. EXECUTION INPUT CONTRACT

Execution receives a host-validated Decision handoff.

Minimum required state:

```text
turn_id
Decision run ID
Decision revision
Decision handoff hash
capability registry version
active executable work items
work dependency graph
parallel groups
active/superseded work state
requirement links
Context/input refs needed by each work item
```

Execution must reject any work item not present in the accepted Decision handoff.

---

# 6. WORK ITEM AUTHORITY

`Wxxx` is the authority for why a tool operation exists.

Tool requests may narrow/compile the work item into a tool-specific argument packet.

They may not broaden its semantic goal.

Invalid:

```text
W001:
Load file A read-only.

TRQ001:
Delete file A.
```

Valid:

```text
W001:
Load file A read-only.

TRQ001:
load_file(path=A)
```

The host validates request-to-work alignment before execution.

---

# 7. ID NAMESPACES

Tool / Execution adds:

```text
TRQ001  Tool Request
REC001  Host Tool Receipt
```

Existing IDs remain:

```text
R001    authoritative requirement
W001    work item
C001    Context point
L001    Context lane
DN001   Derived Need created later by Reconciliation
```

Do not use `Txxx` for tool requests because Intent may use it for term candidates.

---

# 8. CAPABILITY REGISTRY — HOST AUTHORITY

The host owns the registry.

Each capability entry should describe at least:

```text
capability_id
capability_version
capability_class
operation_kinds
work_types_supported
availability
read_or_write
side_effect_class
input_schema
receipt_schema
permission / restriction metadata
idempotency behavior
timeout policy
concurrency policy
```

The registry is runtime state.

A stale conversation claim cannot override it.

---

# 9. CAPABILITY CLASSES

Initial broad classes:

```text
INFORMATION_TOOL
ACTION_TOOL
```

### INFORMATION_TOOL

Produces information/evidence without intentionally changing user/project external state.

Prototype:

```text
Google / Search
Wiki
Load File
```

### ACTION_TOOL

Attempts an external state change.

Prototype:

```text
Save File
```

SQLite remains outside this taxonomy for this recipe because its write authority belongs to Persistence.

---

# 10. TOOL HANDOFF LAYER

Tool Handoff is not another semantic recipe adapter.

It is the host-controlled translation boundary between `Wxxx` and the concrete tool invocation.

```text
DECISION HANDOFF
      |
      v
W001
      |
      v
HOST TOOL REQUEST COMPILER
      |
      v
TRQ001
      |
      v
SCHEMA + AUTHORITY VALIDATION
      |
      v
TOOL EXECUTOR
```

---

# 11. TOOL REQUEST CONTRACT

Recommended common envelope:

```json
{
  "tool_request_id": "TRQ001",
  "turn_id": "...",
  "decision_run_id": "DR001",
  "work_id": "W001",
  "requirement_ids": ["R001"],
  "capability_id": "google_search",
  "capability_version": "prototype-1",
  "operation_kind": "SEARCH",
  "goal": "Establish current official operating hours.",
  "arguments": {
    "query": "..."
  },
  "evidence_target": [
    "correct entity identity",
    "current operating hours"
  ],
  "input_refs": ["C004"],
  "side_effect_class": "READ_ONLY",
  "attempt_number": 1,
  "idempotency_key": null
}
```

Every tool request remains traceable to `Wxxx` and therefore to `Rxxx`.

---

# 12. REQUEST COMPILATION

The prototype host request compiler performs deterministic assembly.

It may:

- copy the chosen capability ID from validated Decision;
- copy `query_hint` into a Google query field;
- canonicalize file paths according to host rules;
- populate IDs;
- populate registry version;
- populate attempt number;
- populate timeout/idempotency metadata;
- validate argument shapes.

It may not semantically invent a different search goal.

If the Decision work item lacks enough semantic data to construct a valid request, return the work item as non-executable rather than guessing.

That condition belongs to downstream repair/replanning.

---

# 13. GOOGLE / SEARCH REQUEST

Prototype conceptual arguments:

```text
query
optional freshness hint
optional domain/source restrictions when Decision supplied them
optional result limit controlled by host configuration
```

Required links:

```text
TRQxxx -> Wxxx -> Rxxx
```

The host may execute several Google requests in the same turn.

There is no "one Google per turn" rule.

---

# 14. MULTIPLE GOOGLE OPERATIONS

Two searches are legitimate when Decision created distinct evidence targets.

Example:

```text
W001
find official current information

W002
find independent current corroboration
```

Execution:

```text
W001 -> TRQ001 -> GOOGLE -> REC001
W002 -> TRQ002 -> GOOGLE -> REC002
```

If Decision marked them independent, the host may execute them concurrently.

---

# 15. WIKI REQUEST

Prototype conceptual arguments:

```text
topic / title query
optional section/lookup hint when supported
```

Wiki is best treated as a reference-information capability.

Execution does not decide whether Wiki is fresh enough for the user's requirement.

Decision defines the evidence target.

Reconciliation later judges the returned information against it.

---

# 16. LOAD FILE REQUEST

Prototype conceptual arguments:

```text
path or host-resolved file reference
read mode / bounded content policy
optional expected type
```

Load File is read-only.

The host owns path resolution and access policy.

A model-provided string is not authority to read arbitrary paths.

Receipt must identify what file was actually read.

---

# 17. SAVE FILE REQUEST

Prototype conceptual arguments:

```text
destination path or host-approved file reference
content artifact reference
write mode
optional expected extension/type
```

Save File is an external write action.

The host owns:

- path permission;
- overwrite rules;
- atomic write behavior;
- collision handling;
- write verification;
- hash calculation;
- final receipt.

The model cannot claim a file exists merely because it requested a save.

---

# 18. SAVE FILE VS SQLITE PERSISTENCE — LOCKED

```text
SAVE_FILE
= write a user/project file through Execution

SQLITE PERSISTENCE
= preserve durable A.R.C.A.D.I.A. knowledge/state through Persistence
```

Do not route SQLite through the Tool / Execution request compiler.

Do not allow a generic "save" capability to blur these two meanings.

---

# 19. PRE-EXECUTION HOST VALIDATION

Before invoking any capability, verify:

```text
Decision handoff hash valid
Wxxx exists and is active
Wxxx not superseded-before-execution
TRQxxx unique
Rxxx refs match Wxxx ownership
capability exists
capability version matches allowed registry
capability available
operation kind supported
work type compatible
arguments schema-valid
required input refs exist
side-effect class matches capability
permissions/restrictions satisfied
idempotency metadata valid for write actions
dependency requirements satisfied
```

If any hard gate fails, do not call the tool.

Create a host receipt describing rejection before execution.

---

# 20. TOOL RECEIPT IS THE AUTHORITY

A receipt is the host's immutable record of the attempted operation.

A tool/model result without a host receipt is not sufficient proof of execution.

Examples:

```text
Google result -> host receipt
Wiki result -> host receipt
Load File -> host receipt
Save File -> success/failure receipt
```

The receipt must distinguish:

```text
request accepted
operation attempted
operation returned
external write verified
```

where applicable.

---

# 21. COMMON RECEIPT CONTRACT

Recommended envelope:

```json
{
  "receipt_id": "REC001",
  "tool_request_id": "TRQ001",
  "turn_id": "...",
  "decision_run_id": "DR001",
  "work_id": "W001",
  "requirement_ids": ["R001"],
  "capability_id": "google_search",
  "operation_kind": "SEARCH",
  "attempt_number": 1,
  "execution_status": "SUCCESS",
  "started_at": "...",
  "finished_at": "...",
  "result_items": [],
  "error": null,
  "side_effect_confirmation": null,
  "receipt_hash": "..."
}
```

Receipts are host-owned artifacts.

---

# 22. EXECUTION STATUS VOCABULARY

Initial host status vocabulary:

```text
SUCCESS
PARTIAL
NO_RESULT
FAILED
TIMEOUT
REJECTED_BEFORE_EXECUTION
CANCELLED
```

`SUCCESS` means the capability operation completed according to its execution protocol.

It does **not** mean the requirement is satisfied.

`NO_RESULT` may still be a valid operation outcome.

`PARTIAL` may still contain useful evidence.

Reconciliation owns semantic interpretation.

---

# 23. INFORMATION RECEIPT RESULT ITEMS

For information tools, each result item should be host-normalized enough for downstream provenance while preserving source payload as needed.

Recommended fields:

```text
result_item_id
source_identity / URI / title when available
content or bounded content artifact ref
source metadata
retrieved_at
source timestamp when available
content_hash
raw_payload_ref when debug retention is enabled
```

Do not make Tool / Execution decide whether the source is true, authoritative, relevant enough, or contradictory.

That is downstream Reconciliation work.

---

# 24. GOOGLE RECEIPT

A Google/Search receipt should preserve at least:

```text
exact executed query
search provider/capability ID
execution status
returned result items
retrieved_at
provider metadata when available
```

If the provider returns zero results:

```text
execution_status: NO_RESULT
```

Do not fabricate fallback information.

---

# 25. WIKI RECEIPT

Preserve:

```text
exact lookup term
resolved article/page identity when available
returned bounded content
source URL/identifier
retrieved_at
execution status
```

Wrong-page or ambiguous-page results are still operation results.

Reconciliation determines whether another lookup is needed.

---

# 26. LOAD FILE RECEIPT

Preserve:

```text
requested file ref/path
host-resolved actual file identity
read status
size
content hash
content artifact or bounded content
file metadata when available
```

A successful read does not mean the file contained the needed information.

---

# 27. SAVE FILE RECEIPT

A successful Save File receipt should preserve:

```text
requested destination
host-resolved actual destination
write status
bytes written
content hash
post-write verification status
overwrite/new-file state when relevant
```

Recommended success requirement:

```text
write completed
AND
post-write host verification passed
```

Only then may:

```text
execution_status: SUCCESS
```

be used for a Save File operation.

---

# 28. RECEIPT IMMUTABILITY

Once created, a receipt is append-only historical fact.

A later Decision revision may mark old work superseded.

It cannot erase the receipt.

A later repair may create:

```text
W005 -> TRQ007 -> REC009
```

The original:

```text
REC004
```

remains in the ledger.

---

# 29. DEPENDENCY SCHEDULING

Execution receives the validated work dependency graph.

The host determines runnable work:

```text
all dependencies satisfied
work active
capability available
no cancellation/supersession
```

Logical dependency belongs to Decision.

Scheduling belongs to the host.

---

# 30. PARALLEL EXECUTION

If Decision marks several work items independent, the host may run them in parallel subject to capability/runtime policy.

Example:

```text
PG001
  W001 Google
  W002 Wiki
```

Each operation receives its own `TRQxxx` and `RECxxx`.

Parallelism must never merge receipts into an ambiguous combined blob.

---

# 31. SUPERSEDED-BEFORE-EXECUTION WORK

If scoped Decision re-entry supersedes a pending work item before execution:

```text
W002 state:
SUPERSEDED_BEFORE_EXECUTION
```

The Tool layer must not execute it.

No fake success/failure receipt should be created for an operation that was never attempted.

The ledger records the work-state transition separately.

---

# 32. TRANSPORT RETRY VS SEMANTIC FOLLOW-UP

These are different.

### Transport retry

Same `Wxxx`, same semantic operation, repeated because of a clearly transient execution failure.

Example:

```text
provider connection reset before response
```

A retry creates a new `TRQxxx` attempt linked to the same `Wxxx`.

### Semantic follow-up

New query/work because returned evidence was insufficient, contradictory, or exposed a new need.

That is **not** an Execution auto-retry.

It goes:

```text
Receipt
  -> Reconciliation
  -> possible DNxxx / Context update
  -> Decision re-entry
  -> new Wxxx
```

---

# 33. PROTOTYPE RETRY POLICY

Recommended host default:

```text
maximum automatic transport retry: 1
```

Only retry failures classified by host/capability adapter as transient and safe to repeat.

For side-effecting Save File, retry only when idempotency/write-verification rules prove duplicate or ambiguous writes will not be created.

Do not automatically retry:

```text
NO_RESULT
wrong page
irrelevant result
valid empty file
permission rejection
invalid arguments
semantic insufficiency
source disagreement
```

Those require downstream judgment.

---

# 34. REQUEST VALIDATION FAILURE

If `TRQxxx` cannot pass schema/authority validation:

```text
execution_status:
REJECTED_BEFORE_EXECUTION
```

The receipt/error metadata should identify the exact host reason.

Examples:

```text
INVALID_ARGUMENT_SCHEMA
UNKNOWN_CAPABILITY
CAPABILITY_DISABLED
UNAUTHORIZED_SIDE_EFFECT
DEPENDENCY_NOT_SATISFIED
WORK_ITEM_SUPERSEDED
PATH_REJECTED
```

Do not call the tool and then pretend the rejected request failed externally.

---

# 35. TOOL RESULT IS NOT CONTEXT YET

A receipt is operation evidence.

It is not automatically an active Context point.

```text
REC001
```

does not itself mean:

```text
C017 supported fact
```

Reconciliation must determine what the result actually established.

Only validated downstream Context revision/promotion makes new grounded Context active.

---

# 36. DISCOVERY BELONGS DOWNSTREAM

Tool / Execution does not decide:

> "This new term is important enough to become a new lane."

It returns exact operation results.

Reconciliation may later identify:

```text
DN001
```

from one or more receipts.

The Tool layer must preserve enough exact provenance for that judgment to be auditable.

---

# 37. DISCOVERY LOOP INTERFACE

Canonical downstream flow:

```text
W001 -> TRQ001 -> GOOGLE -> REC001
W002 -> TRQ002 -> GOOGLE -> REC002
                         |
                         v
                  RECONCILIATION
                         |
                         | useful new term/gap
                         v
                       DN001
                         |
                         v
                   HOST VALIDATION
                         |
                         v
              official Context lane/revision
                         |
                         v
                    Howard comment
                         |
                         v
                 Decision re-entry
                         |
                         v
                       W003
                         |
                         v
                      Google
```

The new work is additive.

Nothing replaces the original result packet or requirement history.

---

# 38. OFFICIAL LANE PROMOTION + HOWARD COMMENT — EXECUTION INTERFACE RULE

Execution itself does not promote lanes.

But its receipts must support the locked downstream rule:

> When a validated discovery/re-entry packet is officially promoted into a Context lane or lane revision, the host attaches a bounded Howard comment explaining the lane's purpose and provenance.

Receipt references used by that comment must remain resolvable.

Example:

```text
Howard_comment:
"REC001 and REC002 exposed the term 'XYZ', which is needed to continue R001. This lane was added without replacing the original requirement."
```

The comment remains commentary/provenance, not execution authority.

---

# 39. RESULT PACKET IS ADDITIVE

The turn ledger grows.

Do not replace earlier artifacts with a newly flattened packet.

Conceptual history:

```text
TURN
|
+-- Intent
|    +-- R001
|
+-- Context
|    +-- C001
|
+-- Decision
|    +-- W001
|    +-- W002
|
+-- Tool Requests
|    +-- TRQ001
|    +-- TRQ002
|
+-- Receipts
|    +-- REC001
|    +-- REC002
|
+-- Reconciliation
|    +-- DN001
|
+-- Context Revision
|    +-- L004 / C009
|
+-- Decision Re-entry
|    +-- W003
|
+-- Tool Request
|    +-- TRQ003
|
+-- Receipt
     +-- REC003
```

Active state can change.

History remains.

---

# 40. INFORMATION TOOL FAILURE DOES NOT AUTOMATICALLY END THE TURN

Example:

```text
REC001 -> FAILED
REC002 -> SUCCESS
```

Execution reports both.

It does not decide whether `R001` can still be answered from `REC002`.

Reconciliation and Completion own those judgments.

---

# 41. ACTION TOOL FAILURE DOES NOT GET HIDDEN

Example:

```text
Save File requested
write permission denied
```

Receipt:

```text
execution_status: REJECTED_BEFORE_EXECUTION
```

or:

```text
FAILED
```

according to where the failure occurred.

Do not silently fall back to claiming the file was saved.

Result may later report the failure truthfully.

---

# 42. ALL_WORK_SUCCEEDED VS READY_FOR_RESULT

Execution should never conflate these concepts.

Example:

```text
all_work_succeeded: false
```

may coexist later with:

```text
ready_for_result: true
```

because a failed operation can be fully understood and truthfully reportable.

Execution's job is to preserve accurate work outcomes so later stages can make that distinction.

---

# 43. PERMISSION / AUTHORITY PRINCIPLE

Capability knowledge does not grant authority.

The host controls:

- current availability;
- permission scope;
- path scope;
- side-effect policy;
- execution;
- retries;
- cancellation;
- receipts.

A Decision model may select a capability.

The host may still reject execution under current runtime policy.

The receipt must show that truth.

---

# 44. NO TOOL WHEN NO WORK EXISTS

If Decision produces:

```text
work_items: []
```

Execution performs zero operations.

It records a valid empty Execution stage and passes onward.

Do not invent a search merely because the Tool recipe ran.

---


# R2. UNDO / REVERSAL SEMANTICS — LOCKED

User language such as:

```text
"undo that"
"undo your last tool calls"
"don't save that"
```

must never erase immutable execution history.

Rules:

```text
past TRQ/REC receipts remain immutable facts
semantic-memory reversal uses Persistence compensation, not receipt deletion
an external ACTION_TOOL is reversible only if its capability explicitly exposes a validated compensating operation
irreversible external side effects remain historical reality and must be disclosed
```

If a capability supports compensation, the compensation is a **new authorized work item / request / receipt chain** linked to the original side effect. It is never represented as though the original operation did not occur.

For Save File or other host-owned reversible operations, policy may expose explicit restore/delete compensation only when the host can verify the previous and resulting state.

---

# 45. REQUEST/RECEIPT HASHING

Recommended host integrity fields:

```text
Decision handoff hash
Tool request hash
Receipt hash
result-item content hashes
```

Hashes support:

- debugging;
- immutable history checks;
- exact re-entry provenance;
- training artifact verification;
- detecting accidental mutation.

---

# 46. IDEMPOTENCY FOR WRITE TOOLS

Save File should receive a host-generated idempotency key when retry could otherwise duplicate state.

Recommended conceptual rule:

```text
same Wxxx + same intended content + same authorized destination
-> stable idempotency identity for retry window
```

Do not rely on the model to reason about filesystem atomicity.

The host owns write safety.

---

# 47. CANCELLATION

If a work item is cancelled before execution:

```text
work state: CANCELLED_BEFORE_EXECUTION
```

No operation receipt claiming an attempt should be fabricated.

If cancellation occurs during an already-started operation, the host records the real capability outcome and uses:

```text
execution_status: CANCELLED
```

only if the executor can establish that state.

---

# 48. TIMEOUTS

Timeout is an execution fact.

Receipt should include:

```text
execution_status: TIMEOUT
attempt_number
elapsed time
whether any partial result payload was received
whether side effects are known/unknown for write operations
```

For writes, an ambiguous timeout must not be treated as a clean failure if the host cannot prove whether the write occurred.

Preserve ambiguity for Reconciliation/repair policy.

---

# 49. PARTIAL RESULTS

A tool may legitimately return partial data.

Example:

```text
Load File read first bounded segment due size policy.
```

or:

```text
Search provider returned some results before an upstream error.
```

Receipt:

```text
execution_status: PARTIAL
```

Preserve the partial payload and exact limitation.

Reconciliation decides whether it is enough.

---

# 50. TOOL-SPECIFIC RESULT NORMALIZATION

Normalize only what improves downstream reliability without destroying source fidelity.

Allowed host normalization:

- stable IDs;
- timestamps;
- canonical field names;
- bounded content storage;
- hashes;
- source URL separation;
- encoding cleanup when exact raw payload is still recoverable in debug artifacts.

Do not semantically summarize every tool result inside Execution.

That would create a hidden Reconciliation stage.

---

# 51. RAW PAYLOAD RETENTION

For debug/training builds, retain raw tool payloads or safe references to them when feasible.

The active downstream packet may use bounded normalized content.

This gives both:

```text
runtime efficiency
+
forensic reproducibility
```

Sensitive/private payload retention must follow host policy.

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
pathlib
os
shutil
tempfile
typing
concurrent.futures or asyncio according to runtime
```

Tool-provider-specific clients belong behind capability executors.

Do not expose provider internals to Decision.

---

# 53. RECOMMENDED EXECUTOR INTERFACE

Conceptual Python interface:

```text
validate_request(tool_request) -> ValidationReport
execute(tool_request) -> RawExecutionOutcome
normalize(raw_outcome) -> ReceiptPayload
build_receipt(...) -> HostReceipt
```

Each capability executor implements the same host-facing lifecycle.

---

# 54. RECOMMENDED SOURCE LAYOUT

```text
tool_execution_prototype/
|
+-- tool_execution_prototype.py
+-- README.md
|
+-- execution/
|   +-- models.py
|   +-- registry.py
|   +-- scheduler.py
|   +-- request_compiler.py
|   +-- validation.py
|   +-- receipts.py
|   +-- provenance.py
|   +-- hashing.py
|   +-- retry.py
|   +-- ledger.py
|
+-- tools/
|   +-- google_search.py
|   +-- wiki_lookup.py
|   +-- load_file.py
|   +-- save_file.py
|
+-- schemas/
|   +-- tool_request.schema.json
|   +-- information_receipt.schema.json
|   +-- action_receipt.schema.json
|   +-- google_request.schema.json
|   +-- wiki_request.schema.json
|   +-- load_file_request.schema.json
|   +-- save_file_request.schema.json
|
+-- fixtures/
|   +-- capabilities.prototype.json
|
+-- tests/
    +-- test_request_compiler.py
    +-- test_registry.py
    +-- test_google.py
    +-- test_wiki.py
    +-- test_load_file.py
    +-- test_save_file.py
    +-- test_receipts.py
    +-- test_dependencies.py
    +-- test_parallel.py
    +-- test_retry.py
    +-- test_idempotency.py
    +-- test_execution_end_to_end.py
```

---

# 55. SCHEMA GATES

Every Tool Request crosses:

```text
WORK ITEM
   |
   v
REQUEST COMPILATION
   |
   v
COMMON REQUEST SCHEMA
   |
   v
TOOL-SPECIFIC SCHEMA
   |
   v
AUTHORITY / REGISTRY CHECK
   |
   v
EXECUTION
```

Every result crosses:

```text
RAW TOOL OUTCOME
   |
   v
NORMALIZATION
   |
   v
RECEIPT SCHEMA
   |
   v
HASH / PROVENANCE CHECK
   |
   v
LEDGER APPEND
   |
   v
RECONCILIATION HANDOFF
```

---

# 56. EXECUTION HANDOFF TO RECONCILIATION

Recommended packet:

```text
EXECUTION_HANDOFF

turn_id
Decision run/revision
Decision handoff hash
capability registry version

work_execution_state
  Wxxx active/completed/failed/pending/superseded

tool_requests
  TRQxxx

receipts
  RECxxx

unexecuted_work
  with exact reasons

execution_summary
  operation counts only
  no semantic claim that requirements are satisfied

provenance
  hashes
  timestamps
```

Reconciliation receives exact receipts plus the original Decision evidence targets.

---

# 57. PERMANENT TURN LEDGER ADDITIONS

Execution appends:

```text
TOOL_REQUESTS
  TRQ001
  TRQ002

TOOL_RECEIPTS
  REC001
  REC002

WORK_EXECUTION_STATE

EXECUTION_ATTEMPTS

EXECUTION_VALIDATION

CAPABILITY_REGISTRY_SNAPSHOT_REF
```

It does not overwrite Decision history.

---

# 58. COMMAND-WINDOW DISPLAY

Recommended development trace:

```text
[EXECUTION]
Decision: DR001 rev 1
Runnable: W001 W002

[TRQ001] W001 -> google_search
  validate .... PASS
  execute ..... SUCCESS
  receipt ..... REC001

[TRQ002] W002 -> wiki_lookup
  validate .... PASS
  execute ..... NO_RESULT
  receipt ..... REC002

Execution complete.
2 work items attempted.
Semantic sufficiency: NOT JUDGED HERE.
Handoff -> Reconciliation
```

For Save File:

```text
[TRQ005] W004 -> save_file
  authority ... PASS
  write ........ PASS
  verify ....... PASS
  receipt ...... REC007 SUCCESS
```

---

# 59. REQUIRED RUN ARTIFACTS / DEBUG TRACE

Record at minimum:

```text
exact Decision handoff ref/hash
capability registry snapshot/version
scheduler decisions
exact TRQxxx objects
validation reports
provider invocation timing
attempt number
raw outcome ref
normalized receipt
receipt hash
write verification details
transport retry decisions
cancellation/supersession state
```

No adapter KV instrumentation is needed because this prototype uses no Tool adapters.

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


# R2A. AGGREGATE EXECUTION BUDGET TRACE

Execution appends per-requirement/turn counters supplied by the host budget ledger, including work expansion, retry count, compensation count, and terminal budget-stop reason when present. Transport retry remains distinct from semantic re-entry.

---

# 60. INDEPENDENT SLICE TESTING

Required targets:

```text
test_tool_request_common_envelope
test_google_request
test_wiki_request
test_load_file_request
test_save_file_request
test_request_work_alignment
test_receipt_creation
test_receipt_immutability
test_no_result
test_partial_result
test_timeout
test_rejected_before_execution
test_dependency_scheduler
test_parallel_execution
test_transport_retry
test_semantic_no_auto_retry
test_save_idempotency
test_save_verification
test_zero_work_path
test_execution_end_to_end
```

---

# 61. REQUIRED FAILURE TESTS

At minimum:

1. Unknown `Wxxx` request.
2. Tool request references wrong `Rxxx`.
3. Capability missing from registry.
4. Capability disabled.
5. Work type/capability mismatch.
6. Illegal argument schema.
7. Load File path rejected by host policy.
8. Save File tries unauthorized destination.
9. Save File write succeeds but verification fails.
10. Save File timeout leaves ambiguous write state.
11. Pending work becomes superseded before invocation.
12. Dependency not satisfied.
13. Two parallel operations accidentally share one receipt ID.
14. Search returns no results and executor invents fallback evidence.
15. Wiki returns wrong page and executor labels requirement satisfied.
16. Tool result is automatically inserted into Context without Reconciliation.
17. Search reveals a new term and Execution rewrites Intent directly.
18. Semantic insufficiency causes blind same-query retry loop.
19. Transport retry accidentally duplicates an external write.
20. Tool/model claims success without a host receipt.

---

# 62. EXAMPLE A — GOOGLE SUCCESS BUT SEMANTIC STATUS UNKNOWN

Decision:

```text
W001
work_type: CURRENT_EXTERNAL_INFORMATION
preferred_capability: google_search
evidence_target:
  current official hours
```

Execution:

```text
TRQ001
  -> Google
  -> provider returns results
```

Host:

```text
REC001
execution_status: SUCCESS
```

Execution stops there.

It does not claim:

```text
R001 SATISFIED
```

Reconciliation examines whether the returned pages actually establish the hours.

---

# 63. EXAMPLE B — TWO GOOGLE SEARCHES

Decision:

```text
W001 official evidence
W002 independent corroboration
parallel_group: PG001
```

Execution:

```text
TRQ001 -> Google -> REC001
TRQ002 -> Google -> REC002
```

Each receipt preserves exact query and returned results.

Downstream may compare them.

---

# 64. EXAMPLE C — DISCOVERY CREATES NEW WORK DOWNSTREAM

Execution returns valid:

```text
REC001
REC002
```

The results expose a technical term not present in original Intent.

Execution does nothing semantic with that fact.

Reconciliation later creates:

```text
DN001
```

After host validation and official lane promotion, the lane receives a Howard comment.

Decision re-entry creates:

```text
W003
work_origin: DISCOVERY
```

Execution then performs:

```text
W003 -> TRQ003 -> Google -> REC003
```

The packet grows rather than replacing `REC001/REC002`.

---

# 65. EXAMPLE D — SAVE FILE

Decision:

```text
W004
work_type: SAVE_USER_FILE
preferred_capability: save_file
side_effect: EXTERNAL_WRITE
```

Tool compiler:

```text
TRQ006
```

Host validates destination and content artifact.

Host writes atomically.

Host verifies content/hash.

Receipt:

```text
REC008
execution_status: SUCCESS
actual_path: ...
content_hash: ...
verification: PASS
```

Only `REC008` establishes that the save occurred.

---

# 66. EXAMPLE E — NO RESULT

Google runs successfully but finds nothing useful at provider level.

Receipt:

```text
REC009
execution_status: NO_RESULT
result_items: []
```

No automatic second query is invented by Execution.

Reconciliation/Decision may later determine whether a different search is warranted.

---

# 67. EXAMPLE F — TRANSIENT RETRY

First attempt:

```text
TRQ010
provider transport reset
REC010 -> FAILED / transient classification
```

Host policy permits one transport retry.

Second attempt:

```text
TRQ011
same W006
attempt_number: 2
REC011 -> SUCCESS
```

Both receipts/attempts remain in debug history.

The retry did not create new semantic work.

---

# 68. EXAMPLE G — SEMANTIC FOLLOW-UP IS NOT RETRY

First search:

```text
W007 -> TRQ012 -> REC012 SUCCESS
```

Returned information is valid but reveals a narrower required term.

Correct path:

```text
REC012
 -> Reconciliation
 -> DN002
 -> official lane/comment if promoted
 -> Decision re-entry
 -> W008 DISCOVERY
 -> TRQ013
```

Incorrect path:

```text
Execution keeps inventing new Google queries until it feels satisfied.
```

---

# 69. EXECUTION SUCCESS CRITERIA

Tool / Execution passes when it consistently:

- invokes only host-authorized active work;
- preserves `Rxxx -> Wxxx -> TRQxxx -> RECxxx` provenance;
- uses exact current capability registry state;
- distinguishes information tools from action tools;
- creates truthful receipts;
- preserves no-result/partial/failure outcomes;
- verifies writes before claiming Save File success;
- never writes SQLite;
- never decides requirement satisfaction;
- never turns raw results directly into Context truth;
- never rewrites Intent from a discovered term;
- allows multiple valid searches;
- keeps transport retry separate from semantic follow-up;
- preserves immutable execution history.

---

# 70. PERFORMANCE PHILOSOPHY

Tool / Execution should be fast because it contains almost no learned reasoning.

The host does:

- routing;
- schema checks;
- request compilation;
- permissions;
- scheduling;
- tool invocation;
- retries;
- hashing;
- receipt creation;
- write verification.

Do not add model inference merely to make the stage feel intelligent.

Intelligence belongs upstream in Decision and downstream in Reconciliation where semantic judgment is actually required.

---

# 71. BUILD ORDER

Recommended implementation order:

1. Define capability registry dataclasses/schema.
2. Define common `TRQxxx` envelope.
3. Define common receipt model.
4. Implement request/work provenance validation.
5. Implement Google executor wrapper.
6. Implement Wiki executor wrapper.
7. Implement Load File executor with path policy.
8. Implement Save File executor with atomic write/verification.
9. Implement receipt hashing.
10. Implement work-state scheduler.
11. Implement dependency gating.
12. Implement optional parallel groups.
13. Implement transport retry classifier/policy.
14. Implement write idempotency.
15. Implement permanent turn-ledger append logic.
16. Implement Reconciliation handoff packet.
17. Add CLI trace.
18. Run tool-specific independent tests.
19. Run failure suite.
20. Run Decision -> Execution integration tests.
21. Freeze receipt contract before building Reconciliation.

---

# 72. NON-GOALS FOR THIS PROTOTYPE

Do not build inside Tool / Execution:

- a Google adapter;
- a Wiki adapter;
- a File adapter;
- a general Tool Request Builder adapter;
- semantic source relevance judgment;
- source conflict resolution;
- discovery/Derived Need creation;
- Context lane promotion;
- SQLite writes;
- Persistence decisions;
- terminal requirement Completion;
- final Result prose.

The stage should remain intentionally narrow.

---

# 73. LOCKED TOOL / EXECUTION DESIGN SUMMARY

```text
INPUT
  validated Decision work graph

HOST
  compiles Wxxx -> TRQxxx
  validates current capability registry
  validates permissions/side effects
  schedules dependencies/parallel work
  executes tool
  creates immutable RECxxx

TOOLS
  Google/Search
  Wiki
  Load File
  Save File

ADAPTERS
  none in Tool layer

AUTHORITY
  model may request
  host executes
  receipt proves what happened

SEMANTICS
  Execution does NOT decide what result established
  Reconciliation does

DISCOVERY
  raw results may later cause DNxxx
  DNxxx never rewrites original Intent
  accepted discovery may become official Context lane/revision
  official promoted lane receives Howard comment
  Decision then creates new DISCOVERY Wxxx

PERSISTENCE
  SQLite excluded
```

---

# 74. BUILD PHILOSOPHY

The Tool / Execution stage should be deliberately boring.

That is a strength.

Its job is not to be creative.

Its job is to make the system's claims about action **provable**.

Decision provides the reason.

The host provides authority.

The tool provides an outcome.

The receipt preserves the fact.

Reconciliation later decides what that fact means.

Keeping those responsibilities separate is what allows A.R.C.A.D.I.A. to recurse, repair, discover, persist, and report without losing the original requirement chain.
