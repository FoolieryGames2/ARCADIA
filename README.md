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

The Qwen3 source-integrity verifier and qualification-only CUDA candidate setup
are now reproducible with:

```bat
verify_qwen3_source.bat
prepare_qwen3_runtime.bat -Smoke
```

For a fast smoke rerun after the one-time conversion/build:

```bat
prepare_qwen3_runtime.bat -SkipDependencies -SkipBuild -SkipConversion -SkipQuantization -Smoke
```

Run the pinned runtime's 43 registered native tests with `-NativeTests`. This
test set includes an exhaustive CUDA backend operation matrix and can take
several minutes on the RTX 2060.

This is explicit `BASE_ONLY_TEST_MODE` infrastructure. It does not dispatch an
AAE, apply a LoRA, or promote runtime authority above T0.

## Local ARCADIA test lab

After the Python environment and Qwen3 runtime are prepared, double-click
`run_arcadia.bat` or run it from a terminal:

```bat
run_arcadia.bat
```

That opens a simple interactive prompt in `recipe` mode, the checked-in default.
The current recipe harness executes the real zero-history Recipe 0 boundary and
stops explicitly at `R1 NOT_IMPLEMENTED`. The lab remains labeled
`T0 BASE_ONLY_TEST_MODE`; each prompt is an independent experiment and this
surface does not retain conversational history or create a shadow transcript.

Prepare the pinned resident CUDA server once after the base runtime build:

```bat
prepare_qwen3_server.bat
```

The default `resident` transport pays the model-load cost once when the lab
opens, then reuses the loaded model weights for fast stateless requests. Use
`--transport process` only when testing the original one-process-per-prompt
boundary.

Useful one-shot commands:

```bat
run_arcadia.bat "Explain what ARCADIA is in one sentence."
run_arcadia.bat --show-settings
run_arcadia.bat --set temperature 0.4
run_arcadia.bat --reset-settings
run_arcadia.bat --verify
run_arcadia.bat "Test this turn" --mode recipe
run_arcadia.bat "Talk directly to the model" --mode direct
```

Inside the interactive lab, use `/mode recipe` or `/mode direct` to switch the
persistent default without closing ARCADIA. `/recipe PROMPT` and
`/direct PROMPT` route one prompt explicitly. `/status`, `/config`,
`/set NAME VALUE`, `/reset`, `/restart`, `/verify`, `/help`, and `/quit` provide
the remaining controls. Persistent operator overrides are stored only in the
Git-ignored `runtime-data/lab_settings.json`; checked-in safe defaults remain in
`configs/lab.toml`. One-shot flags such as `--temperature 0.7`, `--seed 9`, or
`--max-output-tokens 512` do not change saved settings.
If an older local override still opens in direct mode, enter `/mode recipe` or
run `run_arcadia.bat --reset-settings` once.

`--mode direct` preserves the direct model line. Recipe mode is the default and
`--mode recipe` currently
executes the real zero-history Recipe 0 boundary through the qualification-only
base invoker, prints its validated trace and activation receipt, and stops
honestly at `R1 NOT_IMPLEMENTED`. It is the first executable slice toward the
full Recipe 0–8 base-model harness; it does not claim the later recipes ran.

The resident launcher refuses to start when its configured loopback port is
already occupied. This prevents a new CLI session from silently adopting a
stale or unrelated server process.

Run `check_architecture_freeze.bat` to execute the normal deterministic gates and
verify the exact frozen authority payload set.
