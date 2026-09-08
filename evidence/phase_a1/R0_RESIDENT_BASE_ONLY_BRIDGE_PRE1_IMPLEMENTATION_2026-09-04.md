# R0 Resident BASE_ONLY Bridge — PRE-1 implementation checkpoint

## Standing

PASS for the bounded bridge slice; not a full R0→R1 pipeline.

## Implemented

- The resident recipe harness now constructs and runs `Recipe0ConversationController` instead of fabricating a zero-history `ConversationPacket`.
- The harness uses the real `TranscriptRepository` and `MigrationRunner` when a transcript repository is not explicitly injected for qualification tests.
- The current user prompt is appended as a real OPEN transcript turn before R0 so one-next-turn continuation claiming remains authoritative.
- The harness does **not** fabricate or publish an assistant completion. R8/publication remains absent, so the current turn stays OPEN.
- `BudgetedBaseOnlyRecipeInvoker` adapts the qualification-only `BaseOnlySpecialistInvoker` to the recipe-facing `SpecialistInvoker` protocol.
- One immutable `WorkBudgetLedger` is carried forward across every R0 learned call; each new call receives the prior call's returned ledger head.
- Activation receipts are retained in learned-call order.
- Frozen history token counting uses the resident runtime tokenizer over canonical JSON for the exact frozen history payload.
- R1 remains `NOT_IMPLEMENTED` in this slice.

## Qualification project scope

The default resident lab transcript repository is isolated in `runtime-data/arcadia_recipe0_lab.sqlite3` and uses a checked-in T0 qualification project UUID:

`48003a9b-1516-4ac3-bbb3-e3366f63bde8`

A fresh conversation UUID is created when no explicit qualification conversation is injected. This prevents incomplete R0-only qualification turns from polluting the future production transcript database.

## Important boundary

The harness starts an OPEN user turn but does not complete it. This is deliberate. Until downstream Result/publication authority exists, the lab must not invent completed assistant transcript history merely to exercise R0 retrieval.

History-bearing R0 qualification should therefore use an explicitly seeded `TranscriptRepository` fixture containing real completed exchanges.

## Tests added

- fresh prompt uses a real transcript repository and leaves zero completed exchanges;
- proposal + validation path proves budget continuity: incoming model-call usage is `0` then `1`, final usage is `2`;
- ordered activation receipts are retained;
- exact prior completed exchange is frozen into the resulting Conversation Packet.

## Dependency

This slice assumes the immediately preceding `ARCADIA_R0_BOUNDED_HISTORY_EXPANSION_SLICE_2026-09-04.patch` has been applied.
