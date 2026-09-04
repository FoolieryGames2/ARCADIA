# A.R.C.A.D.I.A. — Adapter Runtime Experiment Result Template

Use one copy per pinned runtime/model configuration.

## Identity

```text
experiment_id:
date:
hardware:
OS:
Python:
CUDA/driver:
llama.cpp commit:
llama.cpp build flags:
libllama hash:
base model:
base GGUF filename:
base GGUF SHA-256:
quantization:
context profile:
InferenceProfile hash:
adapter set manifest hash:
```

## Residency policy

```text
strategy: ALL_RESIDENT | BOUNDED_HOT_POOL | OTHER
configured max_hot:
staging headroom policy:
loaded inactive adapter count:
active adapters per normal call: 1
fresh context per attempt: yes/no
fresh sampler per attempt: yes/no
```

## Memory baseline

| State | Host RAM | VRAM | Notes |
|---|---:|---:|---|
| process start | | | |
| base loaded | | | |
| +1 adapter loaded inactive | | | |
| +5 | | | |
| +10 | | | |
| +15 | | | |
| inference peak | | | |
| post-soak | | | |

## Isolation sequence

```text
A -> B -> A -> C -> B
```

| Call | Expected adapter | Actual receipt adapter | Fresh ctx | Fresh sampler | Wrong adapter active? | PASS/FAIL |
|---|---|---|---|---|---|---|
| 1 | A | | | | | |
| 2 | B | | | | | |
| 3 | A | | | | | |
| 4 | C | | | | | |
| 5 | B | | | | | |

## Performance

| Metric | p50 | p95 | max | Notes |
|---|---:|---:|---:|---|
| adapter select/apply | | | | |
| context creation | | | | |
| TTFT | | | | |
| tokens/sec | | | | |
| learned-call latency | | | | |
| end-to-end turn latency | | | | |

## Churn

```text
adapter hot hits:
adapter physical loads:
adapter frees:
evictions:
staging replacements:
poisoned restarts:
wrong-adapter incidents:
OOM incidents:
```

## Failure injection

- [ ] full-pool replacement load fails; old committed set preserved
- [ ] stale lease release rejected
- [ ] duplicate release rejected
- [ ] all HOT leased exhaustion handled
- [ ] hard-pin exhaustion handled
- [ ] stale soft protection overridden by current demand
- [ ] shutdown during load
- [ ] shutdown during context creation
- [ ] shutdown during inference
- [ ] uncertain cleanup -> POISONED -> controlled new epoch

## Soak

```text
iterations:
duration:
start RAM/VRAM:
end RAM/VRAM:
trend acceptable: yes/no
errors:
```

## Verdict

```text
QUALIFIED / NOT QUALIFIED / NEEDS FOLLOW-UP
```

### Reason

...

### Next action

...
