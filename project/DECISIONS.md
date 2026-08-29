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
