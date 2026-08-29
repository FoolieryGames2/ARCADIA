---
title: "ST01_BOUNDARY_UNIT_TEST.txt"
project: "A.R.C.A.D.I.A."
version: "0.1-prototype"
checkpoint_date: "2026-08-29"
document_role: "validation-evidence"
source_path: "reference/ST01_BOUNDARY_UNIT_TEST.txt"
source_sha256: "f82ab6a801a5e3fbb66698ca830407dd82c6d239d8e8bad09840e86995ee5497"
source_bytes: 1567
source_integrity: "preserved"
tags:
  - "arcadia/v0-1"
  - "type/validation"
  - "type/reference"
aliases:
  - "ST01_BOUNDARY_UNIT_TEST.txt"
---

> [!info] Obsidian navigation
> **Checkpoint role:** `validation-evidence`  
> **Frozen source:** `reference/ST01_BOUNDARY_UNIT_TEST.txt` · SHA-256 `f82ab6a801a5e3fb…`  
> **Command center:** [[ARCADIA v0.1 - Command Center]]  
> **Connected:** [[06_ARCADIA_V0_1_QUALIFICATION_AND_STRESS_GATES]] · [[arcadia_aae_boundary.py]] · [[test_arcadia_aae_boundary.py]]

# Source artifact — `ST01_BOUNDARY_UNIT_TEST.txt`

> [!note] Lossless-content conversion
> Original file type: `.txt` · decoded as `utf-8`. The complete source text is retained below; the original SHA-256 is in frontmatter.

```text
test_duplicate_key_rejected (test_arcadia_aae_boundary.BoundaryTests.test_duplicate_key_rejected) ... ok
test_duplicate_markers_fail_closed (test_arcadia_aae_boundary.BoundaryTests.test_duplicate_markers_fail_closed) ... ok
test_final_rendered_aae_is_reparsed_and_schema_checked (test_arcadia_aae_boundary.BoundaryTests.test_final_rendered_aae_is_reparsed_and_schema_checked) ... ok
test_handwritten_single_backslash_path_is_rejected (test_arcadia_aae_boundary.BoundaryTests.test_handwritten_single_backslash_path_is_rejected) ... ok
test_nonfinite_rejected_on_parse (test_arcadia_aae_boundary.BoundaryTests.test_nonfinite_rejected_on_parse) ... ok
test_nonfinite_rejected_on_serialize (test_arcadia_aae_boundary.BoundaryTests.test_nonfinite_rejected_on_serialize) ... ok
test_schema_must_reject_unknown_fields (test_arcadia_aae_boundary.BoundaryTests.test_schema_must_reject_unknown_fields) ... ok
test_trailing_content_rejected (test_arcadia_aae_boundary.BoundaryTests.test_trailing_content_rejected) ... ok
test_unknown_field_rejected (test_arcadia_aae_boundary.BoundaryTests.test_unknown_field_rejected) ... ok
test_value_outside_bounds_rejected (test_arcadia_aae_boundary.BoundaryTests.test_value_outside_bounds_rejected) ... ok
test_windows_path_is_escaped_by_serializer (test_arcadia_aae_boundary.BoundaryTests.test_windows_path_is_escaped_by_serializer) ... ok
test_wrong_type_rejected (test_arcadia_aae_boundary.BoundaryTests.test_wrong_type_rejected) ... ok

----------------------------------------------------------------------
Ran 12 tests in 0.008s

OK
```
