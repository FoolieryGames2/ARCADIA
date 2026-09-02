from __future__ import annotations

import pytest

from arcadia.contracts.policies.schema_rules import (
    STRICT_SCHEMA_POLICY_PRE_V1,
    STRICT_SCHEMA_POLICY_REGISTRY_PRE_V1,
    SchemaPolicyError,
    SchemaPolicyStatus,
    get_schema_policy,
    require_fixed_top_level_output_shape,
)
from arcadia.contracts.schemas.r0.scope_proposal import SCOPE_PROPOSAL_OUTPUT_SCHEMA
from arcadia.core.validation import JSON_SCHEMA_DIALECT, compile_strict_schema


def test_pre1_policy_records_reviewed_schema_authority_split() -> None:
    policy = STRICT_SCHEMA_POLICY_PRE_V1

    assert policy.status is SchemaPolicyStatus.PRE_VERSION
    assert policy.frozen is False
    assert policy.reject_unknown_object_fields is True
    assert policy.schema_owns_shape_and_syntax is True
    assert policy.host_owns_cross_field_and_state_semantics is True
    assert policy.fixed_output_top_level_shape is True
    assert policy.optional_fields_require_explicit_absence_semantics is True
    assert policy.model_selected_contract_structure_forbidden is True
    assert policy.silent_truncation_or_correction_forbidden is True
    assert policy.impossible_downstream_branch_rejected is True


def test_policy_registry_is_exact_and_immutable() -> None:
    policy = get_schema_policy("learned_call.strict_schema")
    assert policy is STRICT_SCHEMA_POLICY_PRE_V1

    with pytest.raises(TypeError):
        STRICT_SCHEMA_POLICY_REGISTRY_PRE_V1["other"] = policy  # type: ignore[index]
    with pytest.raises(KeyError, match="unknown schema policy"):
        get_schema_policy("missing")


def test_scope_proposal_output_satisfies_fixed_shape_policy() -> None:
    assert require_fixed_top_level_output_shape(SCOPE_PROPOSAL_OUTPUT_SCHEMA) is (
        SCOPE_PROPOSAL_OUTPUT_SCHEMA
    )


def test_fixed_shape_policy_rejects_optional_top_level_branch_field() -> None:
    schema = compile_strict_schema(
        schema_id="test.optional_output",
        schema_version="PRE-1",
        schema={
            "$schema": JSON_SCHEMA_DIALECT,
            "type": "object",
            "additionalProperties": False,
            "required": ["status"],
            "properties": {
                "status": {"type": "string"},
                "memory_hint": {"type": "string"},
            },
        },
    )

    with pytest.raises(SchemaPolicyError, match="fixed top-level field shape"):
        require_fixed_top_level_output_shape(schema)


def test_fixed_shape_policy_rejects_non_object_output() -> None:
    schema = compile_strict_schema(
        schema_id="test.scalar_output",
        schema_version="PRE-1",
        schema={"$schema": JSON_SCHEMA_DIALECT, "type": "string"},
    )

    with pytest.raises(SchemaPolicyError, match="type=object"):
        require_fixed_top_level_output_shape(schema)
