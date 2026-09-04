# A.R.C.A.D.I.A. — Recipe 0 Open-Continuation Architecture Correction

**Date:** 2026-09-03  
**Standing:** accepted architecture correction; implementation/test work remains open; Gate A1 remains OPEN

## Problem

A next user turn can be grammatically self-contained while still being the answer to an immediately
preceding Arcadia solicitation. The prior R0 zero-history rule could therefore drop required dialogue
frame.

Example:

```text
User: I want to edit my journal.
Arcadia: Sure — what would you like to add or change?
User: I dreamed of pink elephants again last night. I woke up to a broken toe!
```

The third line is journal-edit payload only because the preceding completed exchange supplies that
conversational role.

## Accepted correction

1. `current_transcript_metadata` receives host-owned fixed-shape `continuation_state`.
2. `AWAITING_USER_INPUT` is set only from authoritative completed-turn state requiring user input.
3. The marker points only to the immediately preceding completed exchange and carries no semantic summary.
4. An active marker causes exact one-exchange prefetch into `SCOPE_VALIDATION`.
5. `SCOPE_VALIDATION` adds `SUFFICIENT_WITHOUT_HISTORY` so unrelated next turns can discard the prefetch.
6. The marker is one-next-turn only and never becomes semantic memory.
7. Exact user payload remains exact; the continuation cue does not authorize paraphrase or older-history search.

## Required implementation touch points

```text
src/arcadia/contracts/schemas/r0/scope_proposal.py
src/arcadia/contracts/schemas/r0/scope_validation.py
Recipe 0 host initial packet builder / transcript metadata projection
Recipe 0 retrieval/validation orchestration
completed-turn continuation-state writer
Conversation Packet freezer
R0 unit + integration fixtures
```

Exact source paths may be adjusted to the current repository layout; authority semantics above are frozen.

## Required tests

```text
test_r0_open_continuation_prefetches_exact_prior_exchange
test_r0_open_continuation_self_contained_payload_keeps_required_frame
test_r0_open_continuation_unrelated_turn_drops_prefetched_history
test_r0_open_continuation_marker_is_one_turn_only
test_full_journal_edit_elicitation_then_exact_payload
```

## Non-goals

- no general automatic history injection;
- no semantic memory lookup;
- no journal-specific R0 logic;
- no model-written hidden summary;
- no tool execution in the elicitation turn;
- no change to Intent authority.
