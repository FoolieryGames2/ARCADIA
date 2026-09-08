# Recipe 0 History Controller PRE-1 Implementation — 2026-09-04

## Standing

**PASS — bounded initial-history Recipe 0 host slice; full Recipe 0 remains open.**

This checkpoint extends the frozen Recipe 0 Conversation Resolver host implementation beyond the
previous zero-history-only resident harness. It does not claim Recipe 0 is complete or runtime-qualified.

## Source authority

Implementation follows:

- `ARCADIA_V0_1_PROTOTYPE_BUILD_DOCS_2026-08-29/.../recipes/R0_CONVERSATION_RESOLVER_V0_1.md`
- `architecture/v0.1/freeze-2026-09-04/recipe0_continuation_fix/ARCADIA_R0_OPEN_CONTINUATION_FIX_2026-09-03.md`
- the existing strict PRE-1 `SCOPE_PROPOSAL` and `SCOPE_VALIDATION` schemas
- the existing project-scoped append-only `TranscriptRepository`

The patch was authored against the uploaded `93cb20b...` snapshot. The touched existing source files
were unchanged by the live `93cb20b... -> 7959475...` resident-harness delta, so this slice is intended
to apply cleanly to current `main` at `795947526fa89494ef459b24c9483d8ccc79188b`.

## Implemented

1. Added a recipe-facing `SpecialistInvoker` protocol and immutable `SpecialistInvocation` record.
2. Added exact public `TranscriptRepository.load_completed_exchange(turn_id=...)` for deterministic
   targeted-history hydration after FTS returns a turn identity.
3. Added `Recipe0Policy` with host-owned bounds for recent lookback, targeted candidates, expansion
   cycles, and injected-history tokens.
4. Added `Recipe0ConversationController` supporting:
   - zero-history `SUFFICIENT_WITHOUT_HISTORY`;
   - exact chronological `REQUEST_RECENT` retrieval;
   - bounded transcript-FTS `REQUEST_TARGETED` retrieval;
   - exact one-exchange `AWAITING_USER_INPUT` continuation prefetch;
   - strict `SCOPE_VALIDATION` revalidation before packet freeze;
   - exact transcript text/hash preservation in the Conversation Packet;
   - `SUFFICIENT_WITHOUT_HISTORY` dropping an unnecessary continuation prefetch;
   - deterministic unresolved packet freeze when targeted search returns no candidate turns;
   - injected-history token-bound rejection through a host-supplied exact token counter.
5. Preserved the one-next-turn continuation marker semantics and consumes it only when the current
   Recipe 0 packet is successfully frozen.

## Intentionally not implemented

`SCOPE_VALIDATION` may return `NEEDS_MORE_RECENT` or `NEEDS_TARGETED_HISTORY`. This checkpoint stops
with explicit `Recipe0ExpansionRequired` instead of inventing a retrieval-expansion policy that is not
fully specified by the frozen documents. Multi-cycle delta expansion is therefore the next Recipe 0
controller slice.

Normal recipe-mode runs also still do **not** fabricate completed transcript exchanges. Until a real
Recipe 8/publication result exists, completed-history fixtures should be seeded only in tests or an
explicit qualification harness through the real `TranscriptRepository` APIs.

## Tests added

- zero-history packet freeze without validation
- exact recent one-exchange retrieval
- targeted FTS retrieval and exact completed-exchange hydration
- targeted no-hit unresolved freeze
- open-continuation exact prior-exchange prefetch
- unrelated continuation payload drops the prefetch
- continuation marker consumption after successful freeze
- explicit stop on additional retrieval request
- fail-closed injected-history token bound
- exact completed-exchange public read and open-turn rejection

## Sandbox evidence

Focused new tests:

```text
9 passed
```

R0/transcript/contract regression set:

```text
82 passed
```

Broad executable suite excluding environment-only blockers:

```text
529 passed
```

Excluded here only because this workstation sandbox does not reproduce the project development
environment:

- `tests/unit/test_environment.py` — sandbox is Python 3.13; project pins Python 3.12.
- `tests/unit/core/test_canonical_json.py` — Hypothesis unavailable.
- `tests/unit/core/test_ids.py` — Hypothesis unavailable.
- Ruff and strict MyPy — packages unavailable in the sandbox.

`python -m compileall -q src` passed.

## Next slice

Implement the deterministic bounded expansion loop for `NEEDS_MORE_RECENT` and
`NEEDS_TARGETED_HISTORY`, including delta-only retrieval, cycle accounting, history-token budget
handling, and terminal `BOUND_EXHAUSTED` / `UNRESOLVABLE_WITH_TRANSCRIPT` behavior. Only after that
should the resident harness call Recipe 0 complete enough to hand its packet to the Recipe 1 Intent
controller.
