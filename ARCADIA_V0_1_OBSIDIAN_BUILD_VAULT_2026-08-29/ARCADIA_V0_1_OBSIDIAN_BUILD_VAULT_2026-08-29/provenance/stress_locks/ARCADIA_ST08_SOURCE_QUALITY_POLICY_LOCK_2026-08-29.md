---
title: "A.R.C.A.D.I.A. R3 — ST-08 Source Quality / Evidence Authority Lock"
project: "A.R.C.A.D.I.A."
version: "0.1-prototype"
checkpoint_date: "2026-08-29"
document_role: "stress-lock"
source_path: "provenance/stress_locks/ARCADIA_ST08_SOURCE_QUALITY_POLICY_LOCK_2026-08-29.md"
source_sha256: "98c81980b3c6bb38eee20a033054d2344779cd066e5be5d4cc4bb871f89f836f"
source_bytes: 6659
source_integrity: "preserved"
tags:
  - "arcadia/v0-1"
  - "type/provenance"
  - "type/stress-lock"
  - "status/frozen"
aliases:
  - "ARCADIA_ST08_SOURCE_QUALITY_POLICY_LOCK_2026-08-29.md"
  - "A.R.C.A.D.I.A. R3 — ST-08 Source Quality / Evidence Authority Lock"
---

> [!info] Obsidian navigation
> **Checkpoint role:** `stress-lock`  
> **Frozen source:** `provenance/stress_locks/ARCADIA_ST08_SOURCE_QUALITY_POLICY_LOCK_2026-08-29.md` · SHA-256 `98c81980b3c6bb38…`  
> **Command center:** [[ARCADIA v0.1 - Command Center]]  
> **Connected:** [[07_ARCADIA_V0_1_SOURCE_POLICY_REGISTRY]] · [[R5_RECONCILIATION_V0_1]] · [[ARCADIA_R3_STRESS_RESOLUTION_LEDGER_2026-08-28]]

<!-- OBSIDIAN_LAYER_END — ORIGINAL SOURCE CONTENT BEGINS BELOW -->

# A.R.C.A.D.I.A. R3 — ST-08 Source Quality / Evidence Authority Lock

**Date:** 2026-08-29  
**Stress item:** ST-08 — research cannot yet earn strong terminal claims  
**Status:** **CLOSED — DESIGN LOCK**

## 1. Core decision

A.R.C.A.D.I.A. does **not** use a universal source-reputation score. Evidence authority is evaluated relative to the claim through a host-owned, versioned `SourcePolicyRegistry`.

The policy registry defines, per research-policy family:

- acceptable source relationships;
- evidence directness requirements;
- freshness rules;
- minimum provenance requirements;
- corroboration requirements;
- duplicate/syndication handling;
- conflict handling;
- minimum terminal-evidence conditions.

Example policy families may include:

- `SOFTWARE_CURRENT_RELEASE`
- `CURRENT_OFFICE_HOLDER`
- `CURRENT_PRODUCT_SPEC`
- `CURRENT_LAW_OR_RULE`
- `HISTORICAL_FACT`
- `SCIENTIFIC_CLAIM`
- `GENERAL_INFORMATION`
- `COMMUNITY_SENTIMENT`

The registry is extensible and versioned. These example families do not imply that every category is fully enumerated now.

## 2. No universal trust score

A source's usefulness depends on the claim it is being asked to support. A first-party release page may be authoritative for a software release identifier but not for broad community sentiment.

Therefore A.R.C.A.D.I.A. preserves discrete evidence attributes rather than collapsing them into one global number.

Relevant axes include:

- `source_relation`
- `evidence_directness`
- `freshness_status`
- `claim_specificity`
- `independence_group`
- `retrieval_integrity`

Possible source relationships include, as policy vocabulary rather than a universal ranking:

- `OFFICIAL_PUBLISHER`
- `OFFICIAL_REGISTRY`
- `PRIMARY_PARTICIPANT`
- `GOVERNMENT_OR_REGULATOR`
- `ACADEMIC_PRIMARY`
- `INDEPENDENT_SECONDARY`
- `NEWS_SECONDARY`
- `COMMUNITY`
- `UNKNOWN`

Authority metadata never substitutes for semantic support. A source may be official yet fail to support the specific claim under review.

## 3. Required external-evidence provenance

Every external evidence item must preserve enough host-owned provenance for later Reconciliation and replay. At minimum, where applicable:

- `evidence_ref`
- retrieval capability/tool class
- query or request that produced the item
- original locator / URL
- canonical locator
- source identity
- source domain
- `retrieved_at`
- `published_at` when known
- `updated_at` when known
- version/release/effective date when applicable
- title
- content hash
- source relationship
- evidence directness
- independence/duplicate/syndication grouping
- bounded relevant content/extract
- claim references the evidence is being used to support

A label such as `DIRECT_SOURCE_EVIDENCE` alone carries no terminal authority.

## 4. Deterministic preprocessing before semantic Reconciliation

Raw evidence receipts are deterministically normalized before learned reconciliation:

```text
raw tool receipts
  -> canonical locator normalization
  -> duplicate / syndication grouping
  -> source metadata extraction
  -> freshness calculation
  -> SourcePolicyRegistry lookup
  -> Evidence Signal Pack
  -> Evidence/Reconciliation specialist
```

The host supplies the structured provenance and policy facts. Learned specialists compare semantics and conflicts; they do not invent reputation scores.

## 5. Freshness-sensitive terminal gate

Terms such as `latest`, `current`, `today`, `still`, `presently`, and `most recent` make freshness part of the truth conditions.

A freshness-sensitive requirement may not receive unconditional `SATISFIED` standing unless its active SourcePolicy proves all policy-required conditions, including as applicable:

- provenance complete enough for evaluation;
- freshness checked and within policy;
- source relationship/authority fit is sufficient for the claim;
- directness requirement is met;
- required corroboration is met;
- duplicate/syndication inflation is controlled;
- material conflicts are resolved or explicitly bounded.

If those conditions are absent, the requirement remains `PARTIALLY_SATISFIED`, `BLOCKED`, or another permitted unresolved standing. Missing evidence remains missing evidence.

## 6. Conflict handling

Source-class labels do not mechanically decide every conflict. Two sources can both be official while representing different scopes, release channels, dates, platforms, or update cadences.

Reconciliation considers:

- dates/freshness;
- actual semantic claim supported;
- stable vs pre-release or draft status;
- applicability/scope;
- source relationship;
- directness;
- independence;
- policy-specific precedence.

If conflict remains material and unresolved, A.R.C.A.D.I.A. preserves the conflict and does not manufacture a stronger terminal claim.

## 7. Corroboration is claim-specific

One direct official source may be sufficient for some policy families, such as an official software release identifier. Other claims, such as broad consensus or breaking events, may require multiple independent sources.

Corroboration requirements are defined by `SourcePolicyRegistry`, not by one global rule.

## 8. Ownership

- Host owns provenance capture, normalization, time metadata, duplicate grouping, policy lookup, and terminal policy gates.
- Reconciliation owns bounded semantic comparison of supplied evidence.
- Completion may only claim terminal satisfaction when the host evidence gate permits it.
- Result may not upgrade a weaker standing into a stronger factual claim.

## 9. Required acceptance tests

At minimum:

1. `latest/current` claim with missing retrieval/freshness provenance cannot become unconditional `SATISFIED`.
2. Newer direct official evidence defeats stale secondary evidence when the active policy permits that precedence.
3. Two duplicated/syndicated secondary pages count as one independence group.
4. Two conflicting official sources remain conflict-present until scope/date semantics resolve them.
5. A high-authority source that does not semantically support the claim cannot satisfy the requirement.
6. Community-sentiment policy does not treat an official publisher as automatically sufficient evidence of community sentiment.
7. Evidence provenance survives full trace/replay with content hashes and canonical locators intact.

## 10. Frozen invariant

> Evidence quality in A.R.C.A.D.I.A. is claim-relative, provenance-backed, freshness-aware, and policy-gated. No universal source reputation score exists. Freshness-sensitive claims cannot earn unconditional terminal truth unless the active SourcePolicy's provenance, authority-fit, freshness, corroboration, and conflict requirements are actually met.

