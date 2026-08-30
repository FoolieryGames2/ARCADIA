# Phase A Item 12 — Hash-Verified SQLite Migrations

Date: 2026-08-30
Standing: **PASS — item complete; Gate A remains open**

## Authority implemented

- `Migration`, `MigrationCatalog`, and `MigrationRunner` define one immutable,
  forward-only schema authority. Catalog versions must be unique and contiguous
  from one; names are canonical tokens; every migration hashes its ordered SQL
  statements with Canonical JSON V1 and typed SHA-256. The complete catalog also
  has a pinned canonical hash.
- The migration ledger records exact version, name, migration hash, and canonical
  UTC application time. Before any upgrade, replay verifies the database ledger
  is a byte-identity prefix of the host catalog. Changed historical SQL/name/hash,
  missing middle records, malformed fields/timestamps, and databases newer than
  the running host fail closed.
- A truly empty SQLite file may be adopted. Any table, view, or trigger without
  the ARCADIA migration ledger makes the database unmanaged and is refused, so
  the host cannot silently claim or mutate a foreign database.
- The runner requires a managed read/write connection and owns one outer
  `BEGIN IMMEDIATE` transaction. Ledger creation, all pending DDL/indexes, and
  every applied record commit together. Any SQLite error rolls the entire batch
  back, including the bootstrap ledger. Valid prefixes advance without rerunning
  history; a fully current database is a true no-op.
- The frozen Phase A catalog contains four migrations: host `system_meta`, the
  separate conversation/turn/transcript substrate, immutable artifact identity/
  revisions/basis links, and versioned registry snapshots carrying project plus
  contract/schema/recipe/registry/runtime identity versions.
- Transcript rows have their own table and project/conversation/turn foreign-key
  domain. Artifact identities/revisions/links occupy separate tables with exact-
  revision basis foreign keys. Registry snapshots occupy their own versioned
  table. These schemas prepare but do not collapse the authority of the next
  three repositories.
- The carried-forward semantic-memory tables, `memory_commit_seq`, provisional
  standing, compensation, and PRC-success record are intentionally absent. The
  exact build order assigns installation of that frozen semantic substrate to
  Phase C, after the Phase A repositories and before normal Context memory use.

Pinned catalog hash:

```text
sha256:2d7d9660dddb818b188fdaf8c7153c850bb4812db6bd120e6a0d23b8c7762d6c
```

## Evidence

Commands: `check.bat` and `check_phase0.bat`

```text
328 tests passed
Ruff: PASS
strict MyPy: PASS (18 source files)
Phase 0 authority, dependency, model, llama.cpp, CUDA, and runtime hashes: PASS
```

The 25 migration tests cover pinned catalog/migration hashes, immutable and
strict definitions, contiguous versions/names, safe empty adoption, unmanaged
database refusal, complete atomic application/reporting, exact Phase A table set,
semantic-schema deferral, idempotency, valid-prefix advance, injected-DDL full
rollback, ledger hash/timestamp/deletion tampering, newer-database rejection,
changed-history rejection, read-only/outer-transaction refusal, transcript role
and project/turn constraints, exact artifact-revision links, and machine-readable
applied records.

Gate A remains open for the three authority-separated repositories. The next
exact-order item is `storage/transcript_repository.py`.
