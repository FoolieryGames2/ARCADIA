from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from arcadia.contracts.aae.registry import AAE_REGISTRY_PRE_V1, get_contract
from arcadia.contracts.policies.schema_rules import require_fixed_top_level_output_shape
from arcadia.contracts.schemas import LEARNED_MODE_SCHEMAS
from arcadia.core.canonical_json import strict_json_loads
from arcadia.core.validation import InstanceValidationError


def _pattern_string(pattern: str, index: int) -> str:
    if pattern == r"^sha256:[0-9a-f]{64}$":
        return "sha256:" + f"{index + 1:064x}"
    if "[A-Z][A-Z0-9_]*[0-9]" in pattern:
        return f"R{index + 1:03d}"
    if "[A-Z][A-Z0-9_]*[0-9]+" in pattern:
        return f"N{index + 1}"
    if pattern.startswith("^[A-Z]"):
        return f"LABEL_{index + 1}"
    return f"TOKEN-{index + 1}"


def _example(schema: dict[str, Any], index: int = 0) -> Any:
    if "const" in schema:
        return schema["const"]
    if "enum" in schema:
        values = schema["enum"]
        return values[index % len(values)]
    if "anyOf" in schema:
        return _example(schema["anyOf"][0], index)
    kind = schema.get("type")
    if kind == "object":
        return {
            name: _example(schema["properties"][name], child_index)
            for child_index, name in enumerate(schema["required"])
        }
    if kind == "array":
        count = schema.get("minItems", 0)
        return [_example(schema["items"], item_index) for item_index in range(count)]
    if kind == "string":
        if "pattern" in schema:
            return _pattern_string(schema["pattern"], index)
        return "x" * max(1, schema.get("minLength", 0))
    if kind == "integer":
        return schema.get("minimum", 0)
    if kind == "number":
        return schema.get("minimum", 0)
    if kind == "boolean":
        return True
    if kind == "null":
        return None
    raise AssertionError(f"test generator does not support schema: {schema}")


def test_every_registered_learned_mode_has_one_strict_schema_pair() -> None:
    assert set(LEARNED_MODE_SCHEMAS) == set(AAE_REGISTRY_PRE_V1)
    assert len(LEARNED_MODE_SCHEMAS) == 20


def test_schema_identity_and_fixed_output_shape_match_aae_registry() -> None:
    for mode, schemas in LEARNED_MODE_SCHEMAS.items():
        contract = get_contract(mode)
        assert (schemas.input.schema_id, schemas.input.schema_version) == (
            contract.input_schema.schema_id,
            contract.input_schema.schema_version,
        )
        assert (schemas.output.schema_id, schemas.output.schema_version) == (
            contract.output_schema.schema_id,
            contract.output_schema.schema_version,
        )
        assert require_fixed_top_level_output_shape(schemas.output) is schemas.output


def test_every_schema_accepts_a_generated_complete_fixed_shape_example() -> None:
    for schemas in LEARNED_MODE_SCHEMAS.values():
        schemas.input.require_valid(_example(schemas.input.schema_value()))
        schemas.output.require_valid(_example(schemas.output.schema_value()))


def test_every_learned_boundary_rejects_unknown_input_and_output_fields() -> None:
    for schemas in LEARNED_MODE_SCHEMAS.values():
        call_data = _example(schemas.input.schema_value())
        output = _example(schemas.output.schema_value())
        call_data["unknown_authority"] = True
        output["route_to"] = "BYPASS_HOST"
        with pytest.raises(InstanceValidationError):
            schemas.input.require_valid(call_data)
        with pytest.raises(InstanceValidationError):
            schemas.output.require_valid(output)


def test_pre1_manifest_locks_every_exact_schema_hash() -> None:
    root = Path(__file__).resolve().parents[4]
    manifest = strict_json_loads(
        (root / "manifests" / "aae_schema_catalog_pre1.json").read_text(encoding="utf-8")
    )
    assert type(manifest) is dict
    assert manifest["catalog_version"] == "AAE-SCHEMAS-PRE-1"
    assert manifest["dispatch_enabled"] is False
    recorded = manifest["modes"]
    assert type(recorded) is dict
    actual = {
        mode: [schemas.input.schema_hash.value, schemas.output.schema_hash.value]
        for mode, schemas in LEARNED_MODE_SCHEMAS.items()
    }
    assert recorded == actual
