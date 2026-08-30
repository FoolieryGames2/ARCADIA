# ARCADIA Operating Status

Updated: 2026-08-30

## North star

Build a truth-preserving agent runtime whose learned specialists are compartmentalized behind deterministic, auditable host contracts.

## Verified

- Git repository initialized at the workspace root.
- Initial workspace checkpoint committed and published to `FoolieryGames2/ARCADIA` on GitHub.
- Local baseline: Python `3.13.7`, SQLite `3.50.4`, and an in-memory FTS5 table creation test passes.
- Project host environment pinned to CPython `3.12` with resolved dependencies in `requirements.lock`.
- Re-runnable Windows bootstrap passes environment, unit-test, lint, and strict type-check gates.
- The v0.1 architecture and implementation order are frozen.
- Documentation/static consolidation reports `PASS`.
- The canonical spine contains Recipes 0–8 with no collapsed stage.
- The core learned roster contains 15 physical adapters; Tool / Execution is host-only.
- Existing checkpoint ZIPs preserve both the canonical docs and Obsidian vault forms.
- Phase 0 immutable input manifest reproduces the authority, dependency, model,
  llama.cpp source, CUDA toolchain, and native runtime hashes.
- Pinned llama.cpp CUDA build passes 43/43 upstream tests.
- Pinned Qwen2.5 3B Q4_K_M smoke run offloads 37/37 layers to the RTX 2060 and exits cleanly.

## Not yet verified

- `SpecialistInvoker` real-runtime enforcement
- LoRA load/apply/isolation behavior
- Safe HOT adapter ceiling and A/B/A lifecycle behavior
- Logical specialist qualification beyond T0

## Active gate: Phase A1 — AAE Contract Registry and canonical serialization

Detailed execution tracking lives in `project/TODO_V0_1.md`. Items are marked complete only with reproducible evidence.

Gate 0 is closed by `evidence/phase0/PHASE0_GATE_REPORT.md`. The next work follows
the frozen Phase A module order: configuration, IDs, Canonical JSON V1, hashing,
artifact envelopes, ledgers, strict validation, budgets, trace index, trust
registry, and authority-separated SQLite repositories.

Configuration, identifier, Canonical JSON V1, SHA-256 hashing, Artifact Envelope
V1, additive technical turn ledger, and strict JSON Schema 2020-12 validation
are now implemented and evidenced. Schemas are immutable canonical snapshots;
every object schema rejects unknown properties, and deterministic reports bind
validation outcomes to exact schema and instance hashes. Final rendered AAE
extraction remains assigned to Phase A1. Learned-call repairs now use immutable
hash-bound source/mode/profile lineage, unique attempt UUIDs, exact failure
evidence, mandatory fresh-state flags, and a fail-closed per-call cap. The next
aggregate work-budget ledger now atomically enforces all Config V1 learned-call,
repair, token, expansion, work, retry, compensation, and discovery-depth limits
with explicit `BUDGET_EXHAUSTED` evidence and no partial grants. The next
privacy-minimized trace index now covers the full slice/causal graph with fixed
non-content metadata, permanent held-out classification, resolved parent/call
lineage, retention/pin/tombstone state, and immutable chronological event replay.
The exact-runtime trust registry now enforces independent logical-mode T0–T6
qualification, strict evidence-bound sequential promotion, explicit block/reset
transitions, operational authority ceilings, and qualification-only BASE_ONLY
behavior without fallback inheritance. The managed SQLite connection boundary
now confines the configured database to the workspace, verifies WAL/foreign
keys/busy timeout/FTS5, separates read-only access, and permits durable mutation
only inside its rollback-safe host transaction guard. The hash-verified migration
runner now installs the distinct Phase A transcript, artifact, and registry-
snapshot substrates atomically, refuses unmanaged or divergent history, and
deliberately defers semantic-memory schema installation to Phase C. The scoped
transcript repository now writes exact hashed user input and only an exact
published assistant Result, commits completion plus its monotonically increasing
transcript sequence atomically, recovers idempotently by turn UUID and Result
hash, and exposes only bounded completed-history and scoped FTS retrieval. Failed
drafts have no transcript write path. The artifact repository now accepts only complete,
verified Artifact Envelope V1 values; appends revisions under an optimistic exact
head; preserves stable project/turn/recipe/type/alias identity; verifies each
upstream basis UUID, revision, project, and hash before commit and again on read;
and detects revision gaps, time regression, relational drift, and durable envelope
tampering. It has no overwrite, deletion, transcript, semantic-memory, or file-
execution authority. The registry snapshot repository now seals canonical JSON
registry documents with host UUID, project, kind/version, all five identity axes,
creation time, and a hash over the complete unsigned snapshot. Kind/version is
immutable within a project; exact retries are idempotent; reads are project-
scoped and bounded; and the repository deliberately exposes no inferred latest/
active selection, overwrite, or deletion authority.

Phase A is closed by `evidence/phase_a/PHASE_A_GATE_REPORT.md`: all frozen core
and storage modules are implemented, all deterministic and authority-separation
checks pass without a model, and runtime authority remains T0. Phase A1 now has
the imported `AAE-REGISTRY-PRE-1` review candidate: 15 physical adapter semantic
identities, 20 independent logical modes, and one shared `GA-PRE-1` Global
Awareness block. All records are immutable, explicitly unfrozen,
`dispatch_enabled=False`, and fail `runtime_ready`; Recipe 4 remains host-only.
Vertical Slice 01 now makes `SCOPE_PROPOSAL` executable through the deterministic
boundary without a model: strict PRE-1 input/output schemas, semantic cross-field
and host-bound checks, structured AAE construction, role-separated Canonical JSON
messages, deterministic bracketed audit rendering, and final structured-message
`CALL_DATA` reparse/schema/byte/value/hash verification. Injection-shaped text and
fake AAE delimiters remain lower-trust data. The slice and registry remain
non-dispatchable/T0; the remaining 19 schemas, registry-wide origin/trust policy,
caps/projection, profiles, and training/runtime-source proof remain open.

## Next implementation gate

Phase A1: AAE Contract Registry, structured Global Awareness, strict schemas and
policies, canonical machine serialization, deterministic audit rendering, and
the final rendered `CALL_DATA` reparse/revalidation gate.

## Guardrail

The current status authorizes implementation and narrow spikes—not production trust, unreviewed trace training, or claims of runtime qualification.
