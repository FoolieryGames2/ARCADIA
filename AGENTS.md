# ARCADIA Workspace Instructions

## Authority

Before implementation, read the canonical prototype documents in their declared order. When sources conflict, follow the supersession rule in `00_README_FIRST.md`.

Do not silently revise the frozen v0.1 architecture. Record an explicit decision in `project/DECISIONS.md` when implementation reveals a needed clarification or change.

## Build discipline

- Follow `02_ARCADIA_V0_1_EXACT_BUILD_ORDER.md`; do not skip gates.
- Preserve the nine-recipe spine (Recipe 0 through Recipe 8).
- Keep deterministic host authority separate from learned semantic judgment.
- Treat learned authority as T0 until the exact runtime identity is qualified.
- Keep transcript, trace, Context, semantic memory, and training data distinct.
- Every loop, repair, re-entry, and work budget must be bounded.
- Never infer success from execution alone; preserve `OUTCOME_UNKNOWN` where side effects are uncertain.

## Engineering practice

- Put Python package code under `src/arcadia/` and tests under `tests/`.
- Add deterministic tests with each host component.
- Prefer strict schemas and fail-closed validation.
- Do not commit model weights, raw traces, secrets, local databases, or generated caches.
- Update `project/STATUS.md` when a gate changes standing.
- Append consequential choices to `project/DECISIONS.md`; do not rewrite history casually.
