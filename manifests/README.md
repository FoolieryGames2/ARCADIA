# ARCADIA manifests

- `architecture_freeze_v0_1_2026-09-04.json` is the active architecture-authority
  identity and locks `Qwen/Qwen3-4B-Instruct-2507` only at the model-family level.
- `phase0_inputs.json` remains the immutable identity of the successful historical
  Qwen2.5/llama.cpp/CUDA spike. It does not select or qualify the active Qwen3
  deployment.

The exact Qwen3 GGUF, llama.cpp build, context/sampler profiles, and adapter
residency policy must be recorded in a new forward manifest after A3 measurement.
Do not overwrite the historical Phase 0 manifest or infer qualification across
the model-family change.

- `qwen3_4b_source_2026-09-04.json` pins and verifies the complete local
  safetensors source package against the official model revision. It proves only
  source-input integrity; GGUF conversion, CUDA execution, adapters, and runtime
  authority remain unqualified/T0.
- `qwen3_runtime_candidate_b10796_q4_k_m_2026-09-04.json` identifies the exact
  forward llama.cpp build, conversion products, runtime binaries, and measured
  base-only CUDA smoke. It selects a qualification candidate at T0; it does not
  qualify adapters, `SpecialistInvoker`, residency, or Gate A3.
