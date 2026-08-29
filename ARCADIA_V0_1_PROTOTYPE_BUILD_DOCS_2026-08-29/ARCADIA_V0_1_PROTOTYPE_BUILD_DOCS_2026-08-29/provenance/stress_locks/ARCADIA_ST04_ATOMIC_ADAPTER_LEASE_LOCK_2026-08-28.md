# A.R.C.A.D.I.A. R3 — ST-04 Atomic Adapter Lease Lock

**Date:** 2026-08-28  
**User-march item:** #3  
**Stress item:** ST-04 — atomic acquisition exists in pseudocode but not in the required interface  
**Status:** **CLOSED FOR DESIGN / LOCKED IMPLEMENTATION CONTRACT**  
**Scope:** learned-call AdapterManager acquisition/release API, lease identity, and serialized lifecycle mutation.

## 1. Superseded call-facing API

For learned calls, the independent sequence:

```text
ensure_hot(adapter_id)
acquire(adapter_id)
```

is forbidden because eviction or lifecycle mutation can occur between the two operations.

These operations may exist only as private/internal helpers if needed; recipe code and SpecialistInvoker may not compose them independently.

## 2. Frozen invariant — ST04-G01

> Every learned adapter activation MUST acquire residency and eviction protection through the single atomic call-facing operation `ensure_hot_and_acquire(adapter_id, ...) -> AdapterLease`. Residency assurance and lease acquisition are one synchronized AdapterManager transaction. No caller may observe a promised HOT adapter with `lease_count == 0` between assurance and acquisition.

## 3. Required call-facing interface — ST04-G02

```text
ensure_hot_and_acquire(adapter_id, minimum_trust, ...) -> AdapterLease
release(lease) -> release result
snapshot() -> manager state
```

`SpecialistInvoker` is the learned-call consumer of this interface. Recipe code does not call AdapterManager directly.

## 4. AdapterLease identity — ST04-G03

Every returned lease carries at minimum:

```text
adapter_id
live_handle reference/token
handle_generation
process_epoch
lease_uuid
activation_receipt / activation identity
released flag or equivalent host-owned linear-state record
```

`handle_generation` changes whenever a new live adapter handle replaces a previous live handle for that adapter within a process epoch.

`process_epoch` changes on runtime/process initialization so pre-restart leases cannot mutate post-restart state.

`lease_uuid` is unique per acquisition even when many callers concurrently lease the same live handle.

## 5. Linear release semantics — ST04-G04

A lease is consumable exactly once:

```text
ISSUED -> ACTIVE -> RELEASED
```

Rules:

- first valid release decrements the matching generation's lease count exactly once;
- double release is rejected and does not mutate counts;
- a release whose process epoch does not match current runtime is rejected;
- a release whose handle generation does not match the current/matching live generation is rejected as stale;
- stale/double-release attempts are forensic events, not silent success.

Recommended typed failures include:

```text
LEASE_ALREADY_RELEASED
STALE_LEASE_GENERATION
STALE_PROCESS_EPOCH
LEASE_IDENTITY_MISMATCH
```

## 6. Prototype synchronization policy — ST04-G05

For the first runtime spike, AdapterManager lifecycle mutations are serialized under one manager mutation lock (or equivalent single-threaded critical section). This includes:

- load/staging commit;
- eviction selection and commitment;
- lease acquisition;
- lease release;
- handle-generation mutation;
- pool membership mutation.

Do not optimize to per-adapter/lock-free concurrency until correctness tests and telemetry justify it.

Potentially slow backend operations may later use reservation states and finer-grained synchronization, but any optimization must preserve the atomic external contract.

## 7. Interaction with ST-03 — ST04-G06

When the committed HOT pool is full, `ensure_hot_and_acquire(N)` owns the entire ST-03 prepare/commit sequence.

On successful staged replacement:

```text
stage N
prove N live
commit legal victim eviction
promote N HOT
increment N lease before exposing the successful acquisition
return lease
```

On failed staged replacement:

```text
discard/health-handle staging N
old committed pool unchanged
no lease returned
```

There is no externally visible interval where the newly promised adapter is HOT but unleased.

## 8. Required acceptance tests

1. Race acquisition against eviction -> requested adapter cannot disappear between ensure and acquire because no such call-facing gap exists.
2. 100 concurrent requests for the same READY adapter -> one physical live generation, 100 unique leases, correct final lease count.
3. Double release -> second release rejected; count unchanged.
4. Evict and reload same adapter -> handle generation increments.
5. Release an old-generation lease after reload -> rejected; new generation count untouched.
6. Process restart -> prior-process lease rejected.
7. Inference/context failure -> finally-path valid release returns count to prior value.
8. ST-03 full-pool staged replacement + acquisition -> eviction/promotion/lease commitment behaves as one externally atomic acquisition.

## 9. Canonical-consolidation patch intent

Future canonical runtime interface sections must remove separate call-facing `ensure_hot()` + `acquire()` and expose `ensure_hot_and_acquire()` as the sole learned-call acquisition operation. The existing reference pseudocode already points in this direction; the interface must be made consistent with it.
