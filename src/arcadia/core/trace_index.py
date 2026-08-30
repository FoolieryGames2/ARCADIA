"""Privacy-minimized, immutable trace-index metadata and raw-state lifecycle."""

from __future__ import annotations

import hmac
import re
from dataclasses import dataclass, replace
from datetime import UTC, datetime, timedelta
from enum import StrEnum

from arcadia.core.artifact_envelope import RecipeId, canonical_utc_timestamp
from arcadia.core.canonical_json import JsonValue, canonical_json_dumps
from arcadia.core.config import TracingConfig
from arcadia.core.hashing import Sha256Digest, sha256_canonical_json
from arcadia.core.ids import CanonicalId

TRACE_INDEX_VERSION = 1
_MODE_PATTERN = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:+/-]{0,127}", re.ASCII)


class TraceSliceKind(StrEnum):
    RAW_TURN = "RAW_TURN"
    RECIPE_ARTIFACT = "RECIPE_ARTIFACT"
    LEARNED_CALL = "LEARNED_CALL"
    REPAIR_ATTEMPT = "REPAIR_ATTEMPT"
    REENTRY_SLICE = "REENTRY_SLICE"
    TOOL_EVIDENCE = "TOOL_EVIDENCE"
    PERSISTENCE_TRANSACTION = "PERSISTENCE_TRANSACTION"
    COMPLETION = "COMPLETION"
    RESULT_PUBLICATION = "RESULT_PUBLICATION"
    RECOVERY_EVENT = "RECOVERY_EVENT"
    CROSS_TURN_LINEAGE = "CROSS_TURN_LINEAGE"


class TraceReferenceKind(StrEnum):
    ARTIFACT = "ARTIFACT"
    CALL = "CALL"
    ATTEMPT = "ATTEMPT"
    ACTIVATION = "ACTIVATION"
    OPERATION = "OPERATION"
    PUBLICATION = "PUBLICATION"
    TURN = "TURN"
    TRACE = "TRACE"


class ValidationStanding(StrEnum):
    NOT_APPLICABLE = "NOT_APPLICABLE"
    PASSED = "PASSED"
    REJECTED = "REJECTED"
    ERROR = "ERROR"


class FirstPassStanding(StrEnum):
    NOT_APPLICABLE = "NOT_APPLICABLE"
    VALID = "VALID"
    INVALID = "INVALID"
    NOT_RUN = "NOT_RUN"


class TrainingState(StrEnum):
    NOT_SELECTED = "NOT_SELECTED"
    NEVER_TRAIN = "NEVER_TRAIN"


class RawDeletionState(StrEnum):
    NOT_CAPTURED = "NOT_CAPTURED"
    AVAILABLE = "AVAILABLE"
    TOMBSTONED = "TOMBSTONED"


class RawDeletionReason(StrEnum):
    RETENTION_EXPIRED = "RETENTION_EXPIRED"
    OWNER_DELETED = "OWNER_DELETED"


class TraceEventKind(StrEnum):
    REGISTERED = "REGISTERED"
    PINNED = "PINNED"
    UNPINNED = "UNPINNED"
    RAW_DELETION_CONFIRMED = "RAW_DELETION_CONFIRMED"


class TraceIndexError(ValueError):
    """Base error for trace-index metadata or lifecycle rejection."""


class TraceFieldError(TraceIndexError):
    """A trace field is malformed, content-bearing, or out of scope."""


class TraceIntegrityError(TraceIndexError):
    """A trace hash, transition, revision, or lineage relation is inconsistent."""


class TraceConflictError(TraceIndexError):
    """A mutation used a stale index head or stale trace revision."""


class TraceDisabledError(TraceIndexError):
    """Trace registration was attempted while the frozen policy disables tracing."""


def _nonnegative(name: str, value: object) -> int:
    if type(value) is not int or value < 0:
        raise TraceFieldError(f"{name} must be a nonnegative integer")
    return value


def _positive(name: str, value: object) -> int:
    if type(value) is not int or value < 1:
        raise TraceFieldError(f"{name} must be a positive integer")
    return value


def _digest_equal(left: Sha256Digest, right: Sha256Digest) -> bool:
    return hmac.compare_digest(left.value, right.value)


def _parse_timestamp(name: str, value: object) -> datetime:
    if type(value) is not str:
        raise TraceFieldError(f"{name} must be a canonical UTC timestamp")
    try:
        parsed = datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=UTC)
    except ValueError as exc:
        raise TraceFieldError(
            f"{name} must use a real YYYY-MM-DDTHH:MM:SS.ffffffZ timestamp"
        ) from exc
    if canonical_utc_timestamp(parsed) != value:
        raise TraceFieldError(f"{name} is not in canonical UTC form")
    return parsed


@dataclass(frozen=True, slots=True)
class TracePolicy:
    """Immutable trace configuration identity copied from Config V1."""

    enabled: bool
    raw_trace_enabled: bool
    raw_trace_retention_days: int
    training_export_enabled: bool
    policy_version: int = TRACE_INDEX_VERSION

    def __post_init__(self) -> None:
        if type(self.policy_version) is not int or self.policy_version != TRACE_INDEX_VERSION:
            raise TraceFieldError("unsupported trace policy version")
        for name in ("enabled", "raw_trace_enabled", "training_export_enabled"):
            if type(getattr(self, name)) is not bool:
                raise TraceFieldError(f"{name} must be a boolean")
        days = _positive("raw_trace_retention_days", self.raw_trace_retention_days)
        if days > 3650:
            raise TraceFieldError("raw_trace_retention_days cannot exceed 3650")
        if not self.enabled and (self.raw_trace_enabled or self.training_export_enabled):
            raise TraceFieldError("disabled tracing cannot enable raw trace or training export")

    @classmethod
    def from_config(cls, config: TracingConfig) -> TracePolicy:
        if type(config) is not TracingConfig:
            raise TraceFieldError("config must be a TracingConfig")
        return cls(**config.model_dump())

    @property
    def policy_hash(self) -> Sha256Digest:
        return sha256_canonical_json(self.to_value())

    def to_value(self) -> dict[str, JsonValue]:
        return {
            "enabled": self.enabled,
            "policy_version": self.policy_version,
            "raw_trace_enabled": self.raw_trace_enabled,
            "raw_trace_retention_days": self.raw_trace_retention_days,
            "training_export_enabled": self.training_export_enabled,
        }


@dataclass(frozen=True, slots=True, order=True)
class TraceReference:
    """A typed non-content link into the full causal graph."""

    kind: TraceReferenceKind
    target_id: CanonicalId
    target_hash: Sha256Digest | None = None

    def __post_init__(self) -> None:
        if type(self.kind) is not TraceReferenceKind:
            raise TraceFieldError("trace reference kind must be a TraceReferenceKind")
        if type(self.target_id) is not CanonicalId:
            raise TraceFieldError("trace reference target must be a CanonicalId")
        if self.target_hash is not None and type(self.target_hash) is not Sha256Digest:
            raise TraceFieldError("trace reference hash must be a Sha256Digest")

    def to_value(self) -> dict[str, JsonValue]:
        return {
            "kind": self.kind.value,
            "target_hash": None if self.target_hash is None else self.target_hash.value,
            "target_uuid": str(self.target_id),
        }


@dataclass(frozen=True, slots=True)
class TraceTelemetry:
    """Fixed numeric telemetry only; no arbitrary labels or content fields."""

    model_latency_ms: int = 0
    adapter_transition_ms: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    adapter_hot_hits: int = 0
    adapter_loads: int = 0
    adapter_evictions: int = 0

    def __post_init__(self) -> None:
        for name in (
            "model_latency_ms",
            "adapter_transition_ms",
            "input_tokens",
            "output_tokens",
            "adapter_hot_hits",
            "adapter_loads",
            "adapter_evictions",
        ):
            _nonnegative(name, getattr(self, name))

    def to_value(self) -> dict[str, JsonValue]:
        return {
            "adapter_evictions": self.adapter_evictions,
            "adapter_hot_hits": self.adapter_hot_hits,
            "adapter_loads": self.adapter_loads,
            "adapter_transition_ms": self.adapter_transition_ms,
            "input_tokens": self.input_tokens,
            "model_latency_ms": self.model_latency_ms,
            "output_tokens": self.output_tokens,
        }


@dataclass(frozen=True, slots=True)
class TraceIndexRecord:
    """One privacy-minimized current trace-index record."""

    trace_id: CanonicalId
    project_id: CanonicalId
    conversation_id: CanonicalId
    turn_id: CanonicalId
    revision: int
    slice_kind: TraceSliceKind
    recipe_id: RecipeId | None
    parent_trace_ids: tuple[CanonicalId, ...]
    specialist_id: CanonicalId | None
    specialist_mode: str | None
    base_model_hash: Sha256Digest | None
    adapter_hash: Sha256Digest | None
    aae_contract_hash: Sha256Digest | None
    schema_hash: Sha256Digest | None
    inference_profile_hash: Sha256Digest | None
    runtime_identity_hash: Sha256Digest | None
    runtime_epoch: int
    validation_standing: ValidationStanding
    repair_count: int
    first_pass_standing: FirstPassStanding
    telemetry: TraceTelemetry
    references: tuple[TraceReference, ...]
    created_at: str
    policy_hash: Sha256Digest
    raw_trace_id: CanonicalId | None
    raw_payload_hash: Sha256Digest | None
    raw_retention_expires_at: str | None
    raw_pinned: bool
    raw_deletion_state: RawDeletionState
    raw_deleted_at: str | None
    raw_deletion_reason: RawDeletionReason | None
    training_state: TrainingState
    trace_version: int = TRACE_INDEX_VERSION

    def __post_init__(self) -> None:
        if type(self.trace_version) is not int or self.trace_version != TRACE_INDEX_VERSION:
            raise TraceFieldError("unsupported trace index version")
        identities = (
            self.trace_id,
            self.project_id,
            self.conversation_id,
            self.turn_id,
        )
        if any(type(identity) is not CanonicalId for identity in identities):
            raise TraceFieldError("trace/project/conversation/turn IDs must be CanonicalId values")
        if len(set(identities)) != len(identities):
            raise TraceIntegrityError("trace/project/conversation/turn UUIDs must be distinct")
        _positive("revision", self.revision)
        if type(self.slice_kind) is not TraceSliceKind:
            raise TraceFieldError("slice_kind must be a TraceSliceKind")
        if self.recipe_id is not None and type(self.recipe_id) is not RecipeId:
            raise TraceFieldError("recipe_id must be a RecipeId")
        recipe_kinds = {
            TraceSliceKind.RECIPE_ARTIFACT,
            TraceSliceKind.LEARNED_CALL,
            TraceSliceKind.REPAIR_ATTEMPT,
            TraceSliceKind.REENTRY_SLICE,
            TraceSliceKind.PERSISTENCE_TRANSACTION,
            TraceSliceKind.COMPLETION,
            TraceSliceKind.RESULT_PUBLICATION,
        }
        if self.slice_kind in recipe_kinds and self.recipe_id is None:
            raise TraceFieldError("this trace slice requires a locked Recipe ID")
        self._validate_parents()
        self._validate_learned_identity()
        _nonnegative("runtime_epoch", self.runtime_epoch)
        if type(self.validation_standing) is not ValidationStanding:
            raise TraceFieldError("validation_standing must be a ValidationStanding")
        _nonnegative("repair_count", self.repair_count)
        if self.slice_kind is TraceSliceKind.REPAIR_ATTEMPT and self.repair_count < 1:
            raise TraceFieldError("repair-attempt traces require a positive repair_count")
        if type(self.first_pass_standing) is not FirstPassStanding:
            raise TraceFieldError("first_pass_standing must be a FirstPassStanding")
        if type(self.telemetry) is not TraceTelemetry:
            raise TraceFieldError("telemetry must be TraceTelemetry")
        self._validate_references()
        _parse_timestamp("created_at", self.created_at)
        if type(self.policy_hash) is not Sha256Digest:
            raise TraceFieldError("policy_hash must be a Sha256Digest")
        if type(self.training_state) is not TrainingState:
            raise TraceFieldError("training_state must be a TrainingState")
        self._validate_raw_state()

    def _validate_parents(self) -> None:
        if type(self.parent_trace_ids) is not tuple:
            raise TraceFieldError("parent_trace_ids must be an immutable tuple")
        if any(type(parent) is not CanonicalId for parent in self.parent_trace_ids):
            raise TraceFieldError("every parent trace ID must be a CanonicalId")
        if self.trace_id in self.parent_trace_ids:
            raise TraceIntegrityError("a trace cannot be its own parent")
        if len(set(self.parent_trace_ids)) != len(self.parent_trace_ids):
            raise TraceIntegrityError("parent trace IDs must be unique")
        if tuple(sorted(self.parent_trace_ids)) != self.parent_trace_ids:
            raise TraceFieldError("parent trace IDs must use canonical UUID order")
        if self.slice_kind is TraceSliceKind.CROSS_TURN_LINEAGE and not self.parent_trace_ids:
            raise TraceFieldError("cross-turn lineage requires at least one parent trace")

    def _validate_learned_identity(self) -> None:
        learned = self.slice_kind in {
            TraceSliceKind.LEARNED_CALL,
            TraceSliceKind.REPAIR_ATTEMPT,
        }
        if learned:
            if type(self.specialist_id) is not CanonicalId:
                raise TraceFieldError("learned-call traces require a specialist UUID")
            if (
                type(self.specialist_mode) is not str
                or _MODE_PATTERN.fullmatch(self.specialist_mode) is None
            ):
                raise TraceFieldError("learned-call traces require a canonical specialist mode")
            hashes = (
                self.base_model_hash,
                self.aae_contract_hash,
                self.schema_hash,
                self.inference_profile_hash,
                self.runtime_identity_hash,
            )
            if any(type(digest) is not Sha256Digest for digest in hashes):
                raise TraceFieldError("learned-call traces require exact runtime/contract hashes")
        elif self.specialist_id is not None or self.specialist_mode is not None:
            raise TraceFieldError("non-learned traces cannot claim specialist identity")
        for name in (
            "base_model_hash",
            "adapter_hash",
            "aae_contract_hash",
            "schema_hash",
            "inference_profile_hash",
            "runtime_identity_hash",
        ):
            value = getattr(self, name)
            if value is not None and type(value) is not Sha256Digest:
                raise TraceFieldError(f"{name} must be a Sha256Digest")

    def _validate_references(self) -> None:
        if type(self.references) is not tuple:
            raise TraceFieldError("references must be an immutable tuple")
        if any(type(reference) is not TraceReference for reference in self.references):
            raise TraceFieldError("every reference must be a TraceReference")
        keys = [(reference.kind, reference.target_id) for reference in self.references]
        if len(keys) != len(set(keys)):
            raise TraceIntegrityError("trace references must be unique by kind and target")
        ordered = tuple(sorted(self.references, key=lambda ref: (ref.kind.value, str(ref.target_id))))
        if self.references != ordered:
            raise TraceFieldError("trace references must use canonical kind/UUID order")
        kinds = {reference.kind for reference in self.references}
        if self.slice_kind is TraceSliceKind.LEARNED_CALL and TraceReferenceKind.CALL not in kinds:
            raise TraceFieldError("learned-call traces require their call reference")
        if self.slice_kind is TraceSliceKind.REPAIR_ATTEMPT and not {
            TraceReferenceKind.CALL,
            TraceReferenceKind.ATTEMPT,
        }.issubset(kinds):
            raise TraceFieldError("repair-attempt traces require call and attempt references")

    def _validate_raw_state(self) -> None:
        if type(self.raw_pinned) is not bool:
            raise TraceFieldError("raw_pinned must be a boolean")
        if type(self.raw_deletion_state) is not RawDeletionState:
            raise TraceFieldError("raw_deletion_state must be a RawDeletionState")
        if self.raw_deletion_state is RawDeletionState.NOT_CAPTURED:
            if any(
                value is not None
                for value in (
                    self.raw_trace_id,
                    self.raw_payload_hash,
                    self.raw_retention_expires_at,
                    self.raw_deleted_at,
                    self.raw_deletion_reason,
                )
            ) or self.raw_pinned:
                raise TraceIntegrityError("NOT_CAPTURED raw state cannot carry raw lifecycle data")
        elif self.raw_deletion_state is RawDeletionState.AVAILABLE:
            if type(self.raw_trace_id) is not CanonicalId:
                raise TraceFieldError("available raw state requires a raw trace UUID")
            if type(self.raw_payload_hash) is not Sha256Digest:
                raise TraceFieldError("available raw state requires a payload hash")
            if self.raw_retention_expires_at is None:
                raise TraceFieldError("available raw state requires a retention deadline")
            deadline = _parse_timestamp(
                "raw_retention_expires_at", self.raw_retention_expires_at
            )
            if deadline <= _parse_timestamp("created_at", self.created_at):
                raise TraceIntegrityError("raw retention deadline must follow creation")
            if self.raw_deleted_at is not None or self.raw_deletion_reason is not None:
                raise TraceIntegrityError("available raw state cannot carry deletion metadata")
        else:
            if self.raw_trace_id is not None or self.raw_retention_expires_at is not None:
                raise TraceIntegrityError("tombstoned raw state cannot retain a live raw reference")
            if type(self.raw_payload_hash) is not Sha256Digest:
                raise TraceFieldError("raw tombstone must retain the forensic payload hash")
            if self.raw_pinned:
                raise TraceIntegrityError("tombstoned raw state cannot remain pinned")
            deleted = _parse_timestamp("raw_deleted_at", self.raw_deleted_at)
            if deleted < _parse_timestamp("created_at", self.created_at):
                raise TraceIntegrityError("raw deletion cannot precede trace creation")
            if type(self.raw_deletion_reason) is not RawDeletionReason:
                raise TraceFieldError("raw tombstone requires a deletion reason")

    @classmethod
    def create(
        cls,
        *,
        policy: TracePolicy,
        project_id: CanonicalId,
        conversation_id: CanonicalId,
        turn_id: CanonicalId,
        slice_kind: TraceSliceKind,
        created_at: datetime,
        recipe_id: RecipeId | None = None,
        parent_trace_ids: tuple[CanonicalId, ...] = (),
        specialist_id: CanonicalId | None = None,
        specialist_mode: str | None = None,
        base_model_hash: Sha256Digest | None = None,
        adapter_hash: Sha256Digest | None = None,
        aae_contract_hash: Sha256Digest | None = None,
        schema_hash: Sha256Digest | None = None,
        inference_profile_hash: Sha256Digest | None = None,
        runtime_identity_hash: Sha256Digest | None = None,
        runtime_epoch: int = 0,
        validation_standing: ValidationStanding = ValidationStanding.NOT_APPLICABLE,
        repair_count: int = 0,
        first_pass_standing: FirstPassStanding = FirstPassStanding.NOT_APPLICABLE,
        telemetry: TraceTelemetry | None = None,
        references: tuple[TraceReference, ...] = (),
        raw_trace_id: CanonicalId | None = None,
        raw_payload_hash: Sha256Digest | None = None,
        held_out: bool = False,
    ) -> TraceIndexRecord:
        if type(policy) is not TracePolicy:
            raise TraceFieldError("policy must be a TracePolicy")
        if type(held_out) is not bool:
            raise TraceFieldError("held_out must be a boolean")
        if type(parent_trace_ids) is not tuple:
            raise TraceFieldError("parent_trace_ids must be an immutable tuple")
        if type(references) is not tuple:
            raise TraceFieldError("references must be an immutable tuple")
        timestamp = canonical_utc_timestamp(created_at)
        if (raw_trace_id is None) != (raw_payload_hash is None):
            raise TraceFieldError("raw trace UUID and payload hash must be supplied together")
        if raw_trace_id is not None:
            if not policy.raw_trace_enabled:
                raise TraceFieldError("frozen policy does not permit raw trace capture")
            deadline = canonical_utc_timestamp(
                created_at + timedelta(days=policy.raw_trace_retention_days)
            )
            raw_state = RawDeletionState.AVAILABLE
        else:
            deadline = None
            raw_state = RawDeletionState.NOT_CAPTURED
        return cls(
            trace_id=CanonicalId.new(),
            project_id=project_id,
            conversation_id=conversation_id,
            turn_id=turn_id,
            revision=1,
            slice_kind=slice_kind,
            recipe_id=recipe_id,
            parent_trace_ids=tuple(sorted(parent_trace_ids)),
            specialist_id=specialist_id,
            specialist_mode=specialist_mode,
            base_model_hash=base_model_hash,
            adapter_hash=adapter_hash,
            aae_contract_hash=aae_contract_hash,
            schema_hash=schema_hash,
            inference_profile_hash=inference_profile_hash,
            runtime_identity_hash=runtime_identity_hash,
            runtime_epoch=runtime_epoch,
            validation_standing=validation_standing,
            repair_count=repair_count,
            first_pass_standing=first_pass_standing,
            telemetry=TraceTelemetry() if telemetry is None else telemetry,
            references=tuple(
                sorted(references, key=lambda ref: (ref.kind.value, str(ref.target_id)))
            ),
            created_at=timestamp,
            policy_hash=policy.policy_hash,
            raw_trace_id=raw_trace_id,
            raw_payload_hash=raw_payload_hash,
            raw_retention_expires_at=deadline,
            raw_pinned=False,
            raw_deletion_state=raw_state,
            raw_deleted_at=None,
            raw_deletion_reason=None,
            training_state=(TrainingState.NEVER_TRAIN if held_out else TrainingState.NOT_SELECTED),
        )

    @property
    def raw_trace_available(self) -> bool:
        return self.raw_deletion_state is RawDeletionState.AVAILABLE

    @property
    def record_hash(self) -> Sha256Digest:
        return sha256_canonical_json(self.to_value())

    def retention_due(self, now: datetime) -> bool:
        timestamp = _parse_timestamp("now", canonical_utc_timestamp(now))
        if not self.raw_trace_available or self.raw_pinned:
            return False
        assert self.raw_retention_expires_at is not None
        return timestamp >= _parse_timestamp(
            "raw_retention_expires_at", self.raw_retention_expires_at
        )

    def to_value(self) -> dict[str, JsonValue]:
        return {
            "aae_contract_hash": None if self.aae_contract_hash is None else self.aae_contract_hash.value,
            "adapter_hash": None if self.adapter_hash is None else self.adapter_hash.value,
            "base_model_hash": None if self.base_model_hash is None else self.base_model_hash.value,
            "conversation_uuid": str(self.conversation_id),
            "created_at": self.created_at,
            "first_pass_standing": self.first_pass_standing.value,
            "inference_profile_hash": None if self.inference_profile_hash is None else self.inference_profile_hash.value,
            "parent_trace_uuids": [str(parent) for parent in self.parent_trace_ids],
            "policy_hash": self.policy_hash.value,
            "project_uuid": str(self.project_id),
            "raw_deleted_at": self.raw_deleted_at,
            "raw_deletion_reason": None if self.raw_deletion_reason is None else self.raw_deletion_reason.value,
            "raw_deletion_state": self.raw_deletion_state.value,
            "raw_payload_hash": None if self.raw_payload_hash is None else self.raw_payload_hash.value,
            "raw_pinned": self.raw_pinned,
            "raw_retention_expires_at": self.raw_retention_expires_at,
            "raw_trace_available": self.raw_trace_available,
            "raw_trace_uuid": None if self.raw_trace_id is None else str(self.raw_trace_id),
            "recipe_id": None if self.recipe_id is None else self.recipe_id.value,
            "references": [reference.to_value() for reference in self.references],
            "repair_count": self.repair_count,
            "revision": self.revision,
            "runtime_epoch": self.runtime_epoch,
            "runtime_identity_hash": None if self.runtime_identity_hash is None else self.runtime_identity_hash.value,
            "schema_hash": None if self.schema_hash is None else self.schema_hash.value,
            "slice_kind": self.slice_kind.value,
            "specialist_mode": self.specialist_mode,
            "specialist_uuid": None if self.specialist_id is None else str(self.specialist_id),
            "telemetry": self.telemetry.to_value(),
            "trace_uuid": str(self.trace_id),
            "trace_version": self.trace_version,
            "training_state": self.training_state.value,
            "turn_uuid": str(self.turn_id),
            "validation_standing": self.validation_standing.value,
        }


@dataclass(frozen=True, slots=True)
class TraceIndexEvent:
    """One hash-chained record revision in the trace index."""

    event_id: CanonicalId
    sequence: int
    event_kind: TraceEventKind
    occurred_at: str
    record: TraceIndexRecord
    previous_event_hash: Sha256Digest | None
    event_hash: Sha256Digest
    trace_version: int = TRACE_INDEX_VERSION

    def __post_init__(self) -> None:
        if type(self.trace_version) is not int or self.trace_version != TRACE_INDEX_VERSION:
            raise TraceFieldError("unsupported trace event version")
        if type(self.event_id) is not CanonicalId:
            raise TraceFieldError("event_id must be a CanonicalId")
        _positive("sequence", self.sequence)
        if type(self.event_kind) is not TraceEventKind:
            raise TraceFieldError("event_kind must be a TraceEventKind")
        _parse_timestamp("occurred_at", self.occurred_at)
        if type(self.record) is not TraceIndexRecord:
            raise TraceFieldError("record must be a TraceIndexRecord")
        if self.event_id == self.record.trace_id:
            raise TraceIntegrityError("trace event UUID must differ from trace UUID")
        if self.sequence == 1:
            if self.previous_event_hash is not None:
                raise TraceIntegrityError("first trace event cannot have a predecessor")
        elif type(self.previous_event_hash) is not Sha256Digest:
            raise TraceIntegrityError("later trace events require a predecessor hash")
        if type(self.event_hash) is not Sha256Digest:
            raise TraceFieldError("event_hash must be a Sha256Digest")
        expected = sha256_canonical_json(self._unsigned_value())
        if not _digest_equal(expected, self.event_hash):
            raise TraceIntegrityError("event_hash does not match trace event content")

    @classmethod
    def create(
        cls,
        *,
        sequence: int,
        event_kind: TraceEventKind,
        occurred_at: datetime,
        record: TraceIndexRecord,
        previous_event_hash: Sha256Digest | None,
    ) -> TraceIndexEvent:
        event_id = CanonicalId.new()
        timestamp = canonical_utc_timestamp(occurred_at)
        unsigned = _trace_event_value(
            event_id=event_id,
            sequence=sequence,
            event_kind=event_kind,
            occurred_at=timestamp,
            record=record,
            previous_event_hash=previous_event_hash,
        )
        return cls(
            event_id=event_id,
            sequence=sequence,
            event_kind=event_kind,
            occurred_at=timestamp,
            record=record,
            previous_event_hash=previous_event_hash,
            event_hash=sha256_canonical_json(unsigned),
        )

    def _unsigned_value(self) -> dict[str, JsonValue]:
        return _trace_event_value(
            event_id=self.event_id,
            sequence=self.sequence,
            event_kind=self.event_kind,
            occurred_at=self.occurred_at,
            record=self.record,
            previous_event_hash=self.previous_event_hash,
        )

    def to_value(self) -> dict[str, JsonValue]:
        return {**self._unsigned_value(), "event_hash": self.event_hash.value}


def _trace_event_value(
    *,
    event_id: CanonicalId,
    sequence: int,
    event_kind: TraceEventKind,
    occurred_at: str,
    record: TraceIndexRecord,
    previous_event_hash: Sha256Digest | None,
) -> dict[str, JsonValue]:
    return {
        "event_kind": event_kind.value,
        "event_uuid": str(event_id),
        "occurred_at": occurred_at,
        "previous_event_hash": None if previous_event_hash is None else previous_event_hash.value,
        "record": record.to_value(),
        "record_hash": record.record_hash.value,
        "sequence": sequence,
        "trace_version": TRACE_INDEX_VERSION,
    }


@dataclass(frozen=True, slots=True)
class TraceIndex:
    """Append-only low-content trace index with replayed current records."""

    policy: TracePolicy
    events: tuple[TraceIndexEvent, ...] = ()

    def __post_init__(self) -> None:
        if type(self.policy) is not TracePolicy:
            raise TraceFieldError("policy must be a TracePolicy")
        if type(self.events) is not tuple:
            raise TraceFieldError("events must be an immutable tuple")
        self._replay()

    @classmethod
    def create(cls, policy: TracePolicy) -> TraceIndex:
        return cls(policy=policy)

    @property
    def head_hash(self) -> Sha256Digest | None:
        return None if not self.events else self.events[-1].event_hash

    def current_records(self) -> dict[CanonicalId, TraceIndexRecord]:
        return self._replay()

    def get(self, trace_id: CanonicalId) -> TraceIndexRecord:
        if type(trace_id) is not CanonicalId:
            raise TraceFieldError("trace_id must be a CanonicalId")
        try:
            return self.current_records()[trace_id]
        except KeyError as exc:
            raise TraceFieldError("unknown trace UUID") from exc

    def register(
        self,
        *,
        record: TraceIndexRecord,
        occurred_at: datetime,
        expected_head: Sha256Digest | None,
    ) -> tuple[TraceIndex, TraceIndexEvent]:
        if not self.policy.enabled:
            raise TraceDisabledError("trace policy disables index registration")
        if type(record) is not TraceIndexRecord:
            raise TraceFieldError("record must be a TraceIndexRecord")
        if record.revision != 1:
            raise TraceIntegrityError("new trace registration must start at revision one")
        if not _digest_equal(record.policy_hash, self.policy.policy_hash):
            raise TraceIntegrityError("record uses a different trace policy")
        records = self.current_records()
        if record.trace_id in records:
            raise TraceIntegrityError("trace UUID is already registered")
        self._validate_registration_lineage(record, records)
        return self._append(
            event_kind=TraceEventKind.REGISTERED,
            record=record,
            occurred_at=occurred_at,
            expected_head=expected_head,
        )

    def pin_raw(
        self,
        *,
        trace_id: CanonicalId,
        expected_revision: int,
        occurred_at: datetime,
        expected_head: Sha256Digest | None,
    ) -> tuple[TraceIndex, TraceIndexEvent]:
        current = self._current_for_update(trace_id, expected_revision)
        if not current.raw_trace_available:
            raise TraceIntegrityError("only an available raw trace can be pinned")
        if current.raw_pinned:
            raise TraceIntegrityError("raw trace is already pinned")
        updated = replace(current, revision=current.revision + 1, raw_pinned=True)
        return self._append(
            event_kind=TraceEventKind.PINNED,
            record=updated,
            occurred_at=occurred_at,
            expected_head=expected_head,
        )

    def unpin_raw(
        self,
        *,
        trace_id: CanonicalId,
        expected_revision: int,
        occurred_at: datetime,
        expected_head: Sha256Digest | None,
    ) -> tuple[TraceIndex, TraceIndexEvent]:
        current = self._current_for_update(trace_id, expected_revision)
        if not current.raw_trace_available or not current.raw_pinned:
            raise TraceIntegrityError("only a pinned available raw trace can be unpinned")
        updated = replace(current, revision=current.revision + 1, raw_pinned=False)
        return self._append(
            event_kind=TraceEventKind.UNPINNED,
            record=updated,
            occurred_at=occurred_at,
            expected_head=expected_head,
        )

    def confirm_raw_deleted(
        self,
        *,
        trace_id: CanonicalId,
        raw_trace_id: CanonicalId,
        expected_revision: int,
        reason: RawDeletionReason,
        occurred_at: datetime,
        expected_head: Sha256Digest | None,
    ) -> tuple[TraceIndex, TraceIndexEvent]:
        """Record a tombstone only after the secure payload store confirms deletion."""

        current = self._current_for_update(trace_id, expected_revision)
        if type(reason) is not RawDeletionReason:
            raise TraceFieldError("reason must be a RawDeletionReason")
        if not current.raw_trace_available or current.raw_trace_id != raw_trace_id:
            raise TraceIntegrityError("raw deletion confirmation does not match a live raw trace")
        if reason is RawDeletionReason.RETENTION_EXPIRED:
            if current.raw_pinned:
                raise TraceIntegrityError("pinned raw trace cannot expire")
            if not current.retention_due(occurred_at):
                raise TraceIntegrityError("raw retention deadline has not elapsed")
        updated = replace(
            current,
            revision=current.revision + 1,
            raw_trace_id=None,
            raw_retention_expires_at=None,
            raw_pinned=False,
            raw_deletion_state=RawDeletionState.TOMBSTONED,
            raw_deleted_at=canonical_utc_timestamp(occurred_at),
            raw_deletion_reason=reason,
        )
        return self._append(
            event_kind=TraceEventKind.RAW_DELETION_CONFIRMED,
            record=updated,
            occurred_at=occurred_at,
            expected_head=expected_head,
        )

    def due_for_expiry(self, now: datetime) -> tuple[CanonicalId, ...]:
        due = [record.trace_id for record in self.current_records().values() if record.retention_due(now)]
        return tuple(sorted(due))

    def _current_for_update(
        self, trace_id: CanonicalId, expected_revision: int
    ) -> TraceIndexRecord:
        current = self.get(trace_id)
        if type(expected_revision) is not int or current.revision != expected_revision:
            raise TraceConflictError("expected trace revision does not match current revision")
        return current

    def _append(
        self,
        *,
        event_kind: TraceEventKind,
        record: TraceIndexRecord,
        occurred_at: datetime,
        expected_head: Sha256Digest | None,
    ) -> tuple[TraceIndex, TraceIndexEvent]:
        self._require_head(expected_head)
        event = TraceIndexEvent.create(
            sequence=len(self.events) + 1,
            event_kind=event_kind,
            occurred_at=occurred_at,
            record=record,
            previous_event_hash=self.head_hash,
        )
        advanced = TraceIndex(policy=self.policy, events=(*self.events, event))
        return advanced, event

    def _validate_registration_lineage(
        self,
        record: TraceIndexRecord,
        records: dict[CanonicalId, TraceIndexRecord],
    ) -> None:
        for parent_id in record.parent_trace_ids:
            parent = records.get(parent_id)
            if parent is None:
                raise TraceIntegrityError("parent trace UUID is not registered")
            if parent.project_id != record.project_id:
                raise TraceIntegrityError("parent trace belongs to a different project")
        if record.slice_kind is TraceSliceKind.REENTRY_SLICE and not record.parent_trace_ids:
            raise TraceIntegrityError("re-entry trace requires registered parent lineage")
        if record.slice_kind is TraceSliceKind.CROSS_TURN_LINEAGE:
            if any(
                records[parent].conversation_id != record.conversation_id
                for parent in record.parent_trace_ids
            ):
                raise TraceIntegrityError(
                    "cross-turn lineage parent belongs to a different conversation"
                )
            if not any(records[parent].turn_id != record.turn_id for parent in record.parent_trace_ids):
                raise TraceIntegrityError("cross-turn lineage requires a parent from another turn")
        if record.slice_kind is TraceSliceKind.REPAIR_ATTEMPT:
            call_ids = {
                reference.target_id
                for reference in record.references
                if reference.kind is TraceReferenceKind.CALL
            }
            registered_calls = {
                reference.target_id
                for prior in records.values()
                if prior.slice_kind is TraceSliceKind.LEARNED_CALL
                and prior.project_id == record.project_id
                and prior.turn_id == record.turn_id
                for reference in prior.references
                if reference.kind is TraceReferenceKind.CALL
            }
            if not call_ids.issubset(registered_calls):
                raise TraceIntegrityError("repair trace call has no registered learned-call trace")

    def _require_head(self, expected: Sha256Digest | None) -> None:
        actual = self.head_hash
        if actual is None:
            if expected is not None:
                raise TraceConflictError("empty trace index requires expected_head=None")
            return
        if type(expected) is not Sha256Digest or not _digest_equal(actual, expected):
            raise TraceConflictError("expected trace-index head does not match current head")

    def _replay(self) -> dict[CanonicalId, TraceIndexRecord]:
        records: dict[CanonicalId, TraceIndexRecord] = {}
        event_ids: set[CanonicalId] = set()
        previous_hash: Sha256Digest | None = None
        previous_time: datetime | None = None
        for sequence, event in enumerate(self.events, start=1):
            if type(event) is not TraceIndexEvent:
                raise TraceFieldError("every index event must be a TraceIndexEvent")
            if event.sequence != sequence:
                raise TraceIntegrityError("trace event sequences must be contiguous from one")
            if event.event_id in event_ids:
                raise TraceIntegrityError("trace event UUIDs must be unique")
            event_ids.add(event.event_id)
            if event.previous_event_hash != previous_hash:
                raise TraceIntegrityError("trace event predecessor chain is broken")
            event_time = _parse_timestamp("occurred_at", event.occurred_at)
            if event_time < _parse_timestamp("record created_at", event.record.created_at):
                raise TraceIntegrityError("trace event cannot precede trace creation")
            if previous_time is not None and event_time < previous_time:
                raise TraceIntegrityError("trace event timestamps must be nondecreasing")
            if not _digest_equal(event.record.policy_hash, self.policy.policy_hash):
                raise TraceIntegrityError("trace event record uses a different policy")
            prior = records.get(event.record.trace_id)
            if event.event_kind is TraceEventKind.REGISTERED:
                self._validate_registration_lineage(event.record, records)
            self._validate_transition(event, prior)
            records[event.record.trace_id] = event.record
            previous_hash = event.event_hash
            previous_time = event_time
        return records

    def _validate_transition(
        self, event: TraceIndexEvent, prior: TraceIndexRecord | None
    ) -> None:
        current = event.record
        if event.event_kind is TraceEventKind.REGISTERED:
            if prior is not None or current.revision != 1:
                raise TraceIntegrityError("REGISTERED must create revision one exactly once")
            return
        if prior is None or current.revision != prior.revision + 1:
            raise TraceIntegrityError("trace lifecycle revisions must be contiguous")
        before = prior.to_value()
        after = current.to_value()
        allowed = {
            TraceEventKind.PINNED: {"revision", "raw_pinned"},
            TraceEventKind.UNPINNED: {"revision", "raw_pinned"},
            TraceEventKind.RAW_DELETION_CONFIRMED: {
                "revision",
                "raw_trace_uuid",
                "raw_trace_available",
                "raw_retention_expires_at",
                "raw_pinned",
                "raw_deletion_state",
                "raw_deleted_at",
                "raw_deletion_reason",
            },
        }[event.event_kind]
        changed = {key for key in before if before[key] != after[key]}
        required = (
            {
                "revision",
                "raw_trace_uuid",
                "raw_trace_available",
                "raw_retention_expires_at",
                "raw_deletion_state",
                "raw_deleted_at",
                "raw_deletion_reason",
            }
            if event.event_kind is TraceEventKind.RAW_DELETION_CONFIRMED
            else allowed
        )
        if not required.issubset(changed) or not changed.issubset(allowed):
            raise TraceIntegrityError("trace lifecycle event changed unauthorized metadata")
        if event.event_kind is TraceEventKind.PINNED and (prior.raw_pinned or not current.raw_pinned):
            raise TraceIntegrityError("invalid PINNED transition")
        if event.event_kind is TraceEventKind.UNPINNED and (
            not prior.raw_pinned or current.raw_pinned
        ):
            raise TraceIntegrityError("invalid UNPINNED transition")
        if event.event_kind is TraceEventKind.RAW_DELETION_CONFIRMED and (
            not prior.raw_trace_available
            or current.raw_deletion_state is not RawDeletionState.TOMBSTONED
        ):
            raise TraceIntegrityError("invalid raw deletion transition")
        if (
            event.event_kind is TraceEventKind.RAW_DELETION_CONFIRMED
            and current.raw_deletion_reason is RawDeletionReason.RETENTION_EXPIRED
            and (
                prior.raw_pinned
                or not prior.retention_due(
                    _parse_timestamp("occurred_at", event.occurred_at)
                )
            )
        ):
            raise TraceIntegrityError("invalid retention-expiry tombstone timing")

    def to_value(self) -> dict[str, JsonValue]:
        records = self.current_records()
        return {
            "current_records": [records[key].to_value() for key in sorted(records)],
            "event_count": len(self.events),
            "events": [event.to_value() for event in self.events],
            "head_hash": None if self.head_hash is None else self.head_hash.value,
            "policy": self.policy.to_value(),
            "policy_hash": self.policy.policy_hash.value,
            "trace_version": TRACE_INDEX_VERSION,
        }

    def to_json(self) -> str:
        return canonical_json_dumps(self.to_value())
