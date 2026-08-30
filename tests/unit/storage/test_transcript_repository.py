from __future__ import annotations

import sqlite3
from dataclasses import FrozenInstanceError, replace
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from arcadia.core.config import StorageConfig
from arcadia.core.hashing import sha256_text
from arcadia.core.ids import CanonicalId
from arcadia.storage.connection import SQLiteConnectionFactory
from arcadia.storage.migrations import MigrationRunner
from arcadia.storage.transcript_repository import (
    MAX_RECENT_EXCHANGES,
    MAX_TARGETED_QUERY_CHARACTERS,
    MAX_TARGETED_QUERY_TERMS,
    MAX_TARGETED_TURNS,
    CompletedExchange,
    TranscriptConflictError,
    TranscriptFieldError,
    TranscriptIntegrityError,
    TranscriptNotFoundError,
    TranscriptRepository,
    TranscriptRepositoryError,
    TranscriptRole,
    TranscriptSearchHit,
    TurnStatus,
)

NOW = datetime(2026, 8, 30, 12, 0, tzinfo=UTC)


def _factory(root: Path) -> SQLiteConnectionFactory:
    return SQLiteConnectionFactory(
        workspace_root=root,
        storage=StorageConfig(
            data_dir="data",
            database_name="transcript.sqlite3",
            busy_timeout_ms=1000,
            require_fts5=True,
        ),
    )


def _repository(
    root: Path, *, project_id: CanonicalId | None = None
) -> TranscriptRepository:
    factory = _factory(root)
    with factory.connect() as connection:
        MigrationRunner().migrate(connection, applied_at=NOW)
    return TranscriptRepository(factory, project_id or CanonicalId.new())


def _conversation(
    repository: TranscriptRepository, *, at: datetime = NOW
) -> CanonicalId:
    conversation_id = CanonicalId.new()
    repository.create_conversation(conversation_id=conversation_id, created_at=at)
    return conversation_id


def _complete(
    repository: TranscriptRepository,
    conversation_id: CanonicalId,
    *,
    user: str,
    assistant: str,
    at: datetime,
) -> CompletedExchange:
    turn_id = CanonicalId.new()
    repository.append_user_turn(
        conversation_id=conversation_id,
        turn_id=turn_id,
        content=user,
        created_at=at,
    )
    return repository.commit_published_response(
        turn_id=turn_id,
        result_hash=sha256_text(assistant),
        exact_published_text=assistant,
        committed_at=at + timedelta(seconds=1),
    )


def test_repository_requires_current_migrated_schema(tmp_path: Path) -> None:
    factory = _factory(tmp_path)
    with factory.connect():
        pass
    repository = TranscriptRepository(factory, CanonicalId.new())
    with pytest.raises(TranscriptRepositoryError, match="schema is not current"):
        repository.transcript_commit_seq()


def test_repository_identity_is_strict_and_immutable(tmp_path: Path) -> None:
    factory = _factory(tmp_path)
    with pytest.raises(TranscriptFieldError, match="factory"):
        TranscriptRepository(object(), CanonicalId.new())  # type: ignore[arg-type]
    with pytest.raises(TranscriptFieldError, match="project_id"):
        TranscriptRepository(factory, "project")  # type: ignore[arg-type]
    repository = _repository(tmp_path)
    with pytest.raises(FrozenInstanceError):
        repository.project_id = CanonicalId.new()  # type: ignore[misc]


def test_conversation_creation_is_exact_and_idempotent(tmp_path: Path) -> None:
    repository = _repository(tmp_path)
    conversation_id = CanonicalId.new()
    first = repository.create_conversation(
        conversation_id=conversation_id, created_at=NOW
    )
    second = repository.create_conversation(
        conversation_id=conversation_id, created_at=NOW
    )
    assert first == second
    assert first.project_id == repository.project_id
    with pytest.raises(TranscriptConflictError, match="different immutable"):
        repository.create_conversation(
            conversation_id=conversation_id, created_at=NOW + timedelta(seconds=1)
        )


def test_conversation_uuid_cannot_cross_project_scope(tmp_path: Path) -> None:
    project_one = CanonicalId.new()
    project_two = CanonicalId.new()
    first = _repository(tmp_path, project_id=project_one)
    second = TranscriptRepository(first.factory, project_two)
    conversation_id = _conversation(first)
    with pytest.raises(TranscriptConflictError):
        second.create_conversation(conversation_id=conversation_id, created_at=NOW)
    with pytest.raises(TranscriptConflictError, match="another project"):
        second.append_user_turn(
            conversation_id=conversation_id,
            turn_id=CanonicalId.new(),
            content="wrong scope",
            created_at=NOW,
        )


def test_user_turn_is_append_only_hashed_and_idempotent(tmp_path: Path) -> None:
    repository = _repository(tmp_path)
    conversation_id = _conversation(repository)
    turn_id = CanonicalId.new()
    first = repository.append_user_turn(
        conversation_id=conversation_id,
        turn_id=turn_id,
        content="  preserve exact whitespace  ",
        created_at=NOW,
    )
    second = repository.append_user_turn(
        conversation_id=conversation_id,
        turn_id=turn_id,
        content="  preserve exact whitespace  ",
        created_at=NOW,
    )
    assert first == second
    assert first.turn.turn_ordinal == 1
    assert first.turn.status is TurnStatus.OPEN
    assert first.user_entry.entry_ordinal == 1
    assert first.user_entry.role is TranscriptRole.USER
    assert first.user_entry.content_hash == sha256_text("  preserve exact whitespace  ")
    assert repository.transcript_commit_seq() == 0


def test_turn_retry_cannot_change_content_time_or_scope(tmp_path: Path) -> None:
    repository = _repository(tmp_path)
    conversation_id = _conversation(repository)
    other_conversation = _conversation(repository, at=NOW + timedelta(seconds=1))
    turn_id = CanonicalId.new()
    repository.append_user_turn(
        conversation_id=conversation_id,
        turn_id=turn_id,
        content="original",
        created_at=NOW,
    )
    for changed in (
        {"conversation_id": conversation_id, "content": "changed", "created_at": NOW},
        {
            "conversation_id": conversation_id,
            "content": "original",
            "created_at": NOW + timedelta(seconds=1),
        },
        {"conversation_id": other_conversation, "content": "original", "created_at": NOW},
    ):
        with pytest.raises(TranscriptConflictError):
            repository.append_user_turn(turn_id=turn_id, **changed)


def test_turn_requires_existing_conversation_and_strict_content(tmp_path: Path) -> None:
    repository = _repository(tmp_path)
    with pytest.raises(TranscriptNotFoundError):
        repository.append_user_turn(
            conversation_id=CanonicalId.new(),
            turn_id=CanonicalId.new(),
            content="orphan",
            created_at=NOW,
        )
    conversation_id = _conversation(repository)
    with pytest.raises(TranscriptFieldError, match="nonempty"):
        repository.append_user_turn(
            conversation_id=conversation_id,
            turn_id=CanonicalId.new(),
            content="",
            created_at=NOW,
        )


def test_published_response_commits_exact_text_relation_and_sequence(tmp_path: Path) -> None:
    repository = _repository(tmp_path)
    conversation_id = _conversation(repository)
    exchange = _complete(
        repository,
        conversation_id,
        user="What happened?",
        assistant="Exactly this response.\n",
        at=NOW,
    )
    assert exchange.turn.status is TurnStatus.COMPLETED
    assert exchange.assistant_entry.content == "Exactly this response.\n"
    assert exchange.assistant_entry.content_hash == sha256_text("Exactly this response.\n")
    assert exchange.publication.result_hash == exchange.assistant_entry.content_hash
    assert exchange.publication.transcript_commit_seq == 1
    assert repository.transcript_commit_seq() == 1


def test_hash_mismatch_cannot_store_failed_draft_or_complete_turn(tmp_path: Path) -> None:
    repository = _repository(tmp_path)
    conversation_id = _conversation(repository)
    turn_id = CanonicalId.new()
    repository.append_user_turn(
        conversation_id=conversation_id,
        turn_id=turn_id,
        content="question",
        created_at=NOW,
    )
    with pytest.raises(TranscriptIntegrityError, match="does not match"):
        repository.commit_published_response(
            turn_id=turn_id,
            result_hash=sha256_text("validated result"),
            exact_published_text="failed draft",
            committed_at=NOW,
        )
    assert repository.transcript_commit_seq() == 0
    assert repository.load_recent_exchanges(conversation_id=conversation_id, limit=1) == ()
    with repository.factory.connect() as connection:
        count = connection.execute(
            "SELECT count(*) AS count FROM transcript_entries WHERE turn_uuid=?",
            (str(turn_id),),
        ).fetchone()
        assert count is not None and count["count"] == 1


def test_publication_retry_uses_turn_and_result_hash_without_duplication(tmp_path: Path) -> None:
    repository = _repository(tmp_path)
    conversation_id = _conversation(repository)
    turn_id = CanonicalId.new()
    repository.append_user_turn(
        conversation_id=conversation_id,
        turn_id=turn_id,
        content="question",
        created_at=NOW,
    )
    first = repository.commit_published_response(
        turn_id=turn_id,
        result_hash=sha256_text("answer"),
        exact_published_text="answer",
        committed_at=NOW,
    )
    retry = repository.commit_published_response(
        turn_id=turn_id,
        result_hash=sha256_text("answer"),
        exact_published_text="answer",
        committed_at=NOW + timedelta(hours=1),
    )
    assert retry == first
    assert repository.transcript_commit_seq() == 1
    with pytest.raises(TranscriptConflictError, match="different immutable"):
        repository.commit_published_response(
            turn_id=turn_id,
            result_hash=sha256_text("different"),
            exact_published_text="different",
            committed_at=NOW,
        )


def test_recent_history_is_completed_exchange_only_and_chronological(tmp_path: Path) -> None:
    repository = _repository(tmp_path)
    conversation_id = _conversation(repository)
    exchanges = [
        _complete(
            repository,
            conversation_id,
            user=f"user {index}",
            assistant=f"assistant {index}",
            at=NOW + timedelta(minutes=index),
        )
        for index in range(3)
    ]
    repository.append_user_turn(
        conversation_id=conversation_id,
        turn_id=CanonicalId.new(),
        content="still open",
        created_at=NOW + timedelta(minutes=4),
    )
    recent = repository.load_recent_exchanges(conversation_id=conversation_id, limit=2)
    assert recent == tuple(exchanges[-2:])
    assert [item.turn.turn_ordinal for item in recent] == [2, 3]
    assert repository.transcript_commit_seq() == 3


@pytest.mark.parametrize("limit", [0, True, MAX_RECENT_EXCHANGES + 1])
def test_recent_history_limit_is_strictly_bounded(tmp_path: Path, limit: object) -> None:
    repository = _repository(tmp_path)
    conversation_id = _conversation(repository)
    with pytest.raises(TranscriptFieldError, match="between"):
        repository.load_recent_exchanges(
            conversation_id=conversation_id, limit=limit  # type: ignore[arg-type]
        )


def test_targeted_fts_is_conversation_scoped_completed_and_turn_deduplicated(
    tmp_path: Path,
) -> None:
    repository = _repository(tmp_path)
    first_conversation = _conversation(repository)
    second_conversation = _conversation(repository)
    first = _complete(
        repository,
        first_conversation,
        user="Project Cobalt launch detail",
        assistant="Cobalt launch was recorded",
        at=NOW,
    )
    _complete(
        repository,
        second_conversation,
        user="Project Cobalt private other conversation",
        assistant="Cobalt other response",
        at=NOW,
    )
    repository.append_user_turn(
        conversation_id=first_conversation,
        turn_id=CanonicalId.new(),
        content="Cobalt open draft",
        created_at=NOW + timedelta(minutes=1),
    )
    hits = repository.search_targeted(
        conversation_id=first_conversation, query="Cobalt launch", limit=MAX_TARGETED_TURNS
    )
    assert len(hits) == 1
    assert hits[0].entry.turn_id == first.turn.turn_id
    assert hits[0].entry.conversation_id == first_conversation


def test_targeted_query_treats_operator_text_as_terms_not_fts_authority(tmp_path: Path) -> None:
    repository = _repository(tmp_path)
    conversation_id = _conversation(repository)
    _complete(
        repository,
        conversation_id,
        user="alpha OR beta NEAR gamma",
        assistant="operator text remains data",
        at=NOW,
    )
    hits = repository.search_targeted(
        conversation_id=conversation_id,
        query='alpha" OR beta*',
        limit=1,
    )
    assert len(hits) == 1


@pytest.mark.parametrize(
    "query",
    [
        "",
        "***",
        "x" * (MAX_TARGETED_QUERY_CHARACTERS + 1),
        " ".join(f"term{index}" for index in range(MAX_TARGETED_QUERY_TERMS + 1)),
    ],
)
def test_targeted_query_is_strictly_bounded(tmp_path: Path, query: str) -> None:
    repository = _repository(tmp_path)
    conversation_id = _conversation(repository)
    with pytest.raises(TranscriptFieldError, match="query"):
        repository.search_targeted(conversation_id=conversation_id, query=query, limit=1)
    with pytest.raises(TranscriptFieldError, match="between"):
        repository.search_targeted(
            conversation_id=conversation_id, query="valid", limit=MAX_TARGETED_TURNS + 1
        )


def test_history_reads_require_project_conversation_scope(tmp_path: Path) -> None:
    repository = _repository(tmp_path)
    with pytest.raises(TranscriptNotFoundError):
        repository.load_recent_exchanges(conversation_id=CanonicalId.new(), limit=1)
    with pytest.raises(TranscriptNotFoundError):
        repository.search_targeted(
            conversation_id=CanonicalId.new(), query="anything", limit=1
        )


def test_durable_content_hash_tampering_is_detected_on_read(tmp_path: Path) -> None:
    repository = _repository(tmp_path)
    conversation_id = _conversation(repository)
    exchange = _complete(
        repository,
        conversation_id,
        user="question",
        assistant="answer",
        at=NOW,
    )
    with repository.factory.connect() as connection:
        with connection.transaction():
            connection.execute(
                "UPDATE transcript_entries SET content='tampered' WHERE entry_uuid=?",
                (str(exchange.assistant_entry.entry_id),),
            )
    with pytest.raises(TranscriptIntegrityError, match="content hash"):
        repository.load_recent_exchanges(conversation_id=conversation_id, limit=1)


def test_malformed_commit_sequence_prevents_partial_publication(tmp_path: Path) -> None:
    repository = _repository(tmp_path)
    conversation_id = _conversation(repository)
    turn_id = CanonicalId.new()
    repository.append_user_turn(
        conversation_id=conversation_id,
        turn_id=turn_id,
        content="question",
        created_at=NOW,
    )
    with repository.factory.connect() as connection:
        with connection.transaction():
            connection.execute(
                "UPDATE system_meta SET value='01' WHERE key='transcript_commit_seq'"
            )
    with pytest.raises(TranscriptIntegrityError, match="not canonical"):
        repository.commit_published_response(
            turn_id=turn_id,
            result_hash=sha256_text("answer"),
            exact_published_text="answer",
            committed_at=NOW,
        )
    with repository.factory.connect() as connection:
        row = connection.execute(
            "SELECT count(*) AS count FROM transcript_publications"
        ).fetchone()
        assert row is not None and row["count"] == 0


def test_exchange_and_search_value_invariants_reject_cross_links(tmp_path: Path) -> None:
    repository = _repository(tmp_path)
    conversation_id = _conversation(repository)
    exchange = _complete(
        repository,
        conversation_id,
        user="question",
        assistant="answer",
        at=NOW,
    )
    with pytest.raises(TranscriptIntegrityError, match="different turns"):
        replace(
            exchange,
            assistant_entry=replace(exchange.assistant_entry, turn_id=CanonicalId.new()),
        )
    with pytest.raises(TranscriptIntegrityError, match="finite"):
        TranscriptSearchHit(exchange.user_entry, float("nan"))


def test_raw_sql_cannot_store_unknown_transcript_role(tmp_path: Path) -> None:
    repository = _repository(tmp_path)
    conversation_id = _conversation(repository)
    started = repository.append_user_turn(
        conversation_id=conversation_id,
        turn_id=CanonicalId.new(),
        content="question",
        created_at=NOW,
    )
    with repository.factory.connect() as connection:
        with pytest.raises(sqlite3.IntegrityError):
            with connection.transaction():
                connection.execute(
                    """
                    INSERT INTO transcript_entries VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        str(CanonicalId.new()),
                        str(repository.project_id),
                        str(conversation_id),
                        str(started.turn.turn_id),
                        2,
                        "SYSTEM",
                        "fake authority",
                        sha256_text("fake authority").value,
                        started.turn.created_at,
                    ),
                )
