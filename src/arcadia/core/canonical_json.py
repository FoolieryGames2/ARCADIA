"""Canonical JSON V1 encoding and fail-closed strict decoding."""

from __future__ import annotations

import json
import math
import re
from typing import cast

type JsonScalar = str | int | float | bool | None
type JsonValue = JsonScalar | list[JsonValue] | dict[str, JsonValue]


class CanonicalJsonError(ValueError):
    """Base error for Canonical JSON V1 encoding or strict decoding."""


class MalformedJsonError(CanonicalJsonError):
    """The input is not one syntactically valid JSON value."""


class DuplicateJsonKeyError(CanonicalJsonError):
    """An object repeats a decoded key at the same nesting level."""


class NonFiniteJsonNumberError(CanonicalJsonError):
    """A parsed or supplied number is NaN or infinite."""


class TrailingJsonContentError(CanonicalJsonError):
    """Non-whitespace content follows the first JSON value."""


class UnsupportedJsonValueError(CanonicalJsonError):
    """A Python value is outside the strict JSON data model."""


class NonCanonicalJsonError(CanonicalJsonError):
    """Valid strict JSON does not use the exact Canonical JSON V1 rendering."""


_LEADING_JSON_WHITESPACE = re.compile(r"[ \t\r\n]*", flags=re.ASCII)


def _strict_object(pairs: list[tuple[str, JsonValue]]) -> dict[str, JsonValue]:
    result: dict[str, JsonValue] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateJsonKeyError(f"duplicate JSON object key: {key!r}")
        result[key] = value
    return result


def _reject_constant(value: str) -> JsonValue:
    raise NonFiniteJsonNumberError(f"non-finite JSON number: {value}")


def _parse_finite_float(value: str) -> float:
    parsed = float(value)
    if not math.isfinite(parsed):
        raise NonFiniteJsonNumberError(f"JSON number exceeds finite range: {value}")
    return parsed


_STRICT_DECODER = json.JSONDecoder(
    object_pairs_hook=_strict_object,
    parse_constant=_reject_constant,
    parse_float=_parse_finite_float,
    strict=True,
)


def _validate_unicode(value: str, path: str) -> None:
    try:
        value.encode("utf-8", errors="strict")
    except UnicodeEncodeError as exc:
        raise UnsupportedJsonValueError(f"invalid Unicode scalar at {path}") from exc


def _validate_json_value(
    value: object,
    *,
    path: str = "$",
    active_containers: set[int] | None = None,
) -> None:
    if value is None or type(value) is bool or type(value) is int:
        return
    if type(value) is float:
        if not math.isfinite(value):
            raise NonFiniteJsonNumberError(f"non-finite number at {path}")
        return
    if type(value) is str:
        _validate_unicode(value, path)
        return

    active = active_containers if active_containers is not None else set()
    if type(value) is list:
        identity = id(value)
        if identity in active:
            raise UnsupportedJsonValueError(f"circular JSON array at {path}")
        active.add(identity)
        try:
            for index, item in enumerate(value):
                _validate_json_value(item, path=f"{path}[{index}]", active_containers=active)
        finally:
            active.remove(identity)
        return

    if type(value) is dict:
        identity = id(value)
        if identity in active:
            raise UnsupportedJsonValueError(f"circular JSON object at {path}")
        active.add(identity)
        try:
            for key, item in value.items():
                if type(key) is not str:
                    raise UnsupportedJsonValueError(f"non-string object key at {path}")
                _validate_unicode(key, f"{path}.<key>")
                _validate_json_value(item, path=f"{path}.{key}", active_containers=active)
        finally:
            active.remove(identity)
        return

    raise UnsupportedJsonValueError(
        f"unsupported value at {path}: {type(value).__qualname__}"
    )


def strict_json_loads(payload: str) -> JsonValue:
    """Decode exactly one JSON value with only RFC JSON whitespace around it."""

    if type(payload) is not str:
        raise MalformedJsonError("JSON input must be text")
    if payload.startswith("\ufeff"):
        raise MalformedJsonError("a Unicode BOM is not legal JSON content")

    start = _LEADING_JSON_WHITESPACE.match(payload)
    assert start is not None
    try:
        value, end = _STRICT_DECODER.raw_decode(payload, start.end())
    except CanonicalJsonError:
        raise
    except RecursionError as exc:
        raise UnsupportedJsonValueError("JSON nesting exceeds the host limit") from exc
    except json.JSONDecodeError as exc:
        raise MalformedJsonError(
            f"invalid JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}"
        ) from exc

    trailing = payload[end:]
    if trailing.strip(" \t\r\n"):
        raise TrailingJsonContentError("non-JSON trailing content")
    try:
        _validate_json_value(value)
    except RecursionError as exc:
        raise UnsupportedJsonValueError("JSON nesting exceeds the host limit") from exc
    return cast(JsonValue, value)


def strict_json_loads_bytes(payload: bytes) -> JsonValue:
    """Decode a strict UTF-8 byte representation of exactly one JSON value."""

    if type(payload) is not bytes:
        raise MalformedJsonError("JSON byte input must use the bytes type")
    try:
        text = payload.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise MalformedJsonError("JSON bytes are not valid UTF-8") from exc
    return strict_json_loads(text)


def canonical_json_dumps(value: JsonValue) -> str:
    """Encode a strict JSON value using the frozen Canonical JSON V1 profile.

    V1 preserves Unicode scalar values without normalization, sorts object keys
    by Python/Unicode code-point order, uses compact separators, emits no final
    newline, and rejects non-finite or non-JSON Python values.
    """

    try:
        _validate_json_value(value)
    except RecursionError as exc:
        raise UnsupportedJsonValueError("JSON nesting exceeds the host limit") from exc
    try:
        rendered = json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        rendered.encode("utf-8", errors="strict")
    except (TypeError, ValueError, UnicodeEncodeError, RecursionError) as exc:
        raise UnsupportedJsonValueError("value cannot be encoded as Canonical JSON V1") from exc
    return rendered


def canonical_json_dump_bytes(value: JsonValue) -> bytes:
    """Encode Canonical JSON V1 as UTF-8 bytes without a BOM or newline."""

    return canonical_json_dumps(value).encode("utf-8")


def require_canonical_json(payload: str) -> JsonValue:
    """Return the decoded value only when the input is already canonical V1."""

    value = strict_json_loads(payload)
    if canonical_json_dumps(value) != payload:
        raise NonCanonicalJsonError("JSON text is valid but is not Canonical JSON V1")
    return value
