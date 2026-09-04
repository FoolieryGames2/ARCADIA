# A.R.C.A.D.I.A. — Context Recipe Architecture Freeze Checkpoint
**Date:** 2026-09-03  
**Status:** Recipe 2 / CONTEXT architecture frozen for prototype implementation and empirical testing  
**Next recipe:** Recipe 3 / DECISION

---

## 1. Purpose of this checkpoint

This checkpoint freezes the current architectural decisions for A.R.C.A.D.I.A. Recipe 2 — CONTEXT before moving into Recipe 3 — DECISION.

This is an **architecture/design freeze**, not a claim that implementation validation has already been completed. Prototype testing is expected to refine small taxonomies and optional states where explicitly marked below, without changing the core authority boundaries.

---

## 2. Core architecture principles

### Host authority
**Host owns authority. Hats own bounded semantic judgment.**

The host owns:
- routing
- retrieval
- authoritative IDs
- provenance
- structural/reference validation
- bounds
- persistence/publication
- immutable freeze
- downstream handoff

The learned specialists own:
- semantic relevance
- support / contradiction judgment
- bounded inference
- conflict recognition
- narrow synthesis

### Specialist isolation
**A specialist should be locally complete and globally ignorant.**

A specialist receives:
- its exact task
- the bounded semantic material needed for that task
- only those qualifiers that materially change the semantics of the task

A specialist does **not** receive pipeline history, routing internals, upstream/downstream identities, or global state merely because it could reason about them.

### Deterministic-host preference
**If the host can derive the correct treatment deterministically from already-frozen state, do not spend model reasoning on it.**

### Contract separation
**Ingress contract ≠ model prompt contract.**

Host-side execution contracts may contain provenance, IDs, routing scope, and other control state that should never be exposed to a specialist.

---

## 3. Frozen Context pipeline

```text
Accepted Intent
    ↓
Context Ingress
    ↓
Host Router
    ↓
LaneRequest
    ↓
Host Retrieval
    ↓
Evidence Candidate Packet
    ↓
Evidence Specialist
    ↓
Host Validation
    ↓
Context Lane Commentator
    ↓
Host Validation + authoritative Cxxx
    ↓
Final Context Synthesis
    ↓
Host Snapshot Validation
    ↓
Canonicalize + SHA-256
    ↓
Immutable Context Snapshot
    ↓
DECISION
```

---

# 4. Context Ingress — frozen

Semantic ingress from accepted Intent:

```json
{
  "intent_artifact_ref": "...",
  "intent_hash": "...",
  "source_map_ref": "...",
  "source_map_hash": "...",
  "in_scope_requirements": [],
  "context_needs": [],
  "clarification_state": "...",
  "unresolved_blockers": []
}
```

Host-only Context runtime/configuration remains separate:

```json
{
  "split_library_ref": "...",
  "split_library_version": "...",
  "split_library_hash": "...",
  "routing_limits": {}
}
```

### Visibility rules
- `clarification_state` is host/audit state; it does not automatically propagate to hats.
- `unresolved_blockers` are host-controlled and projected only when their unresolved semantic state matters to a specific specialist.
- split-library state and routing limits are never semantic Context ingress.

---

# 5. LaneRequest — frozen

`LaneRequest` is an authoritative **host execution contract**, not a model prompt.

```json
{
  "lane_id": "L001",
  "split_id": "project_continuity@1",
  "requirement_refs": [
    "R001",
    "R002"
  ],
  "context_need_refs": [
    "CN001"
  ],
  "retrieval_scope": {
    "sources": [
      "project_memory"
    ],
    "limits": {
      "candidate_limit": 8
    }
  },
  "supersedes_lane_id": null,
  "provenance": {
    "intent_artifact_ref": "...",
    "intent_hash": "...",
    "split_library_ref": "...",
    "split_library_version": "...",
    "split_library_hash": "..."
  }
}
```

### Explicitly excluded
- raw prompt
- normalized prompt
- source-span duplication
- lane-purpose prose
- clarification state
- blocker list
- model-selected Split
- model-selected retrieval scope
- model-generated lane ID

### Retrieval invariant
A lane retrieval scope must be a subset of the selected Split's permitted retrieval scope.

---

# 6. Evidence Specialist — frozen

## Job
> Given this exact Context need and this exact bounded evidence, what does each supplied evidence item legitimately establish?

One Context need per specialist invocation.

## Model-facing input

```json
{
  "context_need": {
    "ref": "CN001",
    "statement": "..."
  },
  "candidates": [
    {
      "evidence_id": "E001",
      "content": "..."
    }
  ]
}
```

Candidate metadata is hidden by default. A semantic qualifier may cross the boundary only when removing it would materially prevent the specialist from performing the assigned judgment.

## Model return

```json
{
  "judgments": [
    {
      "evidence_id": "E001",
      "status": "supports",
      "finding": "..."
    }
  ]
}
```

### Frozen evidence states
- `supports`
- `contradicts`
- `relevant`
- `irrelevant`
- `ambiguous`

### Explicitly excluded
- confidence score
- chain-of-thought / reasoning essay
- overall lane conclusion
- invented evidence IDs
- retrieval or pipeline metadata

The host validates supplied/returned IDs, schema, completeness, enum membership, duplicate IDs, and bounds.

---

# 7. Context Lane Commentator — frozen

## Job
> Given the relevant accepted requirement(s), one Context need, and host-validated Evidence judgments, what grounded Context points are worth preserving for this lane?

The Commentator receives validated semantic findings rather than raw evidence by default.

## Model-facing input
- relevant accepted requirement projection(s)
- one Context need
- host-validated Evidence Specialist judgments

No lane ID, routing state, pipeline history, or downstream knowledge is required.

## Model return

```json
{
  "context_points": [
    {
      "statement": "...",
      "basis": "supported",
      "evidence_refs": [
        "E001"
      ]
    }
  ]
}
```

### Prototype basis taxonomy
- `supported`
- `inference`
- `unresolved`

### Inference rule
An inference may combine validated evidence findings into a useful proposition, but may not introduce unsupported facts, assumptions, intentions, preferences, or external knowledge.

### One-hop rule
Inference must ground directly to validated `E###` findings.

Allowed:

```text
E001 ─┐
E002 ─┼→ one bounded inference
E003 ─┘
```

Not allowed:

```text
E001 → inference A → inference B → inference C
```

The Commentator **proposes** Context. It does not assign authoritative `Cxxx` IDs.

### Host validation after Commentator
The host performs structural/reference/bounds validation and then assigns authoritative `Cxxx`.

The host does not attempt to reproduce generic semantic reasoning deterministically.

---

# 8. `unresolved` empirical-review note — frozen TODO

Keep `unresolved` during prototype testing.

Specifically test:
- genuine insufficient-evidence cases
- contradictory evidence cases
- ambiguous Evidence Specialist findings
- cases where the Commentator could safely emit nothing instead
- selective Context re-entry after unresolved output

Review criterion:

> If `unresolved` is unnecessary or redundant in approximately 99% of valid runs, and removing it does not lose meaningful state or permit unsafe assumptions, remove it from the Commentator taxonomy.

Do not remove it based on theoretical simplification alone.

---

# 9. Authoritative `Cxxx` Context points — frozen

After host validation, authoritative Context points are deliberately lean:

```json
{
  "context_id": "C001",
  "statement": "...",
  "basis": "supported"
}
```

### Retained
- authoritative Context ID
- grounded statement
- semantic basis

### Removed from final `Cxxx`
- evidence refs
- requirement refs
- construction lineage

Those relationships remain host-recoverable through immutable lane results.

### Rule
**Strip construction lineage from Context points, but retain semantic metadata that changes the meaning or authority of the point itself.**

`basis` stays because a supported fact and a bounded inference should not become epistemically indistinguishable downstream.

---

# 10. Final Context Synthesis — frozen

This is the first Context hat allowed to see across lanes.

## Job
> Given accepted `Cxxx` Context points and the relevant accepted requirements, what relationships across the grounded state should Decision be aware of?

It does not receive:
- raw evidence
- source documents
- lane IDs
- Split IDs
- retrieval information
- raw prompt
- downstream Decision instructions

## Model return

```json
{
  "cross_context": [
    {
      "statement": "...",
      "context_refs": [
        "C001",
        "C002"
      ]
    }
  ],
  "conflicts": [],
  "unresolved": [],
  "do_not_assume": []
}
```

### Cross-context rule
Cross-context synthesis may describe a relationship necessary to understand the grounded state.

It may **not**:
- recommend an action
- choose a plan
- prioritize work
- decide what should happen next
- perform tool selection
- perform execution logic

Simple boundary:

> If the proposition means **"this is the grounded state"**, it may belong in Context.  
> If it becomes **"therefore we should..."**, it belongs in Decision.

### One-hop cross-context rule

Allowed:

```text
C001 ─┐
C002 ─┼→ one cross-context conclusion
C003 ─┘
```

Not allowed:

```text
C001 + C002 → synthesis A
A + C003 → synthesis B
B + C004 → synthesis C
```

Final Synthesis may relate/select/synthesize accepted `Cxxx`, but may not alter, replace, or silently correct them.

Cross-context outputs remain a separate derived synthesis layer and are not automatically promoted into new authoritative `Cxxx`.

---

# 11. Frozen Context Snapshot — frozen

Canonical snapshot contents:

```json
{
  "snapshot_id": "CS001",
  "schema_version": "context_snapshot@1",
  "snapshot_hash": "sha256:...",

  "intent": {
    "artifact_ref": "...",
    "hash": "..."
  },

  "context_points": [
    {
      "context_id": "C001",
      "statement": "...",
      "basis": "supported"
    }
  ],

  "synthesis": {
    "cross_context": [],
    "conflicts": [],
    "unresolved": [],
    "do_not_assume": []
  },

  "provenance": {
    "lane_result_refs": [
      "LR001"
    ]
  }
}
```

### Removed from canonical snapshot
- raw / normalized prompt
- duplicated source map
- duplicated in-scope requirement list
- `Cxxx` requirement refs
- `Cxxx` evidence refs
- retrieval information
- Split information
- hat/model information
- superseded lane bodies
- model prompts / retry history
- Decision instructions
- Completion state

### Snapshot rule
**`Cxxx` carries grounded semantic state, not its construction history. Construction history remains host-recoverable through authoritative immutable lane results.**

---

# 12. Lane-result provenance — frozen

Snapshot provenance is:

```json
{
  "provenance": {
    "lane_result_refs": [
      "LR001",
      "LR002"
    ]
  }
}
```

Not `active_lane_result_refs`.

Reason: a historical snapshot should never change meaning because a later lane result becomes current.

### Lane-result invariant
A `LRxxx` reference identifies one immutable frozen lane-result artifact forever.

If Context re-entry occurs:

```text
LR001 = preserved old result
LR007 = new result that supersedes LR001
```

Existing snapshots remain unchanged.

---

# 13. Final host validation and freeze — frozen

The final Context snapshot is built by the host, never by a model.

Before freeze, the host verifies:
- Intent artifact exists and hash matches
- every referenced lane result exists and is frozen
- lane results belong to the same accepted Intent artifact/hash
- every selected `Cxxx` is authoritative and originates in the selected lane results
- `Cxxx` IDs are unique
- `basis` is allowed
- Final Synthesis schema is valid
- every synthesis `Cxxx` ref exists in the snapshot
- no unknown refs
- count/string/reference bounds pass
- no materially unresolved Context need disappears silently

The host derives the snapshot's Context-point set from frozen lane results rather than accepting an arbitrary free-floating `Cxxx` list.

---

# 14. Canonicalization and hash — frozen

Before SHA-256:
- serialize deterministically as UTF-8 JSON
- use fixed serialization rules
- deterministic object-key ordering
- remove insignificant whitespace
- deterministically order arrays where ordering has no semantic meaning
- deterministically order Context points by authoritative ID

The canonical snapshot body includes:
- `snapshot_id`
- `schema_version`
- Intent anchor
- Context points
- synthesis
- lane-result provenance

The `snapshot_hash` field itself is excluded from the bytes being hashed.

```text
Canonical Snapshot Body
        ↓
SHA-256
        ↓
snapshot_hash
        ↓
Immutable Stored Artifact
```

---

# 15. Immutability and re-entry — frozen principle

Once `CS001` is frozen:

```text
NO update CS001
NO patch C001 inside CS001
NO replace synthesis
NO swap lane-result refs
NO update Intent hash
```

Context change or selective re-entry produces a new immutable Context snapshot:

```text
CS001 → preserved
Context re-entry
CS002 → new snapshot
```

Historical state is never rewritten.

---

# 16. Recipe 2 freeze status

## Frozen for prototype architecture
- Context ingress
- host/router ownership
- LaneRequest
- Evidence Specialist input/output boundary
- Evidence judgment taxonomy
- Context Lane Commentator boundary
- one-hop lane inference
- authoritative `Cxxx` construction
- Final Context Synthesis boundary
- one-hop cross-context synthesis
- Context snapshot contents
- lane-result traceback
- final host validation
- canonicalization / SHA-256
- immutable freeze semantics

## Explicitly empirical / revisitable without architecture rewrite
- whether `unresolved` remains useful enough to retain
- exact enum wording if specialist testing proves a cleaner taxonomy
- bounded limits / token limits / candidate counts
- exceptional semantic qualifiers exposed to a specialist

---

# 17. Recipe 3 handoff

Recipe 2 is architecturally frozen.

The next boundary is:

```text
Immutable Accepted Intent
        +
Immutable Context Snapshot
        ↓
RECIPE 3 — DECISION
```

Recipe 3 should be reviewed using the same design discipline:
- host first
- deterministic logic before model reasoning
- small local specialist projections
- no authority leakage to hats
- immutable upstream Intent and Context
- explicit boundary between deciding work and executing work
