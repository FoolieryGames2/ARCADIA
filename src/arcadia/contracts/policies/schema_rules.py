"""PRE-1 shared strict-schema policy for learned AAE contracts.

This module records the review decisions that apply across learned-call schemas.
It is deliberately PRE_VERSION: it constrains current schema work without claiming
that the full Phase A1 schema/policy layer is frozen.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from types import MappingProxyType
from typing import Final

from arcadia.core.validation import StrictJsonSchema


class SchemaPolicyStatus(StrEnum):
    """Lifecycle state for a shared schema-policy definition."""

    PRE_VERSION = "PRE_VERSION"
    FROZEN = "FROZEN"


@dataclass(frozen=True, slots=True)
class StrictSchemaPolicy:
    """Reviewable policy separating JSON shape from host semantic authority."""

    policy_id: str
    policy_version: str
    status: SchemaPolicyStatus
    reject_unknown_object_fields: bool
    schema_owns_shape_and_syntax: bool
    host_owns_cross_field_and_state_semantics: bool
    fixed_output_top_level_shape: bool
    optional_fields_require_explicit_absence_semantics: bool
    model_selected_contract_structure_forbidden: bool
    silent_truncation_or_correction_forbidden: bool
    impossible_downstream_branch_rejected: bool

    @property
    def frozen(self) -> bool:
        return self.status is SchemaPolicyStatus.FROZEN


STRICT_SCHEMA_POLICY_PRE_V1: Final = StrictSchemaPolicy(
    policy_id="learned_call.strict_schema",
    policy_version="PRE-1",
    status=SchemaPolicyStatus.PRE_VERSION,
    reject_unknown_object_fields=True,
    schema_owns_shape_and_syntax=True,
    host_owns_cross_field_and_state_semantics=True,
    fixed_output_top_level_shape=True,
    optional_fields_require_explicit_absence_semantics=True,
    model_selected_contract_structure_forbidden=True,
    silent_truncation_or_correction_forbidden=True,
    impossible_downstream_branch_rejected=True,
)

STRICT_SCHEMA_POLICY_REGISTRY_PRE_V1: Final[Mapping[str, StrictSchemaPolicy]] = MappingProxyType(
    {STRICT_SCHEMA_POLICY_PRE_V1.policy_id: STRICT_SCHEMA_POLICY_PRE_V1}
)


class SchemaPolicyError(ValueError):
    """A compiled schema violates a shared learned-call schema policy."""


def get_schema_policy(policy_id: str) -> StrictSchemaPolicy:
    """Resolve one exact PRE-1 schema policy or fail closed."""

    try:
        return STRICT_SCHEMA_POLICY_REGISTRY_PRE_V1[policy_id]
    except KeyError as exc:
        raise KeyError(f"unknown schema policy: {policy_id}") from exc


def require_fixed_top_level_output_shape(schema: StrictJsonSchema) -> StrictJsonSchema:
    """Require one deterministic top-level output object shape.

    Branches may change field *values*, but not which top-level fields exist.
    Optional top-level fields therefore require a future explicit policy exception
    rather than silently becoming part of the default learned-call contract.
    """

    value = schema.schema_value()
    if value.get("type") != "object":
        raise SchemaPolicyError("learned output schema must declare type=object")
    if value.get("additionalProperties") is not False:
        raise SchemaPolicyError("learned output schema must reject unknown top-level fields")

    properties = value.get("properties")
    required = value.get("required")
    if type(properties) is not dict:
        raise SchemaPolicyError("learned output schema must declare top-level properties")
    if type(required) is not list or any(type(item) is not str for item in required):
        raise SchemaPolicyError("learned output schema must declare required top-level fields")

    property_names = set(properties)
    required_names = {item for item in required if type(item) is str}
    if property_names != required_names:
        optional = sorted(property_names - required_names)
        undeclared = sorted(required_names - property_names)
        details: list[str] = []
        if optional:
            details.append(f"optional={optional}")
        if undeclared:
            details.append(f"required_without_property={undeclared}")
        detail_text = ", ".join(details) or "top-level shape mismatch"
        raise SchemaPolicyError(
            "learned output schema must use a fixed top-level field shape; " + detail_text
        )

    return schema
