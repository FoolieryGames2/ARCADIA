# A.R.C.A.D.I.A. — Phase A1 AAE Registry Pre-Version Build Report

**Date:** 2026-08-30  
**Status:** PRE_VERSION / REVIEW CANDIDATE / NOT DISPATCHABLE

Imported archive:

```text
patch_brige/ARCADIA_AAE_REGISTRY_PRE_V1_2026-08-30.zip
SHA-256: f56593dae71dd11b84b03c0f3bfd55b1f3f298423085c5b997bdfad4583288d1
```

All 12 archive entries were verified as unique, relative paths without parent
traversal before extraction. Two Python 3.12/Ruff modernization-only import
changes were applied (`Mapping` from `collections.abc`); registry semantics were
not changed during integration.

## Scope built

Implemented the AAE registry scaffolding only. This deliberately does **not** claim completion of the full Phase A1 serializer/schema/CALL_DATA-gate work.

Created:

```text
src/arcadia/contracts/__init__.py
src/arcadia/contracts/aae/__init__.py
src/arcadia/contracts/aae/types.py
src/arcadia/contracts/aae/global_awareness.py
src/arcadia/contracts/aae/registry.py
tests/unit/contracts/aae/test_registry.py
evidence/phase_a1/AAE_REGISTRY_PRE_VERSION_REVIEW.md
```

## Registry shape

- 15 physical adapter semantic identities.
- 20 independently identified logical modes.
- 2 Conversation Resolver modes.
- 5 Conversational Howard modes.
- Recipe 4 / Tool Execution has no learned registry entry.
- One shared Global Awareness candidate (`GA-PRE-1`).
- Every record is immutable, `PRE_VERSION`, and `dispatch_enabled=False`.
- Schema IDs and inference-profile IDs are candidate references only and explicitly unfrozen.
- Field/token caps and minimum trust levels remain unresolved rather than guessed.
- Runtime lifecycle fields (paths, hashes, handles, residency, leases, VRAM telemetry) are absent by design.

## Validation performed in this workstation

Registry-only test command on the pinned project environment:

```text
.venv\Scripts\python.exe -m pytest tests/unit/contracts/aae/test_registry.py -q
```

Result:

```text
11 passed
```

Complete repository validation:

```text
428 tests passed
Ruff: PASS
strict MyPy: PASS (26 source files)
CPython 3.12.10 environment gate: PASS
```

Phase 0 regression:

```text
check_phase0.bat: PASS
45/45 frozen authority files verified
dependency/config/model/llama.cpp/CUDA/runtime hashes: PASS
```

## Review-first decisions

The following are intentionally not silently frozen:

- exact final logical-mode string names;
- exact schema bodies;
- complete field/token caps;
- complete inference profile values/hashes;
- minimum trust thresholds;
- enum sets that recipe prose did not fully freeze;
- repair counts where the source did not clearly establish one contract-specific final value.

This keeps the next joint review honest: accepting this registry means accepting its semantic boundaries and names, not accidentally accepting guessed runtime limits.
