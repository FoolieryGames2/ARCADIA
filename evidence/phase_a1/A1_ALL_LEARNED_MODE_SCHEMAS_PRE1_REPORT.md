# A.R.C.A.D.I.A. — All Learned-Mode Schemas PRE-1 Report

**Date:** 2026-09-04  
**Standing:** PRE-version implementation / all 20 schema pairs resolve / Gate A1 remains open

## Scope

The 18 previously missing Recipe 1–3 and Recipe 5–8 learned-mode contracts now
have strict input and output schemas. Together with the two Recipe 0 contracts,
`LEARNED_MODE_SCHEMAS` resolves exactly 20 modes. Recipe 4 remains host-only and
has no learned schema contract.

## Frozen-boundary alignment

- Recipe 1 preserves Spell, Meaning, Analyst, Organizer, and presentation-only Intent Comment.
- Recipe 2 uses the architecture-freeze evidence states `supports`, `contradicts`,
  `relevant`, `irrelevant`, and `ambiguous`; the Commentator proposes lean Context
  points and Final Synthesis sees accepted `Cxxx` only.
- Recipe 3 removes confidence/tool syntax from Requirement Assessment, requires a
  semantic work need for `WORK_REQUIRED`, and restricts Plan Composition to the
  minimal local-node graph with `ORIGINAL|DISCOVERY|REPAIR` origin.
- Recipe 5 keeps consequences nonterminal and separates discovery, repair, Context
  update, and Persistence relevance.
- Recipe 6 produces semantic assessment/mutation proposals only; SQL, permanent IDs,
  commit success, and transaction execution remain host-owned.
- Recipe 7 alone proposes terminal per-requirement standing; its Composer cannot
  change statuses or write final prose.
- Recipe 8 accepts bounded presentation packets and emits only comment/final text;
  publication remains host-owned.

Every reachable object rejects unknown fields. All learned outputs have one fixed
top-level shape, bounded arrays/strings, and closed host-behavior enums. The shared
catalog remains non-dispatchable and at T0.

## Exact identity evidence

`manifests/aae_schema_catalog_pre1.json` records both compiled SHA-256 schema hashes
for every mode. Tests prove the manifest covers the exact registry mode set and that
each schema ID/version resolves to its AAE registry reference.

## Verification

- Complete generated fixed-shape samples validate for all 40 schemas.
- Unknown-field and learned-routing injection fails on every input and output boundary.
- Mode-specific host checks are encoded for Spell spans, Context evidence completeness,
  Decision dispositions/graphs, Reconciliation evidence basis, Persistence coverage,
  Completion standing consistency, and Result disclosure/literal gates.
- Full deterministic suite: 551 passed.
- Ruff: pass.
- strict MyPy: pass across 62 source files.

## Honest boundary

This completes the missing PRE-1 schema bodies, not Gate A1. Complete measured tuning
profiles, deterministic context-budget projection, training/runtime same-source proof,
registry-wide serializer/pre-dispatch integration, and joint freeze review remain open.
