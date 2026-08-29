---
title: "A.R.C.A.D.I.A. R3 — ST-03 Transactional HOT-Swap Lock"
project: "A.R.C.A.D.I.A."
version: "0.1-prototype"
checkpoint_date: "2026-08-29"
document_role: "stress-lock"
source_path: "provenance/stress_locks/ARCADIA_ST03_TRANSACTIONAL_HOT_SWAP_LOCK_2026-08-28.md"
source_sha256: "f0f47042ec2d35018436a7420695308a1d4281e3d834aea7085b0acd213da3c5"
source_bytes: 4129
source_integrity: "preserved"
tags:
  - "arcadia/v0-1"
  - "type/provenance"
  - "type/stress-lock"
  - "status/frozen"
aliases:
  - "ARCADIA_ST03_TRANSACTIONAL_HOT_SWAP_LOCK_2026-08-28.md"
  - "A.R.C.A.D.I.A. R3 — ST-03 Transactional HOT-Swap Lock"
---

> [!info] Obsidian navigation
> **Checkpoint role:** `stress-lock`  
> **Frozen source:** `provenance/stress_locks/ARCADIA_ST03_TRANSACTIONAL_HOT_SWAP_LOCK_2026-08-28.md` · SHA-256 `f0f47042ec2d3501…`  
> **Command center:** [[ARCADIA v0.1 - Command Center]]  
> **Connected:** [[05_ARCADIA_V0_1_MODEL_RUNTIME_ADAPTER_MANAGER]] · [[ARCADIA_R3_STRESS_RESOLUTION_LEDGER_2026-08-28]]

<!-- OBSIDIAN_LAYER_END — ORIGINAL SOURCE CONTENT BEGINS BELOW -->

# A.R.C.A.D.I.A. R3 — ST-03 Transactional HOT-Swap Lock

**Date:** 2026-08-28  
**User-march item:** #2  
**Stress item:** ST-03 — pool-full load failure cannot preserve previous HOT pool under eviction-first ordering  
**Status:** **CLOSED FOR DESIGN / LOCKED IMPLEMENTATION CONTRACT**  
**Scope:** AdapterManager pool-full replacement behavior and swap-headroom policy.

## 1. Superseded behavior

The R3 sequence `select victim -> free victim -> load requested adapter` is superseded for ordinary pool-full replacement. It conflicts with the lifecycle invariant that a failed replacement load leaves the previously committed HOT pool unchanged.

## 2. Frozen invariant — ST03-G01

> A failed adapter load MUST NOT alter the committed HOT set. Pool-full replacement is a prepare/commit transaction: the requested adapter is loaded into one temporary manager-owned STAGING handle while the legal eviction candidate remains HOT. Only after the replacement handle loads and passes required runtime validation may the manager commit the victim eviction and promote the replacement to HOT.

## 3. STAGING semantics — ST03-G02

`STAGING` is not a fourth durable residency class alongside COLD/READY/HOT. It is a temporary transactional state owned only by AdapterManager during replacement.

A STAGING handle:

- is not exposed to recipe code;
- is not returned to SpecialistInvoker;
- is not eligible for ordinary acquisition;
- is not counted as a committed HOT member;
- must be either promoted atomically or discarded;
- must carry its own transition/telemetry record.

## 4. Swap sequence — ST03-G03

```text
request N while committed HOT pool is full
  -> synchronize manager mutation
  -> select one legal victim V (lease_count == 0; not hard-pinned; policy-legal)
  -> verify measured swap headroom
  -> load N as temporary STAGING while V remains HOT
  -> validate N's live handle/runtime identity

if N fails:
  -> discard/clean STAGING N
  -> do not evict V
  -> committed HOT set is byte-for-byte/logically unchanged
  -> return ADAPTER_LOAD_FAILED (or stronger health-state failure if cleanup is uncertain)

if N succeeds:
  -> commit eviction of V
  -> promote N to committed HOT
  -> acquisition/lease semantics continue under ST-04 atomic acquisition lock
```

## 5. Memory/headroom policy — ST03-G04

`max_hot_adapters` is the steady-state committed HOT ceiling, not permission to exceed measured physical safety.

The configured steady ceiling must leave enough measured reserve for:

```text
base model
+ committed HOT pool
+ one temporary STAGING adapter
+ fresh context/inference peak
+ required host/VRAM safety reserve
```

If one STAGING handle cannot safely coexist with the configured committed pool, the steady HOT ceiling must be reduced until transactional replacement is safe. The host must not evict first merely to make room.

## 6. Failure interaction — ST03-G05

A normal replacement-load failure is non-destructive to the committed pool.

If cleanup of the failed STAGING handle is uncertain, the manager must not pretend rollback succeeded. That case routes to the runtime-health policy defined by ST-05 (user-march item #4), which may quarantine/poison the residency domain and require controlled restart.

## 7. Required acceptance tests

1. `HOT={A,B,C,D,E}`, force `F` load failure -> `HOT` remains exactly `{A,B,C,D,E}` with same live generations and lease counts.
2. Same setup, allow `F` success -> `E` remains HOT until `F` is proven live; then exactly one legal eviction commits and final `HOT={A,B,C,D,F}`.
3. No legal eviction candidate -> no load transaction begins; committed HOT pool unchanged.
4. Swap headroom unavailable -> no victim eviction and no unsafe staging load; fail closed or use lower configured steady HOT ceiling.
5. Failed STAGING cleanup becomes uncertain -> route to ST-05 health-state handling rather than claiming ordinary rollback success.

## 8. Canonical-consolidation patch intent

Future canonical R3/R4 runtime documents must replace eviction-first wording with this prepare/commit staging policy and update lifecycle/pool tests accordingly.
