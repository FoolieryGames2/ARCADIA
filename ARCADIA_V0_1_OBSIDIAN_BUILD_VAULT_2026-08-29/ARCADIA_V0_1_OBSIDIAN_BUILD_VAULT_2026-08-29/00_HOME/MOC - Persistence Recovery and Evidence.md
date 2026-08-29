---
title: "MOC — Persistence, Recovery, and Evidence"
project: "A.R.C.A.D.I.A."
version: "0.1-prototype"
generated_navigation: true
tags:
  - "arcadia/v0-1"
  - "moc/persistence"
---

# MOC — Persistence, Recovery, and Evidence

## Durable truth boundary

```mermaid
flowchart LR
    D[Decision obligations] --> E[Execution receipts]
    E --> R[Reconciliation meaning]
    R --> P[Persistence semantic commit]
    P --> C[Completion standing]
    C --> O[Result publication]
```

## Canonical specs

- [[07_ARCADIA_V0_1_SOURCE_POLICY_REGISTRY|SourcePolicyRegistry]]
- [[08_ARCADIA_V0_1_RECOVERY_TRACE_PRIVACY|Recovery, Trace Privacy, Training Firewall]]
- [[R4_TOOL_EXECUTION_V0_1|Recipe 4 — Tool / Execution]]
- [[R5_RECONCILIATION_V0_1|Recipe 5 — Reconciliation]]
- [[R6_PERSISTENCE_V0_1|Recipe 6 — Persistence]]
- [[R7_COMPLETION_V0_1|Recipe 7 — Completion]]
- [[R8_RESULT_V0_1|Recipe 8 — Result]]
- [[ARCADIA_PERSISTENCE_SQLITE_SCHEMA_V0_1.sql|Persistence SQLite schema]]

## Locks

- [[ARCADIA_ST08_SOURCE_QUALITY_POLICY_LOCK_2026-08-29|ST08 — Source quality policy]]
- [[ARCADIA_ST09_CRASH_REPLAY_OUTCOME_LOCK_2026-08-29|ST09 — Crash/replay + OUTCOME_UNKNOWN]]
- [[ARCADIA_ST10_TRACE_PRIVACY_TRAINING_FIREWALL_LOCK_2026-08-29|ST10 — Trace/privacy/training firewall]]
