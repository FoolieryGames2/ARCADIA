# Phase A Item 4 — Artifact Envelope V1

Date: 2026-08-29
Standing: **PASS — item complete; Gate A remains open**

## Authority implemented

- New artifacts receive a canonical host-generated artifact UUID and carry
  canonical project and turn UUIDs; parsing reconstructs existing identities but
  never treats a readable alias as authority.
- Envelope V1 carries Recipe 0–8 identity, artifact type, optional turn-scoped
  alias, positive revision, and project/contract/schema/recipe/registry/runtime
  identity versions.
- Creation timestamps use one fixed real-UTC representation with six fractional
  digits. Naive, non-UTC, impossible, or alternate timestamp forms fail closed.
- Payloads are snapshotted as immutable Canonical JSON V1 text. Caller mutation
  after creation and mutation of a returned decoded value cannot alter the
  artifact.
- `content_hash` covers the canonical payload. `artifact_hash` covers every
  envelope field except itself, including payload, content hash, metadata, and
  ordered upstream basis references.
- Each basis reference carries exact artifact UUID, positive revision, and typed
  SHA-256 hash. Duplicate and self references are structurally rejected.
- Complete envelopes serialize and parse only as Canonical JSON V1 UTF-8. Missing
  fields, unknown fields, malformed identities, invalid aliases, unsupported
  versions, implicit type coercion, and non-canonical wire forms fail closed.
- Payload and whole-envelope hash verification use constant-time digest
  comparison. Tampering with either payload or metadata is detected.
- Repository existence, graph-cycle checks beyond direct self-reference, and
  recipe-specific payload validation remain assigned to later Phase A modules.

## Evidence

Command: `check.bat`

```text
126 tests passed
Ruff: PASS
strict MyPy: PASS (9 source files)
```

Envelope tests cover canonical round trips, immutable payload snapshots,
payload/metadata tampering, strict fields and versions, malformed and
non-canonical input, invalid UTF-8, alias scope, basis-reference identity/order,
host type coercion attacks, and fixed UTC timestamp validation.

Gate A remains open for the ledger, schema validation, bounded repair/work
accounting, trace/trust registries, and storage.
