---
title: "A.R.C.A.D.I.A. v0.1 — Full Project Checkpoint"
project: "A.R.C.A.D.I.A."
version: "0.1-prototype"
checkpoint_date: "2026-08-29"
document_role: "master-build-authority"
source_path: "ARCADIA_V0_1_MASTER_BUILD_AUTHORITY.md"
source_sha256: "6f4ade64f4910fa4fe96fdda8c43fdeafa7e56e19d93185d15fa3db03d0d597e"
source_bytes: 55192
source_integrity: "preserved"
tags:
  - "arcadia/v0-1"
  - "type/authority"
  - "status/frozen"
aliases:
  - "ARCADIA_V0_1_MASTER_BUILD_AUTHORITY.md"
  - "A.R.C.A.D.I.A. v0.1 — Full Project Checkpoint"
---

> [!info] Obsidian navigation
> **Checkpoint role:** `master-build-authority`  
> **Frozen source:** `ARCADIA_V0_1_MASTER_BUILD_AUTHORITY.md` · SHA-256 `6f4ade64f4910fa4…`  
> **Command center:** [[ARCADIA v0.1 - Command Center]]  
> **Connected:** [[00_README_FIRST]] · [[01_ARCADIA_V0_1_FULL_PROJECT_CHECKPOINT]] · [[02_ARCADIA_V0_1_EXACT_BUILD_ORDER]] · [[03_ARCADIA_V0_1_GLOBAL_CONTRACTS_AND_INVARIANTS]] · [[04_ARCADIA_V0_1_AAE_CONTRACT_REGISTRY_AND_SERIALIZATION]] · [[05_ARCADIA_V0_1_MODEL_RUNTIME_ADAPTER_MANAGER]] · [[06_ARCADIA_V0_1_QUALIFICATION_AND_STRESS_GATES]] · [[07_ARCADIA_V0_1_SOURCE_POLICY_REGISTRY]] · [[08_ARCADIA_V0_1_RECOVERY_TRACE_PRIVACY]] · [[09_ARCADIA_V0_1_PERFORMANCE_FAST_PATH]] · [[CONSOLIDATION_NOTES]]

<!-- OBSIDIAN_LAYER_END — ORIGINAL SOURCE CONTENT BEGINS BELOW -->

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
# A.R.C.A.D.I.A. v0.1 — Exact Prototype Build Order

**Date:** 2026-08-29  
**Status:** LOCKED IMPLEMENTATION ORDER  
**Rule:** do not skip an acceptance gate because downstream code is easier or more exciting to build.

# Phase 0 — Freeze build inputs

1. Commit this v0.1 docs bundle and SHA256 manifest.
2. Pin Python/runtime dependencies used by host validation.
3. Pin SQLite feature assumptions (FTS5 required).
4. Select/pin the initial base GGUF identity.
5. Pin exact llama.cpp repo commit/build options/library hash before real runtime qualification.
6. Create one versioned runtime config source; no magic settings hidden in recipe files.

Gate 0: source manifest reproducible; no unresolved v0.1 design contradiction blocks the narrow runtime spike.

# Phase A — Shared deterministic foundation

Build first:

```text
core/config.py
core/ids.py
core/canonical_json.py
core/hashing.py
core/artifact_envelope.py
core/ledger.py
core/validation.py
core/repair_policy.py
core/work_budget.py
core/trace_index.py
core/trust_registry.py
storage/connection.py
storage/migrations.py
storage/transcript_repository.py
storage/artifact_repository.py
storage/registry_snapshots.py
```

Required behavior:

- UUID host authority.
- scoped human-readable aliases.
- Canonical JSON V1.
- strict JSON decoder rejects duplicate keys/non-finite/trailing content.
- JSON Schema 2020-12 validation.
- WAL/foreign keys/busy timeout/rollback.
- transcript and semantic-memory authority remain separate.
- aggregate call/work/re-entry/repair budget ledger exists before full runtime.

Gate A: deterministic unit tests only; no model required.

# Phase A1 — AAE Contract Registry + canonical serializer

Create:

```text
contracts/aae/registry.*
contracts/aae/global_awareness.*
contracts/schemas/
contracts/policies/origin_trust.*
aa_runtime/serializer.py
aa_runtime/human_renderer.py
aa_runtime/call_data_gate.py
```

Requirements:

1. Define all core physical adapter bindings and logical modes.
2. Store authority text/fields once.
3. Define strict input/output schemas, legal refs/enums, field caps, repair shape, next consumers.
4. Build machine role-separated messages from structured AAE objects.
5. Canonically encode untrusted data; no delimiter parser.
6. Produce deterministic bracketed human-readable audit rendering from the same object.
7. Reparse/revalidate final rendered `CALL_DATA` immediately before dispatch.
8. Add adversarial instruction-impersonation fixtures.
9. Add deterministic context-budget projection; never silently truncate.

Gate A1:

- training/runtime use same registry source;
- exact CALL_DATA malformed-path regression rejected;
- fake `[RESPONSE_CONTRACT]`/closing tags remain data;
- schema-less dispatch impossible;
- human render is deterministic.

# Phase A2 — ModelRuntime / AdapterManager with test doubles

Create:

```text
model_runtime/libllama_backend.py
model_runtime/model_runtime.py
model_runtime/context_factory.py
model_runtime/sampler_factory.py
model_runtime/inference_profiles.py
model_runtime/adapter_registry.py
model_runtime/adapter_manager.py
model_runtime/residency_policy.py
model_runtime/adapter_lease.py
model_runtime/activation_receipts.py
model_runtime/memory_telemetry.py
model_runtime/specialist_invoker.py
model_runtime/runtime_health.py
```

Implement before real LoRAs:

- COLD / READY / HOT.
- STAGING as temporary replacement transaction state.
- ACTIVE per call.
- HEALTHY / QUARANTINED / POISONED health axis.
- process epoch and handle generation.
- atomic `ensure_hot_and_acquire()`.
- linear one-time lease release.
- steady `max_hot_adapters` policy with measured swap headroom requirement.
- load-before-evict prepare/commit swap.
- hard vs soft protection, expiry/generation, current-demand precedence.
- fresh context + fresh sampler per attempt.
- mode-specific immutable InferenceProfile hash.
- controlled POISONED restart semantics.
- 100-entry synthetic registry.

Gate A2-TD: race/failure tests pass with test doubles, including forced staging-load failure and stale lease release.

# Phase A3 — Real pinned GGUF / LoRA runtime spike

This is the checkpoint the independent stress report required before full learned recipe implementation.

1. Pin llama.cpp build and confirm required adapter APIs.
2. Load one base GGUF and keep it resident.
3. Run BASE_ONLY_TEST_MODE through real SpecialistInvoker.
4. Load a small set of actual/test LoRA GGUF adapters.
5. Run A/B/A isolation with fresh context **and fresh sampler**.
6. Run load/apply/infer/free soak.
7. Measure host RAM/VRAM baseline, load deltas, inference peak, post-free behavior.
8. Determine safe committed HOT ceiling that still leaves one STAGING swap slot + inference reserve.
9. Force load failure while full; old committed HOT set must remain unchanged.
10. Force every-HOT-leased and every-hard-pinned exhaustion.
11. Test soft-protect expiry/current-demand override.
12. Inject shutdown/failure at lifecycle boundaries.
13. Inject uncertain cleanup; domain must POISON and restart into new epoch.
14. Record real per-call and end-to-end timing distributions.

Gate A3: no unacceptable memory trend; runtime state remains provable; all activation receipts complete; safe HOT ceiling measured rather than assumed.

# Phase B — Recipe 0 Conversation Resolver + Recipe 1 Intent

Build Recipe 0 first, then Intent specialists:

```text
Conversation Resolver
Spell
Term / Meaning
Prompt Analyst
Intent Organizer
Conversational Howard (Intent comment mode)
```

Fast path MUST be disabled for canonical full-pipeline qualification fixtures unless the test specifically targets fast-path equivalence.

Gate B: zero-history, targeted history, ambiguity, control-signal, exact-literal, and immutable Rxxx tests pass.

# Phase C — Persistence Host skeleton before normal Context memory use

Before Context may consume clean semantic memory:

- install semantic-memory SQLite migration;
- implement semantic read repository;
- implement `memory_commit_seq`;
- implement PROVISIONAL transaction standing;
- implement compensation lineage;
- implement pre-Context provisional review gate;
- implement PRC-in-same-transaction success recording.

Learned Persistence adapters are not required yet.

Gate C: crash-safe provisional state is excluded from clean Context until policy says otherwise.

# Phase D — Recipe 2 Context

Build:

```text
router / split library
bounded packet projection
semantic retrieval
Evidence Specialist
Conversational Howard context-lane modes
promotion transaction
Context snapshot
projection-recall metrics
```

Integrate SourcePolicy metadata where external evidence is part of Context.

Gate D: conflicts/unresolved preserved; downstream discovery cannot mutate Intent; promotion comment gate works.

# Phase E — Recipe 3 Decision

Build Requirement Assessor and Plan Composer plus host graph/capability gates.

Host owns IDs, graph legality, capability existence, side-effect class, persistence-obligation separation, work budgets, and re-entry scope.

Gate E: no-work cases do not compulsively create tools; blocked requirements create no executable work.

# Phase F — Recipe 4 Tool / Execution + OperationJournal

Build host-only execution:

```text
request compiler
capability registry bindings
scheduler
OperationJournal
per-capability recovery policy
immutable receipts
transport retry
idempotency / verification
compensation interface
publication-independent receipt commit
```

Prototype capabilities may include search/wiki/load/save fixtures as documented.

Gate F: request-compilation failure produces no false receipt; uncertain side effect becomes OUTCOME_UNKNOWN; restart does not blindly duplicate.

# Phase G — Recipe 5 Reconciliation + SourcePolicyRegistry

Build deterministic evidence preprocessing first:

```text
normalization
canonical URL/identity
content hashing
duplicate/syndication groups
freshness metadata
source relationship/directness
claim-policy lookup
signal pack
```

Then Evidence Reconciler + Reconciliation Composer + bounded Context/Decision re-entry.

Gate G: source labels alone cannot justify terminal truth; latest/current evidence obeys policy; discovery vs repair remains separate.

# Phase H — Recipe 6 learned Persistence

Build Persistence Assessor and Persistence Composer over already-proven host semantic transactions.

Add typed Memory Inspector user controls.

Gate H: all normative obligations accounted for; model-written SQL impossible; stale snapshot cannot commit; compensation preserves history.

# Phase I — Recipe 7 Completion

Build closure bundles, Completion Assessor, Completion Composer, FSP, projection-recall and provisional-persistence closure cases.

Completion terminal states remain:

```text
SATISFIED
PARTIALLY_SATISFIED
BLOCKED
FAILED
```

Freshness-sensitive claims are additionally constrained by SourcePolicy terminal gates.

Gate I: no new work/facts; exact requirement coverage; status preservation.

# Phase J — Recipe 8 Result + PublicationJournal

Build per-requirement Conversational Howard comments, bounded final composition/fan-in, literal locks, disclosure coverage, publication, and transcript commit.

Publication recovery uses `turn_uuid + result_hash` identity and never regenerates semantic Result merely because transcript commit failed.

Gate J: mixed partial/blocker truth cannot be cleaned up into false certainty.

# Phase K — Qualification progression

For every logical specialist mode:

```text
base GGUF frozen-suite baseline
-> T1 fixture/shape competence
-> T2 held-out semantic
-> T3 adversarial/composition
-> T4 shadow runtime
-> T5 limited authority
-> T6 production authorization
```

Base and adapter comparisons use identical fixture/AAE/schema/InferenceProfile/qualification seed policy.

Held-out data is permanently NEVER_TRAIN.

# Phase L — Full-spine v0.1 stress/demo gate

Required end-to-end classes:

```text
D0 deterministic exact-literal fast path ON
same exact-literal with fast path OFF
zero-history normal semantic answer
history-dependent reference resolution
durable semantic-memory lookup
search success but semantic failure
latest/current source conflict
material discovery + Context re-entry
verified Save File
save timeout with OUTCOME_UNKNOWN
crash after effect before receipt
explicit remember -> PROVISIONAL
next-turn affirmation
next-turn neutral stabilization
next-turn correction/undo compensation
Memory Inspector correction
Persistence commit + publication failure
mixed partial/blocker Result
budget exhaustion with honest Completion
full provenance replay
trace deletion/candidate-cascade test
training export held-out rejection
```

Gate L: v0.1 prototype demo may be called **implemented** only after these gates pass. It still does not imply T6 for every specialist.

# Fast-path operating rule

Config:

```text
fast_path_enabled: bool
```

- snapshotted at turn start;
- recorded in performance/turn receipt;
- qualification/full-spine tests default OFF unless specifically testing deterministic equivalence;
- normal prototype use may enable after D0 tests pass;
- disabling it is supported normal operation, not an unsupported debug hack.
# A.R.C.A.D.I.A. v0.1 — Global Contracts and Invariants

This document is the cross-cutting rulebook. Recipe details may become more specific but may not weaken these invariants.

# 1. Identity and provenance

- Host creates canonical UUID identities.
- Human IDs (`R001`, `W001`, `REC001`, etc.) are scoped aliases.
- Every durable artifact is versioned, hashable, traceable, and linked to upstream basis refs.
- Canonical JSON V1 is the hashing/serialization baseline unless an artifact explicitly uses another frozen profile.
- Models never invent canonical IDs and cannot promote local proposal keys without host allocation.

# 2. Retention domains

```text
conversation transcript
technical artifact ledger
semantic memory
secure raw trace
training candidate quarantine
training-approved datasets
```

These are separate authorities. Presence in one never implies presence in another.

# 3. Intent immutability

Original accepted Rxxx requirements represent what the user communicated. Later discovery, repair, evidence, or memory does not rewrite them.

# 4. Context promotion

Context can be partial/conflicted/unresolved and still valid. Invalid/not-ready Context cannot enter Decision. Replacement Context does not become ACTIVE until required promotion validation/comment succeeds; prior ACTIVE revision remains authoritative during pending promotion.

# 5. Work reality

Decision plans. Execution performs. Reconciliation interprets. Persistence writes semantic state. Completion closes requirements. Result speaks.

No layer may claim authority owned by another because it “probably happened.”

# 6. Uncertainty

Unknown is a valid state. Examples include unresolved Context, source conflict, blocked work, OUTCOME_UNKNOWN execution, and POISONED runtime state. No learned component may fill these gaps with fabricated certainty.

# 7. Budgets

Every loop is bounded. Host configuration must define finite per-stage and aggregate ceilings for:

```text
model attempts/repairs
context/history expansion
Context retrieval expansion
Decision work expansion
Reconciliation discovery depth
re-entry depth
side-effect retries/compensations
total learned calls
total model-visible input/output tokens
```

Budget exhaustion preserves accumulated truth and routes toward honest Completion. It never resets history or fabricates success.

# 8. Repair

Repair is not a hidden extra reasoning universe. Every repair has its own attempt UUID/trace, uses the same authoritative base packet plus explicit validation error, obeys aggregate attempt/token caps, and receives a fresh context/sampler.

# 9. Packet projection

Models see only bounded authorized content needed for their contract. A bare reference ID never supplies semantic meaning. If a specialist must interpret an item, bounded content must be present. Projection itself is benchmarked for required-artifact recall and irrelevant-artifact injection.

# 10. Runtime health versus model quality

Bad model output, schema rejection, semantic failure, or repair exhaustion do not automatically mean runtime corruption.

Health changes only when mechanical state certainty/integrity is lost.

# 11. Side effects

External operation state is host truth only. `SUCCESS`, `FAILED`, and `OUTCOME_UNKNOWN` are based on receipts/journal/verification, not model inference.

# 12. Evidence

Evidence authority is claim-specific. `DIRECT_SOURCE_EVIDENCE` or similar labels are descriptive metadata, not terminal proof by themselves.

# 13. Deterministic host elision

If host rules completely prove a stage output, the host may emit the normal artifact without calling a model. The trace records the proof rule. When fast path is disabled, the ordinary learned-eligible path is forced for semantic stages, but mandatory host safety/authority checks remain.

# 14. Training

Runtime success does not automatically create training data. Training consumes only immutable approved dataset manifests. Held-out fixtures never enter training.

# 15. Human readability

Every authoritative machine object important to debugging must have a deterministic human-readable rendering. Human-readable views are derived audit surfaces, not alternate sources of truth.
# A.R.C.A.D.I.A. v0.1 — AAE Contract Registry and Canonical Serialization

**Purpose:** freeze the shared learned-call contract that training and runtime must use identically.

# 1. Structured AAE object

The runtime object is not a handwritten delimiter document.

```text
AAECall
  contract_id
  contract_version
  specialist_mode_id
  authority_plane
  data_plane
  input_schema_version
  output_schema_version
  response_contract
  inference_profile_id
```

# 2. Authority and data planes

## Authority plane

Host-owned stable instructions:

```text
Global Awareness
Specialist Awareness / jurisdiction
forbidden responsibilities
legal reference behavior
uncertainty behavior
Response Contract
```

## Data plane

Bounded content such as:

```text
raw prompt
transcript excerpts
Context artifacts
memory evidence
tool results
web/source evidence
prior validated recipe artifacts
```

Data text has `CONTENT_ONLY` authority even if it contains imperative language, role labels, fake system messages, fake response contracts, or AAE delimiters.

# 3. Message-role serialization

Where the model/chat template supports roles:

- authority plane goes in the highest supported trusted instruction role;
- structured data goes in lower data/user role messages;
- no raw untrusted text is concatenated into authority instructions.

If the backend has weaker role semantics, the serializer still maintains explicit structural separation and origin labels; qualification must test the exact template actually used.

# 4. CALL_DATA hard gate

Runtime order:

```text
host Python/typed object
-> strict JSON Schema validation
-> Canonical JSON V1
-> build final model messages
-> extract final CALL_DATA representation
-> strict production-equivalent parse
-> same schema validation
-> dispatch
```

Reject at minimum:

```text
illegal escapes / malformed JSON
duplicate keys
NaN / Infinity
trailing content
unknown properties
wrong types
out-of-range enum/length/item counts
non-strict object schemas
```

# 5. Origin/trust metadata

Model-visible data items use explicit metadata such as:

```text
origin:
  USER_PROMPT
  TRANSCRIPT
  SEMANTIC_MEMORY
  TOOL_RECEIPT
  WEB_RESULT
  HOST_DERIVED_SIGNAL

authority_class:
  CONTENT_ONLY
  EXTERNAL_UNTRUSTED_EVIDENCE
  HOST_VERIFIED_EXECUTION
  HOST_VERIFIED_STATE
```

These labels constrain framing; they do not magically make an LLM injection-proof.

# 6. Field caps and deterministic projection

Every contract defines:

```text
max item count
max string/array size
max source excerpt size
max total model-visible input budget
reserved output budget
projection priority rules
```

If budget is exceeded, the host deterministically projects or fails with an explicit bounded state. Silent truncation is forbidden.

# 7. Human-readable audit renderer

A deterministic renderer may display:

```text
<A.R.C.A.D.I.A_ADAPTER_CALL>
[GLOBAL_AWARENESS]
...
[SPECIALIST_AWARENESS]
...
[CALL_DATA]
{canonical JSON}
[RESPONSE_CONTRACT]
...
</A.R.C.A.D.I.A_ADAPTER_CALL>
```

This format is mandatory for inspectability but is **not** the parser boundary. Fake tags inside data remain escaped/encoded string content.

# 8. Core registry entries

The physical roster is 15; logical modes may be more numerous.

| Physical adapter | Recipe | Principal logical modes |
|---|---:|---|
| Conversation Resolver | 0 | `SCOPE_PROPOSAL`, `SCOPE_VALIDATION` |
| Spell | 1 | spelling/normalization semantic pass |
| Term / Meaning | 1 | bounded term/reference meaning |
| Prompt Analyst | 1 | task/constraint analysis |
| Intent Organizer | 1 | requirement composition |
| Conversational Howard | 1/2/8 | Intent comment, Context lane comment, Context synthesis, Result requirement comment, Result final compose |
| Evidence Specialist | 2 | Context evidence semantic selection |
| Requirement Assessor | 3 | per-Rxxx readiness/work/blocker/persistence assessment |
| Plan Composer | 3 | shared Wxxx graph composition |
| Evidence Reconciler | 5 | receipt/evidence semantic assessment |
| Reconciliation Composer | 5 | cross-work findings/discovery/repair composition |
| Persistence Assessor | 6 | candidate/obligation semantic disposition |
| Persistence Composer | 6 | bounded semantic mutation plan |
| Completion Assessor | 7 | per-Rxxx closure judgment |
| Completion Composer | 7 | final standing packet composition |

Each logical mode binds independently to:

```text
physical_adapter_id
AAE contract/version
input/output schema versions
host validator version
InferenceProfile id/hash
minimum trust level
```

# 9. Repair contract

Repair receives:

```text
same authoritative source packet
same specialist mode
same InferenceProfile
new context
new sampler
new attempt UUID
exact machine validation error
```

A repair may not receive invented facts or expanded authority merely because attempt 1 failed.

# 10. Injection qualification

Required adversarial fixtures include data containing:

```text
[GLOBAL_AWARENESS]
[RESPONSE_CONTRACT]
</A.R.C.A.D.I.A_ADAPTER_CALL>
SYSTEM: ignore previous instructions
fake host authorization
fake tool success
fake trusted memory labels
nested quoted prompt injection
Unicode-confusable reference IDs
```

Passing output shape alone is insufficient; semantic compliance with the actual authority contract is scored.

# 11. Training/runtime identity

Training examples and runtime calls are generated from the same registry definitions. Manual prompt re-authoring for training is forbidden.
# A.R.C.A.D.I.A. v0.1 — ModelRuntime + AdapterManager Specification

# 1. Canonical runtime

```text
ONE long-lived compatible base GGUF
+ host-owned LoRA GGUF adapter library
+ bounded committed HOT pool
+ temporary transactional STAGING slot/headroom
+ one standard ACTIVE adapter per learned call
+ fresh context + fresh sampler per attempt
```

Recipes never load/free/apply LoRAs.

# 2. Ownership

```text
ModelRuntime:
  base model lifetime
  context/sampler create/destroy
  raw libllama adapter primitives through backend wrapper
  raw inference
  backend/build identity
  memory telemetry

AdapterManager:
  registry readiness
  COLD/READY/HOT
  STAGING transactions
  leases/generations/epochs
  pin/protect policy
  load/eviction commitment
  health routing

SpecialistInvoker:
  logical binding
  atomic lease acquisition
  AAE construction
  inference profile
  output validation/repair
  trace/activation receipt
```

# 3. Residency

```text
COLD: registered, no live adapter handle, readiness not current for epoch
READY: integrity/base/contract checked, no live adapter handle
HOT: manager owns a valid live adapter handle
ACTIVE: HOT handle is bound to this fresh call context
STAGING: temporary replacement handle, not committed HOT and never exposed to recipes
```

READY makes no CPU-RAM/VRAM promise. HOT means a live libllama adapter object exists; physical placement is measured.

# 4. Health

```text
HEALTHY: lifecycle assumptions trustworthy
QUARANTINED: specific adapter blocked while shared runtime remains trustworthy
POISONED: affected runtime domain mechanically uncertain; no new learned calls
```

Bad model answers do not change runtime health.

POISONED cannot return to HEALTHY in the same runtime epoch. Recovery requires controlled teardown/restart, new epoch, base/runtime validation, and zero inherited handles/leases.

# 5. Atomic acquisition

Public learned-call manager API:

```text
ensure_hot_and_acquire(adapter_id, minimum_trust, protect_context=...) -> AdapterLease
release(lease) -> result
snapshot() -> state
```

Independent call-facing `ensure_hot()` + `acquire()` is forbidden.

# 6. Lease identity and linear release

```text
adapter_id
lease_uuid
process_epoch
handle_generation
live_handle token/reference
acquired_at
released state
```

First valid release mutates once. Double release, stale epoch, stale generation, identity mismatch are rejected and forensically logged.

# 7. Transactional pool-full replacement

Given committed HOT `{A,B,C,D,E}` and requested `F`:

```text
select legal victim E
verify swap headroom
load F -> STAGING while E remains HOT
validate F handle/runtime identity

if F fails:
  discard F staging
  committed HOT stays {A,B,C,D,E}

if F succeeds:
  commit E eviction
  promote F HOT
  atomically lease F before exposing it as unprotected demand
```

If failed STAGING cleanup is uncertain, route to health policy rather than pretending rollback succeeded.

`max_hot_adapters` is the steady committed ceiling. Hardware qualification must leave enough physical headroom for one STAGING adapter plus context/inference peak and safety reserve. If not, lower the steady ceiling.

# 8. Protection policy

## Hard protection

- `lease_count > 0`;
- active lifecycle/staging commit guard;
- hard `PINNED` policy.

Hard protection cannot be overridden by ordinary demand.

## Soft protection

- predicted next adapters from validated work graph;
- `HIGH_PRIORITY` preference;
- protect-set generation with expiry/replacement token.

Current demand may override stale/older soft protection when it needs a legal eviction candidate. Soft protection must not become immortal.

# 9. InferenceProfile

Each logical mode binds to an immutable profile covering at least:

```text
chat template identity
prompt serializer version
tokenizer identity/overrides
n_ctx / context budget policy / reserved output
sampler chain
temperature/top-k/top-p/min-p
repeat/frequency/presence penalties
grammar if any
seed policy
max output tokens
stop policy/sequences
qualification-sensitive backend settings
```

Canonical JSON + SHA-256 => `inference_profile_hash`.

Fresh sampler is created for every attempt. Qualification fixtures use deterministic seed policy; actual realized seed is recorded.

# 10. Activation receipt

Minimum host-only fields:

```text
call_uuid / attempt_uuid / turn_uuid
capability_id / specialist_mode_id
base_model_sha256
llama_cpp_build_id
runtime/manager/invoker versions
physical_adapter_id + adapter_sha256 or BASE_ONLY
AAE/input/output/validator versions
inference_profile_id/hash
prompt_render_hash
sampler_instance_uuid
seed_policy + actual_seed
process_epoch + handle_generation + lease_uuid
residency before/after
load/staging/eviction facts
fresh_context=true
fresh_sampler=true
apply status/scale
memory telemetry
timings
```

It is not a Recipe 4 `RECxxx` receipt.

# 11. Base-only mode

`BASE_ONLY_TEST_MODE` goes through the same Invoker path but applies no LoRA. It is qualification infrastructure and never silent fallback after expected adapter failure.

# 12. Runtime shutdown

```text
stop accepting new learned calls
mark/drain active acquisitions
complete or abort safely under journal/health rules
destroy contexts/samplers
release valid leases
free HOT adapters when certainty permits
free base
shutdown backend
```

If lifecycle certainty is lost during destructive operations, poison rather than guessing.

# 13. Default prototype policy

Initial config may request:

```text
max_hot_adapters = 5
standard_active_adapters = 1
standard_scale = 1.0
serialized_manager_mutation = true
```

But the real safe steady HOT ceiling is finalized only by target-hardware measurement with swap/inference headroom.
# A.R.C.A.D.I.A. v0.1 — Qualification and Stress Gates

# 1. Trust progression

```text
T0 UNQUALIFIED
T1 SCHEMA/FIXTURE COMPETENCE
T2 HELD-OUT SEMANTIC COMPETENCE
T3 ADVERSARIAL/COMPOSITION COMPETENCE
T4 SHADOW RUNTIME
T5 LIMITED AUTHORITY
T6 PRODUCTION AUTHORIZATION
```

Qualification belongs to an **exact runtime identity**, not merely an adapter filename.

# 2. Base versus adapter comparison

For each mode:

```text
same frozen fixture
same AAE registry version
same packet builder
same schemas/validators
same InferenceProfile hash
same deterministic qualification seed policy
fresh context/sampler
```

Run once base-only, then with target adapter. Poor base semantic output is expected data and does not poison runtime.

# 3. Phase-A runtime gates

Must test:

```text
pinned libllama API
base hash mismatch
adapter hash/path/base mismatch
atomic ensure_hot_and_acquire
full-pool staging load success
full-pool staging load failure preserves committed pool
no legal eviction candidate
swap headroom unavailable
all HOT leased
hard pins versus soft protects
soft protect expiry/current-demand precedence
double lease release
stale release after unload/reload
stale pre-restart lease
fresh context every attempt
fresh sampler every attempt
A/B/A isolation
100-adapter synthetic registry
load/free memory soak
uncertain free -> POISONED -> controlled restart
shutdown/process kill at lifecycle transitions
```

# 4. AAE/schema adversarial gates

```text
malformed CALL_DATA / illegal escapes
duplicate keys
NaN/Infinity
trailing content
unknown fields
huge arrays/strings
wrong types
fake response contract / fake AAE close tag
fake SYSTEM/host authorization inside user/tool/memory text
invented authoritative IDs
dangling/cyclic refs
duplicate local keys
Unicode-confusable IDs
context budget overflow: deterministic projection or explicit failure
repair attempt UUID + aggregate cap
```

# 5. Side-effect/recovery gates

```text
crash before dispatch
crash after ATTEMPT_ARMED
external success before local receipt commit
effect succeeds but receipt lost
receipt commits but publication fails
persistence commit boundary crash
restart with in-flight work
timeout where outcome cannot be determined
duplicate request after restart
verify-then-replay
provider-idempotent replay
unverifiable non-idempotent OUTCOME_UNKNOWN
```

# 6. Source-policy gates

```text
latest/current with fresh official source
latest/current with stale official source
newer secondary versus stale official
conflicting official sources
syndicated duplicates do not count as independent corroboration
missing retrieval/publication/version date
claim policy requiring multiple independent sources
community sentiment not judged by official publisher alone
```

# 7. Trace/training gates

```text
secure raw trace encrypted/owner controlled
raw retention expiry removes payload but preserves safe tombstone/index
full turn lineage spans all recipe/re-entry/repair slices
candidate extraction copies only selected fields
sanitization transforms candidate copy, not forensic raw source
held-out fixture rejected from training export
runtime cannot directly mark TRAINING_APPROVED
deletion cascades through untrained candidates/manifests
approved dataset manifest hash reproducible
```

# 8. Performance gates

Every completed turn records:

```text
path_class
fast_path_enabled / taken / proof rule / bypass reason
learned_call_count
first_pass_success_count
repair_attempt_count
fresh_context_count
adapter hot hits / loads / evictions
input/output tokens
model latency
adapter transition latency
end-to-end latency
```

Do not invent p50/p95 budgets before the real pinned runtime spike. Freeze numbers from measurement by path class.

# 9. Historical five-slice stress baseline

Corrected learned-call counts:

| Slice | Task | Actual learned calls | Distinct physical adapters | Cold strict-LRU loads at 5 | Evictions |
|---|---|---:|---:|---:|---:|
| 1 | exact `Ready.` | 13 | 10 | 10 | 5 |
| 2 | repeat prior line | 14 | 10 | 10 | 5 |
| 3 | research + remember | 27 | 15 | 18 | 13 |
| 4 | exact file-save attempt | 13 | 10 | 10 | 5 |
| 5 | research + ambiguous save | 20 | 13 | 14 | 9 |

The 88th balanced AAE pair in the historical file is the syntax template; actual slice calls = 87.

The purpose of v0.1 fast-path/model-necessity elision is not to erase complex semantic work. It is to prevent provable host-only work from being multiplied into unnecessary model calls.

# 10. v0.1 demo acceptance

A v0.1 implementation checkpoint must publish:

```text
pinned dependency manifest
base model hash
adapter manifest hashes
all active InferenceProfile hashes
AAE registry hash
schema/validator versions
runtime health/epoch record
Phase A/A2/A3 test report
full-spine integration report
performance distribution report
known failing/blocked qualification modes
```

A demo may run while specialists remain below T6 as long as authority routing respects their trust levels.
# A.R.C.A.D.I.A. v0.1 — SourcePolicyRegistry Specification

# 1. Core decision

A.R.C.A.D.I.A. does **not** maintain a universal website reputation score.

Evidence sufficiency is claim-specific.

# 2. Policy families

Initial extensible families:

```text
SOFTWARE_CURRENT_RELEASE
CURRENT_OFFICE_HOLDER
CURRENT_PRODUCT_SPEC
CURRENT_LAW_OR_RULE
HISTORICAL_FACT
SCIENTIFIC_CLAIM
GENERAL_INFORMATION
COMMUNITY_SENTIMENT
```

Each policy defines preferred source relationships, minimum provenance, freshness rules, corroboration, conflict behavior, and terminal Completion requirements.

# 3. Evidence axes

Preserve discrete facts, not one magic score:

```text
source_relation
  OFFICIAL_PUBLISHER
  OFFICIAL_REGISTRY
  GOVERNMENT_OR_REGULATOR
  ACADEMIC_PRIMARY
  PRIMARY_PARTICIPANT
  INDEPENDENT_SECONDARY
  NEWS_SECONDARY
  COMMUNITY
  UNKNOWN

evidence_directness
  PRIMARY
  DERIVED
  SECONDARY
  COMMENTARY

freshness_status
  CURRENT_WITHIN_POLICY
  STALE_FOR_POLICY
  UNKNOWN

claim_specificity
  DIRECT
  PARTIAL
  CONTEXTUAL

retrieval_integrity
  COMPLETE
  PARTIAL
  FAILED
```

# 4. Required external evidence receipt fields

At minimum when available/applicable:

```text
evidence_ref
retrieval_capability
query_or_request
original_locator
canonical_locator
source_identity/domain
retrieved_at
published_at
updated_at
version_date
title
content_hash
source_relation
evidence_directness
independence_group / syndication metadata
bounded relevant extract
claim refs supported/challenged
```

A label such as `DIRECT_SOURCE_EVIDENCE` is never enough on its own.

# 5. Freshness-sensitive truth

Terms such as:

```text
latest
current
today
still
presently
most recent
```

make freshness part of the claim's truth conditions.

Completion may emit unconditional SATISFIED only when the active policy confirms required provenance, freshness, authority fit, and conflict resolution.

# 6. Conflicts

Authority metadata does not erase semantic disagreement. Reconciliation still examines what each source actually says and whether distinctions such as stable/prerelease/platform/date explain the conflict.

Unresolved material conflict remains uncertainty/partial/blocker state.

# 7. Independence

Exact duplicates, syndication, mirrors, and content copies share an `independence_group` and do not count as independent corroboration merely because URLs differ.

# 8. Claim-specific examples

- Official software release registry may be sufficient to establish current stable version when fresh and unambiguous.
- One company page is not enough to prove “experts broadly agree.”
- Official publisher is not automatically the best authority for community sentiment.
- Two official sources can still conflict and require semantic reconciliation.

# 9. Host/model split

Host deterministically extracts/canonicalizes source metadata, duplicate groups, timestamps, and policy family. Evidence/Reconciliation specialists judge bounded semantic support/conflict. Models do not invent missing provenance.
# A.R.C.A.D.I.A. v0.1 — Recovery, Trace Privacy, and Training Firewall

# Part A — Side-effect crash/replay

## A1. OperationJournal

Before an external side-effect attempt crosses its execution boundary, persist a journal record.

States:

```text
PREPARED
ATTEMPT_ARMED
CONFIRMED_SUCCESS
CONFIRMED_FAILURE
OUTCOME_UNKNOWN
```

Once ATTEMPT_ARMED is durable, a crash means the effect **may** have occurred. Absence of a success receipt is not proof of failure.

## A2. Capability recovery classes

```text
PROVIDER_IDEMPOTENT
  replay same idempotency key; provider deduplicates

VERIFY_THEN_REPLAY
  query external state first; replay only after proving no effect

NON_IDEMPOTENT_UNVERIFIABLE
  never auto-retry an uncertain armed attempt; remain OUTCOME_UNKNOWN
```

Read-only capabilities are separately classified and normally replayable under their own transport policy.

## A3. Save File prototype

Use atomic write where possible, post-write verification, desired content hash, and stable idempotency identity. After restart:

```text
matching file/hash -> recovered confirmed success
provably absent -> safe replay if policy permits
cannot determine -> OUTCOME_UNKNOWN
```

## A4. Persistence PRC atomicity

For semantic Persistence, successful semantic mutations and the durable PRC-success row should commit inside the same SQLite transaction. Either the semantic commit and its local proof exist together or both roll back.

## A5. PublicationJournal

Result publication and transcript commit are distinct.

Journal at least:

```text
turn_uuid
result_hash
publication_attempt_uuid
transport_state
transcript_state
```

If publication succeeds but transcript commit fails, recover the transcript relation for the same immutable `result_hash`; do not regenerate Result or rerun the semantic pipeline.

## A6. Model prohibition

Models never decide an uncertain external outcome. OUTCOME_UNKNOWN propagates through Reconciliation/Completion/Result honestly until host verification changes it.

# Part B — Trace scope and privacy

## B1. Scope

Trace policy covers the complete causal graph:

```text
raw turn
Recipe 0–8 artifacts
all learned calls
all repair attempts
all re-entry slices
all tool/evidence receipts
Persistence transactions
Completion
Result/publication
cross-turn lineage/back-and-forth references
```

## B2. Four trace/training domains

### TRACE INDEX
Long-lived low-content metadata:

```text
trace/call/turn IDs
recipe/mode/runtime identities
schema/AAE/InferenceProfile hashes
validation/repair metrics
timings/tokens
raw trace availability flag
training status
deletion tombstone state
```

### SECURE RAW TRACE
Exact forensic packet/output data. Sensitive by definition.

Prototype requirements:

```text
encrypted at rest
owner/debug authority only
no plaintext mirror log
finite default retention (prototype default 30 days)
explicit PIN can extend retention
```

### TRAINING CANDIDATE QUARANTINE
A separate copy created only by explicit extraction. Copy only fields needed for the target specialist. Sanitization/redaction happens on this copy, not by corrupting the exact forensic source.

### TRAINING_APPROVED
Only explicit review/host authorization can promote candidate data. Runtime/model/validation success cannot self-promote.

## B3. Secret minimization

Where credentials/tokens/passwords need not be model-visible, replace them before AAE construction with host-held protected references such as `<SECRET_REF:S003>`. What the model never sees, the trace need not retain.

## B4. Held-out firewall

Frozen qualification fixtures are permanently classified:

```text
NEVER_TRAIN
```

Training export rejects them regardless of later convenience.

## B5. Dataset manifest

Approved exports record:

```text
dataset_export_uuid
target adapter/mode
source trace refs
sanitization profile version
record hashes
review/approval identity and time
heldout_exclusion_check
manifest hash
```

Training consumes manifests, never arbitrary trace DB queries.

## B6. Deletion

Deleting a raw trace destroys its encrypted payload and leaves a minimal safe tombstone/index as policy permits. Untrained candidate/export copies cascade-delete/revoke. If already-trained weights consumed the record, lineage records that fact; deleting JSON cannot truthfully claim to erase influence already embedded in weights.

## B7. Trace is not memory

Normal models cannot retrieve arbitrary diagnostic traces merely because they exist. Any content must cross an explicit host-owned transition into transcript, Context, semantic memory, or approved training data.

## B8. Human-readable view

The authoritative canonical machine trace deterministically renders the readable AAE/audit view. Do not store a second uncontrolled plaintext duplicate solely for readability.
# A.R.C.A.D.I.A. v0.1 — Performance, Deterministic Fast Path, and Toggle

# 1. Problem

The R3 five-slice trace demonstrated severe call amplification: 13 learned calls for an exact literal response and 27 for a research+remember path. Compartmentalization remains valuable, but invoking a model for mechanically provable work adds latency, failure probability, and adapter churn without adding semantic value.

# 2. DeterministicPathGate

Before normal learned work, the host may match a small allowlisted grammar of **syntactically provable** operations.

Initial v0.1 D0 rule:

```text
EXACT_LITERAL_RESPONSE_V1
```

Example:

```text
Reply exactly: Ready.
```

The host already possesses the required bytes. It may create the normal authoritative artifact lineage and publish under a deterministic proof rule with zero learned calls.

Do not expand the allowlist casually. File operations or other commands may receive deterministic grammars later only after their authority/ambiguity rules are separately proven.

# 3. Model-necessity gate inside recipes

Even when a turn did not enter at D0, each recipe asks:

> Is semantic judgment actually required for this stage, or is the required artifact/transition fully derivable from validated host artifacts?

If fully derivable:

```text
MODEL SEES NOTHING — HOST-ONLY PASS
```

The resulting artifact still carries normal IDs, provenance, hashes, and traceability.

# 4. Fast-path toggle

Config:

```text
fast_path_enabled: true | false
```

Rules:

- snapshotted at turn start;
- immutable for that turn;
- recorded in turn/performance receipt;
- OFF forces ordinary learned-eligible semantic pipeline behavior;
- OFF is supported for testing **and normal use**;
- host safety, schema, execution, persistence, and truth gates remain mandatory either way;
- optional shadow field may record `would_have_fast_pathed=true` without taking it.

Recommended qualification default:

```text
fast_path_enabled = false
```

Recommended normal prototype default after D0 equivalence tests pass may be true, but remains user/operator configurable.

# 5. Required telemetry

```text
fast_path_enabled
fast_path_taken
proof_rule_id
fast_path_bypass_reason
would_have_fast_pathed
path_class
learned_call_count
first_pass_success_count
repair_count
adapter loads/evictions/hits
input/output tokens
model latency
adapter transition latency
end_to_end_latency
```

# 6. Path classes

```text
D0 DETERMINISTIC
D1 BOUNDED_RESOLUTION
D2 NORMAL_SEMANTIC
D3 EXTERNAL_WORK
D4 REENTRY_PERSISTENCE_COMPLEX
```

Performance budgets are measured per class. Do not compare a literal echo to research+memory as if they should have equal cost.

# 7. What optimization may not do

Performance work may remove unnecessary model calls. It may not merge specialist authority boundaries merely to reduce latency without a new explicit architecture/qualification decision.

# 8. Failure rule

Fast path fails open to the normal pipeline in the routing sense:

```text
no exact allowlisted proof -> normal A.R.C.A.D.I.A.
```

It never guesses to remain fast.
