# A.R.C.A.D.I.A. — A1 Repair Shape PRE-1

**Date:** 2026-08-31
**Standing:** PRE-version implementation / not frozen / Gate A1 remains OPEN

## Purpose

Implement numbered A1 strict-schema/policy TODO item 7 without changing the frozen Phase-A repair ledger or inventing final retry counts.

## Canonical constraints preserved

The v0.1 authority defines repair as the same authoritative source packet, same specialist mode, same InferenceProfile, a new context, new sampler, new attempt UUID, and the exact machine validation error. It also requires finite aggregate model-attempt/token budgets and forbids repair from gaining invented facts or expanded authority.

## PRE-1 implementation

- Added `contracts/policies/repair_shape.py` as the A1 semantic/settings bridge.
- All 20 current PRE-version learned contracts keep explicit `repair.allowed=True`.
- Removed numeric `max_repairs` ownership from `RepairShape`; contracts now describe semantic repair invariants only.
- Added `max_repair_attempts` to the separate AAE tuning settings handler. The knob accepts nonnegative integers, including zero.
- Checked-in R0 PRE-1 profiles intentionally leave the numeric repair count unresolved until testing/qualification gives evidence for values. Unresolved never means unlimited.
- Added typed host stops: `REPAIR_NOT_ALLOWED`, `REPAIR_LIMIT_UNRESOLVED`, and `REPAIR_BUDGET_EXHAUSTED`.
- The model repair projection contains the unchanged authoritative source packet, same specialist/profile identity, new attempt UUID, and exact frozen validation error. The previous invalid output remains host audit evidence and is not re-fed as model authority.
- The deterministic Phase-A `RepairPolicy` / `RepairBasis` / `RepairAttempt` / `RepairSession` machinery remains unchanged and authoritative for hashing, lineage, UUID uniqueness, fresh-context/sampler requirements, and aggregate cap enforcement.

## Files

```text
src/arcadia/contracts/policies/repair_shape.py
src/arcadia/contracts/policies/__init__.py
src/arcadia/contracts/aae/types.py
src/arcadia/contracts/aae/registry.py
src/arcadia/settings/handler.py
configs/aae_tuning.pre1.toml
tests/unit/contracts/policies/test_repair_shape.py
tests/unit/settings/test_handler.py
project/TODO_A1_STRICT_SCHEMAS_POLICIES.md
project/DECISIONS.md
```

## Local verification

Focused registry + repair shape + settings + existing Phase-A repair tests:

```text
60 passed
```

Broader runnable repository suite on this container, excluding only the unavailable Hypothesis modules and the intentional Python-3.12 environment assertion:

```text
466 passed
```

`python -m compileall -q src tests` also passed.

The canonical Windows environment should run `check.bat` before checkpointing this PRE-version.

## Still open

- Final `max_repair_attempts` values per specialist/profile remain intentionally unresolved.
- Aggregate per-turn learned-call/token/work budgets still belong to their broader runtime budget authority.
- Actual fresh context/sampler creation is A2 runtime work; PRE-1 records and tests the mandatory requirement without pretending to instantiate model runtime state.
- Gate A1 remains open.
