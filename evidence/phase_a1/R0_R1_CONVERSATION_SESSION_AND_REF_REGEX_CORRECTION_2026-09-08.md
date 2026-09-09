# R0 -> R1 Conversation Session + REF Regex Compatibility Correction — 2026-09-08

## Standing

**PASS — narrow qualification-harness correction; R0/R1 semantic authority unchanged.**

This slice corrects two implementation/runtime-integration issues discovered from the
2026-09-08 resident BASE_ONLY qualification logs and transcript database.

## Correction 1 — llama.cpp-compatible reference regex

`REF_PATTERN` changes from:

```text
^[A-Z][A-Z0-9_]*[0-9][A-Z0-9._:+/\-]*$
```

to:

```text
^[A-Z][A-Z0-9_]*[0-9][A-Z0-9._:+/-]*$
```

The hyphen remains literal because it is the final character in the character class.
Representative equivalence tests require the old and new patterns to accept/reject the
same values under Python `re.ASCII`. This removes the unsupported escaped-hyphen form
reported by llama.cpp without broadening Arcadia's host validator.

This correction does **not** weaken or remove Recipe 1's stronger host-owned semantic
namespace checks such as `TERM_` / `REF_` local-key requirements.

## Correction 2 — session-scoped recipe conversation identity

The interactive CLI now lazily creates one host-owned `RecipeLabSession` for recipe mode.
Every recipe prompt in that interactive session receives the same authoritative
`conversation_uuid` and the isolated lab `TranscriptRepository`. The session survives a
resident runtime `/restart` because restarting llama.cpp is not a new conversation.

`/new` explicitly starts a fresh recipe conversation UUID. `/status` reports the active
recipe conversation UUID, or `not started` before the first recipe prompt.

One-shot recipe commands retain their existing behavior and receive a fresh conversation.
Direct-mode prompts are not inserted into the recipe transcript.

## Authority boundary

This is conversation identity/state plumbing, not a new semantic-memory source. OPEN or
failed qualification turns remain ineligible for R0 history. R0 continues to retrieve only
authoritative completed exchanges under its frozen transcript rules. No assistant Result,
publication, semantic memory, tool authority, or Recipe 2 behavior is fabricated.

## Targeted checks in the build environment

- Python compile check for all modified Python files: PASS.
- `REF_PATTERN` exact-value and representative old/new equivalence tests: 2 passed.
- Isolated interactive session-state exercise: same conversation for two prompts, `/new`
  changes it, third prompt uses the new conversation, and `/restart` returns the same active
  conversation: PASS.
- `git diff --check`: PASS.

## Integration completion on the pinned workstation

The compatibility spelling changes the exact Canonical JSON schema documents even though
the Python `re.ASCII` acceptance set is unchanged. The affected exact compiled hashes in
`manifests/aae_schema_catalog_pre1.json` were refreshed and the choice was recorded as
`D-0035`; the catalog remains PRE-1, unfrozen, non-dispatchable, and T0.

Pinned-workstation result after integration fixes:

```text
pytest: 620 passed
Ruff: PASS
MyPy: PASS (74 source files)
```

A resident smoke on loopback port `18081` compiled the revised schema and completed accepted
`SCOPE_PROPOSAL` and `SPELL_NORMALIZATION` calls before a later Recipe 1 controller namespace
check rejected the model's `MILK_001` local key. This establishes regex/runtime compatibility,
not full Recipe 1 semantic qualification.
