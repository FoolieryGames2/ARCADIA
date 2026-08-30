# Phase A Item 14 — Immutable Artifact Repository

Date: 2026-08-30
Standing: **PASS — item complete; Gate A remains open**

## Authority implemented

- `ArtifactRepository` is immutable and scoped to one canonical project UUID.
  It accepts only an already sealed and hash-verified Artifact Envelope V1; the
  repository does not generate model content, invent schema meaning, or admit a
  second persistence representation.
- A new host artifact identity begins only at revision 1 with expected head 0.
  Later revisions append contiguously against the caller's exact optimistic head.
  Exact retries return the existing revision without duplication; changed bytes
  at an existing identity/revision conflict. Project, turn, Recipe, artifact type,
  and scoped human alias remain stable across a revision line, while revisions
  cannot move backward in canonical creation time.
- Identity, complete canonical envelope JSON, redundant content/envelope hashes,
  and ordered basis links commit atomically. Failed validation, missing basis,
  stale head, or any constraint error leaves no partial artifact identity or
  revision.
- Every basis reference must already exist in the same project at the exact UUID,
  revision, and envelope hash. Because a new envelope cannot cite itself and can
  cite only committed history, repository writes cannot introduce forward or
  cyclic artifact provenance. Reads recheck both the stored link and the current
  durable upstream hash.
- Exact-revision and latest-revision reads are project-scoped. Bounded turn reads
  return immutable revisions chronologically, optionally constrained to one
  locked Recipe, with a hard maximum of 200 revisions per call.
- Every read reconstructs Artifact Envelope V1 from exact Canonical JSON and
  verifies its content/envelope hashes, project/turn/Recipe/type/revision columns,
  revision-1 identity timestamp, contiguous history, ordered basis rows, and
  upstream durable identities. Malformed or tampered durable state fails closed.
- There is no delete, overwrite, Save File, transcript, semantic-memory, active-
  state, or registry-snapshot operation. Supersession remains represented by
  later technical artifacts/revisions and recipe contracts, never destructive
  mutation of historical rows.

## Evidence

Commands: `check.bat` and `check_phase0.bat`

```text
382 tests passed
Ruff: PASS
strict MyPy: PASS (20 source files)
Phase 0 authority, dependency, model, llama.cpp, CUDA, and runtime hashes: PASS
```

The 27 artifact repository tests cover current-schema refusal; strict immutable
repository identity; first-revision commit; exact and latest reads; idempotent
retry; exact new-artifact head; project/turn scope; contiguous optimistic
revision append; stale head and skipped revision rejection; immutable turn,
Recipe, type, and alias identity; nondecreasing time; conflicting existing
revision; exact/missing/mismatched basis refs; atomic failure; revision-gap
detection; chronological and Recipe-scoped bounded turn reads; cross-project and
missing reads; canonical envelope, relational-link, and upstream-hash tamper
detection; strict arguments; and absence of destructive/cross-authority methods.

Gate A remains open for `storage/registry_snapshots.py` and the complete Gate A
deterministic authority review. The next exact-order item is
`storage/registry_snapshots.py`.
