from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from arcadia.contracts.aae.global_awareness import GLOBAL_AWARENESS_PRE_V1
from arcadia.contracts.aae.registry import (
    AAE_REGISTRY_PRE_V1,
    PHYSICAL_ADAPTER_IDS,
    contracts_for_adapter,
    get_contract,
)
from arcadia.contracts.aae.types import RegistryStatus


def test_pre_registry_has_frozen_roster_shape_without_claiming_runtime_authority() -> None:
    assert len(AAE_REGISTRY_PRE_V1) == 20
    assert {record.physical_adapter_id for record in AAE_REGISTRY_PRE_V1.values()} == set(
        PHYSICAL_ADAPTER_IDS
    )
    assert len(PHYSICAL_ADAPTER_IDS) == 15

    for record in AAE_REGISTRY_PRE_V1.values():
        assert record.registry_status is RegistryStatus.PRE_VERSION
        assert record.dispatch_enabled is False
        assert record.runtime_ready is False
        assert record.minimum_trust_level is None
        assert record.input_schema.frozen is False
        assert record.output_schema.frozen is False
        assert record.inference_profile_frozen is False
        assert record.settings_profile_id == f"settings.{record.specialist_mode_id.lower()}.pre1"
        assert record.context_projection_policy_id == (
            f"projection.{record.specialist_mode_id.lower()}.pre1"
        )
    assert len(
        {record.context_projection_policy_id for record in AAE_REGISTRY_PRE_V1.values()}
    ) == len(AAE_REGISTRY_PRE_V1)


def test_contract_and_logical_mode_ids_are_unique() -> None:
    records = tuple(AAE_REGISTRY_PRE_V1.values())
    assert len({record.contract_id for record in records}) == len(records)
    assert len({record.specialist_mode_id for record in records}) == len(records)


def test_global_awareness_is_one_shared_pre_version_source() -> None:
    assert GLOBAL_AWARENESS_PRE_V1.status is RegistryStatus.PRE_VERSION
    assert GLOBAL_AWARENESS_PRE_V1.version == "GA-PRE-1"
    assert "bounded semantic specialist" in GLOBAL_AWARENESS_PRE_V1.text
    assert "host owns authoritative IDs" in GLOBAL_AWARENESS_PRE_V1.text
    assert all(
        record.global_awareness_version == GLOBAL_AWARENESS_PRE_V1.version
        for record in AAE_REGISTRY_PRE_V1.values()
    )


def test_conversational_howard_has_five_separate_mode_contracts() -> None:
    howard = contracts_for_adapter("CONVERSATIONAL_HOWARD")
    assert {record.specialist_mode_id for record in howard} == {
        "INTENT_COMMENT",
        "CONTEXT_LANE_COMMENT",
        "CONTEXT_FINAL_SYNTHESIS",
        "RESULT_REQUIREMENT_COMMENT",
        "RESULT_FINAL_COMPOSE",
    }
    assert len({record.contract_id for record in howard}) == 5
    assert len({record.inference_profile_id for record in howard}) == 5


def test_conversation_resolver_has_two_independent_modes() -> None:
    resolver = contracts_for_adapter("CONVERSATION_RESOLVER")
    assert {record.specialist_mode_id for record in resolver} == {
        "SCOPE_PROPOSAL",
        "SCOPE_VALIDATION",
    }


def test_tool_execution_has_no_learned_registry_entry() -> None:
    assert not any(record.recipe_id == "R4" for record in AAE_REGISTRY_PRE_V1.values())


def test_model_generated_authoritative_ids_are_forbidden_for_every_contract() -> None:
    assert all(
        record.local_key_policy.authoritative_id_allocation_forbidden
        and record.local_key_policy.host_canonicalization_required
        for record in AAE_REGISTRY_PRE_V1.values()
    )


def test_key_semantic_vocabularies_match_current_recipe_contracts() -> None:
    assert get_contract("SCOPE_PROPOSAL").semantic_enums["proposal_outcome"] == (
        "SUFFICIENT_WITHOUT_HISTORY",
        "REQUEST_RECENT",
        "REQUEST_TARGETED",
    )
    assert get_contract("REQUIREMENT_ASSESSMENT").semantic_enums["disposition"] == (
        "READY",
        "WORK_REQUIRED",
        "BLOCKED",
        "PERSISTENCE_REQUIRED",
    )
    assert get_contract("EVIDENCE_RECONCILIATION").semantic_enums["semantic_state"] == (
        "ESTABLISHED",
        "PARTIAL",
        "NOT_ESTABLISHED",
        "CONFLICT",
    )
    assert get_contract("COMPLETION_ASSESSMENT").semantic_enums["terminal_status"] == (
        "SATISFIED",
        "PARTIALLY_SATISFIED",
        "BLOCKED",
        "FAILED",
    )


def test_registry_records_and_semantic_enums_are_immutable() -> None:
    record = get_contract("REQUIREMENT_ASSESSMENT")
    with pytest.raises(FrozenInstanceError):
        record.contract_version = "changed"  # type: ignore[misc]
    with pytest.raises(TypeError):
        record.semantic_enums["disposition"] = ("BROKEN",)  # type: ignore[index]


def test_unknown_mode_fails_closed() -> None:
    with pytest.raises(KeyError, match="unknown AAE specialist mode"):
        get_contract("NOT_A_REAL_MODE")


def test_a1_registry_does_not_embed_adapter_runtime_lifecycle_state() -> None:
    forbidden_names = {
        "adapter_path",
        "adapter_sha256",
        "live_adapter_handle",
        "residency_state",
        "lease_count",
        "observed_vram_delta",
        "observed_host_memory_delta",
    }
    record_fields = set(next(iter(AAE_REGISTRY_PRE_V1.values())).__dataclass_fields__)
    assert forbidden_names.isdisjoint(record_fields)
