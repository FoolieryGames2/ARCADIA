from __future__ import annotations

import pytest

from arcadia.contracts.policies.vocabulary import (
    FIELD_VOCABULARY_REGISTRY_PRE_V1,
    SHARED_VOCABULARY_POLICY_PRE_V1,
    VocabularyKind,
    VocabularyPolicyError,
    get_vocabulary_rule,
    require_valid_vocabulary_value,
)


def test_reviewed_three_way_vocabulary_policy_is_encoded() -> None:
    policy = SHARED_VOCABULARY_POLICY_PRE_V1
    assert policy.host_behavior_values_are_closed is True
    assert policy.descriptive_machine_labels_are_pattern_bounded is True
    assert policy.human_language_is_bounded_free_text is True
    assert policy.size_caps_owned_by_settings_handler is True


def test_scope_statuses_are_closed_and_registry_derived() -> None:
    proposal = get_vocabulary_rule("SCOPE_PROPOSAL.status")
    validation = get_vocabulary_rule("SCOPE_VALIDATION.status")
    assert proposal.kind is VocabularyKind.CLOSED_ENUM
    assert proposal.closed_values == (
        "SUFFICIENT_WITHOUT_HISTORY",
        "REQUEST_RECENT",
        "REQUEST_TARGETED",
    )
    assert validation.kind is VocabularyKind.CLOSED_ENUM
    assert validation.closed_values == (
        "SUFFICIENT",
        "SUFFICIENT_WITHOUT_HISTORY",
        "NEEDS_MORE_RECENT",
        "NEEDS_TARGETED_HISTORY",
        "UNRESOLVABLE_WITH_TRANSCRIPT",
        "BOUND_EXHAUSTED",
    )


def test_closed_enum_rejects_model_invented_host_branch() -> None:
    rule = get_vocabulary_rule("SCOPE_PROPOSAL.status")
    with pytest.raises(VocabularyPolicyError, match="outside closed vocabulary"):
        require_valid_vocabulary_value(rule, "NEEDS_SOME_HISTORY")


def test_reason_codes_are_pattern_bounded_not_silently_taxonomized() -> None:
    rule = get_vocabulary_rule("SCOPE_PROPOSAL.reason_codes[]")
    assert rule.kind is VocabularyKind.PATTERN_BOUNDED
    assert require_valid_vocabulary_value(rule, "UNRESOLVED_REFERENCE") == "UNRESOLVED_REFERENCE"
    with pytest.raises(VocabularyPolicyError, match="does not match"):
        require_valid_vocabulary_value(rule, "unresolved reference")


def test_language_fields_are_bounded_free_text_not_closed_enums() -> None:
    for field_id in (
        "SCOPE_PROPOSAL.target_terms[]",
        "SCOPE_VALIDATION.unresolved_references[]",
    ):
        rule = get_vocabulary_rule(field_id)
        assert rule.kind is VocabularyKind.BOUNDED_FREE_TEXT
        assert require_valid_vocabulary_value(rule, "whatever the user actually said")


def test_every_pre1_vocabulary_rule_has_an_explicit_kind() -> None:
    assert FIELD_VOCABULARY_REGISTRY_PRE_V1
    assert all(rule.kind in VocabularyKind for rule in FIELD_VOCABULARY_REGISTRY_PRE_V1.values())
