from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
from datetime import UTC, datetime, timedelta

import pytest

from arcadia.core.config import AuthorityTier, RuntimeBackend, RuntimeConfig
from arcadia.core.hashing import Sha256Digest, sha256_canonical_json, sha256_text
from arcadia.core.ids import CanonicalId
from arcadia.core.trust_registry import (
    AdapterBindingKind,
    AuthorityUse,
    BlockingEvidence,
    QualificationEvidence,
    QualificationTarget,
    RuntimeQualificationIdentity,
    TrustConflictError,
    TrustDecisionCode,
    TrustEvent,
    TrustEventKind,
    TrustFieldError,
    TrustIntegrityError,
    TrustPolicy,
    TrustRecord,
    TrustRegistry,
    TrustStanding,
)

NOW = datetime(2026, 8, 30, 12, 0, tzinfo=UTC)


def _identity(
    *,
    binding: AdapterBindingKind = AdapterBindingKind.PHYSICAL_ADAPTER,
    profile: str = "profile.intent.v1",
    profile_hash: Sha256Digest | None = None,
    adapter_hash: Sha256Digest | None = None,
) -> RuntimeQualificationIdentity:
    return RuntimeQualificationIdentity(
        binding_kind=binding,
        base_model_hash=sha256_text("base-model"),
        physical_adapter_id=(
            CanonicalId.new() if binding is AdapterBindingKind.PHYSICAL_ADAPTER else None
        ),
        physical_adapter_hash=(
            adapter_hash or sha256_text("adapter")
            if binding is AdapterBindingKind.PHYSICAL_ADAPTER
            else None
        ),
        llama_cpp_build_id="c9ca51c1",
        model_runtime_version="1",
        adapter_manager_version="1",
        specialist_invoker_version="1",
        aae_contract_version="1",
        specialist_mode_contract_version="1",
        input_schema_version="1",
        output_schema_version="1",
        host_validator_version="1",
        inference_profile_id=profile,
        inference_profile_hash=profile_hash or sha256_text(profile),
    )


def _target(
    *,
    mode: str = "intent.organize",
    identity: RuntimeQualificationIdentity | None = None,
    minimum: AuthorityTier = AuthorityTier.T3,
) -> QualificationTarget:
    return QualificationTarget.create(
        logical_mode_id=mode,
        minimum_runtime_tier=minimum,
        runtime_identity=identity or _identity(),
    )


def _evidence(
    target: QualificationTarget, tier: AuthorityTier, *, at: datetime = NOW
) -> QualificationEvidence:
    return QualificationEvidence.create(
        tier=tier,
        suite_manifest_hash=sha256_text(f"suite-{tier}"),
        report_hash=sha256_text(f"report-{tier}"),
        evaluation_identity_hash=target.runtime_identity.identity_hash,
        reviewer_id=CanonicalId.new(),
        qualified_at=at,
    )


def _blocking(*, at: datetime = NOW, reason: str = "REGRESSION") -> BlockingEvidence:
    return BlockingEvidence.create(
        reason_code=reason,
        report_hash=sha256_text(reason),
        reviewer_id=CanonicalId.new(),
        recorded_at=at,
    )


def _register(
    registry: TrustRegistry, target: QualificationTarget, *, at: datetime = NOW
) -> TrustRegistry:
    return registry.register(
        target=target, occurred_at=at, expected_head=registry.head_hash
    )[0]


def _promote_to(
    registry: TrustRegistry,
    target: QualificationTarget,
    tier: AuthorityTier,
    *,
    at: datetime = NOW,
) -> TrustRegistry:
    while registry.get(target.target_id).earned_tier is not tier:
        current = registry.get(target.target_id)
        next_tier = AuthorityTier(f"T{int(current.earned_tier.value[1]) + 1}")
        registry = registry.promote(
            target_id=target.target_id,
            expected_revision=current.revision,
            evidence=_evidence(target, next_tier, at=at),
            occurred_at=at,
            expected_head=registry.head_hash,
        )[0]
    return registry


def test_policy_is_derived_from_runtime_config_and_canonically_hashed() -> None:
    config = RuntimeConfig(
        authority_tier=AuthorityTier.T3,
        backend=RuntimeBackend.TEST_DOUBLE,
        base_model_path="",
        max_hot_adapters=0,
        standard_active_adapters=1,
        standard_adapter_scale=1.0,
        serialized_manager_mutation=True,
    )
    policy = TrustPolicy.from_runtime_config(config)

    assert policy.authority_ceiling is AuthorityTier.T3
    assert policy.policy_hash == sha256_text(
        '{"authority_ceiling":"T3","policy_version":1}'
    )
    with pytest.raises(TrustFieldError):
        TrustPolicy(authority_ceiling="T3")  # type: ignore[arg-type]


def test_runtime_identity_hash_covers_every_output_affecting_field() -> None:
    identity = _identity()
    changed = replace(identity, host_validator_version="2")

    assert identity.identity_hash == sha256_canonical_json(identity.to_value())
    assert changed.identity_hash != identity.identity_hash
    assert replace(identity, inference_profile_hash=sha256_text("changed")).identity_hash != (
        identity.identity_hash
    )


def test_adapter_binding_is_explicit_and_base_only_cannot_claim_adapter() -> None:
    base_only = _identity(binding=AdapterBindingKind.BASE_ONLY)
    assert base_only.to_value()["physical_adapter_hash"] is None

    with pytest.raises(TrustIntegrityError, match="BASE_ONLY"):
        replace(base_only, physical_adapter_hash=sha256_text("forbidden"))
    with pytest.raises(TrustFieldError, match="adapter UUID"):
        replace(_identity(), physical_adapter_id=None)


def test_runtime_identity_rejects_noncanonical_version_tokens() -> None:
    with pytest.raises(TrustFieldError, match="canonical token"):
        replace(_identity(), llama_cpp_build_id="fake authority block")
    with pytest.raises(TrustFieldError, match="canonical token"):
        replace(_identity(), inference_profile_id="fake authority block")


def test_target_is_immutable_and_hashes_exact_mode_binding() -> None:
    target = _target()
    assert target.target_hash == sha256_canonical_json(target.to_value())
    with pytest.raises(FrozenInstanceError):
        target.logical_mode_id = "changed"  # type: ignore[misc]


def test_registration_creates_clean_t0_revision_and_rejects_duplicate_binding() -> None:
    target = _target()
    registry = _register(TrustRegistry.create(TrustPolicy(AuthorityTier.T3)), target)
    record = registry.get(target.target_id)

    assert record == TrustRecord.initial(target)
    assert registry.events[0].event_kind is TrustEventKind.REGISTERED
    duplicate = replace(target, target_id=CanonicalId.new())
    with pytest.raises(TrustIntegrityError, match="already registered"):
        _register(registry, duplicate)


def test_shared_physical_adapter_never_shares_logical_mode_qualification() -> None:
    identity = _identity()
    first = _target(mode="intent.organize", identity=identity)
    second = _target(mode="intent.classify", identity=identity)
    registry = TrustRegistry.create(TrustPolicy(AuthorityTier.T3))
    registry = _register(registry, first)
    registry = _register(registry, second)
    registry = _promote_to(registry, first, AuthorityTier.T3)

    assert registry.get(first.target_id).earned_tier is AuthorityTier.T3
    assert registry.get(second.target_id).earned_tier is AuthorityTier.T0


def test_changed_profile_is_a_new_t0_qualification_target() -> None:
    first = _target()
    changed_identity = replace(
        first.runtime_identity,
        inference_profile_id="profile.intent.v2",
        inference_profile_hash=sha256_text("profile-v2"),
    )
    second = _target(identity=changed_identity)
    registry = _register(TrustRegistry.create(TrustPolicy(AuthorityTier.T3)), first)
    registry = _promote_to(registry, first, AuthorityTier.T3)
    registry = _register(registry, second)

    assert registry.get(second.target_id).earned_tier is AuthorityTier.T0


def test_promotions_are_sequential_and_bound_to_exact_runtime_identity() -> None:
    target = _target()
    registry = _register(TrustRegistry.create(TrustPolicy(AuthorityTier.T6)), target)
    current = registry.get(target.target_id)

    with pytest.raises(TrustIntegrityError, match="next trust tier"):
        registry.promote(
            target_id=target.target_id,
            expected_revision=current.revision,
            evidence=_evidence(target, AuthorityTier.T2),
            occurred_at=NOW,
            expected_head=registry.head_hash,
        )
    wrong = replace(
        _evidence(target, AuthorityTier.T1),
        evaluation_identity_hash=sha256_text("different runtime"),
    )
    with pytest.raises(TrustIntegrityError, match="different runtime"):
        registry.promote(
            target_id=target.target_id,
            expected_revision=current.revision,
            evidence=wrong,
            occurred_at=NOW,
            expected_head=registry.head_hash,
        )

    registry = _promote_to(registry, target, AuthorityTier.T6)
    assert tuple(item.tier for item in registry.get(target.target_id).qualification_evidence) == (
        AuthorityTier.T1,
        AuthorityTier.T2,
        AuthorityTier.T3,
        AuthorityTier.T4,
        AuthorityTier.T5,
        AuthorityTier.T6,
    )
    with pytest.raises(TrustIntegrityError, match="already has T6"):
        registry.promote(
            target_id=target.target_id,
            expected_revision=7,
            evidence=_evidence(target, AuthorityTier.T6),
            occurred_at=NOW,
            expected_head=registry.head_hash,
        )


def test_future_dated_evidence_cannot_precede_its_transition() -> None:
    target = _target()
    registry = _register(TrustRegistry.create(TrustPolicy(AuthorityTier.T3)), target)
    with pytest.raises(TrustIntegrityError, match="promotion transition"):
        registry.promote(
            target_id=target.target_id,
            expected_revision=1,
            evidence=_evidence(target, AuthorityTier.T1, at=NOW + timedelta(seconds=1)),
            occurred_at=NOW,
            expected_head=registry.head_hash,
        )


@pytest.mark.parametrize(
    ("tier", "use", "allowed"),
    [
        (AuthorityTier.T0, AuthorityUse.QUALIFICATION, True),
        (AuthorityTier.T2, AuthorityUse.PROTOTYPE, False),
        (AuthorityTier.T3, AuthorityUse.PROTOTYPE, True),
        (AuthorityTier.T4, AuthorityUse.SHADOW_RUNTIME, True),
        (AuthorityTier.T5, AuthorityUse.LIMITED_AUTHORITY, True),
        (AuthorityTier.T6, AuthorityUse.PRODUCTION, True),
    ],
)
def test_authority_uses_require_their_frozen_tiers(
    tier: AuthorityTier, use: AuthorityUse, allowed: bool
) -> None:
    target = _target()
    registry = _register(TrustRegistry.create(TrustPolicy(AuthorityTier.T6)), target)
    registry = _promote_to(registry, target, tier)
    decision = registry.authorize(
        logical_mode_id=target.logical_mode_id,
        runtime_identity_hash=target.runtime_identity.identity_hash,
        requested_use=use,
    )
    assert decision.allowed is allowed
    assert decision.code is (
        TrustDecisionCode.AUTHORIZED if allowed else TrustDecisionCode.INSUFFICIENT_TRUST
    )


def test_mode_minimum_tier_and_environment_ceiling_are_independent_controls() -> None:
    target = _target(minimum=AuthorityTier.T5)
    registry = _register(TrustRegistry.create(TrustPolicy(AuthorityTier.T3)), target)
    registry = _promote_to(registry, target, AuthorityTier.T5)
    decision = registry.authorize(
        logical_mode_id=target.logical_mode_id,
        runtime_identity_hash=target.runtime_identity.identity_hash,
        requested_use=AuthorityUse.PROTOTYPE,
    )
    assert not decision.allowed
    assert decision.required_tier is AuthorityTier.T5
    assert decision.code is TrustDecisionCode.AUTHORITY_CEILING


def test_base_only_is_explicit_qualification_infrastructure_not_runtime_fallback() -> None:
    target = _target(identity=_identity(binding=AdapterBindingKind.BASE_ONLY))
    registry = _register(TrustRegistry.create(TrustPolicy(AuthorityTier.T6)), target)
    registry = _promote_to(registry, target, AuthorityTier.T6)

    qualification = registry.authorize(
        logical_mode_id=target.logical_mode_id,
        runtime_identity_hash=target.runtime_identity.identity_hash,
        requested_use=AuthorityUse.QUALIFICATION,
    )
    runtime = registry.authorize(
        logical_mode_id=target.logical_mode_id,
        runtime_identity_hash=target.runtime_identity.identity_hash,
        requested_use=AuthorityUse.PROTOTYPE,
    )
    assert qualification.allowed
    assert runtime.code is TrustDecisionCode.BASE_ONLY_QUALIFICATION_ONLY


def test_authorization_never_falls_back_to_another_identity_or_mode() -> None:
    target = _target()
    registry = _register(TrustRegistry.create(TrustPolicy(AuthorityTier.T6)), target)

    missing_mode = registry.authorize(
        logical_mode_id="unknown.mode",
        runtime_identity_hash=target.runtime_identity.identity_hash,
        requested_use=AuthorityUse.QUALIFICATION,
    )
    changed_runtime = registry.authorize(
        logical_mode_id=target.logical_mode_id,
        runtime_identity_hash=sha256_text("changed-profile"),
        requested_use=AuthorityUse.QUALIFICATION,
    )
    assert missing_mode.code is TrustDecisionCode.MODE_NOT_REGISTERED
    assert changed_runtime.code is TrustDecisionCode.TARGET_NOT_REGISTERED


def test_block_and_reset_are_explicit_audited_transitions_requiring_requalification() -> None:
    target = _target()
    registry = _register(TrustRegistry.create(TrustPolicy(AuthorityTier.T3)), target)
    registry = _promote_to(registry, target, AuthorityTier.T3)
    block = _blocking()
    registry, block_event = registry.block(
        target_id=target.target_id,
        expected_revision=4,
        evidence=block,
        occurred_at=NOW,
        expected_head=registry.head_hash,
    )
    denied = registry.authorize(
        logical_mode_id=target.logical_mode_id,
        runtime_identity_hash=target.runtime_identity.identity_hash,
        requested_use=AuthorityUse.PROTOTYPE,
    )
    qualification = registry.authorize(
        logical_mode_id=target.logical_mode_id,
        runtime_identity_hash=target.runtime_identity.identity_hash,
        requested_use=AuthorityUse.QUALIFICATION,
    )
    assert block_event.transition_evidence == block
    assert denied.code is TrustDecisionCode.TARGET_BLOCKED
    assert qualification.allowed
    with pytest.raises(TrustIntegrityError, match="blocked target"):
        registry.promote(
            target_id=target.target_id,
            expected_revision=5,
            evidence=_evidence(target, AuthorityTier.T4),
            occurred_at=NOW,
            expected_head=registry.head_hash,
        )

    registry, reset_event = registry.reset_blocked_to_t0(
        target_id=target.target_id,
        expected_revision=5,
        reviewer_id=CanonicalId.new(),
        reset_report_hash=sha256_text("reviewed reset"),
        occurred_at=NOW,
        expected_head=registry.head_hash,
    )
    record = registry.get(target.target_id)
    assert record.standing is TrustStanding.ACTIVE
    assert record.earned_tier is AuthorityTier.T0
    assert record.qualification_evidence == ()
    assert reset_event.transition_evidence is not None
    assert reset_event.transition_evidence.reason_code == "RESET_TO_T0"


def test_reset_requires_blocked_state() -> None:
    target = _target()
    registry = _register(TrustRegistry.create(TrustPolicy(AuthorityTier.T3)), target)
    with pytest.raises(TrustIntegrityError, match="only a blocked"):
        registry.reset_blocked_to_t0(
            target_id=target.target_id,
            expected_revision=1,
            reviewer_id=CanonicalId.new(),
            reset_report_hash=sha256_text("reset"),
            occurred_at=NOW,
            expected_head=registry.head_hash,
        )


def test_transition_evidence_uuid_cannot_be_reused() -> None:
    target = _target()
    registry = _register(TrustRegistry.create(TrustPolicy(AuthorityTier.T3)), target)
    evidence = _blocking()
    registry = registry.block(
        target_id=target.target_id,
        expected_revision=1,
        evidence=evidence,
        occurred_at=NOW,
        expected_head=registry.head_hash,
    )[0]
    registry = registry.reset_blocked_to_t0(
        target_id=target.target_id,
        expected_revision=2,
        reviewer_id=CanonicalId.new(),
        reset_report_hash=sha256_text("reset"),
        occurred_at=NOW,
        expected_head=registry.head_hash,
    )[0]
    with pytest.raises(TrustIntegrityError, match="authorize two transitions"):
        registry.block(
            target_id=target.target_id,
            expected_revision=3,
            evidence=evidence,
            occurred_at=NOW,
            expected_head=registry.head_hash,
        )


def test_optimistic_head_and_target_revision_reject_stale_updates() -> None:
    target = _target()
    registry = _register(TrustRegistry.create(TrustPolicy(AuthorityTier.T3)), target)
    with pytest.raises(TrustConflictError, match="target revision"):
        registry.promote(
            target_id=target.target_id,
            expected_revision=2,
            evidence=_evidence(target, AuthorityTier.T1),
            occurred_at=NOW,
            expected_head=registry.head_hash,
        )
    with pytest.raises(TrustConflictError, match="head"):
        registry.promote(
            target_id=target.target_id,
            expected_revision=1,
            evidence=_evidence(target, AuthorityTier.T1),
            occurred_at=NOW,
            expected_head=sha256_text("stale"),
        )


def test_hash_chain_and_registry_serialization_are_canonical() -> None:
    target = _target()
    registry = _register(TrustRegistry.create(TrustPolicy(AuthorityTier.T3)), target)
    registry = _promote_to(registry, target, AuthorityTier.T1)

    assert registry.events[1].previous_event_hash == registry.events[0].event_hash
    assert registry.registry_hash == sha256_canonical_json(registry.to_value())
    assert registry.to_json().encode("utf-8").decode("utf-8") == registry.to_json()


def test_replay_rejects_reordering_deletion_and_target_mutation() -> None:
    target = _target()
    registry = _register(TrustRegistry.create(TrustPolicy(AuthorityTier.T3)), target)
    registry = _promote_to(registry, target, AuthorityTier.T1)

    with pytest.raises(TrustIntegrityError):
        TrustRegistry(policy=registry.policy, events=tuple(reversed(registry.events)))
    with pytest.raises(TrustIntegrityError):
        TrustRegistry(policy=registry.policy, events=(registry.events[1],))

    changed_record = replace(
        registry.events[1].record,
        target=replace(target, logical_mode_id="intent.changed"),
    )
    changed_event = TrustEvent.create(
        sequence=2,
        event_kind=TrustEventKind.PROMOTED,
        occurred_at=NOW,
        record=changed_record,
        transition_evidence=None,
        previous_event_hash=registry.events[0].event_hash,
    )
    with pytest.raises(TrustIntegrityError, match="target"):
        TrustRegistry(policy=registry.policy, events=(registry.events[0], changed_event))


def test_replay_rejects_nonmonotonic_event_time() -> None:
    target = _target()
    registry = _register(
        TrustRegistry.create(TrustPolicy(AuthorityTier.T3)), target, at=NOW
    )
    earlier = TrustEvent.create(
        sequence=2,
        event_kind=TrustEventKind.PROMOTED,
        occurred_at=NOW - timedelta(seconds=1),
        record=replace(
            registry.get(target.target_id),
            revision=2,
            earned_tier=AuthorityTier.T1,
            qualification_evidence=(
                _evidence(target, AuthorityTier.T1, at=NOW - timedelta(seconds=1)),
            ),
        ),
        transition_evidence=None,
        previous_event_hash=registry.head_hash,
    )
    with pytest.raises(TrustIntegrityError, match="nondecreasing"):
        TrustRegistry(policy=registry.policy, events=(*registry.events, earlier))


def test_event_hash_detects_content_tampering() -> None:
    target = _target()
    registry = _register(TrustRegistry.create(TrustPolicy(AuthorityTier.T3)), target)
    with pytest.raises(TrustIntegrityError, match="event_hash"):
        replace(registry.events[0], event_hash=sha256_text("tampered"))
