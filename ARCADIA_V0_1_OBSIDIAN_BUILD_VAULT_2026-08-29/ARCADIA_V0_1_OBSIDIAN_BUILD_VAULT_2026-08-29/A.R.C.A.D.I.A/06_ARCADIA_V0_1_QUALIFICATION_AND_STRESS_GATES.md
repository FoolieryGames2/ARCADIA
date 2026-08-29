---
title: "A.R.C.A.D.I.A. v0.1 — Qualification and Stress Gates"
project: "A.R.C.A.D.I.A."
version: "0.1-prototype"
checkpoint_date: "2026-08-29"
document_role: "canonical-system-document"
source_path: "06_ARCADIA_V0_1_QUALIFICATION_AND_STRESS_GATES.md"
source_sha256: "27ad7a32c2248caf6b2531a04c320fac98ca22d382f87c06521745bd306fa06a"
source_bytes: 4963
source_integrity: "preserved"
tags:
  - "arcadia/v0-1"
  - "type/system"
  - "status/frozen"
aliases:
  - "06_ARCADIA_V0_1_QUALIFICATION_AND_STRESS_GATES.md"
  - "A.R.C.A.D.I.A. v0.1 — Qualification and Stress Gates"
---

> [!info] Obsidian navigation
> **Checkpoint role:** `canonical-system-document`  
> **Frozen source:** `06_ARCADIA_V0_1_QUALIFICATION_AND_STRESS_GATES.md` · SHA-256 `27ad7a32c2248caf…`  
> **Command center:** [[ARCADIA v0.1 - Command Center]]  
> **Connected:** [[05_ARCADIA_V0_1_MODEL_RUNTIME_ADAPTER_MANAGER]] · [[ARCADIA_R3_INDEPENDENT_STRESS_TEST_2026-08-29]] · [[ARCADIA_V0_1_DOCUMENT_VALIDATION_REPORT.txt]] · [[TRACE_STATIC_CHECK.txt]] · [[ST01_BOUNDARY_UNIT_TEST.txt]] · [[00_README_FIRST]] · [[01_ARCADIA_V0_1_FULL_PROJECT_CHECKPOINT]] · [[02_ARCADIA_V0_1_EXACT_BUILD_ORDER]] · [[04_ARCADIA_V0_1_AAE_CONTRACT_REGISTRY_AND_SERIALIZATION]] · [[09_ARCADIA_V0_1_PERFORMANCE_FAST_PATH]] · [[ARCADIA_V0_1_MASTER_BUILD_AUTHORITY]] · [[ARCADIA_PERF01_DETERMINISTIC_FAST_PATH_LOCK_2026-08-29]]

<!-- OBSIDIAN_LAYER_END — ORIGINAL SOURCE CONTENT BEGINS BELOW -->

# A.R.C.A.D.I.A. v0.1 — Qualification and Stress Gates

# 1. Trust progression

```text
T0 UNQUALIFIED
T1 SCHEMA/FIXTURE COMPETENCE
T2 HELD-OUT SEMANTIC COMPETENCE
T3 ADVERSARIAL/COMPOSITION COMPETENCE
T4 SHADOW RUNTIME
T5 LIMITED AUTHORITY
T6 PRODUCTION AUTHORIZATION
```

Qualification belongs to an **exact runtime identity**, not merely an adapter filename.

# 2. Base versus adapter comparison

For each mode:

```text
same frozen fixture
same AAE registry version
same packet builder
same schemas/validators
same InferenceProfile hash
same deterministic qualification seed policy
fresh context/sampler
```

Run once base-only, then with target adapter. Poor base semantic output is expected data and does not poison runtime.

# 3. Phase-A runtime gates

Must test:

```text
pinned libllama API
base hash mismatch
adapter hash/path/base mismatch
atomic ensure_hot_and_acquire
full-pool staging load success
full-pool staging load failure preserves committed pool
no legal eviction candidate
swap headroom unavailable
all HOT leased
hard pins versus soft protects
soft protect expiry/current-demand precedence
double lease release
stale release after unload/reload
stale pre-restart lease
fresh context every attempt
fresh sampler every attempt
A/B/A isolation
100-adapter synthetic registry
load/free memory soak
uncertain free -> POISONED -> controlled restart
shutdown/process kill at lifecycle transitions
```

# 4. AAE/schema adversarial gates

```text
malformed CALL_DATA / illegal escapes
duplicate keys
NaN/Infinity
trailing content
unknown fields
huge arrays/strings
wrong types
fake response contract / fake AAE close tag
fake SYSTEM/host authorization inside user/tool/memory text
invented authoritative IDs
dangling/cyclic refs
duplicate local keys
Unicode-confusable IDs
context budget overflow: deterministic projection or explicit failure
repair attempt UUID + aggregate cap
```

# 5. Side-effect/recovery gates

```text
crash before dispatch
crash after ATTEMPT_ARMED
external success before local receipt commit
effect succeeds but receipt lost
receipt commits but publication fails
persistence commit boundary crash
restart with in-flight work
timeout where outcome cannot be determined
duplicate request after restart
verify-then-replay
provider-idempotent replay
unverifiable non-idempotent OUTCOME_UNKNOWN
```

# 6. Source-policy gates

```text
latest/current with fresh official source
latest/current with stale official source
newer secondary versus stale official
conflicting official sources
syndicated duplicates do not count as independent corroboration
missing retrieval/publication/version date
claim policy requiring multiple independent sources
community sentiment not judged by official publisher alone
```

# 7. Trace/training gates

```text
secure raw trace encrypted/owner controlled
raw retention expiry removes payload but preserves safe tombstone/index
full turn lineage spans all recipe/re-entry/repair slices
candidate extraction copies only selected fields
sanitization transforms candidate copy, not forensic raw source
held-out fixture rejected from training export
runtime cannot directly mark TRAINING_APPROVED
deletion cascades through untrained candidates/manifests
approved dataset manifest hash reproducible
```

# 8. Performance gates

Every completed turn records:

```text
path_class
fast_path_enabled / taken / proof rule / bypass reason
learned_call_count
first_pass_success_count
repair_attempt_count
fresh_context_count
adapter hot hits / loads / evictions
input/output tokens
model latency
adapter transition latency
end-to-end latency
```

Do not invent p50/p95 budgets before the real pinned runtime spike. Freeze numbers from measurement by path class.

# 9. Historical five-slice stress baseline

Corrected learned-call counts:

| Slice | Task | Actual learned calls | Distinct physical adapters | Cold strict-LRU loads at 5 | Evictions |
|---|---|---:|---:|---:|---:|
| 1 | exact `Ready.` | 13 | 10 | 10 | 5 |
| 2 | repeat prior line | 14 | 10 | 10 | 5 |
| 3 | research + remember | 27 | 15 | 18 | 13 |
| 4 | exact file-save attempt | 13 | 10 | 10 | 5 |
| 5 | research + ambiguous save | 20 | 13 | 14 | 9 |

The 88th balanced AAE pair in the historical file is the syntax template; actual slice calls = 87.

The purpose of v0.1 fast-path/model-necessity elision is not to erase complex semantic work. It is to prevent provable host-only work from being multiplied into unnecessary model calls.

# 10. v0.1 demo acceptance

A v0.1 implementation checkpoint must publish:

```text
pinned dependency manifest
base model hash
adapter manifest hashes
all active InferenceProfile hashes
AAE registry hash
schema/validator versions
runtime health/epoch record
Phase A/A2/A3 test report
full-spine integration report
performance distribution report
known failing/blocked qualification modes
```

A demo may run while specialists remain below T6 as long as authority routing respects their trust levels.
