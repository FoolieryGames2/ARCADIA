from __future__ import annotations

import re

from arcadia.contracts.schemas.common import REF_PATTERN

OLD_REF_PATTERN = r"^[A-Z][A-Z0-9_]*[0-9][A-Z0-9._:+/\-]*$"


def test_ref_pattern_uses_llama_cpp_compatible_hyphen_form() -> None:
    assert REF_PATTERN == r"^[A-Z][A-Z0-9_]*[0-9][A-Z0-9._:+/-]*$"


def test_ref_pattern_change_preserves_representative_python_semantics() -> None:
    samples = (
        "S001",
        "TERM_1",
        "A1",
        "R001/foo-bar",
        "REF_9:part.two",
        "bad",
        "A",
        "-A1",
        "A 1",
        "A1?",
    )
    for sample in samples:
        old_matches = re.fullmatch(OLD_REF_PATTERN, sample, flags=re.ASCII) is not None
        new_matches = re.fullmatch(REF_PATTERN, sample, flags=re.ASCII) is not None
        assert new_matches == old_matches, sample
