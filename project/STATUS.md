# ARCADIA Operating Status

Updated: 2026-08-29

## North star

Build a truth-preserving agent runtime whose learned specialists are compartmentalized behind deterministic, auditable host contracts.

## Verified

- Git repository initialized at the workspace root.
- Initial workspace checkpoint committed and published to `FoolieryGames2/ARCADIA` on GitHub.
- Local baseline: Python `3.13.7`, SQLite `3.50.4`, and an in-memory FTS5 table creation test passes.
- Project host environment pinned to CPython `3.12` with resolved dependencies in `requirements.lock`.
- Re-runnable Windows bootstrap passes environment, unit-test, lint, and strict type-check gates.
- The v0.1 architecture and implementation order are frozen.
- Documentation/static consolidation reports `PASS`.
- The canonical spine contains Recipes 0–8 with no collapsed stage.
- The core learned roster contains 15 physical adapters; Tool / Execution is host-only.
- Existing checkpoint ZIPs preserve both the canonical docs and Obsidian vault forms.

## Not yet verified

- Pinned SQLite/FTS5 assumptions
- Pinned base GGUF identity
- Pinned llama.cpp commit, build options, and library hash
- Real GGUF/LoRA runtime behavior or qualification

## Active gate: Phase 0 — freeze build inputs

Detailed execution tracking lives in `project/TODO_V0_1.md`. Items are marked complete only with reproducible evidence.

1. Convert the verified SQLite/FTS5 host baseline into an explicit startup contract.
2. Select the initial base GGUF.
3. Select and pin llama.cpp only before the real runtime spike.
4. Expand the single versioned runtime configuration as Phase A contracts are implemented.

## Next implementation gate

Phase A: deterministic host foundation, beginning with canonical JSON, strict decoding/validation, IDs, hashing, artifact envelopes, ledgers, budgets, trust registry, and SQLite connection/migrations.

## Guardrail

The current status authorizes implementation and narrow spikes—not production trust, unreviewed trace training, or claims of runtime qualification.
