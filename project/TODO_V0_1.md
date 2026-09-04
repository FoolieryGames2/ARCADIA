# ARCADIA v0.1 Execution Ledger

Updated: 2026-09-04

Authority: `architecture/v0.1/freeze-2026-09-04/`, then the 2026-08-29 exact build order where non-conflicting

Current standing: **Gate A passed / Phase A1 active — PRE_VERSION registry / runtime authority T0**

This is the live implementation ledger, not a replacement for the frozen build authority.
When this ledger and the canonical documents disagree, the canonical documents win.

## Honest status rules

- `[ ]` — not demonstrated.
- `[x]` — demonstrated with reproducible evidence.
- A component is not complete merely because code exists.
- A phase gate closes only when every required behavior and its tests pass.
- Test-double success is not real-runtime qualification.
- Documentation/static validation is not runtime qualification.
- Execution success is not semantic success.
- Missing certainty remains missing certainty; uncertain side effects become `OUTCOME_UNKNOWN`.
- Qualification belongs to an exact immutable runtime identity, never to a specialist name alone.

## Evidence index

| ID | Evidence | Standing |
|---|---|---|
| E-0001 | GitHub `main` initial workspace checkpoint | PASS |
| E-0002 | `setup.bat` clean/repeat bootstrap | PASS |
| E-0003 | `arcadia doctor`: CPython 3.12 + SQLite FTS5 + host packages | PASS |
| E-0004 | Current unit, Ruff, and strict MyPy gates | PASS |
| E-0005 | Canonical document consolidation validation report | PASS — docs only |
| E-0006 | `manifests/phase0_inputs.json` plus `scripts/verify_phase0.py` | PASS |
| E-0007 | `evidence/phase0/PHASE0_GATE_REPORT.md`: native build, 43/43 tests, GPU smoke | PASS — Gate 0 only |
| E-0008 | `evidence/phase_a/ITEM1_CONFIG_IDS.md`: strict Config V1 and scoped host IDs | PASS — Phase A item 1 |
| E-0009 | `evidence/phase_a/ITEM2_CANONICAL_JSON.md`: Canonical JSON V1 and strict decoding | PASS — Phase A item 2 |
| E-0010 | `evidence/phase_a/ITEM3_HASHING.md`: typed SHA-256 identity and exact/canonical hashing | PASS — Phase A item 3 |
| E-0011 | `evidence/phase_a/ITEM4_ARTIFACT_ENVELOPE.md`: immutable versioned artifact envelope | PASS — Phase A item 4 |
| E-0012 | `evidence/phase_a/ITEM5_LEDGER.md`: additive hash-chained technical turn ledger | PASS — Phase A item 5 |
| E-0013 | `evidence/phase_a/ITEM6_VALIDATION.md`: strict JSON Schema 2020-12 boundary | PASS — Phase A item 6 |
| E-0014 | `evidence/phase_a/ITEM7_REPAIR_POLICY.md`: bounded immutable learned-call repair policy | PASS — Phase A item 7 |
| E-0015 | `evidence/phase_a/ITEM8_WORK_BUDGET.md`: aggregate immutable work-budget ledger | PASS — Phase A item 8 |
| E-0016 | `evidence/phase_a/ITEM9_TRACE_INDEX.md`: privacy-minimized immutable trace index | PASS — Phase A item 9 |
| E-0017 | `evidence/phase_a/ITEM10_TRUST_REGISTRY.md`: exact-runtime per-mode trust and authority registry | PASS — Phase A item 10 |
| E-0018 | `evidence/phase_a/ITEM11_STORAGE_CONNECTION.md`: managed workspace-contained SQLite connection boundary | PASS — Phase A item 11 |
| E-0019 | `evidence/phase_a/ITEM12_STORAGE_MIGRATIONS.md`: atomic hash-verified Phase A SQLite migrations | PASS — Phase A item 12 |
| E-0020 | `evidence/phase_a/ITEM13_TRANSCRIPT_REPOSITORY.md`: scoped exact transcript lifecycle and bounded history retrieval | PASS — Phase A item 13 |
| E-0021 | `evidence/phase_a/ITEM14_ARTIFACT_REPOSITORY.md`: immutable scoped technical artifact revision repository | PASS — Phase A item 14 |
| E-0022 | `evidence/phase_a/ITEM15_REGISTRY_SNAPSHOTS.md`: immutable identity-bound registry snapshot repository | PASS — Phase A item 15 |
| E-0023 | `evidence/phase_a/PHASE_A_GATE_REPORT.md`: complete deterministic foundation and authority-separation review | PASS — Gate A |
| E-0024 | `evidence/phase_a1/AAE_REGISTRY_PRE_VERSION_REPORT.md`: 15-adapter/20-mode AAE registry review candidate | PASS — PRE_VERSION only; not dispatchable |
| E-0025 | `evidence/phase_a1/A1_VERTICAL_SLICE_01_SCOPE_PROPOSAL_REPORT.md`: strict Recipe 0 schema/serializer/CALL_DATA-gate golden slice | PASS — Slice 01 only; Gate A1 open |
| E-0026 | `evidence/phase_a1/A1_PRE08_HANDOFF_RECONCILIATION_REPORT.md`: reconciled PRE-08 R0 schema/policy/settings checkpoint | PASS — PRE_VERSION only; Gate A1 open |
| E-0027 | `evidence/architecture/ARCHITECTURE_FREEZE_INTAKE_2026-09-04.md`: exact full Recipe 0–8 architecture authority intake | PASS — architecture only; implementation/runtime open |
| E-0028 | `evidence/phase_a1/A1_R0_OPEN_CONTINUATION_ARCHITECTURE_DELTA.md`: durable one-next-turn cue, exact prior-exchange prefetch/drop, and five frozen scenarios | PASS — PRE-1 host correction; Gate A1 open |
| E-0029 | `evidence/phase_a1/A1_ALL_LEARNED_MODE_SCHEMAS_PRE1_REPORT.md`: all 20 strict schema pairs and exact hash manifest | PASS — PRE-1 contracts; Gate A1 open |
| E-0030 | `evidence/phase_a3/QWEN3_BASE_ONLY_SPIKE_2026-09-04.md`: verified source, pinned CUDA build, immutable Q4_K_M candidate, and 37/37-layer base-only smoke | PASS — candidate smoke only; Gate A3 open / T0 |
| E-0031 | `evidence/phase_a1/A1_CONTEXT_BUDGET_PROJECTION_PRE1_REPORT.md`: whole-candidate exact-token projection, structural limits, explicit incomplete/exhausted standings, and 20 policy identities | PASS — PRE-1 boundary; Gate A1 open / T0 |

Add evidence here before changing a phase or qualification standing.

---

## Phase 0 — Freeze build inputs

- [x] Commit and publish the v0.1 documentation/workspace checkpoint. Evidence: E-0001.
- [x] Pin CPython and deterministic host dependencies. Evidence: `.python-version`, `pyproject.toml`, `requirements.lock`, E-0002.
- [x] Require and verify SQLite FTS5 in the project environment. Evidence: `configs/runtime.toml`, E-0003.
- [x] Select the initial base GGUF and record URL, license, size, quantization, and SHA-256. Evidence: E-0006.
- [x] Pin the exact llama.cpp repository commit. Evidence: E-0006.
- [x] Pin llama.cpp build options, compiler/toolkit identities, and resulting library hash. Evidence: E-0006, E-0007.
- [x] Create one versioned runtime configuration source. Evidence: `configs/runtime.toml`.
- [x] Record a reproducible Phase 0 source manifest. Evidence: E-0006.
- [x] Close Gate 0: no unresolved contradiction blocks the narrow runtime spike. Evidence: E-0007.

The original Gate 0 evidence remains valid for its exact historical Qwen2.5 runtime
identity. The 2026-09-04 authority supersedes that model as the active v0.1 family;
the Qwen3 deployment identity must earn separate A3 evidence.

### Immediate Phase 0 decisions

- [x] Choose Qwen2.5-3B-Instruct Q4_K_M for the RTX 2060 6 GB qualification spike. Evidence: E-0006.
- [x] Select the pinned CUDA source-build strategy. Evidence: E-0006, E-0007.
- [x] Install and pin the native build prerequisites. Evidence: E-0007.
- [x] Define model artifact download and hash verification. Adapter import remains Phase K work. Evidence: E-0006.
- [x] Import and hash-freeze the full Recipe 0–8 architecture authority. Evidence: E-0027.
- [x] Lock `Qwen/Qwen3-4B-Instruct-2507` as the starting model family without inheriting Qwen2.5 qualification. Evidence: E-0027.
- [x] Select and hash an exact Qwen3 GGUF deployment candidate through a narrow A3 base-only measurement. Evidence: E-0030. Full A3 qualification remains open.
- [ ] Pin and qualify the exact Qwen3-compatible llama.cpp build/runtime identity.

---

## Phase A — Shared deterministic foundation

### Core

- [x] `core/config.py` — strict immutable Config V1. Evidence: E-0008.
- [x] `core/ids.py` — host UUIDs and scoped readable aliases. Evidence: E-0008.
- [x] `core/canonical_json.py` — Canonical JSON V1 and strict decoder. Evidence: E-0009.
- [x] `core/hashing.py` — typed SHA-256 identity, exact-byte hashing, and verification. Evidence: E-0010.
- [x] `core/artifact_envelope.py` — immutable versioned payload/provenance envelope. Evidence: E-0011.
- [x] `core/ledger.py` — immutable additive technical turn ledger and replay. Evidence: E-0012.
- [x] `core/validation.py` — strict immutable Draft 2020-12 schema boundary. Evidence: E-0013.
- [x] `core/repair_policy.py` — bounded immutable repair authorization and lineage. Evidence: E-0014.
- [x] `core/work_budget.py` — aggregate atomic work/token authorization ledger. Evidence: E-0015.
- [x] `core/trace_index.py` — privacy-minimized trace lineage and tombstone index. Evidence: E-0016.
- [x] `core/trust_registry.py` — exact-runtime, per-logical-mode qualification and authority routing. Evidence: E-0017.

### Storage

- [x] `storage/connection.py` — verified WAL/foreign-key/FTS5 connections and rollback-safe transaction authority. Evidence: E-0018.
- [x] `storage/migrations.py` — immutable forward-only catalog and atomic foundation schema. Evidence: E-0019.
- [x] `storage/transcript_repository.py` — scoped exact transcript commits, recovery identity, and bounded history/FTS reads. Evidence: E-0020.
- [x] `storage/artifact_repository.py` — immutable envelope revisions, optimistic heads, and exact verified basis refs. Evidence: E-0021.
- [x] `storage/registry_snapshots.py` — immutable kind/version snapshots bound to all runtime identity axes. Evidence: E-0022.

### Gate A evidence

- [x] UUIDs remain host authority. Evidence: E-0008.
- [x] Human-readable aliases are scoped and non-authoritative. Evidence: E-0008.
- [x] Canonical JSON V1 is deterministic. Evidence: E-0009.
- [x] Strict decoder rejects duplicate keys, non-finite values, and trailing content. Evidence: E-0009.
- [x] JSON Schema 2020-12 validation is enforced. Evidence: E-0013.
- [x] SQLite WAL, foreign keys, busy timeout, and rollback are tested. Evidence: E-0018, E-0019.
- [x] Transcript and semantic-memory authorities remain separate. Evidence: E-0019, E-0020, E-0021.
- [x] Aggregate call/work/re-entry/repair budgets exist. Evidence: E-0014, E-0015.
- [x] Gate A deterministic test suite passes without a model. Evidence: E-0023.

---

## Phase A1 — AAE registry and canonical serialization

- [x] Create the machine-readable AAE Contract Registry pre-version candidate. Evidence: E-0024. Freeze review remains open.
- [x] Create shared Global Awareness pre-version definitions. Evidence: E-0024. Freeze review remains open.
- [x] Create strict input/output schemas and policy registries for all 20 learned modes. Evidence: E-0026, E-0029. PRE-1 joint freeze remains open.
- [x] Implement canonical machine serializer. Evidence: E-0025.
- [x] Implement deterministic human audit renderer from the same source object. Evidence: E-0025.
- [x] Implement final structured-message `CALL_DATA` reparse/revalidation gate. Evidence: E-0025.
- [x] Structurally separate authority instructions from untrusted data. Evidence: E-0025.
- [x] Add instruction-impersonation/adversarial fixtures for Slice 01. Evidence: E-0025. Registry-wide coverage remains open.
- [x] Add deterministic context-budget projection with no silent truncation. Evidence: E-0031. Measured final limits remain unresolved.
- [ ] Supply recipe-owned semantically sufficient projection-candidate builders as each controller is implemented.
- [ ] Prove training and runtime consume the same registry source.
- [x] Prove schema-less AAE preparation/pre-dispatch is impossible for Slice 01 and schema catalog resolution is total for all 20 modes. Evidence: E-0025, E-0029. Registry-wide dispatch remains disabled.
- [x] Implement the frozen Recipe 0 one-next-turn `AWAITING_USER_INPUT` continuation correction. Evidence: E-0028.
- [ ] Close Gate A1.

---

## Phase A2 — Runtime boundary with test doubles

- [ ] Implement `ModelRuntime` test double.
- [ ] Implement `AdapterManager` lifecycle: COLD / READY / HOT / STAGING / ACTIVE.
- [ ] Implement independent HEALTHY / QUARANTINED / POISONED health axis.
- [ ] Implement process epoch and handle generation.
- [ ] Implement atomic `ensure_hot_and_acquire()`.
- [ ] Implement linear one-time lease release and stale-release rejection.
- [ ] Implement load-before-evict transactional replacement.
- [ ] Implement hard and expiring/generation-bound soft protection.
- [ ] Implement fresh context and sampler per attempt.
- [ ] Implement immutable mode-specific `InferenceProfile` hashes.
- [ ] Implement controlled POISONED restart semantics.
- [ ] Run race/failure tests against a 100-entry synthetic registry.
- [ ] Force staging-load failure without changing the committed HOT set.
- [ ] Close Gate A2-TD.

---

## Phase A3 — Real pinned GGUF/LoRA spike

- [x] Build/load the exact pinned libllama identity in direct BASE_ONLY_TEST_MODE. Evidence: E-0030. `SpecialistInvoker` and adapter qualification remain open.
- [ ] Keep one pinned base GGUF resident.
- [ ] Run BASE_ONLY_TEST_MODE through the real `SpecialistInvoker`.
- [ ] Load a small pinned LoRA set.
- [ ] Run A/B/A isolation using fresh contexts and samplers.
- [ ] Run load/apply/infer/free soak.
- [ ] Measure RAM/VRAM baseline, deltas, peak, and post-free behavior.
- [ ] Measure a safe HOT ceiling with one STAGING slot and inference reserve.
- [ ] Force full-pool load failure and preserve the old committed HOT set.
- [ ] Test all-leased and all-hard-pinned exhaustion.
- [ ] Test soft-protection expiry and current-demand override.
- [ ] Inject lifecycle shutdown/failure boundaries.
- [ ] Prove uncertain cleanup POISONs the domain and changes process epoch after restart.
- [ ] Record activation receipts and timing distributions.
- [ ] Close Gate A3; do not infer broader specialist qualification.

---

## Phase B — Recipe 0 Conversation Resolver + Recipe 1 Intent

- [ ] Build Conversation Resolver.
- [ ] Build Spell specialist.
- [ ] Build Term / Meaning specialist.
- [ ] Build Prompt Analyst.
- [ ] Build Intent Organizer.
- [ ] Build Conversational Howard Intent-comment mode.
- [ ] Pass zero-history, targeted-history, ambiguity, control-signal, exact-literal, and immutable-Rxxx tests.
- [ ] Close Gate B.

## Phase C — Persistence Host skeleton

- [ ] Install semantic-memory SQLite migration.
- [ ] Implement semantic read repository and `memory_commit_seq`.
- [ ] Implement PROVISIONAL standing and compensation lineage.
- [ ] Implement pre-Context provisional-review gate.
- [ ] Record PRC success in the same transaction.
- [ ] Prove crash-safe provisional state is excluded from clean Context.
- [ ] Close Gate C.

## Phase D — Recipe 2 Context

- [ ] Build router/split library and bounded packet projection.
- [ ] Build semantic retrieval and Evidence Specialist.
- [ ] Build Howard Context-lane modes.
- [ ] Build promotion transaction and Context snapshot.
- [ ] Add projection-recall metrics and SourcePolicy metadata.
- [ ] Preserve conflict/unresolved standing and prevent Intent mutation.
- [ ] Close Gate D.

## Phase E — Recipe 3 Decision

- [ ] Build Requirement Assessor and Plan Composer.
- [ ] Implement host-owned IDs, graph legality, capability gates, side-effect classes, budgets, and re-entry scope.
- [ ] Prove no-work cases create no compulsory tool work.
- [ ] Prove blocked requirements create no executable work.
- [ ] Close Gate E.

## Phase F — Recipe 4 Execution + OperationJournal

- [ ] Build request compiler, capability registry, and scheduler.
- [ ] Build durable OperationJournal and immutable receipts.
- [ ] Implement per-capability idempotency, verification, recovery, and compensation policies.
- [ ] Keep publication-independent receipt commits.
- [ ] Prove compilation failure creates no false receipt.
- [ ] Prove uncertain side effects become `OUTCOME_UNKNOWN` and are not blindly retried after restart.
- [ ] Close Gate F.

## Phase G — Recipe 5 Reconciliation + SourcePolicyRegistry

- [ ] Build deterministic evidence normalization, hashing, deduplication, freshness, and authority preprocessing.
- [ ] Build claim-specific SourcePolicyRegistry.
- [ ] Build Evidence Reconciler and Reconciliation Composer.
- [ ] Preserve disagreement, missing evidence, and legitimate discovery.
- [ ] Route material discovery through bounded Context re-entry.
- [ ] Close Gate G.

## Phase H — Recipe 6 learned Persistence

- [ ] Build Persistence Assessor and Persistence Composer.
- [ ] Keep all IDs, SQL, transactions, compensation, and PRC authority in the host.
- [ ] Enforce clean/PROVISIONAL/superseded visibility policies.
- [ ] Prove model output cannot directly mutate SQLite.
- [ ] Close Gate H.

## Phase I — Recipe 7 Completion

- [ ] Build Completion Assessor and Completion Composer.
- [ ] Require terminal standing for every immutable Rxxx.
- [ ] Preserve partial, blocked, failed, and unknown standing without cleanup into false success.
- [ ] Prevent Completion from creating work or rewriting upstream truth.
- [ ] Close Gate I.

## Phase J — Recipe 8 Result + PublicationJournal

- [ ] Build per-requirement Howard comments and bounded final fan-in.
- [ ] Enforce literal locks and disclosure coverage.
- [ ] Build PublicationJournal and transcript commit separation.
- [ ] Recover publication using `turn_uuid + result_hash` without regenerating semantic Result.
- [ ] Prove mixed partial/blocker truth remains explicit.
- [ ] Close Gate J.

---

## Phase K — Specialist qualification progression

For every logical specialist mode, track an exact runtime identity through:

- [ ] Base-GGUF frozen-suite baseline recorded separately.
- [ ] T1 — schema/fixture competence.
- [ ] T2 — held-out semantic competence.
- [ ] T3 — adversarial/composition competence.
- [ ] T4 — shadow runtime.
- [ ] T5 — limited authority.
- [ ] T6 — production authorization.
- [ ] Permanently mark held-out material `NEVER_TRAIN`.
- [ ] Prove base/adapter comparisons share fixture, AAE, schema, profile, and seed policy.

Maintain a separate qualification row per logical mode and immutable runtime identity; never check these boxes globally based on one adapter.

---

## Phase L — Full-spine v0.1 stress/demo

- [ ] Exact-literal deterministic path with fast path ON.
- [ ] Same exact-literal case with fast path OFF.
- [ ] Zero-history semantic answer.
- [ ] History-dependent reference resolution.
- [ ] Durable semantic-memory lookup.
- [ ] Search success with semantic failure.
- [ ] Latest/current source conflict.
- [ ] Material discovery with Context re-entry.
- [ ] Verified Save File.
- [ ] Save timeout resulting in `OUTCOME_UNKNOWN`.
- [ ] Crash after side effect but before receipt.
- [ ] Explicit remember producing PROVISIONAL state.
- [ ] Next-turn affirmation.
- [ ] Next-turn neutral stabilization.
- [ ] Next-turn correction/undo compensation.
- [ ] Memory Inspector correction.
- [ ] Persistence commit followed by publication failure.
- [ ] Mixed partial/blocker Result.
- [ ] Budget exhaustion with honest Completion.
- [ ] Full provenance replay.
- [ ] Trace deletion/candidate-cascade test.
- [ ] Training-export held-out rejection.
- [ ] Close Gate L.

Only after Gate L closes may v0.1 be called **implemented**. This does not imply that every specialist has earned T6.

---

## Current next actions

1. Implement the frozen Recipe 0 open-continuation schema delta and deterministic host fixtures.
2. Review and implement the five Recipe 1 strict schemas in frozen mode order.
3. Continue Recipe 2, Recipe 3, and Recipe 5–8 schemas without introducing Recipe 4 learned authority.
4. Complete deterministic context-budget projection and prove all 20 modes resolve from the same runtime/training registry source.
5. Build A2 with test doubles, then use A3 measurements to select the exact Qwen3 deployment identity and finish runtime-dependent settings/InferenceProfiles.
6. Keep runtime authority at T0 and Gate A1 open until its registry-wide integrity and freeze review pass.

## Change protocol

When work advances:

1. Add or update the test/evidence artifact.
2. Add its immutable reference to the Evidence index.
3. Check only the demonstrated item.
4. Update `project/STATUS.md` if a phase/gate standing changes.
5. Append consequential architectural changes to `project/DECISIONS.md`.
6. Commit the implementation, tests, ledger, and status together.
