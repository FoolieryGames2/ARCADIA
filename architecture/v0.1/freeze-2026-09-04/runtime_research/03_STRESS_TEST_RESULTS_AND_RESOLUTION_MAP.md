# A.R.C.A.D.I.A. — Independent Stress Test Results and Resolution Map

**Stress test source:** `ARCADIA_R3_INDEPENDENT_STRESS_TEST_2026-08-29.md`  
**Current resolution authority:** `ARCADIA_V0_1_MASTER_BUILD_AUTHORITY.md` and later A1 hardening artifacts  
**Review date:** 2026-09-03

## Original verdict

The independent R3 stress test issued:

```text
CONDITIONAL GO for a narrow runtime spike
NO-GO for full pipeline implementation, qualification, or training-data generation yet
```

It explicitly judged the core ownership architecture worth continuing, while warning that documentation/static validation was not runtime proof.

## What the stress test said was already good

The report accepted these core directions:

- semantic recipe ownership remains separate from physical adapter residency;
- recipes do not choose LoRA paths or manage adapter lifetime;
- base-model compatibility is a hard gate;
- adapter activation receipts are distinct from external Execution receipts;
- fresh contexts and lease-before-bind/release-after-destroy are the right default direction;
- the five-HOT ceiling is a measured runtime policy, not a semantic limit;
- host authority remains over IDs, tools, transactions, and publication;
- deterministic stages are allowed to omit model calls.

## Stress baseline — call amplification and adapter churn

The independent checker found **87 actual learned calls** across the five slices, not 88; one balanced envelope was a syntax template.

| Slice | Task | Learned calls | Distinct adapters | Cold strict-LRU loads at max_hot=5 | Evictions |
|---|---|---:|---:|---:|---:|
| 1 | exact `Ready.` | 13 | 10 | 10 | 5 |
| 2 | repeat prior line | 14 | 10 | 10 | 5 |
| 3 | research + remember | 27 | 15 | 18 | 13 |
| 4 | exact file-save attempt | 13 | 10 | 10 | 5 |
| 5 | research + ambiguous save | 20 | 13 | 14 | 9 |

The stress report identified this as the largest prototype viability risk. The later master build authority responded with deterministic fast paths / model-necessity elision and per-path end-to-end telemetry.

## ST-01 through ST-10 resolution map

| ID | Original finding | Current architecture status | Build proof still required |
|---|---|---|---|
| ST-01 | malformed exact CALL_DATA / validation missed model-path JSON | **DESIGN CLOSED** — structured host object, strict schema, Canonical JSON V1, final pre-dispatch reparse/revalidation | Keep regression; prove production dispatcher uses same gate |
| ST-02 | 88 envelope count included syntax template | **CLOSED** — canonical historical count is 87 actual learned calls | None beyond preserving corrected fixture counts |
| ST-03 | evict-first load failure could not preserve old HOT set | **DESIGN CLOSED** — STAGING / load-before-commit; old committed HOT set remains until replacement is live | A2 forced staging failure; A3 full-pool real failure injection |
| ST-04 | separate ensure_hot + acquire race | **DESIGN CLOSED** — sole call-facing `ensure_hot_and_acquire()` with synchronized lease identity | A2 race tests, stale/double release tests |
| ST-05 | residency states could not express uncertain cleanup | **DESIGN CLOSED** — separate `HEALTHY / QUARANTINED / POISONED` axis; controlled epoch restart | A2 poison-state tests; A3 uncertain cleanup injection |
| ST-06 | qualification identity omitted inference settings | **DESIGN CLOSED** — immutable `inference_profile_hash`; fresh sampler per attempt | Measure/freeze real profiles; qualification is per exact identity |
| ST-07 | AAE text envelope lacked injection-safe serialization boundary | **DESIGN CLOSED / A1 IMPLEMENTATION IN PROGRESS** — authority/data planes, structured messages, canonical serializer, audit rendering only | Finish registry-wide A1 proof and adversarial fixtures |
| ST-08 | source-quality/evidence authority unresolved for latest/current claims | **DESIGN CLOSED** — claim-specific `SourcePolicyRegistry`, freshness/provenance/conflict rules | Implement and test in Reconciliation/Context evidence path |
| ST-09 | crash/replay semantics missing for side effects | **DESIGN CLOSED** — durable `OperationJournal`, recovery classes, `OUTCOME_UNKNOWN` | Implement Recipe 4 host path and restart/failure tests |
| ST-10 | full-trace privacy / retention / training firewall missing | **DESIGN CLOSED** — trace tiers, secure raw trace, quarantine, TRAINING_APPROVED separation, NEVER_TRAIN held-outs | Implement storage/retention/deletion/export gates before persistent full traces are trusted |

## Additional stress resolution — deterministic elision

The master build authority now locks:

> A recipe does not deserve a model call merely because the recipe exists.

The D0 exact-literal fast path is the first allowlisted proof rule. Each recipe may also skip a learned call when the host can completely and syntactically derive the authoritative artifact from validated inputs.

This directly answers the stress report's `13 learned calls to reproduce Ready.` example without collapsing semantic ownership boundaries.

## A1 status after later hardening

Later Recipe-1 stress hardening reports:

```text
focused Recipe-1 contract suite: 69 passed
external deterministic repository subset: 572 passed
source compilation: PASS
retained reference envelopes: 1 template + 87 actual slice calls
```

Residual Recipe-1 risks are correctly classified as qualification/runtime work rather than falsely claimed as deterministic proof, including semantic spelling correctness, free-text semantic faithfulness, runtime accepted-artifact identity, and the canonical Python 3.12 Windows gate.

## Important remaining implementation gates — not architecture blockers

Before learned runtime authority can rise above T0:

1. Finish/close the A1 registry-wide contract and serializer gate.
2. Run canonical Windows CPython 3.12 `check.bat`; Python 3.13 stress runs are intentionally non-canonical.
3. Build A2 AdapterManager/ModelRuntime/SpecialistInvoker with test doubles.
4. Run A3 with the pinned Qwen3-4B base and real LoRA fixtures.
5. Pin the exact llama.cpp commit/build and exact model/quantization hashes.
6. Measure safe residency policy instead of assuming five HOT or assuming all-resident.
7. Run A/B/A isolation with fresh context **and fresh sampler**.
8. Run memory soak, load-failure, leased/pinned exhaustion, and poisoned-restart tests.
9. Measure end-to-end latency/call/repair/adapter-transition distributions by path class.

## Bottom line

No original stress-test item requires a new pre-build architecture redesign at this checkpoint.

The correct move is:

```text
RETURN TO BUILD
but keep runtime authority at T0 until A1/A2/A3 gates actually pass
```
