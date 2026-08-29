# Phase A Item 1 — Configuration and Identifiers

Date: 2026-08-29
Standing: **PASS — item complete; Gate A remains open**

## Authority implemented

- One immutable Config V1 object is loaded from `configs/runtime.toml`.
- Unknown fields, unsupported versions, type coercion, unsafe storage paths,
  missing real-runtime model paths, disabled FTS5, unbounded/negative budgets,
  nonstandard adapter application, and unserialized manager mutation fail closed.
- All frozen finite budget categories have explicit ceilings. Zero means that
  class of work is denied, not unlimited.
- Canonical identity is a non-nil, canonical lowercase UUID created by the host.
- Readable aliases carry a canonical scope, declared namespace, and positive
  fixed-width ordinal. They are audit labels and never global identity.
- The v0.1 recipe namespaces are registered without collisions. The `E001`
  turn-evidence alias and durable `E000001` semantic-entity alias remain distinct
  by kind, width, and canonical scope.
- Non-ASCII/confusable aliases, lowercase aliases, zero ordinals, wrong widths,
  wrong namespaces, path-like strings, uppercase/braced/compact UUID spellings,
  and the nil UUID are rejected.

## Evidence

Command: `check.bat`

```text
34 tests passed
Ruff: PASS
strict MyPy: PASS (6 source files)
```

Gate A remains open for Canonical JSON V1, hashing, envelopes, ledgers,
validation, bounded repair/work accounting, trace/trust registries, and storage.
