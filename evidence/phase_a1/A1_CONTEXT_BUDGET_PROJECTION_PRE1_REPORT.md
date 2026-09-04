# A1 deterministic context-budget projection PRE-1 report

Date: 2026-09-04

Standing: **PASS for the shared deterministic projection boundary; Gate A1 remains open, registry dispatch remains disabled, and runtime authority remains T0.**

## Implemented boundary

`aa_runtime/context_projection.py` accepts only complete, schema-valid AAE
CALL_DATA candidates bound to the contract's projection-policy identity. Candidate
ranks must be unique and contiguous from zero. The boundary selects the first
whole candidate that satisfies all configured limits.

It does not edit candidate content. It never slices a string, shortens an array,
drops a field, estimates tokens from character counts, or treats an unresolved
limit as unlimited. Recipe-owned controllers remain responsible for constructing
semantically sufficient full/reduced candidates and recording omitted item refs.

## Enforced limits and evidence

For each evaluated candidate the host records:

- canonical CALL_DATA hash;
- exact model-input token count supplied by the pinned tokenizer/chat-template boundary;
- maximum string length, array size, nesting depth, and declared source-excerpt length;
- omitted item references;
- every deterministic rejection reason.

Selection reserves the configured maximum output tokens and context headroom
inside the supplied inference context window. If settings are incomplete, the
result is `SETTINGS_INCOMPLETE` with exact missing field names and token counting
does not run. If no whole candidate fits, the result is `BUDGET_EXHAUSTED` with
no dispatchable call. Successful evidence is Canonical-JSON hash bound.

The checked-in PRE-1 settings deliberately remain incomplete pending measured
InferenceProfiles, so they correctly produce `SETTINGS_INCOMPLETE`; this report
does not invent final token limits.

## Registry identity

All 20 learned modes carry unique `context_projection_policy_id` values.
`manifests/aae_context_projection_pre1.json` freezes the PRE-1 algorithm identity,
registry binding, exact-count rule, overflow standing, and mode-to-policy mapping.
Recipe 4 remains host-only and has no learned-mode entry.

## Tests

Focused tests cover:

- full-first then explicitly ranked reduced-candidate selection;
- exact final-role-message token counts;
- output reservation and context headroom;
- string, real transcript-array, nesting, and source-excerpt bounds;
- immutable whole-candidate behavior with no silent truncation;
- incomplete settings before token counting;
- typed exhaustion with no dispatchable call;
- policy/profile/mode/rank mismatch rejection;
- invalid token-counter results;
- exact 20-mode manifest/registry agreement.

## Remaining A1 work

- Prove runtime and training materialize contracts from the same registry source.
- Supply recipe-owned semantic candidate builders as their controllers are implemented.
- Replace unresolved PRE-1 numeric limits with measured per-mode settings and immutable InferenceProfiles.
- Complete joint freeze review before enabling dispatch or changing trust.
