---
title: "A.R.C.A.D.I.A. v0.1 — Prototype Build Docs"
project: "A.R.C.A.D.I.A."
version: "0.1-prototype"
checkpoint_date: "2026-08-29"
document_role: "canonical-system-document"
source_path: "00_README_FIRST.md"
source_sha256: "72f15887b5281490bee276af895575c401ea19b46a5e9da978cb9c19657daf0b"
source_bytes: 4469
source_integrity: "preserved"
tags:
  - "arcadia/v0-1"
  - "type/system"
  - "status/frozen"
aliases:
  - "00_README_FIRST.md"
  - "A.R.C.A.D.I.A. v0.1 — Prototype Build Docs"
---

> [!info] Obsidian navigation
> **Checkpoint role:** `canonical-system-document`  
> **Frozen source:** `00_README_FIRST.md` · SHA-256 `72f15887b5281490…`  
> **Command center:** [[ARCADIA v0.1 - Command Center]]  
> **Connected:** [[01_ARCADIA_V0_1_FULL_PROJECT_CHECKPOINT]] · [[02_ARCADIA_V0_1_EXACT_BUILD_ORDER]] · [[03_ARCADIA_V0_1_GLOBAL_CONTRACTS_AND_INVARIANTS]] · [[04_ARCADIA_V0_1_AAE_CONTRACT_REGISTRY_AND_SERIALIZATION]] · [[05_ARCADIA_V0_1_MODEL_RUNTIME_ADAPTER_MANAGER]] · [[06_ARCADIA_V0_1_QUALIFICATION_AND_STRESS_GATES]] · [[07_ARCADIA_V0_1_SOURCE_POLICY_REGISTRY]] · [[08_ARCADIA_V0_1_RECOVERY_TRACE_PRIVACY]] · [[09_ARCADIA_V0_1_PERFORMANCE_FAST_PATH]] · [[10_ARCADIA_V0_1_R3_TO_V0_1_CHANGELOG]] · [[ARCADIA_V0_1_MASTER_BUILD_AUTHORITY]] · [[ARCADIA_V0_1_DOCUMENT_VALIDATION_REPORT.txt]]

<!-- OBSIDIAN_LAYER_END — ORIGINAL SOURCE CONTENT BEGINS BELOW -->

# A.R.C.A.D.I.A. v0.1 — Prototype Build Docs
## Final design checkpoint after R3 independent stress resolution

**Project:** A.R.C.A.D.I.A. — Adaptive Runtime for Compartmentalized Agents, Decisions, Interaction & Automation  
**Version:** `0.1-prototype`  
**Checkpoint date:** 2026-08-29  
**Status:** **DESIGN FROZEN FOR IMPLEMENTATION / RUNTIME NOT YET QUALIFIED**  
**Authority:** This bundle is the canonical build authority for the v0.1 prototype.

## Read this first

The previous R3 documentation proved that the nine-recipe semantic spine was coherent, then an independent stress review found several runtime, AAE, source-quality, recovery, privacy, and performance gaps. Those gaps have now been turned into explicit v0.1 contracts.

This bundle therefore does **not** mean “the runtime has passed.” It means:

```text
architecture frozen
known R3 contradictions removed
test gates defined
implementation order frozen
runtime qualification still must be earned on the pinned GGUF/LoRA stack
```

The independent stress verdict was a conditional GO for a narrow runtime spike, not a blanket production validation. v0.1 preserves that discipline.

## Canonical reading order

1. `01_ARCADIA_V0_1_FULL_PROJECT_CHECKPOINT.md` — system authority and final invariants.
2. `02_ARCADIA_V0_1_EXACT_BUILD_ORDER.md` — build sequence from empty branch to v0.1 demo.
3. `03_ARCADIA_V0_1_GLOBAL_CONTRACTS_AND_INVARIANTS.md` — cross-cutting rules.
4. `04_ARCADIA_V0_1_AAE_CONTRACT_REGISTRY_AND_SERIALIZATION.md` — learned-call boundary.
5. `05_ARCADIA_V0_1_MODEL_RUNTIME_ADAPTER_MANAGER.md` — libllama/adapter runtime.
6. `06_ARCADIA_V0_1_QUALIFICATION_AND_STRESS_GATES.md` — tests, T0–T6, real-spike gates.
7. `07_ARCADIA_V0_1_SOURCE_POLICY_REGISTRY.md` — evidence authority/freshness policy.
8. `08_ARCADIA_V0_1_RECOVERY_TRACE_PRIVACY.md` — crash/replay, OUTCOME_UNKNOWN, trace firewall.
9. `09_ARCADIA_V0_1_PERFORMANCE_FAST_PATH.md` — deterministic elision and toggle.
10. `recipes/` — full Recipe 0–8 semantic build contracts.
11. `storage/` — semantic-memory SQLite substrate.
12. `reference/` — five-slice human-readable trace and stress record.
13. `provenance/` — individual resolution locks that led to this consolidation.

## Supersession rule

When documents disagree, use this order:

```text
v0.1 system documents (01–09)
    > v0.1 recipe wrappers / carried-forward semantic bodies
    > R3 checkpoint/runtime wording
    > R2 checkpoint/recipe wording
    > historical patch notes / draft examples
```

The long recipe bodies are deliberately retained because they contain detailed edge cases and tests. Their semantic ownership remains current unless a v0.1 system contract explicitly supersedes a runtime/cross-cutting detail.

## Core prototype spine

```text
0 Conversation Resolver
1 Intent
2 Context
3 Decision
4 Tool / Execution
5 Reconciliation
6 Persistence
7 Completion
8 Result
```

No recipe is collapsed in v0.1.

## Core learned roster

Fifteen physical LoRA adapters remain the core roster. Tool / Execution is host-only. One physical adapter may expose multiple independently qualified logical modes.

## Important v0.1 changes from R3

- Strict production-equivalent `CALL_DATA` validation on the final rendered call.
- AAE Contract Registry + canonical machine serialization + deterministic human-readable audit rendering.
- Transactional load-before-evict adapter replacement using temporary STAGING.
- Atomic `ensure_hot_and_acquire()` leases with process epoch and handle generation.
- Runtime health axis: `HEALTHY | QUARANTINED | POISONED` separate from residency.
- Per-specialist/per-mode immutable `InferenceProfile` and fresh sampler per attempt.
- Claim-specific `SourcePolicyRegistry`; `latest/current` cannot be strongly satisfied without freshness/authority evidence.
- Durable operation journal and explicit `OUTCOME_UNKNOWN` after uncertain side effects.
- Tiered encrypted raw traces and a physically/logically separate training-approval firewall.
- Deterministic fast-path / model-necessity elision with an explicit runtime toggle.
- R3 count correction: five slices contain **87 actual learned calls**; the 88th balanced AAE pair is the syntax template.

## Final checkpoint statement

> Build the host truth system first. Build the runtime boundary second. Prove it with test doubles and a real pinned GGUF spike. Only then spend training effort across the full specialist roster.
