# Interactive Recipe Mode Control — 2026-09-04

## Standing

**PASS — operator routing correction only; T0 authority unchanged.**

Recipe mode is the checked-in default. Direct mode remains available explicitly.
This checkpoint does not implement Recipe 1–8, adapter loading, or production
authority.

## Corrected behavior

- `run_arcadia.bat` opens in `recipe` mode unless a Git-ignored local override
  intentionally selects another mode.
- `/mode recipe` and `/mode direct` switch and persist the interactive route.
- `--mode recipe` and `--mode direct` are accepted as forgiving in-session
  aliases instead of being sent to the model.
- `/recipe PROMPT` and `/direct PROMPT` route one call explicitly.
- `/status` reports the active mode and honest implemented recipe span.
- `/restart` closes the owned resident process and reloads saved runtime
  settings.
- Resident startup fails when the configured loopback port is already occupied;
  it cannot claim another process's health response as its own readiness.

## Reproduction

```text
run_arcadia.bat
/status
/mode direct
/status
--mode recipe
/status
/quit
```

The observed mode sequence was `recipe`, `direct`, then `recipe`, with no mode
command reaching model generation. A clean resident lifecycle test loaded the
pinned CUDA runtime, exited its context, and found no ARCADIA `llama-server.exe`
process afterward.

## External-build wiring baseline

Code built outside Codex should target the repository checkpoint tagged
`v0.1-cli-recipe-default-2026-09-04`. Integrations should call the typed
`arcadia run` command boundary or the recipe/controller APIs under
`src/arcadia/`; they must not move recipe authority into the batch wrapper or
interactive parser. Returned patches should include their base commit and avoid
generated model/runtime artifacts.

## Gate impact

The complete deterministic gate passed 588 tests, Ruff, and strict MyPy over 69
source files. Gate A1 and Gates A2/A3 remain open.
