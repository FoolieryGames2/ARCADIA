# Phase A Item 6 — Strict JSON Schema Validation

Date: 2026-08-30
Standing: **PASS — item complete; Gate A remains open**

## Authority implemented

- The host compiles only schemas that explicitly declare the JSON Schema
  Draft 2020-12 dialect.
- Every object-shaped schema reachable through Draft 2020-12 structural and
  composition keywords must explicitly set `additionalProperties: false`.
  Non-strict schemas fail before an instance can be dispatched.
- Schema definitions must themselves use the strict JSON data model. They are
  snapshotted as Canonical JSON V1 and bound to a typed SHA-256 hash, schema ID,
  schema version, and host-validator version.
- Caller mutation after compilation cannot change the schema snapshot or its
  identity.
- Host values are checked against the strict JSON data model before schema
  evaluation. Text and byte entry points first use the existing strict decoder,
  preserving rejection of duplicate keys, non-finite numbers, trailing content,
  malformed JSON, invalid UTF-8, and unsupported host values.
- Known declared formats are asserted through the pinned validator's format
  checker. Type, enum, length, item-count, property-count, required-field, and
  other declared Draft 2020-12 constraints are enforced without applying
  defaults or mutating input.
- Validation returns all discovered issues in deterministic order. Each issue
  carries escaped JSON Pointer instance/schema locations, the failed keyword,
  and message. Reports bind the outcome to exact schema and instance hashes.
- `require_valid` fails closed with the complete report attached. The same
  immutable compiled schema supports typed host validation and strict parsed
  text/byte validation, enabling the frozen pre-render/post-render same-schema
  invariant. Final AAE extraction remains assigned to Phase A1.
- Reference existence, invented-ID detection, dangling/cyclic reference checks,
  and recipe semantics remain with their later host validators and repositories;
  this module grants no such authority.

## Evidence

Command: `check.bat`

```text
168 tests passed
Ruff: PASS
strict MyPy: PASS (11 source files)
```

Validation tests cover dialect and schema identity enforcement, invalid schema
definitions, immutable snapshots, root/nested/composed non-strict object
schemas, object type unions, format assertion, unknown properties, wrong types,
enums, length and item bounds, deterministic complete reports, JSON Pointer
escaping, no default mutation, schema/input hash binding, same-schema host/text
validation, strict decoder propagation, UTF-8 byte input, and non-JSON host
values.

Gate A remains open for repair policy, bounded work accounting, trace/trust
registries, and storage.
