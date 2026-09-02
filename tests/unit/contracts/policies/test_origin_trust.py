from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from arcadia.contracts.aae.registry import AAE_REGISTRY_PRE_V1, get_contract
from arcadia.contracts.policies.origin_trust import (
    CANONICAL_V0_1_DATA_ORIGINS,
    ORIGIN_AUTHORITY_COMPATIBILITY_PRE_V1,
    ORIGIN_TRUST_POLICY_REGISTRY_PRE_V1,
    PRE1_ORIGIN_EXTENSIONS,
    DataAuthorityClass,
    DataOrigin,
    ModelVisibleDataTrust,
    OriginTrustPolicyError,
    OriginTrustPolicyStatus,
    ReferenceContentState,
    SemanticUse,
    get_origin_trust_policy,
    require_valid_origin_trust_item,
    require_valid_origin_trust_manifest,
)


def _item(
    *,
    origin: DataOrigin = DataOrigin.USER_PROMPT,
    authority: DataAuthorityClass = DataAuthorityClass.CONTENT_ONLY,
    content_state: ReferenceContentState = ReferenceContentState.CONTENT_SUPPLIED,
    semantic_use: SemanticUse = SemanticUse.SEMANTIC_INTERPRETATION,
    ref: str | None = None,
    key: str = "item-1",
) -> ModelVisibleDataTrust:
    return ModelVisibleDataTrust(
        item_key=key,
        origin=origin,
        authority_class=authority,
        reference_content_state=content_state,
        semantic_use=semantic_use,
        authoritative_ref=ref,
    )


def test_canonical_origin_and_authority_vocabularies_match_v0_1_authority() -> None:
    assert tuple(item.value for item in CANONICAL_V0_1_DATA_ORIGINS) == (
        "USER_PROMPT",
        "TRANSCRIPT",
        "SEMANTIC_MEMORY",
        "TOOL_RECEIPT",
        "WEB_RESULT",
        "HOST_DERIVED_SIGNAL",
    )
    assert tuple(item.value for item in DataAuthorityClass) == (
        "CONTENT_ONLY",
        "EXTERNAL_UNTRUSTED_EVIDENCE",
        "HOST_VERIFIED_EXECUTION",
        "HOST_VERIFIED_STATE",
    )
    assert PRE1_ORIGIN_EXTENSIONS == (DataOrigin.VALIDATED_RECIPE_ARTIFACT,)


def test_all_twenty_logical_modes_resolve_one_pre_version_origin_policy() -> None:
    assert set(ORIGIN_TRUST_POLICY_REGISTRY_PRE_V1) == set(AAE_REGISTRY_PRE_V1)
    assert len(ORIGIN_TRUST_POLICY_REGISTRY_PRE_V1) == 20
    for mode, contract in AAE_REGISTRY_PRE_V1.items():
        policy = get_origin_trust_policy(mode)
        assert policy.status is OriginTrustPolicyStatus.PRE_VERSION
        assert policy.frozen is False
        assert policy.policy_id == contract.origin_trust_policy_id
        assert policy.specialist_mode_id == mode
        assert policy.data_text_instruction_authority is DataAuthorityClass.CONTENT_ONLY
        assert policy.labels_are_framing_not_injection_proof is True
        assert policy.source_quality_ranking_out_of_scope is True
        assert policy.adapter_runtime_trust_out_of_scope is True


def test_recipe_zero_origin_admission_preserves_proposal_vs_validation_boundary() -> None:
    proposal = get_origin_trust_policy("SCOPE_PROPOSAL")
    validation = get_origin_trust_policy("SCOPE_VALIDATION")
    assert DataOrigin.TRANSCRIPT not in proposal.allowed_origins
    assert DataOrigin.TRANSCRIPT in validation.allowed_origins
    assert DataOrigin.SEMANTIC_MEMORY not in proposal.allowed_origins
    assert DataOrigin.SEMANTIC_MEMORY not in validation.allowed_origins


def test_spell_consumes_only_direct_user_prompt_origin() -> None:
    assert get_origin_trust_policy("SPELL_NORMALIZATION").allowed_origins == (
        DataOrigin.USER_PROMPT,
    )


@pytest.mark.parametrize(
    ("origin", "authority"),
    [
        (DataOrigin.USER_PROMPT, DataAuthorityClass.HOST_VERIFIED_STATE),
        (DataOrigin.TRANSCRIPT, DataAuthorityClass.HOST_VERIFIED_EXECUTION),
        (DataOrigin.WEB_RESULT, DataAuthorityClass.HOST_VERIFIED_EXECUTION),
        (DataOrigin.TOOL_RECEIPT, DataAuthorityClass.EXTERNAL_UNTRUSTED_EVIDENCE),
        (DataOrigin.VALIDATED_RECIPE_ARTIFACT, DataAuthorityClass.HOST_VERIFIED_STATE),
    ],
)
def test_illegal_origin_authority_relabeling_fails_closed(
    origin: DataOrigin,
    authority: DataAuthorityClass,
) -> None:
    assert authority not in ORIGIN_AUTHORITY_COMPATIBILITY_PRE_V1[origin]
    with pytest.raises(OriginTrustPolicyError, match="may not claim authority_class"):
        require_valid_origin_trust_item(
            "CONTEXT_EVIDENCE_ASSESSMENT",
            _item(origin=origin, authority=authority),
        )


def test_web_and_receipt_authority_classes_are_narrow() -> None:
    require_valid_origin_trust_item(
        "EVIDENCE_RECONCILIATION",
        _item(
            origin=DataOrigin.WEB_RESULT,
            authority=DataAuthorityClass.EXTERNAL_UNTRUSTED_EVIDENCE,
        ),
    )
    require_valid_origin_trust_item(
        "EVIDENCE_RECONCILIATION",
        _item(
            origin=DataOrigin.TOOL_RECEIPT,
            authority=DataAuthorityClass.HOST_VERIFIED_EXECUTION,
        ),
    )


def test_semantic_memory_can_be_content_only_or_host_verified_state_without_source_ranking() -> None:
    for authority in (
        DataAuthorityClass.CONTENT_ONLY,
        DataAuthorityClass.HOST_VERIFIED_STATE,
    ):
        require_valid_origin_trust_item(
            "PERSISTENCE_ASSESSMENT",
            _item(origin=DataOrigin.SEMANTIC_MEMORY, authority=authority),
        )


def test_bare_authoritative_ref_is_legal_for_identity_but_not_semantic_interpretation() -> None:
    identity_only = _item(
        origin=DataOrigin.VALIDATED_RECIPE_ARTIFACT,
        content_state=ReferenceContentState.REFERENCE_ONLY,
        semantic_use=SemanticUse.IDENTITY_ONLY,
        ref="R001",
    )
    assert require_valid_origin_trust_item("REQUIREMENT_ASSESSMENT", identity_only) is identity_only

    semantic = _item(
        origin=DataOrigin.VALIDATED_RECIPE_ARTIFACT,
        content_state=ReferenceContentState.REFERENCE_ONLY,
        semantic_use=SemanticUse.SEMANTIC_INTERPRETATION,
        ref="R001",
    )
    with pytest.raises(OriginTrustPolicyError, match="cannot supply semantic meaning"):
        require_valid_origin_trust_item("REQUIREMENT_ASSESSMENT", semantic)


def test_reference_only_metadata_requires_an_actual_authoritative_ref() -> None:
    with pytest.raises(OriginTrustPolicyError, match="requires authoritative_ref"):
        require_valid_origin_trust_item(
            "REQUIREMENT_ASSESSMENT",
            _item(
                origin=DataOrigin.VALIDATED_RECIPE_ARTIFACT,
                content_state=ReferenceContentState.REFERENCE_ONLY,
                semantic_use=SemanticUse.IDENTITY_ONLY,
                ref=None,
            ),
        )


def test_mode_origin_mismatch_fails_before_learned_dispatch() -> None:
    with pytest.raises(OriginTrustPolicyError, match="SPELL_NORMALIZATION may not consume origin TRANSCRIPT"):
        require_valid_origin_trust_item(
            "SPELL_NORMALIZATION",
            _item(origin=DataOrigin.TRANSCRIPT),
        )


def test_manifest_rejects_duplicate_host_item_keys_and_returns_immutable_tuple() -> None:
    first = _item(key="raw_prompt")
    second = _item(key="raw_prompt")
    with pytest.raises(OriginTrustPolicyError, match="duplicate origin/trust item_key"):
        require_valid_origin_trust_manifest("SCOPE_PROPOSAL", [first, second])

    checked = require_valid_origin_trust_manifest("SCOPE_PROPOSAL", [first])
    assert checked == (first,)
    assert type(checked) is tuple


def test_manifest_and_policy_records_are_immutable_and_unknown_modes_fail_closed() -> None:
    policy = get_origin_trust_policy("SCOPE_PROPOSAL")
    with pytest.raises(FrozenInstanceError):
        policy.policy_version = "evil"  # type: ignore[misc]
    with pytest.raises(TypeError):
        ORIGIN_TRUST_POLICY_REGISTRY_PRE_V1["EVIL"] = policy  # type: ignore[index]
    with pytest.raises(KeyError, match="unknown origin/trust specialist mode"):
        get_origin_trust_policy("NOT_A_MODE")


def test_registry_contract_origin_policy_binding_is_not_runtime_trust_level() -> None:
    contract = get_contract("SCOPE_VALIDATION")
    assert contract.origin_trust_policy_id == "origin_trust.scope_validation.pre1"
    assert contract.minimum_trust_level is None
    assert contract.runtime_ready is False
