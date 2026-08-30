"""Exact-runtime, per-logical-mode qualification and authority registry."""

from __future__ import annotations

import hmac
import re
from dataclasses import dataclass, replace
from datetime import UTC, datetime
from enum import StrEnum

from arcadia.core.artifact_envelope import canonical_utc_timestamp
from arcadia.core.canonical_json import JsonValue, canonical_json_dumps
from arcadia.core.config import AuthorityTier, RuntimeConfig
from arcadia.core.hashing import Sha256Digest, sha256_canonical_json
from arcadia.core.ids import CanonicalId

TRUST_REGISTRY_VERSION = 1
_TOKEN_PATTERN = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:+/-]{0,127}", re.ASCII)
_TIER_RANK = {
    AuthorityTier.T0: 0,
    AuthorityTier.T1: 1,
    AuthorityTier.T2: 2,
    AuthorityTier.T3: 3,
    AuthorityTier.T4: 4,
    AuthorityTier.T5: 5,
    AuthorityTier.T6: 6,
}


class AdapterBindingKind(StrEnum):
    PHYSICAL_ADAPTER = "PHYSICAL_ADAPTER"
    BASE_ONLY = "BASE_ONLY"


class TrustStanding(StrEnum):
    ACTIVE = "ACTIVE"
    BLOCKED = "BLOCKED"


class AuthorityUse(StrEnum):
    QUALIFICATION = "QUALIFICATION"
    PROTOTYPE = "PROTOTYPE"
    SHADOW_RUNTIME = "SHADOW_RUNTIME"
    LIMITED_AUTHORITY = "LIMITED_AUTHORITY"
    PRODUCTION = "PRODUCTION"


class TrustEventKind(StrEnum):
    REGISTERED = "REGISTERED"
    PROMOTED = "PROMOTED"
    BLOCKED = "BLOCKED"
    RESET_TO_T0 = "RESET_TO_T0"


class TrustDecisionCode(StrEnum):
    AUTHORIZED = "AUTHORIZED"
    TARGET_NOT_REGISTERED = "TARGET_NOT_REGISTERED"
    MODE_NOT_REGISTERED = "MODE_NOT_REGISTERED"
    TARGET_BLOCKED = "TARGET_BLOCKED"
    BASE_ONLY_QUALIFICATION_ONLY = "BASE_ONLY_QUALIFICATION_ONLY"
    INSUFFICIENT_TRUST = "INSUFFICIENT_TRUST"
    AUTHORITY_CEILING = "AUTHORITY_CEILING"


class TrustRegistryError(ValueError):
    """Base error for invalid qualification identity or registry state."""


class TrustFieldError(TrustRegistryError):
    """A trust field is malformed, coerced, or outside the frozen contract."""


class TrustIntegrityError(TrustRegistryError):
    """A trust hash, evidence chain, target identity, or transition is inconsistent."""


class TrustConflictError(TrustRegistryError):
    """A registry update used a stale global head or target revision."""


def _token(name: str, value: object) -> str:
    if type(value) is not str or _TOKEN_PATTERN.fullmatch(value) is None:
        raise TrustFieldError(f"{name} is not a legal canonical token")
    return value


def _positive(name: str, value: object) -> int:
    if type(value) is not int or value < 1:
        raise TrustFieldError(f"{name} must be a positive integer")
    return value


def _digest_equal(left: Sha256Digest, right: Sha256Digest) -> bool:
    return hmac.compare_digest(left.value, right.value)


def _parse_timestamp(name: str, value: object) -> datetime:
    if type(value) is not str:
        raise TrustFieldError(f"{name} must be a canonical UTC timestamp")
    try:
        parsed = datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=UTC)
    except ValueError as exc:
        raise TrustFieldError(
            f"{name} must use a real YYYY-MM-DDTHH:MM:SS.ffffffZ timestamp"
        ) from exc
    if canonical_utc_timestamp(parsed) != value:
        raise TrustFieldError(f"{name} is not in canonical UTC form")
    return parsed


def _next_tier(tier: AuthorityTier) -> AuthorityTier | None:
    rank = _TIER_RANK[tier] + 1
    return next((candidate for candidate, value in _TIER_RANK.items() if value == rank), None)


def _maximum_tier(left: AuthorityTier, right: AuthorityTier) -> AuthorityTier:
    return left if _TIER_RANK[left] >= _TIER_RANK[right] else right


@dataclass(frozen=True, slots=True)
class TrustPolicy:
    """Operational authority ceiling; earned qualification remains separate."""

    authority_ceiling: AuthorityTier
    policy_version: int = TRUST_REGISTRY_VERSION

    def __post_init__(self) -> None:
        if type(self.policy_version) is not int or self.policy_version != TRUST_REGISTRY_VERSION:
            raise TrustFieldError("unsupported trust policy version")
        if type(self.authority_ceiling) is not AuthorityTier:
            raise TrustFieldError("authority_ceiling must be an AuthorityTier")

    @classmethod
    def from_runtime_config(cls, config: RuntimeConfig) -> TrustPolicy:
        if type(config) is not RuntimeConfig:
            raise TrustFieldError("config must be a RuntimeConfig")
        return cls(authority_ceiling=config.authority_tier)

    @property
    def policy_hash(self) -> Sha256Digest:
        return sha256_canonical_json(self.to_value())

    def to_value(self) -> dict[str, JsonValue]:
        return {
            "authority_ceiling": self.authority_ceiling.value,
            "policy_version": self.policy_version,
        }


@dataclass(frozen=True, slots=True)
class RuntimeQualificationIdentity:
    """Every output-affecting identity field frozen into one qualification target."""

    binding_kind: AdapterBindingKind
    base_model_hash: Sha256Digest
    physical_adapter_id: CanonicalId | None
    physical_adapter_hash: Sha256Digest | None
    llama_cpp_build_id: str
    model_runtime_version: str
    adapter_manager_version: str
    specialist_invoker_version: str
    aae_contract_version: str
    specialist_mode_contract_version: str
    input_schema_version: str
    output_schema_version: str
    host_validator_version: str
    inference_profile_id: str
    inference_profile_hash: Sha256Digest

    def __post_init__(self) -> None:
        if type(self.binding_kind) is not AdapterBindingKind:
            raise TrustFieldError("binding_kind must be an AdapterBindingKind")
        if type(self.base_model_hash) is not Sha256Digest:
            raise TrustFieldError("base_model_hash must be a Sha256Digest")
        if self.binding_kind is AdapterBindingKind.PHYSICAL_ADAPTER:
            if type(self.physical_adapter_id) is not CanonicalId:
                raise TrustFieldError("physical adapter identity requires an adapter UUID")
            if type(self.physical_adapter_hash) is not Sha256Digest:
                raise TrustFieldError("physical adapter identity requires an adapter hash")
        elif self.physical_adapter_id is not None or self.physical_adapter_hash is not None:
            raise TrustIntegrityError("BASE_ONLY identity cannot carry a physical adapter")
        for name in (
            "llama_cpp_build_id",
            "model_runtime_version",
            "adapter_manager_version",
            "specialist_invoker_version",
            "aae_contract_version",
            "specialist_mode_contract_version",
            "input_schema_version",
            "output_schema_version",
            "host_validator_version",
            "inference_profile_id",
        ):
            _token(name, getattr(self, name))
        if type(self.inference_profile_hash) is not Sha256Digest:
            raise TrustFieldError("inference_profile_hash must be a Sha256Digest")

    @property
    def identity_hash(self) -> Sha256Digest:
        return sha256_canonical_json(self.to_value())

    def to_value(self) -> dict[str, JsonValue]:
        return {
            "aae_contract_version": self.aae_contract_version,
            "adapter_manager_version": self.adapter_manager_version,
            "base_model_hash": self.base_model_hash.value,
            "binding_kind": self.binding_kind.value,
            "host_validator_version": self.host_validator_version,
            "inference_profile_hash": self.inference_profile_hash.value,
            "inference_profile_id": self.inference_profile_id,
            "input_schema_version": self.input_schema_version,
            "llama_cpp_build_id": self.llama_cpp_build_id,
            "model_runtime_version": self.model_runtime_version,
            "output_schema_version": self.output_schema_version,
            "physical_adapter_hash": (
                None if self.physical_adapter_hash is None else self.physical_adapter_hash.value
            ),
            "physical_adapter_uuid": (
                None if self.physical_adapter_id is None else str(self.physical_adapter_id)
            ),
            "specialist_invoker_version": self.specialist_invoker_version,
            "specialist_mode_contract_version": self.specialist_mode_contract_version,
        }


@dataclass(frozen=True, slots=True)
class QualificationTarget:
    """One independently qualified logical mode bound to one exact runtime identity."""

    target_id: CanonicalId
    logical_mode_id: str
    minimum_runtime_tier: AuthorityTier
    runtime_identity: RuntimeQualificationIdentity

    def __post_init__(self) -> None:
        if type(self.target_id) is not CanonicalId:
            raise TrustFieldError("target_id must be a CanonicalId")
        _token("logical_mode_id", self.logical_mode_id)
        if type(self.minimum_runtime_tier) is not AuthorityTier:
            raise TrustFieldError("minimum_runtime_tier must be an AuthorityTier")
        if type(self.runtime_identity) is not RuntimeQualificationIdentity:
            raise TrustFieldError("runtime_identity must be a RuntimeQualificationIdentity")

    @classmethod
    def create(
        cls,
        *,
        logical_mode_id: str,
        minimum_runtime_tier: AuthorityTier,
        runtime_identity: RuntimeQualificationIdentity,
    ) -> QualificationTarget:
        return cls(
            target_id=CanonicalId.new(),
            logical_mode_id=logical_mode_id,
            minimum_runtime_tier=minimum_runtime_tier,
            runtime_identity=runtime_identity,
        )

    @property
    def target_hash(self) -> Sha256Digest:
        return sha256_canonical_json(self.to_value())

    def to_value(self) -> dict[str, JsonValue]:
        return {
            "logical_mode_id": self.logical_mode_id,
            "minimum_runtime_tier": self.minimum_runtime_tier.value,
            "runtime_identity": self.runtime_identity.to_value(),
            "runtime_identity_hash": self.runtime_identity.identity_hash.value,
            "target_uuid": str(self.target_id),
        }


@dataclass(frozen=True, slots=True, order=True)
class QualificationEvidence:
    """Immutable passing evidence for exactly one next trust tier."""

    evidence_id: CanonicalId
    tier: AuthorityTier
    suite_manifest_hash: Sha256Digest
    report_hash: Sha256Digest
    evaluation_identity_hash: Sha256Digest
    reviewer_id: CanonicalId
    qualified_at: str

    def __post_init__(self) -> None:
        if type(self.evidence_id) is not CanonicalId:
            raise TrustFieldError("evidence_id must be a CanonicalId")
        if type(self.tier) is not AuthorityTier or self.tier is AuthorityTier.T0:
            raise TrustFieldError("qualification evidence tier must be T1 through T6")
        for name in ("suite_manifest_hash", "report_hash", "evaluation_identity_hash"):
            if type(getattr(self, name)) is not Sha256Digest:
                raise TrustFieldError(f"{name} must be a Sha256Digest")
        if type(self.reviewer_id) is not CanonicalId:
            raise TrustFieldError("reviewer_id must be a CanonicalId")
        _parse_timestamp("qualified_at", self.qualified_at)

    @classmethod
    def create(
        cls,
        *,
        tier: AuthorityTier,
        suite_manifest_hash: Sha256Digest,
        report_hash: Sha256Digest,
        evaluation_identity_hash: Sha256Digest,
        reviewer_id: CanonicalId,
        qualified_at: datetime,
    ) -> QualificationEvidence:
        return cls(
            evidence_id=CanonicalId.new(),
            tier=tier,
            suite_manifest_hash=suite_manifest_hash,
            report_hash=report_hash,
            evaluation_identity_hash=evaluation_identity_hash,
            reviewer_id=reviewer_id,
            qualified_at=canonical_utc_timestamp(qualified_at),
        )

    def to_value(self) -> dict[str, JsonValue]:
        return {
            "evaluation_identity_hash": self.evaluation_identity_hash.value,
            "evidence_uuid": str(self.evidence_id),
            "qualified_at": self.qualified_at,
            "report_hash": self.report_hash.value,
            "reviewer_uuid": str(self.reviewer_id),
            "suite_manifest_hash": self.suite_manifest_hash.value,
            "tier": self.tier.value,
        }


@dataclass(frozen=True, slots=True)
class BlockingEvidence:
    """Host evidence that prevents normal authority for one exact target."""

    evidence_id: CanonicalId
    reason_code: str
    report_hash: Sha256Digest
    reviewer_id: CanonicalId
    recorded_at: str

    def __post_init__(self) -> None:
        if type(self.evidence_id) is not CanonicalId:
            raise TrustFieldError("blocking evidence_id must be a CanonicalId")
        _token("reason_code", self.reason_code)
        if type(self.report_hash) is not Sha256Digest:
            raise TrustFieldError("blocking report_hash must be a Sha256Digest")
        if type(self.reviewer_id) is not CanonicalId:
            raise TrustFieldError("blocking reviewer_id must be a CanonicalId")
        _parse_timestamp("recorded_at", self.recorded_at)

    @classmethod
    def create(
        cls,
        *,
        reason_code: str,
        report_hash: Sha256Digest,
        reviewer_id: CanonicalId,
        recorded_at: datetime,
    ) -> BlockingEvidence:
        return cls(
            evidence_id=CanonicalId.new(),
            reason_code=reason_code,
            report_hash=report_hash,
            reviewer_id=reviewer_id,
            recorded_at=canonical_utc_timestamp(recorded_at),
        )

    def to_value(self) -> dict[str, JsonValue]:
        return {
            "evidence_uuid": str(self.evidence_id),
            "reason_code": self.reason_code,
            "recorded_at": self.recorded_at,
            "report_hash": self.report_hash.value,
            "reviewer_uuid": str(self.reviewer_id),
        }


@dataclass(frozen=True, slots=True)
class TrustRecord:
    """Current earned tier and standing for one immutable qualification target."""

    target: QualificationTarget
    revision: int
    earned_tier: AuthorityTier
    standing: TrustStanding
    qualification_evidence: tuple[QualificationEvidence, ...]
    blocking_evidence: BlockingEvidence | None

    def __post_init__(self) -> None:
        if type(self.target) is not QualificationTarget:
            raise TrustFieldError("target must be a QualificationTarget")
        _positive("revision", self.revision)
        if type(self.earned_tier) is not AuthorityTier:
            raise TrustFieldError("earned_tier must be an AuthorityTier")
        if type(self.standing) is not TrustStanding:
            raise TrustFieldError("standing must be a TrustStanding")
        if type(self.qualification_evidence) is not tuple:
            raise TrustFieldError("qualification_evidence must be an immutable tuple")
        if any(type(item) is not QualificationEvidence for item in self.qualification_evidence):
            raise TrustFieldError("every qualification item must be QualificationEvidence")
        tiers = tuple(item.tier for item in self.qualification_evidence)
        expected = tuple(
            tier
            for tier in AuthorityTier
            if 0 < _TIER_RANK[tier] <= _TIER_RANK[self.earned_tier]
        )
        if tiers != expected:
            raise TrustIntegrityError("qualification evidence must be contiguous from T1")
        evidence_ids = [item.evidence_id for item in self.qualification_evidence]
        if len(evidence_ids) != len(set(evidence_ids)):
            raise TrustIntegrityError("qualification evidence UUIDs must be unique")
        if self.standing is TrustStanding.ACTIVE and self.blocking_evidence is not None:
            raise TrustIntegrityError("active trust record cannot carry blocking evidence")
        if self.standing is TrustStanding.BLOCKED and type(self.blocking_evidence) is not BlockingEvidence:
            raise TrustFieldError("blocked trust record requires BlockingEvidence")

    @classmethod
    def initial(cls, target: QualificationTarget) -> TrustRecord:
        return cls(
            target=target,
            revision=1,
            earned_tier=AuthorityTier.T0,
            standing=TrustStanding.ACTIVE,
            qualification_evidence=(),
            blocking_evidence=None,
        )

    @property
    def record_hash(self) -> Sha256Digest:
        return sha256_canonical_json(self.to_value())

    def to_value(self) -> dict[str, JsonValue]:
        return {
            "blocking_evidence": (
                None if self.blocking_evidence is None else self.blocking_evidence.to_value()
            ),
            "earned_tier": self.earned_tier.value,
            "qualification_evidence": [item.to_value() for item in self.qualification_evidence],
            "revision": self.revision,
            "standing": self.standing.value,
            "target": self.target.to_value(),
            "target_hash": self.target.target_hash.value,
        }


@dataclass(frozen=True, slots=True)
class TrustEvent:
    """One immutable, hash-chained trust-registry revision."""

    event_id: CanonicalId
    sequence: int
    event_kind: TrustEventKind
    occurred_at: str
    record: TrustRecord
    transition_evidence: BlockingEvidence | None
    previous_event_hash: Sha256Digest | None
    event_hash: Sha256Digest
    registry_version: int = TRUST_REGISTRY_VERSION

    def __post_init__(self) -> None:
        if type(self.registry_version) is not int or self.registry_version != TRUST_REGISTRY_VERSION:
            raise TrustFieldError("unsupported trust event version")
        if type(self.event_id) is not CanonicalId:
            raise TrustFieldError("event_id must be a CanonicalId")
        _positive("sequence", self.sequence)
        if type(self.event_kind) is not TrustEventKind:
            raise TrustFieldError("event_kind must be a TrustEventKind")
        _parse_timestamp("occurred_at", self.occurred_at)
        if type(self.record) is not TrustRecord:
            raise TrustFieldError("record must be a TrustRecord")
        if self.transition_evidence is not None and type(self.transition_evidence) is not BlockingEvidence:
            raise TrustFieldError("transition_evidence must be BlockingEvidence or None")
        if self.event_id == self.record.target.target_id:
            raise TrustIntegrityError("event UUID must differ from target UUID")
        if self.sequence == 1:
            if self.previous_event_hash is not None:
                raise TrustIntegrityError("first trust event cannot have a predecessor")
        elif type(self.previous_event_hash) is not Sha256Digest:
            raise TrustIntegrityError("later trust events require a predecessor hash")
        if type(self.event_hash) is not Sha256Digest:
            raise TrustFieldError("event_hash must be a Sha256Digest")
        if not _digest_equal(sha256_canonical_json(self._unsigned_value()), self.event_hash):
            raise TrustIntegrityError("event_hash does not match trust event content")

    @classmethod
    def create(
        cls,
        *,
        sequence: int,
        event_kind: TrustEventKind,
        occurred_at: datetime,
        record: TrustRecord,
        transition_evidence: BlockingEvidence | None,
        previous_event_hash: Sha256Digest | None,
    ) -> TrustEvent:
        event_id = CanonicalId.new()
        timestamp = canonical_utc_timestamp(occurred_at)
        unsigned = _trust_event_value(
            event_id=event_id,
            sequence=sequence,
            event_kind=event_kind,
            occurred_at=timestamp,
            record=record,
            transition_evidence=transition_evidence,
            previous_event_hash=previous_event_hash,
        )
        return cls(
            event_id=event_id,
            sequence=sequence,
            event_kind=event_kind,
            occurred_at=timestamp,
            record=record,
            transition_evidence=transition_evidence,
            previous_event_hash=previous_event_hash,
            event_hash=sha256_canonical_json(unsigned),
        )

    def _unsigned_value(self) -> dict[str, JsonValue]:
        return _trust_event_value(
            event_id=self.event_id,
            sequence=self.sequence,
            event_kind=self.event_kind,
            occurred_at=self.occurred_at,
            record=self.record,
            transition_evidence=self.transition_evidence,
            previous_event_hash=self.previous_event_hash,
        )

    def to_value(self) -> dict[str, JsonValue]:
        return {**self._unsigned_value(), "event_hash": self.event_hash.value}


def _trust_event_value(
    *,
    event_id: CanonicalId,
    sequence: int,
    event_kind: TrustEventKind,
    occurred_at: str,
    record: TrustRecord,
    transition_evidence: BlockingEvidence | None,
    previous_event_hash: Sha256Digest | None,
) -> dict[str, JsonValue]:
    return {
        "event_kind": event_kind.value,
        "event_uuid": str(event_id),
        "occurred_at": occurred_at,
        "previous_event_hash": None if previous_event_hash is None else previous_event_hash.value,
        "record": record.to_value(),
        "record_hash": record.record_hash.value,
        "registry_version": TRUST_REGISTRY_VERSION,
        "sequence": sequence,
        "transition_evidence": (
            None if transition_evidence is None else transition_evidence.to_value()
        ),
    }


@dataclass(frozen=True, slots=True)
class TrustDecision:
    """Deterministic exact-target authorization decision; never performs dispatch."""

    allowed: bool
    code: TrustDecisionCode
    logical_mode_id: str
    runtime_identity_hash: Sha256Digest
    requested_use: AuthorityUse
    earned_tier: AuthorityTier | None
    required_tier: AuthorityTier
    authority_ceiling: AuthorityTier
    target_hash: Sha256Digest | None
    registry_hash: Sha256Digest

    def to_value(self) -> dict[str, JsonValue]:
        return {
            "allowed": self.allowed,
            "authority_ceiling": self.authority_ceiling.value,
            "code": self.code.value,
            "earned_tier": None if self.earned_tier is None else self.earned_tier.value,
            "logical_mode_id": self.logical_mode_id,
            "registry_hash": self.registry_hash.value,
            "requested_use": self.requested_use.value,
            "required_tier": self.required_tier.value,
            "runtime_identity_hash": self.runtime_identity_hash.value,
            "target_hash": None if self.target_hash is None else self.target_hash.value,
        }


_USE_TIER = {
    AuthorityUse.QUALIFICATION: AuthorityTier.T0,
    AuthorityUse.PROTOTYPE: AuthorityTier.T3,
    AuthorityUse.SHADOW_RUNTIME: AuthorityTier.T4,
    AuthorityUse.LIMITED_AUTHORITY: AuthorityTier.T5,
    AuthorityUse.PRODUCTION: AuthorityTier.T6,
}


@dataclass(frozen=True, slots=True)
class TrustRegistry:
    """Append-only trust progression for exact mode/runtime targets."""

    policy: TrustPolicy
    events: tuple[TrustEvent, ...] = ()

    def __post_init__(self) -> None:
        if type(self.policy) is not TrustPolicy:
            raise TrustFieldError("policy must be a TrustPolicy")
        if type(self.events) is not tuple:
            raise TrustFieldError("events must be an immutable tuple")
        self._replay()

    @classmethod
    def create(cls, policy: TrustPolicy) -> TrustRegistry:
        return cls(policy=policy)

    @property
    def head_hash(self) -> Sha256Digest | None:
        return None if not self.events else self.events[-1].event_hash

    @property
    def registry_hash(self) -> Sha256Digest:
        return sha256_canonical_json(self.to_value())

    def current_records(self) -> dict[CanonicalId, TrustRecord]:
        return self._replay()

    def get(self, target_id: CanonicalId) -> TrustRecord:
        if type(target_id) is not CanonicalId:
            raise TrustFieldError("target_id must be a CanonicalId")
        try:
            return self.current_records()[target_id]
        except KeyError as exc:
            raise TrustFieldError("unknown qualification target UUID") from exc

    def register(
        self,
        *,
        target: QualificationTarget,
        occurred_at: datetime,
        expected_head: Sha256Digest | None,
    ) -> tuple[TrustRegistry, TrustEvent]:
        if type(target) is not QualificationTarget:
            raise TrustFieldError("target must be a QualificationTarget")
        records = self.current_records()
        if target.target_id in records:
            raise TrustIntegrityError("qualification target UUID is already registered")
        key = (target.logical_mode_id, target.runtime_identity.identity_hash)
        if any(
            (record.target.logical_mode_id, record.target.runtime_identity.identity_hash) == key
            for record in records.values()
        ):
            raise TrustIntegrityError("logical mode/runtime identity is already registered")
        return self._append(
            event_kind=TrustEventKind.REGISTERED,
            record=TrustRecord.initial(target),
            transition_evidence=None,
            occurred_at=occurred_at,
            expected_head=expected_head,
        )

    def promote(
        self,
        *,
        target_id: CanonicalId,
        expected_revision: int,
        evidence: QualificationEvidence,
        occurred_at: datetime,
        expected_head: Sha256Digest | None,
    ) -> tuple[TrustRegistry, TrustEvent]:
        current = self._current_for_update(target_id, expected_revision)
        if current.standing is TrustStanding.BLOCKED:
            raise TrustIntegrityError("blocked target cannot be promoted")
        expected_tier = _next_tier(current.earned_tier)
        if expected_tier is None:
            raise TrustIntegrityError("target already has T6 production authorization")
        if type(evidence) is not QualificationEvidence or evidence.tier is not expected_tier:
            raise TrustIntegrityError("promotion evidence must match the exact next trust tier")
        if evidence.evaluation_identity_hash != current.target.runtime_identity.identity_hash:
            raise TrustIntegrityError("qualification evidence belongs to a different runtime identity")
        updated = replace(
            current,
            revision=current.revision + 1,
            earned_tier=expected_tier,
            qualification_evidence=(*current.qualification_evidence, evidence),
        )
        return self._append(
            event_kind=TrustEventKind.PROMOTED,
            record=updated,
            transition_evidence=None,
            occurred_at=occurred_at,
            expected_head=expected_head,
        )

    def block(
        self,
        *,
        target_id: CanonicalId,
        expected_revision: int,
        evidence: BlockingEvidence,
        occurred_at: datetime,
        expected_head: Sha256Digest | None,
    ) -> tuple[TrustRegistry, TrustEvent]:
        current = self._current_for_update(target_id, expected_revision)
        if current.standing is TrustStanding.BLOCKED:
            raise TrustIntegrityError("target is already blocked")
        if type(evidence) is not BlockingEvidence:
            raise TrustFieldError("evidence must be BlockingEvidence")
        updated = replace(
            current,
            revision=current.revision + 1,
            standing=TrustStanding.BLOCKED,
            blocking_evidence=evidence,
        )
        return self._append(
            event_kind=TrustEventKind.BLOCKED,
            record=updated,
            transition_evidence=evidence,
            occurred_at=occurred_at,
            expected_head=expected_head,
        )

    def reset_blocked_to_t0(
        self,
        *,
        target_id: CanonicalId,
        expected_revision: int,
        reviewer_id: CanonicalId,
        reset_report_hash: Sha256Digest,
        occurred_at: datetime,
        expected_head: Sha256Digest | None,
    ) -> tuple[TrustRegistry, TrustEvent]:
        current = self._current_for_update(target_id, expected_revision)
        if current.standing is not TrustStanding.BLOCKED:
            raise TrustIntegrityError("only a blocked target can reset to T0")
        if type(reviewer_id) is not CanonicalId:
            raise TrustFieldError("reviewer_id must be a CanonicalId")
        if type(reset_report_hash) is not Sha256Digest:
            raise TrustFieldError("reset_report_hash must be a Sha256Digest")
        reset_evidence = BlockingEvidence.create(
            reason_code="RESET_TO_T0",
            report_hash=reset_report_hash,
            reviewer_id=reviewer_id,
            recorded_at=occurred_at,
        )
        updated = replace(
            current,
            revision=current.revision + 1,
            earned_tier=AuthorityTier.T0,
            standing=TrustStanding.ACTIVE,
            qualification_evidence=(),
            blocking_evidence=None,
        )
        return self._append(
            event_kind=TrustEventKind.RESET_TO_T0,
            record=updated,
            transition_evidence=reset_evidence,
            occurred_at=occurred_at,
            expected_head=expected_head,
        )

    def authorize(
        self,
        *,
        logical_mode_id: str,
        runtime_identity_hash: Sha256Digest,
        requested_use: AuthorityUse,
    ) -> TrustDecision:
        mode = _token("logical_mode_id", logical_mode_id)
        if type(runtime_identity_hash) is not Sha256Digest:
            raise TrustFieldError("runtime_identity_hash must be a Sha256Digest")
        if type(requested_use) is not AuthorityUse:
            raise TrustFieldError("requested_use must be an AuthorityUse")
        records = self.current_records().values()
        mode_records = [record for record in records if record.target.logical_mode_id == mode]
        record = next(
            (
                candidate
                for candidate in mode_records
                if _digest_equal(
                    candidate.target.runtime_identity.identity_hash,
                    runtime_identity_hash,
                )
            ),
            None,
        )
        required = _USE_TIER[requested_use]
        if record is not None and requested_use is not AuthorityUse.QUALIFICATION:
            required = _maximum_tier(required, record.target.minimum_runtime_tier)
        code = TrustDecisionCode.AUTHORIZED
        allowed = True
        if not mode_records:
            code, allowed = TrustDecisionCode.MODE_NOT_REGISTERED, False
        elif record is None:
            code, allowed = TrustDecisionCode.TARGET_NOT_REGISTERED, False
        elif record.standing is TrustStanding.BLOCKED and requested_use is not AuthorityUse.QUALIFICATION:
            code, allowed = TrustDecisionCode.TARGET_BLOCKED, False
        elif (
            record.target.runtime_identity.binding_kind is AdapterBindingKind.BASE_ONLY
            and requested_use is not AuthorityUse.QUALIFICATION
        ):
            code, allowed = TrustDecisionCode.BASE_ONLY_QUALIFICATION_ONLY, False
        elif _TIER_RANK[record.earned_tier] < _TIER_RANK[required]:
            code, allowed = TrustDecisionCode.INSUFFICIENT_TRUST, False
        elif (
            requested_use is not AuthorityUse.QUALIFICATION
            and _TIER_RANK[self.policy.authority_ceiling] < _TIER_RANK[required]
        ):
            code, allowed = TrustDecisionCode.AUTHORITY_CEILING, False
        return TrustDecision(
            allowed=allowed,
            code=code,
            logical_mode_id=mode,
            runtime_identity_hash=runtime_identity_hash,
            requested_use=requested_use,
            earned_tier=None if record is None else record.earned_tier,
            required_tier=required,
            authority_ceiling=self.policy.authority_ceiling,
            target_hash=None if record is None else record.target.target_hash,
            registry_hash=self.registry_hash,
        )

    def _current_for_update(
        self, target_id: CanonicalId, expected_revision: int
    ) -> TrustRecord:
        current = self.get(target_id)
        if type(expected_revision) is not int or current.revision != expected_revision:
            raise TrustConflictError("expected target revision does not match current revision")
        return current

    def _append(
        self,
        *,
        event_kind: TrustEventKind,
        record: TrustRecord,
        transition_evidence: BlockingEvidence | None,
        occurred_at: datetime,
        expected_head: Sha256Digest | None,
    ) -> tuple[TrustRegistry, TrustEvent]:
        self._require_head(expected_head)
        event = TrustEvent.create(
            sequence=len(self.events) + 1,
            event_kind=event_kind,
            occurred_at=occurred_at,
            record=record,
            transition_evidence=transition_evidence,
            previous_event_hash=self.head_hash,
        )
        advanced = TrustRegistry(policy=self.policy, events=(*self.events, event))
        return advanced, event

    def _require_head(self, expected: Sha256Digest | None) -> None:
        actual = self.head_hash
        if actual is None:
            if expected is not None:
                raise TrustConflictError("empty trust registry requires expected_head=None")
            return
        if type(expected) is not Sha256Digest or not _digest_equal(actual, expected):
            raise TrustConflictError("expected trust-registry head does not match current head")

    def _replay(self) -> dict[CanonicalId, TrustRecord]:
        records: dict[CanonicalId, TrustRecord] = {}
        keys: dict[tuple[str, Sha256Digest], CanonicalId] = {}
        event_ids: set[CanonicalId] = set()
        evidence_owners: dict[CanonicalId, CanonicalId] = {}
        introduced_evidence_ids: set[CanonicalId] = set()
        previous_hash: Sha256Digest | None = None
        previous_time: datetime | None = None
        for sequence, event in enumerate(self.events, start=1):
            if type(event) is not TrustEvent:
                raise TrustFieldError("every registry event must be a TrustEvent")
            if event.sequence != sequence:
                raise TrustIntegrityError("trust event sequences must be contiguous from one")
            if event.event_id in event_ids:
                raise TrustIntegrityError("trust event UUIDs must be unique")
            event_ids.add(event.event_id)
            if event.previous_event_hash != previous_hash:
                raise TrustIntegrityError("trust event predecessor chain is broken")
            event_time = _parse_timestamp("occurred_at", event.occurred_at)
            if previous_time is not None and event_time < previous_time:
                raise TrustIntegrityError("trust event timestamps must be nondecreasing")
            target = event.record.target
            for evidence in event.record.qualification_evidence:
                owner = evidence_owners.setdefault(evidence.evidence_id, target.target_id)
                if owner != target.target_id:
                    raise TrustIntegrityError("qualification evidence UUID was reused across targets")
            if event.transition_evidence is not None:
                owner = evidence_owners.setdefault(
                    event.transition_evidence.evidence_id, target.target_id
                )
                if owner != target.target_id:
                    raise TrustIntegrityError("transition evidence UUID was reused across targets")
            prior = records.get(target.target_id)
            key = (target.logical_mode_id, target.runtime_identity.identity_hash)
            self._validate_transition(event, prior)
            introduced: CanonicalId | None = None
            if event.event_kind is TrustEventKind.PROMOTED:
                introduced = event.record.qualification_evidence[-1].evidence_id
            elif event.transition_evidence is not None:
                introduced = event.transition_evidence.evidence_id
            if introduced is not None:
                if introduced in introduced_evidence_ids:
                    raise TrustIntegrityError("evidence UUID cannot authorize two transitions")
                introduced_evidence_ids.add(introduced)
            if event.event_kind is TrustEventKind.REGISTERED:
                if key in keys:
                    raise TrustIntegrityError("logical mode/runtime target is duplicated")
                keys[key] = target.target_id
            elif prior is not None and prior.target != target:
                raise TrustIntegrityError("trust transition changed immutable target identity")
            records[target.target_id] = event.record
            previous_hash = event.event_hash
            previous_time = event_time
        return records

    def _validate_transition(self, event: TrustEvent, prior: TrustRecord | None) -> None:
        current = event.record
        event_time = _parse_timestamp("occurred_at", event.occurred_at)
        if event.event_kind is TrustEventKind.REGISTERED:
            if (
                prior is not None
                or event.transition_evidence is not None
                or current.revision != 1
                or current != TrustRecord.initial(current.target)
            ):
                raise TrustIntegrityError("REGISTERED must create a clean T0 revision one")
            return
        if prior is None or current.revision != prior.revision + 1:
            raise TrustIntegrityError("trust revisions must be contiguous")
        if current.target != prior.target:
            raise TrustIntegrityError("trust transition changed qualification target")
        if event.event_kind is TrustEventKind.PROMOTED:
            next_tier = _next_tier(prior.earned_tier)
            latest_evidence = current.qualification_evidence[-1]
            if (
                event.transition_evidence is not None
                or prior.standing is not TrustStanding.ACTIVE
                or next_tier is None
                or current.earned_tier is not next_tier
                or current.standing is not TrustStanding.ACTIVE
                or current.blocking_evidence is not None
                or current.qualification_evidence[:-1] != prior.qualification_evidence
                or latest_evidence.tier is not next_tier
                or latest_evidence.evaluation_identity_hash
                != current.target.runtime_identity.identity_hash
                or _parse_timestamp("qualified_at", latest_evidence.qualified_at) > event_time
            ):
                raise TrustIntegrityError("invalid sequential promotion transition")
        elif event.event_kind is TrustEventKind.BLOCKED:
            if (
                prior.standing is not TrustStanding.ACTIVE
                or current.standing is not TrustStanding.BLOCKED
                or current.earned_tier is not prior.earned_tier
                or current.qualification_evidence != prior.qualification_evidence
                or current.blocking_evidence is None
                or event.transition_evidence != current.blocking_evidence
                or _parse_timestamp(
                    "recorded_at", current.blocking_evidence.recorded_at
                )
                > event_time
            ):
                raise TrustIntegrityError("invalid blocked transition")
        elif event.event_kind is TrustEventKind.RESET_TO_T0:
            if (
                prior.standing is not TrustStanding.BLOCKED
                or current.standing is not TrustStanding.ACTIVE
                or current.earned_tier is not AuthorityTier.T0
                or current.qualification_evidence
                or current.blocking_evidence is not None
                or event.transition_evidence is None
                or event.transition_evidence.reason_code != "RESET_TO_T0"
                or _parse_timestamp(
                    "recorded_at", event.transition_evidence.recorded_at
                )
                > event_time
            ):
                raise TrustIntegrityError("invalid reset-to-T0 transition")

    def to_value(self) -> dict[str, JsonValue]:
        records = self.current_records()
        return {
            "current_records": [records[key].to_value() for key in sorted(records)],
            "event_count": len(self.events),
            "events": [event.to_value() for event in self.events],
            "head_hash": None if self.head_hash is None else self.head_hash.value,
            "policy": self.policy.to_value(),
            "policy_hash": self.policy.policy_hash.value,
            "registry_version": TRUST_REGISTRY_VERSION,
        }

    def to_json(self) -> str:
        return canonical_json_dumps(self.to_value())
