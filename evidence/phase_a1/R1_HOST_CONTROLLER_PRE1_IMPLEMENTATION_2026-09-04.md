# A.R.C.A.D.I.A. — Recipe 1 Host Controller PRE-1 Implementation Checkpoint

Date: 2026-09-04
Standing: implementation checkpoint only; not runtime-qualified and not a registry freeze

## Scope implemented

This checkpoint adds the first host controller after Recipe 0 without changing the frozen
Recipe 0–8 architecture:

- recipe-facing `SpecialistInvoker` protocol boundary;
- Recipe 1 `Spell -> Term / Meaning -> Prompt Analyst -> Intent Organizer` orchestration;
- optional `Intent Comment` presentation call after the machine Intent artifact is frozen;
- deterministic host source-span allocation (`Sxxx`);
- host canonicalization of accepted Meaning local keys to `Txxx`;
- host canonicalization of Organizer requirement local keys to `Rxxx`;
- local dependency validation and canonical dependency rewrite;
- source-reference, capability-reference, control-signal, and dependency-cycle gates;
- machine Intent artifact hashing that excludes non-authoritative presentation prose.

## Authority preserved

The implementation does not grant the model authority to:

- allocate authoritative `Sxxx`, `Txxx`, or `Rxxx` aliases;
- invent source refs outside the current host-built span map;
- nominate capabilities that are absent from the supplied host capability registry;
- create dependency cycles or dangling requirement dependencies;
- mutate Prompt Analyst control signals inside Organizer;
- place Intent-comment prose into the downstream machine handoff.

Recipe 1 remains dependent on a host-owned `SpecialistInvoker`; this checkpoint defines the
recipe-facing protocol but does not claim a real runtime, adapter manager, residency policy,
repair loop, or T0+ authority.

## Tests added

`tests/unit/recipes/r1/test_controller.py`

Focused result in the available sandbox:

```text
6 passed
```

Broader executable suite result:

```text
526 passed
```

The broader command excludes three environment-only blockers in this sandbox:

- `tests/unit/core/test_canonical_json.py` — Hypothesis is not installed;
- `tests/unit/core/test_ids.py` — Hypothesis is not installed;
- `tests/unit/test_environment.py` — sandbox Python is 3.13, while ARCADIA pins CPython 3.12.

The sandbox has no package-network access, so Ruff, MyPy, and the missing Hypothesis package
could not be installed here. The canonical Windows `check.bat` gate must be rerun in the
project's pinned environment before merge/qualification claims.

## Next implementation slice

Implement the concrete qualification-only `SpecialistInvoker` path and connect it to the
resident Qwen3 CUDA backend. Then run Recipe 1 base-only end-to-end and capture exact call data,
raw model output, parsed output, host-validation outcome, timing, token counts, and failure/
repair evidence for each of the five modes.
