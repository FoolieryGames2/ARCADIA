"""Hash-verified, forward-only SQLite migrations for the Phase A substrate."""

from __future__ import annotations

import re
import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime

from arcadia.core.artifact_envelope import canonical_utc_timestamp
from arcadia.core.canonical_json import JsonValue
from arcadia.core.hashing import Sha256Digest, parse_sha256_digest, sha256_canonical_json
from arcadia.storage.connection import (
    ConnectionAccess,
    DatabaseConnection,
    StorageConnectionError,
    TransactionMode,
)

MIGRATION_FRAMEWORK_VERSION = 1
_NAME_PATTERN = re.compile(r"[a-z][a-z0-9_]{0,63}", re.ASCII)
_LEDGER_TABLE = "schema_migrations"


class MigrationError(StorageConnectionError):
    """Base error for an invalid migration catalog or database schema state."""


class MigrationCatalogError(MigrationError):
    """The host migration catalog is malformed or internally inconsistent."""


class MigrationIntegrityError(MigrationError):
    """Applied migration history does not match the immutable host catalog."""


class UnmanagedDatabaseError(MigrationError):
    """A nonempty database has no ARCADIA migration authority ledger."""


@dataclass(frozen=True, slots=True)
class Migration:
    """One immutable ordered set of single-statement SQLite changes."""

    version: int
    name: str
    statements: tuple[str, ...]

    def __post_init__(self) -> None:
        if type(self.version) is not int or self.version < 1:
            raise MigrationCatalogError("migration version must be a positive integer")
        if type(self.name) is not str or _NAME_PATTERN.fullmatch(self.name) is None:
            raise MigrationCatalogError("migration name must be a canonical snake-case token")
        if type(self.statements) is not tuple or not self.statements:
            raise MigrationCatalogError("migration statements must be a nonempty immutable tuple")
        if any(type(statement) is not str or not statement.strip() for statement in self.statements):
            raise MigrationCatalogError("every migration statement must be a nonempty string")

    @property
    def migration_hash(self) -> Sha256Digest:
        return sha256_canonical_json(self.to_value())

    def to_value(self) -> dict[str, JsonValue]:
        return {
            "framework_version": MIGRATION_FRAMEWORK_VERSION,
            "name": self.name,
            "statements": list(self.statements),
            "version": self.version,
        }


@dataclass(frozen=True, slots=True)
class MigrationCatalog:
    """Complete contiguous schema history known to this host build."""

    migrations: tuple[Migration, ...]
    framework_version: int = MIGRATION_FRAMEWORK_VERSION

    def __post_init__(self) -> None:
        if type(self.framework_version) is not int or (
            self.framework_version != MIGRATION_FRAMEWORK_VERSION
        ):
            raise MigrationCatalogError("unsupported migration framework version")
        if type(self.migrations) is not tuple or not self.migrations:
            raise MigrationCatalogError("migration catalog must be a nonempty immutable tuple")
        if any(type(migration) is not Migration for migration in self.migrations):
            raise MigrationCatalogError("catalog entries must be Migration values")
        versions = tuple(migration.version for migration in self.migrations)
        if versions != tuple(range(1, len(self.migrations) + 1)):
            raise MigrationCatalogError("migration versions must be contiguous from one")
        names = tuple(migration.name for migration in self.migrations)
        if len(names) != len(set(names)):
            raise MigrationCatalogError("migration names must be unique")

    @property
    def target_version(self) -> int:
        return self.migrations[-1].version

    @property
    def catalog_hash(self) -> Sha256Digest:
        return sha256_canonical_json(self.to_value())

    def to_value(self) -> dict[str, JsonValue]:
        return {
            "framework_version": self.framework_version,
            "migrations": [
                {
                    **migration.to_value(),
                    "migration_hash": migration.migration_hash.value,
                }
                for migration in self.migrations
            ],
        }


@dataclass(frozen=True, slots=True)
class AppliedMigration:
    version: int
    name: str
    migration_hash: Sha256Digest
    applied_at: str

    def to_value(self) -> dict[str, JsonValue]:
        return {
            "applied_at": self.applied_at,
            "migration_hash": self.migration_hash.value,
            "name": self.name,
            "version": self.version,
        }


@dataclass(frozen=True, slots=True)
class MigrationState:
    managed: bool
    current_version: int
    target_version: int
    applied: tuple[AppliedMigration, ...]
    catalog_hash: Sha256Digest


@dataclass(frozen=True, slots=True)
class MigrationReport:
    previous_version: int
    current_version: int
    target_version: int
    applied_now: tuple[AppliedMigration, ...]
    catalog_hash: Sha256Digest

    @property
    def changed(self) -> bool:
        return bool(self.applied_now)


_CREATE_MIGRATION_LEDGER = """
CREATE TABLE schema_migrations (
    version INTEGER PRIMARY KEY CHECK(version >= 1),
    name TEXT NOT NULL UNIQUE CHECK(length(name) BETWEEN 1 AND 64),
    migration_hash TEXT NOT NULL CHECK(length(migration_hash) = 71),
    applied_at TEXT NOT NULL CHECK(length(applied_at) = 27)
) STRICT
""".strip()


FOUNDATION_MIGRATIONS = MigrationCatalog(
    migrations=(
        Migration(
            version=1,
            name="host_metadata",
            statements=(
                """
                CREATE TABLE system_meta (
                    key TEXT PRIMARY KEY CHECK(length(key) BETWEEN 1 AND 128),
                    value TEXT NOT NULL
                ) STRICT
                """.strip(),
            ),
        ),
        Migration(
            version=2,
            name="transcript_substrate",
            statements=(
                """
                CREATE TABLE conversations (
                    conversation_uuid TEXT PRIMARY KEY CHECK(length(conversation_uuid) = 36),
                    project_uuid TEXT NOT NULL CHECK(length(project_uuid) = 36),
                    created_at TEXT NOT NULL CHECK(length(created_at) = 27),
                    UNIQUE(project_uuid, conversation_uuid)
                ) STRICT
                """.strip(),
                """
                CREATE TABLE conversation_turns (
                    turn_uuid TEXT PRIMARY KEY CHECK(length(turn_uuid) = 36),
                    project_uuid TEXT NOT NULL CHECK(length(project_uuid) = 36),
                    conversation_uuid TEXT NOT NULL CHECK(length(conversation_uuid) = 36),
                    turn_ordinal INTEGER NOT NULL CHECK(turn_ordinal >= 1),
                    created_at TEXT NOT NULL CHECK(length(created_at) = 27),
                    UNIQUE(conversation_uuid, turn_ordinal),
                    UNIQUE(project_uuid, turn_uuid),
                    UNIQUE(project_uuid, conversation_uuid, turn_uuid),
                    FOREIGN KEY(project_uuid, conversation_uuid)
                        REFERENCES conversations(project_uuid, conversation_uuid)
                ) STRICT
                """.strip(),
                """
                CREATE TABLE transcript_entries (
                    entry_uuid TEXT PRIMARY KEY CHECK(length(entry_uuid) = 36),
                    project_uuid TEXT NOT NULL CHECK(length(project_uuid) = 36),
                    conversation_uuid TEXT NOT NULL CHECK(length(conversation_uuid) = 36),
                    turn_uuid TEXT NOT NULL CHECK(length(turn_uuid) = 36),
                    entry_ordinal INTEGER NOT NULL CHECK(entry_ordinal >= 1),
                    role TEXT NOT NULL CHECK(role IN ('USER', 'ASSISTANT')),
                    content TEXT NOT NULL,
                    content_hash TEXT NOT NULL CHECK(length(content_hash) = 71),
                    created_at TEXT NOT NULL CHECK(length(created_at) = 27),
                    UNIQUE(conversation_uuid, entry_ordinal),
                    FOREIGN KEY(project_uuid, conversation_uuid, turn_uuid)
                        REFERENCES conversation_turns(project_uuid, conversation_uuid, turn_uuid)
                ) STRICT
                """.strip(),
                """
                CREATE INDEX idx_conversation_turns_conversation
                ON conversation_turns(conversation_uuid, turn_ordinal)
                """.strip(),
                """
                CREATE INDEX idx_transcript_entries_turn
                ON transcript_entries(turn_uuid, entry_ordinal)
                """.strip(),
            ),
        ),
        Migration(
            version=3,
            name="artifact_substrate",
            statements=(
                """
                CREATE TABLE artifacts (
                    artifact_uuid TEXT PRIMARY KEY CHECK(length(artifact_uuid) = 36),
                    project_uuid TEXT NOT NULL CHECK(length(project_uuid) = 36),
                    turn_uuid TEXT NOT NULL CHECK(length(turn_uuid) = 36),
                    recipe_id TEXT NOT NULL,
                    artifact_type TEXT NOT NULL CHECK(length(artifact_type) BETWEEN 1 AND 128),
                    created_at TEXT NOT NULL CHECK(length(created_at) = 27),
                    FOREIGN KEY(project_uuid, turn_uuid)
                        REFERENCES conversation_turns(project_uuid, turn_uuid)
                ) STRICT
                """.strip(),
                """
                CREATE TABLE artifact_revisions (
                    artifact_uuid TEXT NOT NULL CHECK(length(artifact_uuid) = 36),
                    revision INTEGER NOT NULL CHECK(revision >= 1),
                    envelope_json TEXT NOT NULL,
                    content_hash TEXT NOT NULL CHECK(length(content_hash) = 71),
                    envelope_hash TEXT NOT NULL UNIQUE CHECK(length(envelope_hash) = 71),
                    created_at TEXT NOT NULL CHECK(length(created_at) = 27),
                    PRIMARY KEY(artifact_uuid, revision),
                    FOREIGN KEY(artifact_uuid) REFERENCES artifacts(artifact_uuid)
                ) STRICT
                """.strip(),
                """
                CREATE TABLE artifact_links (
                    artifact_uuid TEXT NOT NULL CHECK(length(artifact_uuid) = 36),
                    artifact_revision INTEGER NOT NULL CHECK(artifact_revision >= 1),
                    link_ordinal INTEGER NOT NULL CHECK(link_ordinal >= 1),
                    basis_artifact_uuid TEXT NOT NULL CHECK(length(basis_artifact_uuid) = 36),
                    basis_revision INTEGER NOT NULL CHECK(basis_revision >= 1),
                    basis_envelope_hash TEXT NOT NULL CHECK(length(basis_envelope_hash) = 71),
                    PRIMARY KEY(artifact_uuid, artifact_revision, link_ordinal),
                    UNIQUE(
                        artifact_uuid,
                        artifact_revision,
                        basis_artifact_uuid,
                        basis_revision
                    ),
                    FOREIGN KEY(artifact_uuid, artifact_revision)
                        REFERENCES artifact_revisions(artifact_uuid, revision),
                    FOREIGN KEY(basis_artifact_uuid, basis_revision)
                        REFERENCES artifact_revisions(artifact_uuid, revision)
                ) STRICT
                """.strip(),
                """
                CREATE INDEX idx_artifacts_turn
                ON artifacts(turn_uuid, recipe_id)
                """.strip(),
                """
                CREATE INDEX idx_artifact_links_basis
                ON artifact_links(basis_artifact_uuid, basis_revision)
                """.strip(),
            ),
        ),
        Migration(
            version=4,
            name="registry_snapshot_substrate",
            statements=(
                """
                CREATE TABLE registry_snapshots (
                    snapshot_uuid TEXT PRIMARY KEY CHECK(length(snapshot_uuid) = 36),
                    project_uuid TEXT NOT NULL CHECK(length(project_uuid) = 36),
                    registry_kind TEXT NOT NULL CHECK(length(registry_kind) BETWEEN 1 AND 128),
                    registry_version TEXT NOT NULL CHECK(length(registry_version) BETWEEN 1 AND 128),
                    contract_identity_version TEXT NOT NULL,
                    schema_identity_version TEXT NOT NULL,
                    recipe_identity_version TEXT NOT NULL,
                    registry_identity_version TEXT NOT NULL,
                    runtime_identity_version TEXT NOT NULL,
                    snapshot_json TEXT NOT NULL,
                    snapshot_hash TEXT NOT NULL CHECK(length(snapshot_hash) = 71),
                    created_at TEXT NOT NULL CHECK(length(created_at) = 27),
                    UNIQUE(project_uuid, registry_kind, registry_version)
                ) STRICT
                """.strip(),
                """
                CREATE INDEX idx_registry_snapshots_kind_version
                ON registry_snapshots(project_uuid, registry_kind, registry_version)
                """.strip(),
                """
                CREATE INDEX idx_registry_snapshots_hash
                ON registry_snapshots(project_uuid, snapshot_hash)
                """.strip(),
            ),
        ),
    )
)


@dataclass(frozen=True, slots=True)
class MigrationRunner:
    catalog: MigrationCatalog = FOUNDATION_MIGRATIONS

    def __post_init__(self) -> None:
        if type(self.catalog) is not MigrationCatalog:
            raise MigrationCatalogError("catalog must be a MigrationCatalog")

    def inspect(self, connection: DatabaseConnection) -> MigrationState:
        self._require_connection(connection)
        managed = self._ledger_exists(connection)
        if not managed:
            objects = self._application_objects(connection)
            if objects:
                raise UnmanagedDatabaseError(
                    "nonempty SQLite database has no ARCADIA migration ledger"
                )
            applied: tuple[AppliedMigration, ...] = ()
        else:
            applied = self._read_applied(connection)
            self._verify_prefix(applied)
        return MigrationState(
            managed=managed,
            current_version=len(applied),
            target_version=self.catalog.target_version,
            applied=applied,
            catalog_hash=self.catalog.catalog_hash,
        )

    def migrate(
        self, connection: DatabaseConnection, *, applied_at: datetime
    ) -> MigrationReport:
        self._require_connection(connection)
        if connection.access is not ConnectionAccess.READ_WRITE:
            raise MigrationError("migrations require a read/write connection")
        if connection.in_transaction:
            raise MigrationError("migration runner must own the outer transaction")
        timestamp = canonical_utc_timestamp(applied_at)
        initial = self.inspect(connection)
        if initial.current_version == self.catalog.target_version:
            return MigrationReport(
                previous_version=initial.current_version,
                current_version=initial.current_version,
                target_version=initial.target_version,
                applied_now=(),
                catalog_hash=self.catalog.catalog_hash,
            )
        applied_now: list[AppliedMigration] = []
        try:
            with connection.transaction(TransactionMode.IMMEDIATE):
                locked = self.inspect(connection)
                if locked.current_version != initial.current_version:
                    raise MigrationIntegrityError("migration state changed before lock acquisition")
                if not locked.managed:
                    connection.execute(_CREATE_MIGRATION_LEDGER)
                for migration in self.catalog.migrations[locked.current_version :]:
                    for statement in migration.statements:
                        connection.execute(statement)
                    record = AppliedMigration(
                        version=migration.version,
                        name=migration.name,
                        migration_hash=migration.migration_hash,
                        applied_at=timestamp,
                    )
                    connection.execute(
                        """
                        INSERT INTO schema_migrations(
                            version, name, migration_hash, applied_at
                        ) VALUES (?, ?, ?, ?)
                        """,
                        (
                            record.version,
                            record.name,
                            record.migration_hash.value,
                            record.applied_at,
                        ),
                    )
                    applied_now.append(record)
        except sqlite3.Error as exc:
            raise MigrationError("SQLite rejected an atomic schema migration") from exc
        final = self.inspect(connection)
        if final.current_version != self.catalog.target_version:
            raise MigrationIntegrityError("migration transaction did not reach target version")
        return MigrationReport(
            previous_version=initial.current_version,
            current_version=final.current_version,
            target_version=final.target_version,
            applied_now=tuple(applied_now),
            catalog_hash=self.catalog.catalog_hash,
        )

    def _read_applied(self, connection: DatabaseConnection) -> tuple[AppliedMigration, ...]:
        try:
            rows = connection.execute(
                """
                SELECT version, name, migration_hash, applied_at
                FROM schema_migrations
                ORDER BY version
                """
            ).fetchall()
            applied: list[AppliedMigration] = []
            for row in rows:
                version = row["version"]
                name = row["name"]
                migration_hash = row["migration_hash"]
                applied_at = row["applied_at"]
                if (
                    type(version) is not int
                    or type(name) is not str
                    or type(migration_hash) is not str
                    or type(applied_at) is not str
                ):
                    raise MigrationIntegrityError("migration ledger contains coerced fields")
                applied.append(
                    AppliedMigration(
                        version=version,
                        name=name,
                        migration_hash=parse_sha256_digest(migration_hash),
                        applied_at=applied_at,
                    )
                )
            return tuple(applied)
        except (sqlite3.Error, TypeError, ValueError) as exc:
            raise MigrationIntegrityError("migration ledger is malformed") from exc

    def _verify_prefix(self, applied: tuple[AppliedMigration, ...]) -> None:
        if len(applied) > self.catalog.target_version:
            raise MigrationIntegrityError("database schema is newer than this host catalog")
        for expected_version, record in enumerate(applied, start=1):
            if record.version != expected_version:
                raise MigrationIntegrityError("applied migration versions are not contiguous")
            expected = self.catalog.migrations[expected_version - 1]
            if record.name != expected.name or record.migration_hash != expected.migration_hash:
                raise MigrationIntegrityError("applied migration identity differs from catalog")
            try:
                parsed = datetime.strptime(record.applied_at, "%Y-%m-%dT%H:%M:%S.%fZ")
            except ValueError as exc:
                raise MigrationIntegrityError("applied migration timestamp is not canonical") from exc
            if canonical_utc_timestamp(parsed.replace(tzinfo=UTC)) != record.applied_at:
                raise MigrationIntegrityError("applied migration timestamp is not canonical UTC")

    @staticmethod
    def _ledger_exists(connection: DatabaseConnection) -> bool:
        row = connection.execute(
            "SELECT 1 AS present FROM sqlite_master WHERE type='table' AND name=?",
            (_LEDGER_TABLE,),
        ).fetchone()
        return row is not None

    @staticmethod
    def _application_objects(connection: DatabaseConnection) -> tuple[str, ...]:
        rows = connection.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type IN ('table', 'view', 'trigger') AND name NOT LIKE 'sqlite_%'
            ORDER BY name
            """
        ).fetchall()
        return tuple(str(row["name"]) for row in rows)

    @staticmethod
    def _require_connection(connection: DatabaseConnection) -> None:
        if type(connection) is not DatabaseConnection or connection.closed:
            raise MigrationError("an open managed DatabaseConnection is required")
