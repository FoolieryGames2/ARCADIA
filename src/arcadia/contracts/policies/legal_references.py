"""PRE-1 legal-reference policy derived from the AAE Contract Registry.

Authoritative references are opaque host-owned identities.  A learned specialist
may copy only a reference that was explicitly supplied in a namespace legal for its
logical mode.  New model proposals use the contract's separate local-key prefixes
and never become authoritative merely because the model typed an identifier.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from enum import StrEnum
from types import MappingProxyType
from typing import Final

from arcadia.contracts.aae.registry import AAE_REGISTRY_PRE_V1, get_contract


class LegalReferencePolicyStatus(StrEnum):
    PRE_VERSION = "PRE_VERSION"
    FROZEN = "FROZEN"


@dataclass(frozen=True, slots=True)
class LegalReferencePolicy:
    policy_id: str
    policy_version: str
    status: LegalReferencePolicyStatus
    specialist_mode_id: str
    legal_authoritative_namespaces: tuple[str, ...]
    legal_local_key_prefixes: tuple[str, ...]
    exact_copy_required: bool = True
    authoritative_id_allocation_host_only: bool = True
    local_keys_are_non_authoritative: bool = True
    host_canonicalization_required: bool = True
    identifier_text_has_no_semantic_meaning: bool = True

    @property
    def frozen(self) -> bool:
        return self.status is LegalReferencePolicyStatus.FROZEN


@dataclass(frozen=True, slots=True)
class SuppliedAuthoritativeReference:
    """One authoritative identity explicitly supplied by the host for this call."""

    namespace: str
    value: str


def _policy(mode: str) -> LegalReferencePolicy:
    contract = get_contract(mode)
    return LegalReferencePolicy(
        policy_id=f"legal_refs.{mode.lower()}.pre1",
        policy_version="PRE-1",
        status=LegalReferencePolicyStatus.PRE_VERSION,
        specialist_mode_id=mode,
        legal_authoritative_namespaces=contract.legal_authoritative_ref_namespaces,
        legal_local_key_prefixes=contract.local_key_policy.allowed_prefixes,
        authoritative_id_allocation_host_only=(
            contract.local_key_policy.authoritative_id_allocation_forbidden
        ),
        host_canonicalization_required=contract.local_key_policy.host_canonicalization_required,
    )


LEGAL_REFERENCE_POLICY_REGISTRY_PRE_V1: Final[Mapping[str, LegalReferencePolicy]] = MappingProxyType(
    {mode: _policy(mode) for mode in AAE_REGISTRY_PRE_V1}
)


class LegalReferencePolicyError(ValueError):
    """A learned reference or local proposal key violates host identity authority."""


def get_legal_reference_policy(specialist_mode_id: str) -> LegalReferencePolicy:
    try:
        return LEGAL_REFERENCE_POLICY_REGISTRY_PRE_V1[specialist_mode_id]
    except KeyError as exc:
        raise KeyError(f"unknown legal-reference specialist mode: {specialist_mode_id}") from exc


def require_valid_supplied_reference_manifest(
    specialist_mode_id: str,
    refs: Sequence[SuppliedAuthoritativeReference],
) -> tuple[SuppliedAuthoritativeReference, ...]:
    """Validate the authoritative refs made available to one learned call.

    The manifest may be empty.  Every supplied namespace must be legal for the
    mode, and duplicate namespace/value pairs are rejected rather than normalized.
    """

    policy = get_legal_reference_policy(specialist_mode_id)
    legal = set(policy.legal_authoritative_namespaces)
    seen: set[tuple[str, str]] = set()
    result: list[SuppliedAuthoritativeReference] = []
    for ref in refs:
        if not ref.namespace or not ref.value:
            raise LegalReferencePolicyError("supplied authoritative reference fields must be non-empty")
        if ref.namespace not in legal:
            raise LegalReferencePolicyError(
                f"{specialist_mode_id} may not receive authoritative namespace {ref.namespace}"
            )
        key = (ref.namespace, ref.value)
        if key in seen:
            raise LegalReferencePolicyError(
                f"duplicate supplied authoritative reference: {ref.namespace}={ref.value}"
            )
        seen.add(key)
        result.append(ref)
    return tuple(result)


def require_exact_authoritative_reference_copy(
    specialist_mode_id: str,
    *,
    namespace: str,
    value: str,
    supplied_refs: Sequence[SuppliedAuthoritativeReference],
) -> str:
    """Accept only an exact, case-sensitive copy of a supplied legal ref."""

    policy = get_legal_reference_policy(specialist_mode_id)
    if namespace not in policy.legal_authoritative_namespaces:
        raise LegalReferencePolicyError(
            f"{specialist_mode_id} may not output authoritative namespace {namespace}"
        )

    checked = require_valid_supplied_reference_manifest(specialist_mode_id, supplied_refs)
    if not any(ref.namespace == namespace and ref.value == value for ref in checked):
        raise LegalReferencePolicyError(
            f"authoritative reference was not supplied exactly: {namespace}={value}"
        )
    return value


def require_valid_local_proposal_key(
    specialist_mode_id: str,
    local_key: str,
    *,
    supplied_refs: Sequence[SuppliedAuthoritativeReference] = (),
) -> str:
    """Require a mode-legal, visibly non-authoritative local proposal key.

    PRE-1 intentionally does not freeze the full local-key grammar.  It enforces
    the registry-owned prefix, a small ASCII-safe token surface, and no collision
    with any authoritative value supplied to the call.
    """

    policy = get_legal_reference_policy(specialist_mode_id)
    if not policy.legal_local_key_prefixes:
        raise LegalReferencePolicyError(
            f"{specialist_mode_id} does not permit model-created local proposal keys"
        )
    if not any(local_key.startswith(prefix) for prefix in policy.legal_local_key_prefixes):
        raise LegalReferencePolicyError(
            f"local key does not use a legal prefix for {specialist_mode_id}: {local_key}"
        )
    if not local_key or len(local_key) > 128 or any(
        not (char.isascii() and (char.isupper() or char.isdigit() or char == "_"))
        for char in local_key
    ):
        raise LegalReferencePolicyError(
            "PRE-1 local proposal key must be <=128 ASCII uppercase/digit/underscore characters"
        )
    if any(ref.value == local_key for ref in supplied_refs):
        raise LegalReferencePolicyError(
            "model-local proposal key may not collide with a supplied authoritative reference"
        )
    return local_key
