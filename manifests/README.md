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
