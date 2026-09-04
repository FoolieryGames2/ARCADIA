# T0 Base-Model Lab CLI Evidence — 2026-09-04

## Standing

**PASS — qualification-only operator lab. Gate A3 remains open and runtime
authority remains T0.**

This checkpoint adds an easy local testing surface around the already pinned
Qwen3 base candidate. It does not implement `SpecialistInvoker`, attach a LoRA,
dispatch an AAE, write transcript or semantic memory, or qualify a logical mode.

## Implemented surface

- `run_arcadia.bat` starts the checked-in Python environment and executes
  `arcadia run`.
- `arcadia run "PROMPT"` performs one clean base-only inference and prints the
  visible model response beneath `ARCADIA>`.
- `arcadia run` opens an interactive prompt with `/config`, `/set`, `/reset`,
  `/verify`, `/help`, and `/quit` controls.
- Each interactive prompt is an independent experiment; no conversational
  history is retained by this direct lab boundary.
- Safe adjustable settings are context tokens, maximum output tokens,
  temperature, seed, GPU layers, and the test-only system prompt.
- Checked-in defaults are in `configs/lab.toml`. Persistent operator overrides
  are atomically replaced at `runtime-data/lab_settings.json`, which is excluded
  from Git. Command-line overrides are ephemeral.
- Settings reject unknown keys, invalid types, unsafe ranges, empty system
  prompts, and output budgets that do not leave context headroom.
- Runtime launch uses an argument vector without a shell and does not include a
  LoRA argument. Startup diagnostics stay separate from clean model output.

## Exact runtime verification

Command:

```bat
run_arcadia.bat --verify
```

Observed:

```text
PASS  model            bytes=2497279008
PASS  runtime          bytes=10752
PASS  cuda             C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.3\bin\x64\cublas64_13.dll
PASS  runtime_sha256   5a4693c7668115866188c5b0dd6dafdc28d56cb52b39f6b909c9ddfdc27090be
PASS  model_sha256     4e00d30a00c71456198672a86a155a2935a7201f5112734f7dbf564362243f73
```

## Live CUDA smoke

Command:

```bat
run_arcadia.bat "Reply with exactly: ARCADIA READY" --max-output-tokens 32 --temperature 0 --no-metrics
```

Observed:

```text
ARCADIA>
ARCADIA READY
```

## Deterministic gate

`check.bat` passed on Windows with:

- CPython 3.12.10 and SQLite 3.49.1/FTS5.
- 580/580 tests.
- Ruff clean.
- strict MyPy clean over 66 source files.

The new lab boundary contributes 14 focused tests for configuration parsing and
atomic persistence, strict override rejection, file/hash checks, subprocess
arguments, failed runtime behavior, clean output, ephemeral command-line
overrides, and the no-launch interactive exit path.

## Training firewall

The lab is not a data-ingestion path. Its prompts and responses remain ephemeral
unless a human separately reviews and admits material through the future frozen
training-export workflow. Held-out, adversarial, and composition fixtures remain
permanently separate under `NEVER_TRAIN` manifests.
