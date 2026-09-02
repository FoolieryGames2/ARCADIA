from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from arcadia.contracts.aae.registry import AAE_REGISTRY_PRE_V1
from arcadia.contracts.policies.legal_references import (
    LEGAL_REFERENCE_POLICY_REGISTRY_PRE_V1,
    LegalReferencePolicyError,
    LegalReferencePolicyStatus,
    SuppliedAuthoritativeReference,
    get_legal_reference_policy,
    require_exact_authoritative_reference_copy,
    require_valid_local_proposal_key,
    require_valid_supplied_reference_manifest,
)


def _ref(namespace: str, value: str) -> SuppliedAuthoritativeReference:
    return SuppliedAuthoritativeReference(namespace=namespace, value=value)


def test_all_twenty_modes_derive_legal_reference_policy_from_contract_registry() -> None:
    assert set(LEGAL_REFERENCE_POLICY_REGISTRY_PRE_V1) == set(AAE_REGISTRY_PRE_V1)
    for mode, contract in AAE_REGISTRY_PRE_V1.items():
        policy = get_legal_reference_policy(mode)
        assert policy.status is LegalReferencePolicyStatus.PRE_VERSION
        assert policy.frozen is False
        assert policy.legal_authoritative_namespaces == contract.legal_authoritative_ref_namespaces
        assert policy.legal_local_key_prefixes == contract.local_key_policy.allowed_prefixes
        assert policy.exact_copy_required is True
        assert policy.authoritative_id_allocation_host_only is True
        assert policy.local_keys_are_non_authoritative is True
        assert policy.host_canonicalization_required is True
        assert policy.identifier_text_has_no_semantic_meaning is True


def test_spell_has_no_authoritative_refs_but_can_use_edit_local_keys() -> None:
    policy = get_legal_reference_policy("SPELL_NORMALIZATION")
    assert policy.legal_authoritative_namespaces == ()
    assert require_valid_local_proposal_key("SPELL_NORMALIZATION", "EDIT_1") == "EDIT_1"
    with pytest.raises(LegalReferencePolicyError, match="may not receive authoritative namespace"):
        require_valid_supplied_reference_manifest("SPELL_NORMALIZATION", [_ref("Rxxx", "R001")])


def test_exact_copy_is_case_sensitive_and_cannot_be_invented() -> None:
    supplied = [_ref("Rxxx", "R001"), _ref("Cxxx", "C007")]
    assert (
        require_exact_authoritative_reference_copy(
            "REQUIREMENT_ASSESSMENT",
            namespace="Rxxx",
            value="R001",
            supplied_refs=supplied,
        )
        == "R001"
    )
    with pytest.raises(LegalReferencePolicyError, match="not supplied exactly"):
        require_exact_authoritative_reference_copy(
            "REQUIREMENT_ASSESSMENT",
            namespace="Rxxx",
            value="r001",
            supplied_refs=supplied,
        )
    with pytest.raises(LegalReferencePolicyError, match="not supplied exactly"):
        require_exact_authoritative_reference_copy(
            "REQUIREMENT_ASSESSMENT",
            namespace="Rxxx",
            value="R002",
            supplied_refs=supplied,
        )


def test_mode_cannot_smuggle_reference_from_illegal_namespace() -> None:
    with pytest.raises(LegalReferencePolicyError, match="may not output authoritative namespace Wxxx"):
        require_exact_authoritative_reference_copy(
            "INTENT_COMMENT",
            namespace="Wxxx",
            value="W001",
            supplied_refs=[_ref("Wxxx", "W001")],
        )


def test_supplied_reference_manifest_rejects_unknown_and_duplicate_entries() -> None:
    with pytest.raises(LegalReferencePolicyError, match="may not receive authoritative namespace"):
        require_valid_supplied_reference_manifest(
            "INTENT_COMMENT", [_ref("Wxxx", "W001")]
        )
    with pytest.raises(LegalReferencePolicyError, match="duplicate supplied authoritative reference"):
        require_valid_supplied_reference_manifest(
            "INTENT_COMMENT", [_ref("Rxxx", "R001"), _ref("Rxxx", "R001")]
        )


def test_local_key_must_use_mode_prefix_and_never_be_authoritative_namespace() -> None:
    assert require_valid_local_proposal_key("INTENT_ORGANIZER", "REQ_1") == "REQ_1"
    assert require_valid_local_proposal_key("INTENT_ORGANIZER", "MEM_CAND_12") == "MEM_CAND_12"
    with pytest.raises(LegalReferencePolicyError, match="does not use a legal prefix"):
        require_valid_local_proposal_key("INTENT_ORGANIZER", "R001")
    with pytest.raises(LegalReferencePolicyError, match="does not use a legal prefix"):
        require_valid_local_proposal_key("INTENT_ORGANIZER", "WORK_1")


def test_local_key_grammar_is_ascii_safe_and_collision_rejected() -> None:
    with pytest.raises(LegalReferencePolicyError, match="ASCII uppercase"):
        require_valid_local_proposal_key("INTENT_ORGANIZER", "REQ_é")
    with pytest.raises(LegalReferencePolicyError, match="ASCII uppercase"):
        require_valid_local_proposal_key("INTENT_ORGANIZER", "REQ_one")
    with pytest.raises(LegalReferencePolicyError, match="collide"):
        require_valid_local_proposal_key(
            "INTENT_ORGANIZER",
            "REQ_1",
            supplied_refs=[_ref("SOURCE_SPAN", "REQ_1")],
        )


def test_modes_without_local_proposals_fail_closed() -> None:
    with pytest.raises(LegalReferencePolicyError, match="does not permit model-created local"):
        require_valid_local_proposal_key("INTENT_COMMENT", "REQ_1")


def test_reference_policy_registry_is_immutable_and_unknown_mode_fails_closed() -> None:
    policy = get_legal_reference_policy("SCOPE_PROPOSAL")
    with pytest.raises(FrozenInstanceError):
        policy.policy_version = "evil"  # type: ignore[misc]
    with pytest.raises(TypeError):
        LEGAL_REFERENCE_POLICY_REGISTRY_PRE_V1["EVIL"] = policy  # type: ignore[index]
    with pytest.raises(KeyError, match="unknown legal-reference specialist mode"):
        get_legal_reference_policy("NOT_A_MODE")
