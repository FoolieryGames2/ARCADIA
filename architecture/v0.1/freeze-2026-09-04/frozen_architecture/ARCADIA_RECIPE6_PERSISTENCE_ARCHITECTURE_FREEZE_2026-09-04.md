# A.R.C.A.D.I.A. Recipe 6 — Persistence Architecture Freeze

**Date:** 2026-09-04  
**Standing:** Architecturally frozen; implementation/stress qualification remains open.

## Purpose

Persistence determines and applies legitimate durable semantic-state changes after upstream work has stabilized. It does not invent new save intentions and does not assign terminal requirement standing.

## Ingress / authority queues

Recipe 6 receives one final frozen Reconciliation artifact ref/hash:

```json
{
  "reconciliation": {
    "artifact_ref": "RC003",
    "hash": "sha256:..."
  }
}
```

Host resolves three authority-separated durability queues:

1. **Decision normative obligations** — must receive explicit disposition.
2. **Context advisory user-origin candidates** — may be accepted/ignored/deferred/etc.
3. **Reconciliation advisory evidence-derived candidates** — may be accepted/ignored/deferred/etc.

Current memory snapshot/base commit sequence and policy are host runtime state, not semantic recipe ingress.

Persistence does not notice a raw user statement and independently decide it should be saved if upstream did not surface an obligation/candidate.

## Persistence Assessor

One item at a time against a bounded frozen semantic-memory snapshot.

Question:

> Given this exact candidate/obligation and the bounded durable memory that already exists, what semantic memory consequence is justified?

Assessor handles:

- durability judgment;
- entity resolution;
- duplicate/same relation;
- change vs correction;
- refinement;
- conflict;
- retraction;
- unrelated state;
- alias implications;
- bounded `NEEDS_MORE_MEMORY` when the supplied snapshot is insufficient.

It does not execute SQL, allocate permanent IDs, commit state, rewrite transcript/Intent/Context, create requirements, or decide Completion.

Identity ambiguity must not be escaped by silently creating duplicate entities.

## Persistence Composer

Combines validated per-item assessments into the smallest coherent semantic mutation plan.

It must:

- cover every normative obligation exactly once;
- preserve advisory authority;
- coalesce duplicate/overlapping effects when appropriate;
- use temporary local refs for new semantic objects;
- propose claim/alias/conflict/merge/entity mutations without allocating durable IDs.

Planning vocabulary is not commit vocabulary. Composer may produce dispositions such as `WRITE`, `NO_CHANGE`, `IGNORE`, `DEFER`, `BLOCKED`, `POLICY_REJECT`, `COALESCED`.

`COMMITTED` is reserved for the post-transaction receipt.

## Host Commit Bridge

Validated frozen `PPxxx` enters host-only commit logic.

Flow:

```text
PPxxx
  ↓
recheck memory_commit_seq
  ↓
if stale: abort + bounded reevaluation
  ↓
allocate permanent IDs
  ↓
BEGIN IMMEDIATE
  ↓
apply semantic mutations + provenance/audit
  ↓
increment commit sequence
  ↓
verify resulting semantic state
  ↓
COMMIT or ROLLBACK
  ↓
PRCxxx
```

All mutations are atomic. A stale plan never overwrites newer semantic state.

Only a verified immutable `PRCxxx` proves durable write/no-change outcome.

Candidate receipt:

```json
{
  "persistence_receipt_id": "PRC001",
  "plan_ref": "PP001",
  "status": "SUCCESS",
  "base_commit_seq": 40,
  "result_commit_seq": 41,
  "item_results": [
    {"item_ref": "PO001", "result": "COMMITTED"}
  ],
  "semantic_effect_refs": {
    "created_entities": [],
    "created_claims": ["M000193"],
    "transition_refs": ["MT000055"],
    "alias_change_refs": [],
    "conflict_refs": [],
    "merge_refs": []
  },
  "transaction_standing": "PROVISIONAL",
  "verification": "PASS",
  "diagnostic_refs": [],
  "receipt_hash": "sha256:..."
}
```

Operational receipt statuses may include `SUCCESS`, `NO_CHANGE`, `FAILED`, `ROLLED_BACK`, `STALE_SNAPSHOT_BLOCKED`.

New conversational semantic state may commit successfully while remaining `PROVISIONAL`; durable write success and future clean-Context eligibility are distinct.

## Persistence Finalizer / Completion handoff

Finalizer mechanically validates obligation/candidate coverage, PP/PRC lineage, commit sequences, status/verification consistency, effect refs, and absence of silently dropped normative items.

Candidate immutable result:

```json
{
  "persistence_id": "PS001",
  "schema_version": "persistence_result@1",
  "persistence_hash": "sha256:...",
  "reconciliation": {"artifact_ref": "RC003", "hash": "sha256:..."},
  "plan_ref": "PP001",
  "receipt_ref": "PRC001",
  "obligation_results": [
    {"item_ref": "PO001", "result": "COMMITTED"}
  ],
  "candidate_results": [
    {"item_ref": "PC002", "result": "DEFERRED"}
  ],
  "memory_state": {
    "base_commit_seq": 40,
    "result_commit_seq": 41
  },
  "persistence_state": "FINALIZED"
}
```

Completion receives only:

```json
{
  "persistence": {
    "artifact_ref": "PS001",
    "hash": "sha256:..."
  }
}
```

Persistence does not assign terminal `Rxxx` status.

## Future Context read-back

Repository authority is split:

```text
Recipe 0
→ transcript only

Recipe 2 Context
→ SemanticMemoryReadRepository only

Recipe 6 Persistence Host
→ SemanticMemoryWriteRepository only
```

Future Context semantic-memory retrieval is:

- bounded;
- snapshot-pinned;
- hash-verifiable;
- filtered by claim standing, expiry, contest state, alias status, and canonical entity identity;
- unable to inject unresolved `PROVISIONAL` state as clean Context;
- routed into the already-frozen Context evidence path rather than bypassing Context validation.

A future memory snapshot records at least the memory commit sequence and exact record identity/hashes used by that Context run. Later memory changes do not retroactively alter a prior Context snapshot.

## Review comments preserved, not implemented

### Conversational ambiguity affordance

Non-blocking ambiguity/identity uncertainty surfaced during Persistence may later be exposed as an optional conversational-comment opportunity without interrupting the main task. If ambiguity affects correctness, normal clarification/block rules apply. This is a future design comment only—no current schema/routing authority.

### Journal classification

Explicit journal save intent must be surfaced upstream; Persistence cannot invent it. Before implementation lock, classify whether Journal content is stored as semantic memory or through a separate durable application-data repository so raw journal prose is not accidentally forced into the entity/claim store.
