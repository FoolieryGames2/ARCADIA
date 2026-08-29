# A.R.C.A.D.I.A. — PERF-01 Deterministic Fast Path + Runtime Toggle Lock

**Date:** 2026-08-29  
**Status:** LOCKED DESIGN RESOLUTION  
**Source finding:** Independent R3 stress test §6, Product-level stress: call amplification.

## 1. Problem

The five R3 slices demonstrate unacceptable learned-call amplification for simple tasks. The strongest example is a self-contained exact-literal response requiring 13 learned calls even though the host already possesses the exact requested output. The stress test requires deterministic fast paths for syntactically provable cases while preserving authoritative artifacts and auditability.

Performance optimization must not weaken A.R.C.A.D.I.A.'s authority boundaries, traceability, or qualification discipline.

## 2. Locked principle

> A.R.C.A.D.I.A. MUST NOT invoke a learned specialist when the required artifact or transition is completely derivable by an enabled deterministic host proof rule from authoritative inputs.

A deterministic fast path is an optimization of execution, not an alternate authority system. It MUST create the authoritative artifact lineage that the corresponding normal path requires and MUST record the exact proof rule that justified learned-call elision.

## 3. Explicit runtime toggle

The deterministic fast path is controlled by a host-owned runtime setting:

```text
fast_path_enabled: boolean
```

Required behavior:

```text
fast_path_enabled = true
    -> eligible allowlisted deterministic proof rules MAY short-circuit learned-eligible semantic calls.

fast_path_enabled = false
    -> deterministic fast-track short-circuiting is forbidden.
    -> the turn follows the ordinary Recipe 0–8 path and invokes every learned specialist that the normal recipe contracts require.
```

The toggle MAY be changed for testing or normal operation through owner/runtime configuration. The setting in force for a turn is snapshotted at turn start and MUST NOT silently change mid-turn.

Recommended initial operational policy:

```text
prototype / adapter qualification / end-to-end contract testing:
    fast_path_enabled = false

normal runtime after deterministic-path qualification:
    fast_path_enabled = true
```

The user/operator may intentionally run normal use with the fast path disabled.

## 4. What disabling fast track does NOT disable

`fast_path_enabled = false` is a performance/testing control, not a safety bypass.

The following remain host-owned and mandatory regardless of toggle state:

- schema validation;
- canonical serialization;
- reference/hash validation;
- Literal Lock;
- tool/execution authority;
- transaction and receipt rules;
- runtime health gates;
- adapter lifecycle safety;
- source-policy terminal gates;
- persistence authority;
- publication authority;
- stages that are structurally host-only by architecture.

The toggle MUST NOT create model calls for operations that are forbidden to models. For example, Tool/Execution remains host-owned even in full-pipeline testing.

## 5. Fast-path eligibility

Fast path is allowlist-based. A rule may execute only when the host can syntactically and deterministically prove all required semantics for that rule.

Initial example:

```text
proof_rule_id: EXACT_LITERAL_RESPONSE_V1
input: "Reply with exactly: Ready."
output literal: "Ready."
```

No learned model is required to rediscover the literal.

If any ambiguity, semantic interpretation, unsupported syntax, unresolved reference, or missing authoritative input exists:

```text
FAST_PATH_NO_MATCH
    -> ordinary Recipe 0–8 path
```

The fast path may never guess merely to remain eligible.

## 6. Deterministic artifact lineage

An accepted fast-path turn MUST still create the normal host-owned audit lineage required for the task, with deterministic provenance fields such as:

```text
resolution_method: HOST_DETERMINISTIC_PROOF
proof_rule_id: EXACT_LITERAL_RESPONSE_V1
proof_rule_version: 1
fast_path_enabled: true
fast_path_taken: true
```

Artifacts generated deterministically MUST be distinguishable from learned proposals while remaining first-class authoritative host artifacts.

Human-readable trace rendering remains mandatory.

## 7. Full-path testing semantics

When `fast_path_enabled = false`, traces MUST record:

```text
fast_path_enabled: false
fast_path_taken: false
fast_path_bypass_reason: DISABLED_BY_RUNTIME_CONFIG
```

This mode exists specifically so adapter, recipe, AAE, repair, isolation, and end-to-end tests can exercise the ordinary learned pipeline even when a deterministic shortcut would otherwise qualify.

Optional diagnostic telemetry MAY record a non-authoritative `would_have_matched_proof_rule` while disabled, but it MUST NOT alter routing or artifact authority.

## 8. Per-recipe deterministic elision

Within the enabled fast-track policy, each recipe may also omit a learned call when every required field/transition is mechanically derivable from authoritative host artifacts and an allowlisted proof rule covers that derivation.

A recipe does not earn a model call merely because the recipe exists.

However, when fast path is disabled for full-path testing, learned-eligible recipe calls follow their normal contracts. Architecturally host-only work remains host-only.

## 9. No specialist collapse by optimization

Performance work may remove provably unnecessary learned calls. It MUST NOT merge specialist authorities, collapse recipes, or broaden adapter jurisdiction solely to reduce latency.

Any future batching/collapse requires separate qualification proving preserved:

- authority separation;
- repair isolation;
- schema/contract identity;
- traceability;
- trust/qualification semantics.

## 10. End-to-end performance receipt

Every completed turn MUST produce or contribute to end-to-end performance telemetry including at minimum:

```text
path_class
fast_path_enabled
fast_path_taken
proof_rule_id|null
learned_call_count
first_pass_success_count
repair_attempt_count
fresh_context_count
adapter_hot_hits
adapter_load_count
adapter_eviction_count
input_tokens_total
output_tokens_total
model_latency_total
adapter_transition_latency_total
end_to_end_latency
```

Hardware-qualified p50/p95 latency, first-pass-success, repair-rate, adapter-load, and token/call budgets are frozen from real pinned-runtime measurements rather than guessed before the runtime spike.

## 11. Path classes

Initial performance classes:

```text
D0 DETERMINISTIC
D1 BOUNDED_RESOLUTION
D2 NORMAL_SEMANTIC
D3 EXTERNAL_WORK
D4 REENTRY_PERSISTENCE
```

Performance expectations are evaluated relative to path class rather than holding a literal response and research/persistence job to the same budget.

## 12. Acceptance tests

Required tests include:

```text
test_fast_path_exact_literal_enabled_zero_learned_calls
test_fast_path_exact_literal_preserves_artifact_lineage
test_fast_path_ambiguous_input_falls_back_normal_pipeline
test_fast_path_disabled_forces_normal_learned_eligible_path
test_fast_path_disabled_does_not_modelize_host_only_authority
test_fast_path_toggle_snapshotted_per_turn
test_fast_path_trace_records_enabled_taken_rule
test_fast_path_trace_records_disabled_bypass
test_fast_path_safety_gates_cannot_be_disabled
test_fast_path_and_full_path_terminal_semantics_equivalent_for_qualified_fixture
```

For qualification fixtures where both paths are legal, compare terminal authoritative meaning, literal constraints, required disclosures, and artifact provenance. Performance differences are expected; authority correctness must not differ.

## 13. Locked outcome

The product-level call-amplification finding is resolved by a conservative deterministic proof layer plus end-to-end performance qualification.

The fast path is explicitly operator-controllable. It can be turned OFF to exercise the full ordinary Recipe pipeline during prototype testing, adapter qualification, regression testing, or normal use. Turning it OFF never disables host safety or authority boundaries.
