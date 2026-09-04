# A.R.C.A.D.I.A. — Return-to-Build Checklist

**Date:** 2026-09-03

## Decision

Return to implementation. Do **not** reopen the full architecture before writing code unless a new empirical failure violates a frozen invariant.

## Immediate documentation patches before/alongside build

- [ ] Replace current-authority claims that the base is a generic/locked `3B` model with `Qwen/Qwen3-4B-Instruct-2507` or a size-neutral pinned-base reference.
- [ ] Preserve historical documents as history; add supersession notes instead of silently rewriting provenance.
- [ ] Enforce the terminology rule: `Howard` only means the Howard conversational adapter/personality.
- [ ] Keep `max_hot_adapters = 5` labeled as a provisional/measured policy, not a hard system limit.
- [ ] Record that all-resident/zero-active-between-calls is a primary A3 research candidate, not a proven deployment state.

## Existing build gates still matter

### A1 — contract/serializer gate

- [ ] Finish registry-wide strict schemas/policies.
- [ ] Prove runtime and training resolve from the same AAE source.
- [ ] Finish deterministic context-budget projection.
- [ ] Freeze measured per-mode settings/InferenceProfiles when runtime evidence exists.
- [ ] Run canonical Windows CPython 3.12 `check.bat` before closing A1.

### A2 — test-double runtime

- [ ] Implement `ModelRuntime / AdapterManager / SpecialistInvoker` state machine.
- [ ] Atomic `ensure_hot_and_acquire()` only.
- [ ] STAGING load-before-commit.
- [ ] HEALTHY/QUARANTINED/POISONED.
- [ ] Fresh context + fresh sampler per attempt.
- [ ] Process epoch + handle generation + linear leases.
- [ ] Failure/race tests pass.

### A3 — real model/runtime

- [ ] Pin exact Qwen3 GGUF candidate hash.
- [ ] Pin exact llama.cpp commit/build/library hash.
- [ ] Run BASE_ONLY_TEST_MODE through real SpecialistInvoker.
- [ ] Run a small real LoRA set first.
- [ ] Run A/B/A isolation.
- [ ] Run memory/load/free soak.
- [ ] Benchmark 1/5/10/15 loaded-inactive adapter residency.
- [ ] Determine safe production residency strategy from measurements.
- [ ] Keep learned authority at T0 until qualification proves more.

## What does NOT need another architecture brainstorm first

The original independent stress-test findings ST-01 through ST-10 have current architectural answers in the master build authority.

Do not spend another design cycle rediscovering:

```text
strict CALL_DATA gate
STAGING replacement
atomic lease acquisition
runtime POISONED state
inference profile hashing
AAE authority/data separation
SourcePolicyRegistry
OperationJournal / OUTCOME_UNKNOWN
trace privacy / training firewall
deterministic fast path
```

Implement and test them.

## Stop-and-redesign triggers

Reopen architecture only if real implementation proves a structural assumption false, such as:

- current llama.cpp cannot safely satisfy single-active adapter isolation;
- adapter residency cannot be made race-safe with the current ownership split;
- required semantics cannot be represented without violating recipe ownership;
- Context/Decision/Execution/Persistence boundaries prove mechanically impossible;
- target hardware makes the intended local system unusable even after measured residency/quantization tuning.

Performance disappointment alone should first trigger measurement and runtime-policy tuning, not semantic recipe collapse.

## Build-order note

The existing master build authority explicitly authorizes deterministic host foundation and narrow runtime spikes while withholding production trust until exact runtime identities qualify.

That remains the correct posture.
