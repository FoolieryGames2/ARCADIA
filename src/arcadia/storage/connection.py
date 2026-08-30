"""Workspace-contained SQLite connections and rollback-safe transactions."""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator, Sequence
from contextlib import contextmanager
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any, cast

from arcadia.core.config import StorageConfig


class StorageConnectionError(RuntimeError):
    """Base error for an invalid or unavailable SQLite connection boundary."""


class StoragePathError(StorageConnectionError):
    """The configured database location is not a safe workspace-contained path."""


class StorageFeatureError(StorageConnectionError):
    """SQLite cannot provide a mandatory frozen feature or connection setting."""


class StorageAccessError(StorageConnectionError):
    """A caller attempted to bypass the managed storage authority boundary."""


class TransactionStateError(StorageConnectionError):
    """A transaction was nested, escaped, or otherwise left in an illegal state."""


class ConnectionAccess(StrEnum):
    READ_WRITE = "READ_WRITE"
    READ_ONLY = "READ_ONLY"


class TransactionMode(StrEnum):
    DEFERRED = "DEFERRED"
    IMMEDIATE = "IMMEDIATE"
    EXCLUSIVE = "EXCLUSIVE"


@dataclass(frozen=True, slots=True)
class ConnectionSettings:
    """Verified effective settings for one opened SQLite connection."""

    access: ConnectionAccess
    database_path: Path
    journal_mode: str
    foreign_keys: bool
    busy_timeout_ms: int
    synchronous: int
    fts5_available: bool


class DatabaseCursor:
    """Restricted cursor view that does not expose the raw SQLite connection."""

    __slots__ = ("__cursor",)

    def __init__(self, cursor: sqlite3.Cursor) -> None:
        self.__cursor = cursor

    @property
    def rowcount(self) -> int:
        return self.__cursor.rowcount

    @property
    def lastrowid(self) -> int | None:
        value = self.__cursor.lastrowid
        return value if type(value) is int else None

    @property
    def description(self) -> tuple[tuple[Any, ...], ...] | None:
        return self.__cursor.description

    def fetchone(self) -> sqlite3.Row | None:
        return cast(sqlite3.Row | None, self.__cursor.fetchone())

    def fetchmany(self, size: int | None = None) -> list[sqlite3.Row]:
        if size is None:
            return self.__cursor.fetchmany()
        if type(size) is not int or size < 0:
            raise StorageAccessError("fetchmany size must be a nonnegative integer")
        return self.__cursor.fetchmany(size)

    def fetchall(self) -> list[sqlite3.Row]:
        return self.__cursor.fetchall()

    def close(self) -> None:
        self.__cursor.close()

    def __iter__(self) -> Iterator[sqlite3.Row]:
        return iter(self.__cursor)


_MUTATING_ACTIONS = frozenset(
    action
    for action in (
        getattr(sqlite3, "SQLITE_ALTER_TABLE", None),
        getattr(sqlite3, "SQLITE_ANALYZE", None),
        getattr(sqlite3, "SQLITE_CREATE_INDEX", None),
        getattr(sqlite3, "SQLITE_CREATE_TABLE", None),
        getattr(sqlite3, "SQLITE_CREATE_TEMP_INDEX", None),
        getattr(sqlite3, "SQLITE_CREATE_TEMP_TABLE", None),
        getattr(sqlite3, "SQLITE_CREATE_TEMP_TRIGGER", None),
        getattr(sqlite3, "SQLITE_CREATE_TEMP_VIEW", None),
        getattr(sqlite3, "SQLITE_CREATE_TRIGGER", None),
        getattr(sqlite3, "SQLITE_CREATE_VIEW", None),
        getattr(sqlite3, "SQLITE_CREATE_VTABLE", None),
        getattr(sqlite3, "SQLITE_DELETE", None),
        getattr(sqlite3, "SQLITE_DROP_INDEX", None),
        getattr(sqlite3, "SQLITE_DROP_TABLE", None),
        getattr(sqlite3, "SQLITE_DROP_TEMP_INDEX", None),
        getattr(sqlite3, "SQLITE_DROP_TEMP_TABLE", None),
        getattr(sqlite3, "SQLITE_DROP_TEMP_TRIGGER", None),
        getattr(sqlite3, "SQLITE_DROP_TEMP_VIEW", None),
        getattr(sqlite3, "SQLITE_DROP_TRIGGER", None),
        getattr(sqlite3, "SQLITE_DROP_VIEW", None),
        getattr(sqlite3, "SQLITE_DROP_VTABLE", None),
        getattr(sqlite3, "SQLITE_INSERT", None),
        getattr(sqlite3, "SQLITE_REINDEX", None),
        getattr(sqlite3, "SQLITE_UPDATE", None),
    )
    if action is not None
)
_FORBIDDEN_ACTIONS = frozenset(
    action
    for action in (
        getattr(sqlite3, "SQLITE_ATTACH", None),
        getattr(sqlite3, "SQLITE_DETACH", None),
        getattr(sqlite3, "SQLITE_PRAGMA", None),
    )
    if action is not None
)


class DatabaseConnection:
    """Managed connection that admits writes only inside its transaction guard."""

    __slots__ = (
        "__access",
        "__closed",
        "__connection",
        "__control_authorized",
        "__transaction_active",
        "settings",
    )

    def __init__(
        self,
        connection: sqlite3.Connection,
        *,
        access: ConnectionAccess,
        settings: ConnectionSettings,
    ) -> None:
        self.__connection = connection
        self.__access = access
        self.__closed = False
        self.__transaction_active = False
        self.__control_authorized = False
        self.settings = settings
        connection.set_authorizer(self.__authorize)

    @property
    def access(self) -> ConnectionAccess:
        return self.__access

    @property
    def closed(self) -> bool:
        return self.__closed

    @property
    def in_transaction(self) -> bool:
        return not self.__closed and self.__connection.in_transaction

    def execute(
        self, statement: str, parameters: Sequence[object] = ()
    ) -> DatabaseCursor:
        self.__require_open()
        if type(statement) is not str or not statement.strip():
            raise StorageAccessError("SQL statement must be a nonempty string")
        if isinstance(parameters, (str, bytes, bytearray)) or not isinstance(
            parameters, Sequence
        ):
            raise StorageAccessError("SQL parameters must be a positional sequence")
        try:
            return DatabaseCursor(self.__connection.execute(statement, parameters))
        except sqlite3.DatabaseError as exc:
            self.__translate_denial(exc)
            raise

    def executemany(
        self, statement: str, parameters: Sequence[Sequence[object]]
    ) -> DatabaseCursor:
        self.__require_open()
        if type(statement) is not str or not statement.strip():
            raise StorageAccessError("SQL statement must be a nonempty string")
        if isinstance(parameters, (str, bytes, bytearray)) or not isinstance(
            parameters, Sequence
        ):
            raise StorageAccessError("SQL parameter rows must be an immutable sequence")
        if any(
            isinstance(row, (str, bytes, bytearray)) or not isinstance(row, Sequence)
            for row in parameters
        ):
            raise StorageAccessError("each SQL parameter row must be a positional sequence")
        try:
            return DatabaseCursor(self.__connection.executemany(statement, parameters))
        except sqlite3.DatabaseError as exc:
            self.__translate_denial(exc)
            raise

    @contextmanager
    def transaction(
        self, mode: TransactionMode = TransactionMode.IMMEDIATE
    ) -> Iterator[DatabaseConnection]:
        self.__require_open()
        if type(mode) is not TransactionMode:
            raise StorageAccessError("mode must be a TransactionMode")
        if self.__access is ConnectionAccess.READ_ONLY:
            raise StorageAccessError("read-only connections cannot begin write transactions")
        if self.__transaction_active or self.__connection.in_transaction:
            raise TransactionStateError("nested or unmanaged transactions are forbidden")
        self.__transaction_active = True
        try:
            self.__run_control(f"BEGIN {mode.value}")
            try:
                yield self
                if self.__closed:
                    raise TransactionStateError("connection closed inside managed transaction")
                if not self.__connection.in_transaction:
                    raise TransactionStateError("managed transaction ended outside its owner")
                self.__run_control("COMMIT")
            except BaseException:
                if not self.__closed and self.__connection.in_transaction:
                    self.__run_control("ROLLBACK")
                raise
        finally:
            self.__transaction_active = False

    def close(self) -> None:
        if self.__closed:
            return
        try:
            if self.__connection.in_transaction:
                self.__run_control("ROLLBACK")
        finally:
            self.__connection.close()
            self.__closed = True
            self.__transaction_active = False

    def __enter__(self) -> DatabaseConnection:
        self.__require_open()
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def __authorize(
        self,
        action: int,
        _argument_one: str | None,
        _argument_two: str | None,
        _database: str | None,
        _trigger: str | None,
    ) -> int:
        if action in _FORBIDDEN_ACTIONS:
            return sqlite3.SQLITE_DENY
        if action == getattr(sqlite3, "SQLITE_TRANSACTION", -1):
            return sqlite3.SQLITE_OK if self.__control_authorized else sqlite3.SQLITE_DENY
        if action in _MUTATING_ACTIONS:
            if self.__access is ConnectionAccess.READ_ONLY or not self.__transaction_active:
                return sqlite3.SQLITE_DENY
        return sqlite3.SQLITE_OK

    def __run_control(self, statement: str) -> None:
        self.__control_authorized = True
        try:
            self.__connection.execute(statement)
        finally:
            self.__control_authorized = False

    def __require_open(self) -> None:
        if self.__closed:
            raise StorageAccessError("database connection is closed")

    @staticmethod
    def __translate_denial(error: sqlite3.DatabaseError) -> None:
        if "not authorized" in str(error).lower():
            raise StorageAccessError(
                "SQL bypassed transaction, connection, or PRAGMA authority"
            ) from error


@dataclass(frozen=True, slots=True)
class SQLiteConnectionFactory:
    """Opens only the configured database beneath one resolved workspace root."""

    workspace_root: Path
    storage: StorageConfig

    def __post_init__(self) -> None:
        if not isinstance(self.workspace_root, Path):
            raise StoragePathError("workspace_root must be a Path")
        if type(self.storage) is not StorageConfig:
            raise StorageConnectionError("storage must be a StorageConfig")
        root = self.workspace_root.resolve()
        if not root.is_dir():
            raise StoragePathError("workspace_root must be an existing directory")
        object.__setattr__(self, "workspace_root", root)
        self._validate_path(self.database_path)

    @property
    def data_directory(self) -> Path:
        return self.workspace_root / self.storage.data_dir

    @property
    def database_path(self) -> Path:
        return self.data_directory / self.storage.database_name

    def open(
        self, access: ConnectionAccess = ConnectionAccess.READ_WRITE
    ) -> DatabaseConnection:
        if type(access) is not ConnectionAccess:
            raise StorageAccessError("access must be a ConnectionAccess")
        if access is ConnectionAccess.READ_WRITE:
            try:
                self.data_directory.mkdir(parents=True, exist_ok=True)
            except OSError as exc:
                raise StoragePathError("cannot create configured data directory") from exc
            self._validate_path(self.data_directory)
            self._validate_path(self.database_path)
            target = str(self.database_path)
            uri = False
        else:
            if not self.database_path.is_file():
                raise StoragePathError("read-only database must already exist")
            self._validate_path(self.database_path)
            target = f"{self.database_path.as_uri()}?mode=ro"
            uri = True
        try:
            raw = sqlite3.connect(
                target,
                timeout=self.storage.busy_timeout_ms / 1000,
                detect_types=0,
                isolation_level=None,
                check_same_thread=True,
                uri=uri,
            )
        except sqlite3.Error as exc:
            raise StorageConnectionError("cannot open configured SQLite database") from exc
        try:
            settings = self._configure(raw, access)
            self._validate_path(self.database_path)
            return DatabaseConnection(raw, access=access, settings=settings)
        except BaseException:
            raw.close()
            raise

    @contextmanager
    def connect(
        self, access: ConnectionAccess = ConnectionAccess.READ_WRITE
    ) -> Iterator[DatabaseConnection]:
        connection = self.open(access)
        try:
            yield connection
        finally:
            connection.close()

    def _configure(
        self, connection: sqlite3.Connection, access: ConnectionAccess
    ) -> ConnectionSettings:
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        journal_mode = str(connection.execute("PRAGMA journal_mode = WAL").fetchone()[0])
        connection.execute("PRAGMA synchronous = NORMAL")
        connection.execute(f"PRAGMA busy_timeout = {self.storage.busy_timeout_ms}")
        foreign_keys = int(connection.execute("PRAGMA foreign_keys").fetchone()[0])
        busy_timeout = int(connection.execute("PRAGMA busy_timeout").fetchone()[0])
        synchronous = int(connection.execute("PRAGMA synchronous").fetchone()[0])
        if journal_mode.lower() != "wal":
            raise StorageFeatureError("configured database did not enter WAL journal mode")
        if foreign_keys != 1:
            raise StorageFeatureError("SQLite foreign-key enforcement is unavailable")
        if busy_timeout != self.storage.busy_timeout_ms:
            raise StorageFeatureError("SQLite busy timeout does not match Config V1")
        fts5_available = self._verify_fts5(connection)
        if self.storage.require_fts5 and not fts5_available:
            raise StorageFeatureError("SQLite FTS5 is required but unavailable")
        if access is ConnectionAccess.READ_ONLY:
            connection.execute("PRAGMA query_only = ON")
            query_only = int(connection.execute("PRAGMA query_only").fetchone()[0])
            if query_only != 1:
                raise StorageFeatureError("read-only connection did not enter query-only mode")
        return ConnectionSettings(
            access=access,
            database_path=self.database_path,
            journal_mode=journal_mode.lower(),
            foreign_keys=foreign_keys == 1,
            busy_timeout_ms=busy_timeout,
            synchronous=synchronous,
            fts5_available=fts5_available,
        )

    @staticmethod
    def _verify_fts5(connection: sqlite3.Connection) -> bool:
        try:
            connection.execute(
                "CREATE VIRTUAL TABLE temp.__arcadia_fts5_probe USING fts5(content)"
            )
            connection.execute("DROP TABLE temp.__arcadia_fts5_probe")
        except sqlite3.Error:
            return False
        return True

    def _validate_path(self, path: Path) -> None:
        try:
            resolved = path.resolve()
        except OSError as exc:
            raise StoragePathError("cannot resolve configured database path") from exc
        if not resolved.is_relative_to(self.workspace_root):
            raise StoragePathError("configured database path escapes the workspace root")
