# A.R.C.A.D.I.A. v0.1 — Full Architecture Freeze / Build Handoff

**Checkpoint date:** 2026-09-04  
**Standing:** Full Recipe 0→8 architecture frozen for prototype implementation/testing. Runtime and implementation qualification remain open.

## Start here

1. `ARCADIA_V0_1_FULL_ARCHITECTURE_FREEZE_CHECKPOINT_2026-09-04.md`
2. `ARCADIA_V0_1_BUILD_HANDOFF_2026-09-04.md`
3. `frozen_architecture/` for recipe-level architecture authority.

## What changed since the R0–R6 checkpoint

- Recipe 7 Completion was reviewed and frozen.
- Recipe 8 Result was reviewed and frozen.
- The selected conversational-adapter presentation contract was intentionally kept small for v0.1.
- Host validation, deterministic fallback, `RSTxxx`, publication, `PUBxxx`, and exact-transcript completion boundary were frozen.
- Full Recipe 0→8 architecture is now ready for implementation handoff.

## Important distinction

**Architecture frozen ≠ implementation qualified.**

The build must still pass recipe tests, runtime/adapter qualification, failure injection, persistence stress gates, Completion/Result stress gates, and full-spine replay/hash tests.

## Canonical terminology/model

- Foundation model: `Qwen/Qwen3-4B-Instruct-2507`
- Arcadia = whole runtime/system.
- Base/foundation model = underlying replaceable model.
- Specialist adapters = narrow learned hats.
- Conversational adapter = selected user-facing personality layer.
- Howard = only the specific Howard conversational adapter/personality.
