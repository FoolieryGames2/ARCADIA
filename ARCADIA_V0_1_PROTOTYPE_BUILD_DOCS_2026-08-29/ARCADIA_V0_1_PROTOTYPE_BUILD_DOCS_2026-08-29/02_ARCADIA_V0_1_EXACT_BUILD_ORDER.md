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
