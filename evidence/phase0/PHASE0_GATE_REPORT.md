# Phase 0 Gate Report

Date: 2026-08-29
Standing: **PASS**
Runtime authority: **T0**

This report closes only the frozen-input gate. It does not qualify the
`SpecialistInvoker`, LoRAs, logical specialist modes, or production authority.

## Frozen identities

- Authority manifest SHA-256: `de817029f765a2e6e099326742322b2a8df27c40cced3b5550aaeb20b96f2e49`
- Base model: `Qwen/Qwen2.5-3B-Instruct-GGUF` revision `7dabda4d13d513e3e842b20f0d435c732f172cbe`
- Model artifact: `qwen2.5-3b-instruct-q4_k_m.gguf`, 2,104,932,768 bytes, SHA-256 `626b4a6678b86442240e33df819e00132d3ba7dddfe1cdc4fbb18e0a9615c62d`
- llama.cpp commit: `c9ca51c1f6b18427cde490c7c7eba11d87a96b2d`
- Visual Studio Build Tools: 17.14.39; MSVC 19.44.35228
- CMake: 4.3.2
- CUDA compiler/toolkit: 13.3.73
- Target GPU: NVIDIA GeForce RTX 2060, compute capability 7.5, 6,144 MiB

All runtime artifact sizes and SHA-256 values are frozen in
`manifests/phase0_inputs.json` and reproduced by `scripts/verify_phase0.py`.

## Build controls

- Visual Studio 17 2022 x64 generator
- `GGML_CUDA=ON`
- `CMAKE_CUDA_ARCHITECTURES=75`
- `GGML_NATIVE=ON`
- `BUILD_SHARED_LIBS=ON`
- `LLAMA_BUILD_SERVER=OFF`
- `LLAMA_BUILD_APP=OFF`
- `LLAMA_BUILD_TESTS=ON`
- `LLAMA_BUILD_EXAMPLES=ON`
- Maximum two parallel build workers for the 8 GB host

The pinned upstream unified `llama-app` target links the server implementation
even when `LLAMA_BUILD_SERVER=OFF`; it is therefore disabled. The independent
libraries, examples, tools, and test targets remain enabled. This preserves the
server-disabled boundary rather than silently enabling a server dependency.

## Verification results

- Canonical authority bundle: 45/45 files hash-verified.
- Host bootstrap, unit tests, Ruff, strict MyPy, and SQLite FTS5: PASS.
- Base model size and SHA-256: PASS.
- llama.cpp submodule identity: PASS.
- CUDA toolkit identity: PASS.
- Frozen runtime artifacts: PASS.
- Upstream native test suite: 43/43 passed, total real time 457.01 seconds.
- GPU smoke: Qwen2.5 3B Q4_K_M loaded successfully, 37/37 layers offloaded to CUDA0, generation completed, exit code 0.
- Observed smoke timing: model load 13,624.96 ms; prompt evaluation 37.69 tokens/s; token evaluation 56.45 tokens/s.

## Resolved build discoveries

1. Unbounded MSBuild parallelism produced a missing-object linker race. The
   reproducible build is capped at two workers.
2. CUDA 13.3 runtime DLLs are under `bin/x64`; launch/test environments include
   both `bin/x64` and `bin`.
3. The optional unified app conflicts with the required server-disabled build;
   `LLAMA_BUILD_APP=OFF` resolves that upstream target coupling without changing
   ARCADIA's CLI-first application boundary.

No unresolved design contradiction blocks Phase A.
