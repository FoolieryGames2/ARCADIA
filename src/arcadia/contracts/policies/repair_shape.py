"""PRE-1 AAE repair-shape policy.

Repair is a bounded correction of the same learned call, never a fresh reasoning
universe. Semantic repair permissions live in the AAE contract registry. Tunable
attempt counts live in the separate AAE settings handler. The deterministic Phase A
repair ledger remains the authority for immutable repair basis, attempt UUIDs, exact
validation-error evidence, lineage, and aggregate exhaustion accounting.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from types import MappingProxyType
from typing import Final

from arcadia.contracts.aae.registry import AAE_REGISTRY_PRE_V1, get_contract
from arcadia.contracts.aae.types import AAEContractRecord, RepairShape
from arcadia.core.canonical_json import JsonValue
from arcadia.core.hashing import Sha256Digest
from arcadia.core.repair_policy import (
    RepairAttempt,
    RepairBasis,
    RepairExhaustedError,
    RepairPolicy,
    RepairSession,
)
from arcadia.settings import AAESettingsHandler


class RepairShapePolicyError(ValueError):
    """A repair request violates semantic repair policy or is unresolved."""


class RepairStopCode(StrEnum):
    """Typed host outcomes when a repair cannot legitimately continue."""

    REPAIR_NOT_ALLOWED = "REPAIR_NOT_ALLOWED"
    REPAIR_LIMIT_UNRESOLVED = "REPAIR_LIMIT_UNRESOLVED"
    REPAIR_BUDGET_EXHAUSTED = "REPAIR_BUDGET_EXHAUSTED"


@dataclass(frozen=True, slots=True)
class RepairShapePolicy:
    """Registry-derived semantic repair rules for one specialist mode."""

    specialist_mode_id: str
    settings_profile_id: str
    shape: RepairShape


@dataclass(frozen=True, slots=True)
class RepairResolution:
    """Resolved repair permission and tunable attempt ceiling for one contract."""

    specialist_mode_id: str
    settings_profile_id: str
    allowed: bool
    max_repair_attempts: int | None

    @property
    def resolved(self) -> bool:
        return (not self.allowed) or self.max_repair_attempts is not None

    def to_policy(self) -> RepairPolicy:
        if not self.allowed:
            return RepairPolicy(max_repairs_per_call=0)
        if self.max_repair_attempts is None:
            raise RepairShapePolicyError(
                f"repair limit is unresolved for {self.specialist_mode_id}; unresolved is not unlimited"
            )
        return RepairPolicy(max_repairs_per_call=self.max_repair_attempts)


@dataclass(frozen=True, slots=True)
class RepairModelPacket:
    """Exact model-visible repair projection; prior invalid output stays audit-only."""

    authoritative_source_packet: JsonValue
    specialist_mode: str
    inference_profile_id: str
    inference_profile_hash: str
    attempt_uuid: str
    validation_error: dict[str, JsonValue]

    def to_value(self) -> dict[str, JsonValue]:
        return {
            "attempt_uuid": self.attempt_uuid,
            "authoritative_source_packet": self.authoritative_source_packet,
            "inference_profile_hash": self.inference_profile_hash,
            "inference_profile_id": self.inference_profile_id,
            "specialist_mode": self.specialist_mode,
            "validation_error": self.validation_error,
        }


@dataclass(frozen=True, slots=True)
class RepairStop:
    """Typed host-side stop that preserves truth instead of starting another loop."""

    code: RepairStopCode
    call_uuid: str
    specialist_mode_id: str
    repairs_used: int
    max_repair_attempts: int | None

    def to_value(self) -> dict[str, JsonValue]:
        return {
            "call_uuid": self.call_uuid,
            "code": self.code.value,
            "max_repair_attempts": self.max_repair_attempts,
            "repairs_used": self.repairs_used,
            "specialist_mode_id": self.specialist_mode_id,
        }


def _policy_from_contract(contract: AAEContractRecord) -> RepairShapePolicy:
    return RepairShapePolicy(
        specialist_mode_id=contract.specialist_mode_id,
        settings_profile_id=contract.settings_profile_id,
        shape=contract.repair,
    )


REPAIR_SHAPE_POLICY_REGISTRY_PRE_V1: Final[Mapping[str, RepairShapePolicy]] = MappingProxyType(
    {
        mode: _policy_from_contract(contract)
        for mode, contract in AAE_REGISTRY_PRE_V1.items()
    }
)


def get_repair_shape_policy(specialist_mode_id: str) -> RepairShapePolicy:
    try:
        return REPAIR_SHAPE_POLICY_REGISTRY_PRE_V1[specialist_mode_id]
    except KeyError as exc:
        raise RepairShapePolicyError(
            f"unknown specialist mode for repair policy: {specialist_mode_id}"
        ) from exc


def resolve_repair_policy(
    specialist_mode_id: str,
    *,
    settings: AAESettingsHandler,
) -> RepairResolution:
    """Resolve semantic permission plus the independently tunable repair ceiling."""

    policy = get_repair_shape_policy(specialist_mode_id)
    if not policy.shape.allowed:
        return RepairResolution(
            specialist_mode_id=specialist_mode_id,
            settings_profile_id=policy.settings_profile_id,
            allowed=False,
            max_repair_attempts=0,
        )
    resolved_settings = settings.resolve(policy.settings_profile_id)
    if resolved_settings.specialist_mode_id != specialist_mode_id:
        raise RepairShapePolicyError(
            "settings profile specialist mode does not match repair contract"
        )
    return RepairResolution(
        specialist_mode_id=specialist_mode_id,
        settings_profile_id=policy.settings_profile_id,
        allowed=True,
        max_repair_attempts=resolved_settings.limits.max_repair_attempts,
    )


def begin_repair_session(
    specialist_mode_id: str,
    *,
    settings: AAESettingsHandler,
    basis: RepairBasis,
) -> RepairSession | RepairStop:
    """Begin a bounded session or return a typed stop; never infer an unlimited cap."""

    contract = get_contract(specialist_mode_id)
    shape = contract.repair
    if basis.specialist_mode != specialist_mode_id:
        raise RepairShapePolicyError("repair basis changed specialist mode")
    if shape.same_inference_profile and basis.inference_profile_id != contract.inference_profile_id:
        raise RepairShapePolicyError("repair basis changed inference profile")

    resolution = resolve_repair_policy(specialist_mode_id, settings=settings)
    if not resolution.allowed:
        return RepairStop(
            code=RepairStopCode.REPAIR_NOT_ALLOWED,
            call_uuid=str(basis.call_id),
            specialist_mode_id=specialist_mode_id,
            repairs_used=0,
            max_repair_attempts=0,
        )
    if resolution.max_repair_attempts is None:
        return RepairStop(
            code=RepairStopCode.REPAIR_LIMIT_UNRESOLVED,
            call_uuid=str(basis.call_id),
            specialist_mode_id=specialist_mode_id,
            repairs_used=0,
            max_repair_attempts=None,
        )
    return RepairSession.begin(policy=resolution.to_policy(), basis=basis)


def authorize_repair_or_stop(
    session: RepairSession,
    *,
    previous_output: JsonValue,
    validation_error: dict[str, JsonValue],
) -> tuple[RepairSession, RepairAttempt] | RepairStop:
    """Authorize exactly one correction or convert exhaustion into a typed stop."""

    if session.exhausted:
        return RepairStop(
            code=RepairStopCode.REPAIR_BUDGET_EXHAUSTED,
            call_uuid=str(session.basis.call_id),
            specialist_mode_id=session.basis.specialist_mode,
            repairs_used=session.repairs_used,
            max_repair_attempts=session.policy.max_repairs_per_call,
        )
    try:
        return session.authorize(
            previous_output=previous_output,
            validation_error=validation_error,
        )
    except RepairExhaustedError:
        # Defensive conversion if the lower-level aggregate policy changes state
        # between a future preflight and authorization implementation.
        return RepairStop(
            code=RepairStopCode.REPAIR_BUDGET_EXHAUSTED,
            call_uuid=str(session.basis.call_id),
            specialist_mode_id=session.basis.specialist_mode,
            repairs_used=session.repairs_used,
            max_repair_attempts=session.policy.max_repairs_per_call,
        )


def project_repair_attempt_for_model(
    specialist_mode_id: str,
    *,
    basis: RepairBasis,
    attempt: RepairAttempt,
) -> RepairModelPacket:
    """Project only the canonical repair contract; invalid prior output is not re-fed."""

    contract = get_contract(specialist_mode_id)
    shape = contract.repair
    if not shape.allowed:
        raise RepairShapePolicyError(f"repair is not allowed for {specialist_mode_id}")
    if attempt.call_id != basis.call_id:
        raise RepairShapePolicyError("repair attempt belongs to a different learned call")
    if attempt.basis_hash != basis.basis_hash:
        raise RepairShapePolicyError("repair attempt changed authoritative repair basis")
    if shape.same_specialist_mode and basis.specialist_mode != specialist_mode_id:
        raise RepairShapePolicyError("repair changed specialist mode")
    if shape.same_inference_profile and basis.inference_profile_id != contract.inference_profile_id:
        raise RepairShapePolicyError("repair changed inference profile")
    if not isinstance(basis.inference_profile_hash, Sha256Digest):
        raise RepairShapePolicyError("repair inference profile hash is invalid")

    return RepairModelPacket(
        authoritative_source_packet=basis.packet_value(),
        specialist_mode=basis.specialist_mode,
        inference_profile_id=basis.inference_profile_id,
        inference_profile_hash=basis.inference_profile_hash.value,
        attempt_uuid=str(attempt.attempt_id),
        validation_error=attempt.validation_error_value(),
    )
