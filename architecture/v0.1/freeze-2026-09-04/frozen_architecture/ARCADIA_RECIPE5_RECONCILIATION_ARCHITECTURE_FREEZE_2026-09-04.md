# A.R.C.A.D.I.A. Recipe 5 — Reconciliation Architecture Freeze

**Date:** 2026-09-04  
**Standing:** Architecturally frozen; implementation/testing remains open.

## Purpose

> What did the work that actually occurred establish relative to the work that was requested?

## Ingress

Recipe 5 receives one immutable Execution artifact ref/hash:

```json
{
  "execution": {
    "artifact_ref": "ER001",
    "hash": "sha256:..."
  }
}
```

Host resolves DR/W/WN/R lineage, TRQ/REC/results, relevant Context, and deterministic evidence signals. Raw conversation is not dumped into Reconciliation merely because it exists.

## Deterministic-first rule

If the host can establish the operational/semantic consequence mechanically from frozen authoritative state, it does so without a model call. Semantic interpretation is used only when judgment is genuinely required.

## Evidence Reconciler

One `Wxxx` per call.

Question:

> Given this work target and supplied evidence, what was actually established?

Allowed semantic state:

- `ESTABLISHED`
- `PARTIAL`
- `NOT_ESTABLISHED`
- `CONFLICT`

Output may contain supported established statements, not-established targets/reasons, conflicts, material discoveries, and Context impacts with exact evidence refs. Host owns `EFxxx` IDs and lineage.

It may not search, invent evidence, choose new work, execute tools, write persistence, or assign terminal requirement standing.

## Reconciliation Composer

Consumes validated `EFxxx` projections in a fresh call.

Question:

> Across these already-validated findings, what consequences follow for the current work set?

Allowed consequence classes:

- `DISCOVERY`
- `REPAIR_NEEDED`
- `CONTEXT_UPDATE`
- `PERSISTENCE_RELEVANCE`

It cannot create W/R IDs, select tools, execute, mutate Context/Persistence, or assign SATISFIED/FAILED/BLOCKED.

## Host transition validator

Accepted proposals become host-authoritative transition artifacts:

- `DISCOVERY` → `DNxxx` → Context re-entry.
- `CONTEXT_UPDATE` → `CIPxxx` → Context re-entry.
- `REPAIR_NEEDED` → `RRQxxx` → scoped Decision re-entry.
- `PERSISTENCE_RELEVANCE` → advisory `PCxxx` → eventual Persistence.

Discovery does not rewrite Intent and does not jump directly to Decision.

Context-impact proposals do not edit `Cxxx`; Context re-entry decides whether old Context is superseded, conflicted, revised, or retained.

Repair corrects previously planned/executed work; discovery represents new information learned by valid work.

## Re-entry / finalization

Re-entry loops are scoped, bounded, provenance-linked, and additive. Old RC/ER/DR/CS artifacts remain immutable.

Recipe 5 exits only when required Reconciliation re-entry is resolved or honestly exhausted.

Candidate final immutable result:

```json
{
  "reconciliation_id": "RC003",
  "schema_version": "reconciliation_result@1",
  "reconciliation_hash": "sha256:...",
  "execution": {"artifact_ref": "ER003", "hash": "sha256:..."},
  "prior_reconciliation_refs": ["RC001", "RC002"],
  "evidence_finding_refs": ["EF004", "EF005"],
  "accepted_consequences": {
    "derived_need_refs": [],
    "context_impact_refs": [],
    "repair_request_refs": [],
    "persistence_candidate_refs": ["PC002"]
  },
  "reentry_event_refs": [],
  "active_context": {"snapshot_ref": "CS003", "hash": "sha256:..."},
  "persistence_inputs": {
    "decision_obligation_refs": ["PO001"],
    "context_candidate_refs": ["CPC001"],
    "reconciliation_candidate_refs": ["PC002"]
  },
  "reconciliation_state": "FINALIZED",
  "diagnostic_refs": []
}
```

Persistence receives only the frozen final `RCxxx` ref/hash.
