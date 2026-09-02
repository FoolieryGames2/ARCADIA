# A.R.C.A.D.I.A. — A1 Next-Consumer Rules PRE-1

**Date:** 2026-08-31
**Standing:** PRE-version implementation / not frozen / Gate A1 remains OPEN

## Purpose

Encode numbered A1 strict-schema/policy TODO item 8: the registry defines the legal outgoing graph from each learned specialist boundary, while deterministic host control alone chooses which legal edge is actually traversed.

## Encoded behavior

- All 20 learned logical modes receive a PRE-1 next-consumer policy derived from their immutable `next_legal_consumers` registry field.
- Every referenced consumer identity must independently resolve as either a registered deterministic host stage or a learned-consumer alias bound to an existing logical specialist mode.
- The host-stage identity registry is independent of the AAE edge list so a typo/new host route does not self-authorize by appearing in the contract being validated.
- Learned-consumer aliases resolve to canonical logical specialist-mode IDs; they do not directly operate adapters.
- Only `RouteSelector.HOST` may authorize traversal. `MODEL_OUTPUT` is rejected even for an otherwise legal edge.
- Consumer identity matching is exact and case-sensitive.
- Illegal cross-lane edges fail closed.
- Passing this gate proves routing legality only. It does not make a PRE-version target dispatchable and cannot bypass downstream schema, trust, settings, qualification, or runtime gates.
- Empty legal-consumer tuples remain representable for future terminal learned boundaries; the current PRE registry happens to route every learned result back through at least one host/consumer stage.

## Files

```text
src/arcadia/contracts/policies/next_consumers.py
src/arcadia/contracts/policies/__init__.py
tests/unit/contracts/policies/test_next_consumers.py
project/TODO_A1_STRICT_SCHEMAS_POLICIES.md
project/DECISIONS.md
```

## Still open

- This is PRE-1, not a frozen full recipe router.
- Host-stage implementations and actual recipe controllers remain later build work.
- Host-stage-to-learned-mode routing is not invented here; this policy covers the learned-boundary outgoing edges already recorded by the AAE registry.
- The remaining Recipe 1–8 strict schemas and final cross-contract integrity gate remain open.

## Reproducible tests in this build workstation

Focused registry/policy/R0/settings/repair suite:

```text
138 passed
```

Broader runnable repository suite, excluding only this container's unavailable
`hypothesis` modules and the intentional canonical Python-3.12 environment gate:

```text
478 passed
```

Compilation:

```text
python -m compileall -q src tests
PASS
```

The canonical Windows `check.bat` remains the acceptance gate because that environment
has the pinned Python 3.12 toolchain and Hypothesis dependency.
