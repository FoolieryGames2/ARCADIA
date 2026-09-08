# Recipe 0 Bounded History Expansion PRE-1 Implementation — 2026-09-04

## Standing

**PASS — deterministic bounded Recipe 0 expansion controller slice; runtime wiring remains open.**

This checkpoint completes the missing host-side expansion loop after the initial Recipe 0 history
retrieval. It remains PRE-1 implementation evidence. It does not change frozen architecture,
qualify a learned model, close Gate A1, or claim the resident lab is already wired through this
controller.

## Source authority

Implementation is grounded in:

- `.../recipes/R0_CONVERSATION_RESOLVER_V0_1.md`;
- the frozen `SCOPE_PROPOSAL` / `SCOPE_VALIDATION` PRE-1 schemas;
- `project/TODO_A1_STRICT_SCHEMAS_POLICIES.md`, which explicitly leaves deterministic expansion-delta
  selection to host policy/runtime work;
- `evidence/phase_a1/A1_SCOPE_VALIDATION_PRE1_REPORT.md`;
- the accepted one-next-turn continuation correction.

The frozen model response shape is unchanged. No count/search-term fields were added to
`SCOPE_VALIDATION`.

## PRE-1 host policy choice

The architecture deliberately leaves exact expansion-delta selection unspecified. This
implementation makes the following deterministic PRE-1 choice without presenting it as a new
frozen contract:

1. An initial `REQUEST_RECENT` or `REQUEST_TARGETED` retrieval consumes the first configured scope
   cycle, matching the existing reference trace where a three-cycle bound projects two remaining
   cycles into the first validation call.
2. `NEEDS_MORE_RECENT` expands the contiguous recent window to the configured
   `max_contiguous_lookback_exchanges` in one **older-only delta**. Already supplied turns are never
   reinjected.
3. `NEEDS_TARGETED_HISTORY` uses the validator's existing `unresolved_references[]` strings as the
   bounded transcript-FTS queries. This avoids inventing a hidden search-term output field.
4. Targeted results are project/conversation scoped, exact-turn hydrated, deduplicated, sorted by
   authoritative turn ordinal, and capped by the existing PRE-1 validation-turn shape.
5. Every successful expansion decrements `remaining_expansion_cycles` before the next validation
   call. A validation call with zero remaining cycles therefore cannot legally request another
   expansion under the existing semantic validator.
6. The one-turn `AWAITING_USER_INPUT` prefetch remains a correction prefetch rather than an initial
   proposal retrieval, so the configured expansion cycles remain available if validation says that
   exact prior exchange is still insufficient.

## Terminal handling

The host freezes `BOUND_EXHAUSTED` with the last validated unresolved references when another safe
history delta cannot be added because:

- the contiguous recent bound is already fully represented;
- the transcript contains no older completed recent exchange;
- targeted search only rediscovers already supplied turns;
- the fixed validation-turn capacity has been reached; or
- adding the candidate delta would cross the configured injected-history token budget.

The host freezes `UNRESOLVABLE_WITH_TRANSCRIPT` when a requested targeted expansion produces no
legal transcript-FTS hit at all for the validator's unresolved-reference strings.

Initial retrieval still fails closed with `Recipe0HistoryBoundExceeded` if the very first exact
history slice already exceeds the injected-history budget; this checkpoint does not fabricate an
unresolved conversational reference merely to synthesize a packet for that host configuration
error.

## Storage delta support

`TranscriptRepository.load_recent_exchanges_before(...)` was added so contiguous expansion can read
only the next older completed-exchange delta rather than repeatedly materializing the whole recent
window.

The previous exact `load_completed_exchange(turn_id=...)` addition remains the targeted-hit hydration
boundary.

## Trace behavior

`Recipe0Result` now retains all `validation_invocations` in order. A compatibility property exposes
the final validation invocation when older test/runtime code only needs the last attempt.

Conversation Packet evidence remains exact transcript text plus exact authoritative hashes; no
summary substitutes for transcript evidence.

## Tests

Focused new/updated Recipe 0 and transcript-delta tests:

```text
16 passed
```

R0 + transcript + strict-schema + adjacent runtime regression set:

```text
101 passed
```

Broad executable suite in the available sandbox, excluding only environment-only blockers:

```text
536 passed
```

Also passed:

```text
python -m compileall -q src
```

Unavailable in this sandbox:

- project-pinned Python 3.12 identity check (sandbox is Python 3.13);
- Hypothesis-dependent tests;
- Ruff;
- strict MyPy.

Those gates are not claimed as executed.

## Live-repository compatibility

This slice was prepared against live `main` head:

```text
5d7a911c3213ab321ebf62124b5da3e64d1ce079
```

The existing files touched by the cumulative R0 patch still match the live-main blobs checked before
packaging, including:

```text
src/arcadia/recipes/r0/controller.py          2e6b7cf2b187c7eb38a052ea56fdde00edfac966
src/arcadia/storage/transcript_repository.py d7065d523c67a64a6401861eab19943c1c64dfce
src/arcadia/recipes/r0/__init__.py            e03d03224aa2b692e3e96d275ff4c66f8c5e630a
```

The connected GitHub integration allowed live reads but rejected branch creation with HTTP 403, so
this checkpoint is supplied as a tested patch/overlay rather than falsely claiming it was pushed.

## Next slice

Wire this completed Recipe 0 controller to the resident BASE_ONLY qualification invoker, then place
the already-built Recipe 1 Intent controller behind the validated Conversation Packet handoff. The
first live goal is an honest `R0 -> R1 -> R2 NOT_IMPLEMENTED` base-model trace.
