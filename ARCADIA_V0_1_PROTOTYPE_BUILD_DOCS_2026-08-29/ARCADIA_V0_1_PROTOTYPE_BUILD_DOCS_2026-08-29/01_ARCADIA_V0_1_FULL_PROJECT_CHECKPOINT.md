# A.R.C.A.D.I.A. v0.1 — Full Project Checkpoint
## Final Prototype Integration Specification

**Version:** `0.1-prototype`  
**Date:** 2026-08-29  
**Status:** **FULL-SPINE DESIGN FROZEN / IMPLEMENTATION AUTHORIZED BY GATES / LEARNED AUTHORITY T0 UNTIL QUALIFIED**

# 0. Checkpoint verdict

A.R.C.A.D.I.A. v0.1 retains the complete compartmentalized spine:

```text
[0] CONVERSATION RESOLVER
    minimum sufficient transcript evidence
        ->
[1] INTENT
    what the user communicated
        ->
[pre-Context provisional-memory gate when required]
        ->
[2] CONTEXT
    grounded working state
        ->
[3] DECISION
    required work plan
        ->
[4] TOOL / EXECUTION
    operation reality / immutable receipts
        ->
[5] RECONCILIATION
    what returned work semantically establishes
        ->
[6] PERSISTENCE
    durable semantic mutation
        ->
[7] COMPLETION
    terminal standing of every immutable Rxxx
        ->
[8] RESULT
    truth-preserving conversational articulation + publication
```

No semantic recipe is merged to solve latency, VRAM pressure, or model count.

The correct v0.1 implementation posture is:

```text
GO: deterministic host foundation
GO: AAE/runtime boundary implementation
GO: test-double AdapterManager/ModelRuntime/SpecialistInvoker spike
GO: real pinned base-GGUF + small LoRA spike after test doubles pass
CONDITIONAL GO: full Recipe 0–8 implementation after runtime gates pass
NO-GO: production trust before exact runtime identities earn qualification
NO-GO: bulk training-data generation from unreviewed runtime traces
```

# 1. System authority model

| Layer | Owns | Must not own |
|---|---|---|
| Conversation Resolver | minimum sufficient transcript scope | semantic memory, Intent, tools |
| Intent | immutable current-turn requirements | history retrieval, execution, durable truth |
| Context | grounded active state + provenance | Intent mutation, tools, durable writes |
| Decision | work plan / evidence targets / persistence obligations | execution, returned-evidence truth, SQLite writes |
| Execution Host | whether authorized operations occurred | semantic sufficiency |
| Reconciliation | meaning of immutable receipts/evidence | Intent mutation, tool execution, terminal completion |
| Persistence models | bounded semantic assessment/composition | SQL, canonical IDs, Completion |
| Persistence Host | semantic IDs, transactions, compensation, PRC | free-form invention, terminal standing |
| Completion | terminal Rxxx standing | new work, new facts, upstream rewrite |
| Result | truth-preserving articulation | re-deciding standing or doing work |
| ModelRuntime | pinned base/context/sampler/libllama mechanics | specialist selection, recipe semantics |
| AdapterManager | physical adapter lifecycle/leases/residency/health | model-visible semantic contracts |
| SpecialistInvoker | sole legal learned-call dispatch boundary | recipe authority or external execution |
| AAE Contract Registry | machine-readable learned contract definitions | runtime adapter lifecycle |
| SourcePolicyRegistry | claim-specific external-evidence policy | semantic answer composition |
| OperationJournal | side-effect attempt/recovery truth | semantic requirement standing |
| Trace subsystem | forensic observability under retention policy | implicit memory or automatic training |

> **Models judge bounded semantics. The host owns identity, legality, state transitions, retrieval, schemas, hashes, side effects, durable commits, and publication.**

# 2. Core adapter roster

```text
1  Conversation Resolver
2  Spell
3  Term / Meaning
4  Prompt Analyst
5  Intent Organizer
6  Conversational Howard
7  Evidence Specialist
8  Requirement Assessor
9  Plan Composer
10 Evidence Reconciler
11 Reconciliation Composer
12 Persistence Assessor
13 Persistence Composer
14 Completion Assessor
15 Completion Composer
```

Tool / Execution adds zero learned adapters.

Physical adapter count is not logical mode count. Conversational Howard may serve multiple modes with separate AAE, schema, InferenceProfile, and qualification identities.

# 3. Global semantic locks

```text
Stored != injected.
Transcript != semantic memory.
Trace != transcript != Context != semantic memory != training data.
Technical artifact identity != semantic entity identity.
Conversation resolution != Intent.
Context resolution != Intent mutation.
Valid unresolved state != failure.
Invalid/not-ready Context != Decision input.
Planned work != executed work.
Execution success != semantic success.
Discovery != repair.
Discovery != new Intent.
Persistence obligation != persistence suggestion.
Receipt != claim of truth.
Howard commentary != host authority.
Human-readable IDs != global database identity.
Previous active Context remains active until replacement promotion is complete.
Every loop is bounded.
Every re-entry is scoped.
Every durable artifact is traceable.
Every semantic write waits for Persistence.
Missing certainty remains missing certainty.
```

# 4. Learned-call locks

Every learned call MUST satisfy all of the following:

1. Enter through `SpecialistInvoker` only.
2. Resolve one logical specialist mode to one qualified runtime identity.
3. Use host-owned structured `CALL_DATA`; no handwritten JSON runtime fragments.
4. Validate `CALL_DATA` against a strict schema with unknown fields rejected.
5. Serialize through Canonical JSON V1.
6. Build model messages through Canonical AAE Serializer from the AAE Contract Registry.
7. Keep authority instructions and untrusted data structurally separated.
8. Re-extract/reparse/revalidate the final rendered `CALL_DATA` before dispatch.
9. Acquire adapter residency+lease atomically through `ensure_hot_and_acquire()`.
10. Create a fresh context and a fresh sampler for every attempt, including repairs.
11. Apply exactly one standard adapter at scale 1.0 unless a future independently qualified contract says otherwise.
12. Record the exact InferenceProfile hash and realized seed.
13. Validate output schema + host semantic contract.
14. Bound repairs and aggregate model-call/token/work budgets.
15. Destroy context before lease release.
16. Emit host-only activation/trace artifacts; models do not self-attest runtime identity.

# 5. Adapter lifecycle lock

Long-lived residency vocabulary:

```text
COLD
READY
HOT
```

Per-call binding:

```text
ACTIVE
```

Temporary manager-only swap state:

```text
STAGING
```

Health is an independent axis:

```text
HEALTHY
QUARANTINED
POISONED
```

A failed replacement load cannot alter the committed HOT set. Full-pool replacement is load-before-commit using STAGING; the old victim remains HOT until the replacement is proven live.

A POISONED runtime domain is terminal for the current runtime epoch and requires controlled restart. Poor model answers do **not** poison the runtime.

# 6. Runtime acquisition lock

The only learned-call acquisition API is conceptually:

```text
ensure_hot_and_acquire(adapter_id, mode, minimum_trust, ...) -> AdapterLease
```

Lease identity includes:

```text
adapter_id
lease_uuid
process_epoch
handle_generation
live_handle token/reference
linear release state
```

Double release, stale generation, and stale process epoch are rejected without mutating current state.

Initial prototype lifecycle mutation is serialized for correctness.

# 7. Protection semantics

Protection is explicit:

```text
HARD protection:
  active lease
  runtime-owned active/staging commit guard
  hard PINNED policy
  never overridden by ordinary current demand

SOFT protection:
  predictive work-graph protect_set
  high-priority cache preference
  generation/expiry bounded
  may be overridden by newer current demand when no hard protection exists
```

Soft protection MUST carry an epoch/generation and finite lifetime or replacement token. Stale predictive protection may not deadlock the pool. Current demand outranks stale soft protection but never leases/hard pins.

# 8. Inference identity lock

Qualification identity includes at minimum:

```text
base_model_sha256
physical_adapter_sha256 (or BASE_ONLY marker)
llama_cpp_build_id
ModelRuntime_version
AdapterManager_version
SpecialistInvoker_version
AAE_contract_version
specialist_mode_contract_version
input_schema_version
output_schema_version
host_validator_version
inference_profile_hash
```

`InferenceProfile` covers output-affecting rendering/tokenizer/context/sampler/generation/stop/seed/backend settings. Profiles are mode-specific. Changing one creates a new qualification target.

# 9. Base-only qualification lock

The first specialist baseline is allowed—and expected—to perform poorly semantically.

`BASE_ONLY_TEST_MODE` uses:

```text
same fixture
same AAE contract
same structured packet
same schemas/validators
same InferenceProfile
same deterministic qualification seed policy
fresh context
fresh sampler
NO LoRA
```

Bad semantic output is a model/qualification failure, not runtime poisoning.

# 10. AAE authority/serialization lock

AAE v0.1 is a host-side structured contract with two planes:

```text
AUTHORITY PLANE
  stable host-owned instructions/contracts

DATA PLANE
  raw prompt, transcript, memory, tool/evidence content, refs
```

Where supported, authority occupies the highest supported chat role and data occupies a lower data/user role. Data may contain fake instructions or fake AAE delimiters but cannot create control structure.

The human-readable bracketed AAE remains mandatory as a **deterministic audit rendering**, not as the runtime parser protocol.

# 11. Source-quality lock

No universal website trust score exists.

A versioned `SourcePolicyRegistry` evaluates evidence relative to the claim using structured source relationship, directness, freshness, independence/duplication, and conflict policy.

Claims such as `latest`, `current`, `today`, or `most recent` cannot receive unconditional `SATISFIED` unless the active policy proves sufficient provenance, freshness, authority fit, and conflict resolution.

# 12. Side-effect/recovery lock

Before any external side effect, the host creates a durable OperationJournal record. Recovery is capability-specific:

```text
PROVIDER_IDEMPOTENT
VERIFY_THEN_REPLAY
NON_IDEMPOTENT_UNVERIFIABLE
```

Unknown outcome is a first-class state:

```text
OUTCOME_UNKNOWN
```

A model cannot convert network loss, crash, missing receipt, or timeout into invented SUCCESS or FAILURE.

For Persistence, the semantic mutation and successful PRC record should commit in the same SQLite transaction.

# 13. Trace/privacy/training lock

The trace policy covers the entire turn graph and cross-turn lineage: all recipe slices, re-entry, repair, learned calls, tools, evidence, Persistence, Completion, Result/publication, and back-and-forth history links.

Trace tiers:

```text
TRACE INDEX
SECURE RAW TRACE
TRAINING CANDIDATE QUARANTINE
TRAINING_APPROVED DATASET
```

Raw traces are sensitive by definition, encrypted at rest, owner-controlled, and finite-retention by default. Runtime cannot write training-approved data directly. Held-out fixtures are permanent `NEVER_TRAIN` material.

# 14. Performance / deterministic elision lock

A recipe does not deserve a model call merely because the recipe exists.

When the host can prove an artifact/transition completely and syntactically from authoritative inputs, it may produce the same authoritative artifact lineage under a deterministic proof rule.

Fast path is explicitly toggleable:

```text
fast_path_enabled = true | false
```

The value is snapshotted at turn start and recorded in the turn trace. `false` forces the ordinary learned-eligible Recipe path for testing or normal use. Safety/authority host rules remain mandatory regardless of toggle.

Fast path may never guess. Any ambiguity routes to the normal pipeline.

# 15. Historical stress correction

The R3 validation report counted 88 opening and 88 closing AAE tags. The independent checker proved:

```text
1 syntax-template envelope
87 actual learned calls across five slices
```

v0.1 uses 87 as the learned-call count for that reference trace.

# 16. v0.1 implementation verdict

The design is frozen enough to build, but runtime authority is not pre-granted.

```text
T0 = unqualified
T1 = fixture shape competence
T2 = held-out semantic competence
T3 = adversarial/composition competence
T4 = shadow runtime
T5 = limited authority
T6 = production authorization
```

No adapter/mode inherits qualification from another mode merely because it shares a physical LoRA.

# 17. Final lock

> **A.R.C.A.D.I.A. v0.1 is a host-authoritative, compartmentalized semantic pipeline. Models may propose bounded meaning; they may not invent system state, execution outcomes, evidence authority, runtime identity, or durable truth.**
