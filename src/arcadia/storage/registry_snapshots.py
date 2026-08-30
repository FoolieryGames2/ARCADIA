"""Immutable, project-scoped snapshots of versioned runtime registries."""

from __future__ import annotations

import hmac
import re
import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Final, cast

from arcadia.core.artifact_envelope import ArtifactEnvelopeError, canonical_utc_timestamp
from arcadia.core.canonical_json import (
    JsonValue,
    canonical_json_dumps,
    require_canonical_json,
)
from arcadia.core.hashing import Sha256Digest, parse_sha256_digest, sha256_canonical_json
from arcadia.core.ids import CanonicalId
from arcadia.storage.connection import (
    ConnectionAccess,
    DatabaseConnection,
    SQLiteConnectionFactory,
)
from arcadia.storage.migrations import MigrationRunner

MAX_REGISTRY_SNAPSHOTS_PER_READ = 200

_KIND_PATTERN: Final = re.compile(r"[A-Z][A-Z0-9_]{0,127}", flags=re.ASCII)
_VERSION_PATTERN: Final = re.compile(
    r"[A-Za-z0-9][A-Za-z0-9._:+-]{0,127}", flags=re.ASCII
)
_SNAPSHOT_FIELDS: Final = frozenset(
    {
        "snapshot_uuid",
        "project_uuid",
        "registry_kind",
        "registry_version",
        "contract_identity_version",
        "schema_identity_version",
        "recipe_identity_version",
        "registry_identity_version",
        "runtime_identity_version",
        "snapshot",
        "snapshot_hash",
        "created_at",
    }
)


class RegistrySnapshotError(RuntimeError):
    """Base error for registry snapshot input, state, or integrity failure."""


class RegistrySnapshotFieldError(RegistrySnapshotError):
    """A snapshot field or repository argument is malformed."""


class RegistrySnapshotNotFoundError(RegistrySnapshotError):
    """A requested project-scoped registry snapshot does not exist."""


class RegistrySnapshotConflictError(RegistrySnapshotError):
    """A snapshot UUID or registry kind/version is already bound differently."""


class RegistrySnapshotIntegrityError(RegistrySnapshotError):
    """A durable registry snapshot fails canonical or hash verification."""


def _require_token(name: str, value: object, pattern: re.Pattern[str]) -> str:
    if type(value) is not str or pattern.fullmatch(value) is None:
        raise RegistrySnapshotFieldError(f"{name} is not a legal canonical token")
    return value


def _require_snapshot_json(value: object) -> tuple[str, dict[str, JsonValue]]:
    if type(value) is not str:
        raise RegistrySnapshotFieldError("snapshot_json must be Canonical JSON text")
    try:
        parsed = require_canonical_json(value)
    except ValueError as exc:
        raise RegistrySnapshotFieldError(
            "snapshot_json is not Canonical JSON V1"
        ) from exc
    if type(parsed) is not dict:
        raise RegistrySnapshotFieldError("registry snapshot must be a JSON object")
    return value, parsed


def _parse_timestamp(value: object) -> str:
    if type(value) is not str:
        raise RegistrySnapshotFieldError("created_at must be canonical UTC text")
    try:
        parsed = datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=UTC)
    except ValueError as exc:
        raise RegistrySnapshotFieldError("created_at is not a real UTC timestamp") from exc
    if canonical_utc_timestamp(parsed) != value:
        raise RegistrySnapshotFieldError("created_at is not canonical UTC")
    return value


def _unsigned_value(
    *,
    snapshot_id: CanonicalId,
    project_id: CanonicalId,
    registry_kind: str,
    registry_version: str,
    contract_identity_version: str,
    schema_identity_version: str,
    recipe_identity_version: str,
    registry_identity_version: str,
    runtime_identity_version: str,
    snapshot: dict[str, JsonValue],
    created_at: str,
) -> dict[str, JsonValue]:
    return {
        "snapshot_uuid": str(snapshot_id),
        "project_uuid": str(project_id),
        "registry_kind": registry_kind,
        "registry_version": registry_version,
        "contract_identity_version": contract_identity_version,
        "schema_identity_version": schema_identity_version,
        "recipe_identity_version": recipe_identity_version,
        "registry_identity_version": registry_identity_version,
        "runtime_identity_version": runtime_identity_version,
        "snapshot": snapshot,
        "created_at": created_at,
    }


@dataclass(frozen=True, slots=True)
class RegistrySnapshot:
    """One immutable canonical registry document and all runtime identity axes."""

    snapshot_id: CanonicalId
    project_id: CanonicalId
    registry_kind: str
    registry_version: str
    contract_identity_version: str
    schema_identity_version: str
    recipe_identity_version: str
    registry_identity_version: str
    runtime_identity_version: str
    snapshot_json: str
    snapshot_hash: Sha256Digest
    created_at: str

    def __post_init__(self) -> None:
        for name, identity in (
            ("snapshot_id", self.snapshot_id),
            ("project_id", self.project_id),
        ):
            if type(identity) is not CanonicalId:
                raise RegistrySnapshotFieldError(f"{name} must be a CanonicalId")
        _require_token("registry_kind", self.registry_kind, _KIND_PATTERN)
        for name, value in (
            ("registry_version", self.registry_version),
            ("contract_identity_version", self.contract_identity_version),
            ("schema_identity_version", self.schema_identity_version),
            ("recipe_identity_version", self.recipe_identity_version),
            ("registry_identity_version", self.registry_identity_version),
            ("runtime_identity_version", self.runtime_identity_version),
        ):
            _require_token(name, value, _VERSION_PATTERN)
        _, snapshot = _require_snapshot_json(self.snapshot_json)
        _parse_timestamp(self.created_at)
        if type(self.snapshot_hash) is not Sha256Digest:
            raise RegistrySnapshotFieldError("snapshot_hash must be a Sha256Digest")
        expected = sha256_canonical_json(self._unsigned_value(snapshot))
        if not hmac.compare_digest(expected.value, self.snapshot_hash.value):
            raise RegistrySnapshotIntegrityError(
                "snapshot_hash does not match registry identity and content"
            )

    @classmethod
    def create(
        cls,
        *,
        project_id: CanonicalId,
        registry_kind: str,
        registry_version: str,
        contract_identity_version: str,
        schema_identity_version: str,
        recipe_identity_version: str,
        registry_identity_version: str,
        runtime_identity_version: str,
        snapshot: dict[str, JsonValue],
        created_at: datetime,
    ) -> RegistrySnapshot:
        if type(project_id) is not CanonicalId:
            raise RegistrySnapshotFieldError("project_id must be a CanonicalId")
        if type(snapshot) is not dict:
            raise RegistrySnapshotFieldError("snapshot must be a JSON object")
        try:
            snapshot_json = canonical_json_dumps(snapshot)
            timestamp = canonical_utc_timestamp(created_at)
        except (ValueError, ArtifactEnvelopeError) as exc:
            raise RegistrySnapshotFieldError(
                "snapshot or created_at is not valid canonical input"
            ) from exc
        immutable_snapshot = cast(
            dict[str, JsonValue], require_canonical_json(snapshot_json)
        )
        snapshot_id = CanonicalId.new()
        unsigned = _unsigned_value(
            snapshot_id=snapshot_id,
            project_id=project_id,
            registry_kind=_require_token("registry_kind", registry_kind, _KIND_PATTERN),
            registry_version=_require_token(
                "registry_version", registry_version, _VERSION_PATTERN
            ),
            contract_identity_version=_require_token(
                "contract_identity_version", contract_identity_version, _VERSION_PATTERN
            ),
            schema_identity_version=_require_token(
                "schema_identity_version", schema_identity_version, _VERSION_PATTERN
            ),
            recipe_identity_version=_require_token(
                "recipe_identity_version", recipe_identity_version, _VERSION_PATTERN
            ),
            registry_identity_version=_require_token(
                "registry_identity_version", registry_identity_version, _VERSION_PATTERN
            ),
            runtime_identity_version=_require_token(
                "runtime_identity_version", runtime_identity_version, _VERSION_PATTERN
            ),
            snapshot=immutable_snapshot,
            created_at=timestamp,
        )
        return cls(
            snapshot_id=snapshot_id,
            project_id=project_id,
            registry_kind=registry_kind,
            registry_version=registry_version,
            contract_identity_version=contract_identity_version,
            schema_identity_version=schema_identity_version,
            recipe_identity_version=recipe_identity_version,
            registry_identity_version=registry_identity_version,
            runtime_identity_version=runtime_identity_version,
            snapshot_json=snapshot_json,
            snapshot_hash=sha256_canonical_json(unsigned),
            created_at=timestamp,
        )

    @property
    def snapshot(self) -> dict[str, JsonValue]:
        _, value = _require_snapshot_json(self.snapshot_json)
        return value

    def _unsigned_value(
        self, snapshot: dict[str, JsonValue] | None = None
    ) -> dict[str, JsonValue]:
        return _unsigned_value(
            snapshot_id=self.snapshot_id,
            project_id=self.project_id,
            registry_kind=self.registry_kind,
            registry_version=self.registry_version,
            contract_identity_version=self.contract_identity_version,
            schema_identity_version=self.schema_identity_version,
            recipe_identity_version=self.recipe_identity_version,
            registry_identity_version=self.registry_identity_version,
            runtime_identity_version=self.runtime_identity_version,
            snapshot=self.snapshot if snapshot is None else snapshot,
            created_at=self.created_at,
        )

    def to_value(self) -> dict[str, JsonValue]:
        value = self._unsigned_value()
        value["snapshot_hash"] = self.snapshot_hash.value
        return value

    def to_json(self) -> str:
        return canonical_json_dumps(self.to_value())

    @classmethod
    def from_value(cls, value: object) -> RegistrySnapshot:
        if type(value) is not dict or any(type(key) is not str for key in value):
            raise RegistrySnapshotFieldError("registry snapshot must be a JSON object")
        parsed = cast(dict[str, JsonValue], value)
        actual = frozenset(parsed)
        if actual != _SNAPSHOT_FIELDS:
            raise RegistrySnapshotFieldError("registry snapshot fields do not match V1")
        try:
            snapshot_value = parsed["snapshot"]
            if type(snapshot_value) is not dict:
                raise RegistrySnapshotFieldError("registry snapshot must be a JSON object")
            return cls(
                snapshot_id=CanonicalId.parse(cast(str, parsed["snapshot_uuid"])),
                project_id=CanonicalId.parse(cast(str, parsed["project_uuid"])),
                registry_kind=cast(str, parsed["registry_kind"]),
                registry_version=cast(str, parsed["registry_version"]),
                contract_identity_version=cast(
                    str, parsed["contract_identity_version"]
                ),
                schema_identity_version=cast(str, parsed["schema_identity_version"]),
                recipe_identity_version=cast(str, parsed["recipe_identity_version"]),
                registry_identity_version=cast(
                    str, parsed["registry_identity_version"]
                ),
                runtime_identity_version=cast(
                    str, parsed["runtime_identity_version"]
                ),
                snapshot_json=canonical_json_dumps(snapshot_value),
                snapshot_hash=parse_sha256_digest(cast(str, parsed["snapshot_hash"])),
                created_at=cast(str, parsed["created_at"]),
            )
        except RegistrySnapshotError:
            raise
        except (TypeError, ValueError) as exc:
            raise RegistrySnapshotFieldError(
                "registry snapshot contains malformed identity data"
            ) from exc

    @classmethod
    def from_json(cls, value: str) -> RegistrySnapshot:
        try:
            parsed = require_canonical_json(value)
        except ValueError as exc:
            raise RegistrySnapshotFieldError(
                "registry snapshot text is not Canonical JSON V1"
            ) from exc
        return cls.from_value(parsed)


@dataclass(frozen=True, slots=True)
class RegistrySnapshotRepository:
    """Stores exact immutable registry snapshots for one project UUID."""

    factory: SQLiteConnectionFactory
    project_id: CanonicalId

    def __post_init__(self) -> None:
        if type(self.factory) is not SQLiteConnectionFactory:
            raise RegistrySnapshotFieldError(
                "factory must be a SQLiteConnectionFactory"
            )
        if type(self.project_id) is not CanonicalId:
            raise RegistrySnapshotFieldError("project_id must be a CanonicalId")

    def store(self, snapshot: RegistrySnapshot) -> RegistrySnapshot:
        if type(snapshot) is not RegistrySnapshot:
            raise RegistrySnapshotFieldError("snapshot must be a RegistrySnapshot")
        if snapshot.project_id != self.project_id:
            raise RegistrySnapshotConflictError("snapshot belongs to another project")
        with self.factory.connect() as connection:
            self._require_current_schema(connection)
            with connection.transaction():
                by_id = self._find_by_id(connection, snapshot.snapshot_id)
                if by_id is not None:
                    if by_id == snapshot:
                        return by_id
                    raise RegistrySnapshotConflictError(
                        "snapshot UUID already has different immutable content"
                    )
                by_version = self._find_by_version(
                    connection, snapshot.registry_kind, snapshot.registry_version
                )
                if by_version is not None:
                    raise RegistrySnapshotConflictError(
                        "registry kind/version already has an immutable snapshot"
                    )
                connection.execute(
                    """
                    INSERT INTO registry_snapshots(
                        snapshot_uuid, project_uuid, registry_kind, registry_version,
                        contract_identity_version, schema_identity_version,
                        recipe_identity_version, registry_identity_version,
                        runtime_identity_version, snapshot_json, snapshot_hash, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        str(snapshot.snapshot_id),
                        str(snapshot.project_id),
                        snapshot.registry_kind,
                        snapshot.registry_version,
                        snapshot.contract_identity_version,
                        snapshot.schema_identity_version,
                        snapshot.recipe_identity_version,
                        snapshot.registry_identity_version,
                        snapshot.runtime_identity_version,
                        snapshot.snapshot_json,
                        snapshot.snapshot_hash.value,
                        snapshot.created_at,
                    ),
                )
        return snapshot

    def load(self, *, snapshot_id: CanonicalId) -> RegistrySnapshot:
        self._require_id("snapshot_id", snapshot_id)
        with self.factory.connect(ConnectionAccess.READ_ONLY) as connection:
            self._require_current_schema(connection)
            snapshot = self._find_by_id(connection, snapshot_id)
            if snapshot is None or snapshot.project_id != self.project_id:
                raise RegistrySnapshotNotFoundError(
                    "project registry snapshot does not exist"
                )
            return snapshot

    def load_version(
        self, *, registry_kind: str, registry_version: str
    ) -> RegistrySnapshot:
        kind = _require_token("registry_kind", registry_kind, _KIND_PATTERN)
        version = _require_token("registry_version", registry_version, _VERSION_PATTERN)
        with self.factory.connect(ConnectionAccess.READ_ONLY) as connection:
            self._require_current_schema(connection)
            snapshot = self._find_by_version(connection, kind, version)
            if snapshot is None:
                raise RegistrySnapshotNotFoundError(
                    "project registry kind/version does not exist"
                )
            return snapshot

    def list_kind(
        self, *, registry_kind: str, limit: int
    ) -> tuple[RegistrySnapshot, ...]:
        kind = _require_token("registry_kind", registry_kind, _KIND_PATTERN)
        if type(limit) is not int or not 1 <= limit <= MAX_REGISTRY_SNAPSHOTS_PER_READ:
            raise RegistrySnapshotFieldError(
                f"limit must be between 1 and {MAX_REGISTRY_SNAPSHOTS_PER_READ}"
            )
        with self.factory.connect(ConnectionAccess.READ_ONLY) as connection:
            self._require_current_schema(connection)
            rows = connection.execute(
                f"""
                {self._snapshot_select()}
                WHERE project_uuid=? AND registry_kind=?
                ORDER BY created_at, snapshot_uuid
                LIMIT ?
                """,
                (str(self.project_id), kind, limit),
            ).fetchall()
            return tuple(self._decode_row(row) for row in rows)

    def _find_by_id(
        self, connection: DatabaseConnection, snapshot_id: CanonicalId
    ) -> RegistrySnapshot | None:
        row = connection.execute(
            f"{self._snapshot_select()} WHERE snapshot_uuid=?",
            (str(snapshot_id),),
        ).fetchone()
        return None if row is None else self._decode_row(row)

    def _find_by_version(
        self, connection: DatabaseConnection, kind: str, version: str
    ) -> RegistrySnapshot | None:
        row = connection.execute(
            f"""
            {self._snapshot_select()}
            WHERE project_uuid=? AND registry_kind=? AND registry_version=?
            """,
            (str(self.project_id), kind, version),
        ).fetchone()
        return None if row is None else self._decode_row(row)

    @staticmethod
    def _snapshot_select() -> str:
        return """
            SELECT snapshot_uuid, project_uuid, registry_kind, registry_version,
                   contract_identity_version, schema_identity_version,
                   recipe_identity_version, registry_identity_version,
                   runtime_identity_version, snapshot_json, snapshot_hash, created_at
            FROM registry_snapshots
        """

    @staticmethod
    def _decode_row(row: sqlite3.Row) -> RegistrySnapshot:
        try:
            return RegistrySnapshot(
                snapshot_id=CanonicalId.parse(
                    RegistrySnapshotRepository._row_text(row, "snapshot_uuid")
                ),
                project_id=CanonicalId.parse(
                    RegistrySnapshotRepository._row_text(row, "project_uuid")
                ),
                registry_kind=RegistrySnapshotRepository._row_text(
                    row, "registry_kind"
                ),
                registry_version=RegistrySnapshotRepository._row_text(
                    row, "registry_version"
                ),
                contract_identity_version=RegistrySnapshotRepository._row_text(
                    row, "contract_identity_version"
                ),
                schema_identity_version=RegistrySnapshotRepository._row_text(
                    row, "schema_identity_version"
                ),
                recipe_identity_version=RegistrySnapshotRepository._row_text(
                    row, "recipe_identity_version"
                ),
                registry_identity_version=RegistrySnapshotRepository._row_text(
                    row, "registry_identity_version"
                ),
                runtime_identity_version=RegistrySnapshotRepository._row_text(
                    row, "runtime_identity_version"
                ),
                snapshot_json=RegistrySnapshotRepository._row_text(row, "snapshot_json"),
                snapshot_hash=parse_sha256_digest(
                    RegistrySnapshotRepository._row_text(row, "snapshot_hash")
                ),
                created_at=RegistrySnapshotRepository._row_text(row, "created_at"),
            )
        except RegistrySnapshotIntegrityError:
            raise
        except RegistrySnapshotError as exc:
            raise RegistrySnapshotIntegrityError(
                "durable registry snapshot fields are malformed"
            ) from exc
        except (TypeError, ValueError) as exc:
            raise RegistrySnapshotIntegrityError(
                "durable registry snapshot identity is malformed"
            ) from exc

    @staticmethod
    def _row_text(row: sqlite3.Row, name: str) -> str:
        value = row[name]
        if type(value) is not str:
            raise RegistrySnapshotIntegrityError(f"durable {name} is not exact text")
        return value

    @staticmethod
    def _require_id(name: str, value: object) -> None:
        if type(value) is not CanonicalId:
            raise RegistrySnapshotFieldError(f"{name} must be a CanonicalId")

    @staticmethod
    def _require_current_schema(connection: DatabaseConnection) -> None:
        state = MigrationRunner().inspect(connection)
        if state.current_version != state.target_version:
            raise RegistrySnapshotError("registry snapshot schema is not current")
