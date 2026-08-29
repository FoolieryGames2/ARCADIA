# A.R.C.A.D.I.A. v0.1 — Performance, Deterministic Fast Path, and Toggle

# 1. Problem

The R3 five-slice trace demonstrated severe call amplification: 13 learned calls for an exact literal response and 27 for a research+remember path. Compartmentalization remains valuable, but invoking a model for mechanically provable work adds latency, failure probability, and adapter churn without adding semantic value.

# 2. DeterministicPathGate

Before normal learned work, the host may match a small allowlisted grammar of **syntactically provable** operations.

Initial v0.1 D0 rule:

```text
EXACT_LITERAL_RESPONSE_V1
```

Example:

```text
Reply exactly: Ready.
```

The host already possesses the required bytes. It may create the normal authoritative artifact lineage and publish under a deterministic proof rule with zero learned calls.

Do not expand the allowlist casually. File operations or other commands may receive deterministic grammars later only after their authority/ambiguity rules are separately proven.

# 3. Model-necessity gate inside recipes

Even when a turn did not enter at D0, each recipe asks:

> Is semantic judgment actually required for this stage, or is the required artifact/transition fully derivable from validated host artifacts?

If fully derivable:

```text
MODEL SEES NOTHING — HOST-ONLY PASS
```

The resulting artifact still carries normal IDs, provenance, hashes, and traceability.

# 4. Fast-path toggle

Config:

```text
fast_path_enabled: true | false
```

Rules:

- snapshotted at turn start;
- immutable for that turn;
- recorded in turn/performance receipt;
- OFF forces ordinary learned-eligible semantic pipeline behavior;
- OFF is supported for testing **and normal use**;
- host safety, schema, execution, persistence, and truth gates remain mandatory either way;
- optional shadow field may record `would_have_fast_pathed=true` without taking it.

Recommended qualification default:

```text
fast_path_enabled = false
```

Recommended normal prototype default after D0 equivalence tests pass may be true, but remains user/operator configurable.

# 5. Required telemetry

```text
fast_path_enabled
fast_path_taken
proof_rule_id
fast_path_bypass_reason
would_have_fast_pathed
path_class
learned_call_count
first_pass_success_count
repair_count
adapter loads/evictions/hits
input/output tokens
model latency
adapter transition latency
end_to_end_latency
```

# 6. Path classes

```text
D0 DETERMINISTIC
D1 BOUNDED_RESOLUTION
D2 NORMAL_SEMANTIC
D3 EXTERNAL_WORK
D4 REENTRY_PERSISTENCE_COMPLEX
```

Performance budgets are measured per class. Do not compare a literal echo to research+memory as if they should have equal cost.

# 7. What optimization may not do

Performance work may remove unnecessary model calls. It may not merge specialist authority boundaries merely to reduce latency without a new explicit architecture/qualification decision.

# 8. Failure rule

Fast path fails open to the normal pipeline in the routing sense:

```text
no exact allowlisted proof -> normal A.R.C.A.D.I.A.
```

It never guesses to remain fast.
