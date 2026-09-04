# A.R.C.A.D.I.A. — Recipe 0 Open-Continuation Architecture Delta

**Date:** 2026-09-04
**Standing:** REQUIRED / NOT YET IMPLEMENTED / Gate A1 remains open

The accepted correction is authoritative at:

`architecture/v0.1/freeze-2026-09-04/recipe0_continuation_fix/ARCADIA_R0_OPEN_CONTINUATION_FIX_2026-09-03.md`

An immediately following user turn may depend on the preceding successfully
published Arcadia solicitation even when the new text is grammatically complete.
The host therefore owns a fixed-shape, one-next-turn `AWAITING_USER_INPUT` marker.
An active marker prefetches only the exact preceding completed exchange for
`SCOPE_VALIDATION`; an unrelated turn discards it, and the marker then expires.

Required implementation remains:

- add `continuation_state` to current transcript metadata;
- derive the marker only from authoritative completed-turn state;
- add exact one-exchange prefetch to Recipe 0 orchestration;
- support `SUFFICIENT_WITHOUT_HISTORY` in `SCOPE_VALIDATION`;
- keep the marker free of model-written semantic summaries;
- freeze the exact published exchange into the Conversation Packet when required;
- pass the five named unit/integration cases in the frozen correction.

This record ports the handoff into the active evidence ledger. It does not claim
that the supplied path-prefixed documentation patch applied or that runtime code exists.
