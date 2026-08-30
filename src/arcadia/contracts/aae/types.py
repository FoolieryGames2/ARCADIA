"""Immutable data types for the A.R.C.A.D.I.A. AAE contract registry."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from types import MappingProxyType


class RegistryStatus(StrEnum):
    """Lifecycle state for a registry definition."""

    PRE_VERSION = "PRE_VERSION"
    FROZEN = "FROZEN"


class AuthorityClass(StrEnum):
    """Descriptive learned authority labels; none grants host authority."""

    SEMANTIC_PROPOSAL = "SEMANTIC_PROPOSAL"
    SEMANTIC_ASSESSMENT = "SEMANTIC_ASSESSMENT"
    SEMANTIC_COMPOSITION = "SEMANTIC_COMPOSITION"
    PRESENTATION_ONLY = "PRESENTATION_ONLY"


@dataclass(frozen=True, slots=True)
class SchemaRef:
    """Reference to a strict schema owned outside the registry record."""

    schema_id: str
    schema_version: str
    frozen: bool = False


@dataclass(frozen=True, slots=True)
class FieldCaps:
    """Model-visible caps. None means deliberately unresolved in this pre-version."""

    max_items_per_array: int | None = None
    max_string_chars: int | None = None
    max_source_excerpt_chars: int | None = None
    max_total_input_tokens: int | None = None
    reserved_output_tokens: int | None = None
    projection_policy_id: str = "deterministic_projection.pre_v1"

    @property
    def complete(self) -> bool:
        return all(
            value is not None
            for value in (
                self.max_items_per_array,
                self.max_string_chars,
                self.max_source_excerpt_chars,
                self.max_total_input_tokens,
                self.reserved_output_tokens,
            )
        )


@dataclass(frozen=True, slots=True)
class LocalKeyPolicy:
    """Rules for model-proposed identifiers that are never authoritative IDs."""

    allowed_prefixes: tuple[str, ...] = ()
    authoritative_id_allocation_forbidden: bool = True
    host_canonicalization_required: bool = True


@dataclass(frozen=True, slots=True)
class RepairShape:
    """Bounded repair framing for one contract."""

    allowed: bool
    same_authoritative_packet: bool = True
    exact_validation_error_required: bool = True
    fresh_context_required: bool = True
    fresh_sampler_required: bool = True
    expanded_authority_forbidden: bool = True
    max_repairs: int | None = None


@dataclass(frozen=True, slots=True)
class SpecialistAwareness:
    """Structured Specialist Awareness stored once for runtime and training."""

    specialist: str
    recipe: str
    authority: AuthorityClass
    purpose: str
    input_origin: str
    responsibilities: tuple[str, ...]
    forbidden_responsibilities: tuple[str, ...]
    next_consumers: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class AAEContractRecord:
    """One independently versioned logical specialist-mode contract."""

    contract_id: str
    contract_version: str
    registry_status: RegistryStatus
    dispatch_enabled: bool
    global_awareness_version: str
    specialist_mode_id: str
    physical_adapter_id: str
    recipe_id: str
    awareness: SpecialistAwareness
    legal_input_artifact_classes: tuple[str, ...]
    legal_authoritative_ref_namespaces: tuple[str, ...]
    local_key_policy: LocalKeyPolicy
    input_schema: SchemaRef
    output_schema: SchemaRef
    response_contract_summary: str
    semantic_enums: Mapping[str, tuple[str, ...]]
    empty_output_meaning: str
    uncertainty_behavior: str
    forbidden_output_fields_or_actions: tuple[str, ...]
    host_validation_rules: tuple[str, ...]
    repair: RepairShape
    next_legal_consumers: tuple[str, ...]
    inference_profile_id: str
    inference_profile_frozen: bool
    minimum_trust_level: str | None
    field_caps: FieldCaps
    review_notes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "semantic_enums", MappingProxyType(dict(self.semantic_enums)))

    @property
    def runtime_ready(self) -> bool:
        """Return true only when this record is frozen enough to permit dispatch."""

        return (
            self.registry_status is RegistryStatus.FROZEN
            and self.dispatch_enabled
            and self.input_schema.frozen
            and self.output_schema.frozen
            and self.inference_profile_frozen
            and self.minimum_trust_level is not None
            and self.field_caps.complete
        )
