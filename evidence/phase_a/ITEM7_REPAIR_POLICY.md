# Phase A Item 7 — Bounded Repair Policy

Date: 2026-08-30
Standing: **PASS — item complete; Gate A remains open**

## Authority implemented

- Repair policy is versioned, immutable, Canonical JSON-compatible, and bound
  to a typed SHA-256 policy hash.
- `max_repairs_per_call` is an exact nonnegative integer. Zero explicitly denies
  repair; negative, boolean, float, string-coerced, and unsupported-version
  policies fail closed.
- Each original learned call receives one frozen `RepairBasis`: host call UUID,
  specialist mode, inference-profile ID/hash, and exact authoritative packet.
- The authoritative packet is snapshotted through Canonical JSON V1 and bound to
  a typed SHA-256 hash. Caller mutation cannot expand or change repair authority.
- Each repair receives a new host UUID, contiguous ordinal, prior-repair UUID
  when applicable, unchanged basis/policy hashes, the exact previous invalid
  output, and a nonempty exact machine validation-error object.
- Previous output and validation error are independently snapshotted and hashed.
  They remain separate from the authoritative source packet and cannot silently
  add facts, change specialist mode, or change inference profile.
- Every authorization declares fresh context and fresh sampler as mandatory.
  Actual context/sampler creation remains enforceable by `SpecialistInvoker` and
  the runtime boundary in Phase A2; this policy grants no learned-call authority.
- Repair sessions are immutable. Authorization returns a new session, leaving
  prior state untouched. Session reconstruction verifies aggregate cap,
  call/basis/policy identity, UUID uniqueness, contiguous ordinals, predecessor
  links, canonical snapshots, and all content hashes.
- Exhaustion is explicit and non-mutating. It neither resets history nor marks
  the runtime unhealthy; downstream recipes must preserve the honest failure or
  unresolved standing.
- Aggregate learned-call/token/work accounting remains assigned to the next
  exact-order item, `core/work_budget.py`.

## Evidence

Command: `check.bat`

```text
198 tests passed
Ruff: PASS
strict MyPy: PASS (12 source files)
```

Repair-policy tests cover zero and finite caps, rejected coercions, policy and
basis hashes, immutable packet snapshots, mode/profile binding, unique attempt
UUIDs, ordinals and predecessor lineage, exact output/error snapshots, fresh
state requirements, cap exhaustion without mutation, malformed error and host
values, frozen state, cross-call/basis/policy tampering, over-cap histories,
duplicate attempts, broken chains, noncanonical snapshots, hash mismatches, and
Canonical JSON-compatible audit output.

Gate A remains open for aggregate work budgets, trace/trust registries, and
storage.
