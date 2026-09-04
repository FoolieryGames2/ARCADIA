# A.R.C.A.D.I.A.

Top-tier operating project for the **Adaptive Runtime for Compartmentalized Agents, Decisions, Interaction & Automation**.

## Current standing

- Version: `0.1-prototype`
- Architecture: full Recipe 0–8 freeze accepted on 2026-09-04
- Deterministic foundation: Gate A passed
- Active implementation gate: A1 open
- Documentation/static validation: passed
- Runtime qualification: not yet earned (`T0`)
- Foundation model family: `Qwen/Qwen3-4B-Instruct-2507`
- Exact deployment/runtime identity: unqualified

The current architecture authority is the immutable bundle at:

`architecture/v0.1/freeze-2026-09-04/`

Start with `README_FIRST.md`, the full freeze checkpoint, and the build handoff.
The 2026-08-29 prototype bundle remains the implementation-detail baseline where
it does not conflict with the newer freeze.

## Operating rule

Models perform bounded semantic judgment. The host owns identity, legality, state transitions, schemas, hashes, side effects, durable commits, and publication.

## Workspace map

- `project/STATUS.md` — live operating state and next actions
- `project/TODO_V0_1.md` — evidence-backed Phase 0–L execution ledger
- `project/DECISIONS.md` — append-only implementation decision log
- `src/arcadia/` — implementation root (begins in Phase A)
- `tests/` — deterministic and qualification tests
- 2026-08-29 canonical prototype bundle — non-conflicting implementation-detail baseline
- `architecture/v0.1/freeze-2026-09-04/` — current Recipe 0–8 architecture authority
- `manifests/architecture_freeze_v0_1_2026-09-04.json` — machine-readable freeze identity
- Obsidian bundle — navigable reference copy
- checkpoint ZIPs — recovery snapshots

No production claim should be made until the exact pinned runtime identity passes its required gates.

## Windows setup

Run `setup.bat` once to create the pinned Python 3.12 environment and install the
host/development dependencies. Use `activate.bat` for a development shell and
`check.bat` to run the environment, test, lint, and type-check gates.

Model weights and the libllama/CUDA runtime are intentionally a separate Phase
A3 setup because their exact identities must be pinned and qualified.

Run `check_architecture_freeze.bat` to execute the normal deterministic gates and
verify the exact frozen authority payload set.
