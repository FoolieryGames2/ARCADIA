---
title: "arcadia_aae_boundary.py"
project: "A.R.C.A.D.I.A."
version: "0.1-prototype"
checkpoint_date: "2026-08-29"
document_role: "reference-implementation"
source_path: "reference_impl/arcadia_aae_boundary.py"
source_sha256: "3f38449d8add27b00e12a30b9b20578c842dbf1676091d813384c196d9a12281"
source_bytes: 7271
source_integrity: "preserved"
tags:
  - "arcadia/v0-1"
  - "type/reference-implementation"
aliases:
  - "arcadia_aae_boundary.py"
---

> [!info] Obsidian navigation
> **Checkpoint role:** `reference-implementation`  
> **Frozen source:** `reference_impl/arcadia_aae_boundary.py` · SHA-256 `3f38449d8add27b0…`  
> **Command center:** [[ARCADIA v0.1 - Command Center]]  
> **Connected:** [[04_ARCADIA_V0_1_AAE_CONTRACT_REGISTRY_AND_SERIALIZATION]] · [[test_arcadia_aae_boundary.py]] · [[ST01_BOUNDARY_UNIT_TEST.txt]]

# Source artifact — `arcadia_aae_boundary.py`

> [!note] Lossless-content conversion
> Original file type: `.py` · decoded as `utf-8`. The complete source text is retained below; the original SHA-256 is in frontmatter.

```python
#!/usr/bin/env python3
"""A.R.C.A.D.I.A. ST-01 CALL_DATA serialization and pre-dispatch validation boundary.

This module deliberately solves only the CALL_DATA safety defect identified by
ST-01. It does not claim to make the complete textual AAE injection-safe; that
is a separate contract/serialization problem (ST-07).
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Mapping

from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError, ValidationError


CALL_DATA_MARKER = "[CALL_DATA]"
RESPONSE_CONTRACT_MARKER = "[RESPONSE_CONTRACT]"


class AAECallDataError(ValueError):
    """Base error for CALL_DATA boundary rejection."""


class DuplicateJSONKeyError(AAECallDataError):
    pass


class NonFiniteJSONNumberError(AAECallDataError):
    pass


class TrailingJSONContentError(AAECallDataError):
    pass


class CallDataSchemaError(AAECallDataError):
    pass


class CallDataBoundaryError(AAECallDataError):
    pass


def _strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateJSONKeyError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _reject_constant(value: str) -> Any:
    raise NonFiniteJSONNumberError(f"non-finite JSON number: {value}")


_STRICT_DECODER = json.JSONDecoder(
    object_pairs_hook=_strict_object,
    parse_constant=_reject_constant,
)


def strict_json_loads(payload: str) -> Any:
    """Parse exactly one strict JSON value and reject trailing content."""
    try:
        value, end = _STRICT_DECODER.raw_decode(payload.lstrip())
    except (AAECallDataError, json.JSONDecodeError) as exc:
        if isinstance(exc, AAECallDataError):
            raise
        raise AAECallDataError(f"invalid JSON: {exc}") from exc
    trailing = payload.lstrip()[end:].strip()
    if trailing:
        raise TrailingJSONContentError("non-JSON trailing content")
    return value


def canonical_json_dumps(value: Any) -> str:
    """Canonical JSON V1 projection for AAE CALL_DATA.

    - UTF-8 text / no ASCII-only rewriting
    - deterministic key ordering
    - compact separators
    - non-finite numbers forbidden
    """
    try:
        return json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
    except (TypeError, ValueError) as exc:
        raise AAECallDataError(f"CALL_DATA is not canonically serializable: {exc}") from exc


def _assert_strict_object_schemas(node: Any, path: str = "$") -> None:
    """Require object schemas to reject unknown properties.

    This is intentionally conservative. Every object-shaped schema reachable via
    common composition keywords must explicitly set additionalProperties=false.
    """
    if isinstance(node, bool):
        return
    if not isinstance(node, Mapping):
        return

    node_type = node.get("type")
    is_object = node_type == "object" or "properties" in node
    if is_object and node.get("additionalProperties") is not False:
        raise CallDataSchemaError(
            f"schema object at {path} must set additionalProperties=false"
        )

    if "properties" in node:
        for key, child in node["properties"].items():
            _assert_strict_object_schemas(child, f"{path}.properties.{key}")
    if "patternProperties" in node:
        for key, child in node["patternProperties"].items():
            _assert_strict_object_schemas(child, f"{path}.patternProperties.{key}")
    if "items" in node:
        _assert_strict_object_schemas(node["items"], f"{path}.items")
    if "prefixItems" in node:
        for idx, child in enumerate(node["prefixItems"]):
            _assert_strict_object_schemas(child, f"{path}.prefixItems[{idx}]")
    for keyword in ("allOf", "anyOf", "oneOf"):
        if keyword in node:
            for idx, child in enumerate(node[keyword]):
                _assert_strict_object_schemas(child, f"{path}.{keyword}[{idx}]")
    for keyword in ("not", "if", "then", "else", "contains"):
        if keyword in node:
            _assert_strict_object_schemas(node[keyword], f"{path}.{keyword}")
    if "$defs" in node:
        for key, child in node["$defs"].items():
            _assert_strict_object_schemas(child, f"{path}.$defs.{key}")


def validate_schema_is_strict(schema: Mapping[str, Any]) -> Draft202012Validator:
    try:
        Draft202012Validator.check_schema(schema)
    except SchemaError as exc:
        raise CallDataSchemaError(f"invalid JSON Schema: {exc.message}") from exc
    _assert_strict_object_schemas(schema)
    return Draft202012Validator(schema)


def validate_call_data(value: Any, schema: Mapping[str, Any]) -> None:
    validator = validate_schema_is_strict(schema)
    errors = sorted(validator.iter_errors(value), key=lambda e: list(e.absolute_path))
    if errors:
        error: ValidationError = errors[0]
        location = "$"
        for part in error.absolute_path:
            location += f"[{part!r}]" if isinstance(part, int) else f".{part}"
        raise CallDataSchemaError(f"CALL_DATA schema rejection at {location}: {error.message}")


def serialize_call_data(value: Any, schema: Mapping[str, Any]) -> str:
    """Validate -> canonical serialize -> strict reparse -> revalidate -> equality check."""
    validate_call_data(value, schema)
    rendered = canonical_json_dumps(value)
    reparsed = strict_json_loads(rendered)
    validate_call_data(reparsed, schema)
    if reparsed != value:
        raise AAECallDataError("CALL_DATA changed during canonical round-trip")
    return rendered


def extract_rendered_call_data(rendered_aae: str) -> str:
    """Extract exactly one CALL_DATA segment from the final rendered AAE."""
    call_count = rendered_aae.count(CALL_DATA_MARKER)
    response_count = rendered_aae.count(RESPONSE_CONTRACT_MARKER)
    if call_count != 1 or response_count != 1:
        raise CallDataBoundaryError(
            f"expected exactly one CALL_DATA and one RESPONSE_CONTRACT marker; "
            f"got CALL_DATA={call_count}, RESPONSE_CONTRACT={response_count}"
        )
    start = rendered_aae.index(CALL_DATA_MARKER) + len(CALL_DATA_MARKER)
    end = rendered_aae.index(RESPONSE_CONTRACT_MARKER)
    if end <= start:
        raise CallDataBoundaryError("RESPONSE_CONTRACT occurs before CALL_DATA payload")
    return rendered_aae[start:end].strip()


def validate_rendered_aae_call_data(
    rendered_aae: str,
    schema: Mapping[str, Any],
) -> Any:
    """Final pre-dispatch gate over the bytes/text the specialist will receive."""
    payload = extract_rendered_call_data(rendered_aae)
    value = strict_json_loads(payload)
    validate_call_data(value, schema)
    return value


@dataclass(frozen=True)
class PreparedCallData:
    """Host-owned result of a successful ST-01 gate."""

    canonical_json: str
    parsed_value: Any


def prepare_call_data(value: Any, schema: Mapping[str, Any]) -> PreparedCallData:
    rendered = serialize_call_data(value, schema)
    parsed = strict_json_loads(rendered)
    return PreparedCallData(canonical_json=rendered, parsed_value=parsed)
```
