# Resident BASE_ONLY Recipe 0 Harness — 2026-09-04

## Standing

**PASS — resident T0 runtime and executable zero-history Recipe 0 slice only.**

Gates A2 and A3 remain open. Recipes 1–8 did not run and are not represented as
implemented. No LoRA was loaded and no learned specialist earned trust.

## Resident runtime identity

- Base/runtime identity: the existing Qwen3 Q4_K_M candidate and llama.cpp
  `b10796` commit `9a4843cf2f1a3fc8e39f8148e92ee6bfe18e2db6`.
- CUDA toolkit: 13.3; compute capability: 75; all model layers GPU-offloaded.
- Server executable SHA-256:
  `fb931a5ee34a4ebd508044de6564b0dba5947f6ebf26ba762d97501f79076c7f`.
- Server implementation SHA-256:
  `6f8d223b3ff2a9dc68e3ca4a26ba70a91bcd7432cd8525a560533d2565238d68`.
- Network boundary: `127.0.0.1` only, one slot, web UI disabled, slot and metrics
  endpoints disabled.
- Rebuild entry: `prepare_qwen3_server.bat`.
- Identity manifest:
  `manifests/qwen3_resident_server_b10796_2026-09-04.json`.

The reproducibility script disables downloaded/prebuilt UI assets so changing
web content cannot silently change the pinned server implementation.

## Performance observation

One interactive resident session produced:

```text
Resident CUDA runtime ready in 17.49s.
ARCADIA> ONE
ARCADIA> TWO
```

The earlier controlled Python measurement separated timing more precisely:

```text
cold load: 19.228s
warm request 1: 0.352s, 54 input tokens, 2 output tokens
warm request 2: 0.197s, 54 input tokens, 3 output tokens
```

A later cold launch after the no-UI rebuild took 27.61 seconds and its Recipe 0
call took 1.46 seconds. Cold load varies with machine state; the demonstrated
performance gain is reuse of one loaded model across subsequent calls.

This confirms the original delay was repeated model startup, not missing GPU
offload. Generation time still depends on prompt and output length.

## Qualification invoker boundary

The new BASE_ONLY invoker performs, in order:

1. Exact logical-mode contract and schema resolution from the PRE-1 registry.
2. Structured AAE serialization.
3. Final rendered `CALL_DATA` reparse, schema validation, and hash equality gate.
4. Exact chat-template input-token count through the pinned runtime.
5. Atomic aggregate work-budget reservation.
6. Fresh stateless request with schema-constrained sampling.
7. Strict JSON decoding, output-schema validation, and mode-specific semantic
   validation.
8. Hash-bound activation receipt with explicit `BASE_ONLY`, T0, no adapter
   lease, and fresh-context/fresh-sampler evidence.

This is qualification infrastructure, not the complete production
`SpecialistInvoker`. Adapter leases, lifecycle state machines, repair attempts,
and POISONED epoch recovery remain Phase A2/A3 work.

## Live Recipe 0 evidence

Command:

```bat
run_arcadia.bat "Explain what you need from me." --mode recipe --transport resident --max-output-tokens 128 --temperature 0
```

Observed:

```text
R0 Conversation Resolver  PASS (2.55s)
SCOPE_PROPOSAL             {"mode":"SCOPE_PROPOSAL","reason_codes":["SUFFICIENT_WITHOUT_HISTORY"],"recent_exchange_count":0,"status":"SUFFICIENT_WITHOUT_HISTORY","target_terms":[]}
R1 Intent                  NOT_IMPLEMENTED
```

The host also created a hashed Conversation Packet and an activation receipt.
Stopping before Recipe 1 is required because only its frozen learned schemas—not
its controller and host transitions—exist in this checkout.

## Deterministic gate

`check.bat` passed with:

- 585/585 tests.
- Ruff clean.
- strict MyPy clean over 69 source files.

New tests cover strict settings, resident response/token decoding, AAE message
separation, work-budget charging, activation receipt identity, semantic rejection
of a schema-valid illegal scope request, and the honest R0-to-unimplemented-R1
stop.
