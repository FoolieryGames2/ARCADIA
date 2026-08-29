from __future__ import annotations

import math

import pytest
from hypothesis import given
from hypothesis import strategies as st

from arcadia.core.canonical_json import (
    DuplicateJsonKeyError,
    MalformedJsonError,
    NonCanonicalJsonError,
    NonFiniteJsonNumberError,
    TrailingJsonContentError,
    UnsupportedJsonValueError,
    canonical_json_dump_bytes,
    canonical_json_dumps,
    require_canonical_json,
    strict_json_loads,
    strict_json_loads_bytes,
)

JSON_SCALARS = st.none() | st.booleans() | st.integers() | st.text()
JSON_VALUES = st.recursive(
    JSON_SCALARS,
    lambda children: st.lists(children, max_size=5)
    | st.dictionaries(st.text(max_size=12), children, max_size=5),
    max_leaves=20,
)


def test_canonical_profile_is_sorted_compact_unicode_and_path_safe() -> None:
    value = {
        "z": r"C:\Arcadia\exports\status.txt",
        "é": "snowman ☃",
        "a": [True, None, 3],
    }

    rendered = canonical_json_dumps(value)

    assert rendered == (
        '{"a":[true,null,3],"z":"C:\\\\Arcadia\\\\exports\\\\status.txt",'
        '"é":"snowman ☃"}'
    )
    assert strict_json_loads(rendered) == value
    assert canonical_json_dump_bytes(value) == rendered.encode("utf-8")


@given(JSON_VALUES)
def test_canonical_round_trip_is_deterministic(value: object) -> None:
    rendered = canonical_json_dumps(value)  # type: ignore[arg-type]

    assert canonical_json_dumps(strict_json_loads(rendered)) == rendered
    assert require_canonical_json(rendered) == value


def test_insertion_order_does_not_change_output() -> None:
    assert canonical_json_dumps({"b": 2, "a": 1}) == canonical_json_dumps({"a": 1, "b": 2})


@pytest.mark.parametrize(
    "payload",
    (
        '{"a":1,"a":2}',
        '{"outer":{"x":1,"x":2}}',
        '{"a":1,"\\u0061":2}',
    ),
)
def test_duplicate_decoded_keys_are_rejected_at_every_depth(payload: str) -> None:
    with pytest.raises(DuplicateJsonKeyError):
        strict_json_loads(payload)


@pytest.mark.parametrize(
    "payload",
    (
        "NaN",
        "Infinity",
        "-Infinity",
        '{"value":NaN}',
        "1e9999",
        "-1e9999",
    ),
)
def test_nonfinite_and_overflow_numbers_are_rejected_on_decode(payload: str) -> None:
    with pytest.raises(NonFiniteJsonNumberError):
        strict_json_loads(payload)


@pytest.mark.parametrize("value", (math.nan, math.inf, -math.inf))
def test_nonfinite_numbers_are_rejected_on_encode(value: float) -> None:
    with pytest.raises(NonFiniteJsonNumberError):
        canonical_json_dumps({"value": value})


@pytest.mark.parametrize(
    "payload",
    (
        "{} garbage",
        "{}{}",
        "null false",
        "[]\u00a0",
    ),
)
def test_trailing_non_json_content_is_rejected(payload: str) -> None:
    with pytest.raises(TrailingJsonContentError):
        strict_json_loads(payload)


def test_only_json_whitespace_may_surround_the_value() -> None:
    assert strict_json_loads(" \t\r\n{\"ok\":true}\r\n ") == {"ok": True}

    with pytest.raises(MalformedJsonError):
        strict_json_loads("\u00a0{}")


@pytest.mark.parametrize(
    "payload",
    (
        "",
        "{",
        '"unterminated',
        '"bad\\qescape"',
        '"raw\x01control"',
        "\ufeff{}",
        r'"\uD800"',
    ),
)
def test_malformed_or_non_unicode_json_is_rejected(payload: str) -> None:
    with pytest.raises((MalformedJsonError, UnsupportedJsonValueError)):
        strict_json_loads(payload)


def test_strict_bytes_require_utf8_without_bom() -> None:
    assert strict_json_loads_bytes('"☃"'.encode()) == "☃"

    with pytest.raises(MalformedJsonError):
        strict_json_loads_bytes(b'"\xff"')
    with pytest.raises(MalformedJsonError):
        strict_json_loads_bytes(b"\xef\xbb\xbf{}")


@pytest.mark.parametrize(
    "value",
    (
        (1, 2),
        {1, 2},
        {1: "coercion forbidden"},
        {"bad": "\ud800"},
    ),
)
def test_non_json_python_values_are_not_coerced(value: object) -> None:
    with pytest.raises(UnsupportedJsonValueError):
        canonical_json_dumps(value)  # type: ignore[arg-type]


def test_circular_containers_are_rejected() -> None:
    value: list[object] = []
    value.append(value)

    with pytest.raises(UnsupportedJsonValueError, match="circular"):
        canonical_json_dumps(value)  # type: ignore[arg-type]


def test_excessive_nesting_is_rejected_by_encode_and_decode() -> None:
    value: object = 0
    for _ in range(1_100):
        value = [value]

    with pytest.raises(UnsupportedJsonValueError, match="nesting"):
        canonical_json_dumps(value)  # type: ignore[arg-type]
    with pytest.raises(UnsupportedJsonValueError, match="nesting"):
        strict_json_loads("[" * 1_100 + "0" + "]" * 1_100)


@pytest.mark.parametrize(
    "payload",
    (
        '{"b":2,"a":1}',
        '{"a": 1}',
        '{"é":"\\u00e9"}',
        " true",
        "true\n",
    ),
)
def test_valid_but_noncanonical_json_is_rejected_by_canonical_gate(payload: str) -> None:
    with pytest.raises(NonCanonicalJsonError):
        require_canonical_json(payload)
