# Windows development setup

## One-command host setup

Run `setup.bat` from the repository root. It creates `.venv` with Python 3.12,
installs the pinned host/development dependencies, creates a local `.env`, and
runs the environment, test, lint, and type-check gates.

Use `activate.bat` for an activated command prompt and `check.bat` to rerun all
local gates. All three scripts are safe to rerun.

## Current runtime boundary

The initial environment deliberately uses `backend = "test_double"`. No model
or LoRA has been selected, downloaded, or qualified, and no runtime dependency
is allowed to imply otherwise.

This workstation has an NVIDIA RTX 2060 with 6 GB VRAM. A later Phase A3 setup
must pin all of the following before installation:

- base GGUF URL and SHA-256;
- physical LoRA URLs and SHA-256 values;
- llama.cpp repository commit and build options;
- CUDA toolkit/build-tool versions or an exact compatible binary distribution;
- the realized library hash and qualification identity.

Installing `llama-cpp-python` ad hoc is not the pinned libllama runtime required
by the design. It may be used for an exploratory spike only if recorded as a
separate, unqualified runtime identity.
