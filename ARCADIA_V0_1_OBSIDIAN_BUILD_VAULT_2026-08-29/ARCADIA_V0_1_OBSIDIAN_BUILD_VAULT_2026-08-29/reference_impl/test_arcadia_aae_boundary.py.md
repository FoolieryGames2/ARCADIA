---
title: "test_arcadia_aae_boundary.py"
project: "A.R.C.A.D.I.A."
version: "0.1-prototype"
checkpoint_date: "2026-08-29"
document_role: "reference-implementation"
source_path: "reference_impl/test_arcadia_aae_boundary.py"
source_sha256: "c1912ed5411d63b8a97226fc444d6ed76d61aa8b41fa27fa903a3636b717ec67"
source_bytes: 3941
source_integrity: "preserved"
tags:
  - "arcadia/v0-1"
  - "type/reference-implementation"
aliases:
  - "test_arcadia_aae_boundary.py"
---

> [!info] Obsidian navigation
> **Checkpoint role:** `reference-implementation`  
> **Frozen source:** `reference_impl/test_arcadia_aae_boundary.py` · SHA-256 `c1912ed5411d63b8…`  
> **Command center:** [[ARCADIA v0.1 - Command Center]]  
> **Connected:** [[arcadia_aae_boundary.py]] · [[ST01_BOUNDARY_UNIT_TEST.txt]] · [[04_ARCADIA_V0_1_AAE_CONTRACT_REGISTRY_AND_SERIALIZATION]]

# Source artifact — `test_arcadia_aae_boundary.py`

> [!note] Lossless-content conversion
> Original file type: `.py` · decoded as `utf-8`. The complete source text is retained below; the original SHA-256 is in frontmatter.

```python
#!/usr/bin/env python3
from __future__ import annotations

import unittest

from arcadia_aae_boundary import (
    AAECallDataError,
    CallDataBoundaryError,
    CallDataSchemaError,
    DuplicateJSONKeyError,
    NonFiniteJSONNumberError,
    TrailingJSONContentError,
    canonical_json_dumps,
    serialize_call_data,
    strict_json_loads,
    validate_rendered_aae_call_data,
)


SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "additionalProperties": False,
    "required": ["protected_literals", "attempt"],
    "properties": {
        "protected_literals": {
            "type": "array",
            "maxItems": 4,
            "items": {"type": "string", "maxLength": 128},
        },
        "attempt": {"type": "integer", "minimum": 1, "maximum": 3},
    },
}


class BoundaryTests(unittest.TestCase):
    def test_windows_path_is_escaped_by_serializer(self):
        value = {
            "protected_literals": [r"C:\Arcadia\exports\status.txt"],
            "attempt": 1,
        }
        payload = serialize_call_data(value, SCHEMA)
        self.assertIn(r"C:\\Arcadia\\exports\\status.txt", payload)
        self.assertEqual(strict_json_loads(payload), value)

    def test_handwritten_single_backslash_path_is_rejected(self):
        payload = '{"protected_literals":["C:\\Arcadia\\exports\\status.txt"],"attempt":1}'
        # Python string above contains single JSON backslashes in the final text.
        with self.assertRaises(AAECallDataError):
            strict_json_loads(payload)

    def test_duplicate_key_rejected(self):
        with self.assertRaises(DuplicateJSONKeyError):
            strict_json_loads('{"attempt":1,"attempt":2}')

    def test_nonfinite_rejected_on_parse(self):
        with self.assertRaises(NonFiniteJSONNumberError):
            strict_json_loads('{"attempt":NaN}')

    def test_nonfinite_rejected_on_serialize(self):
        with self.assertRaises(AAECallDataError):
            canonical_json_dumps({"x": float("nan")})

    def test_trailing_content_rejected(self):
        with self.assertRaises(TrailingJSONContentError):
            strict_json_loads('{"attempt":1} garbage')

    def test_unknown_field_rejected(self):
        with self.assertRaises(CallDataSchemaError):
            serialize_call_data(
                {"protected_literals": [], "attempt": 1, "extra": True},
                SCHEMA,
            )

    def test_wrong_type_rejected(self):
        with self.assertRaises(CallDataSchemaError):
            serialize_call_data(
                {"protected_literals": [], "attempt": "1"},
                SCHEMA,
            )

    def test_value_outside_bounds_rejected(self):
        with self.assertRaises(CallDataSchemaError):
            serialize_call_data(
                {"protected_literals": [], "attempt": 4},
                SCHEMA,
            )

    def test_schema_must_reject_unknown_fields(self):
        loose = {
            "type": "object",
            "properties": {"attempt": {"type": "integer"}},
        }
        with self.assertRaises(CallDataSchemaError):
            serialize_call_data({"attempt": 1}, loose)

    def test_final_rendered_aae_is_reparsed_and_schema_checked(self):
        value = {
            "protected_literals": [r"C:\Arcadia\exports\status.txt"],
            "attempt": 1,
        }
        payload = serialize_call_data(value, SCHEMA)
        aae = f"""<A.R.C.A.D.I.A_ADAPTER_CALL>\n[CALL_DATA]\n{payload}\n\n[RESPONSE_CONTRACT]\nReturn test object.\n</A.R.C.A.D.I.A_ADAPTER_CALL>"""
        self.assertEqual(validate_rendered_aae_call_data(aae, SCHEMA), value)

    def test_duplicate_markers_fail_closed(self):
        aae = "[CALL_DATA]\n{}\n[CALL_DATA]\n{}\n[RESPONSE_CONTRACT]\nx"
        with self.assertRaises(CallDataBoundaryError):
            validate_rendered_aae_call_data(aae, SCHEMA)


if __name__ == "__main__":
    unittest.main(verbosity=2)
```
