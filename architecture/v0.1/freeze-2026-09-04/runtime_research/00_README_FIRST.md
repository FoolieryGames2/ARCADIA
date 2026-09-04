# A.R.C.A.D.I.A. — Runtime / Base-Model Research Bundle

**Date:** 2026-09-03  
**Status:** BUILD-RETURN CHECKPOINT / RUNTIME QUALIFICATION STILL REQUIRED

## Purpose

This bundle captures the decisions and evidence needed to return A.R.C.A.D.I.A. to implementation without reopening the adapter-runtime architecture from intuition.

It records:

1. the locked v0.1 base-model family;
2. the corrected project terminology around A.R.C.A.D.I.A., the base model, specialist adapters, and Howard;
3. the independent R3 stress-test results and the current resolution status of ST-01 through ST-10;
4. the existing runtime test architecture for adapter residency, activation, isolation, failure, memory, and performance;
5. the new research question around **all adapters loaded/inactive versus bounded HOT-pool swapping**;
6. the exact conditions under which implementation may proceed without pretending runtime qualification is already earned.

## Current project decision

> **A.R.C.A.D.I.A. v0.1 starts with `Qwen/Qwen3-4B-Instruct-2507` as the pinned foundation/base checkpoint family.**

The model family is locked for the starting implementation and specialist-adapter program. The exact deployment quantization, llama.cpp commit, CUDA/build options, context size, sampler profile, and adapter-residency policy remain qualification variables and must be pinned by the runtime gates.

## Return-to-build verdict

**GO — return to build.**

The original independent stress test found real architectural defects, but the current master build authority contains explicit design resolutions for the critical findings: strict CALL_DATA serialization, atomic adapter acquisition, STAGING load-before-commit replacement, runtime health/POISONED state, complete inference identity, injection-safe AAE structure, claim-specific SourcePolicy, crash/replay OperationJournal semantics, trace/privacy separation, and deterministic model-call elision.

What remains is implementation and proof, especially Phase A2/A3 runtime qualification. It is not a reason to reopen the architecture again before coding.

## Read order

1. `01_BASE_MODEL_LOCK_QWEN3_4B_INSTRUCT_2507.md`
2. `02_TERMINOLOGY_LOCK_ARCADIA_BASE_HOWARD.md`
3. `03_STRESS_TEST_RESULTS_AND_RESOLUTION_MAP.md`
4. `04_ADAPTER_RUNTIME_RESEARCH_AND_TEST_PLAN.md`
5. `05_BUILD_RETURN_CHECKLIST.md`
6. `06_EXPERIMENT_RESULT_TEMPLATE.md`
7. `07_SOURCE_INDEX.md`

## Source boundary

Project-derived statements in this bundle are grounded in the supplied A.R.C.A.D.I.A. files, especially:

- `ARCADIA_R3_INDEPENDENT_STRESS_TEST_2026-08-29.md`
- `ARCADIA_V0_1_MASTER_BUILD_AUTHORITY.md`
- `ARCADIA_ADAPTER_RUNTIME_MANAGER_PROTOTYPE_BUILD_SPEC_R3_2026-08-28.md`
- `ARCADIA_ADAPTER_RUNTIME_MANAGER_EXACT_BUILD_ORDER_R3_2026-08-28.md`
- `ARCADIA_R3_ADAPTER_RUNTIME_INTEGRATION_CHANGELOG_2026-08-28.md`
- current A1 stress-hardening/status artifacts supplied on 2026-09-03

Current external facts about Qwen3 and llama.cpp were rechecked against official sources on 2026-09-03. See `07_SOURCE_INDEX.md`.
