# A.R.C.A.D.I.A. v0.1 — Recipe 0 Conversation Resolver

**Question:** What prior conversation evidence, if any, is required so Intent can interpret the current raw user prompt without inventing missing conversational references?

# 1. Scope

Recipe 0 is transcript resolution only. It does not query durable semantic memory, create Intent requirements, execute tools, or answer the user.

# 2. Input

```text
turn_uuid
conversation_uuid
raw_user_prompt
transcript metadata
host policy bounds
```

# 3. Learned allocation

One physical `Conversation Resolver` adapter may expose independently qualified modes:

```text
SCOPE_PROPOSAL
SCOPE_VALIDATION
```

Every attempt uses the shared SpecialistInvoker/AAE/InferenceProfile boundary.

# 4. Proposal outcomes

```text
SUFFICIENT_WITHOUT_HISTORY
REQUEST_RECENT
REQUEST_TARGETED
```

Recent scope is measured in completed user/final-response exchanges. Explicit “remember/earlier/we decided” language increases the obligation to resolve history but does not automatically justify a large contiguous window.

# 5. Host retrieval

- recent exchange retrieval is chronological;
- expansion retrieves only the delta;
- targeted lookup uses transcript FTS within authorized conversation/user scope;
- model never emits raw SQL;
- candidate turns carry exact UUID/hash identity.

# 6. Validation outcomes

```text
SUFFICIENT
NEEDS_MORE_RECENT
NEEDS_TARGETED_HISTORY
UNRESOLVABLE_WITH_TRANSCRIPT
BOUND_EXHAUSTED
```

# 7. Configurable prototype bounds

```text
max_contiguous_lookback_exchanges = 20
max_targeted_candidate_turns_per_search = 8
max_scope_expansion_cycles = 3
max_total_injected_history_tokens = model-safe host budget
```

# 8. Output

`CONVERSATION_PACKET` includes resolver run/revision, turn/conversation IDs, raw prompt hash, transcript commit sequence, exact included recent/targeted turn identities+hashes, unresolved refs, status, validation, and packet hash.

# 9. Handoff

Intent receives:

```text
EXACT RAW USER PROMPT
+
VALIDATED CONVERSATION_PACKET
```

Recipe 0 does not rewrite the prompt or replace transcript evidence with an invented summary.

# 10. Failure

If transcript bounds cannot resolve a reference, Intent receives the raw prompt plus explicit unresolved state. It must preserve uncertainty rather than guess; later Context/durable memory/user clarification may resolve it under their own authority.

# 11. v0.1 performance rule

When `fast_path_enabled=true` and the host proves an exact D0 response before history resolution is semantically necessary, the deterministic path may bypass Recipe 0's learned call while still creating auditable host artifacts. When the toggle is OFF, the normal learned-eligible path is used.
