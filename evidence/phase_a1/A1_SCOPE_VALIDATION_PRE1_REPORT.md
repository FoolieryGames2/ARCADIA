# A.R.C.A.D.I.A. — A1 SCOPE_VALIDATION PRE-1 Report

**Checklist item:** #2 — Finish Recipe 0 / `SCOPE_VALIDATION`
**Standing:** PRE-version implementation for review; not dispatch authority
**Parent gate:** Phase A1 remains OPEN

## Source-grounded contract

The canonical Recipe-0 checkpoint asks one question after transcript retrieval:

> Can the current raw prompt now be interpreted without inventing missing conversational referents?

The frozen verdict vocabulary is retained exactly:

```text
SUFFICIENT
NEEDS_MORE_RECENT
NEEDS_TARGETED_HISTORY
UNRESOLVABLE_WITH_TRANSCRIPT
BOUND_EXHAUSTED
```

The trace freezes the model output top-level fields as exactly:

```text
mode
status
reason_codes[]
unresolved_references[]
```

PRE-1 deliberately does not invent a requested lookback count or targeted-search-term
field for the validator. The later host incremental-expansion policy must choose a
deterministic additional delta while staying inside the already frozen Recipe-0 bounds.

## Implemented

Added:

```text
src/arcadia/contracts/schemas/r0/scope_validation.py
tests/unit/contracts/schemas/r0/test_scope_validation.py
```

Updated:

```text
src/arcadia/contracts/schemas/r0/__init__.py
src/arcadia/contracts/aae/registry.py
project/TODO_A1_STRICT_SCHEMAS_POLICIES.md
```

### Strict CALL_DATA shape

Required top-level input fields:

```text
mode
turn_uuid
conversation_uuid
raw_user_prompt
frozen_retrieved_turns[]
host_policy_limits
```

Every frozen retrieved turn requires:

```text
turn_uuid
turn_index
user_message
final_response
user_message_hash
final_response_hash
```

The host-policy projection requires:

```text
remaining_expansion_cycles
max_total_injected_history_tokens
```

Unknown fields are rejected at every object boundary.

### Host semantic checks

PRE-1 additionally proves that:

- at least one retrieved turn exists before `SCOPE_VALIDATION` is invoked;
- retrieved turns are prior turns, never the current `turn_uuid`;
- retrieved `turn_uuid` values are unique;
- retrieved turns are in strictly increasing chronological `turn_index` order;
- exact user-message and final-response text matches each supplied tagged SHA-256 hash;
- `SUFFICIENT` carries an empty `unresolved_references[]`;
- every non-sufficient verdict preserves at least one unresolved reference;
- `NEEDS_MORE_RECENT` / `NEEDS_TARGETED_HISTORY` cannot request impossible expansion when `remaining_expansion_cycles == 0`.

### Deliberately still open

- Shared Origin / Trust policy (#3).
- Legal-reference policy (#4).
- Shared enum/vocabulary policy (#5).
- Shared FieldCaps policy (#6); this slice uses local PRE safety caps only.
- Repair-shape policy (#7).
- Next-consumer policy (#8).
- Deterministic host algorithm that chooses the exact additional recent/targeted delta.
- Full Recipe-0 Conversation Packet schema/build/freeze is outside this narrow checklist item.

## Authority status

The AAE registry remains `AAE-REGISTRY-PRE-1`; the contract remains
`dispatch_enabled=False`; schema refs remain `PRE-1` and unfrozen.
