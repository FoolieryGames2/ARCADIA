---
title: "MOC — Runtime, AAE, and Qualification"
project: "A.R.C.A.D.I.A."
version: "0.1-prototype"
generated_navigation: true
tags:
  - "arcadia/v0-1"
  - "moc/runtime"
---

# MOC — Runtime, AAE, and Qualification

## Boundary chain

```mermaid
flowchart LR
    Recipe[Recipe / Host packet] --> Gate[CALL_DATA hard gate]
    Gate --> Registry[AAE Contract Registry]
    Registry --> Serializer[Canonical AAE Serializer]
    Serializer --> Invoker[SpecialistInvoker]
    Invoker --> Manager[AdapterManager lease]
    Manager --> Runtime[ModelRuntime]
    Runtime --> Output[Schema + host validation]
```

## Canonical specs

- [[04_ARCADIA_V0_1_AAE_CONTRACT_REGISTRY_AND_SERIALIZATION|AAE Contract Registry & Canonical Serialization]]
- [[05_ARCADIA_V0_1_MODEL_RUNTIME_ADAPTER_MANAGER|ModelRuntime + AdapterManager]]
- [[06_ARCADIA_V0_1_QUALIFICATION_AND_STRESS_GATES|Qualification & Stress Gates]]
- [[09_ARCADIA_V0_1_PERFORMANCE_FAST_PATH|Performance / Fast Path]]

## Stress locks that hardened this boundary

- [[ARCADIA_ST01_AAE_CALL_DATA_LOCK_2026-08-28|ST01 — CALL_DATA]]
- [[ARCADIA_ST03_TRANSACTIONAL_HOT_SWAP_LOCK_2026-08-28|ST03 — Transactional hot swap]]
- [[ARCADIA_ST04_ATOMIC_ADAPTER_LEASE_LOCK_2026-08-28|ST04 — Atomic adapter lease]]
- [[ARCADIA_ST05_RUNTIME_HEALTH_POISON_LOCK_2026-08-29|ST05 — Runtime health / poison]]
- [[ARCADIA_ST06_INFERENCE_PROFILE_QUALIFICATION_LOCK_2026-08-29|ST06 — InferenceProfile qualification]]
- [[ARCADIA_ST07_AAE_SERIALIZATION_INJECTION_LOCK_2026-08-29|ST07 — Serialization / injection]]
- [[ARCADIA_PERF01_DETERMINISTIC_FAST_PATH_LOCK_2026-08-29|PERF01 — Deterministic fast path]]

## Reference proofs

- [[arcadia_aae_boundary.py|AAE boundary reference implementation]]
- [[test_arcadia_aae_boundary.py|AAE boundary unit tests]]
- [[ST01_BOUNDARY_UNIT_TEST.txt|Boundary unit-test output]]
- [[arcadia_r3_static_stress_check.py|Static stress checker]]
- [[TRACE_STATIC_CHECK.txt|Static-check output]]
