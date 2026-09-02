# A.R.C.A.D.I.A. — A1 Tunable Settings Handler PRE-1

**Date:** 2026-08-31
**Checklist:** #6 architecture
**Standing:** PRE-version implementation / jointly accepted architecture / Gate A1 remains OPEN

## Accepted boundary

**Logic decides what is legal. Settings decide how much / how aggressively.**

The AAE contract registry no longer owns numeric `FieldCaps`. Every logical mode instead carries a `settings_profile_id`. A separate handler owns tunable ceilings and supports:

```text
GLOBAL DEFAULTS
      -> BUDGET CLASS DEFAULTS
      -> PER-CONTRACT OVERRIDES
```

Budget classes:

```text
TINY
SMALL
MEDIUM
LARGE
FULL_CAPABLE
```

Supported PRE-1 knobs:

```text
max_input_tokens
max_output_tokens
max_string_chars
max_array_items
max_nesting_depth
max_source_excerpt_chars
context_headroom_tokens
```

Missing knobs are **UNRESOLVED**, never unlimited. Unknown knobs fail closed. Dynamic host availability can only reduce a configured ceiling. No silent truncation is authorized.

## Reproducibility

Every resolved profile can be converted to Canonical JSON V1 and SHA-256 hashed. A job/trace can therefore record the exact settings profile and hash that produced a result before later tuning changes the active values.

## PRE-1 file surface

```text
src/arcadia/settings/handler.py
src/arcadia/settings/__init__.py
configs/aae_tuning.pre1.toml
tests/unit/settings/test_handler.py
```

The editable TOML currently assigns only `SCOPE_PROPOSAL` and `SCOPE_VALIDATION`. It carries forward broad string/array ceilings already present in those executable schemas. Final token/output/headroom values and profiles for the remaining logical modes are deliberately left unresolved until runtime measurement.

## Registry integration

`AAEContractRecord.field_caps` was removed. `AAEContractRecord.settings_profile_id` now records the external tuning profile identity. Registry semantic authority therefore no longer changes merely because an operator later tunes a numeric limit.
