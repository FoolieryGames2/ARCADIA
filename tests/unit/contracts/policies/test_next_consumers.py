from __future__ import annotations

import pytest

from arcadia.contracts.aae import AAE_REGISTRY_PRE_V1
from arcadia.contracts.policies.next_consumers import (
    HOST_CONSUMER_IDS_PRE_V1,
    LEARNED_CONSUMER_TARGETS_PRE_V1,
    NEXT_CONSUMER_POLICY_REGISTRY_PRE_V1,
    ConsumerKind,
    NextConsumerPolicyError,
    NextConsumerPolicyStatus,
    RouteSelector,
    get_legal_next_consumers,
    get_next_consumer_policy,
    require_legal_next_consumer,
)


def test_policy_registry_covers_all_20_logical_modes() -> None:
    assert set(NEXT_CONSUMER_POLICY_REGISTRY_PRE_V1) == set(AAE_REGISTRY_PRE_V1)
    assert len(NEXT_CONSUMER_POLICY_REGISTRY_PRE_V1) == 20


def test_policy_is_pre_version_and_host_owned() -> None:
    policy = get_next_consumer_policy("SCOPE_PROPOSAL")
    assert policy.status is NextConsumerPolicyStatus.PRE_VERSION
    assert policy.host_selects_traversal is True
    assert policy.model_selected_routing_forbidden is True


def test_every_registry_edge_is_preserved_exactly_and_in_order() -> None:
    for mode, contract in AAE_REGISTRY_PRE_V1.items():
        refs = get_legal_next_consumers(mode)
        assert tuple(ref.consumer_id for ref in refs) == contract.next_legal_consumers


def test_host_and_learned_consumer_identity_spaces_do_not_overlap() -> None:
    assert not HOST_CONSUMER_IDS_PRE_V1.intersection(LEARNED_CONSUMER_TARGETS_PRE_V1)


def test_every_learned_consumer_alias_resolves_to_real_logical_mode() -> None:
    for target_mode in LEARNED_CONSUMER_TARGETS_PRE_V1.values():
        assert target_mode in AAE_REGISTRY_PRE_V1


def test_legal_host_stage_transition_is_accepted() -> None:
    ref = require_legal_next_consumer(
        "SCOPE_PROPOSAL",
        "R0_HOST_SCOPE_VALIDATOR",
        selected_by=RouteSelector.HOST,
    )
    assert ref.kind is ConsumerKind.HOST_STAGE
    assert ref.target_specialist_mode_id is None


def test_legal_learned_transition_is_resolved_but_not_dispatched() -> None:
    ref = require_legal_next_consumer(
        "SPELL_NORMALIZATION",
        "R1_TERM_MEANING",
        selected_by=RouteSelector.HOST,
    )
    assert ref.kind is ConsumerKind.LEARNED_MODE
    assert ref.target_specialist_mode_id == "TERM_MEANING"
    # Routing legality is not runtime authority; PRE registry remains disabled.
    assert AAE_REGISTRY_PRE_V1[ref.target_specialist_mode_id].dispatch_enabled is False


def test_model_cannot_choose_even_a_legal_edge() -> None:
    with pytest.raises(NextConsumerPolicyError, match="may not choose"):
        require_legal_next_consumer(
            "SPELL_NORMALIZATION",
            "R1_TERM_MEANING",
            selected_by=RouteSelector.MODEL_OUTPUT,
        )


def test_illegal_cross_lane_edge_fails_closed() -> None:
    with pytest.raises(NextConsumerPolicyError, match="illegal next consumer"):
        require_legal_next_consumer(
            "SPELL_NORMALIZATION",
            "R3_PLAN_COMPOSER",
            selected_by=RouteSelector.HOST,
        )


def test_consumer_identity_matching_is_exact_and_case_sensitive() -> None:
    with pytest.raises(NextConsumerPolicyError):
        require_legal_next_consumer(
            "SPELL_NORMALIZATION",
            "r1_term_meaning",
            selected_by=RouteSelector.HOST,
        )


def test_unknown_source_mode_fails_closed() -> None:
    with pytest.raises(KeyError, match="unknown next-consumer specialist mode"):
        get_next_consumer_policy("NOT_A_MODE")


def test_route_policy_does_not_infer_unregistered_destination() -> None:
    with pytest.raises(NextConsumerPolicyError):
        require_legal_next_consumer(
            "RESULT_FINAL_COMPOSE",
            "R8_SOMETHING_THAT_SOUNDS_RIGHT",
            selected_by=RouteSelector.HOST,
        )
