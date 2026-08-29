# ARCADIA Decision Log

Append decisions. Keep prior entries intact; supersede them explicitly.

## D-0001 — Workspace authority boundary

- Date: 2026-08-29
- Status: accepted
- Decision: Keep the delivered v0.1 prototype bundle unchanged as canonical design authority. Use the workspace root for live implementation and operating records.
- Reason: This preserves the validated checkpoint while allowing implementation state to evolve visibly.

## D-0002 — Implementation root

- Date: 2026-08-29
- Status: accepted
- Decision: Place Python implementation under `src/arcadia/` and tests under `tests/`.
- Reason: A conventional package boundary supports deterministic testing and prevents working code from being mixed into the frozen documentation bundle.

## D-0003 — Python host baseline

- Date: 2026-08-29
- Status: accepted
- Decision: Pin the deterministic host development environment to CPython 3.12 and install it in the repository-local `.venv`.
- Reason: Python 3.12 is already installed on the workstation and has the safer native-package compatibility surface for the later Windows model-runtime spike than the current free-threaded Python 3.13 default.

## D-0004 — Separate host and model-runtime setup

- Date: 2026-08-29
- Status: accepted
- Decision: Make the host/test-double environment operational before installing libllama, CUDA build dependencies, models, or LoRAs.
- Reason: The frozen build order requires deterministic host gates before the real runtime spike, and runtime dependencies cannot be qualified until their exact source and build identities are pinned.
