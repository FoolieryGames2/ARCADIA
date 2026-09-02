# A.R.C.A.D.I.A. — A1 Legal Reference Policy PRE-1

**Date:** 2026-08-31
**Standing:** PRE-version implementation / not frozen / Gate A1 remains OPEN

## Purpose

Turn the AAE registry's already-recorded legal authoritative reference namespaces and local proposal-key
prefixes into one deterministic fail-closed policy without duplicating the lists.

## Encoded behavior

- All 20 mode policies are generated directly from `AAE_REGISTRY_PRE_V1`.
- A mode may receive/output only an authoritative namespace listed by its contract.
- A learned authoritative reference is accepted only when its namespace/value pair exactly matches a host-supplied reference.
- Matching is exact and case-sensitive; no normalization creates authority.
- Identifier text is opaque and provides no semantic meaning.
- New learned objects use only the mode's separately registered local-key prefixes.
- Local proposal keys remain non-authoritative and require later host canonicalization.
- A mode with no local-key prefixes cannot mint model-local proposal identifiers.
- Local keys may not collide with supplied authoritative values.
- Authoritative ID allocation remains host-only.

## PRE-1 grammar note

The full local-key suffix grammar is not canonically frozen. PRE-1 therefore enforces only the registered
prefix plus a conservative ASCII uppercase/digit/underscore safety surface and length cap. That grammar
remains reviewable before freeze.

## Files

```text
src/arcadia/contracts/policies/legal_references.py
src/arcadia/contracts/policies/__init__.py
tests/unit/contracts/policies/test_legal_references.py
project/TODO_A1_STRICT_SCHEMAS_POLICIES.md
```
