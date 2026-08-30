# Phase A Item 2 — Canonical JSON V1 and Strict Decoding

Date: 2026-08-29
Standing: **PASS — item complete; Gate A remains open**

## Authority implemented

- Canonical JSON V1 emits deterministic UTF-8 bytes with Unicode preserved,
  keys sorted, compact separators, and no BOM or trailing newline.
- The encoder accepts only the exact JSON host data model. Unsupported key or
  value types, non-finite floats, lone surrogates, cycles, and excessive nesting
  fail closed instead of being coerced.
- The strict decoder rejects malformed JSON, illegal escapes, duplicate decoded
  keys, `NaN`, infinities, exponent overflow such as `1e9999`, trailing content,
  non-JSON whitespace, a BOM, and invalid UTF-8.
- Canonical-input validation reparses and re-encodes the value, then requires an
  exact match with the supplied representation.
- Unicode normalization is not performed: distinct source strings remain
  distinct data while producing a stable representation for the same value.
- Hashing is intentionally deferred to the next frozen Phase A item.

## Evidence

Command: `check.bat`

```text
73 tests passed
Ruff: PASS
strict MyPy: PASS (7 source files)
```

The tests cover deterministic encoding, ordering, Unicode, all supported JSON
values, duplicate-key escape equivalence, malformed and trailing input,
non-finite values and overflow, BOM/UTF-8 failures, unsupported Python values,
cycles, depth limits, and canonical round trips.

Gate A remains open for hashing, envelopes, ledgers, schema validation, bounded
repair/work accounting, trace/trust registries, and storage.
