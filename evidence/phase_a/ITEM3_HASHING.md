# Phase A Item 3 — Hashing

Date: 2026-08-29
Standing: **PASS — item complete; Gate A remains open**

## Authority implemented

- SHA-256 identities are immutable typed values rendered as `sha256:` followed
  by exactly 64 lowercase hexadecimal characters.
- Digest parsing rejects missing or alternate algorithm tags, uppercase hex,
  wrong lengths, non-hex characters, surrounding whitespace, and raw untagged
  digests.
- Raw bytes are hashed exactly. Text is strict UTF-8 with no Unicode or newline
  normalization. Invalid Unicode scalars and implicit byte coercions fail closed.
- Structured values are encoded with Canonical JSON V1 before hashing; mutable
  pretty-printed or insertion-ordered JSON text is never substituted silently.
- Ordered chunks, binary streams, and regular files are hashed incrementally so
  large artifacts do not require whole-file memory loading.
- Verification compares canonical tagged digests in constant time and reports a
  mismatch without mutating or replacing the expected identity.
- Raw and normalized comparison payloads remain separate caller-owned inputs;
  the hashing module never discards or silently transforms source evidence.

## Evidence

Command: `check.bat`

```text
102 tests passed
Ruff: PASS
strict MyPy: PASS (8 source files)
```

The tests cover published SHA-256 vectors, strict digest syntax, exact UTF-8 and
newline behavior, Unicode non-normalization, Canonical JSON equivalence,
different raw JSON representations, chunk boundaries, stream position and
chunk sizing, file hashing and mismatch verification, and fail-closed type
handling.

Gate A remains open for artifact envelopes, ledgers, schema validation, bounded
repair/work accounting, trace/trust registries, and storage.
