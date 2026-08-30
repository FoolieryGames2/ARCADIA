from __future__ import annotations

from copy import deepcopy

import pytest

from arcadia.core.canonical_json import (
    DuplicateJsonKeyError,
    NonFiniteJsonNumberError,
    TrailingJsonContentError,
    UnsupportedJsonValueError,
)
from arcadia.core.hashing import sha256_canonical_json
from arcadia.core.validation import (
    HOST_VALIDATOR_VERSION,
    JSON_SCHEMA_DIALECT,
    InstanceValidationError,
    SchemaDefinitionError,
    StrictJsonSchema,
    compile_strict_schema,
)


def _schema() -> dict[str, object]:
    return {
        "$schema": JSON_SCHEMA_DIALECT,
        "type": "object",
        "additionalProperties": False,
        "required": ["mode", "items", "request_id"],
        "properties": {
            "mode": {"type": "string", "enum": ["PLAN", "ANSWER"]},
            "items": {
                "type": "array",
                "maxItems": 2,
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["text"],
                    "properties": {"text": {"type": "string", "maxLength": 8}},
                },
            },
            "request_id": {"type": "string", "format": "uuid"},
        },
    }


def _instance() -> dict[str, object]:
    return {
        "mode": "PLAN",
        "items": [{"text": "bounded"}],
        "request_id": "12345678-1234-4234-9234-123456789abc",
    }


def _compiled() -> StrictJsonSchema:
    return compile_strict_schema(
        schema_id="intent.call-data", schema_version="v1", schema=_schema()
    )


def test_compile_snapshots_schema_and_records_identity() -> None:
    source = _schema()
    compiled = StrictJsonSchema.compile(
        schema_id="intent.call-data", schema_version="v1", schema=source
    )
    original_hash = compiled.schema_hash

    source["type"] = "array"

    assert compiled.schema_value()["type"] == "object"
    assert compiled.schema_hash == original_hash
    assert compiled.schema_hash == sha256_canonical_json(compiled.schema_value())
    assert compiled.validator_version == HOST_VALIDATOR_VERSION


@pytest.mark.parametrize("value", ["", "has space", "_leading", "x" * 129])
def test_compile_rejects_illegal_schema_identity_tokens(value: str) -> None:
    with pytest.raises(SchemaDefinitionError, match="canonical token"):
        compile_strict_schema(schema_id=value, schema_version="v1", schema=_schema())


def test_compile_requires_exact_draft_2020_12_declaration() -> None:
    schema = _schema()
    schema["$schema"] = "http://json-schema.org/draft-07/schema#"

    with pytest.raises(SchemaDefinitionError, match="Draft 2020-12"):
        compile_strict_schema(schema_id="test", schema_version="v1", schema=schema)


@pytest.mark.parametrize("schema", [True, [], "object", None])
def test_compile_requires_json_object_schema(schema: object) -> None:
    with pytest.raises(SchemaDefinitionError, match="schema must be a strict JSON object"):
        compile_strict_schema(schema_id="test", schema_version="v1", schema=schema)


def test_compile_wraps_meta_schema_failure() -> None:
    schema = _schema()
    schema["required"] = "mode"

    with pytest.raises(SchemaDefinitionError, match="invalid JSON Schema"):
        compile_strict_schema(schema_id="test", schema_version="v1", schema=schema)


def test_compile_rejects_non_json_schema_value() -> None:
    schema = _schema()
    schema["extension"] = ("not", "json")

    with pytest.raises(SchemaDefinitionError, match="schema is not strict JSON"):
        compile_strict_schema(schema_id="test", schema_version="v1", schema=schema)


@pytest.mark.parametrize(
    "mutate, expected_path",
    [
        (lambda s: s.pop("additionalProperties"), "/"),
        (
            lambda s: s["properties"]["items"]["items"].pop("additionalProperties"),
            "/properties/items/items",
        ),
        (
            lambda s: s.update(
                {
                    "$defs": {
                        "nested": {
                            "type": "object",
                            "properties": {"x": {"type": "string"}},
                        }
                    }
                }
            ),
            "/$defs/nested",
        ),
        (
            lambda s: s.update(
                {
                    "dependentSchemas": {
                        "mode": {"type": "object", "required": ["mode"]}
                    }
                }
            ),
            "/dependentSchemas/mode",
        ),
    ],
)
def test_compile_rejects_non_strict_object_schema(mutate: object, expected_path: str) -> None:
    schema = _schema()
    mutate(schema)

    with pytest.raises(SchemaDefinitionError, match="additionalProperties=false") as exc:
        compile_strict_schema(schema_id="test", schema_version="v1", schema=schema)

    assert expected_path in str(exc.value)


def test_compile_detects_object_in_type_union() -> None:
    schema = {
        "$schema": JSON_SCHEMA_DIALECT,
        "type": ["object", "null"],
    }

    with pytest.raises(SchemaDefinitionError, match="additionalProperties=false"):
        compile_strict_schema(schema_id="test", schema_version="v1", schema=schema)


def test_valid_instance_produces_deterministic_hash_bound_report() -> None:
    compiled = _compiled()
    instance = _instance()

    report = compiled.require_valid(instance)

    assert report.valid
    assert report.issues == ()
    assert report.schema_id == "intent.call-data"
    assert report.schema_version == "v1"
    assert report.schema_hash == compiled.schema_hash
    assert report.instance_hash == sha256_canonical_json(instance)
    assert report.to_value()["valid"] is True


def test_validation_does_not_apply_schema_defaults_or_mutate_instance() -> None:
    schema = _schema()
    schema["properties"]["optional"] = {"type": "string", "default": "invented"}
    compiled = compile_strict_schema(schema_id="test", schema_version="v1", schema=schema)
    instance = _instance()
    before = deepcopy(instance)

    compiled.require_valid(instance)

    assert instance == before
    assert "optional" not in instance


def test_unknown_fields_wrong_types_enum_and_bounds_are_all_reported() -> None:
    compiled = _compiled()
    instance = {
        "mode": "INVENTED",
        "items": [{"text": "too-long!", "authority": "SYSTEM"}] * 3,
        "request_id": "not-a-uuid",
        "unknown": True,
    }

    report = compiled.validate(instance)

    assert not report.valid
    keywords = {issue.keyword for issue in report.issues}
    assert {"additionalProperties", "enum", "format", "maxItems", "maxLength"} <= keywords
    assert tuple(report.issues) == tuple(
        sorted(
            report.issues,
            key=lambda issue: (
                issue.instance_path,
                issue.schema_path,
                issue.keyword,
                issue.message,
            ),
        )
    )


def test_json_pointer_paths_escape_property_names() -> None:
    schema = {
        "$schema": JSON_SCHEMA_DIALECT,
        "type": "object",
        "additionalProperties": False,
        "required": ["a/b~c"],
        "properties": {"a/b~c": {"type": "integer"}},
    }
    compiled = compile_strict_schema(schema_id="pointer", schema_version="v1", schema=schema)

    report = compiled.validate({"a/b~c": "wrong"})

    assert report.issues[0].instance_path == "/a~1b~0c"


def test_require_valid_attaches_complete_report() -> None:
    compiled = _compiled()

    with pytest.raises(InstanceValidationError, match="schema rejection") as exc:
        compiled.require_valid({"mode": "PLAN", "items": [], "request_id": "bad"})

    assert not exc.value.report.valid
    assert exc.value.report.schema_hash == compiled.schema_hash


@pytest.mark.parametrize(
    "payload, error",
    [
        ('{"mode":"PLAN","mode":"ANSWER"}', DuplicateJsonKeyError),
        ('{"mode":NaN}', NonFiniteJsonNumberError),
        ('{} trailing', TrailingJsonContentError),
    ],
)
def test_text_entry_point_preserves_strict_decoder_rejections(
    payload: str, error: type[ValueError]
) -> None:
    with pytest.raises(error):
        _compiled().validate_json(payload)


def test_same_compiled_schema_validates_host_and_final_rendered_data() -> None:
    compiled = _compiled()
    instance = _instance()

    host_report = compiled.require_valid(instance)
    parsed, rendered_report = compiled.validate_json(
        '{"items":[{"text":"bounded"}],"mode":"PLAN",'
        '"request_id":"12345678-1234-4234-9234-123456789abc"}'
    )

    assert parsed == instance
    assert rendered_report.valid
    assert rendered_report.schema_hash == host_report.schema_hash
    assert rendered_report.instance_hash == host_report.instance_hash


def test_bytes_entry_point_requires_strict_utf8_and_schema() -> None:
    compiled = _compiled()
    payload = (
        b'{"mode":"PLAN","items":[],"request_id":'
        b'"12345678-1234-4234-9234-123456789abc"}'
    )

    parsed, report = compiled.validate_json_bytes(payload)

    assert parsed["mode"] == "PLAN"
    assert report.valid
    with pytest.raises(InstanceValidationError):
        compiled.require_valid_json_bytes(b"{}")


def test_host_input_rejects_non_json_python_values_before_schema() -> None:
    compiled = _compiled()

    with pytest.raises(UnsupportedJsonValueError):
        compiled.validate({"mode": "PLAN", "items": (), "request_id": "x"})
