# A.R.C.A.D.I.A. v0.1 — Build Handoff

**Date:** 2026-09-04  
**Purpose:** Hand the now-frozen Recipe 0→8 prototype architecture to implementation without reopening design by default.

## 1. Build standing

The full Recipe 0→8 **architecture is frozen for v0.1 prototype implementation/testing**.

This does **not** mean the implementation is qualified. Runtime, adapters, repository behavior, crash handling, persistence, Completion, Result, and full-spine stress gates still have to be implemented and measured.

The build team should treat test failures as evidence. Do not loosen architecture merely because implementation is inconvenient. Reopen architecture only when a failing test exposes a genuine contract defect rather than a coding defect.

## 2. Architecture authority precedence

When documents disagree, use this precedence:

1. this final full-architecture checkpoint and its dedicated Recipe 4–8 freeze docs;
2. Recipe 2 Context and Recipe 3 Decision freeze docs;
3. accepted Recipe 0 continuation-correction doc/patch;
4. current runtime/model terminology locks;
5. older prototype build specs/exact build orders for implementation detail where they do not conflict;
6. historical/reference bundles for audit only.

Older documents that call the base model, runtime, or generic specialists “Howard” are terminology-defective. Howard is only a specific conversational adapter/personality.

## 3. Foundation/runtime lock

v0.1 foundation model:

`Qwen/Qwen3-4B-Instruct-2507`

Runtime qualification remains open. Empirically qualify the pinned llama.cpp/runtime build, adapter residency/isolation, memory footprint, selection latency, A/B/A isolation, crash behavior, and measured throughput before declaring the runtime production-ready.

## 4. Canonical spine

```text
Recipe 0 — Conversation Resolver
    ↓
Recipe 1 — Intent
    ↓
Recipe 2 — Context
    ↓
Recipe 3 — Decision
    ↓
Recipe 4 — Execution
    ↓
Recipe 5 — Reconciliation
    ↓
Recipe 6 — Persistence
    ↓
Recipe 7 — Completion
    ↓
Recipe 8 — Result
    ↓
Publication Host
    ↓
completed transcript turn
```

## 5. Build strategy

### A. Start with schemas, immutable artifact store, hashing, ledgers, and host validators

Do not begin by wiring all learned specialists together. Implement the deterministic authority substrate first:

- canonical JSON + SHA-256;
- artifact identity/immutability;
- transcript ledger + commit sequence;
- technical ledger;
- capability registry;
- semantic-memory repositories;
- policy snapshots;
- deterministic validators and transition gates.

### B. Implement recipe-by-recipe with independent gates

Use the existing exact build-order documents as checklists, applying the newer freeze-doc deltas.

Important current deltas include:

- Recipe 0 open-continuation marker / one-next-turn prefetch behavior;
- Recipe 4 compact `TRQxxx`, `RECxxx`, deterministic scheduler, `OperationJournal`, `ERxxx` finalizer;
- Recipe 5 `ERxxx` ingress, lean Evidence Reconciler, Composer consequence classes, host transition routing, `RCxxx` freeze;
- Recipe 6 `RCxxx` ingress, three persistence authority queues, lean Assessor/Composer, `PPxxx` plan vs `PRCxxx` commit distinction, `PSxxx`, future Context read-back;
- Recipe 7 `PSxxx` ingress, one closure bundle per `Rxxx`, lean Completion Assessor, host-owned status/posture compile, immutable `FSPxxx`;
- Recipe 8 `FSPxxx` ingress, compact per-R presentation packets, selected conversational adapter terminology, host validation, deterministic fallback, `RSTxxx`, publication receipt `PUBxxx`, exact-transcript rule.

### C. Keep host-vs-model boundaries hard

Models may perform bounded semantic judgment only. Host owns:

- IDs;
- provenance;
- routing;
- graph legality;
- capability availability/authority;
- execution compilation/scheduling;
- receipts/journals;
- SQL and durable commits;
- hashes/canonicalization;
- terminal artifact freezing;
- publication and transcript completion.

## 6. Required implementation qualification lanes

### Recipe 0

Implement and test the accepted `AWAITING_USER_INPUT` continuation correction, including:

- implicit reply to open solicitation;
- unrelated next turn drops prefetched exchange;
- marker expires after one next turn;
- exact published exchange is what Recipe 0 retrieves.

### Recipes 1–6

Use their existing build/stress gates plus the newer freeze docs. Persistence must pass its 30-case gate before Completion implementation is considered qualified according to the prior exact build plan.

### Recipe 7–8

Use the preserved Completion/Result exact build order as implementation checklist, but apply current architecture deltas.

The historical C7/R8 stress suite remains useful, including:

- satisfied / partial / blocked / failed contrast;
- shared work across multiple requirements;
- open DN/RRQ preventing premature completion;
- provenance orphan rejection;
- Composer status-mutation rejection;
- FSP tamper rejection;
- exact-name/version corruption rejection;
- blocker hiding rejection;
- false “saved” claim rejection;
- internal ID suppression;
- repair/fallback paths;
- exact published text == transcript text;
- failed transport does not mark turn completed;
- Recipe 0 next-turn retrieval sees exact published response;
- full Recipe 0→8 replay/hash validation.

## 7. Prototype conversational-result target

The v0.1 selected conversational adapter should receive small bounded presentation packets, not Arcadia's full trace.

Design target:

```text
Here is what is true.
Here is what must be said.
Here is what must not be claimed.
Here are exact strings you cannot alter.
Say it naturally.
```

Broaden only after empirical testing shows the compact packet is insufficient. Do not grant the conversational adapter authority to re-decide status/facts as a shortcut to better prose.

## 8. Known open review comments (not blockers)

These remain comments only unless build/testing gives reason to promote them:

1. richer post-Reconciliation/final-state experiential bridges (game engine/watch/join/commentary/etc.);
2. optional conversational use of non-blocking ambiguity signals;
3. classify Journal storage as semantic memory vs separate durable application-data repository before implementation lock of that feature.

## 9. Definition of a successful first build handback

Return to architecture review with:

- repository commit/hash;
- canonical Python/Windows qualification environment details;
- exact foundation model/runtime build identifiers;
- test counts and failures by recipe;
- deterministic artifact/hash replay evidence;
- adapter isolation/residency measurements;
- full pipeline trace(s) through Recipe 0→8;
- crash/restart and idempotency evidence;
- persistence stress results;
- Completion/Result stress results;
- exact published-response/transcript equality evidence.

The first build does not need to be pretty. CLI/technical traces are acceptable. Correct contracts and reproducible tests come first.

## 10. Build instruction in one sentence

> **Implement the frozen spine as written, prove the host-owned authority boundaries with tests, and treat architecture changes as evidence-driven exceptions rather than implementation conveniences.**
