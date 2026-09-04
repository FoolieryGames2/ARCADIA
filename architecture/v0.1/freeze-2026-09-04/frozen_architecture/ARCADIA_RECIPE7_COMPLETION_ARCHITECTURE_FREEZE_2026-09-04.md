# A.R.C.A.D.I.A. Recipe 7 — Completion Architecture Freeze

**Date:** 2026-09-04  
**Standing:** Architecturally frozen for v0.1 prototype implementation/testing.

## Purpose

Completion answers one terminal question:

> **After all legitimate upstream work, reconciliation, re-entry, and persistence have ended, what is the final standing of each original `Rxxx` requirement?**

Completion evaluates existing authoritative reality only. It creates no new reality.

## Ingress

Recipe 7 receives only the frozen Persistence result reference/hash:

```json
{
  "persistence": {
    "artifact_ref": "PS001",
    "hash": "sha256:..."
  }
}
```

The host follows immutable lineage backward as needed:

```text
PSxxx
 ↓
RCxxx
 ↓
ERxxx
 ↓
DRxxx
 ↓
CSxxx
 ↓
Intent / Rxxx
```

Completion does not require a duplicated giant turn envelope.

## Host reconstruction / integrity gate

Before any learned call the host:

1. validates `PSxxx` and all required upstream hashes;
2. reconstructs the exact provenance graph;
3. proves all required subordinate references exist;
4. proves all legitimate re-entry is terminal or honestly exhausted;
5. derives deterministic closure signals;
6. builds one bounded `RequirementClosureBundle` per original `Rxxx`.

Mechanical closure facts are host-owned and do not consume model reasoning.

If the upstream chain is structurally invalid, Completion fails closed with an integrity error rather than asking a model to reason over corrupted state.

## One bounded closure bundle per requirement

Each original requirement gets an independent bounded closure view containing only what is needed to judge that requirement, such as:

- requested outcome / constraints;
- relevant final Context projections;
- relevant work outcomes;
- Reconciliation semantic findings;
- persistence outcomes belonging to the requirement;
- remaining material gaps;
- blockers;
- failures;
- host-derived closure signals.

The model does not receive the whole project/turn trace merely because the host can recover it.

## Completion Assessor

One immutable `Rxxx` at a time.

Question:

> **Given this exact requirement and its final authoritative closure state, what is its terminal standing, and what material parts were fulfilled, unmet, blocked, or failed?**

Allowed terminal statuses are exactly:

- `SATISFIED`
- `PARTIALLY_SATISFIED`
- `BLOCKED`
- `FAILED`

Candidate semantic output is intentionally lean:

```json
{
  "terminal_status": "PARTIALLY_SATISFIED",
  "fulfilled_components": [
    {
      "statement": "The requested current version was established.",
      "basis_refs": ["EF001"]
    }
  ],
  "unmet_components": [
    {
      "statement": "The requested file could not be saved.",
      "basis_refs": ["REC004"]
    }
  ],
  "blockers": [],
  "failure_causes": [
    {
      "statement": "The required file write failed.",
      "basis_refs": ["REC004"]
    }
  ],
  "conflict_refs": []
}
```

Host assigns authoritative `CAxxx` and attaches lineage after validation.

### Status consistency gates

Host rejects structurally inconsistent assessments, including:

- `SATISFIED` with an essential unmet component;
- `PARTIALLY_SATISFIED` with nothing materially fulfilled;
- `BLOCKED` with no legitimate blocker;
- `FAILED` with no actual failure basis;
- `SATISFIED` when a required persistence obligation belonging to that requirement failed.

Bounded repair is for invalid structure/references only; a valid `BLOCKED` or `FAILED` judgment is not repaired merely because another outcome is preferred.

## Completion Composer — final compiler

After every `Rxxx` has a validated `CAxxx`, the Completion Composer organizes the already-decided standings into one turn-level presentation structure.

It may:

- propose result focus / presentation role across requirements;
- identify supported shared facts or shared blockers/failures;
- propose disclosure emphasis such as `MUST_REPORT`;
- propose protected-literal importance.

It may **not**:

- re-decide or alter terminal status;
- create/remove requirements;
- create work;
- invent facts;
- execute tools;
- persist anything;
- write final user-facing prose.

Statuses are immutable input facts and need not be echoed unnecessarily in the learned output.

The host deterministically supplies:

- exact `Rxxx` coverage;
- authoritative `CAxxx` refs/statuses;
- overall turn posture;
- authoritative disclosure map;
- authoritative protected literals;
- hashes / basis lineage.

## Final Standing Packet

Host builds and freezes immutable `FSPxxx` after Composer validation.

Conceptual shape:

```json
{
  "final_standing_id": "FSP001",
  "schema_version": "final_standing@1",
  "final_standing_hash": "sha256:...",
  "persistence": {
    "artifact_ref": "PS001",
    "hash": "sha256:..."
  },
  "requirement_standings": [
    {
      "requirement_ref": "R001",
      "completion_assessment_ref": "CA001",
      "terminal_status": "SATISFIED"
    },
    {
      "requirement_ref": "R002",
      "completion_assessment_ref": "CA002",
      "terminal_status": "BLOCKED"
    }
  ],
  "overall_turn_posture": "MIXED",
  "result_focus": [],
  "shared_items": [],
  "disclosure_map": [],
  "protected_literals": []
}
```

Canonicalize, SHA-256 hash, freeze. Old FSP artifacts are never rewritten.

## Authority boundary

> **Completion is the first and only recipe allowed to assign terminal standing to the original `Rxxx`. It begins only after legitimate upstream re-entry has ended. It evaluates existing reality and may not create new reality.**

Completion organizes truth. Recipe 8 Result articulates it.
