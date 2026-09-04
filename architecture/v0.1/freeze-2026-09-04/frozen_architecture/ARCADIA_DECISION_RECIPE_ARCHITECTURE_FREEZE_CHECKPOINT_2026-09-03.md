# A.R.C.A.D.I.A. — Decision Recipe Architecture Freeze Checkpoint
**Date:** 2026-09-03  
**Status:** Recipe 3 / DECISION architecture frozen for prototype implementation and empirical testing  
**Upstream:** Recipe 1 / INTENT + Recipe 2 / CONTEXT  
**Next recipe:** Recipe 4 / TOOL & EXECUTION

---

## 1. Purpose of this checkpoint

This checkpoint freezes the current architectural decisions for A.R.C.A.D.I.A. Recipe 3 — DECISION after a field-by-field reduction and boundary review.

This is an **architecture/design freeze**, not a claim that implementation qualification has already been completed.

The design intentionally supersedes older prototype details where this checkpoint says so. The governing principles are:

> **Host owns authority. Hats own bounded semantic judgment.**

> **If the host can derive the correct treatment deterministically from already-frozen state, do not spend model reasoning on it.**

> **Ingress contract ≠ model prompt contract.**

> **A specialist should be locally complete and globally ignorant.**

> **Do not confuse “host can recover it” with “specialist does not need it.” Use the smallest sufficient projection, not the smallest possible projection.**

---

## 2. Core Decision question

Decision answers:

> **Given authoritative immutable Intent requirements and active grounded Context, what work actually needs to happen next?**

Decision is the first recipe allowed to convert authoritative requirements and grounded Context into an explicit work plan.

Decision does **not** execute that plan.

```text
INTENT
  what did the user communicate?
       ↓
CONTEXT
  what grounded state do we have?
       ↓
DECISION
  what work actually needs to happen?
       ↓
EXECUTION
  perform authorized work
```

Hard boundary:

> **Decision decides. Execution executes.**

---

## 3. Frozen specialist roster

Recipe 3 uses exactly two learned specialists:

```text
Requirement Assessor
        ↓
validated per-requirement Decision state
        ↓
Plan Composer
        ↓
proposed shared work graph
        ↓
Host validation + authoritative freeze
```

There is no Decision router hat, tool-specific Decision hat, or learned Decision critic in the prototype.

The host owns all deterministic legality, identity, graph, scope, capability, persistence-boundary, hash, and freeze operations.

---

# 4. Decision ingress — frozen

The host receives the semantic Decision basis as references to already-frozen upstream artifacts:

```json
{
  "intent": {
    "artifact_ref": "...",
    "hash": "sha256:..."
  },
  "context": {
    "snapshot_ref": "CS001",
    "hash": "sha256:..."
  },
  "decision_scope": [
    "R001",
    "R002"
  ],
  "reentry": null
}
```

`decision_scope` is an **authority boundary**:

> During this Decision run, only requirements listed in `decision_scope` may receive new active Decision state.

### Re-entry conceptual form

```json
{
  "intent": {
    "artifact_ref": "...",
    "hash": "sha256:..."
  },
  "context": {
    "snapshot_ref": "CS002",
    "hash": "sha256:..."
  },
  "decision_scope": [
    "R002"
  ],
  "reentry": {
    "kind": "DISCOVERY"
  }
}
```

Current model-relevant re-entry kinds:

```text
DISCOVERY
REPAIR
```

More detailed trigger/provenance data may exist in host ledger state but is not projected to a specialist unless it materially changes that specialist's semantic task.

### Host-only runtime/configuration

Separate from semantic ingress:

```json
{
  "capability_registry_ref": "...",
  "capability_registry_version": "...",
  "capability_registry_hash": "sha256:...",
  "decision_limits": {
    "assessor_max_repairs": 2,
    "composer_max_repairs": 2
  }
}
```

`prior_decision_ref` is not required in semantic ingress. The host resolves exact prior state by requirement/job lineage when re-entry occurs and projects only the portion that materially changes the specialist's call.

---

# 5. Upstream integrity gate — frozen

Before any Decision specialist runs, the host verifies at minimum:

```text
Intent artifact exists
Intent hash matches
Context snapshot exists
Context hash matches
Context snapshot belongs to the same Intent artifact/hash
all decision_scope Rxxx exist in authoritative Intent
no out-of-scope Rxxx may be modified by this run
capability registry snapshot exists and hash matches
re-entry scope/trigger is legal when present
all projected Cxxx refs exist in the supplied Context snapshot
```

Failure is a host-level upstream failure.

No specialist is asked to reason around corrupt or mismatched upstream state.

---

# 6. Requirement Assessor — frozen role

Core job:

> **For this exact immutable requirement, given the currently grounded Context and the kinds of work A.R.C.A.D.I.A. can currently perform, what remains before downstream stages can legitimately satisfy it?**

One `Rxxx` per Assessor invocation.

The Assessor does not build a cross-requirement graph and does not select concrete tools.

---

# 7. Requirement Assessor input — frozen

Model-facing packet:

```json
{
  "requirement": {
    "requirement_id": "R001",
    "requested_outcome": "...",
    "constraints": []
  },

  "relevant_context": [
    {
      "context_id": "C001",
      "statement": "...",
      "basis": "supported"
    }
  ],

  "context_boundaries": {
    "conflicts": [],
    "unresolved": [],
    "do_not_assume": []
  },

  "capability_availability": [
    {
      "capability_class": "CURRENT_EXTERNAL_INFORMATION",
      "available": true
    }
  ],

  "prior_requirement_state": null,
  "reentry": null
}
```

`prior_requirement_state` and `reentry` are conditional and may be omitted on an initial pass.

## 7.1 Requirement block

Keep:

```text
requirement_id
requested_outcome
constraints[]
```

Do not provide raw prompt, normalized prompt, source-span duplication, unrelated requirements, or Intent routing internals by default.

`constraints[]` remain separate from `requested_outcome`; they are not collapsed simply to save fields.

## 7.2 Relevant Context

Keep only Cxxx points that materially affect the current Rxxx:

```json
{
  "context_id": "C001",
  "statement": "...",
  "basis": "supported"
}
```

The Assessor does not receive all Context just because it exists.

## 7.3 Context boundaries

Keep relevant:

```text
conflicts[]
unresolved[]
do_not_assume[]
```

These are semantic boundaries, not ordinary Context facts. They prevent the Assessor from confidently proceeding where Context says it must not.

## 7.4 Capability availability

The Assessor receives **requirement-relevant capability classes and current availability**, not concrete tools.

Canonical form:

```json
{
  "capability_class": "CURRENT_EXTERNAL_INFORMATION",
  "available": true
}
```

Frozen exclusions:

```text
concrete capability/tool IDs
tool/API schemas
parameter names
credentials/auth
URLs/endpoints
retry policy
timeouts
execution ordering
adapter/model details
```

Rule:

> **Requirement Assessor determines whether the needed class of work can legitimately exist. It does not choose how that work will be executed.**

## 7.5 Re-entry state

If prior Decision state materially changes the current call, the host may project only the relevant semantic state, for example:

```json
{
  "disposition": "WORK_REQUIRED",
  "remaining_work": "...",
  "work_origin": "ORIGINAL"
}
```

No history dump or arbitrary prior Decision artifact is exposed.

---

# 8. Requirement dispositions — frozen

Exactly one:

```text
READY
WORK_REQUIRED
BLOCKED
PERSISTENCE_REQUIRED
```

These are Decision dispositions, **not Completion statuses**.

## READY

No new ordinary runtime work or Persistence obligation currently remains for the requirement.

`READY != SATISFIED`.

Completion later owns terminal requirement standing.

## WORK_REQUIRED

One or more observable runtime work needs must be satisfied before the requirement can proceed.

## BLOCKED

No legitimate executable path currently exists.

Frozen blocker reasons:

```text
USER_INFORMATION_NEEDED
MISSING_CONTEXT
CAPABILITY_UNAVAILABLE
INVALID_UPSTREAM_STATE
```

## PERSISTENCE_REQUIRED

No ordinary Execution work remains; the outstanding normative obligation belongs to Recipe 6 Persistence.

It is not a SQLite command and never becomes a normal Wxxx work node.

---

# 9. Requirement Assessor output — frozen

Canonical `WORK_REQUIRED` model return:

```json
{
  "disposition": "WORK_REQUIRED",
  "basis_refs": [
    "C001",
    "C002"
  ],
  "need_summary": "Current external information is required to establish the requested state.",
  "work_needs": [
    {
      "work_type": "CURRENT_EXTERNAL_INFORMATION",
      "goal": "Establish the latest stable release applicable to Windows.",
      "evidence_target": [
        "current stable release",
        "Windows applicability",
        "freshness/currentness"
      ]
    }
  ],
  "post_work_obligations": []
}
```

Canonical `BLOCKED` return adds:

```json
{
  "blocker": {
    "reason": "MISSING_CONTEXT",
    "detail": "Conflicting accepted Context leaves the destination unresolved."
  }
}
```

Removed from the model return:

```text
assessment_id
requirement_id echo
confidence
chain-of-thought
concrete tool selection
execution details
```

The host already knows which Rxxx was assessed and owns any internal assessment artifact identity.

## 9.1 Work-need invariant — final packaging correction

Every valid `WORK_REQUIRED` assessment must contain at least one semantic work need.

This explicitly supersedes older prototype traces that allowed a dependency-bound `WORK_REQUIRED` assessment with an empty `work_needs[]` array.

If R002 depends on work that is also required by R001, R002 still states the semantic work it needs. The Plan Composer may later merge those shared needs into one Wxxx.

Example:

```text
R001 → WN001 = establish current release
R002 → WN002 = establish current release

Plan Composer:
WN001 + WN002 genuinely shared
        ↓
one W001 serving R001 + R002
```

This preserves deterministic coverage validation without adding a special dependency-only assessment state.

## 9.2 Host allocation of work-need refs

The Assessor does not generate authoritative work-need IDs.

After validation, the host assigns:

```text
WN001
WN002
WN003
...
```

Authoritative normalized work need:

```json
{
  "work_need_ref": "WN001",
  "requirement_ref": "R001",
  "work_type": "CURRENT_EXTERNAL_INFORMATION",
  "goal": "...",
  "evidence_target": [
    "..."
  ]
}
```

---

# 10. Requirement Assessor host validation — frozen

Host checks include:

```text
JSON/schema validity
disposition enum valid
basis refs exist and are in supplied scope
READY has zero work_needs and no Persistence obligation
WORK_REQUIRED has one or more work_needs
BLOCKED includes one allowed blocker reason
BLOCKED does not create executable work
PERSISTENCE_REQUIRED does not request ordinary Execution/SQLite work
work_type values are bounded/allowed
work goals/evidence targets are bounded
no invented Rxxx/Cxxx refs
no tool syntax or capability IDs
```

Malformed output may receive a bounded surgical repair.

Prototype default:

```text
maximum Assessor repairs = 2
```

A valid but inconvenient semantic result is not a parser failure.

---

# 11. Persistence boundary — frozen and corrected

The following boundary is hard:

```text
DECISION
    │
    ├── ordinary executable work ─────→ Wxxx graph ─→ EXECUTION
    │
    └── persistence obligation ─────────────────────→ PERSISTENCE
```

Internal A.R.C.A.D.I.A. semantic Persistence is **not**:

```text
FILE_WRITE
DURABLE_WRITE
ordinary Tool / Execution work
```

A user-requested external/file write remains ordinary state-changing Execution work.

A.R.C.A.D.I.A. internal semantic Persistence never appears in the Plan Composer capability projection.

### Primary Persistence disposition

```text
PERSISTENCE_REQUIRED
```

means:

> ordinary work is already unnecessary/complete; Persistence is the remaining normative obligation.

### Post-work Persistence

```json
{
  "disposition": "WORK_REQUIRED",
  "post_work_obligations": [
    "PERSISTENCE"
  ]
}
```

means:

> ordinary work must be established/reconciled first; then the normative Persistence obligation proceeds downstream.

### Explicit supersession

The earlier idea that Plan Composer should turn Persistence into an ordinary Wxxx node is **revoked and superseded by this checkpoint**.

---

# 12. Plan Composer — frozen role

Core job:

> **Across all validated in-scope work needs, what is the smallest legitimate shared executable work graph?**

The Plan Composer may reason across requirements.

It does not re-assess Intent or Context and does not execute capabilities.

---

# 13. Plan Composer input — frozen

Conceptual packet:

```json
{
  "assessments": [
    {
      "requirement_ref": "R001",
      "disposition": "WORK_REQUIRED",
      "basis_refs": [
        "C001"
      ],
      "need_summary": "...",
      "work_needs": [
        {
          "work_need_ref": "WN001",
          "work_type": "CURRENT_EXTERNAL_INFORMATION",
          "goal": "...",
          "evidence_target": [
            "..."
          ]
        }
      ],
      "post_work_obligations": []
    }
  ],

  "capabilities": [
    {
      "capability_id": "WEB_SEARCH",
      "capability_class": "CURRENT_EXTERNAL_INFORMATION",
      "available": true,
      "effect": "READ_ONLY",
      "accepts": [
        "information_query"
      ],
      "produces": [
        "retrieved_information"
      ]
    }
  ],

  "prior_work": [],
  "reentry": null
}
```

The host attaches `requirement_ref` and `work_need_ref` after validating the Assessor output.

### Plan Composer does not receive by default

```text
raw prompt
normalized prompt
Intent source spans
Evidence packets
E### judgments
Context lane internals
retrieval history
adapter/model identities
actual invocation schemas
credentials/auth
execution receipts unrelated to re-entry composition
```

---

# 14. Plan Composer capability projection — frozen

Composer receives **planning contracts, not execution contracts**.

Canonical planning-grade capability record:

```json
{
  "capability_id": "WEB_SEARCH",
  "capability_class": "CURRENT_EXTERNAL_INFORMATION",
  "available": true,
  "effect": "READ_ONLY",
  "accepts": [
    "information_query"
  ],
  "produces": [
    "retrieved_information"
  ]
}
```

Frozen effect taxonomy:

```text
READ_ONLY
STATE_CHANGING
```

The host projects only capabilities relevant to accepted work needs.

Still excluded:

```text
actual tool/API schema
exact argument names
credentials
authentication
URLs/endpoints
timeouts
retry policy
runtime receipts
implementation details
```

Rule:

> **Plan Composer may choose which registered capability belongs in a work node and how nodes depend on one another. It may not construct or perform the actual invocation.**

---

# 15. Plan Composer output — frozen

The Composer returns only the proposed executable graph:

```json
{
  "nodes": [
    {
      "node_key": "N1",
      "requirement_refs": [
        "R001",
        "R002"
      ],
      "work_need_refs": [
        "WN001",
        "WN002"
      ],
      "goal": "Establish the current authoritative release needed by both requirements.",
      "capability_id": "WEB_SEARCH",
      "depends_on": [],
      "work_origin": "ORIGINAL"
    }
  ]
}
```

No additional top-level model sections are required.

Explicitly dropped:

```text
satisfied requirement list
blocked requirement list
plan summary
plan status
persistence_required duplicate flag
unhandled_requirements[]
priority
execution status
reasoning / chain-of-thought
```

The host derives those states from validated assessments + validated graph.

---

# 16. Proposed work node semantics — frozen

## `node_key`

Local-only graph identity such as:

```text
N1
N2
N3
```

It exists only so the Composer can express sibling dependencies before authoritative Wxxx IDs exist.

It does not survive as durable identity.

## `requirement_refs[]`

Plural so one legitimate shared work item may serve multiple requirements.

## `work_need_refs[]`

Required coverage bindings.

They tell the host exactly which validated semantic work needs the proposed node claims to satisfy.

This makes requirement/work-need coverage mechanically testable.

## `goal`

One bounded semantic statement describing what the work must accomplish.

Do not split into unnecessary action/object/target micro-fields unless testing proves a need.

## `capability_id`

Concrete registered capability selected for planning.

The Plan Composer selects a capability identity but does not construct its invocation.

## `depends_on[]`

Local `node_key` edges defining logical graph dependency.

Scheduling remains host-owned.

## `work_origin`

Frozen values:

```text
ORIGINAL
DISCOVERY
REPAIR
```

---

# 17. Work-node fields explicitly removed

The proposed/final W node does **not** repeat:

```text
inputs[]
produces[]
```

Those are deterministic properties of the selected capability planning contract.

Duplicating them inside the node would let the model disagree with the registry.

If empirical testing later proves that exact data-source binding cannot be derived safely from capability contracts + dependencies, add a narrow binding construct at that time. Do not pre-build one now.

The node also does not contain:

```text
status
priority
reasoning
execution arguments
receipts
```

---

# 18. Host work-graph validation — frozen

No authoritative Wxxx is allocated until the **entire proposed graph** passes validation.

## 18.1 Structural validity

```text
JSON/schema valid
nodes[] within configured bounds
node_key unique
required fields present
no unknown fields
work_origin enum valid
```

## 18.2 Decision-scope validity

For every node:

```text
requirement_refs are inside decision_scope
work_need_refs exist
work_need_refs belong to accepted in-scope assessments
requirements implied by work_need_refs match declared requirement_refs
```

The Composer may not attach unrelated requirements to convenient work.

## 18.3 Work-need coverage

For every accepted in-scope assessment:

```text
READY
→ no new Wxxx coverage required

BLOCKED
→ no executable work may be invented to bypass the blocker

PERSISTENCE_REQUIRED
→ no ordinary Wxxx is created for internal Persistence

WORK_REQUIRED
→ every accepted WNxxx receives legitimate graph coverage
```

This is stronger than checking only that every Rxxx appears somewhere.

## 18.4 Capability legality

For each proposed node:

```text
capability_id exists in the exact registry snapshot
capability is currently available
capability_class can satisfy every linked WNxxx work_type
```

Unknown/unavailable/incompatible capability => reject.

## 18.5 Side-effect authority

If:

```text
effect = STATE_CHANGING
```

host must trace the mutation to legitimate upstream authority.

A Composer's preference that a write would be useful is not authority.

User-directed file/output writes may be legitimate ordinary Execution work.

Internal semantic Persistence is not an Execution side effect and is rejected from Wxxx planning entirely.

## 18.6 Dependency graph legality

Host verifies:

```text
every dependency exists
no self dependency
no duplicate dependency edge
no cycle
cross-requirement dependency remains requirement/work-need legitimate
```

## 18.7 Shared-work legality

A node may serve multiple Rxxx only when its `work_need_refs[]` legitimately cover work needs belonging to each declared requirement.

Shared capability class alone is insufficient reason to merge work.

## 18.8 Re-entry/origin legality

```text
initial run → ORIGINAL work
DISCOVERY re-entry → legitimate new work may be DISCOVERY
REPAIR re-entry → legitimate corrective work may be REPAIR
```

Composer may not invent re-entry origin.

---

# 19. Atomic acceptance and authoritative Wxxx allocation — frozen

Rule:

> **Validate the proposed graph atomically. Allocate authoritative Wxxx only after the whole proposal passes.**

Example:

```text
N1 → W001
N2 → W002
N3 → W003
```

Dependencies are rewritten from local keys to authoritative IDs before freeze.

A failed Composer attempt does not consume meaningful Wxxx history.

Authoritative work node:

```json
{
  "work_id": "W001",
  "requirement_refs": [
    "R001",
    "R002"
  ],
  "work_need_refs": [
    "WN001",
    "WN002"
  ],
  "goal": "...",
  "capability_id": "WEB_SEARCH",
  "depends_on": [],
  "work_origin": "ORIGINAL"
}
```

---

# 20. Persistence obligations — authoritative normalization

Persistence obligations remain separate from the Wxxx graph.

After accepted Assessor state, the host may normalize each normative Persistence obligation to a host-owned reference:

```json
{
  "obligation_ref": "PO001",
  "requirement_refs": [
    "R002"
  ],
  "basis_refs": [
    "C004"
  ],
  "reason": "Persist the validated state required by R002."
}
```

`POxxx` is host-owned and never model-generated.

A Persistence outcome later resolves the obligation through a new downstream artifact. The immutable Decision artifact itself is not mutated to mark the obligation complete.

Execution projection excludes these obligations.

Persistence projection includes them when the pipeline reaches Recipe 6 and their prerequisites are valid.

---

# 21. Authoritative Decision artifact — frozen

Each accepted Decision run becomes an immutable `DRxxx` artifact.

Conceptual canonical shape:

```json
{
  "decision_id": "DR001",
  "schema_version": "decision_snapshot@1",
  "decision_hash": "sha256:...",

  "intent": {
    "artifact_ref": "...",
    "hash": "sha256:..."
  },

  "context": {
    "snapshot_ref": "CS001",
    "hash": "sha256:..."
  },

  "decision_scope": [
    "R001",
    "R002"
  ],

  "capability_registry": {
    "ref": "...",
    "version": "...",
    "hash": "sha256:..."
  },

  "requirements": [
    {
      "requirement_ref": "R001",
      "disposition": "WORK_REQUIRED",
      "basis_refs": [
        "C001"
      ],
      "need_summary": "Current external information is required.",
      "work_need_refs": [
        "WN001"
      ],
      "persistence_obligation_refs": []
    },
    {
      "requirement_ref": "R002",
      "disposition": "BLOCKED",
      "basis_refs": [
        "C003"
      ],
      "need_summary": "A required destination remains unresolved.",
      "work_need_refs": [],
      "persistence_obligation_refs": [],
      "blocker": {
        "reason": "MISSING_CONTEXT",
        "detail": "The destination cannot be established safely."
      }
    }
  ],

  "work_needs": [
    {
      "work_need_ref": "WN001",
      "requirement_ref": "R001",
      "work_type": "CURRENT_EXTERNAL_INFORMATION",
      "goal": "Establish the latest stable release applicable to Windows.",
      "evidence_target": [
        "current stable release",
        "Windows applicability",
        "freshness/currentness"
      ]
    }
  ],

  "work_graph": [
    {
      "work_id": "W001",
      "requirement_refs": [
        "R001"
      ],
      "work_need_refs": [
        "WN001"
      ],
      "goal": "Establish the latest stable release applicable to Windows.",
      "capability_id": "WEB_SEARCH",
      "depends_on": [],
      "work_origin": "ORIGINAL"
    }
  ],

  "persistence_obligations": [],

  "reentry": null
}
```

The Decision artifact contains the authoritative semantic Decision state and executable work graph for this scoped run.

Construction-only model metadata, adapter identities, repair transcripts, and raw prompts remain in technical telemetry/ledger state rather than the canonical semantic Decision snapshot.

---

# 22. Decision artifact host validation before freeze — frozen

Before hashing/freezing, host verifies:

```text
Decision ID is host-owned and unique
Intent ref/hash valid
Context ref/hash valid and belongs to same Intent
all decision_scope requirements exist
all requirements[] exactly correspond to decision_scope
all dispositions valid
all basis_refs valid
all WNxxx host-owned and uniquely defined
all WORK_REQUIRED requirements have >=1 WNxxx
all WNxxx owned by exactly one authoritative Rxxx
all WNxxx covered by at least one valid Wxxx
all Wxxx host-owned and unique
all Wxxx requirement_refs/work_need_refs valid
all selected capabilities valid against frozen registry snapshot
all graph dependencies valid and acyclic
all STATE_CHANGING work has authority
no internal Persistence capability appears in Wxxx
all POxxx host-owned and traceable to normative Decision state
READY/BLOCKED/PERSISTENCE_REQUIRED states do not silently acquire illegal work
reentry metadata, if present, is scope-legal
no out-of-scope requirement state changed
```

Only after all checks pass may the Decision artifact freeze.

---

# 23. Canonicalization and SHA-256 — frozen

Use the same system-wide deterministic artifact hashing discipline as Context.

Minimum profile:

```text
UTF-8 JSON
fixed/versioned canonical serialization profile
deterministic object-key ordering
no insignificant whitespace
set-like arrays deterministically ordered
requirements sorted by requirement_ref
work_needs sorted by work_need_ref
work_graph sorted by work_id
depends_on / requirement_refs / work_need_refs deterministically ordered
persistence_obligations sorted by obligation_ref
```

Hash rule:

> SHA-256 is computed over the canonical Decision body excluding the `decision_hash` field itself.

The hashed body includes:

```text
decision_id
schema_version
upstream refs/hashes
decision_scope
capability registry ref/version/hash
requirement Decision state
WNxxx
Wxxx
Persistence obligations
reentry metadata
```

---

# 24. Immutability and scoped re-entry — frozen

An accepted `DRxxx` is immutable.

Do not update in place:

```text
requirement dispositions
WNxxx contents
Wxxx graph
Persistence obligations
Intent/Context/capability hashes
reentry lineage
```

Selective re-entry creates a new Decision artifact.

Example:

```text
DR001 scope [R001,R002,R003]
R001 → W001
R002 → W002
R003 → READY

later Context/repair/discovery affects only R002

DR002 scope [R002]
R002 → W004
```

`DR001` remains historical truth.

Only R002 receives new active Decision state.

The host maintains active Decision resolution per requirement/job lineage; it does not rewrite old Decision artifacts.

---

# 25. Supersession and executed-history boundary — frozen

Decision may supersede **planning**.

Decision may not erase the fact that an operation occurred.

```text
unexecuted old Wxxx
→ may be superseded by later scoped Decision state

executed Wxxx with immutable receipt
→ execution fact remains forever
```

If later correction is necessary, create new explicit `REPAIR` work.

Historical receipts remain downstream Execution/Reconciliation truth.

No Decision rerun edits them.

---

# 26. Model/host authority summary — frozen

## Requirement Assessor owns

```text
per-Rxxx semantic disposition
semantic need summary
semantic work needs
evidence targets
blocker semantics
post-work Persistence recognition
```

## Plan Composer owns

```text
smallest legitimate shared executable graph
capability selection from supplied planning candidates
semantic graph dependencies
shared-work composition
```

## Host owns

```text
all authoritative IDs
Decision scope
upstream integrity
Context projection
capability registry truth
capability-class projection
WNxxx allocation
POxxx allocation
Wxxx allocation
schema/ref validation
work-need coverage
capability compatibility
graph acyclicity
side-effect authority
Persistence/Execution boundary
repair limits
canonicalization
hashing
immutability
active-state/supersession resolution
stage transition
```

---

# 27. Cross-recipe boundary freeze

```text
INTENT
owns what the user communicated.
Decision may not rewrite Rxxx.

CONTEXT
owns grounded state.
Decision may use but not silently replace Cxxx.

DECISION
owns what work is legitimately required and the frozen Wxxx graph.
Decision performs no operation.

EXECUTION
owns concrete invocation compilation, scheduling, operation attempts, and receipts.
Execution does not reinterpret user intent or invent new Decision work.

RECONCILIATION
owns what returned work actually establishes.
It may expose discovery/repair needs, but material discovery re-enters Context before scoped Decision re-entry.

PERSISTENCE
owns semantic durable-memory judgment and commit flow.
Decision only recognizes normative Persistence obligations.

COMPLETION
owns terminal requirement standing.
READY is not SATISFIED.
```

---

# 28. Explicit supersession ledger from earlier Decision drafts/discussion

The following older forms are superseded by this checkpoint:

### Assessor model IDs / echoes

Old:

```text
assessment_id generated/copied by model
requirement_id echoed by model
confidence
```

Now:

```text
host owns call/assessment identity
one Rxxx per Assessor invocation
no confidence field
```

### Assessor capability view

Old:

```text
concrete tool/capability registry entries
```

Now:

```text
requirement-relevant capability classes + availability only
```

### Composer capability view

Old:

```text
full execution-oriented capability registry/schema
```

Now:

```text
planning-grade capability contracts only
```

### Work nodes

Old:

```text
input/output category echoes
singular requirement ownership in some examples
```

Now:

```text
inputs[] / produces[] removed
requirement_refs[] plural
work_need_refs[] required
```

### Dependency-bound empty work needs

Old trace:

```text
WORK_REQUIRED + work_needs=[]
```

Now:

```text
WORK_REQUIRED always carries >=1 semantic work need
shared/dependency work is independently stated then merged by Composer
```

### Persistence drift

Revoked:

```text
internal Persistence may become an ordinary Wxxx node
```

Frozen:

```text
ordinary executable work → Wxxx → Execution
internal semantic Persistence obligation → Recipe 6 Persistence
```

---

# 29. Required prototype test families

The architecture freeze should be implemented with tests covering at least:

```text
test_decision_ingress_hash_mismatch_rejected
test_decision_scope_blocks_out_of_scope_change

test_assessor_ready_no_work
test_assessor_work_required_has_work_need
test_assessor_blocked_has_no_executable_work
test_assessor_capability_unavailable_block
test_assessor_persistence_required_no_execution_work
test_assessor_post_work_persistence_separate

test_work_need_ids_host_owned
test_dependency_bound_requirement_still_has_work_need
test_shared_semantic_needs_merge_to_one_work_node

test_composer_local_node_keys_not_authoritative
test_composer_cannot_invent_requirement_ref
test_composer_cannot_invent_work_need_ref
test_composer_unknown_capability_rejected
test_composer_unavailable_capability_rejected
test_composer_capability_class_mismatch_rejected
test_composer_state_change_without_authority_rejected
test_composer_internal_persistence_node_rejected

test_graph_missing_dependency_rejected
test_graph_self_dependency_rejected
test_graph_cycle_rejected
test_graph_work_need_coverage_complete
test_graph_shared_work_requires_multi_requirement_coverage

test_w_ids_allocated_only_after_atomic_graph_acceptance
test_failed_composer_attempt_consumes_no_w_id

test_decision_persistence_obligation_separate_from_w_graph
test_decision_scoped_discovery_reentry
test_decision_scoped_repair_reentry
test_decision_reentry_preserves_unaffected_requirements
test_decision_cannot_erase_executed_receipt_history

test_decision_canonical_hash_reproducible
test_decision_immutable_after_freeze
```

Prototype repair budgets:

```text
Requirement Assessor max repairs = 2
Plan Composer max repairs = 2
```

These are runtime/test policy defaults and may be empirically tuned without reopening the semantic authority boundaries.

---

# 30. Final frozen Recipe 3 pipeline

```text
Immutable Intent + Frozen Context
            ↓
Host Decision Ingress / Integrity Gate
            ↓
one Rxxx at a time
            ↓
Requirement Assessor
            ↓
Host validation
            ↓
Host assigns WNxxx / normalizes POxxx
            ↓
validated assessments + relevant planning capabilities
            ↓
Plan Composer
            ↓
local Nxxx graph proposal
            ↓
Host atomic validation
  - scope
  - WN coverage
  - capability legality
  - side-effect authority
  - dependency graph legality
  - Persistence boundary
            ↓
Host assigns authoritative Wxxx
            ↓
Build canonical DRxxx Decision artifact
            ↓
Canonicalize + SHA-256
            ↓
Immutable Decision freeze
            ↓
     ┌──────┴──────┐
     ↓             ↓
Execution Wxxx   Persistence obligations retained
                 for Recipe 6 path
```

---

# 31. Architecture freeze verdict

**Recipe 3 — DECISION is architecturally frozen for prototype implementation.**

The frozen design preserves the central A.R.C.A.D.I.A. split:

> **The Requirement Assessor identifies what work is semantically needed.**

> **The Plan Composer builds the smallest legitimate shared work graph.**

> **The host proves that graph is legal and creates authority.**

> **Execution performs the work.**

> **Persistence remains a separate semantic-memory authority.**

Remaining work is implementation, fixtures, adversarial testing, and empirical refinement of bounded taxonomies—not reopening the fundamental Recipe 3 authority model.
