# A.R.C.A.D.I.A. — Phase A1 PRE-08 Handoff Reconciliation

## Source checkpoint

- Archive: `patch_brige/ARCADIA-main_A1_PRE_08_NEXT_CONSUMERS_2026-08-31.zip`
- Archive size: `1,046,017` bytes
- SHA-256: `a72be5a88a9f0c9c9f687995ad2d7cf4e832d4c0415d0f2f378f3120215af1f8`
- Safety review: 248 file entries, zero unsafe paths, zero duplicate paths.
- Isolated archive verification: 538 tests passed under the canonical workspace Python 3.12 environment with the archive's `src` tree selected explicitly.

## Reconciliation boundary

The archive was treated as a checkpoint handoff, not as an authoritative blind overlay.
Twenty-eight genuinely new source, test, configuration, evidence, and A1 checklist files
were imported. Shared AAE and Recipe 0 files were merged into the newer local checkpoint
so the existing hardened CALL_DATA tests, Windows environment evidence, Phase 0 manifest,
storage fixes, Git history, and local evidence/decision numbering were preserved.

Machine-specific and stale checkpoint files were not overlaid, including `.pytest_cache`,
Phase 0 inputs/evidence, setup scripts, storage modules, and the existing project ledgers.

## PRE-08 surface now present

- Shared strict-schema rules with a fixed top-level learned-output shape.
- Strict Recipe 0 `SCOPE_VALIDATION` input/output schemas and semantic integrity checks.
- Origin/trust, legal-reference, vocabulary, repair-shape, and next-consumer policy registries.
- A separate strict, deterministic AAE tuning-settings handler and PRE-1 TOML source.
- Registry-owned settings-profile and origin/trust-policy references for all 20 logical modes.
- Repair semantics separated from tunable numeric attempt limits.
- Additional `SCOPE_PROPOSAL` history-existence and available-history bounds.
- Host-owned downstream selection; legal edges do not imply dispatch authorization.

## Canonical workstation verification

Executed from `D:\ARCADIA` on CPython 3.12.10:

```text
focused contracts/settings tests: 108 passed
full pytest suite:                538 passed
Ruff:                             PASS
strict MyPy:                      PASS (43 source files)
check.bat:                        PASS
check_phase0.bat:                 PASS
Phase 0 authority files:         45/45 verified
llama.cpp source:                 exact pinned commit verified
native runtime artifacts:        7/7 verified
```

## Standing

This evidence accepts the PRE-08 checkpoint only as Phase A1 PRE-version implementation.
The registry remains non-dispatchable, runtime authority remains T0, and Gate A1 remains
open. Recipe 1–3 and Recipe 5–8 strict schemas, complete settings profiles, deterministic
context projection, registry-wide same-source training/runtime proof, and the joint freeze
review are still required.
