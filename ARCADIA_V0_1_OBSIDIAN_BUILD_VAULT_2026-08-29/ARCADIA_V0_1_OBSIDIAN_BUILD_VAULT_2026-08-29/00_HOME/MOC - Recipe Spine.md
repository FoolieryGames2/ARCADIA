---
title: "MOC — Recipe Spine"
project: "A.R.C.A.D.I.A."
version: "0.1-prototype"
generated_navigation: true
tags:
  - "arcadia/v0-1"
  - "moc/recipes"
---

# MOC — Recipe Spine

## Frozen semantic chain

0. [[R0_CONVERSATION_RESOLVER_V0_1|Recipe 0 — Conversation Resolver]]
1. [[R1_INTENT_V0_1|Recipe 1 — Intent]]
2. [[R2_CONTEXT_V0_1|Recipe 2 — Context]]
3. [[R3_DECISION_V0_1|Recipe 3 — Decision]]
4. [[R4_TOOL_EXECUTION_V0_1|Recipe 4 — Tool / Execution]]
5. [[R5_RECONCILIATION_V0_1|Recipe 5 — Reconciliation]]
6. [[R6_PERSISTENCE_V0_1|Recipe 6 — Persistence]]
7. [[R7_COMPLETION_V0_1|Recipe 7 — Completion]]
8. [[R8_RESULT_V0_1|Recipe 8 — Result]]

```mermaid
flowchart LR
    A[R0 Resolver] --> B[R1 Intent]
    B --> C[R2 Context]
    C --> D[R3 Decision]
    D --> E[R4 Execution]
    E --> F[R5 Reconciliation]
    F --> G[R6 Persistence]
    G --> H[R7 Completion]
    H --> I[R8 Result]
```

## Cross-cutting authority every learned recipe inherits

- [[03_ARCADIA_V0_1_GLOBAL_CONTRACTS_AND_INVARIANTS|Global Contracts & Invariants]]
- [[04_ARCADIA_V0_1_AAE_CONTRACT_REGISTRY_AND_SERIALIZATION|AAE boundary and schemas]]
- [[05_ARCADIA_V0_1_MODEL_RUNTIME_ADAPTER_MANAGER|Runtime and adapter lifecycle]]
- [[06_ARCADIA_V0_1_QUALIFICATION_AND_STRESS_GATES|Qualification progression]]
- [[09_ARCADIA_V0_1_PERFORMANCE_FAST_PATH|Deterministic model-necessity / fast-path rules]]

## Recipe-specific system ties

- Context ↔ [[07_ARCADIA_V0_1_SOURCE_POLICY_REGISTRY|Source policy]] and [[ARCADIA_PERSISTENCE_SQLITE_SCHEMA_V0_1.sql|semantic-memory storage schema]]
- Tool / Execution ↔ [[08_ARCADIA_V0_1_RECOVERY_TRACE_PRIVACY|OperationJournal / OUTCOME_UNKNOWN]]
- Reconciliation ↔ [[07_ARCADIA_V0_1_SOURCE_POLICY_REGISTRY|claim-specific evidence policy]]
- Persistence ↔ [[08_ARCADIA_V0_1_RECOVERY_TRACE_PRIVACY|recovery + PRC]] and [[ARCADIA_PERSISTENCE_SQLITE_SCHEMA_V0_1.sql|SQLite substrate]]
- Result ↔ [[08_ARCADIA_V0_1_RECOVERY_TRACE_PRIVACY|PublicationJournal / trace boundary]]
