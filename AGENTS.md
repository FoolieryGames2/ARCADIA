# ARCADIA Workspace Instructions

## Authority

Before implementation, read the current architecture freeze in
`architecture/v0.1/freeze-2026-09-04/` in this order:

1. `README_FIRST.md`;
2. `ARCADIA_V0_1_FULL_ARCHITECTURE_FREEZE_CHECKPOINT_2026-09-04.md`;
3. `ARCADIA_V0_1_BUILD_HANDOFF_2026-09-04.md`;
4. the applicable document under `frozen_architecture/`.

Then use the earlier canonical prototype documents in their declared order for
implementation detail where they do not conflict. When sources disagree, follow
the precedence in the 2026-09-04 handoff. Historical/reference bundles are audit
sources, not current architecture authority.

Do not silently revise the frozen v0.1 architecture. Record an explicit decision in `project/DECISIONS.md` when implementation reveals a needed clarification or change.

## Build discipline

- Follow `02_ARCADIA_V0_1_EXACT_BUILD_ORDER.md`; do not skip gates.
- Preserve the nine-recipe spine (Recipe 0 through Recipe 8).
- Keep deterministic host authority separate from learned semantic judgment.
- Treat learned authority as T0 until the exact runtime identity is qualified.
- Treat `Qwen/Qwen3-4B-Instruct-2507` as the locked v0.1 starting model family;
  exact GGUF, llama.cpp, sampler, context, and residency identities remain unqualified.
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
