# R0 -> R1 Live Qualification Trace Correction — 2026-09-08

## Standing

**PASS — presentation/qualification observability correction; authority unchanged.**

This slice makes the interactive and one-shot resident Recipe 0 -> Recipe 1 T0 BASE_ONLY
qualification path expose the important learned-call evidence synchronously in the CLI.
It does not weaken validation, grant learned authority, persist raw model output as transcript
truth, implement Recipe 2, or change the frozen R0/R1 semantic contracts.

## Operator-visible sequence

For every learned recipe call, recipe mode now prints, in execution order:

1. specialist mode and call ordinal;
2. exact host `CALL_DATA` as Canonical JSON;
3. aggregate work-budget usage before the call;
4. exact serialized model messages sent to the resident runtime;
5. exact raw model response text marked `UNTRUSTED`;
6. resident prompt/completion token counts and elapsed time;
7. BASE_ONLY invoker `PASS` with call UUID/output hash and updated budget, or
   BASE_ONLY invoker `REJECTED` with the exact exception.

A later deterministic recipe-controller check may still reject an invoker-PASS output. The CLI
keeps the existing outer `ARCADIA runtime error` for those controller failures, so the operator
can distinguish model text, learned-call validation, and recipe-host validation.

The raw response is emitted immediately after the resident runtime returns and before strict
JSON parsing or semantic validation. Therefore malformed, truncated, or semantically illegal
model text remains visible to the local operator even when the existing host boundary fails
closed.

## Authority separation

The live trace is presentation-only qualification evidence. Raw model text remains untrusted.
Only the existing deterministic BaseOnlySpecialistInvoker parsing, schema checks, mode-specific
semantic validation, activation receipt creation, and recipe controllers determine acceptance.
The trace observer cannot alter CALL_DATA, model output, work budgets, receipts, artifacts,
transcript state, routing, or publication state.

## Interaction with prior 2026-09-08 correction

This slice is intended to be applied after
`ARCADIA_R0_R1_CONVERSATION_REGEX_CORRECTION_2026-09-08.patch`.
The prior correction keeps one host-owned recipe conversation UUID across interactive prompts,
adds `/new`, and changes the equivalent REF regex spelling to the llama.cpp-compatible form.
This trace slice does not alter those behaviors.

## Local checks available in the build workspace

- `python -m py_compile` over all changed/new Python files: PASS
- `git diff --check`: PASS
- incremental patch clean-apply check against an exact post-correction overlay: PASS

## Pinned-workstation integration result

```text
pytest: 620 passed
Ruff: PASS
MyPy: PASS (74 source files)
```

A real resident Qwen3 smoke ran on loopback port `18081` because the configured `18080` port
was already occupied and correctly refused by the process-owned launcher. The trace displayed:

- exact `SCOPE_PROPOSAL`, `SPELL_NORMALIZATION`, and `TERM_MEANING` call data;
- exact serialized model messages and raw untrusted responses;
- prompt/completion tokens, elapsed time, and budget transitions;
- invoker `PASS` evidence for all three returned schema-valid objects.

The subsequent deterministic Recipe 1 controller rejected Meaning local key `MILK_001` because
it is outside the frozen `TERM_` / `REF_` namespace. The trace therefore proves the intended
observability and acceptance-layer distinction while preserving an honest failed-closed T0
qualification standing. No complete real-model R0 -> R1 success is claimed.
