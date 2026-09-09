# ARCADIA Operating Status

Updated: 2026-09-08

## North star

Build a truth-preserving agent runtime whose learned specialists are compartmentalized behind deterministic, auditable host contracts.

## Verified

- Git repository initialized at the workspace root.
- Initial workspace checkpoint committed and published to `FoolieryGames2/ARCADIA` on GitHub.
- Local baseline: Python `3.13.7`, SQLite `3.50.4`, and an in-memory FTS5 table creation test passes.
- Project host environment pinned to CPython `3.12` with resolved dependencies in `requirements.lock`.
- Re-runnable Windows bootstrap passes environment, unit-test, lint, and strict type-check gates.
- The full Recipe 0–8 v0.1 architecture is frozen by the verified 2026-09-04 handoff.
- Documentation/static consolidation reports `PASS`.
- The canonical spine contains Recipes 0–8 with no collapsed stage.
- The core learned roster contains 15 physical adapters; Tool / Execution is host-only.
- Existing checkpoint ZIPs preserve both the canonical docs and Obsidian vault forms.
- The historical Phase 0 immutable input manifest reproduces its authority, dependency, model,
  llama.cpp source, CUDA toolchain, and native runtime hashes.
- Pinned llama.cpp CUDA build passes 43/43 upstream tests.
- The historical Qwen2.5 3B Q4_K_M spike offloads 37/37 layers to the RTX 2060 and exits cleanly.
- `Qwen/Qwen3-4B-Instruct-2507` is the locked starting v0.1 foundation-model family.
- The exact b10796/Q4_K_M Qwen3 candidate is hash-pinned and passes a direct
  base-only CUDA smoke with 37/37 layers offloaded on the RTX 2060.
- The architecture authority's 28 declared payload hashes and exact 29-file tree reproduce.
- Recipe 0's one-next-turn continuation correction passes all five frozen scenarios.
- The bounded-history Recipe 0 controller and host-authoritative Recipe 1 Intent controller are
  integrated through one resident BASE_ONLY budget chain and stop honestly at
  `R2 Context NOT_IMPLEMENTED`.
- Interactive recipe prompts now retain one host-owned conversation UUID across resident
  restarts, expose `/new` for an explicit new conversation, and keep direct-mode prompts out of
  the recipe transcript.
- The local qualification CLI now exposes exact CALL_DATA, serialized model messages, raw
  untrusted output, metrics, budget transitions, and separate invoker/controller acceptance
  standing without changing recipe authority.
- Recipe 1 Term / Meaning now receives explicit call-local `TERM_n` / `REF_n` alias rules;
  a real T0 run returned `TERM_1`, which the host accepted and canonicalized to `T001`.
- A schema-valid R0 history request against zero completed exchanges now produces a typed,
  hash-bound non-fatal host correction, freezes truthful `UNRESOLVABLE_WITH_TRANSCRIPT`, and
  continues into R1 without attempting impossible retrieval.
- All 20 learned logical modes resolve strict PRE-1 input/output schemas with exact hash identities.
- All 20 learned modes bind unique PRE-1 context-projection policies; the shared
  boundary selects only complete schema-valid candidates using exact token counts
  and returns explicit incomplete/exhausted evidence without silent truncation.

## Not yet verified

- Full exact-runtime qualification through `SpecialistInvoker`
- `SpecialistInvoker` real-runtime enforcement
- LoRA load/apply/isolation behavior
- Safe HOT adapter ceiling and A/B/A lifecycle behavior
- Logical specialist qualification beyond T0
- A complete real-model resident BASE_ONLY R0 -> R1 run accepted by every frozen semantic gate
- Complete measured tuning profiles and recipe-owned projection candidates
- Training/runtime same-registry-source proof and joint A1 contract freeze

## Active gate: Phase A1 — AAE Contract Registry and canonical serialization

Detailed execution tracking lives in `project/TODO_V0_1.md`. Items are marked complete only with reproducible evidence.

The original Qwen2.5 Gate 0 is closed historically by
`evidence/phase0/PHASE0_GATE_REPORT.md`; that qualification does not transfer to
Qwen3. The next work follows
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
fake AAE delimiters remain lower-trust data. The reconciled PRE-08 checkpoint adds
strict `SCOPE_VALIDATION`, shared strict-shape, origin/trust, legal-reference,
vocabulary, repair-shape, and next-consumer policies, plus a separate deterministic
PRE-1 tuning-settings handler.

The 2026-09-04 architecture-freeze intake is evidenced by
`evidence/architecture/ARCHITECTURE_FREEZE_INTAKE_2026-09-04.md`. Its dedicated
Recipe 2–8 freezes and Recipe 0 continuation correction now govern conflicts with
older documents. The one-next-turn host-owned `AWAITING_USER_INPUT` correction is
now durable and passes all five required prefetch/retain/drop/expiry/journal cases.
The 18 formerly missing learned-mode schema pairs are implemented in recipe-owned
packages, yielding a total 20-mode exact-hash PRE-1 catalog. Recipe 4 remains
host-only. The full suite now passes 551 tests, Ruff, and strict MyPy over 62 source
files. The registry remains non-dispatchable/T0; complete measured settings,
context projection, registry-wide same-source proof, and joint freeze review remain
open. No runtime or adapter qualification is implied.

The Qwen3 base-only spike is evidenced by
`evidence/phase_a3/QWEN3_BASE_ONLY_SPIKE_2026-09-04.md`. It pins llama.cpp
`b10796` / `9a4843c`, the generated Q4_K_M candidate and runtime binary hashes,
and measures a clean 37/37-layer CUDA smoke. This is a T0 candidate checkpoint,
not `SpecialistInvoker`, LoRA, residency, or Gate A3 qualification.

The operator-facing base-model lab is evidenced by
`evidence/phase_a3/T0_BASE_MODEL_LAB_CLI_2026-09-04.md`. `run_arcadia.bat`
now opens a clean interactive or one-shot Qwen3 experience, with validated
checked-in defaults, atomic Git-ignored local overrides, exact runtime
verification, and explicit T0 metrics. A live CUDA call returned `ARCADIA READY`,
and the complete deterministic gate passes 580 tests plus Ruff and strict MyPy
over 66 source files. This direct lab boundary does not dispatch an AAE, attach
an adapter, persist transcript/memory, or inherit Recipe authority.

The next runtime slice is evidenced by
`evidence/phase_a3/RESIDENT_BASE_ONLY_R0_HARNESS_2026-09-04.md`. A reproducible
loopback-only llama.cpp server now keeps the pinned Qwen3 weights resident on
the RTX 2060 while every request receives fresh context and sampler state. The
measured cold loads ranged from 17.5–27.6 seconds; successive direct requests completed
in 0.35 and 0.20 seconds without another model load. The qualification-only
base invoker applies the structured AAE serializer, final `CALL_DATA` gate,
exact token reservation, schema-constrained generation, strict output and R0
semantic validation, and a hash-bound activation receipt. A live zero-history
Recipe 0 call passed in 2.55 seconds and produced a Conversation Packet, then
stopped explicitly at `R1 NOT_IMPLEMENTED`. The complete gate now passes 585
tests plus Ruff and strict MyPy over 69 source files. This is not the full
Recipe 0–8 pipeline or the complete A2 `SpecialistInvoker`/adapter lifecycle.

The interactive routing correction is evidenced by
`evidence/phase_a3/INTERACTIVE_RECIPE_MODE_CONTROL_2026-09-04.md`. Recipe mode
is now the checked-in default; `/mode`, `/recipe`, and `/direct` commands route
inside an already-running lab rather than becoming model prompt text. The
resident launcher also refuses an occupied loopback port instead of silently
adopting a stale process. This changes operator routing only; runtime authority
remains T0 and Recipe 1–8 remain unimplemented.

The shared A1 context-budget boundary is evidenced by
`evidence/phase_a1/A1_CONTEXT_BUDGET_PROJECTION_PRE1_REPORT.md`. The mechanism
and 20 policy identities are deterministic and tested, while checked-in numeric
limits remain intentionally unresolved pending measured InferenceProfiles.

The 2026-09-08 R0 -> R1 integration checkpoint is evidenced by
`evidence/phase_a1/R1_RESIDENT_BASE_ONLY_INTEGRATION_CHECKPOINT_2026-09-08.md`.
All three supplied patch hashes match their manifest, the patches apply to their exact
`5d7a911` base in order, and the pinned workstation gate passes 615 tests plus Ruff and
strict MyPy over 73 source files. Three bounded real resident attempts were rejected by
the frozen host gates for, respectively, truncated JSON, an illegal empty-transcript
history request, and an unauthorized Meaning local-key namespace. These are honest T0
qualification failures: the implementation checkpoint is integrated, but real-model
R0 -> R1 semantic qualification is not established and R2 remains unimplemented.

The follow-up conversation/regex and live-trace corrections are evidenced by
`evidence/phase_a1/R0_R1_CONVERSATION_SESSION_AND_REF_REGEX_CORRECTION_2026-09-08.md`
and `evidence/phase_a1/R0_R1_LIVE_QUALIFICATION_TRACE_CORRECTION_2026-09-08.md`.
The semantically equivalent llama.cpp-compatible REF regex required an explicit PRE-1 schema
hash-catalog refresh recorded in `D-0035`. The pinned workstation now passes 620 tests, Ruff,
and strict MyPy over 74 source files. A real resident trace passed R0 Scope Proposal and R1
Spell, then exposed a schema-valid Meaning response that the stronger Recipe 1 controller
correctly rejected for an unauthorized local-key namespace. Full real-model R0 -> R1 semantic
qualification therefore remains open.

The Recipe 1 local-key guidance correction is evidenced by
`evidence/phase_a1/R1_TERM_MEANING_LOCAL_KEY_AWARENESS_2026-09-08.md` and recorded in
`D-0036`. The exact model-facing Specialist Awareness now requires encounter-ordered
`TERM_n` / `REF_n` aliases, prohibits descriptive keys, and reserves authoritative `Txxx`
allocation for the host. A real resident run cleared the previously repeating Meaning-key
failure and advanced to Prompt Analyst, where an unrelated invented `S00` source reference
was rejected. Host validation remains fail-closed and full R0 -> R1 qualification remains open.

The zero-history continuation correction is evidenced by
`evidence/phase_a1/R0_ZERO_HISTORY_HOST_CONTINUATION_2026-09-08.md` and recorded in
`D-0037`. R0 now treats only a schema-valid history request with an authoritative completed
exchange count of zero as a logged non-fatal host continuation. It performs no retrieval,
preserves the model output and its hash, freezes `UNRESOLVABLE_WITH_TRANSCRIPT`, and advances
to R1. The pinned workstation gate passes 625 tests, Ruff, and strict MyPy over 74 source
files. This does not broaden learned authority or establish real-model R0 -> R1 qualification.

## Next implementation gate

Phase A1: AAE Contract Registry, structured Global Awareness, strict schemas and
policies, canonical machine serialization, deterministic audit rendering, and
the final rendered `CALL_DATA` reparse/revalidation gate.

## Guardrail

The current status authorizes implementation and narrow spikes—not production trust, unreviewed trace training, or claims of runtime qualification.
