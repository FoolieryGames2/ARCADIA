# A.R.C.A.D.I.A. v0.1 — Global Contracts and Invariants

This document is the cross-cutting rulebook. Recipe details may become more specific but may not weaken these invariants.

# 1. Identity and provenance

- Host creates canonical UUID identities.
- Human IDs (`R001`, `W001`, `REC001`, etc.) are scoped aliases.
- Every durable artifact is versioned, hashable, traceable, and linked to upstream basis refs.
- Canonical JSON V1 is the hashing/serialization baseline unless an artifact explicitly uses another frozen profile.
- Models never invent canonical IDs and cannot promote local proposal keys without host allocation.

# 2. Retention domains

```text
conversation transcript
technical artifact ledger
semantic memory
secure raw trace
training candidate quarantine
training-approved datasets
```

These are separate authorities. Presence in one never implies presence in another.

# 3. Intent immutability

Original accepted Rxxx requirements represent what the user communicated. Later discovery, repair, evidence, or memory does not rewrite them.

# 4. Context promotion

Context can be partial/conflicted/unresolved and still valid. Invalid/not-ready Context cannot enter Decision. Replacement Context does not become ACTIVE until required promotion validation/comment succeeds; prior ACTIVE revision remains authoritative during pending promotion.

# 5. Work reality

Decision plans. Execution performs. Reconciliation interprets. Persistence writes semantic state. Completion closes requirements. Result speaks.

No layer may claim authority owned by another because it “probably happened.”

# 6. Uncertainty

Unknown is a valid state. Examples include unresolved Context, source conflict, blocked work, OUTCOME_UNKNOWN execution, and POISONED runtime state. No learned component may fill these gaps with fabricated certainty.

# 7. Budgets

Every loop is bounded. Host configuration must define finite per-stage and aggregate ceilings for:

```text
model attempts/repairs
context/history expansion
Context retrieval expansion
Decision work expansion
Reconciliation discovery depth
re-entry depth
side-effect retries/compensations
total learned calls
total model-visible input/output tokens
```

Budget exhaustion preserves accumulated truth and routes toward honest Completion. It never resets history or fabricates success.

# 8. Repair

Repair is not a hidden extra reasoning universe. Every repair has its own attempt UUID/trace, uses the same authoritative base packet plus explicit validation error, obeys aggregate attempt/token caps, and receives a fresh context/sampler.

# 9. Packet projection

Models see only bounded authorized content needed for their contract. A bare reference ID never supplies semantic meaning. If a specialist must interpret an item, bounded content must be present. Projection itself is benchmarked for required-artifact recall and irrelevant-artifact injection.

# 10. Runtime health versus model quality

Bad model output, schema rejection, semantic failure, or repair exhaustion do not automatically mean runtime corruption.

Health changes only when mechanical state certainty/integrity is lost.

# 11. Side effects

External operation state is host truth only. `SUCCESS`, `FAILED`, and `OUTCOME_UNKNOWN` are based on receipts/journal/verification, not model inference.

# 12. Evidence

Evidence authority is claim-specific. `DIRECT_SOURCE_EVIDENCE` or similar labels are descriptive metadata, not terminal proof by themselves.

# 13. Deterministic host elision

If host rules completely prove a stage output, the host may emit the normal artifact without calling a model. The trace records the proof rule. When fast path is disabled, the ordinary learned-eligible path is forced for semantic stages, but mandatory host safety/authority checks remain.

# 14. Training

Runtime success does not automatically create training data. Training consumes only immutable approved dataset manifests. Held-out fixtures never enter training.

# 15. Human readability

Every authoritative machine object important to debugging must have a deterministic human-readable rendering. Human-readable views are derived audit surfaces, not alternate sources of truth.
