---
title: "A.R.C.A.D.I.A. R3 — Independent Prototype Stress Test"
project: "A.R.C.A.D.I.A."
version: "0.1-prototype"
checkpoint_date: "2026-08-29"
document_role: "reference"
source_path: "reference/ARCADIA_R3_INDEPENDENT_STRESS_TEST_2026-08-29.md"
source_sha256: "15f5f1de4ed4e18734e377e5cca347615388a8090ebe2e1dc19d032617b244c8"
source_bytes: 16172
source_integrity: "preserved"
tags:
  - "arcadia/v0-1"
  - "type/reference"
aliases:
  - "ARCADIA_R3_INDEPENDENT_STRESS_TEST_2026-08-29.md"
  - "A.R.C.A.D.I.A. R3 — Independent Prototype Stress Test"
---

> [!info] Obsidian navigation
> **Checkpoint role:** `reference`  
> **Frozen source:** `reference/ARCADIA_R3_INDEPENDENT_STRESS_TEST_2026-08-29.md` · SHA-256 `15f5f1de4ed4e187…`  
> **Command center:** [[ARCADIA v0.1 - Command Center]]  
> **Connected:** [[06_ARCADIA_V0_1_QUALIFICATION_AND_STRESS_GATES]] · [[ARCADIA_R3_STRESS_RESOLUTION_LEDGER_2026-08-28]]

<!-- OBSIDIAN_LAYER_END — ORIGINAL SOURCE CONTENT BEGINS BELOW -->

# A.R.C.A.D.I.A. R3 — Independent Prototype Stress Test

**Date:** 2026-08-29  
**Evidence boundary:** workstation copies supplied for this review only  
**External memory/web used:** none  
**Verdict:** **CONDITIONAL GO for a narrow runtime spike; NO-GO for full pipeline implementation, qualification, or training-data generation yet.**

## 1. Executive judgment

The central design decision is good: Recipes request logical capabilities; `SpecialistInvoker` owns learned-call construction; `AdapterManager` owns physical LoRA lifetime; `ModelRuntime` owns libllama mechanics; learned outputs remain proposals until host validation. The distinction between COLD/READY/HOT and per-call ACTIVE is also clean and useful.

The bundle is not implementation-safe yet. The static validation report proves document shape and the presence of declared invariants; it does not prove runtime behavior. The supplied files contain no runtime source, compiled llama.cpp build, model/adapter fixtures, test logs, failure-injection output, or memory telemetry. Several contradictions and untested boundaries remain, and one purported exact model call is already malformed.

My strongest recommendation is to patch the runtime/AAE contracts first, then build only the Phase-A2 runtime spike. Do not begin large JSONL generation from this trace and do not build all Recipes 0–8 on top of it yet.

## 2. Intake and reproducibility

Five unique workstation files were readable:

| File | SHA-256 |
|---|---|
| `ARCADIA_R3_VALIDATION_REPORT_2026-08-28.txt` | `ceda2bbd8c7b1b35fe02dd07f21279719b2b65d9b8dc773337eae7a918911353` |
| `ARCADIA_FULL_PIPELINE_JOB_TRACE_AAE_DRAFT_R3_5_SLICES_2026-08-28.md` | `c7c7c294bea67bdb53c1286690b59f0b4d7c6b77a22a4446695279aad25b5e53` |
| `ARCADIA_R3_ADAPTER_RUNTIME_INTEGRATION_CHANGELOG_2026-08-28.md` | `8c4d0d0accf0869959444873149f78ba3bf4bb0f5ed094e56620cdf0635685cd` |
| `ARCADIA_ADAPTER_RUNTIME_MANAGER_EXACT_BUILD_ORDER_R3_2026-08-28.md` | `cc3f3a66d46a69444a4434ec3465229f0ae00834ee09ab3150dd47207995d422` |
| `ARCADIA_ADAPTER_RUNTIME_MANAGER_PROTOTYPE_BUILD_SPEC_R3_2026-08-28.md` | `0dc25acc848139d49188ea63ac75e37c48286d30776c530e7256b737b2c78fc0` |

Two attachment identifiers were supplied for the same changelog name/path. Only one workstation copy exists, so the second attachment could not be compared without leaving the user-defined evidence boundary.

The trace declares eight canonical Recipe specifications, an R3 checkpoint, and an R2 SQLite schema as dependencies, but those files were not supplied. Claims that depend on them remain unverified in this review.

A reproducible checker was created as `arcadia_r3_static_stress_check.py`. It performs strict JSON parsing, including JSON embedded in AAE `CALL_DATA`, and reports per-slice call/adapter churn.

## 3. What passed

- The architecture keeps semantic ownership separate from physical adapter residency.
- Recipes are prohibited from choosing LoRA paths or managing adapter lifetime.
- Base-model hash compatibility is a hard gate.
- Adapter activation receipts are correctly distinguished from execution receipts.
- Fresh contexts and lease-before-bind/release-after-destroy are the correct default direction.
- The five-HOT ceiling is treated as a measured runtime policy, not a semantic limit.
- The trace preserves missing evidence, conflicts, partial satisfaction, BLOCKED versus FAILED, and host authority over tools, IDs, transactions, and publication.
- A model is deliberately omitted from deterministic stages instead of being invoked for symmetry.
- All 110 explicitly fenced JSON examples in the supplied trace parse under strict JSON with no duplicate keys.
- All 15 physical specialist adapters appear in Slice 3.

## 4. Verified defects

### ST-01 — One exact `CALL_DATA` packet is invalid JSON — Critical

The Result-comment call in Slice 4 contains:

```json
"protected_literals": ["C:\Arcadia\exports\status.txt"]
```

As written in the source, the backslashes are single, so `\A` is an invalid JSON escape. The exact source is line 7388 of the supplied pipeline trace. It must be:

```json
"protected_literals": ["C:\\Arcadia\\exports\\status.txt"]
```

The existing validation report parsed fenced JSON examples, not JSON embedded inside the text-fenced AAE calls. It therefore missed a payload on the actual model path.

**Required gate:** Parse every rendered `CALL_DATA` with the same strict runtime parser used in production. Reject duplicate keys, non-finite numbers, trailing content, unknown fields, wrong types, and values outside schema bounds.

### ST-02 — “88 learned-call envelopes” is off by one — Low

There are 88 opening and 88 closing tags, but one pair is the Section-3 syntax template. The five slices contain **87 actual learned calls**, not 88. The validation count is a balanced-tag check, not a learned-call count.

### ST-03 — Pool-full load failure cannot preserve the previous HOT pool — Critical

The canonical order says to evict first and then load the requested adapter. The lifecycle test simultaneously requires “load failure preserves previous HOT pool.” Both cannot be guaranteed under a hard five-object ceiling:

1. Evict victim V.
2. Load requested adapter N.
3. N fails to load.
4. V is no longer HOT.

The remaining four handles may be valid, but the previous pool was not preserved.

**Required decision:** Freeze one implementable policy:

- allow a measured temporary sixth staging handle, then evict only after the new load succeeds; or
- evict first but transactionally reload the victim on failure and report rollback failure separately; or
- weaken the invariant to “all non-evicted HOT handles remain valid and manager state remains consistent.”

Do not leave the current contradictory acceptance test in place.

### ST-04 — Atomic acquisition exists in pseudocode but not in the required interface — Critical

The required interface lists `ensure_hot(adapter_id)` and `acquire(adapter_id)` separately, while reference pseudocode calls `ensure_hot_and_acquire(...)`. With concurrency, a separate ensure/acquire sequence permits eviction between those operations.

**Required gate:** Make `ensure_hot_and_acquire` the sole call-facing atomic operation under manager synchronization. Return a lease carrying `adapter_id`, handle generation/process epoch, and lease UUID. Reject double release and stale-generation release.

### ST-05 — The failure state machine has no place for uncertainty — Critical

The only residency states are COLD/READY/HOT, but the failure vocabulary includes `ADAPTER_FREE_FAILED_OR_UNCERTAIN`. The documented `llama_adapter_lora_free` primitive returns `void`; normal code cannot interpret a nonzero free status. After an FFI fault, backend exception, or uncertain cleanup, marking the adapter READY may enable unsafe reuse while marking it HOT may lie about handle validity.

**Required gate:** Add runtime health states separate from residency, at minimum `HEALTHY | QUARANTINED | POISONED`. An uncertain free or corrupted backend poisons that residency domain, stops new calls, preserves forensic events, and requires controlled runtime restart. Do not pretend it is an ordinary typed free error.

## 5. Critical unproven boundaries

### ST-06 — Qualification identity is incomplete

The trust identity covers base/adapter/build/manager/invoker/AAE/schema/validator versions but omits output-affecting inference configuration. At minimum add an immutable `inference_profile_hash` covering:

- chat template and prompt serializer version;
- tokenizer identity/overrides;
- context parameters and token-budget policy;
- sampler chain, temperature, top-p/top-k/min-p, penalties, grammar, and seed policy;
- maximum output tokens and stop conditions;
- deterministic GPU/backend settings that qualification relies on.

Fresh KV does not imply reproducibility if sampler state or rendering configuration changes. A fresh sampler per attempt must also be explicit.

### ST-07 — The AAE has no frozen injection-safe serialization boundary

The trace places raw prompts, transcript text, memory, and tool evidence inside one textual envelope. No escaping/canonical serialization rule, message-role separation, delimiter-collision policy, or prompt-injection test exists. Untrusted content can imitate `[RESPONSE_CONTRACT]`, the closing AAE tag, or specialist instructions.

The host validator limits output shape, but shape validation alone cannot prevent semantically poisoned choices.

**Required gate:** Freeze the AAE Contract Registry before training, as the trace itself recommends. Generate training and runtime prompts from the same canonical serializer. Put stable authority instructions in the highest supported message role, encode data structurally, label origin/trust, cap every field, and adversarially test user/transcript/web content that impersonates instructions.

### ST-08 — Research cannot yet earn strong terminal claims

The validation report explicitly marks Source Quality / Evidence Authority unresolved. Slice 3 nevertheless demonstrates a fully satisfied “latest stable release” claim from receipt items that lack source URL/identity, retrieval time, query, publication/version date, content hash, or authority ranking. `DIRECT_SOURCE_EVIDENCE` is a label, not proof.

Until the source-quality lane is frozen, production research should not reach an unconditional SATISFIED state for “latest/current” claims. The receipt must preserve enough provenance for Reconciliation to compare freshness and authority.

### ST-09 — No crash/replay contract is supplied for the complete side-effect path

Slice 4 shows one idempotency key for `save_file`, and Slice 3 calls the SQLite write crash-safe, but the supplied files do not define the complete replay behavior for:

- process death before/after tool dispatch;
- side effect succeeds but receipt commit fails;
- receipt commits but publication fails;
- persistence transaction commits but `PRC` freezing fails;
- restart with an in-flight work item;
- retries after timeout where execution outcome is unknown.

Tool execution needs an operation journal and per-capability idempotency semantics. “Exactly once” cannot be assumed for external systems; the host should implement at-least-once dispatch with deduplication/verification where possible and explicit `OUTCOME_UNKNOWN` where it is not.

### ST-10 — Trace persistence has no supplied data-safety policy

The build order requires exact AAE, call data, raw model output, parsed output, repair attempts, and timings to be persisted for every learned call. That can include private prompts, transcript content, file paths, search results, and semantic memory. No supplied document defines redaction, encryption, access controls, retention, trace tiers, user deletion, or a training-export firewall implementation.

The changelog says a firewall is preserved, but its specification/evidence is absent. This is an evidence gap and a production blocker for persistent full traces.

## 6. Product-level stress: call amplification

The five slices contain this learned-call load:

| Slice | User task | Calls | Distinct physical adapters | Cold-start LRU loads (`max_hot=5`) | LRU evictions | Model-view characters across calls |
|---|---|---:|---:|---:|---:|---:|
| 1 | Reply exactly `Ready.` | 13 | 10 | 10 | 5 | 36,959 |
| 2 | Repeat one prior line | 14 | 10 | 10 | 5 | 38,055 |
| 3 | Research + remember | 27 | 15 | 18 | 13 | 80,747 |
| 4 | Attempt exact file save | 13 | 10 | 10 | 5 | 33,597 |
| 5 | Research + ambiguous save | 20 | 13 | 14 | 9 | 56,587 |

The load/eviction figures are a reproducible empty-pool, sequential strict-LRU simulation using the documented five-HOT policy. A warm workload and protect set will change the exact counts; they do not remove the call count or fresh-context cost.

This is the prototype's largest viability risk. A trivial exact response goes through 13 learned calls. If every call independently had 99% validated success, the chance that all 13 pass on the first attempt would be about **87.8%**; for 27 calls it would be about **76.2%**. At 99.5% per call those figures are about **93.7%** and **87.3%**. Repairs can improve completion but add more latency, context construction, and adapter churn.

**Required gate:** Define end-to-end p50/p95 latency, first-pass success, repair rate, and adapter-load budgets per turn—not only per-call telemetry. Add strict deterministic fast paths for syntactically provable cases such as `Reply with exactly: X`, while still generating host-owned artifacts needed for audit. Do not invoke 13 models to reproduce a literal the host already possesses.

## 7. Missing adversarial acceptance tests

Add these before declaring Phase A2 complete:

### Runtime lifecycle

- requested load fails while the pool is full;
- victim rollback also fails;
- duplicate lease release and stale lease after unload/reload;
- shutdown during load, context creation, inference, validation, repair, and trace write;
- all HOT adapters leased, all pinned, and all soft-protected;
- current demand overrides stale predictive protection without violating hard pins/leases;
- adapter file changes after READY and between validation/load;
- symlink/path substitution and approved-directory escape;
- OOM or telemetry unavailable while preserving room for context/inference peak;
- repeated A/B/A plus sampler reset, not only KV reset;
- process kill at every lifecycle transition;
- uncertain free poisons the runtime and forces controlled restart.

### AAE and schema

- user/tool/memory text contains AAE closing tags and fake response contracts;
- tool evidence says “ignore prior instructions”;
- duplicate JSON keys, extra properties, `NaN`, huge arrays/strings, wrong types;
- invented authoritative IDs, dangling refs, cyclic local refs, duplicate local keys;
- Unicode-confusable IDs and normalization mismatches;
- packet exceeds context budget—fail or deterministically project; never silently truncate;
- repair attempts have their own attempt UUID/receipt and a frozen aggregate cap.

### Side effects and recovery

- write partially succeeds and verification fails;
- destination already exists before a failed write;
- effect succeeds but receipt is lost;
- duplicate request after restart;
- stale semantic-memory base commit;
- persistence commit succeeds but response publication fails;
- external outcome cannot be determined and must remain `OUTCOME_UNKNOWN`.

## 8. Required patch order

1. Fix the invalid Slice-4 JSON and update validation to parse all 87 actual `CALL_DATA` objects.
2. Freeze the AAE Contract Registry, canonical serializer, strict schemas, injection tests, and aggregate repair/token budgets.
3. Replace separate `ensure_hot`/`acquire` with one atomic `ensure_hot_and_acquire`; add handle generation and linear lease behavior.
4. Resolve the eviction-first/load-failure contradiction and define rollback behavior.
5. Add runtime health/poison states and controlled restart semantics for uncertain cleanup.
6. Expand qualification identity with the complete inference profile and require fresh sampler state.
7. Freeze hard-versus-soft protection semantics, expiry/generation, and current-demand precedence.
8. Add crash/replay journals and capability-specific idempotency/outcome rules.
9. Freeze source-quality/provenance policy before allowing current/latest research to become SATISFIED.
10. Run a real pinned-build spike with actual GGUF/LoRA fixtures, memory soak, failure injection, and end-to-end latency measurements.
11. Only after those gates pass, begin full Recipe implementation and training-set generation.

## 9. Final decision

**Proceed now:** a narrow, serialized AdapterManager/ModelRuntime/SpecialistInvoker spike using test doubles first and a small set of real adapters second.

**Do not proceed now:** full Recipes 0–8 implementation, claims of runtime validation, production research/persistence trust, or bulk AAE JSONL generation.

The architecture is worth continuing. The current PASS label should be read as **documentation lint passed**, not **prototype validated**.
