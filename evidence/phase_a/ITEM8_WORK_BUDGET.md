# Phase A Item 8 — Aggregate Work-Budget Ledger

Date: 2026-08-30
Standing: **PASS — item complete; Gate A remains open**

## Authority implemented

- `BudgetLimits` copies every Config V1 ceiling into one immutable, versioned,
  Canonical JSON-compatible snapshot with a typed SHA-256 identity.
- Exact nonnegative ceilings cover total learned calls, repairs per original
  call, re-entries, history expansions, Context retrieval expansions, Decision
  work items, Reconciliation discovery depth, side-effect retries,
  compensations, total model input tokens, and total reserved output tokens.
  Zero explicitly denies the corresponding work.
- Each authorization is an atomic immutable grant. A model attempt charges one
  learned call plus its complete input-token count and reserved output-token
  allowance. A repair also charges the aggregate learned-call/token budgets and
  the original call's per-call repair budget.
- Repair grants require the typed current `RepairSession` head, the exact repair
  attempt UUID/ordinal, matching policy limits, and a prior original
  model-attempt grant in the same ledger. Repairs cannot appear from nowhere or
  bypass aggregate call accounting.
- Re-entry, history expansion, Context retrieval expansion, Decision work,
  side-effect retry, and compensation usage accumulate irreversibly.
  Reconciliation discovery is correctly enforced as a depth high-water bound,
  not an additive count.
- Every grant receives a host entry UUID, contiguous sequence, unique operation
  UUID, canonical ordered charges, frozen limits hash, predecessor hash, and
  whole-entry hash. Replay verifies identities, event shapes, unit costs,
  limits, chains, unique operations, repair lineage, and aggregate ceilings.
- Callers must present the current ledger head before authorization. Stale or
  unexpected heads fail before a grant is created.
- Any multi-dimension overflow raises a machine-readable `BUDGET_EXHAUSTED`
  denial identifying dimension, used amount, requested amount, and limit. The
  original ledger remains unchanged; no partial charge, reset, refund, history
  deletion, or fabricated success path exists.
- Reserved output allowance is intentionally conservative and irreversible.
  Later runtime telemetry records realized tokens separately; it cannot reclaim
  authority already granted within the turn.

## Evidence

Command: `check.bat`

```text
229 tests passed
Ruff: PASS
strict MyPy: PASS (13 source files)
```

Work-budget tests cover Config V1 copying, limit hashes, rejected coercions,
zero-denial behavior, atomic model and repair charges, aggregate call/input/
output exhaustion, explicit denial evidence, repair-policy/session/original-call
binding, all additive dimensions, reconciliation high-water behavior, Decision
batch bounds, optimistic head conflicts, duplicate operation rejection,
contiguous hash chaining, frozen-limit binding, deletion/reorder/duplicate/
content tampering, canonical event shape, immutability, and canonical snapshot
rendering.

Gate A remains open for trace/trust registries and authority-separated storage.
