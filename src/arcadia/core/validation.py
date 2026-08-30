"""Strict, deterministic JSON Schema 2020-12 validation boundary."""

from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Final, cast

from jsonschema import Draft202012Validator, FormatChecker  # type: ignore[import-untyped]
from jsonschema.exceptions import SchemaError  # type: ignore[import-untyped]

from arcadia.core.canonical_json import (
    JsonValue,
    canonical_json_dumps,
    strict_json_loads,
    strict_json_loads_bytes,
)
from arcadia.core.hashing import Sha256Digest, sha256_canonical_json

JSON_SCHEMA_DIALECT: Final = "https://json-schema.org/draft/2020-12/schema"
HOST_VALIDATOR_VERSION: Final = "arcadia-json-schema-2020-12-v1"

_IDENTITY_PATTERN: Final = re.compile(
    r"[A-Za-z0-9][A-Za-z0-9._:+/-]{0,127}", flags=re.ASCII
)
_DIRECT_SCHEMA_KEYWORDS: Final = (
    "additionalProperties",
    "contains",
    "contentSchema",
    "else",
    "if",
    "items",
    "not",
    "propertyNames",
    "then",
    "unevaluatedItems",
    "unevaluatedProperties",
)
_ARRAY_SCHEMA_KEYWORDS: Final = ("allOf", "anyOf", "oneOf", "prefixItems")
_MAPPING_SCHEMA_KEYWORDS: Final = (
    "$defs",
    "dependentSchemas",
    "patternProperties",
    "properties",
)


class StrictValidationError(ValueError):
    """Base error for strict schema definition or instance rejection."""


class SchemaDefinitionError(StrictValidationError):
    """A schema is invalid, non-strict, or uses the wrong dialect."""


class InstanceValidationError(StrictValidationError):
    """A strict JSON instance does not satisfy its compiled schema."""

    def __init__(self, report: ValidationReport) -> None:
        self.report = report
        first = report.issues[0]
        super().__init__(
            f"schema rejection at {first.instance_path} "
            f"({first.keyword}): {first.message}"
        )


def _require_identity(name: str, value: object) -> str:
    if type(value) is not str or _IDENTITY_PATTERN.fullmatch(value) is None:
        raise SchemaDefinitionError(f"{name} is not a legal canonical token")
    return value


def _pointer(parts: Iterable[str | int]) -> str:
    encoded: list[str] = []
    for part in parts:
        text = str(part).replace("~", "~0").replace("/", "~1")
        encoded.append(text)
    return "" if not encoded else "/" + "/".join(encoded)


def _schema_path(path: str, keyword: str | int) -> str:
    escaped = str(keyword).replace("~", "~0").replace("/", "~1")
    return f"{path}/{escaped}" if path else f"/{escaped}"


def _is_object_schema(schema: dict[str, JsonValue]) -> bool:
    declared_type = schema.get("type")
    if declared_type == "object":
        return True
    if type(declared_type) is list and "object" in declared_type:
        return True
    object_keywords = {
        "additionalProperties",
        "dependentRequired",
        "dependentSchemas",
        "maxProperties",
        "minProperties",
        "patternProperties",
        "properties",
        "propertyNames",
        "required",
        "unevaluatedProperties",
    }
    return not object_keywords.isdisjoint(schema)


def _assert_strict_object_schemas(node: JsonValue, path: str = "") -> None:
    if type(node) is bool:
        return
    if type(node) is not dict:
        return

    if _is_object_schema(node) and node.get("additionalProperties") is not False:
        location = path or "/"
        raise SchemaDefinitionError(
            f"object schema at {location} must set additionalProperties=false"
        )

    for keyword in _DIRECT_SCHEMA_KEYWORDS:
        child = node.get(keyword)
        if type(child) is dict or type(child) is bool:
            _assert_strict_object_schemas(child, _schema_path(path, keyword))

    for keyword in _ARRAY_SCHEMA_KEYWORDS:
        children = node.get(keyword)
        if type(children) is list:
            for index, child in enumerate(children):
                if type(child) is dict or type(child) is bool:
                    _assert_strict_object_schemas(
                        child, _schema_path(_schema_path(path, keyword), index)
                    )

    for keyword in _MAPPING_SCHEMA_KEYWORDS:
        children = node.get(keyword)
        if type(children) is dict:
            for name, child in children.items():
                if type(child) is dict or type(child) is bool:
                    _assert_strict_object_schemas(
                        child, _schema_path(_schema_path(path, keyword), name)
                    )


def _schema_snapshot(schema: object) -> tuple[dict[str, JsonValue], str]:
    if type(schema) is not dict:
        raise SchemaDefinitionError("schema must be a strict JSON object")
    try:
        canonical = canonical_json_dumps(cast(JsonValue, schema))
        snapshot = strict_json_loads(canonical)
    except ValueError as exc:
        raise SchemaDefinitionError(f"schema is not strict JSON: {exc}") from exc
    if type(snapshot) is not dict:
        raise SchemaDefinitionError("schema must be a strict JSON object")
    return snapshot, canonical


@dataclass(frozen=True, slots=True, order=True)
class ValidationIssue:
    """One deterministic schema failure located with JSON Pointers."""

    instance_path: str
    schema_path: str
    keyword: str
    message: str

    def to_value(self) -> dict[str, JsonValue]:
        """Return a Canonical JSON-compatible issue value."""

        return {
            "instance_path": self.instance_path,
            "keyword": self.keyword,
            "message": self.message,
            "schema_path": self.schema_path,
        }


@dataclass(frozen=True, slots=True)
class ValidationReport:
    """Deterministic evidence tying a result to exact schema and input hashes."""

    schema_id: str
    schema_version: str
    schema_hash: Sha256Digest
    instance_hash: Sha256Digest
    issues: tuple[ValidationIssue, ...]
    validator_version: str = HOST_VALIDATOR_VERSION

    @property
    def valid(self) -> bool:
        """Return true only when the report contains no validation issue."""

        return not self.issues

    def to_value(self) -> dict[str, JsonValue]:
        """Return a Canonical JSON-compatible validation evidence value."""

        return {
            "instance_hash": self.instance_hash.value,
            "issues": [issue.to_value() for issue in self.issues],
            "schema_hash": self.schema_hash.value,
            "schema_id": self.schema_id,
            "schema_version": self.schema_version,
            "valid": self.valid,
            "validator_version": self.validator_version,
        }


@dataclass(frozen=True, slots=True)
class StrictJsonSchema:
    """An immutable strict-schema snapshot used before and after rendering."""

    schema_id: str
    schema_version: str
    canonical_schema: str
    schema_hash: Sha256Digest
    validator_version: str = HOST_VALIDATOR_VERSION

    @classmethod
    def compile(
        cls,
        *,
        schema_id: str,
        schema_version: str,
        schema: object,
    ) -> StrictJsonSchema:
        """Validate and snapshot one strict Draft 2020-12 schema."""

        identity = _require_identity("schema_id", schema_id)
        version = _require_identity("schema_version", schema_version)
        snapshot, canonical = _schema_snapshot(schema)
        if snapshot.get("$schema") != JSON_SCHEMA_DIALECT:
            raise SchemaDefinitionError(
                f"schema must declare the exact Draft 2020-12 dialect: {JSON_SCHEMA_DIALECT}"
            )
        try:
            Draft202012Validator.check_schema(snapshot)
        except SchemaError as exc:
            raise SchemaDefinitionError(f"invalid JSON Schema: {exc.message}") from exc
        _assert_strict_object_schemas(snapshot)
        return cls(
            schema_id=identity,
            schema_version=version,
            canonical_schema=canonical,
            schema_hash=sha256_canonical_json(snapshot),
        )

    def schema_value(self) -> dict[str, JsonValue]:
        """Return a fresh copy of the immutable schema snapshot."""

        value = strict_json_loads(self.canonical_schema)
        assert type(value) is dict
        return value

    def validate(self, instance: JsonValue) -> ValidationReport:
        """Validate one strict host value and return all failures deterministically."""

        canonical_json_dumps(instance)
        validator = Draft202012Validator(
            self.schema_value(), format_checker=FormatChecker()
        )
        issues = tuple(
            sorted(
                (
                    ValidationIssue(
                        instance_path=_pointer(error.absolute_path),
                        schema_path=_pointer(error.absolute_schema_path),
                        keyword=str(error.validator),
                        message=error.message,
                    )
                    for error in validator.iter_errors(instance)
                ),
                key=lambda issue: (
                    issue.instance_path,
                    issue.schema_path,
                    issue.keyword,
                    issue.message,
                ),
            )
        )
        return ValidationReport(
            schema_id=self.schema_id,
            schema_version=self.schema_version,
            schema_hash=self.schema_hash,
            instance_hash=sha256_canonical_json(instance),
            issues=issues,
        )

    def require_valid(self, instance: JsonValue) -> ValidationReport:
        """Return a valid report or fail closed with the complete report attached."""

        report = self.validate(instance)
        if not report.valid:
            raise InstanceValidationError(report)
        return report

    def validate_json(self, payload: str) -> tuple[JsonValue, ValidationReport]:
        """Strictly parse text, then apply this exact schema snapshot."""

        instance = strict_json_loads(payload)
        return instance, self.validate(instance)

    def require_valid_json(self, payload: str) -> JsonValue:
        """Strictly parse and require valid text, returning the parsed value."""

        instance = strict_json_loads(payload)
        self.require_valid(instance)
        return instance

    def validate_json_bytes(self, payload: bytes) -> tuple[JsonValue, ValidationReport]:
        """Strictly parse UTF-8 bytes, then apply this exact schema snapshot."""

        instance = strict_json_loads_bytes(payload)
        return instance, self.validate(instance)

    def require_valid_json_bytes(self, payload: bytes) -> JsonValue:
        """Strictly parse and require valid UTF-8 bytes."""

        instance = strict_json_loads_bytes(payload)
        self.require_valid(instance)
        return instance


def compile_strict_schema(
    *, schema_id: str, schema_version: str, schema: object
) -> StrictJsonSchema:
    """Compile an immutable strict Draft 2020-12 schema."""

    return StrictJsonSchema.compile(
        schema_id=schema_id,
        schema_version=schema_version,
        schema=schema,
    )
