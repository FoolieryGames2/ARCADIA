# A.R.C.A.D.I.A. v0.1 — SourcePolicyRegistry Specification

# 1. Core decision

A.R.C.A.D.I.A. does **not** maintain a universal website reputation score.

Evidence sufficiency is claim-specific.

# 2. Policy families

Initial extensible families:

```text
SOFTWARE_CURRENT_RELEASE
CURRENT_OFFICE_HOLDER
CURRENT_PRODUCT_SPEC
CURRENT_LAW_OR_RULE
HISTORICAL_FACT
SCIENTIFIC_CLAIM
GENERAL_INFORMATION
COMMUNITY_SENTIMENT
```

Each policy defines preferred source relationships, minimum provenance, freshness rules, corroboration, conflict behavior, and terminal Completion requirements.

# 3. Evidence axes

Preserve discrete facts, not one magic score:

```text
source_relation
  OFFICIAL_PUBLISHER
  OFFICIAL_REGISTRY
  GOVERNMENT_OR_REGULATOR
  ACADEMIC_PRIMARY
  PRIMARY_PARTICIPANT
  INDEPENDENT_SECONDARY
  NEWS_SECONDARY
  COMMUNITY
  UNKNOWN

evidence_directness
  PRIMARY
  DERIVED
  SECONDARY
  COMMENTARY

freshness_status
  CURRENT_WITHIN_POLICY
  STALE_FOR_POLICY
  UNKNOWN

claim_specificity
  DIRECT
  PARTIAL
  CONTEXTUAL

retrieval_integrity
  COMPLETE
  PARTIAL
  FAILED
```

# 4. Required external evidence receipt fields

At minimum when available/applicable:

```text
evidence_ref
retrieval_capability
query_or_request
original_locator
canonical_locator
source_identity/domain
retrieved_at
published_at
updated_at
version_date
title
content_hash
source_relation
evidence_directness
independence_group / syndication metadata
bounded relevant extract
claim refs supported/challenged
```

A label such as `DIRECT_SOURCE_EVIDENCE` is never enough on its own.

# 5. Freshness-sensitive truth

Terms such as:

```text
latest
current
today
still
presently
most recent
```

make freshness part of the claim's truth conditions.

Completion may emit unconditional SATISFIED only when the active policy confirms required provenance, freshness, authority fit, and conflict resolution.

# 6. Conflicts

Authority metadata does not erase semantic disagreement. Reconciliation still examines what each source actually says and whether distinctions such as stable/prerelease/platform/date explain the conflict.

Unresolved material conflict remains uncertainty/partial/blocker state.

# 7. Independence

Exact duplicates, syndication, mirrors, and content copies share an `independence_group` and do not count as independent corroboration merely because URLs differ.

# 8. Claim-specific examples

- Official software release registry may be sufficient to establish current stable version when fresh and unambiguous.
- One company page is not enough to prove “experts broadly agree.”
- Official publisher is not automatically the best authority for community sentiment.
- Two official sources can still conflict and require semantic reconciliation.

# 9. Host/model split

Host deterministically extracts/canonicalizes source metadata, duplicate groups, timestamps, and policy family. Evidence/Reconciliation specialists judge bounded semantic support/conflict. Models do not invent missing provenance.
