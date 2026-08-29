---
title: "A.R.C.A.D.I.A. R3 — Independent Stress Resolution Ledger"
project: "A.R.C.A.D.I.A."
version: "0.1-prototype"
checkpoint_date: "2026-08-29"
document_role: "provenance"
source_path: "provenance/ARCADIA_R3_STRESS_RESOLUTION_LEDGER_2026-08-28.md"
source_sha256: "de482e4b53a2e68ac79ab0c8f9a3f934b7be7c6e1a65ffadb706a4f3d32a7351"
source_bytes: 4566
source_integrity: "preserved"
tags:
  - "arcadia/v0-1"
  - "type/provenance"
aliases:
  - "ARCADIA_R3_STRESS_RESOLUTION_LEDGER_2026-08-28.md"
  - "A.R.C.A.D.I.A. R3 — Independent Stress Resolution Ledger"
---

> [!info] Obsidian navigation
> **Checkpoint role:** `provenance`  
> **Frozen source:** `provenance/ARCADIA_R3_STRESS_RESOLUTION_LEDGER_2026-08-28.md` · SHA-256 `de482e4b53a2e68a…`  
> **Command center:** [[ARCADIA v0.1 - Command Center]]  
> **Connected:** [[ARCADIA_R3_INDEPENDENT_STRESS_TEST_2026-08-29]] · [[10_ARCADIA_V0_1_R3_TO_V0_1_CHANGELOG]] · [[ARCADIA_PERF01_DETERMINISTIC_FAST_PATH_LOCK_2026-08-29]] · [[ARCADIA_ST01_AAE_CALL_DATA_LOCK_2026-08-28]] · [[ARCADIA_ST03_TRANSACTIONAL_HOT_SWAP_LOCK_2026-08-28]] · [[ARCADIA_ST04_ATOMIC_ADAPTER_LEASE_LOCK_2026-08-28]] · [[ARCADIA_ST05_RUNTIME_HEALTH_POISON_LOCK_2026-08-29]] · [[ARCADIA_ST06_INFERENCE_PROFILE_QUALIFICATION_LOCK_2026-08-29]] · [[ARCADIA_ST07_AAE_SERIALIZATION_INJECTION_LOCK_2026-08-29]] · [[ARCADIA_ST08_SOURCE_QUALITY_POLICY_LOCK_2026-08-29]] · [[ARCADIA_ST09_CRASH_REPLAY_OUTCOME_LOCK_2026-08-29]] · [[ARCADIA_ST10_TRACE_PRIVACY_TRAINING_FIREWALL_LOCK_2026-08-29]]

<!-- OBSIDIAN_LAYER_END — ORIGINAL SOURCE CONTENT BEGINS BELOW -->

# A.R.C.A.D.I.A. R3 — Independent Stress Resolution Ledger

**Started:** 2026-08-28  
**Rule:** march one stress item at a time; do not mark later items closed implicitly.

| Item | Severity | State | Locked resolution |
|---|---|---|---|
| ST-01 | Critical | **CLOSED — design + boundary prototype** | Host structured object -> strict schema -> Canonical JSON V1 -> final rendered CALL_DATA strict reparse + same schema -> dispatch. Exact malformed Slice-4 path patch recorded. |
| ST-02 | Low | OPEN | Not worked in this march yet. |
| ST-03 | Critical | **CLOSED — design lock** | Transactional load-before-commit STAGING handle; failed load preserves committed HOT set; measured swap headroom required; uncertain cleanup routes to ST-05. |
| ST-04 | Critical | **CLOSED — design lock** | `ensure_hot_and_acquire()` is sole call-facing learned acquisition; serialized manager mutation; lease UUID + handle generation + process epoch; linear release; reject stale/double release. |
| ST-05 | Critical | **CLOSED — design lock** | Residency is separate from HEALTHY/QUARANTINED/POISONED mechanical health; model/qualification failures do not alter health; poison is runtime-domain scoped and terminal for the epoch; controlled restart required. |
| ST-06 | Critical boundary | **CLOSED — design lock** | Immutable per-specialist/per-mode `InferenceProfile`; Canonical JSON hash joins qualification identity; fresh context + fresh sampler every attempt; deterministic qualification seed policy; profile changes require requalification. |
| ST-07 | Critical boundary | **CLOSED — design lock** | Structured authority/data planes; one versioned AAE Contract Registry + Canonical AAE Serializer shared by training/runtime; origin/trust labels + field caps + adversarial injection qualification; bracketed human-readable AAE retained as deterministic observability rendering, never runtime authority. |
| ST-08 | Critical boundary | **CLOSED — design lock** | Claim-relative `SourcePolicyRegistry`; full provenance + freshness/directness/independence metadata; deterministic evidence preprocessing; no universal trust score; `latest/current` cannot be unconditional SATISFIED without policy gate. |
| ST-09 | Critical boundary | **CLOSED — design lock** | Durable OperationJournal before side-effect boundary; per-capability idempotency/recovery policy; atomic local terminal receipt writes; restart verify/safe-replay/OUTCOME_UNKNOWN only; models cannot invent side-effect outcomes. |
| ST-10 | Production blocker | **CLOSED — design lock** | Full-turn/cross-turn trace policy; encrypted finite-retention Secure Raw Trace; durable content-light Trace Index; deterministic human rendering; candidate quarantine + explicit TRAINING_APPROVED firewall; held-out NEVER_TRAIN; deletion/lineage rules. |

## ST-01 artifacts

- `ARCADIA_ST01_AAE_CALL_DATA_LOCK_2026-08-28.md`
- `ARCADIA_ST01_R3_TRACE_PATCH.diff`
- `arcadia_aae_boundary.py`
- `test_arcadia_aae_boundary.py`
- `arcadia_r3_static_stress_check.py` (existing independent checker; parses actual AAE CALL_DATA)

## ST-03 / ST-04 artifacts

- `ARCADIA_ST03_TRANSACTIONAL_HOT_SWAP_LOCK_2026-08-28.md`
- `ARCADIA_ST04_ATOMIC_ADAPTER_LEASE_LOCK_2026-08-28.md`

## ST-05 artifacts

- `ARCADIA_ST05_RUNTIME_HEALTH_POISON_LOCK_2026-08-29.md`

## ST-06 artifacts

- `ARCADIA_ST06_INFERENCE_PROFILE_QUALIFICATION_LOCK_2026-08-29.md`

## ST-07 artifacts

- `ARCADIA_ST07_AAE_SERIALIZATION_INJECTION_LOCK_2026-08-29.md`

## ST-08 artifacts

- `ARCADIA_ST08_SOURCE_QUALITY_POLICY_LOCK_2026-08-29.md`

## ST-09 artifacts

- `ARCADIA_ST09_CRASH_REPLAY_OUTCOME_LOCK_2026-08-29.md`


## ST-10 artifacts

- `ARCADIA_ST10_TRACE_PRIVACY_TRAINING_FIREWALL_LOCK_2026-08-29.md`

## PERF-01 / Product-level call amplification

**State:** **CLOSED — design lock**

Locked resolution:

- allowlisted `DeterministicPathGate` for syntactically provable work;
- deterministic paths retain normal host-owned artifact lineage and human-readable audit rendering;
- `fast_path_enabled` is an explicit host-owned per-turn-snapshotted runtime toggle;
- OFF forces the ordinary learned-eligible Recipe path for testing or normal use but never disables host-only safety/authority rules;
- optional would-have-matched telemetry may observe eligibility while disabled without affecting routing;
- no specialist/recipe authority collapse merely for latency;
- end-to-end path-class telemetry and p50/p95 budgets are set from pinned real-runtime measurements.

Artifact:

- `ARCADIA_PERF01_DETERMINISTIC_FAST_PATH_LOCK_2026-08-29.md`
