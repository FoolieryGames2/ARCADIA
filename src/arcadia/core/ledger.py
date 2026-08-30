"""Immutable additive technical turn ledger with hash-chained replay."""

from __future__ import annotations

import hmac
from dataclasses import dataclass
from datetime import datetime
from typing import Final, cast

from arcadia.core.artifact_envelope import (
    ArtifactEnvelope,
    ArtifactEnvelopeError,
    ArtifactIntegrityError,
    canonical_utc_timestamp,
)
from arcadia.core.canonical_json import (
    JsonValue,
    canonical_json_dumps,
    require_canonical_json,
    strict_json_loads_bytes,
)
from arcadia.core.hashing import Sha256Digest, parse_sha256_digest, sha256_canonical_json
from arcadia.core.ids import CanonicalId

TECHNICAL_LEDGER_VERSION = 1

_ENTRY_FIELDS: Final = frozenset(
    {
        "ledger_version",
        "entry_uuid",
        "project_uuid",
        "turn_uuid",
        "sequence",
        "appended_at",
        "previous_entry_hash",
        "artifact",
        "entry_hash",
    }
)
_LEDGER_FIELDS: Final = frozenset(
    {
        "ledger_version",
        "project_uuid",
        "turn_uuid",
        "entry_count",
        "head_hash",
        "entries",
    }
)


class LedgerError(ValueError):
    """Base error for invalid technical-ledger state."""


class LedgerFieldError(LedgerError):
    """A ledger field is missing, unknown, malformed, or out of scope."""


class LedgerIntegrityError(LedgerError):
    """A ledger entry, chain link, ordering rule, or snapshot does not verify."""


class LedgerConflictError(LedgerError):
    """An append was attempted against a stale or unacknowledged ledger head."""


def _exact_positive_int(name: str, value: object) -> int:
    if type(value) is not int or value < 1:
        raise LedgerFieldError(f"{name} must be a positive integer")
    return value


def _exact_nonnegative_int(name: str, value: object) -> int:
    if type(value) is not int or value < 0:
        raise LedgerFieldError(f"{name} must be a nonnegative integer")
    return value


def _object(name: str, value: object) -> dict[str, JsonValue]:
    if type(value) is not dict:
        raise LedgerFieldError(f"{name} must be a JSON object")
    if any(type(key) is not str for key in value):
        raise LedgerFieldError(f"{name} field names must be strings")
    return cast(dict[str, JsonValue], value)


def _array(name: str, value: object) -> list[JsonValue]:
    if type(value) is not list:
        raise LedgerFieldError(f"{name} must be a JSON array")
    return cast(list[JsonValue], value)


def _exact_fields(
    name: str, value: dict[str, JsonValue], expected: frozenset[str]
) -> None:
    actual = frozenset(value)
    if actual == expected:
        return
    missing = sorted(expected - actual)
    unknown = sorted(actual - expected)
    details: list[str] = []
    if missing:
        details.append(f"missing={missing}")
    if unknown:
        details.append(f"unknown={unknown}")
    raise LedgerFieldError(f"{name} fields do not match V1: {', '.join(details)}")


def _parse_timestamp(value: object) -> str:
    if type(value) is not str:
        raise LedgerFieldError("appended_at must be canonical UTC text")
    try:
        parsed = datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ")
    except ValueError as exc:
        raise LedgerFieldError(
            "appended_at must use a real YYYY-MM-DDTHH:MM:SS.ffffffZ timestamp"
        ) from exc
    if parsed.strftime("%Y-%m-%dT%H:%M:%S.%fZ") != value:
        raise LedgerFieldError("appended_at is not in the canonical UTC form")
    return value


def _timestamp_key(value: str) -> datetime:
    return datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ")


def _digest_equal(left: Sha256Digest, right: Sha256Digest) -> bool:
    return hmac.compare_digest(left.value, right.value)


@dataclass(frozen=True, slots=True)
class LedgerEntry:
    """One immutable append linking a complete artifact into a turn chain."""

    entry_id: CanonicalId
    project_id: CanonicalId
    turn_id: CanonicalId
    sequence: int
    appended_at: str
    previous_entry_hash: Sha256Digest | None
    artifact: ArtifactEnvelope
    entry_hash: Sha256Digest
    ledger_version: int = TECHNICAL_LEDGER_VERSION

    def __post_init__(self) -> None:
        if type(self.ledger_version) is not int or self.ledger_version != TECHNICAL_LEDGER_VERSION:
            raise LedgerFieldError("unsupported technical ledger version")
        for name, identity in (
            ("entry_id", self.entry_id),
            ("project_id", self.project_id),
            ("turn_id", self.turn_id),
        ):
            if type(identity) is not CanonicalId:
                raise LedgerFieldError(f"{name} must be a CanonicalId")
        _exact_positive_int("sequence", self.sequence)
        _parse_timestamp(self.appended_at)
        if self.sequence == 1:
            if self.previous_entry_hash is not None:
                raise LedgerIntegrityError("the first ledger entry cannot have a predecessor")
        elif type(self.previous_entry_hash) is not Sha256Digest:
            raise LedgerIntegrityError("a non-root ledger entry requires a typed predecessor hash")
        if type(self.artifact) is not ArtifactEnvelope:
            raise LedgerFieldError("artifact must be a verified ArtifactEnvelope")
        if self.artifact.project_id != self.project_id or self.artifact.turn_id != self.turn_id:
            raise LedgerFieldError("artifact project/turn scope does not match ledger entry")
        if _timestamp_key(self.appended_at) < _timestamp_key(self.artifact.created_at):
            raise LedgerIntegrityError("an artifact cannot be appended before it was created")
        if type(self.entry_hash) is not Sha256Digest:
            raise LedgerFieldError("entry_hash must be a Sha256Digest")
        expected = sha256_canonical_json(self._unsigned_value())
        if not _digest_equal(expected, self.entry_hash):
            raise LedgerIntegrityError("entry_hash does not match ledger entry content")

    @classmethod
    def create(
        cls,
        *,
        project_id: CanonicalId,
        turn_id: CanonicalId,
        sequence: int,
        appended_at: datetime,
        previous_entry_hash: Sha256Digest | None,
        artifact: ArtifactEnvelope,
    ) -> LedgerEntry:
        """Allocate an entry UUID and seal one append."""

        entry_id = CanonicalId.new()
        timestamp = canonical_utc_timestamp(appended_at)
        unsigned = _entry_unsigned_value(
            entry_id=entry_id,
            project_id=project_id,
            turn_id=turn_id,
            sequence=sequence,
            appended_at=timestamp,
            previous_entry_hash=previous_entry_hash,
            artifact=artifact,
        )
        return cls(
            entry_id=entry_id,
            project_id=project_id,
            turn_id=turn_id,
            sequence=sequence,
            appended_at=timestamp,
            previous_entry_hash=previous_entry_hash,
            artifact=artifact,
            entry_hash=sha256_canonical_json(unsigned),
        )

    def _unsigned_value(self) -> dict[str, JsonValue]:
        return _entry_unsigned_value(
            entry_id=self.entry_id,
            project_id=self.project_id,
            turn_id=self.turn_id,
            sequence=self.sequence,
            appended_at=self.appended_at,
            previous_entry_hash=self.previous_entry_hash,
            artifact=self.artifact,
        )

    def to_value(self) -> dict[str, JsonValue]:
        value = self._unsigned_value()
        value["entry_hash"] = self.entry_hash.value
        return value

    @classmethod
    def from_value(cls, value: object) -> LedgerEntry:
        parsed = _object("ledger entry", value)
        _exact_fields("ledger entry", parsed, _ENTRY_FIELDS)
        if (
            type(parsed["ledger_version"]) is not int
            or parsed["ledger_version"] != TECHNICAL_LEDGER_VERSION
        ):
            raise LedgerFieldError("unsupported technical ledger version")
        try:
            entry_id = CanonicalId.parse(cast(str, parsed["entry_uuid"]))
            project_id = CanonicalId.parse(cast(str, parsed["project_uuid"]))
            turn_id = CanonicalId.parse(cast(str, parsed["turn_uuid"]))
            entry_hash = parse_sha256_digest(cast(str, parsed["entry_hash"]))
            previous_value = parsed["previous_entry_hash"]
            previous_hash = (
                None
                if previous_value is None
                else parse_sha256_digest(cast(str, previous_value))
            )
            artifact = ArtifactEnvelope.from_value(parsed["artifact"])
        except LedgerError:
            raise
        except ArtifactIntegrityError as exc:
            raise LedgerIntegrityError(f"embedded artifact integrity failure: {exc}") from exc
        except ArtifactEnvelopeError as exc:
            raise LedgerFieldError(f"embedded artifact is invalid: {exc}") from exc
        except ValueError as exc:
            raise LedgerFieldError("ledger entry contains an invalid identity") from exc
        try:
            return cls(
                entry_id=entry_id,
                project_id=project_id,
                turn_id=turn_id,
                sequence=_exact_positive_int("sequence", parsed["sequence"]),
                appended_at=_parse_timestamp(parsed["appended_at"]),
                previous_entry_hash=previous_hash,
                artifact=artifact,
                entry_hash=entry_hash,
            )
        except LedgerError:
            raise
        except ValueError as exc:
            raise LedgerFieldError("ledger entry is invalid") from exc


def _entry_unsigned_value(
    *,
    entry_id: CanonicalId,
    project_id: CanonicalId,
    turn_id: CanonicalId,
    sequence: int,
    appended_at: str,
    previous_entry_hash: Sha256Digest | None,
    artifact: ArtifactEnvelope,
) -> dict[str, JsonValue]:
    return {
        "ledger_version": TECHNICAL_LEDGER_VERSION,
        "entry_uuid": str(entry_id),
        "project_uuid": str(project_id),
        "turn_uuid": str(turn_id),
        "sequence": sequence,
        "appended_at": appended_at,
        "previous_entry_hash": (
            None if previous_entry_hash is None else previous_entry_hash.value
        ),
        "artifact": artifact.to_value(),
    }


@dataclass(frozen=True, slots=True)
class TechnicalTurnLedger:
    """An immutable additive snapshot of one turn's technical artifacts."""

    project_id: CanonicalId
    turn_id: CanonicalId
    entries: tuple[LedgerEntry, ...] = ()
    ledger_version: int = TECHNICAL_LEDGER_VERSION

    def __post_init__(self) -> None:
        if type(self.ledger_version) is not int or self.ledger_version != TECHNICAL_LEDGER_VERSION:
            raise LedgerFieldError("unsupported technical ledger version")
        if type(self.project_id) is not CanonicalId or type(self.turn_id) is not CanonicalId:
            raise LedgerFieldError("ledger project_id and turn_id must be CanonicalId values")
        if type(self.entries) is not tuple or any(type(entry) is not LedgerEntry for entry in self.entries):
            raise LedgerFieldError("entries must be a tuple of LedgerEntry values")
        self._verify_chain()

    @classmethod
    def empty(cls, *, project_id: CanonicalId, turn_id: CanonicalId) -> TechnicalTurnLedger:
        return cls(project_id=project_id, turn_id=turn_id)

    @property
    def head_hash(self) -> Sha256Digest | None:
        return None if not self.entries else self.entries[-1].entry_hash

    def _verify_chain(self) -> None:
        prior_hash: Sha256Digest | None = None
        prior_time: datetime | None = None
        entry_ids: set[CanonicalId] = set()
        artifact_revisions: set[tuple[CanonicalId, int]] = set()
        latest_revision: dict[CanonicalId, int] = {}
        for expected_sequence, entry in enumerate(self.entries, start=1):
            if entry.project_id != self.project_id or entry.turn_id != self.turn_id:
                raise LedgerIntegrityError("ledger entry crosses project or turn scope")
            if entry.sequence != expected_sequence:
                raise LedgerIntegrityError("ledger sequences must be contiguous and ordered")
            if entry.previous_entry_hash != prior_hash:
                raise LedgerIntegrityError("ledger predecessor hash chain is broken")
            if entry.entry_id in entry_ids:
                raise LedgerIntegrityError("ledger entry UUIDs must be unique")
            entry_ids.add(entry.entry_id)
            artifact_key = (entry.artifact.artifact_id, entry.artifact.revision)
            if artifact_key in artifact_revisions:
                raise LedgerIntegrityError("artifact UUID/revision was appended more than once")
            artifact_revisions.add(artifact_key)
            previous_revision = latest_revision.get(entry.artifact.artifact_id)
            if previous_revision is not None and entry.artifact.revision <= previous_revision:
                raise LedgerIntegrityError("artifact revisions must increase without erasing history")
            latest_revision[entry.artifact.artifact_id] = entry.artifact.revision
            current_time = _timestamp_key(entry.appended_at)
            if prior_time is not None and current_time < prior_time:
                raise LedgerIntegrityError("ledger append timestamps must be nondecreasing")
            prior_time = current_time
            prior_hash = entry.entry_hash

    def append(
        self,
        artifact: ArtifactEnvelope,
        *,
        appended_at: datetime,
        expected_head_hash: Sha256Digest | None,
    ) -> TechnicalTurnLedger:
        """Return a new snapshot after an optimistic, scope-checked append."""

        actual_head = self.head_hash
        if actual_head is None:
            if expected_head_hash is not None:
                raise LedgerConflictError("empty ledger append expected a nonexistent head")
        elif type(expected_head_hash) is not Sha256Digest or not _digest_equal(
            actual_head, expected_head_hash
        ):
            raise LedgerConflictError("ledger head changed before append")
        if type(artifact) is not ArtifactEnvelope:
            raise LedgerFieldError("append requires a verified ArtifactEnvelope")
        if artifact.project_id != self.project_id or artifact.turn_id != self.turn_id:
            raise LedgerFieldError("artifact crosses the ledger project/turn boundary")
        timestamp = canonical_utc_timestamp(appended_at)
        if self.entries and _timestamp_key(timestamp) < _timestamp_key(self.entries[-1].appended_at):
            raise LedgerIntegrityError("append timestamp cannot move backward")
        artifact_key = (artifact.artifact_id, artifact.revision)
        if any(
            (entry.artifact.artifact_id, entry.artifact.revision) == artifact_key
            for entry in self.entries
        ):
            raise LedgerIntegrityError("artifact UUID/revision is already present")
        prior_revisions = [
            entry.artifact.revision
            for entry in self.entries
            if entry.artifact.artifact_id == artifact.artifact_id
        ]
        if prior_revisions and artifact.revision <= max(prior_revisions):
            raise LedgerIntegrityError("artifact revision does not advance history")
        entry = LedgerEntry.create(
            project_id=self.project_id,
            turn_id=self.turn_id,
            sequence=len(self.entries) + 1,
            appended_at=appended_at,
            previous_entry_hash=actual_head,
            artifact=artifact,
        )
        return TechnicalTurnLedger(
            project_id=self.project_id,
            turn_id=self.turn_id,
            entries=(*self.entries, entry),
        )

    def to_value(self) -> dict[str, JsonValue]:
        return {
            "ledger_version": TECHNICAL_LEDGER_VERSION,
            "project_uuid": str(self.project_id),
            "turn_uuid": str(self.turn_id),
            "entry_count": len(self.entries),
            "head_hash": None if self.head_hash is None else self.head_hash.value,
            "entries": [entry.to_value() for entry in self.entries],
        }

    def to_json(self) -> str:
        return canonical_json_dumps(self.to_value())

    def artifacts(self) -> tuple[ArtifactEnvelope, ...]:
        return tuple(entry.artifact for entry in self.entries)

    def artifact_history(self, artifact_id: CanonicalId) -> tuple[ArtifactEnvelope, ...]:
        if type(artifact_id) is not CanonicalId:
            raise LedgerFieldError("artifact_id must be a CanonicalId")
        return tuple(
            entry.artifact for entry in self.entries if entry.artifact.artifact_id == artifact_id
        )

    @classmethod
    def from_value(cls, value: object) -> TechnicalTurnLedger:
        parsed = _object("technical ledger", value)
        _exact_fields("technical ledger", parsed, _LEDGER_FIELDS)
        if (
            type(parsed["ledger_version"]) is not int
            or parsed["ledger_version"] != TECHNICAL_LEDGER_VERSION
        ):
            raise LedgerFieldError("unsupported technical ledger version")
        try:
            project_id = CanonicalId.parse(cast(str, parsed["project_uuid"]))
            turn_id = CanonicalId.parse(cast(str, parsed["turn_uuid"]))
            entries = tuple(LedgerEntry.from_value(item) for item in _array("entries", parsed["entries"]))
            expected_count = _exact_nonnegative_int("entry_count", parsed["entry_count"])
            head_value = parsed["head_hash"]
            expected_head = None if head_value is None else parse_sha256_digest(cast(str, head_value))
        except LedgerError:
            raise
        except ValueError as exc:
            raise LedgerFieldError("technical ledger contains an invalid identity") from exc
        ledger = cls(project_id=project_id, turn_id=turn_id, entries=entries)
        if expected_count != len(entries):
            raise LedgerIntegrityError("entry_count does not match ledger entries")
        actual_head = ledger.head_hash
        if (actual_head is None) != (expected_head is None) or (
            actual_head is not None
            and expected_head is not None
            and not _digest_equal(actual_head, expected_head)
        ):
            raise LedgerIntegrityError("head_hash does not match the final ledger entry")
        return ledger

    @classmethod
    def from_json(cls, value: str) -> TechnicalTurnLedger:
        try:
            parsed = require_canonical_json(value)
        except ValueError as exc:
            raise LedgerFieldError("ledger text is not Canonical JSON V1") from exc
        return cls.from_value(parsed)

    @classmethod
    def from_bytes(cls, value: bytes) -> TechnicalTurnLedger:
        try:
            parsed = strict_json_loads_bytes(value)
            canonical = canonical_json_dumps(parsed).encode("utf-8")
        except ValueError as exc:
            raise LedgerFieldError("ledger bytes are not strict UTF-8 JSON") from exc
        if canonical != value:
            raise LedgerFieldError("ledger bytes are not Canonical JSON V1")
        return cls.from_value(parsed)
