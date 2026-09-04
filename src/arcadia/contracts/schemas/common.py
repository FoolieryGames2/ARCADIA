"""Small schema-building vocabulary shared by frozen learned-call contracts."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from arcadia.contracts.aae.registry import get_contract
from arcadia.contracts.policies.schema_rules import require_fixed_top_level_output_shape
from arcadia.core.canonical_json import JsonValue
from arcadia.core.validation import JSON_SCHEMA_DIALECT, StrictJsonSchema, compile_strict_schema

TOKEN_PATTERN: Final = r"^[A-Za-z0-9][A-Za-z0-9._:+/\-]{0,127}$"
REF_PATTERN: Final = r"^[A-Z][A-Z0-9_]*[0-9][A-Z0-9._:+/\-]*$"
LOCAL_KEY_PATTERN: Final = r"^[A-Z][A-Z0-9_]*[0-9]+$"
HASH_PATTERN: Final = r"^sha256:[0-9a-f]{64}$"
LABEL_PATTERN: Final = r"^[A-Z][A-Z0-9_]{0,63}$"
MAX_TEXT: Final = 65_536
MAX_ITEMS: Final = 64


def text_schema(*, minimum: int = 0, maximum: int = MAX_TEXT) -> dict[str, JsonValue]:
    return {"type": "string", "minLength": minimum, "maxLength": maximum}


def token_schema() -> dict[str, JsonValue]:
    return {"type": "string", "pattern": TOKEN_PATTERN}


def ref_schema() -> dict[str, JsonValue]:
    return {"type": "string", "pattern": REF_PATTERN}


def local_key_schema() -> dict[str, JsonValue]:
    return {"type": "string", "pattern": LOCAL_KEY_PATTERN}


def label_schema() -> dict[str, JsonValue]:
    return {"type": "string", "pattern": LABEL_PATTERN}


def enum_schema(values: tuple[str, ...]) -> dict[str, JsonValue]:
    return {"type": "string", "enum": list(values)}


def array_schema(
    items: dict[str, JsonValue],
    *,
    minimum: int = 0,
    maximum: int = MAX_ITEMS,
    unique: bool = False,
) -> dict[str, JsonValue]:
    value: dict[str, JsonValue] = {
        "type": "array",
        "minItems": minimum,
        "maxItems": maximum,
        "items": items,
    }
    if unique:
        value["uniqueItems"] = True
    return value


def object_schema(properties: dict[str, JsonValue]) -> dict[str, JsonValue]:
    return {
        "type": "object",
        "additionalProperties": False,
        "required": list(properties),
        "properties": properties,
    }


def nullable(schema: dict[str, JsonValue]) -> dict[str, JsonValue]:
    return {"anyOf": [schema, {"type": "null"}]}


def refs_schema(*, minimum: int = 0) -> dict[str, JsonValue]:
    return array_schema(ref_schema(), minimum=minimum, unique=True)


def strings_schema(*, minimum: int = 0) -> dict[str, JsonValue]:
    return array_schema(text_schema(minimum=1), minimum=minimum, unique=True)


@dataclass(frozen=True, slots=True)
class ModeSchemas:
    mode: str
    input: StrictJsonSchema
    output: StrictJsonSchema

    def require_valid_call(self, call_data: JsonValue) -> JsonValue:
        self.input.require_valid(call_data)
        return call_data

    def require_valid_output(self, output: JsonValue) -> JsonValue:
        self.output.require_valid(output)
        return output


def compile_mode_schemas(
    mode: str,
    *,
    input_properties: dict[str, JsonValue],
    output_properties: dict[str, JsonValue],
) -> ModeSchemas:
    contract = get_contract(mode)
    input_schema = object_schema(
        {"mode": {"type": "string", "const": mode}, **input_properties}
    )
    output_schema = object_schema(
        {"mode": {"type": "string", "const": mode}, **output_properties}
    )
    input_schema["$schema"] = JSON_SCHEMA_DIALECT
    output_schema["$schema"] = JSON_SCHEMA_DIALECT
    return ModeSchemas(
        mode=mode,
        input=compile_strict_schema(
            schema_id=contract.input_schema.schema_id,
            schema_version=contract.input_schema.schema_version,
            schema=input_schema,
        ),
        output=require_fixed_top_level_output_shape(
            compile_strict_schema(
                schema_id=contract.output_schema.schema_id,
                schema_version=contract.output_schema.schema_version,
                schema=output_schema,
            )
        ),
    )
