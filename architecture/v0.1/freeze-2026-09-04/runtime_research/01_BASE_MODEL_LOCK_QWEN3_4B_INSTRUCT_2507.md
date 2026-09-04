# A.R.C.A.D.I.A. v0.1 — Base Model Lock

**Decision date:** 2026-09-03  
**Status:** LOCKED STARTING MODEL FAMILY

## Locked model

```text
Qwen/Qwen3-4B-Instruct-2507
```

This is the starting **foundation/base model** for A.R.C.A.D.I.A. v0.1 and the intended parent checkpoint for the v0.1 specialist adapter family.

## Why this model is a strong fit

Official Qwen documentation describes `Qwen3-4B-Instruct-2507` as:

- a 4.0B-parameter causal language model;
- 3.6B non-embedding parameters;
- 36 layers;
- native 262,144-token context;
- **non-thinking only** — it does not emit `<think></think>` blocks;
- improved for instruction following, reasoning, text comprehension, coding, and tool usage;
- released under Apache-2.0.

Those traits fit A.R.C.A.D.I.A.'s intended use unusually well. The specialist hats need bounded instruction following and structured semantic judgment more than hidden free-running reasoning behavior.

## Architectural meaning of the lock

This locks the **model family/checkpoint identity**, not every deployment parameter.

Still open for runtime qualification:

```text
exact GGUF quantization
exact GGUF file hash
exact llama.cpp commit/build
CUDA/backend build options
GPU layer placement
context size used by each logical mode
KV cache configuration
sampler/generation profile
grammar / structured-output mechanics
adapter rank/target-module choices
adapter residency policy
```

A.R.C.A.D.I.A. already requires those output-affecting values to be included in an immutable `InferenceProfile` / runtime identity before a learned mode earns trust.

## Context-size policy

The model supports a very large native context, but A.R.C.A.D.I.A. should **not** treat that as permission to inject huge packets.

The architecture remains:

> smallest sufficient projection, not maximum available context.

Initial runtime qualification should test realistic compact profiles first (for example 8K and 16K classes) and only expand when a specific recipe proves the need.

## GGUF position

The ggml-org project publishes a llama.cpp-compatible GGUF conversion of this exact model family. That confirms a direct local llama.cpp deployment path exists.

However, **do not lock Q8_0 merely because an official Q8_0 conversion exists**. On the target 6 GB-class GPU, model weights are only one part of the memory budget. Adapter objects, inference scratch space, KV, context, staging headroom, and CUDA/backend overhead all matter.

The quantization decision belongs to Phase A3 measurement.

## Training identity rule

Every trained v0.1 specialist must record at minimum:

```text
base checkpoint identity
base checkpoint hash
training tokenizer identity
adapter configuration
adapter artifact hash
training dataset manifest hash
training code/config identity
```

A specialist trained against a different parent model is not silently interchangeable with this family.

## Failure rule

If the pinned local runtime cannot satisfy A.R.C.A.D.I.A.'s adapter-residency/isolation/latency gates with this model:

```text
replace or re-qualify the runtime/base deployment candidate
DO NOT rewrite recipe ownership to hide the failure
```

The recipe architecture does not depend on Qwen being permanent.

## Official sources

- Qwen model card: https://huggingface.co/Qwen/Qwen3-4B-Instruct-2507
- Qwen license: https://huggingface.co/Qwen/Qwen3-4B-Instruct-2507/blob/main/LICENSE
- ggml-org GGUF conversion: https://huggingface.co/ggml-org/Qwen3-4B-Instruct-2507-Q8_0-GGUF
