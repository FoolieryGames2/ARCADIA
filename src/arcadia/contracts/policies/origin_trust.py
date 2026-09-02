"""PRE-1 origin/trust policy for model-visible AAE data.

The v0.1 build authority requires explicit model-visible origin/trust framing while
keeping all data text non-instructional.  This module encodes that boundary without
inventing numeric adapter trust tiers, source-quality rankings, or tool/runtime
trust mechanics that belong to later gates.

One PRE-1 extension is explicit and deliberate: ``VALIDATED_RECIPE_ARTIFACT``.
The master authority names "prior validated recipe artifacts" as a legal data-plane
class but gives no canonical origin token for it.  Keeping a distinct provisional
origin is safer than mislabeling learned artifacts as ``HOST_DERIVED_SIGNAL``.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from enum import StrEnum
from types import MappingProxyType
from typing import Final


class OriginTrustPolicyStatus(StrEnum):
    """Lifecycle state for an origin/trust policy definition."""

    PRE_VERSION = "PRE_VERSION"
    FROZEN = "FROZEN"


class DataOrigin(StrEnum):
    """Source class for one bounded model-visible data item."""

    USER_PROMPT = "USER_PROMPT"
    TRANSCRIPT = "TRANSCRIPT"
    SEMANTIC_MEMORY = "SEMANTIC_MEMORY"
    TOOL_RECEIPT = "TOOL_RECEIPT"
    WEB_RESULT = "WEB_RESULT"
    HOST_DERIVED_SIGNAL = "HOST_DERIVED_SIGNAL"

    # PRE-1 extension: the master authority explicitly permits prior validated
    # recipe artifacts in the data plane but does not give that class an origin
    # token.  Do not silently pretend those semantic artifacts were host-derived.
    VALIDATED_RECIPE_ARTIFACT = "VALIDATED_RECIPE_ARTIFACT"


CANONICAL_V0_1_DATA_ORIGINS: Final[tuple[DataOrigin, ...]] = (
    DataOrigin.USER_PROMPT,
    DataOrigin.TRANSCRIPT,
    DataOrigin.SEMANTIC_MEMORY,
    DataOrigin.TOOL_RECEIPT,
    DataOrigin.WEB_RESULT,
    DataOrigin.HOST_DERIVED_SIGNAL,
)

PRE1_ORIGIN_EXTENSIONS: Final[tuple[DataOrigin, ...]] = (
    DataOrigin.VALIDATED_RECIPE_ARTIFACT,
)


class DataAuthorityClass(StrEnum):
    """Claim/evidence framing metadata; never instruction authority."""

    CONTENT_ONLY = "CONTENT_ONLY"
    EXTERNAL_UNTRUSTED_EVIDENCE = "EXTERNAL_UNTRUSTED_EVIDENCE"
    HOST_VERIFIED_EXECUTION = "HOST_VERIFIED_EXECUTION"
    HOST_VERIFIED_STATE = "HOST_VERIFIED_STATE"


class ReferenceContentState(StrEnum):
    """Whether the semantic content behind an authoritative reference is supplied."""

    CONTENT_SUPPLIED = "CONTENT_SUPPLIED"
    REFERENCE_ONLY = "REFERENCE_ONLY"


class SemanticUse(StrEnum):
    """How the specialist is allowed to use this item on this call."""

    IDENTITY_ONLY = "IDENTITY_ONLY"
    SEMANTIC_INTERPRETATION = "SEMANTIC_INTERPRETATION"


@dataclass(frozen=True, slots=True)
class ModelVisibleDataTrust:
    """Sidecar metadata for one bounded model-visible item.

    ``authoritative_ref`` is optional for direct content such as a raw user prompt.
    A REFERENCE_ONLY item must carry a reference.  If semantic interpretation is
    required, the bounded content must be supplied rather than only the identifier.
    """

    item_key: str
    origin: DataOrigin
    authority_class: DataAuthorityClass
    reference_content_state: ReferenceContentState
    semantic_use: SemanticUse
    authoritative_ref: str | None = None


@dataclass(frozen=True, slots=True)
class OriginTrustPolicy:
    """Per-specialist PRE-1 origin/trust admission policy."""

    policy_id: str
    policy_version: str
    status: OriginTrustPolicyStatus
    specialist_mode_id: str
    allowed_origins: tuple[DataOrigin, ...]
    data_text_instruction_authority: DataAuthorityClass = DataAuthorityClass.CONTENT_ONLY
    labels_are_framing_not_injection_proof: bool = True
    bare_reference_never_supplies_semantic_meaning: bool = True
    source_quality_ranking_out_of_scope: bool = True
    adapter_runtime_trust_out_of_scope: bool = True

    @property
    def frozen(self) -> bool:
        return self.status is OriginTrustPolicyStatus.FROZEN


# Authority-class admission is intentionally conservative.  This is not a source
# quality hierarchy: it only blocks category mistakes such as a user prompt being
# relabeled as HOST_VERIFIED_STATE or a web result as HOST_VERIFIED_EXECUTION.
ORIGIN_AUTHORITY_COMPATIBILITY_PRE_V1: Final[
    Mapping[DataOrigin, tuple[DataAuthorityClass, ...]]
] = MappingProxyType(
    {
        DataOrigin.USER_PROMPT: (DataAuthorityClass.CONTENT_ONLY,),
        DataOrigin.TRANSCRIPT: (DataAuthorityClass.CONTENT_ONLY,),
        DataOrigin.SEMANTIC_MEMORY: (
            DataAuthorityClass.CONTENT_ONLY,
            DataAuthorityClass.HOST_VERIFIED_STATE,
        ),
        DataOrigin.TOOL_RECEIPT: (DataAuthorityClass.HOST_VERIFIED_EXECUTION,),
        DataOrigin.WEB_RESULT: (DataAuthorityClass.EXTERNAL_UNTRUSTED_EVIDENCE,),
        DataOrigin.HOST_DERIVED_SIGNAL: (
            DataAuthorityClass.CONTENT_ONLY,
            DataAuthorityClass.HOST_VERIFIED_STATE,
        ),
        DataOrigin.VALIDATED_RECIPE_ARTIFACT: (DataAuthorityClass.CONTENT_ONLY,),
    }
)


# These sets are origin admission only.  They do not override each contract's
# legal input artifact classes or legal reference namespaces; all gates must agree.
_MODE_ALLOWED_ORIGINS: Final[Mapping[str, tuple[DataOrigin, ...]]] = MappingProxyType(
    {
        "SCOPE_PROPOSAL": (
            DataOrigin.USER_PROMPT,
            DataOrigin.HOST_DERIVED_SIGNAL,
        ),
        "SCOPE_VALIDATION": (
            DataOrigin.USER_PROMPT,
            DataOrigin.TRANSCRIPT,
            DataOrigin.HOST_DERIVED_SIGNAL,
        ),
        "SPELL_NORMALIZATION": (DataOrigin.USER_PROMPT,),
        "TERM_MEANING": (
            DataOrigin.USER_PROMPT,
            DataOrigin.TRANSCRIPT,
            DataOrigin.HOST_DERIVED_SIGNAL,
            DataOrigin.VALIDATED_RECIPE_ARTIFACT,
        ),
        "PROMPT_ANALYSIS": (
            DataOrigin.USER_PROMPT,
            DataOrigin.HOST_DERIVED_SIGNAL,
            DataOrigin.VALIDATED_RECIPE_ARTIFACT,
        ),
        "INTENT_ORGANIZER": (
            DataOrigin.HOST_DERIVED_SIGNAL,
            DataOrigin.VALIDATED_RECIPE_ARTIFACT,
        ),
        "INTENT_COMMENT": (DataOrigin.VALIDATED_RECIPE_ARTIFACT,),
        "CONTEXT_EVIDENCE_ASSESSMENT": (
            DataOrigin.USER_PROMPT,
            DataOrigin.TRANSCRIPT,
            DataOrigin.SEMANTIC_MEMORY,
            DataOrigin.TOOL_RECEIPT,
            DataOrigin.WEB_RESULT,
            DataOrigin.HOST_DERIVED_SIGNAL,
            DataOrigin.VALIDATED_RECIPE_ARTIFACT,
        ),
        "CONTEXT_LANE_COMMENT": (DataOrigin.VALIDATED_RECIPE_ARTIFACT,),
        "CONTEXT_FINAL_SYNTHESIS": (
            DataOrigin.USER_PROMPT,
            DataOrigin.VALIDATED_RECIPE_ARTIFACT,
        ),
        "REQUIREMENT_ASSESSMENT": (
            DataOrigin.HOST_DERIVED_SIGNAL,
            DataOrigin.VALIDATED_RECIPE_ARTIFACT,
        ),
        "PLAN_COMPOSITION": (
            DataOrigin.HOST_DERIVED_SIGNAL,
            DataOrigin.VALIDATED_RECIPE_ARTIFACT,
        ),
        "EVIDENCE_RECONCILIATION": (
            DataOrigin.TOOL_RECEIPT,
            DataOrigin.WEB_RESULT,
            DataOrigin.HOST_DERIVED_SIGNAL,
            DataOrigin.VALIDATED_RECIPE_ARTIFACT,
        ),
        "RECONCILIATION_COMPOSITION": (
            DataOrigin.HOST_DERIVED_SIGNAL,
            DataOrigin.VALIDATED_RECIPE_ARTIFACT,
        ),
        "PERSISTENCE_ASSESSMENT": (
            DataOrigin.SEMANTIC_MEMORY,
            DataOrigin.HOST_DERIVED_SIGNAL,
            DataOrigin.VALIDATED_RECIPE_ARTIFACT,
        ),
        "PERSISTENCE_COMPOSITION": (
            DataOrigin.SEMANTIC_MEMORY,
            DataOrigin.HOST_DERIVED_SIGNAL,
            DataOrigin.VALIDATED_RECIPE_ARTIFACT,
        ),
        "COMPLETION_ASSESSMENT": (
            DataOrigin.TOOL_RECEIPT,
            DataOrigin.HOST_DERIVED_SIGNAL,
            DataOrigin.VALIDATED_RECIPE_ARTIFACT,
        ),
        "COMPLETION_COMPOSITION": (
            DataOrigin.HOST_DERIVED_SIGNAL,
            DataOrigin.VALIDATED_RECIPE_ARTIFACT,
        ),
        "RESULT_REQUIREMENT_COMMENT": (
            DataOrigin.HOST_DERIVED_SIGNAL,
            DataOrigin.VALIDATED_RECIPE_ARTIFACT,
        ),
        "RESULT_FINAL_COMPOSE": (
            DataOrigin.USER_PROMPT,
            DataOrigin.HOST_DERIVED_SIGNAL,
            DataOrigin.VALIDATED_RECIPE_ARTIFACT,
        ),
    }
)


def _policy(mode: str, allowed: tuple[DataOrigin, ...]) -> OriginTrustPolicy:
    return OriginTrustPolicy(
        policy_id=f"origin_trust.{mode.lower()}.pre1",
        policy_version="PRE-1",
        status=OriginTrustPolicyStatus.PRE_VERSION,
        specialist_mode_id=mode,
        allowed_origins=allowed,
    )


ORIGIN_TRUST_POLICY_REGISTRY_PRE_V1: Final[Mapping[str, OriginTrustPolicy]] = MappingProxyType(
    {mode: _policy(mode, allowed) for mode, allowed in _MODE_ALLOWED_ORIGINS.items()}
)


class OriginTrustPolicyError(ValueError):
    """Model-visible data violates origin/trust or bare-reference policy."""


def get_origin_trust_policy(specialist_mode_id: str) -> OriginTrustPolicy:
    """Resolve the exact PRE-1 origin/trust policy for one logical mode."""

    try:
        return ORIGIN_TRUST_POLICY_REGISTRY_PRE_V1[specialist_mode_id]
    except KeyError as exc:
        raise KeyError(f"unknown origin/trust specialist mode: {specialist_mode_id}") from exc


def require_valid_origin_trust_item(
    specialist_mode_id: str,
    item: ModelVisibleDataTrust,
) -> ModelVisibleDataTrust:
    """Fail closed on illegal mode/origin/authority/reference framing."""

    policy = get_origin_trust_policy(specialist_mode_id)
    if not item.item_key:
        raise OriginTrustPolicyError("origin/trust item_key must be non-empty")
    if item.origin not in policy.allowed_origins:
        raise OriginTrustPolicyError(
            f"{specialist_mode_id} may not consume origin {item.origin.value}"
        )

    allowed_authority = ORIGIN_AUTHORITY_COMPATIBILITY_PRE_V1[item.origin]
    if item.authority_class not in allowed_authority:
        raise OriginTrustPolicyError(
            f"origin {item.origin.value} may not claim authority_class "
            f"{item.authority_class.value}"
        )

    if (
        item.reference_content_state is ReferenceContentState.REFERENCE_ONLY
        and not item.authoritative_ref
    ):
        raise OriginTrustPolicyError("REFERENCE_ONLY metadata requires authoritative_ref")

    if (
        item.semantic_use is SemanticUse.SEMANTIC_INTERPRETATION
        and item.reference_content_state is ReferenceContentState.REFERENCE_ONLY
    ):
        raise OriginTrustPolicyError(
            "bare authoritative reference cannot supply semantic meaning; bounded content is required"
        )

    return item


def require_valid_origin_trust_manifest(
    specialist_mode_id: str,
    items: Sequence[ModelVisibleDataTrust],
) -> tuple[ModelVisibleDataTrust, ...]:
    """Validate an immutable sidecar manifest before learned-call preparation/dispatch.

    This PRE-1 function is the host gate for origin/trust metadata.  Per-contract
    schemas will later decide exactly how each item's metadata is projected into the
    model-visible representation; this gate deliberately does not rewrite CALL_DATA.
    """

    if not items:
        raise OriginTrustPolicyError("origin/trust manifest must contain at least one data item")

    seen_keys: set[str] = set()
    checked: list[ModelVisibleDataTrust] = []
    for item in items:
        if item.item_key in seen_keys:
            raise OriginTrustPolicyError(f"duplicate origin/trust item_key: {item.item_key}")
        seen_keys.add(item.item_key)
        checked.append(require_valid_origin_trust_item(specialist_mode_id, item))
    return tuple(checked)
