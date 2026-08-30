# Phase A Item 13 — Exact Transcript Repository

Date: 2026-08-30
Standing: **PASS — item complete; Gate A remains open**

## Authority implemented

- `TranscriptRepository` is immutable and scoped to one canonical project UUID.
  Conversation and turn UUIDs remain host authority; an existing UUID is either
  an exact idempotent retry or a conflict, never an overwrite or cross-project
  alias.
- Starting a turn atomically creates its turn state and one exact USER entry.
  Content is stored without normalization and bound to typed SHA-256. There is no
  generic entry append method and no ordinary path for learned drafts.
- Committing publication requires the exact transported assistant text to match
  the supplied immutable Result hash. The ASSISTANT entry, publication relation,
  `COMPLETED` turn state, and monotonic `transcript_commit_seq` increment commit in
  one managed transaction. Failure rolls all four back.
- Recovery identity is the frozen `turn_uuid + result_hash`: a same-result retry
  returns the existing completed exchange without adding an entry or increment;
  a changed result conflicts. Durable row decoding revalidates canonical UUIDs,
  UTC timestamps, positive ordinals/sequences, roles, relationships, and content
  hashes before returning authority to callers.
- Recent history returns completed user/assistant exchanges only, in chronology,
  with the prototype limit capped at 20. Targeted FTS5 retrieval is project- and
  conversation-scoped, excludes open/failed turns, deduplicates to at most one
  entry per turn, escapes operator-like input into literal Unicode terms, and is
  capped at 8 turns, 1,024 input characters, and 32 terms.
- Forward-only migration 5 adds transcript turn lifecycle, publication identity,
  commit-sequence metadata, and the transcript-owned FTS5 index without editing
  the four prior migrations. Semantic memory, artifacts, registry snapshots,
  Result creation, transport, and PublicationJournal authority remain separate.
- The connection wrapper now rejects caller-owned PRAGMA and transaction-control
  statements before SQLite prepares them, including comment-prefixed attempts,
  while the authorizer still enforces mutation and database scope. This permits
  necessary SQLite-owned FTS5 internals without exposing a policy-changing caller
  path.

Current catalog hash:

```text
sha256:d16bcfb85f832b8f98591031a1d010668d9fb88616c062ae47f40518b1df9cbb
```

Migration 5 hash:

```text
sha256:201ae389b35269168defece6bc3683a4f35a8444b32fdfbaa82ddbe7a9b50841
```

## Evidence

Commands: `check.bat` and `check_phase0.bat`

```text
355 tests passed
Ruff: PASS
strict MyPy: PASS (19 source files)
Phase 0 authority, dependency, model, llama.cpp, CUDA, and runtime hashes: PASS
```

The 25 transcript repository tests cover current-schema refusal, strict immutable
repository identity, exact/idempotent conversation and user-turn creation,
project isolation, immutable retry conflicts, missing scope, content hashing,
exact published-text/result-hash binding, atomic completion and sequence advance,
failed-draft exclusion, publication recovery without duplication, chronological
completed-only history, retrieval bounds, scoped and turn-deduplicated FTS,
operator-text escaping, durable hash tamper detection, malformed-sequence rollback,
cross-link/value invariants, and role constraints. Connection and migration tests
also cover comment-prefixed caller-control rejection and the pinned forward catalog.

Gate A remains open for `storage/artifact_repository.py` and
`storage/registry_snapshots.py`. The next exact-order item is
`storage/artifact_repository.py`.
