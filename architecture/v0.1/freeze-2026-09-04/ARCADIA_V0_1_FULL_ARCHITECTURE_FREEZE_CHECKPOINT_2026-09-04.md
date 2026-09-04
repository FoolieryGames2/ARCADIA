# A.R.C.A.D.I.A. v0.1 — Full Recipe 0→8 Architecture Freeze Checkpoint

**Date:** 2026-09-04  
**Project:** A.R.C.A.D.I.A. — Adaptive Runtime for Compartmentalized Agents, Decisions, Interaction & Automation  
**Standing:** Recipes 0–8 architecturally frozen for v0.1 prototype implementation/testing. Publication/completed-turn boundary frozen. Runtime and implementation qualification remain open.

## 1. Canonical locks

### Foundation model

`Qwen/Qwen3-4B-Instruct-2507`

### Terminology

- **A.R.C.A.D.I.A. / Arcadia** — complete runtime/system/architecture.
- **Base/foundation model** — underlying replaceable model.
- **Specialist adapters** — bounded learned hats used by particular recipes.
- **Conversational adapter** — user-facing personality/presentation layer.
- **Howard** — only the specific Howard conversational adapter/personality.

Older documents using Howard generically are terminology defects, not current architecture authority.

## 2. Global frozen principles

1. If the host can derive the correct treatment deterministically from already-frozen state, do not spend model reasoning on it.
2. Ingress contract is not model prompt contract.
3. A specialist should be locally complete and globally ignorant.
4. Host owns authority; hats own bounded semantic judgment.
5. Optimize model input for smallest sufficient, not smallest possible.
6. Models do not allocate authoritative IDs, mutate frozen artifacts, write SQL, publish responses, or emit chain-of-thought fields.
7. Immutable artifacts are superseded rather than rewritten.
8. Re-entry is bounded, scoped, provenance-preserving, and additive.
9. Execution success is not semantic success; semantic success is not terminal requirement standing.
10. Persistence plan is not persistence commit.
11. Completion organizes terminal truth; Result articulates it.
12. Conversational prose is not publication-authorized until host validation passes.
13. Transcript history contains the exact user input and exact successfully published Arcadia response, not internal drafts.

## 3. Canonical full spine

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
COMPLETED transcript turn
```

## 4. Recipe freeze summary

### Recipe 0 — Conversation Resolver — FROZEN

Minimum-sufficient completed-transcript retrieval only. No semantic-memory authority.

Accepted continuation correction: a host-owned one-next-turn `AWAITING_USER_INPUT` marker causes the immediately prior completed exchange to be prefetched for scope validation when the previous Arcadia response explicitly solicited continuation. An unrelated next turn discards the prefetch; the marker expires after that one turn. No model-written semantic summary is stored in the marker.

### Recipe 1 — Intent — FROZEN

Creates immutable authoritative requirements (`Rxxx`) and Context needs from what the user communicated. Downstream recipes do not rewrite Intent.

### Recipe 2 — Context — FROZEN

Grounds Intent against bounded evidence, preserves provenance/disagreement, produces host-authoritative `Cxxx`, performs bounded lane work and scoped re-entry, and freezes immutable `CSxxx`. Context does not execute tools or write durable state.

### Recipe 3 — Decision — FROZEN

Decides what work should happen through Requirement Assessor + Plan Composer. Host owns `WNxxx`, `Wxxx`, graph legality, capability authority, schema validation, and immutable `DRxxx`. Internal Arcadia persistence obligations are separate from ordinary Execution work.

### Recipe 4 — Execution — FROZEN

Host-owned / learned-model-free.

```text
DRxxx + execution_scope
→ Integrity Gate
→ deterministic Scheduler
→ Wxxx → TRQxxx
→ Executor
→ RECxxx / OperationJournal
→ bounded transport retry + crash handling
→ Execution Finalizer
→ immutable ERxxx
```

`execution_scope` is an authority boundary. `Wxxx` = semantic executable work; `TRQxxx` = exact proposed operation; `RECxxx` = operational reality. `OUTCOME_UNKNOWN` is preserved. Semantic follow-up must go through Reconciliation/Decision rather than Execution improvisation.

### Recipe 5 — Reconciliation — FROZEN

Ingress: immutable `ERxxx` ref/hash.

Question: **What did the work that actually occurred establish relative to the work requested?**

Two learned jobs only:

- Evidence Reconciler — one W at a time; `ESTABLISHED / PARTIAL / NOT_ESTABLISHED / CONFLICT`.
- Reconciliation Composer — proposes `DISCOVERY / REPAIR_NEEDED / CONTEXT_UPDATE / PERSISTENCE_RELEVANCE` only.

Host validates/routes `DNxxx`→Context, `CIPxxx`→Context, `RRQxxx`→Decision, advisory persistence candidate→Persistence. Final immutable `RCxxx` exits only after legitimate re-entry is resolved or honestly exhausted.

### Recipe 6 — Persistence — FROZEN

Ingress: immutable `RCxxx` ref/hash. Host resolves three authority-separated queues:

- Decision normative persistence obligations;
- Context advisory user-origin candidates;
- Reconciliation advisory evidence-derived candidates.

Persistence Assessor judges one bounded item against bounded semantic memory. Persistence Composer builds the smallest coherent semantic mutation plan using temporary refs. Host commit bridge rechecks the base sequence, allocates permanent IDs, applies one atomic transaction, verifies semantic state, and emits `PRCxxx`. Only `PRCxxx` proves durable write/no-change outcome. Finalizer freezes `PSxxx` and hands one ref/hash to Completion.

Future Context alone gets read-only semantic-memory access; Recipe 0 remains transcript-only; Persistence host alone gets write authority. Persisted records re-enter the normal Context evidence path rather than bypassing Context validation.

### Recipe 7 — Completion — FROZEN

Ingress: immutable `PSxxx` ref/hash.

Host reconstructs immutable lineage, validates integrity, derives deterministic closure signals, and builds one bounded closure bundle per original `Rxxx`.

Completion Assessor assigns exactly one terminal status:

- `SATISFIED`
- `PARTIALLY_SATISFIED`
- `BLOCKED`
- `FAILED`

Completion may not create new work/reality. Completion Composer only organizes already-decided outcomes; it cannot alter terminal standing. Host compiles exact coverage/status/posture/disclosure/literal authority into immutable `FSPxxx`.

### Recipe 8 — Result — FROZEN

Ingress: immutable `FSPxxx` ref/hash.

Host validates FSP, creates Disclosure Map, Literal Lock, Response Budget, and compact per-requirement presentation packets. Selected conversational adapter produces bounded fresh-KV per-requirement comments, each host-validated; failed wording gets bounded repair then deterministic safe fallback.

After comments are validated, conversational KV is cleared and one fresh final composition call receives only bounded approved presentation material. Final prose is then host-validated for internal-ID leakage, protected literals, required disclosure, prohibited claims, standing consistency, surface corruption, and response budget. Invalid final prose gets bounded repair then deterministic safe fallback.

Host freezes exact validated response text in immutable `RSTxxx`.

Publication Host sends the exact RST text, records transport standing, commits the exact published text to transcript, verifies hash equality, increments transcript commit sequence exactly once, and emits immutable `PUBxxx`. Only the successful publication/transcript path marks the turn `COMPLETED`.

## 5. Final authority chain

```text
Intent Rxxx
  ↓
Context CSxxx
  ↓
Decision DRxxx
  ↓
Execution ERxxx
  ↓
Reconciliation RCxxx
  ↓
Persistence PSxxx
  ↓
Completion FSPxxx
  ↓
Result RSTxxx
  ↓
Publication PUBxxx
  ↓
COMPLETED transcript turn
```

The chain intentionally distinguishes:

- work planned vs work executed;
- execution success vs semantic establishment;
- semantic establishment vs terminal requirement standing;
- persistence plan vs durable commit;
- validated response text vs actual publication;
- publication vs normal transcript completion.

## 6. Prototype Result scope lock

For v0.1 the selected conversational adapter receives compact presentation packets rather than the entire trace. This is intentionally narrow and trainable. Broaden only from measured test evidence, without weakening authority boundaries.

## 7. Accepted future-review comments — not current architecture

- richer downstream experiential bridges after reconciled/final state (game engine, watch/join/commentary, etc.);
- optional conversational use of non-blocking ambiguity signals;
- classify Journal durability as semantic-memory vs separate durable application-data storage before implementation lock of that feature.

These comments create no present schema/routing authority.

## 8. Architecture vs qualification

This checkpoint freezes **architecture**, not implementation quality.

Still open:

- Recipe-by-recipe implementation;
- Windows/Python canonical qualification where specified;
- runtime/llama.cpp pin qualification;
- adapter residency/isolation/selection benchmarks;
- failure injection/crash recovery;
- persistence stress suite;
- Completion/Result stress suite;
- full Recipe 0→8 replay/hash/transport/transcript tests.

Use `ARCADIA_V0_1_BUILD_HANDOFF_2026-09-04.md` as the implementation handoff.
