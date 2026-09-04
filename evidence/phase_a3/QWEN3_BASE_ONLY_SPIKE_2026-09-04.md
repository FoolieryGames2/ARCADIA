# Qwen3 base-only CUDA spike — 2026-09-04

Standing: **PASS for source integrity, conversion, and a direct base-only CUDA smoke; Gate A3 remains open and runtime authority remains T0.**

## Exact candidate

- Source: `Qwen/Qwen3-4B-Instruct-2507` at revision `cdbee75f17c01a7cc42f958dc650907174af0554`.
- Runtime: `ggml-org/llama.cpp` tag `b10796`, commit `9a4843cf2f1a3fc8e39f8148e92ee6bfe18e2db6`.
- Candidate: `qwen3-4b-instruct-2507-q4_k_m.gguf`, 2,497,279,008 bytes, SHA-256 `4e00d30a00c71456198672a86a155a2935a7201f5112734f7dbf564362243f73`.
- Immutable details and runtime binary hashes: `manifests/qwen3_runtime_candidate_b10796_q4_k_m_2026-09-04.json`.

The historical pinned Phase 0 llama.cpp submodule was not changed. This forward candidate uses an ignored build tree so the Qwen2.5 evidence remains reproducible.

## Build and conversion

The Windows x64 Release build used MSVC 19.44.35228, CMake 4.3.2, CUDA 13.3.73, compute capability 75, `GGML_CUDA=ON`, shared libraries, tests/examples/tools enabled, and server disabled. In this llama.cpp revision `llama-cli` is coupled to the optional server implementation, so the non-server `llama-completion` tool is the narrow smoke surface.

All 13 source files matched the official revision. The verifier parsed all three safetensors headers and proved that the index's 398 tensors resolve to complete valid shard ranges. Conversion produced an F16 intermediate of 8,051,283,488 bytes with SHA-256 `edec599214b9367149799066c83866637d86074bc58d627303305a143fd07d18`; pinned `llama-quantize` produced the Q4_K_M candidate above.

Two setup defects were found and corrected without changing the model artifacts: the Visual Studio child shell did not expose `Get-FileHash`, so hashing now uses .NET SHA-256 directly; and reused builds needed CUDA's `bin\\x64` on `PATH` for `cublas64_13.dll`. The smoke command also uses `-no-cnv` so it exits deterministically.

## Measured base-only smoke

- Hardware: NVIDIA GeForce RTX 2060, 6,144 MiB, driver 610.62, compute capability 7.5.
- Profile: no adapter, context 2,048, seed 42, temperature 0, eight-token cap.
- Result: clean exit code 0 and generated `Ready.`.
- CUDA assignment: 37/37 layers offloaded.
- Reported buffers: 2,375.91 MiB model, 288.00 MiB KV, 301.75 MiB compute.
- Reported allocation/reserve: 2,965 MiB allocated and 1,047 MiB reserve at measurement.
- Timings: 15,942.23 ms load; 93.21 prompt tokens/s; 49.51 generated tokens/s.

The pinned runtime's complete registered CTest suite passed 43/43. This included
the Qwen-family tokenizer fixtures, chat parser/template tests, model and state
lifecycle tests, quantization checks, and the exhaustive CUDA backend operation
matrix. The latter took 352.40 seconds; total native test time was 444.24 seconds.

The b10796 aggregate `ALL_BUILD` target also includes an unrelated optional
`llama-app` target that still expects `llama-server-impl.lib` when the server is
disabled. ARCADIA therefore builds the required runtime tools and registered
test targets explicitly; it does not enable the server to satisfy that app.

## Reproduction

From the repository root:

```bat
verify_qwen3_source.bat
prepare_qwen3_runtime.bat -Smoke
```

After the first successful build/conversion, rerun only verification, hashes, and smoke with:

```bat
prepare_qwen3_runtime.bat -SkipDependencies -SkipBuild -SkipConversion -SkipQuantization -Smoke
```

Add `-NativeTests` to build and run the pinned runtime's registered native test
targets without enabling its server.

Generated weights, GGUFs, the llama.cpp checkout, build outputs, and conversion environment remain outside Git. Their identities are committed in manifests.

## Explicitly not demonstrated

This direct executable smoke did not pass through `SpecialistInvoker`, did not load any LoRA, did not establish fresh-context A/B/A isolation, did not exercise residency/lease/swap/POISONED behavior, did not measure a safe HOT adapter ceiling, and did not qualify any logical specialist. It does not close A3 or authorize trust above T0.
