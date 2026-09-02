"""Shared PRE-1 vocabulary classification and validation policy.

The host uses closed vocabularies only when a value directly controls host behavior
or the canonical recipe source freezes the complete vocabulary. Descriptive machine
labels remain pattern-bounded. Human-language content remains bounded free text; its
size limits are supplied by the separate AAE settings handler rather than this policy.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from types import MappingProxyType
from typing import Final

from arcadia.contracts.aae.registry import (
    MODE_SCOPE_PROPOSAL,
    MODE_SCOPE_VALIDATION,
    get_contract,
)


class VocabularyPolicyStatus(StrEnum):
    PRE_VERSION = "PRE_VERSION"
    FROZEN = "FROZEN"


class VocabularyKind(StrEnum):
    CLOSED_ENUM = "CLOSED_ENUM"
    PATTERN_BOUNDED = "PATTERN_BOUNDED"
    BOUNDED_FREE_TEXT = "BOUNDED_FREE_TEXT"


MACHINE_LABEL_PATTERN_PRE_V1: Final = r"^[A-Z][A-Z0-9_]*$"


class VocabularyPolicyError(ValueError):
    """A value violates its declared vocabulary class."""


@dataclass(frozen=True, slots=True)
class VocabularyRule:
    rule_id: str
    kind: VocabularyKind
    closed_values: tuple[str, ...] = ()
    pattern: str | None = None
    notes: str = ""

    def __post_init__(self) -> None:
        if not self.rule_id:
            raise VocabularyPolicyError("rule_id must not be empty")
        if self.kind is VocabularyKind.CLOSED_ENUM:
            if not self.closed_values:
                raise VocabularyPolicyError("closed enum requires at least one value")
            if self.pattern is not None:
                raise VocabularyPolicyError("closed enum may not also declare a pattern")
        elif self.kind is VocabularyKind.PATTERN_BOUNDED:
            if self.closed_values:
                raise VocabularyPolicyError("pattern-bounded rule may not declare closed values")
            if not self.pattern:
                raise VocabularyPolicyError("pattern-bounded rule requires a pattern")
            re.compile(self.pattern, flags=re.ASCII)
        else:
            if self.closed_values or self.pattern is not None:
                raise VocabularyPolicyError("bounded free text carries no vocabulary taxonomy")


@dataclass(frozen=True, slots=True)
class SharedVocabularyPolicy:
    policy_id: str
    status: VocabularyPolicyStatus
    host_behavior_values_are_closed: bool
    descriptive_machine_labels_are_pattern_bounded: bool
    human_language_is_bounded_free_text: bool
    size_caps_owned_by_settings_handler: bool


SHARED_VOCABULARY_POLICY_PRE_V1: Final = SharedVocabularyPolicy(
    policy_id="vocabulary.shared.pre1",
    status=VocabularyPolicyStatus.PRE_VERSION,
    host_behavior_values_are_closed=True,
    descriptive_machine_labels_are_pattern_bounded=True,
    human_language_is_bounded_free_text=True,
    size_caps_owned_by_settings_handler=True,
)


def _closed(rule_id: str, values: tuple[str, ...], notes: str = "") -> VocabularyRule:
    return VocabularyRule(
        rule_id=rule_id,
        kind=VocabularyKind.CLOSED_ENUM,
        closed_values=values,
        notes=notes,
    )


def _machine_label(rule_id: str, notes: str = "") -> VocabularyRule:
    return VocabularyRule(
        rule_id=rule_id,
        kind=VocabularyKind.PATTERN_BOUNDED,
        pattern=MACHINE_LABEL_PATTERN_PRE_V1,
        notes=notes,
    )


def _free_text(rule_id: str, notes: str = "") -> VocabularyRule:
    return VocabularyRule(
        rule_id=rule_id,
        kind=VocabularyKind.BOUNDED_FREE_TEXT,
        notes=notes,
    )


_SCOPE_PROPOSAL = get_contract(MODE_SCOPE_PROPOSAL)
_SCOPE_VALIDATION = get_contract(MODE_SCOPE_VALIDATION)

FIELD_VOCABULARY_REGISTRY_PRE_V1: Final[Mapping[str, VocabularyRule]] = MappingProxyType(
    {
        "SCOPE_PROPOSAL.mode": _closed(
            "vocab.scope_proposal.mode.pre1", (MODE_SCOPE_PROPOSAL,), "Host-selected mode identity."
        ),
        "SCOPE_PROPOSAL.status": _closed(
            "vocab.scope_proposal.status.pre1",
            _SCOPE_PROPOSAL.semantic_enums["proposal_outcome"],
            "Host branches on this value, so invention is forbidden.",
        ),
        "SCOPE_PROPOSAL.target_terms[]": _free_text(
            "vocab.scope_proposal.target_terms.pre1",
            "Retrieval terms are language content; separate settings own length/count caps.",
        ),
        "SCOPE_PROPOSAL.reason_codes[]": _machine_label(
            "vocab.scope_proposal.reason_codes.pre1",
            "Descriptive diagnostic vocabulary; not host authority or routing.",
        ),
        "SCOPE_VALIDATION.mode": _closed(
            "vocab.scope_validation.mode.pre1", (MODE_SCOPE_VALIDATION,), "Host-selected mode identity."
        ),
        "SCOPE_VALIDATION.status": _closed(
            "vocab.scope_validation.status.pre1",
            _SCOPE_VALIDATION.semantic_enums["validation_outcome"],
            "Host branches on this verdict, so invention is forbidden.",
        ),
        "SCOPE_VALIDATION.reason_codes[]": _machine_label(
            "vocab.scope_validation.reason_codes.pre1",
            "Descriptive diagnostic vocabulary; not host authority or routing.",
        ),
        "SCOPE_VALIDATION.unresolved_references[]": _free_text(
            "vocab.scope_validation.unresolved_references.pre1",
            "Human-language referent descriptions; settings own size caps.",
        ),
    }
)


def get_vocabulary_rule(field_id: str) -> VocabularyRule:
    try:
        return FIELD_VOCABULARY_REGISTRY_PRE_V1[field_id]
    except KeyError as exc:
        raise VocabularyPolicyError(f"unknown vocabulary field: {field_id}") from exc


def require_valid_vocabulary_value(rule: VocabularyRule, value: str) -> str:
    if type(value) is not str:
        raise VocabularyPolicyError("vocabulary value must be text")
    if rule.kind is VocabularyKind.CLOSED_ENUM:
        if value not in rule.closed_values:
            raise VocabularyPolicyError(
                f"value {value!r} is outside closed vocabulary {rule.rule_id}"
            )
    elif rule.kind is VocabularyKind.PATTERN_BOUNDED:
        assert rule.pattern is not None
        if re.fullmatch(rule.pattern, value, flags=re.ASCII) is None:
            raise VocabularyPolicyError(
                f"value {value!r} does not match pattern vocabulary {rule.rule_id}"
            )
    # BOUNDED_FREE_TEXT intentionally has no taxonomy check here. Size/shape belongs
    # to schema + the settings handler, not the vocabulary policy.
    return value
