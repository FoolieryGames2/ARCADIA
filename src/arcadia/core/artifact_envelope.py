"""Immutable, versioned, hash-verifiable technical artifact envelopes."""

from __future__ import annotations

import hmac
import re
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from enum import StrEnum
from typing import Final, cast

from arcadia.core.canonical_json import (
    JsonValue,
    canonical_json_dumps,
    require_canonical_json,
    strict_json_loads_bytes,
)
from arcadia.core.hashing import Sha256Digest, parse_sha256_digest, sha256_canonical_json
from arcadia.core.ids import AliasKind, CanonicalId, ScopedAlias

ARTIFACT_ENVELOPE_VERSION = 1

_ARTIFACT_TYPE_PATTERN: Final = re.compile(r"[A-Z][A-Z0-9_]{0,63}", flags=re.ASCII)
_VERSION_PATTERN: Final = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:+-]{0,127}", flags=re.ASCII)
_UTC_TIMESTAMP_PATTERN: Final = re.compile(
    r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]{6}Z",
    flags=re.ASCII,
)

_ENVELOPE_FIELDS: Final = frozenset(
    {
        "envelope_version",
        "artifact_uuid",
        "project_uuid",
        "turn_uuid",
        "recipe_id",
        "artifact_type",
        "short_id",
        "short_id_kind",
        "revision",
        "project_version",
        "contract_version",
        "schema_version",
        "recipe_version",
        "registry_version",
        "runtime_identity_version",
        "created_at",
        "basis_refs",
        "payload",
        "content_hash",
        "artifact_hash",
    }
)
_BASIS_REF_FIELDS: Final = frozenset({"artifact_uuid", "revision", "artifact_hash"})


class ArtifactEnvelopeError(ValueError):
    """Base error for malformed or inconsistent artifact envelopes."""


class ArtifactEnvelopeFieldError(ArtifactEnvelopeError):
    """An envelope field is missing, unknown, malformed, or inconsistent."""


class ArtifactIntegrityError(ArtifactEnvelopeError):
    """An envelope payload or whole-envelope hash does not verify."""


class RecipeId(StrEnum):
    CONVERSATION_RESOLVER = "R0"
    INTENT = "R1"
    CONTEXT = "R2"
    DECISION = "R3"
    TOOL_EXECUTION = "R4"
    RECONCILIATION = "R5"
    PERSISTENCE = "R6"
    COMPLETION = "R7"
    RESULT = "R8"


def _require_exact_int(name: str, value: object, *, minimum: int = 1) -> int:
    if type(value) is not int or value < minimum:
        raise ArtifactEnvelopeFieldError(f"{name} must be an integer >= {minimum}")
    return value


def _require_token(name: str, value: object, pattern: re.Pattern[str]) -> str:
    if type(value) is not str or pattern.fullmatch(value) is None:
        raise ArtifactEnvelopeFieldError(f"{name} is not a legal canonical token")
    return value


def canonical_utc_timestamp(value: datetime) -> str:
    """Render an aware UTC datetime in the envelope's fixed RFC 3339 profile."""

    if type(value) is not datetime or value.tzinfo is None:
        raise ArtifactEnvelopeFieldError("created_at must be a timezone-aware datetime")
    if value.utcoffset() != timedelta(0):
        raise ArtifactEnvelopeFieldError("created_at must already use UTC")
    normalized = value.astimezone(UTC)
    return normalized.strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def _parse_timestamp(value: object) -> str:
    if type(value) is not str or _UTC_TIMESTAMP_PATTERN.fullmatch(value) is None:
        raise ArtifactEnvelopeFieldError(
            "created_at must use YYYY-MM-DDTHH:MM:SS.ffffffZ"
        )
    try:
        datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ")
    except ValueError as exc:
        raise ArtifactEnvelopeFieldError("created_at is not a real UTC timestamp") from exc
    return value


def _require_object(name: str, value: object) -> dict[str, JsonValue]:
    if type(value) is not dict:
        raise ArtifactEnvelopeFieldError(f"{name} must be a JSON object")
    return cast(dict[str, JsonValue], value)


def _require_array(name: str, value: object) -> list[JsonValue]:
    if type(value) is not list:
        raise ArtifactEnvelopeFieldError(f"{name} must be a JSON array")
    return cast(list[JsonValue], value)


def _require_exact_fields(
    name: str, value: dict[str, JsonValue], expected: frozenset[str]
) -> None:
    if any(type(key) is not str for key in value):
        raise ArtifactEnvelopeFieldError(f"{name} field names must be strings")
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
    raise ArtifactEnvelopeFieldError(f"{name} fields do not match V1: {', '.join(details)}")


@dataclass(frozen=True, slots=True, order=True)
class ArtifactBasisRef:
    """An exact immutable reference to one upstream artifact revision."""

    artifact_id: CanonicalId
    revision: int
    artifact_hash: Sha256Digest

    def __post_init__(self) -> None:
        _require_exact_int("basis ref revision", self.revision)
        if type(self.artifact_id) is not CanonicalId:
            raise ArtifactEnvelopeFieldError("basis ref artifact_id must be a CanonicalId")
        if type(self.artifact_hash) is not Sha256Digest:
            raise ArtifactEnvelopeFieldError("basis ref artifact_hash must be a Sha256Digest")

    def to_value(self) -> dict[str, JsonValue]:
        return {
            "artifact_uuid": str(self.artifact_id),
            "revision": self.revision,
            "artifact_hash": self.artifact_hash.value,
        }

    @classmethod
    def from_value(cls, value: object) -> ArtifactBasisRef:
        parsed = _require_object("basis ref", value)
        _require_exact_fields("basis ref", parsed, _BASIS_REF_FIELDS)
        try:
            return cls(
                artifact_id=CanonicalId.parse(cast(str, parsed["artifact_uuid"])),
                revision=_require_exact_int("basis ref revision", parsed["revision"]),
                artifact_hash=parse_sha256_digest(cast(str, parsed["artifact_hash"])),
            )
        except ArtifactEnvelopeError:
            raise
        except (TypeError, ValueError) as exc:
            raise ArtifactEnvelopeFieldError("basis ref contains an invalid identity") from exc


def _alias_wire_fields(alias: ScopedAlias | None) -> tuple[JsonValue, JsonValue]:
    if alias is None:
        return None, None
    return alias.text, alias.kind.value


def _unsigned_value(
    *,
    artifact_id: CanonicalId,
    project_id: CanonicalId,
    turn_id: CanonicalId,
    recipe_id: RecipeId,
    artifact_type: str,
    short_id: ScopedAlias | None,
    revision: int,
    project_version: str,
    contract_version: str,
    schema_version: str,
    recipe_version: str,
    registry_version: str,
    runtime_identity_version: str,
    created_at: str,
    basis_refs: tuple[ArtifactBasisRef, ...],
    payload: JsonValue,
    content_hash: Sha256Digest,
) -> dict[str, JsonValue]:
    short_id_text, short_id_kind = _alias_wire_fields(short_id)
    return {
        "envelope_version": ARTIFACT_ENVELOPE_VERSION,
        "artifact_uuid": str(artifact_id),
        "project_uuid": str(project_id),
        "turn_uuid": str(turn_id),
        "recipe_id": recipe_id.value,
        "artifact_type": artifact_type,
        "short_id": short_id_text,
        "short_id_kind": short_id_kind,
        "revision": revision,
        "project_version": project_version,
        "contract_version": contract_version,
        "schema_version": schema_version,
        "recipe_version": recipe_version,
        "registry_version": registry_version,
        "runtime_identity_version": runtime_identity_version,
        "created_at": created_at,
        "basis_refs": [basis_ref.to_value() for basis_ref in basis_refs],
        "payload": payload,
        "content_hash": content_hash.value,
    }


def _validate_metadata(
    *,
    artifact_id: object,
    project_id: object,
    turn_id: object,
    recipe_id: object,
    artifact_type: object,
    short_id: object,
    revision: object,
    project_version: object,
    contract_version: object,
    schema_version: object,
    recipe_version: object,
    registry_version: object,
    runtime_identity_version: object,
    created_at: object,
    basis_refs: object,
) -> None:
    for name, identity in (
        ("artifact_id", artifact_id),
        ("project_id", project_id),
        ("turn_id", turn_id),
    ):
        if type(identity) is not CanonicalId:
            raise ArtifactEnvelopeFieldError(f"{name} must be a CanonicalId")
    if type(recipe_id) is not RecipeId:
        raise ArtifactEnvelopeFieldError("recipe_id must be a RecipeId")
    _require_token("artifact_type", artifact_type, _ARTIFACT_TYPE_PATTERN)
    _require_exact_int("revision", revision)
    for name, value in (
        ("project_version", project_version),
        ("contract_version", contract_version),
        ("schema_version", schema_version),
        ("recipe_version", recipe_version),
        ("registry_version", registry_version),
        ("runtime_identity_version", runtime_identity_version),
    ):
        _require_token(name, value, _VERSION_PATTERN)
    _parse_timestamp(created_at)
    if type(basis_refs) is not tuple or any(
        type(ref) is not ArtifactBasisRef for ref in basis_refs
    ):
        raise ArtifactEnvelopeFieldError("basis_refs must be a tuple of ArtifactBasisRef")
    typed_refs = cast(tuple[ArtifactBasisRef, ...], basis_refs)
    if len(set(typed_refs)) != len(typed_refs):
        raise ArtifactEnvelopeFieldError("basis_refs must not contain duplicates")
    if any(ref.artifact_id == artifact_id for ref in typed_refs):
        raise ArtifactEnvelopeFieldError("an artifact cannot cite itself as an upstream basis")
    if short_id is not None:
        if type(short_id) is not ScopedAlias:
            raise ArtifactEnvelopeFieldError("short_id must be a ScopedAlias or None")
        if short_id.scope_id != turn_id:
            raise ArtifactEnvelopeFieldError("technical short_id scope must equal turn_id")


@dataclass(frozen=True, slots=True)
class ArtifactEnvelope:
    """A V1 technical artifact with immutable canonical payload and provenance."""

    artifact_id: CanonicalId
    project_id: CanonicalId
    turn_id: CanonicalId
    recipe_id: RecipeId
    artifact_type: str
    short_id: ScopedAlias | None
    revision: int
    project_version: str
    contract_version: str
    schema_version: str
    recipe_version: str
    registry_version: str
    runtime_identity_version: str
    created_at: str
    basis_refs: tuple[ArtifactBasisRef, ...]
    payload_json: str
    content_hash: Sha256Digest
    artifact_hash: Sha256Digest
    envelope_version: int = ARTIFACT_ENVELOPE_VERSION

    def __post_init__(self) -> None:
        if (
            type(self.envelope_version) is not int
            or self.envelope_version != ARTIFACT_ENVELOPE_VERSION
        ):
            raise ArtifactEnvelopeFieldError("unsupported artifact envelope version")
        _validate_metadata(
            artifact_id=self.artifact_id,
            project_id=self.project_id,
            turn_id=self.turn_id,
            recipe_id=self.recipe_id,
            artifact_type=self.artifact_type,
            short_id=self.short_id,
            revision=self.revision,
            project_version=self.project_version,
            contract_version=self.contract_version,
            schema_version=self.schema_version,
            recipe_version=self.recipe_version,
            registry_version=self.registry_version,
            runtime_identity_version=self.runtime_identity_version,
            created_at=self.created_at,
            basis_refs=self.basis_refs,
        )
        if type(self.payload_json) is not str:
            raise ArtifactEnvelopeFieldError("payload_json must be canonical JSON text")
        try:
            payload = require_canonical_json(self.payload_json)
        except ValueError as exc:
            raise ArtifactEnvelopeFieldError("payload_json is not Canonical JSON V1") from exc
        if type(self.content_hash) is not Sha256Digest or type(self.artifact_hash) is not Sha256Digest:
            raise ArtifactEnvelopeFieldError("content_hash and artifact_hash must be typed digests")
        expected_content_hash = sha256_canonical_json(payload)
        if not hmac.compare_digest(expected_content_hash.value, self.content_hash.value):
            raise ArtifactIntegrityError("artifact content_hash does not match payload")
        unsigned = self._unsigned_value(payload)
        expected_artifact_hash = sha256_canonical_json(unsigned)
        if not hmac.compare_digest(expected_artifact_hash.value, self.artifact_hash.value):
            raise ArtifactIntegrityError("artifact_hash does not match envelope content")

    @classmethod
    def create(
        cls,
        *,
        project_id: CanonicalId,
        turn_id: CanonicalId,
        recipe_id: RecipeId,
        artifact_type: str,
        revision: int,
        project_version: str,
        contract_version: str,
        schema_version: str,
        recipe_version: str,
        registry_version: str,
        runtime_identity_version: str,
        created_at: datetime,
        payload: JsonValue,
        short_id: ScopedAlias | None = None,
        basis_refs: tuple[ArtifactBasisRef, ...] = (),
    ) -> ArtifactEnvelope:
        """Allocate a host artifact UUID and seal a new immutable V1 envelope."""

        artifact_id = CanonicalId.new()
        timestamp = canonical_utc_timestamp(created_at)
        _validate_metadata(
            artifact_id=artifact_id,
            project_id=project_id,
            turn_id=turn_id,
            recipe_id=recipe_id,
            artifact_type=artifact_type,
            short_id=short_id,
            revision=revision,
            project_version=project_version,
            contract_version=contract_version,
            schema_version=schema_version,
            recipe_version=recipe_version,
            registry_version=registry_version,
            runtime_identity_version=runtime_identity_version,
            created_at=timestamp,
            basis_refs=basis_refs,
        )
        payload_json = canonical_json_dumps(payload)
        immutable_payload = require_canonical_json(payload_json)
        content_hash = sha256_canonical_json(immutable_payload)
        unsigned = _unsigned_value(
            artifact_id=artifact_id,
            project_id=project_id,
            turn_id=turn_id,
            recipe_id=recipe_id,
            artifact_type=artifact_type,
            short_id=short_id,
            revision=revision,
            project_version=project_version,
            contract_version=contract_version,
            schema_version=schema_version,
            recipe_version=recipe_version,
            registry_version=registry_version,
            runtime_identity_version=runtime_identity_version,
            created_at=timestamp,
            basis_refs=basis_refs,
            payload=immutable_payload,
            content_hash=content_hash,
        )
        return cls(
            artifact_id=artifact_id,
            project_id=project_id,
            turn_id=turn_id,
            recipe_id=recipe_id,
            artifact_type=artifact_type,
            short_id=short_id,
            revision=revision,
            project_version=project_version,
            contract_version=contract_version,
            schema_version=schema_version,
            recipe_version=recipe_version,
            registry_version=registry_version,
            runtime_identity_version=runtime_identity_version,
            created_at=timestamp,
            basis_refs=basis_refs,
            payload_json=payload_json,
            content_hash=content_hash,
            artifact_hash=sha256_canonical_json(unsigned),
        )

    @property
    def payload(self) -> JsonValue:
        """Return a fresh decoded payload so callers cannot mutate the envelope."""

        return require_canonical_json(self.payload_json)

    def _unsigned_value(self, payload: JsonValue | None = None) -> dict[str, JsonValue]:
        return _unsigned_value(
            artifact_id=self.artifact_id,
            project_id=self.project_id,
            turn_id=self.turn_id,
            recipe_id=self.recipe_id,
            artifact_type=self.artifact_type,
            short_id=self.short_id,
            revision=self.revision,
            project_version=self.project_version,
            contract_version=self.contract_version,
            schema_version=self.schema_version,
            recipe_version=self.recipe_version,
            registry_version=self.registry_version,
            runtime_identity_version=self.runtime_identity_version,
            created_at=self.created_at,
            basis_refs=self.basis_refs,
            payload=self.payload if payload is None else payload,
            content_hash=self.content_hash,
        )

    def to_value(self) -> dict[str, JsonValue]:
        """Return the complete envelope as a fresh JSON object."""

        value = self._unsigned_value()
        value["artifact_hash"] = self.artifact_hash.value
        return value

    def to_json(self) -> str:
        """Serialize the complete envelope as Canonical JSON V1."""

        return canonical_json_dumps(self.to_value())

    def verify_integrity(self) -> bool:
        """Recompute both hashes; valid immutable instances return true."""

        payload = self.payload
        expected_content = sha256_canonical_json(payload)
        expected_artifact = sha256_canonical_json(self._unsigned_value(payload))
        return hmac.compare_digest(
            self.content_hash.value, expected_content.value
        ) and hmac.compare_digest(self.artifact_hash.value, expected_artifact.value)

    @classmethod
    def from_value(cls, value: object) -> ArtifactEnvelope:
        """Validate and reconstruct a complete envelope from a JSON object."""

        parsed = _require_object("artifact envelope", value)
        _require_exact_fields("artifact envelope", parsed, _ENVELOPE_FIELDS)
        if parsed["envelope_version"] != ARTIFACT_ENVELOPE_VERSION or type(
            parsed["envelope_version"]
        ) is not int:
            raise ArtifactEnvelopeFieldError("unsupported artifact envelope version")
        try:
            artifact_id = CanonicalId.parse(cast(str, parsed["artifact_uuid"]))
            project_id = CanonicalId.parse(cast(str, parsed["project_uuid"]))
            turn_id = CanonicalId.parse(cast(str, parsed["turn_uuid"]))
            recipe_id = RecipeId(cast(str, parsed["recipe_id"]))
            content_hash = parse_sha256_digest(cast(str, parsed["content_hash"]))
            artifact_hash = parse_sha256_digest(cast(str, parsed["artifact_hash"]))
        except (TypeError, ValueError) as exc:
            raise ArtifactEnvelopeFieldError("envelope contains an invalid identity") from exc

        short_text = parsed["short_id"]
        short_kind = parsed["short_id_kind"]
        if short_text is None and short_kind is None:
            short_id = None
        elif type(short_text) is str and type(short_kind) is str:
            try:
                short_id = ScopedAlias.parse(
                    short_text,
                    kind=AliasKind(short_kind),
                    scope_id=turn_id,
                )
            except (TypeError, ValueError) as exc:
                raise ArtifactEnvelopeFieldError("short_id is invalid") from exc
        else:
            raise ArtifactEnvelopeFieldError(
                "short_id and short_id_kind must either both be text or both be null"
            )

        basis_values = _require_array("basis_refs", parsed["basis_refs"])
        basis_refs = tuple(ArtifactBasisRef.from_value(item) for item in basis_values)
        try:
            payload_json = canonical_json_dumps(parsed["payload"])
        except ValueError as exc:
            raise ArtifactEnvelopeFieldError("payload is not a strict JSON value") from exc
        try:
            return cls(
                artifact_id=artifact_id,
                project_id=project_id,
                turn_id=turn_id,
                recipe_id=recipe_id,
                artifact_type=cast(str, parsed["artifact_type"]),
                short_id=short_id,
                revision=_require_exact_int("revision", parsed["revision"]),
                project_version=cast(str, parsed["project_version"]),
                contract_version=cast(str, parsed["contract_version"]),
                schema_version=cast(str, parsed["schema_version"]),
                recipe_version=cast(str, parsed["recipe_version"]),
                registry_version=cast(str, parsed["registry_version"]),
                runtime_identity_version=cast(str, parsed["runtime_identity_version"]),
                created_at=_parse_timestamp(parsed["created_at"]),
                basis_refs=basis_refs,
                payload_json=payload_json,
                content_hash=content_hash,
                artifact_hash=artifact_hash,
            )
        except ArtifactEnvelopeError:
            raise
        except (TypeError, ValueError) as exc:
            raise ArtifactEnvelopeFieldError("artifact envelope is invalid") from exc

    @classmethod
    def from_json(cls, value: str) -> ArtifactEnvelope:
        """Parse only an exact Canonical JSON V1 envelope representation."""

        try:
            parsed = require_canonical_json(value)
        except ValueError as exc:
            raise ArtifactEnvelopeFieldError("envelope text is not Canonical JSON V1") from exc
        return cls.from_value(parsed)

    @classmethod
    def from_bytes(cls, value: bytes) -> ArtifactEnvelope:
        """Parse only exact UTF-8 Canonical JSON V1 envelope bytes."""

        try:
            parsed = strict_json_loads_bytes(value)
            canonical = canonical_json_dumps(parsed).encode("utf-8")
        except ValueError as exc:
            raise ArtifactEnvelopeFieldError("envelope bytes are not strict UTF-8 JSON") from exc
        if canonical != value:
            raise ArtifactEnvelopeFieldError("envelope bytes are not Canonical JSON V1")
        return cls.from_value(parsed)
