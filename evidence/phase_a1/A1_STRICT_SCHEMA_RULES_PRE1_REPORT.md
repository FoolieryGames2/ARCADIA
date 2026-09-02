# A.R.C.A.D.I.A. — A1 Shared Strict-Schema Rules PRE-1

**Date:** 2026-08-30
**Standing:** PRE-version implementation / not frozen / Gate A1 remains OPEN

## Purpose

Record the first jointly reviewed schema-policy decisions before duplicating
contract schemas across the remaining logical specialist modes.

This patch is intentionally limited to numbered TODO item 1: shared strict-schema
rules. It does **not** implement `SCOPE_VALIDATION`, Origin/Trust, legal-reference,
field-cap, repair, or remaining recipe schemas.

## Reviewed decisions encoded

1. JSON Schema validates shape and syntactic legality.
2. Host semantic validation owns cross-field consistency, host state, and host-policy meaning.
3. Unknown object fields are rejected, never ignored.
4. Learned outputs use a fixed top-level field shape by default.
5. Branches change values rather than omitting/adding structural fields.
6. Fields that affect interpretation/downstream behavior are required.
7. Optional learned-output fields require an explicit future exception with defined absence semantics.
8. The model may choose values but may not choose its contract structure.
9. Silent truncation, correction, or implicit defaulting is forbidden at this boundary.
10. Impossible/dead-end downstream requests fail closed instead of continuing into pointless work.

## Executable policy

Added:

```text
src/arcadia/contracts/policies/schema_rules.py
src/arcadia/contracts/policies/__init__.py
tests/unit/contracts/policies/test_schema_rules.py
```

`STRICT_SCHEMA_POLICY_PRE_V1` is immutable and explicitly `PRE_VERSION`.
`STRICT_SCHEMA_POLICY_REGISTRY_PRE_V1` is an immutable registry mapping.

The executable `require_fixed_top_level_output_shape()` policy rejects learned
output schemas whose top-level properties are not all required. This makes the
reviewed rule concrete: branch-dependent values are legal; branch-dependent
omitted top-level fields are not the default contract shape.

## SCOPE_PROPOSAL integration

`SCOPE_PROPOSAL_OUTPUT_SCHEMA` is now compiled through the fixed-output-shape
policy.

The host semantic validator now also rejects history requests when
`completed_exchange_count == 0`. For contiguous recent retrieval it additionally
rejects `recent_exchange_count` values larger than the history that actually
exists. This prevents a known dead-end retrieval branch and avoids silent host
truncation.

The same history-existence rule applies to targeted transcript retrieval: a
specialist cannot request targeted prior-conversation evidence when there are no
completed prior exchanges.

## What remains deliberately open

- The shared policy is not frozen.
- Optional-field exceptions are not yet designed because no accepted case requires one.
- `SCOPE_VALIDATION` remains item 2.
- Origin/Trust remains item 3.
- Legal refs, enums, field caps, repair shape, and next consumers remain later numbered items.
- The remaining learned-mode schemas remain open.

See `project/TODO_A1_STRICT_SCHEMAS_POLICIES.md` for the numbered walk-through.

## Reproducible tests in this build workstation

Focused policy + Slice 01 schema/runtime tests:

```text
31 passed
```

Registry + policy + Slice 01:

```text
42 passed
```

Broader repository run excluding only this container's unavailable `hypothesis`
modules and the intentional Python-3.12 environment assertion:

```text
399 passed
```

`python -m compileall -q src tests` also passed.

The canonical Windows environment should run `check.bat` before checkpointing.
If the previously generated Slice 01 patch contributed 24 tests on top of the
user-verified 428-test registry baseline, this PRE-1 patch adds 7 more tests, for
an expected 459 collected tests when no parallel local changes alter the count.
