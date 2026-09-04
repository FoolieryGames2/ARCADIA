# A.R.C.A.D.I.A. v0.1 — Architecture Freeze Intake

**Date:** 2026-09-04
**Standing:** PASS — architecture authority intake only; implementation and runtime qualification remain open

## Source handoff

```text
archive: ARCADIA_V0_1_FULL_ARCHITECTURE_FREEZE_BUILD_HANDOFF_2026-09-04.zip
bytes: 3784335
sha256: ee24e082df3b24e93b47de371dcc4d87ee2a81c048413dea502dca02fec900a4
```

The outer archive contained 29 safe entries with no duplicate or traversal paths.
Its `SHA256SUMS.txt` declared 28 payloads; all 28 hashes reproduced exactly. All
seven nested ZIP references were independently inspected and contained no unsafe
or duplicate paths.

## Repository intake

The handoff was imported byte-for-byte beneath:

`architecture/v0.1/freeze-2026-09-04/`

The existing 2026-08-29 authority, Phase 0 evidence, and Qwen2.5 runtime spike were
preserved as immutable history. They were not rewritten. The new freeze controls
architecture when it conflicts with those historical sources.

`manifests/architecture_freeze_v0_1_2026-09-04.json` binds the source archive
identity, exact authority root, SHA manifest identity, authority precedence, model
family supersession, T0 standing, and open A1 standing. The deterministic verifier
requires all 28 payload hashes and the exact 29-file authority tree—no missing or
extra files.

## Accepted supersession

- Active starting model family: `Qwen/Qwen3-4B-Instruct-2507`.
- Qwen2.5 3B Q4_K_M evidence: retained as a successful historical Phase 0 runtime spike only.
- Exact Qwen3 GGUF quantization/hash, llama.cpp commit/build, context/sampler profiles,
  and adapter residency strategy: explicitly unqualified until A3 measurement.
- `Howard`: only the specific Howard conversational adapter/personality, not Arcadia,
  the foundation model, or generic specialists.
- Recipe 0 one-next-turn `AWAITING_USER_INPUT` continuation correction: accepted
  architecture; implementation remains open.
- The generic model-download command now fails closed; reproducing the historical
  Qwen2.5 artifact requires the explicit `-HistoricalQwen25Spike` switch.

## Verification

The source archive and imported payload were both verified with
`scripts/verify_architecture_freeze.py`.

```text
CPython:                         3.12.10
full deterministic suite:       540 passed
Ruff src/tests:                  PASS
strict MyPy src:                PASS (43 source files)
freeze-verifier Ruff:            PASS
freeze-verifier strict MyPy:     PASS
declared freeze payload hashes:  28/28 verified
exact freeze authority file set: 29 files
source archive identity:         PASS
generic model downloader guard:  PASS (fails closed without historical opt-in)
legacy authority files:          45/45 verified
legacy runtime artifacts:        7/7 verified
```

`check_architecture_freeze.bat` passed. The legacy Phase 0 verifier also passed
against its exact historical Qwen2.5/llama.cpp identity; that result does not
qualify or select the new Qwen3 deployment identity. This evidence changes no
implementation gate and grants no learned authority.
