from __future__ import annotations

import sqlite3
from dataclasses import FrozenInstanceError, replace
from datetime import UTC, datetime
from pathlib import Path

import pytest

from arcadia.core.config import StorageConfig
from arcadia.core.hashing import sha256_text
from arcadia.storage.connection import ConnectionAccess, SQLiteConnectionFactory
from arcadia.storage.migrations import (
    FOUNDATION_MIGRATIONS,
    AppliedMigration,
    Migration,
    MigrationCatalog,
    MigrationCatalogError,
    MigrationError,
    MigrationIntegrityError,
    MigrationRunner,
    UnmanagedDatabaseError,
)

NOW = datetime(2026, 8, 30, 12, 0, tzinfo=UTC)
TIMESTAMP = "2026-08-30T12:00:00.000000Z"


def _factory(root: Path) -> SQLiteConnectionFactory:
    return SQLiteConnectionFactory(
        workspace_root=root,
        storage=StorageConfig(
            data_dir="data",
            database_name="test.sqlite3",
            busy_timeout_ms=1000,
            require_fts5=True,
        ),
    )


def _migrate(root: Path) -> tuple[SQLiteConnectionFactory, MigrationRunner]:
    factory = _factory(root)
    runner = MigrationRunner()
    with factory.connect() as connection:
        runner.migrate(connection, applied_at=NOW)
    return factory, runner


def test_foundation_catalog_versions_names_and_hashes_are_frozen() -> None:
    assert FOUNDATION_MIGRATIONS.catalog_hash.value == (
        "sha256:2d7d9660dddb818b188fdaf8c7153c850bb4812db6bd120e6a0d23b8c7762d6c"
    )
    assert tuple(
        (migration.version, migration.name, migration.migration_hash.value)
        for migration in FOUNDATION_MIGRATIONS.migrations
    ) == (
        (
            1,
            "host_metadata",
            "sha256:00f996b691725c857887ac5eb1954219df71fae64681a12d00f4da19e30dcade",
        ),
        (
            2,
            "transcript_substrate",
            "sha256:1135cca47a15638d597dc5cdcfbb358e2192e02c3816438a3cfe7623d9dbee69",
        ),
        (
            3,
            "artifact_substrate",
            "sha256:8cea298b6eb8c734408918de0fe5fdb2e28711867fd73475fadbd1f373934ba1",
        ),
        (
            4,
            "registry_snapshot_substrate",
            "sha256:0df8179f14abf0d99a25b1a8c4e8f7ac14f0299cf14a49d7e25b0f794b645ef9",
        ),
    )


@pytest.mark.parametrize(
    "migration",
    [
        Migration(version=1, name="valid", statements=("SELECT 1",)),
    ],
)
def test_migration_values_are_immutable(migration: Migration) -> None:
    with pytest.raises(FrozenInstanceError):
        migration.name = "changed"  # type: ignore[misc]


@pytest.mark.parametrize(
    "kwargs",
    [
        {"version": 0, "name": "valid", "statements": ("SELECT 1",)},
        {"version": True, "name": "valid", "statements": ("SELECT 1",)},
        {"version": 1, "name": "Not-Canonical", "statements": ("SELECT 1",)},
        {"version": 1, "name": "valid", "statements": ()},
        {"version": 1, "name": "valid", "statements": ["SELECT 1"]},
        {"version": 1, "name": "valid", "statements": ("",)},
    ],
)
def test_migration_rejects_malformed_definitions(kwargs: dict[str, object]) -> None:
    with pytest.raises(MigrationCatalogError):
        Migration(**kwargs)  # type: ignore[arg-type]


def test_catalog_rejects_gaps_duplicates_and_mutable_entries() -> None:
    one = Migration(1, "one", ("SELECT 1",))
    with pytest.raises(MigrationCatalogError, match="contiguous"):
        MigrationCatalog((replace(one, version=2),))
    with pytest.raises(MigrationCatalogError, match="unique"):
        MigrationCatalog((one, Migration(2, "one", ("SELECT 2",))))
    with pytest.raises(MigrationCatalogError, match="immutable tuple"):
        MigrationCatalog([one])  # type: ignore[arg-type]


def test_empty_database_is_unmanaged_but_safe_to_adopt(tmp_path: Path) -> None:
    with _factory(tmp_path).connect() as connection:
        state = MigrationRunner().inspect(connection)
        assert not state.managed
        assert state.current_version == 0
        assert state.target_version == 4


def test_nonempty_unmanaged_database_is_never_silently_adopted(tmp_path: Path) -> None:
    with _factory(tmp_path).connect() as connection:
        with connection.transaction():
            connection.execute("CREATE TABLE foreign_owner(value TEXT) STRICT")
        with pytest.raises(UnmanagedDatabaseError, match="nonempty"):
            MigrationRunner().migrate(connection, applied_at=NOW)
        assert connection.execute(
            "SELECT count(*) AS count FROM foreign_owner"
        ).fetchone()["count"] == 0


def test_all_foundation_migrations_apply_in_one_report(tmp_path: Path) -> None:
    with _factory(tmp_path).connect() as connection:
        report = MigrationRunner().migrate(connection, applied_at=NOW)
        assert report.changed
        assert report.previous_version == 0
        assert report.current_version == report.target_version == 4
        assert tuple(record.version for record in report.applied_now) == (1, 2, 3, 4)
        assert all(record.applied_at == TIMESTAMP for record in report.applied_now)

        state = MigrationRunner().inspect(connection)
        assert state.managed
        assert state.current_version == 4
        assert state.applied == report.applied_now


def test_foundation_creates_only_phase_a_schema_not_semantic_memory(tmp_path: Path) -> None:
    factory, _ = _migrate(tmp_path)
    expected = {
        "artifact_links",
        "artifact_revisions",
        "artifacts",
        "conversation_turns",
        "conversations",
        "registry_snapshots",
        "schema_migrations",
        "system_meta",
        "transcript_entries",
    }
    with factory.connect(ConnectionAccess.READ_ONLY) as connection:
        rows = connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        ).fetchall()
        assert {row["name"] for row in rows} == expected
        assert "memory_transactions" not in expected
        assert "semantic_claims" not in expected


def test_repeated_migration_is_a_true_noop(tmp_path: Path) -> None:
    factory, runner = _migrate(tmp_path)
    with factory.connect() as connection:
        before = connection.execute(
            "SELECT version, name, migration_hash, applied_at FROM schema_migrations ORDER BY version"
        ).fetchall()
        report = runner.migrate(connection, applied_at=NOW.replace(hour=13))
        after = connection.execute(
            "SELECT version, name, migration_hash, applied_at FROM schema_migrations ORDER BY version"
        ).fetchall()
        assert not report.changed
        assert report.applied_now == ()
        assert [tuple(row) for row in after] == [tuple(row) for row in before]


def test_partial_valid_prefix_advances_without_reapplying_history(tmp_path: Path) -> None:
    short = MigrationCatalog(FOUNDATION_MIGRATIONS.migrations[:2])
    factory = _factory(tmp_path)
    with factory.connect() as connection:
        first = MigrationRunner(short).migrate(connection, applied_at=NOW)
        assert first.current_version == 2
        second = MigrationRunner().migrate(connection, applied_at=NOW)
        assert second.previous_version == 2
        assert tuple(item.version for item in second.applied_now) == (3, 4)


def test_failing_statement_rolls_back_ledger_and_all_prior_schema(tmp_path: Path) -> None:
    catalog = MigrationCatalog(
        (
            Migration(1, "first", ("CREATE TABLE should_rollback(value TEXT) STRICT",)),
            Migration(2, "broken", ("CREATE TABL invalid(value TEXT)",)),
        )
    )
    with _factory(tmp_path).connect() as connection:
        with pytest.raises(MigrationError, match="atomic schema migration"):
            MigrationRunner(catalog).migrate(connection, applied_at=NOW)
        rows = connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        ).fetchall()
        assert rows == []
        assert not MigrationRunner(catalog).inspect(connection).managed


def test_applied_hash_or_name_tampering_is_detected(tmp_path: Path) -> None:
    factory, runner = _migrate(tmp_path)
    with factory.connect() as connection:
        with connection.transaction():
            connection.execute(
                "UPDATE schema_migrations SET migration_hash=? WHERE version=2",
                (sha256_text("tampered").value,),
            )
        with pytest.raises(MigrationIntegrityError, match="differs from catalog"):
            runner.inspect(connection)


def test_noncanonical_applied_timestamp_is_detected(tmp_path: Path) -> None:
    factory, runner = _migrate(tmp_path)
    with factory.connect() as connection:
        with connection.transaction():
                connection.execute(
                    "UPDATE schema_migrations SET applied_at=? WHERE version=1",
                    ("2026-08-30 12:00:00.000000Z",),
                )
        with pytest.raises(MigrationIntegrityError, match="timestamp"):
            runner.inspect(connection)


def test_deleted_middle_record_breaks_contiguous_history(tmp_path: Path) -> None:
    factory, runner = _migrate(tmp_path)
    with factory.connect() as connection:
        with connection.transaction():
            connection.execute("DELETE FROM schema_migrations WHERE version=2")
        with pytest.raises(MigrationIntegrityError, match="contiguous"):
            runner.inspect(connection)


def test_database_newer_than_catalog_is_rejected(tmp_path: Path) -> None:
    factory, _ = _migrate(tmp_path)
    old_runner = MigrationRunner(MigrationCatalog(FOUNDATION_MIGRATIONS.migrations[:2]))
    with factory.connect() as connection:
        with pytest.raises(MigrationIntegrityError, match="newer"):
            old_runner.inspect(connection)


def test_changed_historical_statement_is_rejected(tmp_path: Path) -> None:
    factory, _ = _migrate(tmp_path)
    changed_first = replace(
        FOUNDATION_MIGRATIONS.migrations[0],
        statements=("CREATE TABLE system_meta(key TEXT PRIMARY KEY) STRICT",),
    )
    changed_catalog = MigrationCatalog(
        (changed_first, *FOUNDATION_MIGRATIONS.migrations[1:])
    )
    with factory.connect() as connection:
        with pytest.raises(MigrationIntegrityError, match="differs from catalog"):
            MigrationRunner(changed_catalog).inspect(connection)


def test_runner_requires_read_write_and_outer_transaction_ownership(tmp_path: Path) -> None:
    factory, runner = _migrate(tmp_path)
    with factory.connect(ConnectionAccess.READ_ONLY) as reader:
        with pytest.raises(MigrationError, match="read/write"):
            runner.migrate(reader, applied_at=NOW)
    with factory.connect() as writer:
        with writer.transaction():
            with pytest.raises(MigrationError, match="outer transaction"):
                runner.migrate(writer, applied_at=NOW)


def test_transcript_schema_enforces_project_turn_and_role_boundaries(tmp_path: Path) -> None:
    factory, _ = _migrate(tmp_path)
    identifier = "00000000-0000-4000-8000-000000000001"
    project = "00000000-0000-4000-8000-000000000002"
    turn = "00000000-0000-4000-8000-000000000003"
    with factory.connect() as connection:
        with connection.transaction():
            connection.execute(
                "INSERT INTO conversations VALUES (?, ?, ?)",
                (identifier, project, TIMESTAMP),
            )
            connection.execute(
                "INSERT INTO conversation_turns VALUES (?, ?, ?, ?, ?)",
                (turn, project, identifier, 1, TIMESTAMP),
            )
        with pytest.raises(sqlite3.IntegrityError):
            with connection.transaction():
                connection.execute(
                    "INSERT INTO transcript_entries VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        "00000000-0000-4000-8000-000000000004",
                        project,
                        identifier,
                        turn,
                        1,
                        "SYSTEM",
                        "hidden authority",
                        sha256_text("hidden authority").value,
                        TIMESTAMP,
                    ),
                )


def test_artifact_links_require_existing_exact_revisions(tmp_path: Path) -> None:
    factory, _ = _migrate(tmp_path)
    conversation = "00000000-0000-4000-8000-000000000001"
    project = "00000000-0000-4000-8000-000000000002"
    turn = "00000000-0000-4000-8000-000000000003"
    artifact = "00000000-0000-4000-8000-000000000004"
    with factory.connect() as connection:
        with connection.transaction():
            connection.execute(
                "INSERT INTO conversations VALUES (?, ?, ?)",
                (conversation, project, TIMESTAMP),
            )
            connection.execute(
                "INSERT INTO conversation_turns VALUES (?, ?, ?, ?, ?)",
                (turn, project, conversation, 1, TIMESTAMP),
            )
            connection.execute(
                "INSERT INTO artifacts VALUES (?, ?, ?, ?, ?, ?)",
                (artifact, project, turn, "R1_INTENT", "intent", TIMESTAMP),
            )
            connection.execute(
                "INSERT INTO artifact_revisions VALUES (?, ?, ?, ?, ?, ?)",
                (
                    artifact,
                    1,
                    "{}",
                    sha256_text("content").value,
                    sha256_text("envelope").value,
                    TIMESTAMP,
                ),
            )
        with pytest.raises(sqlite3.IntegrityError):
            with connection.transaction():
                connection.execute(
                    "INSERT INTO artifact_links VALUES (?, ?, ?, ?, ?, ?)",
                    (
                        artifact,
                        1,
                        1,
                        artifact,
                        2,
                        sha256_text("missing").value,
                    ),
                )


def test_applied_migration_rendering_is_machine_readable() -> None:
    record = AppliedMigration(
        version=1,
        name="host_metadata",
        migration_hash=FOUNDATION_MIGRATIONS.migrations[0].migration_hash,
        applied_at=TIMESTAMP,
    )
    assert record.to_value()["migration_hash"] == record.migration_hash.value
