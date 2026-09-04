# A.R.C.A.D.I.A. — Runtime / Model Research Source Index

**Compiled:** 2026-09-03

## Project sources

### Independent R3 stress test

`ARCADIA_R3_INDEPENDENT_STRESS_TEST_2026-08-29.md`

Key material used:

- ST-01 through ST-10 findings;
- 87 actual learned-call correction;
- five-slice call/load/eviction table;
- runtime failure/adversarial tests;
- required narrow runtime-spike recommendation.

### Master build authority

`ARCADIA_V0_1_MASTER_BUILD_AUTHORITY.md`

Key material used:

- full-spine ownership model;
- AAE authority/data separation;
- STAGING replacement semantics;
- atomic `ensure_hot_and_acquire()`;
- runtime health states;
- inference profile identity;
- SourcePolicyRegistry;
- OperationJournal / OUTCOME_UNKNOWN;
- trace privacy/training firewall;
- deterministic fast path;
- Phase A2/A3 exact build gates.

### Adapter runtime specification

`ARCADIA_ADAPTER_RUNTIME_MANAGER_PROTOTYPE_BUILD_SPEC_R3_2026-08-28.md`

Key material used:

- `SpecialistInvoker -> AdapterManager -> ModelRuntime` ownership;
- COLD/READY/HOT versus ACTIVE distinction;
- max-hot as configurable measured policy;
- fresh-context rule;
- adapter leases and activation receipts.

### Adapter runtime exact build order

`ARCADIA_ADAPTER_RUNTIME_MANAGER_EXACT_BUILD_ORDER_R3_2026-08-28.md`

Key material used:

- A/B/A isolation;
- load/free soak;
- 100-adapter synthetic registry;
- failure matrix;
- runtime acceptance gates.

### Recipe-1 stress hardening / A1 status

Current 2026-09-03 A1 artifacts.

Key material used:

- 69 focused Recipe-1 tests;
- 572 deterministic external subset;
- source compilation PASS;
- retained 87-call reference integrity;
- canonical Windows Python 3.12 qualification still required.

## External official sources — model

### Qwen3-4B-Instruct-2507 model card

https://huggingface.co/Qwen/Qwen3-4B-Instruct-2507

Verified 2026-09-03:

- 4.0B parameters / 3.6B non-embedding;
- 36 layers;
- native 262,144 context;
- non-thinking-only behavior;
- stated improvements in instruction following, reasoning, comprehension, coding, and tool usage.

### Qwen license

https://huggingface.co/Qwen/Qwen3-4B-Instruct-2507/blob/main/LICENSE

Verified Apache License 2.0.

### ggml-org GGUF conversion

https://huggingface.co/ggml-org/Qwen3-4B-Instruct-2507-Q8_0-GGUF

Used only to establish that a llama.cpp-compatible GGUF conversion exists for the exact model family. It does **not** lock Q8_0 as A.R.C.A.D.I.A.'s final runtime quantization.

## External official sources — llama.cpp

### llama.cpp server README

https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md

Verified 2026-09-03:

- multiple LoRAs may be supplied to the server;
- `--lora-init-without-apply` loads LoRAs without initially applying them;
- per-request LoRA configuration exists;
- unspecified adapters in a request default to scale `0.0`.

This is evidence that loaded-versus-applied separation exists in current llama.cpp server behavior.

### libllama adapter API

https://github.com/ggml-org/llama.cpp/blob/master/include/llama.h

Verified 2026-09-03 API surface includes:

```text
llama_adapter_lora_init
llama_adapter_lora_free
llama_set_adapters_lora
```

This is the strongest direct basis for A.R.C.A.D.I.A.'s preferred host-owned adapter lifecycle research path.

## External comparison source — vLLM

https://docs.vllm.ai/en/latest/api/vllm/config/lora/

Current vLLM configuration distinguishes:

```text
max_loras
max_cpu_loras
```

This is useful as a comparison showing that active-LoRA capacity and cached-LoRA capacity are treated as separate serving concerns. It is not an A.R.C.A.D.I.A. runtime selection.

## Evidence discipline

External runtime documentation is moving software documentation. Before Phase A3 qualification:

1. pin the exact llama.cpp commit;
2. archive or record the relevant API/README state;
3. test the compiled build directly;
4. never treat today's `master` documentation as permanent qualification evidence.
