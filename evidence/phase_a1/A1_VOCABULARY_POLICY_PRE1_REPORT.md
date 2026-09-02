# A.R.C.A.D.I.A. — A1 Shared Vocabulary Policy PRE-1

**Date:** 2026-08-31
**Checklist:** #5
**Standing:** PRE-version implementation / jointly accepted policy / Gate A1 remains OPEN

## Accepted rule

A learned string field belongs to one of three classes:

1. **Closed enum** — exact host-behavior, routing, state, or canonically frozen verdict values.
2. **Pattern-bounded machine vocabulary** — descriptive machine labels such as reason codes when no complete canonical taxonomy is frozen.
3. **Bounded free text** — genuine language content; size/count limits are settings, not vocabulary taxonomy.

The host never allows an invented synonym to create a new control branch.

## Implementation

```text
src/arcadia/contracts/policies/vocabulary.py
tests/unit/contracts/policies/test_vocabulary.py
```

Recipe-0 mode/status fields are closed. `reason_codes[]` are pattern-bounded machine labels. `target_terms[]` and `unresolved_references[]` are bounded free text. The closed Recipe-0 status lists are sourced from the existing AAE registry rather than maintained as a separate authority list.

## Still open

This policy does not freeze complete vocabularies for later recipe schemas that do not exist yet. Each future schema must declare the appropriate class during construction/review.
