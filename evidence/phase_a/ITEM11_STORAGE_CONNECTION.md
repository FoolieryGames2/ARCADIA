# Phase A Item 11 — Managed SQLite Connection Boundary

Date: 2026-08-30
Standing: **PASS — item complete; Gate A remains open**

## Authority implemented

- `SQLiteConnectionFactory` derives one database location from the strict Config
  V1 storage section and an existing resolved workspace root. Read/write opens
  create only the configured data directory; read-only opens require the database
  to exist. Resolved directory, file, and symlink targets must remain beneath the
  workspace root before and after opening.
- Every connection uses Python autocommit mode only as a substrate, exposes named
  `sqlite3.Row` values, and verifies the effective frozen settings: WAL journal
  mode, foreign-key enforcement, Config V1 busy timeout, `synchronous=NORMAL`,
  and working FTS5 virtual-table support. Missing mandatory behavior fails closed.
- Read-only connections use SQLite URI `mode=ro` plus `query_only=ON`. They cannot
  create the configured directory/database and expose no write transaction path.
- `DatabaseConnection.transaction()` is the sole transaction owner. It defaults
  to `BEGIN IMMEDIATE`, also supports explicit deferred/exclusive modes, rejects
  nesting and unmanaged transaction state, commits only after a clean body, and
  rolls back on every `BaseException`, constraint failure, or connection close.
  DDL and DML therefore share the same rollback boundary.
- SQLite's authorizer enforces the boundary below SQL text parsing: all mutations
  require an active managed transaction; caller-issued BEGIN/COMMIT/ROLLBACK,
  PRAGMA, ATTACH, and DETACH are denied. This prevents repositories from changing
  verified connection policy, escaping to another database, or autocommitting a
  durable mutation around the Persistence Host.
- The restricted cursor exposes row retrieval/count/description metadata but not
  the raw SQLite connection, so callers cannot recover an unmanaged commit path
  through `cursor.connection`. Multi-row writes remain parameterized and subject
  to the same transaction authorizer.
- Schema definitions, migration ordering/hashes, repository SQL, semantic-memory
  ownership, and PRC atomicity remain assigned to the next frozen migration and
  repository items.

## Evidence

Commands: `check.bat` and `check_phase0.bat`

```text
303 tests passed
Ruff: PASS
strict MyPy: PASS (17 source files)
Phase 0 authority, dependency, model, llama.cpp, CUDA, and runtime hashes: PASS
```

The 17 connection tests cover workspace containment, exact configured location,
directory creation timing, strict input types, effective WAL/foreign-key/timeout/
synchronous/FTS5 settings, named rows, raw-connection concealment, transaction-
only writes, atomic DDL+DML commit and rollback, foreign-key rollback, nested and
manual transaction rejection, PRAGMA/ATTACH denial, parameterized batches,
invalid parameter-row rejection, read-only non-creation/query/write denial,
close-time rollback, data-directory collision handling, invalid inputs, missing-
FTS5 failure, and real two-connection busy-timeout lock behavior.

Gate A remains open for migrations and the authority-separated repositories. The
next exact-order item is `storage/migrations.py`.
