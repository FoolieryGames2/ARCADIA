# A.R.C.A.D.I.A. — Recipe 0 Open-Continuation Architecture Delta

**Date:** 2026-09-04
**Standing:** IMPLEMENTED AND TESTED / PRE-1 / Gate A1 remains open

The accepted correction is authoritative at:

`architecture/v0.1/freeze-2026-09-04/recipe0_continuation_fix/ARCADIA_R0_OPEN_CONTINUATION_FIX_2026-09-03.md`

An immediately following user turn may depend on the preceding successfully
published Arcadia solicitation even when the new text is grammatically complete.
The host therefore owns a fixed-shape, one-next-turn `AWAITING_USER_INPUT` marker.
An active marker prefetches only the exact preceding completed exchange for
`SCOPE_VALIDATION`; an unrelated turn discards it, and the marker then expires.

Implemented behavior:

- [x] fixed-shape `continuation_state` is present in current transcript metadata;
- [x] the transcript repository creates it only while atomically completing a published turn;
- [x] the immediately following user turn claims exactly that source exchange;
- [x] Recipe 0 projects exactly one hash-verified exchange to `SCOPE_VALIDATION`;
- [x] `SUFFICIENT` retains the exchange and `SUFFICIENT_WITHOUT_HISTORY` discards it;
- [x] Conversation Packet freeze consumes the marker exactly once;
- [x] no semantic summary or memory fact exists in the marker;
- [x] all five named frozen correction tests pass.

Implementation touch points:

- `src/arcadia/contracts/schemas/r0/scope_proposal.py`
- `src/arcadia/contracts/schemas/r0/scope_validation.py`
- `src/arcadia/storage/migrations.py` migration 6
- `src/arcadia/storage/transcript_repository.py`
- `src/arcadia/recipes/r0/controller.py`
- `tests/unit/recipes/r0/test_open_continuation.py`

Focused qualification passed 96 tests. The full deterministic suite subsequently
passed 551 tests. This proves the host correction only; it does not qualify a model,
make the PRE-version registry dispatchable, or close Gate A1.
