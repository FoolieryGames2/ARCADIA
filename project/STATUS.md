# ARCADIA Operating Status

Updated: 2026-08-29

## North star

Build a truth-preserving agent runtime whose learned specialists are compartmentalized behind deterministic, auditable host contracts.

## Verified

- Git repository initialized at the workspace root.
- Local baseline: Python `3.13.7`, SQLite `3.50.4`, and an in-memory FTS5 table creation test passes.
- The v0.1 architecture and implementation order are frozen.
- Documentation/static consolidation reports `PASS`.
- The canonical spine contains Recipes 0–8 with no collapsed stage.
- The core learned roster contains 15 physical adapters; Tool / Execution is host-only.
- Existing checkpoint ZIPs preserve both the canonical docs and Obsidian vault forms.

## Not yet verified

- Reproducible committed source-control checkpoint
- Pinned Python and host-validation dependencies
- Pinned SQLite/FTS5 assumptions
- Pinned base GGUF identity
- Pinned llama.cpp commit, build options, and library hash
- Real GGUF/LoRA runtime behavior or qualification

## Active gate: Phase 0 — freeze build inputs

1. Establish the initial repository checkpoint.
2. Choose and pin the Python toolchain and deterministic host dependencies.
3. Re-verify SQLite FTS5 after the project runtime is pinned (local baseline currently passes).
4. Select the initial base GGUF.
5. Select and pin llama.cpp only before the real runtime spike.
6. Create the single versioned runtime configuration source.

## Next implementation gate

Phase A: deterministic host foundation, beginning with canonical JSON, strict decoding/validation, IDs, hashing, artifact envelopes, ledgers, budgets, trust registry, and SQLite connection/migrations.

## Guardrail

The current status authorizes implementation and narrow spikes—not production trust, unreviewed trace training, or claims of runtime qualification.
