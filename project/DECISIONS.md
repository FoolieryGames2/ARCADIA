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
