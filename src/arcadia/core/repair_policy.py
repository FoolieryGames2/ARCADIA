"""Immutable, bounded repair authorization for learned-call failures."""

from __future__ import annotations

import hmac
import re
from dataclasses import dataclass
from typing import Final

from arcadia.core.canonical_json import (
    JsonValue,
    canonical_json_dumps,
    require_canonical_json,
)
from arcadia.core.hashing import Sha256Digest, sha256_canonical_json
from arcadia.core.ids import CanonicalId

REPAIR_POLICY_VERSION = 1

_TOKEN_PATTERN: Final = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:+/-]{0,127}", re.ASCII)


class RepairPolicyError(ValueError):
    """Base error for invalid repair policy, lineage, or authorization."""


class RepairFieldError(RepairPolicyError):
    """A repair value is malformed, mutable, or outside the strict contract."""


class RepairIntegrityError(RepairPolicyError):
    """A repair hash, ordinal, predecessor, or authoritative basis is inconsistent."""


class RepairExhaustedError(RepairPolicyError):
    """No further repair may be authorized under the aggregate per-call cap."""


def _exact_nonnegative_int(name: str, value: object) -> int:
    if type(value) is not int or value < 0:
        raise RepairFieldError(f"{name} must be a nonnegative integer")
    return value


def _exact_positive_int(name: str, value: object) -> int:
    if type(value) is not int or value < 1:
        raise RepairFieldError(f"{name} must be a positive integer")
    return value


def _token(name: str, value: object) -> str:
    if type(value) is not str or _TOKEN_PATTERN.fullmatch(value) is None:
        raise RepairFieldError(f"{name} is not a legal canonical token")
    return value


def _digest_equal(left: Sha256Digest, right: Sha256Digest) -> bool:
    return hmac.compare_digest(left.value, right.value)


def _snapshot_value(name: str, value: JsonValue) -> tuple[str, Sha256Digest]:
    try:
        canonical = canonical_json_dumps(value)
    except ValueError as exc:
        raise RepairFieldError(f"{name} must use the strict JSON data model: {exc}") from exc
    return canonical, sha256_canonical_json(value)


def _verified_snapshot(
    name: str, canonical: object, expected_hash: object
) -> tuple[JsonValue, Sha256Digest]:
    if type(canonical) is not str:
        raise RepairFieldError(f"{name} canonical snapshot must be text")
    if type(expected_hash) is not Sha256Digest:
        raise RepairFieldError(f"{name} hash must be a Sha256Digest")
    try:
        value = require_canonical_json(canonical)
    except ValueError as exc:
        raise RepairFieldError(f"{name} snapshot is not Canonical JSON V1: {exc}") from exc
    actual = sha256_canonical_json(value)
    if not _digest_equal(actual, expected_hash):
        raise RepairIntegrityError(f"{name} hash does not match its canonical snapshot")
    return value, expected_hash


@dataclass(frozen=True, slots=True)
class RepairPolicy:
    """Versioned host policy for the aggregate repairs allowed per learned call."""

    max_repairs_per_call: int
    policy_version: int = REPAIR_POLICY_VERSION

    def __post_init__(self) -> None:
        if type(self.policy_version) is not int or self.policy_version != REPAIR_POLICY_VERSION:
            raise RepairFieldError("unsupported repair policy version")
        _exact_nonnegative_int("max_repairs_per_call", self.max_repairs_per_call)

    @property
    def policy_hash(self) -> Sha256Digest:
        """Return the canonical identity of this policy."""

        return sha256_canonical_json(self.to_value())

    def to_value(self) -> dict[str, JsonValue]:
        """Return the canonical policy value used for audit and hashing."""

        return {
            "max_repairs_per_call": self.max_repairs_per_call,
            "policy_version": self.policy_version,
        }


@dataclass(frozen=True, slots=True)
class RepairBasis:
    """Frozen authority that every repair for one learned call must reuse."""

    call_id: CanonicalId
    specialist_mode: str
    inference_profile_id: str
    inference_profile_hash: Sha256Digest
    authoritative_packet_json: str
    authoritative_packet_hash: Sha256Digest

    def __post_init__(self) -> None:
        if type(self.call_id) is not CanonicalId:
            raise RepairFieldError("call_id must be a CanonicalId")
        _token("specialist_mode", self.specialist_mode)
        _token("inference_profile_id", self.inference_profile_id)
        if type(self.inference_profile_hash) is not Sha256Digest:
            raise RepairFieldError("inference_profile_hash must be a Sha256Digest")
        _verified_snapshot(
            "authoritative packet",
            self.authoritative_packet_json,
            self.authoritative_packet_hash,
        )

    @classmethod
    def create(
        cls,
        *,
        call_id: CanonicalId,
        specialist_mode: str,
        inference_profile_id: str,
        inference_profile_hash: Sha256Digest,
        authoritative_packet: JsonValue,
    ) -> RepairBasis:
        """Freeze the exact packet and runtime binding of the original call."""

        canonical, packet_hash = _snapshot_value(
            "authoritative_packet", authoritative_packet
        )
        return cls(
            call_id=call_id,
            specialist_mode=specialist_mode,
            inference_profile_id=inference_profile_id,
            inference_profile_hash=inference_profile_hash,
            authoritative_packet_json=canonical,
            authoritative_packet_hash=packet_hash,
        )

    @property
    def basis_hash(self) -> Sha256Digest:
        """Hash the call, mode, profile, and exact authoritative packet together."""

        return sha256_canonical_json(self.to_value())

    def packet_value(self) -> JsonValue:
        """Return a fresh strict-JSON copy of the frozen authoritative packet."""

        return require_canonical_json(self.authoritative_packet_json)

    def to_value(self) -> dict[str, JsonValue]:
        """Return a canonical value containing the exact reusable repair basis."""

        return {
            "authoritative_packet": self.packet_value(),
            "authoritative_packet_hash": self.authoritative_packet_hash.value,
            "call_uuid": str(self.call_id),
            "inference_profile_hash": self.inference_profile_hash.value,
            "inference_profile_id": self.inference_profile_id,
            "specialist_mode": self.specialist_mode,
        }


@dataclass(frozen=True, slots=True)
class RepairAttempt:
    """One host-authorized repair with immutable failure evidence and lineage."""

    attempt_id: CanonicalId
    call_id: CanonicalId
    repair_ordinal: int
    previous_attempt_id: CanonicalId | None
    basis_hash: Sha256Digest
    policy_hash: Sha256Digest
    previous_output_json: str
    previous_output_hash: Sha256Digest
    validation_error_json: str
    validation_error_hash: Sha256Digest

    def __post_init__(self) -> None:
        if type(self.attempt_id) is not CanonicalId:
            raise RepairFieldError("attempt_id must be a CanonicalId")
        if type(self.call_id) is not CanonicalId:
            raise RepairFieldError("call_id must be a CanonicalId")
        if self.attempt_id == self.call_id:
            raise RepairIntegrityError("repair attempt UUID must differ from the original call UUID")
        _exact_positive_int("repair_ordinal", self.repair_ordinal)
        if self.repair_ordinal == 1:
            if self.previous_attempt_id is not None:
                raise RepairIntegrityError("the first repair cannot have a repair predecessor")
        elif type(self.previous_attempt_id) is not CanonicalId:
            raise RepairIntegrityError("later repairs require the prior repair attempt UUID")
        if type(self.basis_hash) is not Sha256Digest:
            raise RepairFieldError("basis_hash must be a Sha256Digest")
        if type(self.policy_hash) is not Sha256Digest:
            raise RepairFieldError("policy_hash must be a Sha256Digest")
        _verified_snapshot(
            "previous output", self.previous_output_json, self.previous_output_hash
        )
        validation_error, _ = _verified_snapshot(
            "validation error", self.validation_error_json, self.validation_error_hash
        )
        if type(validation_error) is not dict or not validation_error:
            raise RepairFieldError("validation_error must be a nonempty machine error object")

    @property
    def requires_fresh_context(self) -> bool:
        """Repairs may never reuse model context state."""

        return True

    @property
    def requires_fresh_sampler(self) -> bool:
        """Repairs may never reuse sampler state."""

        return True

    def previous_output_value(self) -> JsonValue:
        """Return a fresh copy of the exact invalid output."""

        return require_canonical_json(self.previous_output_json)

    def validation_error_value(self) -> dict[str, JsonValue]:
        """Return a fresh copy of the exact machine validation error."""

        value = require_canonical_json(self.validation_error_json)
        assert type(value) is dict
        return value

    def to_value(self) -> dict[str, JsonValue]:
        """Return canonical repair-attempt evidence without granting execution authority."""

        return {
            "attempt_uuid": str(self.attempt_id),
            "basis_hash": self.basis_hash.value,
            "call_uuid": str(self.call_id),
            "policy_hash": self.policy_hash.value,
            "previous_attempt_uuid": (
                None if self.previous_attempt_id is None else str(self.previous_attempt_id)
            ),
            "previous_output": self.previous_output_value(),
            "previous_output_hash": self.previous_output_hash.value,
            "repair_ordinal": self.repair_ordinal,
            "requires_fresh_context": True,
            "requires_fresh_sampler": True,
            "validation_error": self.validation_error_value(),
            "validation_error_hash": self.validation_error_hash.value,
        }


@dataclass(frozen=True, slots=True)
class RepairSession:
    """Immutable aggregate repair state for exactly one original learned call."""

    policy: RepairPolicy
    basis: RepairBasis
    attempts: tuple[RepairAttempt, ...] = ()

    def __post_init__(self) -> None:
        if type(self.policy) is not RepairPolicy:
            raise RepairFieldError("policy must be a RepairPolicy")
        if type(self.basis) is not RepairBasis:
            raise RepairFieldError("basis must be a RepairBasis")
        if type(self.attempts) is not tuple:
            raise RepairFieldError("attempts must be an immutable tuple")
        if len(self.attempts) > self.policy.max_repairs_per_call:
            raise RepairIntegrityError("repair history exceeds the aggregate per-call cap")

        seen: set[CanonicalId] = set()
        predecessor: CanonicalId | None = None
        for ordinal, attempt in enumerate(self.attempts, start=1):
            if type(attempt) is not RepairAttempt:
                raise RepairFieldError("every repair history item must be a RepairAttempt")
            if attempt.attempt_id in seen:
                raise RepairIntegrityError("repair attempt UUIDs must be unique")
            seen.add(attempt.attempt_id)
            if attempt.call_id != self.basis.call_id:
                raise RepairIntegrityError("repair attempt belongs to a different learned call")
            if attempt.repair_ordinal != ordinal:
                raise RepairIntegrityError("repair ordinals must be contiguous from one")
            if attempt.previous_attempt_id != predecessor:
                raise RepairIntegrityError("repair predecessor chain is broken")
            if not _digest_equal(attempt.basis_hash, self.basis.basis_hash):
                raise RepairIntegrityError("repair attempt changed its authoritative basis")
            if not _digest_equal(attempt.policy_hash, self.policy.policy_hash):
                raise RepairIntegrityError("repair attempt changed its policy identity")
            predecessor = attempt.attempt_id

    @classmethod
    def begin(cls, *, policy: RepairPolicy, basis: RepairBasis) -> RepairSession:
        """Begin bounded repair accounting without authorizing an attempt yet."""

        return cls(policy=policy, basis=basis)

    @property
    def repairs_used(self) -> int:
        return len(self.attempts)

    @property
    def repairs_remaining(self) -> int:
        return self.policy.max_repairs_per_call - self.repairs_used

    @property
    def exhausted(self) -> bool:
        return self.repairs_remaining == 0

    def authorize(
        self,
        *,
        previous_output: JsonValue,
        validation_error: dict[str, JsonValue],
    ) -> tuple[RepairSession, RepairAttempt]:
        """Authorize one fresh-state repair or fail without altering this session."""

        if self.exhausted:
            raise RepairExhaustedError(
                f"repair cap exhausted for call {self.basis.call_id}: "
                f"{self.policy.max_repairs_per_call} allowed"
            )
        if type(validation_error) is not dict or not validation_error:
            raise RepairFieldError("validation_error must be a nonempty machine error object")
        output_json, output_hash = _snapshot_value("previous_output", previous_output)
        error_json, error_hash = _snapshot_value("validation_error", validation_error)
        previous_attempt_id = self.attempts[-1].attempt_id if self.attempts else None
        attempt = RepairAttempt(
            attempt_id=CanonicalId.new(),
            call_id=self.basis.call_id,
            repair_ordinal=self.repairs_used + 1,
            previous_attempt_id=previous_attempt_id,
            basis_hash=self.basis.basis_hash,
            policy_hash=self.policy.policy_hash,
            previous_output_json=output_json,
            previous_output_hash=output_hash,
            validation_error_json=error_json,
            validation_error_hash=error_hash,
        )
        advanced = RepairSession(
            policy=self.policy,
            basis=self.basis,
            attempts=(*self.attempts, attempt),
        )
        return advanced, attempt

    def to_value(self) -> dict[str, JsonValue]:
        """Return canonical aggregate repair state for trace/ledger consumers."""

        return {
            "attempts": [attempt.to_value() for attempt in self.attempts],
            "basis": self.basis.to_value(),
            "basis_hash": self.basis.basis_hash.value,
            "exhausted": self.exhausted,
            "policy": self.policy.to_value(),
            "policy_hash": self.policy.policy_hash.value,
            "repairs_remaining": self.repairs_remaining,
            "repairs_used": self.repairs_used,
        }
