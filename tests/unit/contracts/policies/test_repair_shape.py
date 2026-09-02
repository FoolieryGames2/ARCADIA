from __future__ import annotations

from pathlib import Path

import pytest

from arcadia.contracts.aae.registry import AAE_REGISTRY_PRE_V1, get_contract
from arcadia.contracts.policies.repair_shape import (
    REPAIR_SHAPE_POLICY_REGISTRY_PRE_V1,
    RepairModelPacket,
    RepairShapePolicyError,
    RepairStop,
    RepairStopCode,
    authorize_repair_or_stop,
    begin_repair_session,
    get_repair_shape_policy,
    project_repair_attempt_for_model,
    resolve_repair_policy,
)
from arcadia.core.hashing import sha256_text
from arcadia.core.ids import CanonicalId
from arcadia.core.repair_policy import RepairBasis, RepairSession
from arcadia.settings import (
    AAESettingsHandler,
    BudgetClass,
    ContractTuningProfile,
    SettingsStatus,
    TuningLimits,
    load_aae_settings,
)

ROOT = Path(__file__).resolve().parents[4]
PRE1_SETTINGS = ROOT / "configs" / "aae_tuning.pre1.toml"
MODE = "SCOPE_PROPOSAL"


def _basis(*, packet: dict[str, object] | None = None, mode: str = MODE) -> RepairBasis:
    contract = get_contract(mode)
    return RepairBasis.create(
        call_id=CanonicalId.new(),
        specialist_mode=mode,
        inference_profile_id=contract.inference_profile_id,
        inference_profile_hash=sha256_text(f"profile:{contract.inference_profile_id}"),
        authoritative_packet={"raw_user_prompt": "same exact packet"} if packet is None else packet,
    )


def _settings(*, max_repairs: int | None) -> AAESettingsHandler:
    contract = get_contract(MODE)
    return AAESettingsHandler(
        settings_id="TEST-REPAIR-SETTINGS",
        status=SettingsStatus.PRE_VERSION,
        global_defaults=TuningLimits(),
        class_defaults={budget: TuningLimits() for budget in BudgetClass},
        profiles={
            contract.settings_profile_id: ContractTuningProfile(
                profile_id=contract.settings_profile_id,
                specialist_mode_id=MODE,
                budget_class=BudgetClass.SMALL,
                overrides=TuningLimits(max_repair_attempts=max_repairs),
            )
        },
    )


def _error() -> dict[str, object]:
    return {
        "code": "MUTUALLY_EXCLUSIVE_RETRIEVAL_MODES",
        "issues": [{"path": "/target_terms", "rule": "must_be_empty"}],
    }


def test_registry_owns_semantic_repair_shape_for_all_20_modes() -> None:
    assert set(REPAIR_SHAPE_POLICY_REGISTRY_PRE_V1) == set(AAE_REGISTRY_PRE_V1)
    assert len(REPAIR_SHAPE_POLICY_REGISTRY_PRE_V1) == 20
    for mode, policy in REPAIR_SHAPE_POLICY_REGISTRY_PRE_V1.items():
        assert policy.specialist_mode_id == mode
        assert policy.settings_profile_id == get_contract(mode).settings_profile_id
        assert policy.shape.same_authoritative_packet
        assert policy.shape.same_specialist_mode
        assert policy.shape.same_inference_profile
        assert policy.shape.exact_validation_error_required
        assert policy.shape.fresh_context_required
        assert policy.shape.fresh_sampler_required
        assert policy.shape.new_attempt_uuid_required
        assert policy.shape.expanded_authority_forbidden
        assert policy.shape.exhausted_repair_routes_typed_failure


def test_numeric_repair_cap_is_not_stored_in_contract_shape() -> None:
    shape = get_repair_shape_policy(MODE).shape
    assert not hasattr(shape, "max_repairs")
    assert get_contract(MODE).settings_profile_id == "settings.scope_proposal.pre1"


def test_pre1_file_leaves_repair_count_unresolved_not_unlimited() -> None:
    settings = load_aae_settings(PRE1_SETTINGS)
    resolution = resolve_repair_policy(MODE, settings=settings)

    assert resolution.allowed
    assert resolution.max_repair_attempts is None
    assert not resolution.resolved

    stop = begin_repair_session(MODE, settings=settings, basis=_basis())
    assert isinstance(stop, RepairStop)
    assert stop.code is RepairStopCode.REPAIR_LIMIT_UNRESOLVED
    assert stop.max_repair_attempts is None


def test_resolved_settings_create_phase_a_aggregate_repair_session() -> None:
    session = begin_repair_session(MODE, settings=_settings(max_repairs=1), basis=_basis())

    assert isinstance(session, RepairSession)
    assert session.policy.max_repairs_per_call == 1
    assert session.repairs_remaining == 1


def test_one_repair_then_exhaustion_returns_typed_stop_not_another_loop() -> None:
    session = begin_repair_session(MODE, settings=_settings(max_repairs=1), basis=_basis())
    assert isinstance(session, RepairSession)

    authorized = authorize_repair_or_stop(
        session,
        previous_output={
            "mode": MODE,
            "status": "REQUEST_RECENT",
            "recent_exchange_count": 2,
            "target_terms": ["adapter"],
            "reason_codes": ["REFERENCE_NEEDS_HISTORY"],
        },
        validation_error=_error(),
    )
    assert isinstance(authorized, tuple)
    advanced, attempt = authorized
    assert advanced.repairs_used == 1
    assert attempt.requires_fresh_context
    assert attempt.requires_fresh_sampler

    stop = authorize_repair_or_stop(
        advanced,
        previous_output={"still": "wrong"},
        validation_error={"code": "SECOND_FAILURE"},
    )
    assert isinstance(stop, RepairStop)
    assert stop.code is RepairStopCode.REPAIR_BUDGET_EXHAUSTED
    assert stop.repairs_used == 1
    assert stop.max_repair_attempts == 1


def test_zero_repair_setting_is_valid_and_immediately_exhausted() -> None:
    session = begin_repair_session(MODE, settings=_settings(max_repairs=0), basis=_basis())
    assert isinstance(session, RepairSession)
    assert session.exhausted

    stop = authorize_repair_or_stop(
        session,
        previous_output={},
        validation_error={"code": "SCHEMA_REJECTION"},
    )
    assert isinstance(stop, RepairStop)
    assert stop.code is RepairStopCode.REPAIR_BUDGET_EXHAUSTED
    assert stop.max_repair_attempts == 0


def test_repair_projection_contains_only_same_basis_plus_exact_error_and_attempt_identity() -> None:
    packet = {"raw_user_prompt": "same source", "host_policy_limits": {"lookback": 4}}
    basis = _basis(packet=packet)
    session = begin_repair_session(MODE, settings=_settings(max_repairs=1), basis=basis)
    assert isinstance(session, RepairSession)
    error = _error()
    authorized = authorize_repair_or_stop(
        session,
        previous_output={"invalid": "output that must remain audit-only"},
        validation_error=error,
    )
    assert isinstance(authorized, tuple)
    _, attempt = authorized

    # Mutating caller-owned values after authorization cannot alter the frozen repair.
    packet["raw_user_prompt"] = "expanded authority"
    error["code"] = "CHANGED_AFTER_AUTHORIZATION"

    projected = project_repair_attempt_for_model(MODE, basis=basis, attempt=attempt)
    assert isinstance(projected, RepairModelPacket)
    value = projected.to_value()
    assert value["authoritative_source_packet"] == {
        "host_policy_limits": {"lookback": 4},
        "raw_user_prompt": "same source",
    }
    assert value["validation_error"]["code"] == "MUTUALLY_EXCLUSIVE_RETRIEVAL_MODES"
    assert value["attempt_uuid"] == str(attempt.attempt_id)
    assert value["specialist_mode"] == MODE
    assert value["inference_profile_id"] == get_contract(MODE).inference_profile_id
    assert "previous_output" not in value
    assert "new_facts" not in value
    assert "expanded_authority" not in repr(value)


def test_repair_basis_cannot_change_mode_or_profile() -> None:
    wrong_mode = _basis(mode="SCOPE_VALIDATION")
    with pytest.raises(RepairShapePolicyError, match="changed specialist mode"):
        begin_repair_session(MODE, settings=_settings(max_repairs=1), basis=wrong_mode)

    contract = get_contract(MODE)
    wrong_profile = RepairBasis.create(
        call_id=CanonicalId.new(),
        specialist_mode=MODE,
        inference_profile_id="ip.some_other_mode.pre1",
        inference_profile_hash=sha256_text("other"),
        authoritative_packet={},
    )
    assert wrong_profile.inference_profile_id != contract.inference_profile_id
    with pytest.raises(RepairShapePolicyError, match="changed inference profile"):
        begin_repair_session(MODE, settings=_settings(max_repairs=1), basis=wrong_profile)


def test_repair_projection_rejects_attempt_from_another_call() -> None:
    first_basis = _basis()
    first = begin_repair_session(MODE, settings=_settings(max_repairs=1), basis=first_basis)
    assert isinstance(first, RepairSession)
    authorized = authorize_repair_or_stop(
        first,
        previous_output={},
        validation_error={"code": "BAD"},
    )
    assert isinstance(authorized, tuple)
    _, attempt = authorized

    with pytest.raises(RepairShapePolicyError, match="different learned call"):
        project_repair_attempt_for_model(MODE, basis=_basis(), attempt=attempt)


def test_unknown_mode_fails_closed() -> None:
    with pytest.raises(RepairShapePolicyError, match="unknown specialist mode"):
        get_repair_shape_policy("NOT_A_MODE")
