from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from arcadia.core.config import StorageConfig
from arcadia.core.hashing import sha256_text
from arcadia.core.ids import CanonicalId
from arcadia.storage.connection import SQLiteConnectionFactory
from arcadia.storage.migrations import MigrationRunner
from arcadia.storage.transcript_repository import TranscriptNotFoundError, TranscriptRepository

NOW = datetime(2026, 9, 4, 14, 0, tzinfo=UTC)


def _repository(root: Path) -> TranscriptRepository:
    factory = SQLiteConnectionFactory(
        workspace_root=root,
        storage=StorageConfig(
            data_dir="data",
            database_name="completed-read.sqlite3",
            busy_timeout_ms=1000,
            require_fts5=True,
        ),
    )
    with factory.connect() as connection:
        MigrationRunner().migrate(connection, applied_at=NOW)
    return TranscriptRepository(factory, CanonicalId.new())


def test_load_completed_exchange_is_exact_and_rejects_open_turn(tmp_path: Path) -> None:
    repository = _repository(tmp_path)
    conversation_id = CanonicalId.new()
    repository.create_conversation(conversation_id=conversation_id, created_at=NOW)

    completed_turn = CanonicalId.new()
    repository.append_user_turn(
        conversation_id=conversation_id,
        turn_id=completed_turn,
        content="User exact text.",
        created_at=NOW,
    )
    repository.commit_published_response(
        turn_id=completed_turn,
        result_hash=sha256_text("Assistant exact text."),
        exact_published_text="Assistant exact text.",
        committed_at=NOW + timedelta(seconds=1),
    )

    exchange = repository.load_completed_exchange(turn_id=completed_turn)
    assert exchange.user_entry.content == "User exact text."
    assert exchange.assistant_entry.content == "Assistant exact text."

    open_turn = CanonicalId.new()
    repository.append_user_turn(
        conversation_id=conversation_id,
        turn_id=open_turn,
        content="Still open.",
        created_at=NOW + timedelta(minutes=1),
    )
    with pytest.raises(TranscriptNotFoundError, match="not a completed exchange"):
        repository.load_completed_exchange(turn_id=open_turn)


def test_load_recent_exchanges_before_returns_only_older_delta(tmp_path: Path) -> None:
    repository = _repository(tmp_path)
    conversation_id = CanonicalId.new()
    repository.create_conversation(conversation_id=conversation_id, created_at=NOW)

    exchanges = []
    for index in range(4):
        turn_id = CanonicalId.new()
        at = NOW + timedelta(minutes=index)
        repository.append_user_turn(
            conversation_id=conversation_id,
            turn_id=turn_id,
            content=f"User {index}.",
            created_at=at,
        )
        exchanges.append(
            repository.commit_published_response(
                turn_id=turn_id,
                result_hash=sha256_text(f"Assistant {index}."),
                exact_published_text=f"Assistant {index}.",
                committed_at=at + timedelta(seconds=1),
            )
        )

    delta = repository.load_recent_exchanges_before(
        conversation_id=conversation_id,
        before_turn_ordinal=exchanges[-1].turn.turn_ordinal,
        limit=2,
    )

    assert [item.turn.turn_id for item in delta] == [
        exchanges[1].turn.turn_id,
        exchanges[2].turn.turn_id,
    ]
