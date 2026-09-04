# A.R.C.A.D.I.A. — A1 Strict Schemas + Policy Registries TODO

**Standing:** PRE-version working checklist
**Parent item:** `Create strict input/output schemas and policy registries.`
**Gate:** Phase A1 remains OPEN until the parent item and all other A1 requirements pass.

This checklist is intentionally narrower than `TODO_V0_1.md`. We will review and
close these items one at a time rather than treating the whole schema/policy layer
as one opaque implementation step.

## 1. Shared strict-schema rules — PRE-1 implemented / review accepted

- [x] JSON Schema owns shape and syntactic legality.
- [x] Host semantic validation owns cross-field, host-state, and host-policy meaning.
- [x] Every object schema rejects unknown properties rather than ignoring them.
- [x] Learned outputs use a fixed top-level shape by default.
- [x] Branches change field values, not which top-level fields exist.
- [x] Fields affecting interpretation/downstream behavior are required.
- [x] Optional learned-output fields require an explicit future absence-semantics exception.
- [x] Model-selected contract structure is forbidden.
- [x] Silent truncation/correction/defaulting is forbidden at this boundary.
- [x] Impossible/dead-end downstream requests fail closed before retrieval/work continues.
- [x] Recipe 0 history requests require actual completed transcript history.
- [x] Recent lookback may not exceed the number of completed exchanges that actually exist.

**PRE-1 implementation:**

```text
src/arcadia/contracts/policies/schema_rules.py
tests/unit/contracts/policies/test_schema_rules.py
```

`SCOPE_PROPOSAL` is the first live consumer of the fixed-output-shape rule and the
history-existence semantic rule. This does not freeze the shared policy yet.

## 2. Finish Recipe 0 — baseline PRE-1 implemented / frozen continuation delta open

- [x] Strict input schema.
- [x] Strict output schema.
- [x] Frozen statuses/enums supported by canonical R0.
- [x] Host semantic validation rules.
- [x] Review fixed-shape behavior against real R0 branches.
- [ ] Add host-owned fixed-shape `continuation_state` to current transcript metadata.
- [ ] Add one-next-turn exact prior-exchange prefetch for `AWAITING_USER_INPUT`.
- [ ] Add `SUFFICIENT_WITHOUT_HISTORY` without weakening the fixed output shape.
- [ ] Prove unrelated-turn discard and unconditional one-turn expiry.
- [ ] Pass the frozen journal-elicitation exact-payload integration case.

**PRE-1 implementation:**

```text
src/arcadia/contracts/schemas/r0/scope_validation.py
tests/unit/contracts/schemas/r0/test_scope_validation.py
```

The frozen four-field output shape is preserved exactly. `NEEDS_MORE_RECENT` and
`NEEDS_TARGETED_HISTORY` do not invent new count/search-term fields; deterministic
expansion-delta selection remains host policy/runtime work. Frozen transcript text
is hash-verified before the semantic verdict is accepted. This item remains PRE-version
until the 2026-09-04 continuation delta and joint review/freeze pass.

## 3. Origin / Trust policy registry — PRE-1 implemented

- [x] Define allowed origin classes.
- [x] Define trust metadata carried with supplied artifacts.
- [x] Define which origins each specialist mode may consume.
- [x] Distinguish bare authoritative refs from supplied referenced content.
- [x] Reject illegal origin/trust combinations before learned dispatch.

**PRE-1 implementation:**

```text
src/arcadia/contracts/policies/origin_trust.py
tests/unit/contracts/policies/test_origin_trust.py
```

The six origin labels and four authority-class labels named by the v0.1 master
authority are preserved exactly. `VALIDATED_RECIPE_ARTIFACT` is an explicit PRE-1
extension because the same authority permits prior validated recipe artifacts in
the data plane but does not assign them an origin token. This avoids falsely
relabeling learned semantic artifacts as host-derived signals. Data text remains
non-instructional regardless of trust metadata. Source-quality ranking and adapter
runtime trust remain deliberately out of scope.

## 4. Legal-reference policy — PRE-1 implemented

- [x] Define legal authoritative namespaces per mode (`Rxxx`, `Cxxx`, `Wxxx`, receipts, evidence refs, etc.).
- [x] Require exact copying of supplied authoritative refs.
- [x] Define legal model-local proposal-key namespaces separately.
- [x] Keep authoritative ID allocation host-only.

**PRE-1 implementation:**

```text
src/arcadia/contracts/policies/legal_references.py
tests/unit/contracts/policies/test_legal_references.py
```

The policy registry is derived from the existing AAE Contract Registry instead of
maintaining a second hand-written namespace list. Supplied authoritative values are
opaque and must be copied exactly; model-created objects use only the separately
registered local-key prefixes and remain non-authoritative until host validation and
canonicalization. PRE-1 intentionally does not infer semantics from identifier text.

## 5. Shared enum / vocabulary handling — PRE-1 implemented / review accepted

- [x] Host-behavior/routing/state values use closed enums.
- [x] Descriptive machine labels use a bounded machine-token pattern when no complete canonical vocabulary is frozen.
- [x] Human-language content remains bounded free text rather than being silently taxonomized.
- [x] Vocabulary classification is separate from tunable size limits.
- [x] Recipe-0 status vocabularies are derived from the AAE registry rather than duplicated as a second authority.

**PRE-1 implementation:**

```text
src/arcadia/contracts/policies/vocabulary.py
tests/unit/contracts/policies/test_vocabulary.py
```

The accepted rule is: if the host makes a control decision from the value itself, the
vocabulary is closed. Descriptive machine labels may be pattern-bounded. Human-language
content is bounded free text. Exact size/count ceilings are settings, not vocabulary logic.

## 6. Field-cap / tuning settings policy — PRE-1 architecture implemented / review accepted

- [x] Move tunable numeric ownership out of the AAE contract registry.
- [x] Give every AAE contract a `settings_profile_id`.
- [x] Add a separate strict settings handler and editable TOML settings document.
- [x] Support global defaults -> budget-class defaults -> per-contract overrides.
- [x] Define budget classes `TINY`, `SMALL`, `MEDIUM`, `LARGE`, `FULL_CAPABLE`.
- [x] Support input/output token, string, array, nesting, source-excerpt, and context-headroom knobs.
- [x] Define host-owned dynamic bounds as the stricter of configured and available capacity.
- [x] Prohibit silent truncation; unresolved values are not interpreted as unlimited.
- [x] Produce deterministic canonical settings snapshots + SHA-256 hashes for replay/review.
- [x] Reject unknown settings knobs rather than silently accepting typos.
- [ ] Populate and tune complete numeric profiles for all logical modes after runtime measurement.
- [ ] Revisit which additional non-semantic runtime knobs belong in this handler as later A1/A2 work exposes them.

**PRE-1 implementation:**

```text
src/arcadia/settings/handler.py
src/arcadia/settings/__init__.py
configs/aae_tuning.pre1.toml
tests/unit/settings/test_handler.py
```

PRE-1 assigns only the two executable Recipe-0 modes and carries forward broad ceilings
already used by their local safety schemas. Final token/output/headroom numbers remain
intentionally unresolved until measured; missing values fail completeness checks rather
than becoming accidental infinity.

## 7. Repair-shape rules — PRE-1 implemented / review accepted

- [x] Define which contracts allow repair.
- [x] Define exact repair input/error evidence.
- [x] Keep repair attempt ceilings in the separate tunable settings handler.
- [x] Leave PRE-1 numeric ceilings unresolved until qualification/runtime evidence supports them.
- [x] Define exhausted-repair behavior as a typed host stop, never a recursive retry loop.
- [x] Require a new host attempt UUID for every repair.
- [x] Require the same authoritative packet, same specialist mode, and same InferenceProfile.
- [x] Require a fresh context and fresh sampler for every repair attempt.
- [x] Supply the exact machine validation error and do not re-feed the invalid prior output as new model authority.
- [x] Prevent repair from adding facts or expanding specialist authority.

**PRE-1 implementation:**

```text
src/arcadia/contracts/policies/repair_shape.py
src/arcadia/contracts/aae/types.py
src/arcadia/settings/handler.py
configs/aae_tuning.pre1.toml
tests/unit/contracts/policies/test_repair_shape.py
```

All 20 PRE-version learned contracts currently permit bounded repair. The semantic
permission lives in each contract's immutable `RepairShape`; the count does not.
`max_repair_attempts` is now a settings knob and may legally be zero. The checked-in
PRE-1 settings deliberately leave it unresolved for the two currently configured R0
profiles rather than inventing a production value. An unresolved count produces the
typed `REPAIR_LIMIT_UNRESOLVED` stop; exhaustion produces
`REPAIR_BUDGET_EXHAUSTED`. The existing Phase-A repair ledger remains authoritative
for immutable repair basis, exact failure snapshots, unique attempt UUIDs, lineage,
and aggregate accounting.

## 8. Next-consumer rules — PRE-1 implemented / review accepted

- [x] Validate legal downstream consumer identities.
- [x] Keep routing metadata host-owned/registry-owned.
- [x] Prevent arbitrary model-selected routing.
- [x] Classify exact consumer identities as deterministic host stages or learned logical modes.
- [x] Require host selection even when an edge is legal.
- [x] Keep routing legality separate from target dispatch/runtime authorization.

**PRE-1 implementation:**

```text
src/arcadia/contracts/policies/next_consumers.py
tests/unit/contracts/policies/test_next_consumers.py
```

The AAE registry remains the authority for each learned mode's allowed outgoing edge list.
A separately registered host-consumer identity set and learned-consumer alias map validate those
identities so a typo/new route does not become legal merely by appearing in the same contract.
The host alone selects traversal. A learned result cannot choose `next_adapter`, `route_to`, or
any equivalent destination, even when that destination is otherwise a legal edge. Passing this
gate proves only routing legality; it does not make the target contract dispatchable or bypass
its schema, trust, settings, qualification, or runtime gates.

## 9. Recipe 1 — Intent schemas

- [ ] `SPELL_NORMALIZATION`
- [ ] `TERM_MEANING`
- [ ] `PROMPT_ANALYSIS`
- [ ] `INTENT_ORGANIZER`
- [ ] `INTENT_COMMENT`

## 10. Recipe 2 + Recipe 3 schemas

- [ ] Context modes.
- [ ] Requirement Assessor.
- [ ] Plan Composer.

## 11. Recipe 5–8 schemas

- [ ] Reconciliation.
- [ ] Persistence.
- [ ] Completion.
- [ ] Result / Howard.
- [ ] Confirm Recipe 4 remains host-only with no learned schema contract.

## 12. Cross-contract integrity review

- [ ] All 20 logical modes resolve strict input/output schemas.
- [ ] Every schema ref resolves to the intended exact version/hash.
- [ ] Every mode resolves origin/trust policy.
- [ ] Every legal ref namespace is known.
- [ ] Field caps exist where required.
- [ ] Repair and next-consumer metadata resolve.
- [ ] Schema-less learned dispatch is impossible.
- [ ] Full `check.bat` passes on canonical Windows environment.
- [ ] Joint review complete before marking parent A1 TODO item done.
