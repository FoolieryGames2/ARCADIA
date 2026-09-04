# ARCADIA Decision Log

Append decisions. Keep prior entries intact; supersede them explicitly.

## D-0001 — Workspace authority boundary

- Date: 2026-08-29
- Status: accepted
- Decision: Keep the delivered v0.1 prototype bundle unchanged as canonical design authority. Use the workspace root for live implementation and operating records.
- Reason: This preserves the validated checkpoint while allowing implementation state to evolve visibly.

## D-0002 — Implementation root

- Date: 2026-08-29
- Status: accepted
- Decision: Place Python implementation under `src/arcadia/` and tests under `tests/`.
- Reason: A conventional package boundary supports deterministic testing and prevents working code from being mixed into the frozen documentation bundle.

## D-0003 — Python host baseline

- Date: 2026-08-29
- Status: accepted
- Decision: Pin the deterministic host development environment to CPython 3.12 and install it in the repository-local `.venv`.
- Reason: Python 3.12 is already installed on the workstation and has the safer native-package compatibility surface for the later Windows model-runtime spike than the current free-threaded Python 3.13 default.

## D-0004 — Separate host and model-runtime setup

- Date: 2026-08-29
- Status: accepted
- Decision: Make the host/test-double environment operational before installing libllama, CUDA build dependencies, models, or LoRAs.
- Reason: The frozen build order requires deterministic host gates before the real runtime spike, and runtime dependencies cannot be qualified until their exact source and build identities are pinned.

## D-0005 — Phase 0 native runtime identity

- Date: 2026-08-29
- Status: accepted
- Decision: Pin Qwen2.5-3B-Instruct Q4_K_M revision `7dabda4d13d513e3e842b20f0d435c732f172cbe`, llama.cpp commit `c9ca51c1f6b18427cde490c7c7eba11d87a96b2d`, CUDA 13.3.73, MSVC 19.44.35228, and compute capability 75 as the Phase 0 runtime identity.
- Reason: The exact model, source, compiler, toolkit, flags, and generated artifact hashes are now reproducible on the target RTX 2060 host.

## D-0006 — Resource-bounded native build

- Date: 2026-08-29
- Status: accepted
- Decision: Cap native build parallelism at two workers and include CUDA 13.3's `bin/x64` runtime directory in launch environments.
- Reason: Unbounded compilation on the 8 GB host caused missing-object linker races, and CUDA 13.3 stores required runtime DLLs in the architecture-specific directory.

## D-0007 — Disable the coupled upstream unified app

- Date: 2026-08-29
- Status: accepted
- Decision: Set `LLAMA_BUILD_APP=OFF` while retaining shared libraries, tests, examples, and non-server tools.
- Reason: At the pinned commit, the optional unified upstream app links `llama-server-impl` even when `LLAMA_BUILD_SERVER=OFF`. Disabling only that app preserves ARCADIA's required server-disabled boundary; ARCADIA's own CLI remains the planned interface.

## D-0008 — Config V1 and scoped alias representation

- Date: 2026-08-29
- Status: accepted
- Decision: Treat the Phase 0 `runtime.toml` as the seed of Config V1 and complete its frozen v0.1 shape before any recipe consumes it. Represent every authoritative identity as a canonical host UUID; represent readable IDs as `(scope UUID, declared alias kind, ordinal)` with namespace-specific display width.
- Reason: The system documents require one versioned configuration source, host-owned UUID authority, and scoped non-authoritative aliases. Completing the unused placeholder schema now avoids hidden recipe settings, while the structured alias identity prevents equal-looking `R001` values from colliding across turns and keeps `E001` evidence distinct from durable `E000001` semantic entities.

## D-0009 — Stable line endings for hashed text inputs

- Date: 2026-08-29
- Status: accepted
- Decision: Pin `requirements.lock` and `configs/runtime.toml` to UTF-8 LF through `.gitattributes` before hashing them in the Phase 0 manifest.
- Reason: Windows `core.autocrlf=true` changed the working-tree byte hash of `requirements.lock` during a branch switch without changing its logical content. Hash authority requires a stable byte representation across checkouts.

## D-0010 — Canonical JSON V1 byte profile

- Date: 2026-08-29
- Status: accepted
- Decision: Encode Canonical JSON V1 as UTF-8 with Unicode preserved, lexicographically sorted object keys, compact separators, no byte-order mark, and no trailing newline. Decode fail-closed for duplicate decoded keys, non-finite numbers (including finite-looking exponent overflow), trailing content, invalid UTF-8, lone Unicode surrogates, unsupported host values, and cyclic or excessively deep structures. Canonical-input validation requires exact byte-for-byte equality with the re-encoded form.
- Reason: The frozen AAE boundary defines deterministic `ensure_ascii=False`, sorted, compact JSON with non-finite values forbidden. Explicitly closing overflow and invalid-Unicode edge cases preserves that byte-level contract across host parsing and hashing without changing the architecture.

## D-0011 — Typed SHA-256 hash identity

- Date: 2026-08-29
- Status: accepted
- Decision: Represent host artifact digests canonically as `sha256:` followed by exactly 64 lowercase hexadecimal characters. Hash raw payloads as their exact bytes; hash text as strict UTF-8 without normalization; hash structured values only after Canonical JSON V1 encoding. Verification requires a typed digest and uses constant-time comparison.
- Reason: The frozen documents select Canonical JSON plus SHA-256 and use algorithm-tagged hash references throughout the pipeline. A single strict representation prevents algorithm ambiguity, case/whitespace aliases, accidental hashing of pretty-printed JSON, and silent loss of raw-versus-normalized provenance.

## D-0012 — Artifact Envelope V1 integrity boundary

- Date: 2026-08-29
- Status: accepted
- Decision: Define the common technical Artifact Envelope V1 with host artifact/project/turn UUIDs; locked Recipe 0–8 identity; artifact type and optional turn-scoped alias; positive revision; project, contract, schema, recipe, registry, and runtime identity versions; fixed UTC creation time; ordered immutable upstream basis references containing artifact UUID/revision/hash; an immutable Canonical JSON V1 payload; its content hash; and a whole-envelope hash. The whole-envelope hash covers every field except itself. Repository existence and recipe-specific payload semantics remain later validation/storage responsibilities.
- Reason: The frozen documents require every durable artifact to be versioned, hashable, traceable, and linked to upstream basis refs while preserving host ownership of identity and validation. Separating payload and envelope hashes detects both semantic-content and provenance/metadata tampering without collapsing recipe schemas into the shared layer.

## D-0013 — Additive technical turn ledger chain

- Date: 2026-08-29
- Status: accepted
- Decision: Represent the Phase A technical turn ledger as an immutable per-project/per-turn sequence of complete verified Artifact Envelope V1 values. Every append receives a host entry UUID, contiguous sequence, canonical UTC timestamp, predecessor hash, and entry hash over all entry fields except itself. Append requires the caller's expected current head; replay validates artifact integrity, scope, sequence, predecessor chain, uniqueness, revision ordering, nondecreasing time, count, and head. Appending returns a new snapshot and exposes no deletion or replacement operation.
- Reason: The frozen recipes require the root turn ledger to grow additively, preserve old artifacts and superseded history, support provenance/debug/replay, and remain separate from transcript and durable semantic memory. Hash chaining plus optimistic head matching makes accidental overwrite, stale concurrent append, reorder, and ordinary tamper visible while leaving transaction durability to the later repository layer.

## D-0014 — Strict Draft 2020-12 validation boundary

- Date: 2026-08-30
- Status: accepted
- Decision: Compile only strict JSON object schemas that declare the exact JSON Schema Draft 2020-12 dialect. Require every object-shaped schema reachable through structural and composition keywords to set `additionalProperties: false`. Snapshot schemas with Canonical JSON V1 and SHA-256; validate strict JSON host values without coercion or default mutation; assert declared known formats; and produce deterministic complete reports bound to schema and instance hashes. Reuse the same immutable compiled schema for host values and strictly decoded final text/bytes. Leave final AAE extraction to Phase A1 and semantic/reference legality to later validators.
- Reason: The frozen CALL_DATA hard gate requires strict schema validation both before serialization and after production-equivalent reparsing, with unknown properties, wrong types, enums, and declared bounds rejected. Immutable schema identity and deterministic reports make that gate replayable and auditable without collapsing later recipe or repository authority into the common validation layer.

## D-0015 — Immutable bounded learned-call repair lineage

- Date: 2026-08-30
- Status: accepted
- Decision: Represent repair as immutable authorization state scoped to one original learned-call UUID. Freeze the authoritative packet, specialist mode, and inference-profile ID/hash into one canonical hash-bound basis. Every repair receives a new host attempt UUID, contiguous ordinal and predecessor, the unchanged basis/policy hashes, and separately canonicalized and hashed copies of the prior invalid output and exact nonempty machine validation-error object. Enforce an exact configurable per-call repair cap, including zero, and expose fresh-context/fresh-sampler requirements as unconditional attempt invariants. Leave aggregate learned-call/token/work consumption to `core/work_budget.py` and actual fresh-state construction to the later runtime boundary.
- Reason: The frozen repair contract prohibits hidden authority expansion and requires the same authoritative source packet, mode, and profile; a new attempt UUID/trace; exact validation error; fresh context/sampler; and bounded aggregate attempts. Immutable lineage makes identity, ordering, predecessor, and content tampering detectable while keeping repair policy separate from inference execution, runtime health, and later recipe-specific failure standing.

## D-0016 — Atomic immutable aggregate work-budget ledger

- Date: 2026-08-30
- Status: accepted
- Decision: Freeze every Config V1 budget ceiling into one canonical hash-bound `BudgetLimits` snapshot and authorize work through an immutable append-only hash chain. Model grants atomically charge one learned call plus exact input tokens and a conservative reserved output allowance. Repair grants additionally charge a per-original-call repair count and must bind to the current typed repair-session head and a prior original model grant. Re-entry, history/Context expansion, Decision work, side-effect retry, and compensation are additive; Reconciliation discovery is a high-water depth bound. Require optimistic head matching, unique operation UUIDs, and all-or-nothing preflight. Represent overflow as machine-readable `BUDGET_EXHAUSTED` evidence and provide no reset or refund path.
- Reason: The frozen invariants require finite per-stage and aggregate model-attempt, repair, token, expansion, work, re-entry, retry, and compensation bounds; exhaustion must preserve accumulated truth and route toward honest Completion. Atomic grants prevent partial multi-budget consumption, prior-call binding prevents repairs from bypassing learned-call accounting, and immutable hash-chained history makes budget authority replayable without allowing later controllers to erase spent capacity.

## D-0017 — Fixed-field trace index and confirmed raw tombstones

- Date: 2026-08-30
- Status: accepted
- Decision: Keep the Phase A trace index strictly non-content by exposing only fixed identity, provenance, validation, repair, runtime-hash, numeric-telemetry, raw-availability, retention, training-classification, and tombstone fields. Represent full-slice and cross-turn lineage with typed prior-only trace/call references resolved during registration. Store lifecycle changes as immutable, chronological, policy-bound hash-chain events with optimistic head and record revisions. Represent raw trace only by secure-store UUID and payload hash; pin/unpin explicitly; record a deletion tombstone only through confirmation of the exact live raw UUID after external payload destruction. Initialize training state only as `NOT_SELECTED` or permanent `NEVER_TRAIN`; expose no candidate/approval/export transition in this runtime index.
- Reason: The frozen privacy lock permits durable low-content observability but forbids diagnostic traces from becoming shadow transcript, Context, semantic memory, or training data. Fixed fields prevent accidental prompt/output storage, prior-only references prevent dangling/cyclic trace lineage, confirmed tombstones avoid falsely claiming deletion, and the absence of approval transitions keeps runtime success from self-promoting data while later storage/trust/training components retain their own authority.

## D-0018 — Exact-runtime, per-logical-mode trust authority

- Date: 2026-08-30
- Status: accepted
- Decision: Bind earned trust to one immutable logical-mode plus complete runtime identity target. Require hash-bound evidence and strictly sequential T1–T6 promotion; never inherit qualification through a shared physical LoRA, previous adapter, or changed inference profile. Evaluate operational use separately against the requested authority class, mode minimum, earned tier, explicit blocked standing, and Config V1 environment ceiling. Keep BASE_ONLY qualification-only. Record registration, promotion, block, and reset-to-T0 as optimistic, immutable, chronological hash-chain events carrying explicit reviewer/report evidence for block/reset transitions.
- Reason: The frozen qualification contract makes exact runtime identity—not adapter filename—the unit of trust, prohibits silent BASE_ONLY fallback, and permits demos below T6 only when authority routing respects actual trust. Separating earned evidence from the operational ceiling prevents test success from raising deployment authority; explicit blocking/reset preserves known failures without conflating model quality with runtime health; and independent logical-mode records prevent a shared LoRA from laundering qualification across contracts.

## D-0019 — Managed SQLite transaction and connection authority

- Date: 2026-08-30
- Status: accepted
- Decision: Open only the Config V1 database beneath a resolved existing workspace root and verify WAL, foreign keys, configured busy timeout, NORMAL synchronization, and FTS5 on every connection. Expose read/write and URI/query-only read-only handles through a restricted wrapper. Make the wrapper's non-nestable managed transaction context the sole write boundary; use SQLite's authorizer to deny writes outside it and deny caller transaction control, PRAGMA changes, ATTACH, and DETACH. Return restricted cursors that do not expose the raw connection.
- Reason: The frozen Phase A gate requires WAL, foreign keys, busy timeout, rollback, FTS5, and distinct repository authority. Python's default connection/cursor API otherwise permits accidental statement-level autocommit, manual COMMIT, policy-changing PRAGMAs, or attachment of another database, each of which could bypass later Persistence atomicity and repository separation. Enforcing these mechanics at the common connection layer preserves the required transaction substrate without assigning schema or semantic authority before their frozen items.

## D-0020 — Atomic hashed Phase A migration catalog

- Date: 2026-08-30
- Status: accepted
- Decision: Represent SQLite schema history as an immutable, contiguous, Canonical-JSON-hashed migration catalog and accept an existing database only when its strict migration ledger is an exact prefix of that catalog. Apply ledger bootstrap and every pending single-statement migration in one managed `BEGIN IMMEDIATE` transaction. Establish four Phase A migrations for host metadata, transcript, artifact identity/revisions/links, and registry snapshots. Refuse nonempty unmanaged databases, divergent history, gaps, downgrades, and read-only or caller-owned transaction execution. Defer the carried-forward semantic-memory SQL to its explicitly assigned Phase C installation gate.
- Reason: The frozen documents require rollback-safe SQLite, distinct transcript/artifact/registry authorities in Phase A, and installation of semantic memory later in Phase C. Hashing the ordered SQL closes silent historical edits; prefix verification makes upgrades forward-only; one transaction prevents partially installed schema from claiming success; and refusing unmanaged files prevents ARCADIA from adopting an unrelated database. Splitting artifact identity from immutable revisions preserves revision history while retaining the parent `artifacts(artifact_uuid)` key required by the frozen future semantic-provenance schema.

## D-0021 — Exact transcript publication and bounded retrieval authority

- Date: 2026-08-30
- Status: accepted
- Decision: Extend the immutable migration catalog forward with a transcript-lifecycle migration; do not alter the four already evidenced migrations. Keep turn completion state, exact assistant publication identity, a monotonic transcript commit sequence, and a scoped FTS5 index in transcript-owned tables. Make `TranscriptRepository` project-scoped and append-only: accept exact user input, admit an assistant entry only when its bytes match the immutable published Result hash, atomically complete the turn and increment the sequence once, and make retry idempotent only for the same turn UUID plus Result hash. Return only completed exchanges through chronological recent reads (maximum 20) or escaped, conversation-scoped FTS reads (maximum 8 turns). Expose no failed-draft or generic transcript-entry write. Reject direct caller PRAGMA/control SQL before preparation while retaining SQLite authorizer enforcement for mutation, transaction, and database-scope boundaries, because FTS5 requires internal virtual-table PRAGMA operations.
- Reason: The frozen publication contract separates Result creation, transport, and transcript commit; requires the exact published surface response and stable recovery identity; excludes failed drafts from ordinary history; and gives Conversation Resolver only minimum-sufficient bounded transcript access. A forward migration preserves already hashed history, atomic completion prevents a published response from diverging from its standing or sequence, strict scope prevents cross-project/conversation retrieval, and distinguishing caller SQL from SQLite-owned FTS internals preserves both the storage authority boundary and required FTS5 behavior.

## D-0022 — Immutable optimistic technical artifact revisions

- Date: 2026-08-30
- Status: accepted
- Decision: Make `ArtifactRepository` a project-scoped append-only store whose only write value is a fully verified Artifact Envelope V1. New identities must begin at revision 1 from expected head 0; later revisions must advance the exact durable head contiguously, preserve project/turn/Recipe/type/scoped-alias identity, and never regress creation time. Exact retries are idempotent; changed content at an existing identity/revision conflicts. Every ordered upstream basis reference must already exist in the same project at the exact revision and envelope hash, and repository reads must reproduce canonical envelope bytes, relational columns, link order, revision continuity, and durable upstream hashes. Expose bounded turn/Recipe listing and exact/latest reads, but no overwrite, deletion, semantic-memory, transcript, or file-execution operation.
- Reason: The frozen contracts require durable technical artifacts to remain versioned, hashable, traceable, linked to exact upstream basis refs, and separate from all other retention domains. Optimistic contiguous appends prevent stale controllers from forking a revision line; exact-envelope revalidation prevents database columns from becoming an alternate source of truth; pre-existing basis enforcement makes causal references acyclic by construction; and immutable historical revisions preserve replay and supersession evidence without granting this repository authority to decide which semantic state is active.

## D-0023 — Identity-bound immutable registry snapshots

- Date: 2026-08-30
- Status: accepted
- Decision: Represent every stored runtime registry document as an immutable Canonical JSON object with a host snapshot UUID, project UUID, canonical registry kind and version, contract/schema/recipe/registry/runtime identity versions, canonical UTC creation time, and a typed SHA-256 hash over all of those fields plus the document. Bind each project/kind/version exactly once; permit only exact idempotent retry; provide exact UUID and kind/version resolution plus bounded chronological audit listing; and expose no generic latest, activation, overwrite, or deletion operation.
- Reason: The frozen architecture makes registries versioned runtime state rather than hard-coded conditionals and requires durable objects to carry complete identity versions. Hashing the document together with its scope and identity axes prevents identical-looking JSON from being reused under a different runtime contract, while refusing to infer “latest” keeps activation and routing authority in their later explicit registries/controllers instead of lexical version ordering or insertion time.

## D-0024 — Non-dispatchable AAE pre-version review candidate

- Date: 2026-08-30
- Status: accepted for Phase A1 review; not frozen
- Decision: Import archive SHA-256 `f56593dae71dd11b84b03c0f3bfd55b1f3f298423085c5b997bdfad4583288d1` as `AAE-REGISTRY-PRE-1` on `phase/a1-aae`. Preserve its 15 physical adapter semantic identities, 20 independently keyed logical modes, shared `GA-PRE-1` Global Awareness block, Recipe 4 host-only exclusion, structured jurisdictions, candidate schema/profile references, and deterministic review surface. Keep every record `PRE_VERSION`, `dispatch_enabled=False`, schema/profile-unfrozen, caps incomplete, and minimum trust unset until explicit review and the remaining Phase A1 contracts pass.
- Reason: The candidate supplies a concrete machine-readable source for reviewing specialist boundaries without silently promoting unresolved names, schemas, caps, profiles, repair counts, or trust thresholds into runtime authority. Its fail-closed readiness predicate makes it useful for tests now while preventing a pre-version registry from reaching model dispatch, training freeze, or qualification by implication.

## D-0025 — Structured CALL_DATA extraction for AAE dispatch

- Date: 2026-08-30
- Status: accepted by frozen v0.1 AAE authority; implemented in PRE-version Slice 01
- Decision: Build model-facing AAE as role-separated structured messages. The authority plane is a host-only trusted instruction message; Canonical JSON V1 `CALL_DATA` is the complete lower-trust user-role message. The final pre-dispatch gate locates `CALL_DATA` by host-owned message index, requires the lower-trust role and exact canonical JSON, reparses with the production strict decoder, reapplies the same immutable schema snapshot, and proves byte/value/schema-hash/instance-hash equality with the initially validated host data. The bracketed human-readable AAE is generated only as an audit surface and is never scanned for control delimiters.
- Reason: The frozen v0.1 contract explicitly forbids a delimiter parser, requires authority/data structural separation, and requires fake `[RESPONSE_CONTRACT]` or closing tags inside user data to remain content. Structured extraction makes those strings incapable of changing the parser boundary while preserving deterministic human inspectability.

## D-0026 — Reconciled PRE-08 schema, policy, and settings boundary

- Date: 2026-09-01
- Status: accepted for Phase A1 review; not frozen
- Decision: Import archive SHA-256 `a72be5a88a9f0c9c9f687995ad2d7cf4e832d4c0415d0f2f378f3120215af1f8` as the PRE-08 handoff on `phase/a1-aae` after safe-path validation and isolated testing. Add strict `SCOPE_VALIDATION`; shared strict-shape, origin/trust, legal-reference, vocabulary, repair-shape, and next-consumer policies; and a separately versioned deterministic tuning-settings handler. Store semantic repair permission in the AAE contract, tunable repair counts and field ceilings in settings, and downstream-edge legality in the registry while retaining host-only route selection. Merge shared files into the newer local Slice 01 checkpoint and refuse stale archive replacements of Phase 0, storage, environment, evidence numbering, and Git state.
- Reason: These boundaries keep semantic legality stable while allowing measured numeric tuning, prevent model-selected routing and identifier laundering, and preserve one reviewable source for all 20 modes without granting dispatch authority. Reconciliation instead of overlay preserves the already evidenced local hardening and makes the exact handoff provenance reproducible. The implementation remains PRE_VERSION/T0 because most mode schemas, projection, settings completeness, same-source training proof, and joint freeze review are still open.

## D-0027 — Full Recipe 0–8 architecture freeze and Qwen3 family supersession

- Date: 2026-09-04
- Status: accepted architecture authority; implementation/runtime qualification open
- Decision: Accept handoff archive SHA-256 `ee24e082df3b24e93b47de371dcc4d87ee2a81c048413dea502dca02fec900a4` as the current v0.1 Recipe 0–8 architecture authority and preserve its exact payload beneath `architecture/v0.1/freeze-2026-09-04/`. Its full checkpoint and dedicated recipe freezes supersede conflicting architecture wording in older sources; older sources remain immutable implementation/audit references. Lock `Qwen/Qwen3-4B-Instruct-2507` as the starting foundation-model family, reclassify the existing Qwen2.5 deployment as historical spike evidence, and leave the exact Qwen3 GGUF/runtime identity open for A3 measurement. Accept the Recipe 0 one-next-turn continuation correction as required but not implemented. Keep Gate A1 open and learned authority at T0.
- Reason: The handoff closes architecture review without pretending that code, model deployment, adapter behavior, or qualification has passed. Versioned intake and exact hash verification preserve provenance; explicit supersession avoids rewriting historical evidence; and separating the model-family lock from the measured deployment identity prevents an untested quantization/runtime from inheriting the old spike's standing.

## D-0028 — Durable one-next-turn continuation cue

- Date: 2026-09-04
- Status: accepted PRE-1 implementation; Gate A1 remains open
- Decision: Extend the transcript migration catalog with a host-owned continuation table. A successfully published completed turn may atomically create only `AWAITING_USER_INPUT` / `USER_INFORMATION_NEEDED`; the immediately following user turn alone may claim it. Recipe 0 projects the fixed-shape marker into SCOPE_PROPOSAL, prefetches exactly the named hash-verified exchange into SCOPE_VALIDATION, and consumes the cue when the Conversation Packet is frozen whether the exchange is retained or discarded. Store no semantic summary in the marker.
- Reason: Grammatical self-containment does not prove semantic independence after Arcadia explicitly solicits a value. Durable immediate-prior binding preserves that conversational frame across restart without becoming general history injection or semantic memory, and one-time consumption prevents accidental propagation.

## D-0029 — Complete PRE-1 learned-mode schema catalog

- Date: 2026-09-04
- Status: accepted implementation checkpoint; not frozen or dispatchable
- Decision: Resolve strict input/output schema pairs for all 20 learned logical modes under recipe-owned packages and one total catalog. Align Context, Decision, Reconciliation, Persistence, Completion, and Result shapes with the 2026-09-04 architecture freeze; retain Recipe 4 as host-only. Require unknown-field rejection, fixed learned-output top-level shapes, bounded collections/text, closed host-behavior enums, and exact compiled schema hashes in `manifests/aae_schema_catalog_pre1.json`. Keep every AAE registry record PRE_VERSION, unfrozen, non-dispatchable, and T0.
- Reason: A total exact-hash schema catalog makes schema-less learned dispatch mechanically impossible and exposes contract drift before runtime integration. Keeping PRE-1 authority unchanged distinguishes structural implementation evidence from measured limits, same-source training proof, runtime qualification, and joint freeze review.

## D-0030 — Forward Qwen3 base-runtime qualification candidate

- Date: 2026-09-04
- Status: accepted as a T0 base-only candidate; Gate A3 remains open
- Decision: Select the locally converted Qwen3-4B-Instruct-2507 Q4_K_M GGUF at SHA-256 `4e00d30a00c71456198672a86a155a2935a7201f5112734f7dbf564362243f73` with llama.cpp tag `b10796` / commit `9a4843cf2f1a3fc8e39f8148e92ee6bfe18e2db6` as the forward A3 qualification candidate. Build it on Windows x64 with CUDA 13.3, compute capability 75, shared libraries and tests/tools enabled, and server disabled. Use `llama-completion` only for the direct non-server base smoke because this revision couples `llama-cli` to its optional server implementation. Preserve the historical Phase 0 submodule and keep all model/build artifacts outside Git under committed hash manifests.
- Reason: The exact candidate loads on the target RTX 2060, offloads all 37/37 layers, exits cleanly, and leaves measured CUDA reserve at a 2,048-token context. That establishes source/conversion/build identity and local fit without laundering a direct executable smoke into `SpecialistInvoker`, LoRA isolation, resident lifecycle, HOT-ceiling, logical-mode, or production authority. All of those remain separately required and trust stays T0.

## D-0031 — Whole-candidate deterministic context projection

- Date: 2026-09-04
- Status: accepted PRE-1 implementation boundary; measured profiles and Gate A1 remain open
- Decision: Bind every learned mode to a unique context-projection policy identity and project only among complete, schema-valid host candidates with explicit contiguous ranks. Count the exact final role messages through a tokenizer/chat-template counter supplied by the pinned runtime boundary. Enforce configured input, reserved-output, headroom, string, array, nesting, and source-excerpt limits; return hash-bound `SETTINGS_INCOMPLETE` or `BUDGET_EXHAUSTED` evidence with no dispatchable call when selection is impossible. Never edit candidate content inside the shared projector.
- Reason: Generic truncation cannot know which evidence remains semantically sufficient and would silently change recipe meaning. Whole-candidate selection leaves semantic projection with the owning recipe controller, makes priority and omissions auditable, keeps exact tokenizer behavior outside A1's model-independent code, and prevents missing PRE-1 measurements from being interpreted as unlimited authority.

## D-0032 — Explicit T0 operator base-model lab

- Date: 2026-09-04
- Status: accepted qualification infrastructure; Gate A3 remains open
- Decision: Provide `run_arcadia.bat` and `arcadia run` as a deliberately direct operator boundary to the pinned Qwen3/llama.cpp candidate. Support one-shot and interactive use, validated safe controls, atomic Git-ignored local overrides, and exact on-demand hash verification. Label every response T0/BASE_ONLY and prohibit implicit adapter attachment, AAE dispatch, transcript or semantic-memory writes, specialist qualification, and production claims. Do not automatically export operator prompts or responses into training data.
- Reason: A usable base-model experience makes prompt behavior, runtime stability, and future base-versus-adapter comparisons observable now without pretending the full application spine exists. Keeping it explicit and isolated preserves the frozen authority boundaries while shortening the feedback loop for reviewed evaluation design and the first controlled Colab training package.
