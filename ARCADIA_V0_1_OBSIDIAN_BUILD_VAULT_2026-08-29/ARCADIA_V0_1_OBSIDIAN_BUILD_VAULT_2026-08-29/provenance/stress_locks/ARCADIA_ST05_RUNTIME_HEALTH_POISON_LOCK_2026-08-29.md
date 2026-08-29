---
title: "A.R.C.A.D.I.A. R3 — ST-05 Runtime Health / Poison Lock"
project: "A.R.C.A.D.I.A."
version: "0.1-prototype"
checkpoint_date: "2026-08-29"
document_role: "stress-lock"
source_path: "provenance/stress_locks/ARCADIA_ST05_RUNTIME_HEALTH_POISON_LOCK_2026-08-29.md"
source_sha256: "c6decaede8f7918d222adafc8c810a911622ac7a25d0d25f37f340c474e39d82"
source_bytes: 5892
source_integrity: "preserved"
tags:
  - "arcadia/v0-1"
  - "type/provenance"
  - "type/stress-lock"
  - "status/frozen"
aliases:
  - "ARCADIA_ST05_RUNTIME_HEALTH_POISON_LOCK_2026-08-29.md"
  - "A.R.C.A.D.I.A. R3 — ST-05 Runtime Health / Poison Lock"
---

> [!info] Obsidian navigation
> **Checkpoint role:** `stress-lock`  
> **Frozen source:** `provenance/stress_locks/ARCADIA_ST05_RUNTIME_HEALTH_POISON_LOCK_2026-08-29.md` · SHA-256 `c6decaede8f7918d…`  
> **Command center:** [[ARCADIA v0.1 - Command Center]]  
> **Connected:** [[05_ARCADIA_V0_1_MODEL_RUNTIME_ADAPTER_MANAGER]] · [[08_ARCADIA_V0_1_RECOVERY_TRACE_PRIVACY]] · [[ARCADIA_R3_STRESS_RESOLUTION_LEDGER_2026-08-28]]

<!-- OBSIDIAN_LAYER_END — ORIGINAL SOURCE CONTENT BEGINS BELOW -->

# A.R.C.A.D.I.A. R3 — ST-05 Runtime Health / Poison Lock

**Date:** 2026-08-29  
**Stress item:** ST-05 — failure state machine has no place for uncertainty  
**Status:** **CLOSED — design lock**  
**Scope:** runtime mechanical health, quarantine/poison behavior, controlled restart, and separation from model qualification outcomes.

## 1. Frozen model

Residency and health are independent host-owned dimensions.

### Residency

```text
COLD
READY
STAGING   # transactional internal state from ST-03
HOT
```

`ACTIVE` remains call-specific and does not replace residency.

### Health

```text
HEALTHY
QUARANTINED
POISONED
```

Residency describes last-known lifecycle placement. Health determines whether that state may be acted upon.

## 2. Frozen invariant — ST05-G01

> No learned call may acquire or use an adapter unless both the adapter and the owning ModelRuntime residency domain are HEALTHY.

Health is a mechanical-integrity signal. It is not model quality, semantic trust tier, qualification status, or answer correctness.

## 3. Model/qualification failures do NOT change runtime health — ST05-G02

The first BASE_ONLY_TEST_MODE qualification run is expected to expose poor model behavior. The following are ordinary model/contract outcomes and MUST NOT by themselves quarantine or poison the runtime:

- malformed or schema-invalid model output;
- invented references;
- semantic mistakes;
- uncertainty mistakes;
- repair-required output;
- repair exhaustion;
- wrong final answer;
- normal deterministic inference/apply failure returned through the documented typed host path.

These outcomes are recorded in qualification/runtime metrics and testing continues while mechanical state remains certain.

Therefore:

```text
BAD MODEL ANSWER != BAD RUNTIME
```

A base GGUF may fail most or all semantic fixtures while `ModelRuntime.health == HEALTHY` if the runtime remains mechanically coherent.

## 4. HEALTHY — ST05-G03

`HEALTHY` means lifecycle ownership assumptions remain mechanically trustworthy. New leases, contexts, loads, evictions, and inference may proceed subject to their normal gates.

Normal controlled operation failures do not automatically alter health.

## 5. QUARANTINED — ST05-G04

`QUARANTINED` is normally adapter-scoped.

Use it only when evidence shows a specific adapter's integrity can no longer be trusted while the shared backend/runtime domain remains mechanically trustworthy.

Examples include validated adapter-file/manifest integrity uncertainty or an adapter-local invariant violation that does not imply shared backend corruption.

Effects:

```text
adapter acquisition blocked
adapter cannot become ACTIVE
other HEALTHY adapters may continue if owning runtime domain remains HEALTHY
forensic event retained
```

A known typed load/apply failure alone does not imply quarantine unless it creates or reveals integrity uncertainty.

## 6. POISONED — ST05-G05

`POISONED` is runtime-domain scoped and means in-process backend/resource lifetime coherence can no longer be proven.

Poison-worthy examples include:

- uncertain adapter free / dangling-handle possibility;
- destructive FFI exception or fault with uncertain outcome;
- uncertain context destruction where backend lifetime may be compromised;
- backend allocator/runtime corruption;
- impossible handle ownership/generation invariant;
- any other shared-state condition where host labels can no longer truthfully describe physical lifetime state.

On poison, fail closed:

```text
NO NEW LEASES
NO NEW CONTEXTS
NO NEW INFERENCE
NO NEW ADAPTER LOADS
NO EVICTIONS / LIFETIME MUTATIONS EXCEPT CONTROLLED SHUTDOWN
```

Preserve the last-known residency for forensic reporting, but do not treat it as authoritative physical reality after poison.

## 7. Controlled restart — ST05-G06

`POISONED` is terminal for the current runtime epoch.

Illegal transition:

```text
POISONED -> HEALTHY   # same runtime epoch
```

Required recovery:

```text
POISONED
  -> stop new learned work
  -> preserve forensic event/trace
  -> controlled ModelRuntime teardown
  -> initialize fresh backend/base runtime
  -> allocate new runtime/process epoch
  -> revalidate required adapters
  -> inherit zero old handles and zero old leases
  -> HEALTHY
```

The ST-04 lease `process_epoch` / `handle_generation` rules make every pre-restart lease stale by construction.

## 8. Trust/qualification separation — ST05-G07

Health is orthogonal to qualification/trust.

Examples:

```text
T6 adapter + POISONED runtime -> DO NOT RUN
T1 adapter + HEALTHY runtime  -> mechanically usable only within T1 authority
BASE_ONLY_TEST_MODE + many semantic FAILs + HEALTHY runtime -> continue frozen suite
```

## 9. Failure ladder

```text
NORMAL OPERATION / MODEL FAILURE
  operation or semantic contract fails
  mechanical state remains certain
  -> record failure and continue safely

QUARANTINED
  one adapter's integrity is uncertain
  shared runtime remains mechanically certain
  -> block that adapter

POISONED
  shared runtime/lifetime state is uncertain
  -> stop learned work and restart runtime domain
```

## 10. Acceptance tests

At minimum:

```text
test_base_only_semantic_failure_runtime_stays_healthy
test_base_only_repair_exhaustion_runtime_stays_healthy
test_known_typed_apply_failure_does_not_auto_poison
test_adapter_local_integrity_uncertainty_quarantines_only_adapter
test_uncertain_free_poison_runtime_domain
test_poison_blocks_new_lease
test_poison_blocks_new_context_and_inference
test_poison_cannot_clear_in_same_epoch
test_controlled_restart_changes_epoch
test_old_lease_rejected_after_restart
test_restart_inherits_zero_old_handles_and_leases
```

## 11. Explicit non-claims

This lock does not claim the real llama.cpp backend has already been failure-injected. It freezes the required host semantics that the upcoming narrow runtime spike must implement and prove.
