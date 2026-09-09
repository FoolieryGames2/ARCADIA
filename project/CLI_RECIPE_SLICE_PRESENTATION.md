# ARCADIA CLI Recipe-Slice Presentation Convention

Updated: 2026-09-09

Status: active implementation convention for the user-facing qualification CLI.

## Required slice layout

Every implemented recipe slice must appear in this order:

1. a fixed-width title box containing `SLICE TITLE`, canonical `IDENTITY`, and a short
   `DESCRIPTION`;
2. all learned-call and host-controller trace content owned by that recipe;
3. `SLICE STATUS> <recipe-id> <title> COMPLETE` after successful controller completion; and
4. exactly two empty lines before the next recipe slice's title box.

Example:

```text
+------------------------------------------------------------------------------+
| SLICE TITLE: Conversation Resolver                                           |
| IDENTITY: Recipe 0 (R0)                                                      |
| DESCRIPTION: Selects the minimum sufficient completed-transcript context for |
|              the current turn.                                               |
+------------------------------------------------------------------------------+
...R0 trace content...
SLICE STATUS> R0 Conversation Resolver COMPLETE


+------------------------------------------------------------------------------+
| SLICE TITLE: Intent                                                          |
| IDENTITY: Recipe 1 (R1)                                                      |
| DESCRIPTION: Converts the resolved turn into immutable requirements and      |
|              Context needs.                                                  |
+------------------------------------------------------------------------------+
```

The two empty lines are represented by three newline characters between the final character
of the status line and the first `+` of the following box.

## Current presentation registry

| Slice | Title | Short description |
|---|---|---|
| R0 | Conversation Resolver | Selects the minimum sufficient completed-transcript context for the current turn. |
| R1 | Intent | Converts the resolved turn into immutable requirements and Context needs. |

The executable source is `RECIPE_SLICE_PRESENTATIONS` in
`src/arcadia/lab/recipe_trace.py`. This table must remain synchronized with that registry.

## New-slice integration checklist

Every patch that exposes another recipe in the qualification CLI must:

- add its canonical ID, title, and short description to `RECIPE_SLICE_PRESENTATIONS`;
- add the same entry to the table above and update this document's date;
- emit `slice_started` immediately before entering the recipe controller;
- emit `slice_completed` only after the recipe controller returns successfully;
- keep specialist calls inside the owning recipe box rather than creating nested recipe boxes;
- preserve exactly two empty lines between completed and next slices; and
- add or extend deterministic tests for box text, slice order, and spacing.

This convention is presentation-only. It must not alter `CALL_DATA`, model messages, learned
outputs, host validation, work budgets, artifacts, routing, persistence, or authority standing.
