# Phase A Item 10 — Exact-Runtime Trust Registry

Date: 2026-08-30
Standing: **PASS — item complete; Gate A remains open**

## Authority implemented

- `RuntimeQualificationIdentity` freezes the base-model hash, physical-adapter
  UUID/hash or explicit `BASE_ONLY` marker, pinned llama.cpp build, ModelRuntime,
  AdapterManager, SpecialistInvoker, AAE and logical-mode contracts, input/output
  schemas, host validator, and mode-specific inference-profile ID/hash. Changing
  any output-affecting field creates a different identity hash and a new T0
  qualification target.
- `QualificationTarget` joins exactly one logical specialist mode to one exact
  runtime identity and its configured minimum runtime tier. Two modes sharing a
  physical LoRA remain independent targets and never inherit each other's trust.
- Earned trust follows the frozen sequential ladder: T0 unqualified, T1 schema/
  fixture competence, T2 held-out semantic competence, T3 adversarial/composition
  competence, T4 shadow runtime, T5 limited authority, and T6 production
  authorization. Promotions cannot skip a tier and require immutable evidence
  tied to the target's exact runtime identity.
- Operational authorization is separate from earned qualification. The requested
  use, exact logical-mode/runtime target, target minimum tier, earned tier,
  standing, and Config V1 environment authority ceiling must all permit dispatch.
- `BASE_ONLY` is explicitly limited to qualification use even if evaluation
  evidence reaches a higher tier. There is no fallback resolver or alternate-
  target selection path, so an adapter/profile/version failure cannot silently
  route through base-only or a previous physical identity.
- Known failing modes can be explicitly blocked with reviewer/report evidence.
  Blocking prevents operational use without poisoning runtime health and still
  permits controlled qualification. Reset requires a second explicit audited
  transition, returns the exact target to T0, and discards all previously earned
  current authority so qualification must be repeated.
- Registration, promotion, blocking, and reset are immutable chronological
  revisions in one versioned SHA-256 event chain. Updates require both the current
  global head and exact target revision. Replay verifies target immutability,
  unique mode/runtime bindings, sequential tiers/revisions, evidence identity and
  chronology, globally single-use transition evidence, hashes, ordering, and
  predecessor continuity.
- The registry performs deterministic authorization decisions only. Adapter
  lifecycle/health, inference dispatch, evidence storage durability, evaluation
  execution, and T4–T6 promotion policy remain with their later frozen owners.

## Evidence

Commands: `check.bat` (through `check_phase0.bat`) and `check_phase0.bat`

```text
286 tests passed
Ruff: PASS
strict MyPy: PASS (15 source files)
Phase 0 authority, dependency, model, llama.cpp, CUDA, and runtime hashes: PASS
```

The 27 trust-registry tests cover Config V1 policy binding, canonical hashes,
strict adapter/base-only identities, all output-affecting identity fields,
immutable targets, duplicate binding rejection, shared-LoRA logical-mode
isolation, changed-profile T0 reset, exact and sequential promotion evidence,
future-dated evidence rejection, T0–T6 use gates, target minimums, environment
ceilings, BASE_ONLY qualification-only behavior, missing-mode/identity denial,
block/reset/requalification, evidence UUID single use, optimistic concurrency,
canonical serialization, hash chaining, event reorder/deletion/time/content
tampering, and immutable dataclasses.

Gate A remains open for authority-separated SQLite connection, migrations, and
repositories. The next exact-order item is `storage/connection.py`.
