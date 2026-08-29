---
title: "A.R.C.A.D.I.A. v0.1 — R3 to v0.1 Consolidation Changelog"
project: "A.R.C.A.D.I.A."
version: "0.1-prototype"
checkpoint_date: "2026-08-29"
document_role: "canonical-system-document"
source_path: "10_ARCADIA_V0_1_R3_TO_V0_1_CHANGELOG.md"
source_sha256: "4bef24c96db0c9614cae37b181fd96cf4b9b5e3045819378b805e3b6cbf35684"
source_bytes: 3949
source_integrity: "preserved"
tags:
  - "arcadia/v0-1"
  - "type/system"
  - "status/frozen"
aliases:
  - "10_ARCADIA_V0_1_R3_TO_V0_1_CHANGELOG.md"
  - "A.R.C.A.D.I.A. v0.1 — R3 to v0.1 Consolidation Changelog"
---

> [!info] Obsidian navigation
> **Checkpoint role:** `canonical-system-document`  
> **Frozen source:** `10_ARCADIA_V0_1_R3_TO_V0_1_CHANGELOG.md` · SHA-256 `4bef24c96db0c961…`  
> **Command center:** [[ARCADIA v0.1 - Command Center]]  
> **Connected:** [[01_ARCADIA_V0_1_FULL_PROJECT_CHECKPOINT]] · [[ARCADIA_R3_STRESS_RESOLUTION_LEDGER_2026-08-28]] · [[CONSOLIDATION_NOTES]] · [[00_README_FIRST]]

<!-- OBSIDIAN_LAYER_END — ORIGINAL SOURCE CONTENT BEGINS BELOW -->

# A.R.C.A.D.I.A. v0.1 — R3 to v0.1 Consolidation Changelog

**Date:** 2026-08-29  
**Purpose:** record the known R3 defects/gaps that were closed or converted into explicit implementation gates before the v0.1 build checkpoint.

## Corrected bookkeeping

- Historical five-slice trace: 88 balanced AAE envelope pairs = 1 syntax template + **87 actual learned calls**.
- The malformed Slice-4 Windows path in actual `CALL_DATA` is corrected in the v0.1 reference trace and guarded by the production-equivalent parser tests.

## Runtime changes

- Eviction-first full-pool replacement superseded by temporary STAGING + load-before-commit.
- `ensure_hot()` + `acquire()` split call-facing interface superseded by atomic `ensure_hot_and_acquire()`.
- Leases now carry process epoch, handle generation, lease UUID, and linear one-time release semantics.
- Runtime health is separate from residency: `HEALTHY | QUARANTINED | POISONED`.
- POISONED requires controlled restart/new epoch; poor model output does not poison runtime.
- Hard versus soft protection is explicit. Soft predictive protection expires/carries generation and may be overridden by newer demand; leases/hard pins may not.
- Full qualification identity now includes `inference_profile_hash` and fresh sampler state.

## AAE / model boundary changes

- Runtime `CALL_DATA` originates as a structured host object; schema-less/handwritten JSON dispatch forbidden.
- Final rendered packet is reparsed/revalidated before inference.
- AAE becomes a structured Authority Plane + Data Plane contract generated from one registry.
- Human-readable bracketed AAE remains mandatory as a deterministic audit rendering, not the parser protocol.
- Training and runtime prompts come from the same AAE Contract Registry.
- Untrusted user/transcript/memory/tool/web text is origin/trust labeled, bounded, and adversarially tested for instruction impersonation.

## Evidence changes

- Source quality is no longer left as an open lane.
- `SourcePolicyRegistry` uses claim-specific source relationship/directness/freshness/independence/conflict rules rather than a universal site score.
- Freshness-sensitive claims cannot become unconditionally SATISFIED without policy-complete evidence.

## Recovery changes

- Side effects use a durable OperationJournal and capability-specific replay class.
- `OUTCOME_UNKNOWN` is a first-class truth state after uncertain crash/network/timeout outcomes.
- Semantic Persistence success receipt is tied to the semantic SQLite transaction boundary.
- Result publication/transcript recovery uses immutable result identity rather than rerunning the semantic pipeline.

## Trace/training changes

- Full-system trace scope explicitly covers all recipes, re-entry, repair, tools/evidence, Persistence, Completion, Result/publication, and cross-turn lineage.
- Trace storage is tiered: index, secure raw, candidate quarantine, training-approved.
- Raw traces are sensitive, encrypted/owner-controlled, finite-retention by default.
- Training consumes explicit approved manifests only; held-out fixtures are permanently `NEVER_TRAIN`.

## Performance changes

- DeterministicPathGate and per-recipe model-necessity elision may remove provably unnecessary learned calls while preserving artifact lineage.
- Fast path is a first-class toggle, snapshotted at turn start, valid OFF for testing or normal use.
- Performance is budgeted/measured by path class with end-to-end p50/p95, call, repair, adapter, and token telemetry.
- No specialist boundaries are merged merely for speed in v0.1.

## Static consolidation evidence

- v0.1 five-slice reference strict checker: PASS, 87 actual calls, all actual CALL_DATA objects parse.
- ST-01 shared boundary unit suite: 12/12 PASS.
- v0.1 documentation lock-presence validation: PASS.

These are static/documentation/prototype-boundary checks. Real pinned GGUF/LoRA runtime qualification remains Phase A3 and later trust progression.
