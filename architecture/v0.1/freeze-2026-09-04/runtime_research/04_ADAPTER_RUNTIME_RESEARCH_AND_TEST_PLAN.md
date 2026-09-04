# A.R.C.A.D.I.A. — Adapter Runtime Research and Test Plan

**Date:** 2026-09-03  
**Status:** QUALIFICATION PLAN / RESIDENCY POLICY NOT YET MEASURED

## Research question

> What local inference configuration can keep A.R.C.A.D.I.A.'s specialist adapter library available with the lowest safe transition cost while guaranteeing that exactly the requested specialist — and only that specialist — is active for each fresh learned call?

## Critical correction

`max_hot_adapters = 5` is **not** an A.R.C.A.D.I.A. semantic rule and is **not** a known llama.cpp ceiling.

It is a provisional/measured runtime policy from the earlier design and stress simulations.

The architecture already separates:

```text
installed adapter library size
!= loaded/HOT adapter count
!= ACTIVE adapter count
```

A.R.C.A.D.I.A. should therefore test the preferred hypothesis rather than design around an assumed five-object cap.

## Preferred hypothesis

```text
one pinned base model
all core adapters physically loaded/resident if memory permits
all adapters inactive between calls
exactly one adapter active for a normal learned call
fresh context + fresh sampler per attempt
```

This is conceptually:

```text
Adapter 01   loaded   inactive
Adapter 02   loaded   inactive
...
Adapter 15   loaded   inactive

CALL needs Adapter 08
    -> bind/apply Adapter 08 to fresh context
    -> all others remain inactive for that call
```

## Grounded llama.cpp basis

Current official llama.cpp exposes separate adapter-load and context-application primitives:

```text
llama_adapter_lora_init(...)
llama_set_adapters_lora(...)
llama_adapter_lora_free(...)
```

Its current server also documents:

```text
--lora-init-without-apply
```

which loads adapters without initially applying them, and per-request LoRA lists where unspecified adapters default to scale `0.0`.

This does **not** prove A.R.C.A.D.I.A.'s desired all-15 deployment is safe or fast on the target hardware. It does prove that the key conceptual separation — loaded versus applied — exists in current llama.cpp.

## Canonical A.R.C.A.D.I.A. runtime position

The current R3 architecture still prefers:

```text
Recipe
  -> SpecialistInvoker
      -> AdapterManager
          -> ModelRuntime
              -> pinned libllama
```

`llama-server` should be treated as:

- a useful feasibility/reference implementation;
- a comparison target;
- possibly a temporary spike harness;

but **not automatically as the canonical recipe-side adapter authority**.

## Candidate residency strategies to benchmark

### Strategy A — All core adapters loaded, one active

Goal: determine whether all 15 v0.1 adapters can remain live without swaps.

Expected advantage:

```text
near-zero physical adapter load/free churn during normal turns
```

Risk:

```text
RAM/VRAM/backend allocation may make this unsafe or leave too little inference headroom
```

### Strategy B — Measured bounded HOT pool + STAGING

The current safe fallback architecture.

```text
committed HOT ceiling = measured N
one temporary STAGING slot/headroom for load-before-commit replacement
one ACTIVE adapter per call
```

The ceiling might be 5, but it might also be 7, 10, 15, or another value. Measurement decides.

### Strategy C — Larger CPU-resident / smaller active device set

If backend behavior supports it efficiently, test keeping a broader adapter cache in host memory while only the needed subset occupies expensive device memory/resources.

This resembles a common multi-LoRA serving pattern; vLLM, for example, explicitly separates the number of LoRAs active in a batch from the size of its CPU LoRA cache. This is a comparison point, not a runtime commitment.

## Phase A2 — test-double qualification

Before real model/adapter testing, prove host state-machine correctness:

```text
COLD / READY / HOT
STAGING transaction state
ACTIVE per call
HEALTHY / QUARANTINED / POISONED
process_epoch
handle_generation
ensure_hot_and_acquire()
linear lease release
hard vs soft protection
current-demand precedence
controlled poisoned restart
100-entry synthetic registry
```

Mandatory failure tests:

- forced replacement load failure while full;
- old committed HOT set remains unchanged;
- stale-generation release;
- duplicate lease release;
- every HOT adapter leased;
- every candidate hard-pinned;
- stale soft protection cannot deadlock current demand;
- shutdown during lifecycle transitions.

## Phase A3 — real Qwen3 / LoRA runtime matrix

### Base identity

```text
Qwen/Qwen3-4B-Instruct-2507
```

Runtime GGUF quantization remains a measured variable.

### Residency ladder

Measure at least:

```text
BASE ONLY
+ 1 loaded inactive adapter
+ 5 loaded inactive adapters
+ 10 loaded inactive adapters
+ 15 loaded inactive adapters
```

For each step record:

```text
host RAM baseline/delta
VRAM baseline/delta
load latency
peak memory
context creation latency
adapter apply/select latency
TTFT
tokens/sec
end-to-end latency
failure/crash count
```

### Activation isolation sequence

Use strongly distinguishable adapter fixtures:

```text
A -> B -> A -> C -> B
```

Verify every call:

```text
fresh context identity
fresh sampler identity
correct adapter identity
exactly intended adapter active
no previous-call KV/token state
correct activation receipt
no stale process epoch/handle generation
```

Then hammer alternating calls:

```text
A/B/A/B/A/B/...
```

for a long soak.

### Residency comparison

Benchmark the same workload under:

```text
ALL-RESIDENT candidate
vs
measured bounded-pool candidate
```

Compare:

```text
adapter load/free count
adapter transition latency
end-to-end latency
peak RAM/VRAM
memory trend over time
crashes/restarts
first-pass learned success
```

## Stress-test workload reuse

Reuse the historical five-slice adapter churn as a baseline workload shape:

| Slice | Calls | Distinct adapters | strict-LRU loads @5 | evictions @5 |
|---|---:|---:|---:|---:|
| 1 | 13 | 10 | 10 | 5 |
| 2 | 14 | 10 | 10 | 5 |
| 3 | 27 | 15 | 18 | 13 |
| 4 | 13 | 10 | 10 | 5 |
| 5 | 20 | 13 | 14 | 9 |

Run both fast-path OFF and fast-path ON where applicable. This separates architecture qualification from expected normal-runtime optimization.

## Success criteria

Do not declare a residency strategy qualified because one demonstration works.

Require:

```text
no wrong-adapter activation
no stale context/sampler contamination
no unacceptable memory growth trend
no unsafe eviction of leased handles
provable behavior on full-pool load failure
complete activation receipts
controlled recovery from poisoned runtime state
measured p50/p95 end-to-end behavior by path class
```

## Decision rule

```text
If all-15 loaded/inactive passes safely:
    prefer it and reduce normal swap churn.

If it fails memory/headroom/isolation/latency gates:
    use the largest measured safe committed HOT pool with STAGING.

If direct libllama behavior is unstable:
    evaluate another runtime/backend without changing Recipe ownership.
```

The runtime implementation is replaceable infrastructure. The semantic spine is not a cache-policy hostage.
