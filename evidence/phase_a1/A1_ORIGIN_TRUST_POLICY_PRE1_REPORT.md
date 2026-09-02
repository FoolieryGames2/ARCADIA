# A.R.C.A.D.I.A. — A1 Origin / Trust Policy PRE-1

**Date:** 2026-08-31
**Standing:** PRE-version implementation / not frozen / Gate A1 remains OPEN

## Purpose

Implement numbered strict-schema/policy TODO item 3 without expanding into source-quality ranking,
adapter qualification trust, runtime residency trust, or tool execution mechanics.

## Source-grounded vocabulary

The v0.1 master authority names six model-visible data origins:

```text
USER_PROMPT
TRANSCRIPT
SEMANTIC_MEMORY
TOOL_RECEIPT
WEB_RESULT
HOST_DERIVED_SIGNAL
```

and four data authority classes:

```text
CONTENT_ONLY
EXTERNAL_UNTRUSTED_EVIDENCE
HOST_VERIFIED_EXECUTION
HOST_VERIFIED_STATE
```

The same authority also explicitly permits `prior validated recipe artifacts` in the data plane but
provides no origin token for that class. PRE-1 therefore adds one visibly provisional token:

```text
VALIDATED_RECIPE_ARTIFACT
```

This is intentionally an extension rather than silently misclassifying model-produced, host-validated
semantic artifacts as `HOST_DERIVED_SIGNAL`.

## Encoded boundaries

- Every one of the 20 logical specialist modes resolves exactly one PRE-1 origin/trust policy.
- Origin admission does not override the contract's legal input-artifact classes or legal reference namespaces.
- User prompts and transcript text cannot be relabeled as host-verified state/execution.
- Web results admit only `EXTERNAL_UNTRUSTED_EVIDENCE` in this PRE-1 framing.
- Tool receipts admit only `HOST_VERIFIED_EXECUTION`; this does not make their returned semantic claims true.
- Semantic memory may be framed as `CONTENT_ONLY` or `HOST_VERIFIED_STATE` depending on the host-owned stored-state standing; no source ranking is inferred.
- Prior validated recipe artifacts remain `CONTENT_ONLY` data when shown to another model.
- All data text remains non-instructional even when its metadata records stronger host evidence/state standing.
- A bare authoritative identifier is legal for identity/reference use, but cannot supply semantic meaning. If a specialist must interpret the referenced item, bounded authorized content must accompany it.
- Illegal mode/origin, origin/authority, duplicate-item, and bare-ref semantic-use combinations fail closed through `require_valid_origin_trust_manifest()` / `require_valid_origin_trust_item()`.

## Deliberately not frozen

- The PRE-1 `VALIDATED_RECIPE_ARTIFACT` token requires joint review before freeze.
- Source quality / evidence precedence is a separate open lane and is not invented here.
- Numeric adapter trust levels / T0–T6 qualification are not part of this data-origin policy.
- Per-schema representation of origin metadata remains later schema integration work; this policy validates the host sidecar manifest and does not rewrite frozen Recipe-0 CALL_DATA shapes.
- No real learned dispatch is enabled.

## Files

```text
src/arcadia/contracts/policies/origin_trust.py
src/arcadia/contracts/policies/__init__.py
src/arcadia/contracts/aae/types.py
src/arcadia/contracts/aae/registry.py
tests/unit/contracts/policies/test_origin_trust.py
project/TODO_A1_STRICT_SCHEMAS_POLICIES.md
```
