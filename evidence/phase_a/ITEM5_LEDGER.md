# Phase A Item 5 — Technical Turn Ledger

Date: 2026-08-29
Standing: **PASS — item complete; Gate A remains open**

## Authority implemented

- A technical ledger is scoped to exactly one canonical project UUID and turn
  UUID. Cross-project and cross-turn artifacts fail closed.
- Ledger state is immutable. Append returns a new snapshot; the prior snapshot
  and every earlier entry remain unchanged and addressable.
- Each append stores a complete verified Artifact Envelope V1 and receives a
  host-generated entry UUID, contiguous sequence, fixed UTC append timestamp,
  predecessor hash, and canonical entry hash.
- Root entries require no predecessor. Every later entry must reference the exact
  prior entry hash, producing one replay-verifiable chain.
- Append requires the caller to present the current head hash. Missing, stale, or
  unexpected heads fail with an optimistic-concurrency conflict before append.
- Entry UUIDs and artifact UUID/revision identities are unique. Later revisions
  of one artifact identity may only advance; history cannot be appended backward
  or replaced.
- Artifact creation precedes append, and append timestamps are nondecreasing.
- Canonical replay verifies embedded artifact integrity, project/turn scope,
  entry hashes, contiguous ordering, predecessor links, uniqueness, revision
  ordering, entry count, and final head hash.
- Snapshot and entry parsers reject missing/unknown fields, unsupported versions,
  invalid identities, implicit host type coercion, non-canonical JSON, and
  invalid UTF-8.
- The module stores technical provenance only. It provides no transcript,
  semantic-memory, raw-trace, or training-promotion write path.

## Evidence

Command: `check.bat`

```text
140 tests passed
Ruff: PASS
strict MyPy: PASS (10 source files)
```

Ledger tests cover empty and multi-entry canonical replay, immutability,
hash-chain construction, optimistic head conflicts, scope rejection, duplicate
artifacts, timestamp legality, metadata and embedded-artifact tampering,
deletion/reordering/broken-link detection, count/head verification, strict wire
input, host type coercion, and identity-specific artifact history.

Gate A remains open for schema validation, repair policy, bounded work
accounting, trace/trust registries, and storage.
