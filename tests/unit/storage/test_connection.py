from __future__ import annotations

import sqlite3
from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from arcadia.core.config import StorageConfig
from arcadia.storage.connection import (
    ConnectionAccess,
    SQLiteConnectionFactory,
    StorageAccessError,
    StorageConnectionError,
    StorageFeatureError,
    StoragePathError,
    TransactionMode,
    TransactionStateError,
)


def _storage(*, timeout: int = 5000) -> StorageConfig:
    return StorageConfig(
        data_dir="runtime-data",
        database_name="arcadia.sqlite3",
        busy_timeout_ms=timeout,
        require_fts5=True,
    )


def _factory(root: Path, *, timeout: int = 5000) -> SQLiteConnectionFactory:
    return SQLiteConnectionFactory(workspace_root=root, storage=_storage(timeout=timeout))


def test_factory_opens_only_configured_workspace_database(tmp_path: Path) -> None:
    factory = _factory(tmp_path)
    assert factory.database_path == tmp_path / "runtime-data" / "arcadia.sqlite3"
    assert not factory.data_directory.exists()

    with factory.connect() as connection:
        assert factory.database_path.is_file()
        assert connection.settings.database_path == factory.database_path
        assert connection.settings.access is ConnectionAccess.READ_WRITE

    assert connection.closed
    with pytest.raises(FrozenInstanceError):
        factory.workspace_root = Path("changed")  # type: ignore[misc]


def test_factory_requires_existing_path_root_and_strict_types(tmp_path: Path) -> None:
    with pytest.raises(StoragePathError, match="existing directory"):
        _factory(tmp_path / "missing")
    with pytest.raises(StoragePathError, match="must be a Path"):
        SQLiteConnectionFactory(workspace_root=str(tmp_path), storage=_storage())  # type: ignore[arg-type]
    with pytest.raises(StorageConnectionError, match="StorageConfig"):
        SQLiteConnectionFactory(workspace_root=tmp_path, storage=object())  # type: ignore[arg-type]


def test_data_directory_collision_fails_as_storage_path_error(tmp_path: Path) -> None:
    (tmp_path / "runtime-data").write_text("not a directory", encoding="utf-8")
    with pytest.raises(StoragePathError, match="create configured data directory"):
        _factory(tmp_path).open()


def test_every_connection_verifies_frozen_sqlite_settings(tmp_path: Path) -> None:
    with _factory(tmp_path, timeout=137).connect() as connection:
        settings = connection.settings
        assert settings.journal_mode == "wal"
        assert settings.foreign_keys
        assert settings.busy_timeout_ms == 137
        assert settings.synchronous == 1  # SQLite NORMAL
        assert settings.fts5_available


def test_rows_are_named_and_cursor_does_not_expose_raw_connection(tmp_path: Path) -> None:
    with _factory(tmp_path).connect() as connection:
        row = connection.execute("SELECT 7 AS answer").fetchone()
        assert row is not None
        assert row["answer"] == 7
        cursor = connection.execute("SELECT 1")
        assert not hasattr(cursor, "connection")


def test_writes_require_managed_transaction_and_commit_atomically(tmp_path: Path) -> None:
    with _factory(tmp_path).connect() as connection:
        with pytest.raises(StorageAccessError, match="bypassed"):
            connection.execute("CREATE TABLE items(value TEXT NOT NULL)")

        with connection.transaction() as transaction:
            transaction.execute("CREATE TABLE items(value TEXT NOT NULL)")
            transaction.execute("INSERT INTO items(value) VALUES (?)", ("kept",))

        row = connection.execute("SELECT value FROM items").fetchone()
        assert row is not None and row["value"] == "kept"
        assert not connection.in_transaction


def test_exception_rolls_back_ddl_and_dml_together(tmp_path: Path) -> None:
    with _factory(tmp_path).connect() as connection:
        with pytest.raises(RuntimeError, match="fail"):
            with connection.transaction():
                connection.execute("CREATE TABLE rolled_back(value TEXT)")
                connection.execute("INSERT INTO rolled_back VALUES ('lost')")
                raise RuntimeError("fail")

        row = connection.execute(
            "SELECT count(*) AS count FROM sqlite_master WHERE name = ?", ("rolled_back",)
        ).fetchone()
        assert row is not None and row["count"] == 0


def test_foreign_keys_are_enforced_and_violation_rolls_back(tmp_path: Path) -> None:
    with _factory(tmp_path).connect() as connection:
        with connection.transaction():
            connection.execute("CREATE TABLE parent(id INTEGER PRIMARY KEY)")
            connection.execute(
                "CREATE TABLE child(parent_id INTEGER REFERENCES parent(id))"
            )

        with pytest.raises(sqlite3.IntegrityError):
            with connection.transaction():
                connection.execute("INSERT INTO child(parent_id) VALUES (99)")
        row = connection.execute("SELECT count(*) AS count FROM child").fetchone()
        assert row is not None and row["count"] == 0


def test_nested_and_unmanaged_transaction_control_are_rejected(tmp_path: Path) -> None:
    with _factory(tmp_path).connect() as connection:
        with connection.transaction(TransactionMode.DEFERRED):
            with pytest.raises(TransactionStateError, match="nested"):
                with connection.transaction():
                    pass
            with pytest.raises(StorageAccessError, match="bypassed"):
                connection.execute("COMMIT")
            assert connection.in_transaction

        with pytest.raises(StorageAccessError, match="bypassed"):
            connection.execute("BEGIN IMMEDIATE")


@pytest.mark.parametrize(
    "statement",
    [
        "PRAGMA foreign_keys = OFF",
        "/* attempted bypass */ -- still direct caller SQL\n PRAGMA foreign_keys = OFF",
        "/* attempted bypass */ PRAGMA(foreign_keys)",
        "ATTACH DATABASE ':memory:' AS escaped",
    ],
)
def test_connection_settings_and_database_scope_cannot_be_bypassed(
    tmp_path: Path, statement: str
) -> None:
    with _factory(tmp_path).connect() as connection:
        with connection.transaction():
            with pytest.raises(StorageAccessError, match="bypassed"):
                connection.execute(statement)


def test_executemany_is_transaction_bound_and_parameterized(tmp_path: Path) -> None:
    with _factory(tmp_path).connect() as connection:
        with connection.transaction():
            connection.execute("CREATE TABLE batch(value INTEGER NOT NULL)")
            cursor = connection.executemany(
                "INSERT INTO batch(value) VALUES (?)", ((1,), (2,), (3,))
            )
            assert cursor.rowcount == 3
        rows = connection.execute("SELECT value FROM batch ORDER BY value").fetchall()
        assert [row["value"] for row in rows] == [1, 2, 3]
        with pytest.raises(StorageAccessError, match="each SQL parameter row"):
            connection.executemany("SELECT ?", ("not-a-row",))  # type: ignore[arg-type]


def test_read_only_connection_requires_existing_database_and_denies_writes(
    tmp_path: Path,
) -> None:
    factory = _factory(tmp_path)
    with pytest.raises(StoragePathError, match="already exist"):
        factory.open(ConnectionAccess.READ_ONLY)
    assert not factory.data_directory.exists()

    with factory.connect() as writer:
        with writer.transaction():
            writer.execute("CREATE TABLE visible(value TEXT)")
            writer.execute("INSERT INTO visible VALUES ('yes')")

    with factory.connect(ConnectionAccess.READ_ONLY) as reader:
        row = reader.execute("SELECT value FROM visible").fetchone()
        assert row is not None and row["value"] == "yes"
        assert reader.settings.access is ConnectionAccess.READ_ONLY
        with pytest.raises(StorageAccessError, match="read-only"):
            with reader.transaction():
                pass
        with pytest.raises(StorageAccessError, match="bypassed"):
            reader.execute("DELETE FROM visible")


def test_close_rolls_back_open_transaction_and_is_idempotent(tmp_path: Path) -> None:
    factory = _factory(tmp_path)
    connection = factory.open()
    manager = connection.transaction()
    manager.__enter__()
    connection.execute("CREATE TABLE abandoned(value TEXT)")
    connection.close()
    connection.close()
    with pytest.raises(TransactionStateError, match="closed inside"):
        manager.__exit__(None, None, None)

    with factory.connect() as reopened:
        row = reopened.execute(
            "SELECT count(*) AS count FROM sqlite_master WHERE name='abandoned'"
        ).fetchone()
        assert row is not None and row["count"] == 0
    with pytest.raises(StorageAccessError, match="closed"):
        connection.execute("SELECT 1")


def test_invalid_sql_inputs_and_enum_coercion_are_rejected(tmp_path: Path) -> None:
    with _factory(tmp_path).connect() as connection:
        with pytest.raises(StorageAccessError, match="nonempty"):
            connection.execute("")
        with pytest.raises(StorageAccessError, match="positional"):
            connection.execute("SELECT 1", "bad")  # type: ignore[arg-type]
        with pytest.raises(StorageAccessError, match="ConnectionAccess"):
            _factory(tmp_path).open("READ_WRITE")  # type: ignore[arg-type]
        with pytest.raises(StorageAccessError, match="TransactionMode"):
            with connection.transaction("IMMEDIATE"):  # type: ignore[arg-type]
                pass


def test_missing_fts5_fails_closed(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        SQLiteConnectionFactory,
        "_verify_fts5",
        staticmethod(lambda _connection: False),
    )
    with pytest.raises(StorageFeatureError, match="FTS5"):
        _factory(tmp_path).open()


def test_file_lock_honors_configured_busy_timeout(tmp_path: Path) -> None:
    factory = _factory(tmp_path, timeout=25)
    first = factory.open()
    second = factory.open()
    try:
        with first.transaction():
            first.execute("CREATE TABLE lock_probe(value INTEGER)")
            with pytest.raises(sqlite3.OperationalError, match="locked"):
                with second.transaction(TransactionMode.IMMEDIATE):
                    pass
        assert not second.in_transaction
    finally:
        first.close()
        second.close()
