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
- Phase 0 immutable input manifest reproduces the authority, dependency, model,
  llama.cpp source, CUDA toolchain, and native runtime hashes.
- Pinned llama.cpp CUDA build passes 43/43 upstream tests.
- Pinned Qwen2.5 3B Q4_K_M smoke run offloads 37/37 layers to the RTX 2060 and exits cleanly.

## Not yet verified

- `SpecialistInvoker` real-runtime enforcement
- LoRA load/apply/isolation behavior
- Safe HOT adapter ceiling and A/B/A lifecycle behavior
- Logical specialist qualification beyond T0

## Active gate: Phase A — deterministic host foundation

Detailed execution tracking lives in `project/TODO_V0_1.md`. Items are marked complete only with reproducible evidence.

Gate 0 is closed by `evidence/phase0/PHASE0_GATE_REPORT.md`. The next work follows
the frozen Phase A module order: configuration, IDs, Canonical JSON V1, hashing,
artifact envelopes, ledgers, strict validation, budgets, trace index, trust
registry, and authority-separated SQLite repositories.

Configuration, identifier, and Canonical JSON V1 contracts are now implemented
and evidenced. Strict decoding rejects duplicate keys, non-finite values,
trailing content, invalid UTF-8, unsupported values, and non-canonical byte
representations. The next exact-order item is hashing.

## Next implementation gate

Phase A: deterministic host foundation, continuing with hashing, artifact
envelopes, ledgers, strict schema validation, budgets, trust registry, and
SQLite connection/migrations.

## Guardrail

The current status authorizes implementation and narrow spikes—not production trust, unreviewed trace training, or claims of runtime qualification.
