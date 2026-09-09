# A.R.C.A.D.I.A. — R0 Zero-History Host Continuation

Date: 2026-09-08

Standing: accepted PRE-1 host-policy correction; deterministic host authority and the frozen
Recipe 0 -> Recipe 1 boundary are unchanged; full real-model qualification remains open.

## Problem

When `SCOPE_PROPOSAL` requested transcript history but the host-authoritative completed
exchange count was zero, Recipe 0 rejected the output and stopped the CLI. A real T0 response
also combined `REQUEST_RECENT`, a zero recent count, and a target term. Those request fields
were internally inconsistent, but none could select history because no completed exchange
existed.

## Correction

For a schema-valid `SCOPE_PROPOSAL` with status `REQUEST_RECENT` or `REQUEST_TARGETED` and
`completed_exchange_count=0`, the host now:

1. preserves the original model output as untrusted evidence;
2. records `R0_NO_COMPLETED_HISTORY_AVAILABLE`, its source mode, the canonical source-output
   hash, and action `CONTINUE_TO_INTENT_WITH_UNRESOLVABLE_TRANSCRIPT`;
3. performs no transcript retrieval and no scope-validation call;
4. freezes an empty `ConversationPacket` with `UNRESOLVABLE_WITH_TRANSCRIPT`; and
5. continues the bounded recipe flow into Recipe 1.

The host does not rewrite the model response to `SUFFICIENT_WITHOUT_HISTORY`. Target terms,
when supplied, remain unresolved references in the packet. The CLI reports the event as
`HOST CORRECTION [NON-FATAL]` and the invocation as `PASS_WITH_HOST_CONTINUATION`.

The zero-history fact takes precedence over history-request cross-field checks because the
request parameters are operationally moot. The output must still pass its strict JSON schema.
All nonzero-history semantic checks and all unrelated failures remain fail-closed.

`HostCorrection` is a general evidence envelope, not general permission to continue. Any
future use requires its own named condition, deterministic action, bounded tests, decision,
and operator-visible log.

## Verification

Regression coverage proves:

- valid recent and targeted history requests receive the typed correction;
- the mixed request shape returned by the T0 model receives the same bounded correction;
- the BASE_ONLY activation receipt and recipe invocation retain correction evidence;
- the live trace prints the source-output hash and non-fatal continuation action;
- Recipe 0 performs neither retrieval nor validation and freezes the truthful packet; and
- the Recipe 0 -> Recipe 1 harness advances to `SPELL` under the same aggregate budget.

The pinned workstation gate passes 625 tests, Ruff, and strict MyPy over 74 source files.
