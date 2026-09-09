# A.R.C.A.D.I.A. — CLI Recipe-Slice Presentation

Date: 2026-09-09

Standing: PASS — user-facing qualification-trace presentation; architecture and authority
unchanged.

## Change

The R0 -> R1 qualification CLI now opens each implemented recipe with a fixed-width box that
shows the slice title, canonical identity, and short purpose. A successful slice ends with an
explicit `SLICE STATUS` line. Exactly two empty lines separate that line from the next slice's
box.

The boundary is the recipe controller, not each learned specialist call. Scope Proposal remains
inside Recipe 0; Spell, Term / Meaning, Prompt Analyst, Intent Organizer, and the optional
Intent Comment remain inside Recipe 1.

Presentation metadata is centralized in `RECIPE_SLICE_PRESENTATIONS`. The trace rejects an
unregistered slice identity, ensuring that a newly wired recipe cannot silently omit its
operator-facing heading. `project/CLI_RECIPE_SLICE_PRESENTATION.md` is the living registry and
integration checklist that must be updated with each new CLI slice.

## Verification

Deterministic tests prove:

- the R0 and R1 title, identity, and description fields render inside the box;
- a completed R0 status precedes the R1 title;
- exactly two empty lines occur at that boundary;
- the real R0 -> R1 harness emits both boundaries in controller order; and
- an unregistered future slice is rejected instead of rendering without metadata.

The pinned workstation gate passes 628 tests, Ruff, and strict MyPy over 74 source files.
