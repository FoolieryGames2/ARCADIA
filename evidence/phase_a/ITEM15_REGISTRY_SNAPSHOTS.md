# Phase A Item 15 — Immutable Registry Snapshots

Date: 2026-08-30
Standing: **PASS — item complete; Gate A passes separately in E-0023**

## Authority implemented

- `RegistrySnapshot` accepts only a top-level strict JSON object, snapshots it as
  Canonical JSON V1, allocates a host UUID, and binds it to project UUID,
  canonical registry kind/version, contract/schema/recipe/registry/runtime
  identity versions, and canonical UTC creation time.
- The typed SHA-256 snapshot hash covers the complete unsigned record, including
  identity/scope metadata and registry content. Construction, wire round-trip,
  and durable decoding recompute that hash; mutable caller input and returned
  decoded values cannot mutate the sealed snapshot.
- `RegistrySnapshotRepository` is immutable and project-scoped. A project/kind/
  version can be assigned exactly once. Exact retries are idempotent; changed
  content under an existing UUID or kind/version conflicts, while another project
  owns an independent version namespace.
- Reads resolve exact snapshot UUID or exact registry kind/version. Bounded kind
  listing provides a chronological audit surface with a hard maximum of 200.
  The repository deliberately has no `latest`, `activate`, overwrite, or delete
  method: insertion time and lexical version text cannot silently gain runtime
  selection authority.
- Durable rows are decoded with strict UUID, canonical token, Canonical JSON,
  timestamp, typed hash, and full-hash verification. Malformed durable state is
  reported as repository integrity failure, distinct from caller field errors.
- Transcript, technical artifacts, semantic memory, AAE semantics, routing,
  runtime activation, and trust promotion remain outside this repository.

## Evidence

Commands: `check.bat` and `check_phase0.bat`

```text
417 tests passed
Ruff: PASS
strict MyPy: PASS (21 source files)
Phase 0 authority, dependency, model, llama.cpp, CUDA, and runtime hashes: PASS
```

The 35 registry snapshot tests cover schema readiness; strict immutable
repository identity; canonical creation, hashing, wire round-trip, and defensive
copies; kind/version and top-level-object constraints; unknown fields; content-
hash tampering; invalid JSON/time translation; exact store/load/version resolve;
idempotent retry; UUID and kind/version conflicts; independent project version
namespaces; cross-project isolation; bounded chronological kind listing; missing
reads; durable JSON/hash/timestamp corruption; strict arguments; and absence of
implicit activation or destructive methods.

This is the final exact-order Phase A file. Gate closure is recorded separately
in `PHASE_A_GATE_REPORT.md`.
