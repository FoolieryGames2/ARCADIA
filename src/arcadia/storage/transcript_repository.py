"""Project-scoped, append-only transcript persistence and bounded history reads."""

from __future__ import annotations

import re
import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from math import isfinite

from arcadia.core.artifact_envelope import canonical_utc_timestamp
from arcadia.core.canonical_json import JsonValue
from arcadia.core.hashing import Sha256Digest, parse_sha256_digest, sha256_text
from arcadia.core.ids import CanonicalId
from arcadia.storage.connection import ConnectionAccess, DatabaseConnection, SQLiteConnectionFactory
from arcadia.storage.migrations import MigrationRunner

MAX_RECENT_EXCHANGES = 20
MAX_TARGETED_TURNS = 8
MAX_TARGETED_QUERY_CHARACTERS = 1024
MAX_TARGETED_QUERY_TERMS = 32
_WORD_PATTERN = re.compile(r"\w+", re.UNICODE)


class TranscriptRepositoryError(RuntimeError):
    """Base error for transcript repository input, state, or integrity failure."""


class TranscriptFieldError(TranscriptRepositoryError):
    """A transcript repository input is malformed or would require coercion."""


class TranscriptNotFoundError(TranscriptRepositoryError):
    """A requested project-scoped conversation or turn does not exist."""


class TranscriptConflictError(TranscriptRepositoryError):
    """An authoritative UUID or publication identity conflicts with durable state."""


class TranscriptIntegrityError(TranscriptRepositoryError):
    """Durable transcript rows violate their hashes, ordering, or relationships."""


class TranscriptRole(StrEnum):
    USER = "USER"
    ASSISTANT = "ASSISTANT"


class TurnStatus(StrEnum):
    OPEN = "OPEN"
    COMPLETED = "COMPLETED"


class ContinuationStatus(StrEnum):
    NONE = "NONE"
    AWAITING_USER_INPUT = "AWAITING_USER_INPUT"


class ContinuationReason(StrEnum):
    USER_INFORMATION_NEEDED = "USER_INFORMATION_NEEDED"


@dataclass(frozen=True, slots=True)
class ContinuationState:
    """Fixed-shape host metadata for Recipe 0's one-next-turn cue."""

    status: ContinuationStatus
    source_turn_id: CanonicalId | None
    reason_code: ContinuationReason | None

    def __post_init__(self) -> None:
        if self.status is ContinuationStatus.NONE:
            if self.source_turn_id is not None or self.reason_code is not None:
                raise TranscriptIntegrityError("NONE continuation state must have null details")
        elif (
            type(self.source_turn_id) is not CanonicalId
            or self.reason_code is not ContinuationReason.USER_INFORMATION_NEEDED
        ):
            raise TranscriptIntegrityError(
                "AWAITING_USER_INPUT requires its source turn and fixed reason code"
            )

    @classmethod
    def none(cls) -> ContinuationState:
        return cls(ContinuationStatus.NONE, None, None)

    def to_value(self) -> dict[str, JsonValue]:
        return {
            "status": self.status.value,
            "source_turn_uuid": (
                None if self.source_turn_id is None else str(self.source_turn_id)
            ),
            "reason_code": None if self.reason_code is None else self.reason_code.value,
        }


@dataclass(frozen=True, slots=True)
class ConversationRecord:
    conversation_id: CanonicalId
    project_id: CanonicalId
    created_at: str


@dataclass(frozen=True, slots=True)
class TurnRecord:
    turn_id: CanonicalId
    project_id: CanonicalId
    conversation_id: CanonicalId
    turn_ordinal: int
    created_at: str
    status: TurnStatus


@dataclass(frozen=True, slots=True)
class TranscriptEntry:
    entry_id: CanonicalId
    project_id: CanonicalId
    conversation_id: CanonicalId
    turn_id: CanonicalId
    entry_ordinal: int
    role: TranscriptRole
    content: str
    content_hash: Sha256Digest
    created_at: str


@dataclass(frozen=True, slots=True)
class TranscriptPublication:
    publication_id: CanonicalId
    project_id: CanonicalId
    conversation_id: CanonicalId
    turn_id: CanonicalId
    assistant_entry_id: CanonicalId
    result_hash: Sha256Digest
    transcript_commit_seq: int
    committed_at: str


@dataclass(frozen=True, slots=True)
class StartedTurn:
    turn: TurnRecord
    user_entry: TranscriptEntry


@dataclass(frozen=True, slots=True)
class CompletedExchange:
    turn: TurnRecord
    user_entry: TranscriptEntry
    assistant_entry: TranscriptEntry
    publication: TranscriptPublication

    def __post_init__(self) -> None:
        identities = {
            self.turn.turn_id,
            self.user_entry.turn_id,
            self.assistant_entry.turn_id,
            self.publication.turn_id,
        }
        if len(identities) != 1:
            raise TranscriptIntegrityError("completed exchange rows belong to different turns")
        projects = {
            self.turn.project_id,
            self.user_entry.project_id,
            self.assistant_entry.project_id,
            self.publication.project_id,
        }
        conversations = {
            self.turn.conversation_id,
            self.user_entry.conversation_id,
            self.assistant_entry.conversation_id,
            self.publication.conversation_id,
        }
        if len(projects) != 1 or len(conversations) != 1:
            raise TranscriptIntegrityError("completed exchange rows cross transcript scope")
        if self.turn.status is not TurnStatus.COMPLETED:
            raise TranscriptIntegrityError("completed exchange requires COMPLETED turn state")
        if self.user_entry.role is not TranscriptRole.USER:
            raise TranscriptIntegrityError("completed exchange user entry has the wrong role")
        if self.assistant_entry.role is not TranscriptRole.ASSISTANT:
            raise TranscriptIntegrityError("completed exchange assistant entry has the wrong role")
        if self.publication.assistant_entry_id != self.assistant_entry.entry_id:
            raise TranscriptIntegrityError("publication references a different assistant entry")
        if self.publication.result_hash != self.assistant_entry.content_hash:
            raise TranscriptIntegrityError("published result hash differs from transcript content")


@dataclass(frozen=True, slots=True)
class TranscriptSearchHit:
    entry: TranscriptEntry
    rank: float

    def __post_init__(self) -> None:
        if type(self.rank) is not float or not isfinite(self.rank):
            raise TranscriptIntegrityError("FTS rank must be a finite SQLite float")


@dataclass(frozen=True, slots=True)
class TranscriptRepository:
    """Owns exact surface transcript rows for one host project UUID."""

    factory: SQLiteConnectionFactory
    project_id: CanonicalId

    def __post_init__(self) -> None:
        if type(self.factory) is not SQLiteConnectionFactory:
            raise TranscriptFieldError("factory must be a SQLiteConnectionFactory")
        if type(self.project_id) is not CanonicalId:
            raise TranscriptFieldError("project_id must be a CanonicalId")

    def create_conversation(
        self, *, conversation_id: CanonicalId, created_at: datetime
    ) -> ConversationRecord:
        self._require_id("conversation_id", conversation_id)
        timestamp = canonical_utc_timestamp(created_at)
        requested = ConversationRecord(conversation_id, self.project_id, timestamp)
        with self.factory.connect() as connection:
            self._require_current_schema(connection)
            with connection.transaction():
                existing = self._find_conversation(connection, conversation_id)
                if existing is not None:
                    if existing != requested:
                        raise TranscriptConflictError(
                            "conversation UUID already exists with different immutable fields"
                        )
                    return existing
                connection.execute(
                    """
                    INSERT INTO conversations(conversation_uuid, project_uuid, created_at)
                    VALUES (?, ?, ?)
                    """,
                    (str(conversation_id), str(self.project_id), timestamp),
                )
        return requested

    def append_user_turn(
        self,
        *,
        conversation_id: CanonicalId,
        turn_id: CanonicalId,
        content: str,
        created_at: datetime,
    ) -> StartedTurn:
        self._require_id("conversation_id", conversation_id)
        self._require_id("turn_id", turn_id)
        text = self._require_content(content)
        timestamp = canonical_utc_timestamp(created_at)
        content_hash = sha256_text(text)
        with self.factory.connect() as connection:
            self._require_current_schema(connection)
            with connection.transaction():
                existing_turn = self._find_turn_any_project(connection, turn_id)
                if existing_turn is not None:
                    return self._verify_idempotent_user_turn(
                        connection,
                        existing_turn,
                        conversation_id=conversation_id,
                        content=text,
                        content_hash=content_hash,
                        created_at=timestamp,
                    )
                conversation = self._find_conversation(connection, conversation_id)
                if conversation is None:
                    raise TranscriptNotFoundError("project conversation does not exist")
                if conversation.project_id != self.project_id:
                    raise TranscriptConflictError(
                        "conversation UUID already belongs to another project"
                    )
                turn_ordinal = self._next_turn_ordinal(connection, conversation_id)
                entry_ordinal = self._next_entry_ordinal(connection, conversation_id)
                entry_id = CanonicalId.new()
                connection.execute(
                    """
                    INSERT INTO conversation_turns(
                        turn_uuid, project_uuid, conversation_uuid,
                        turn_ordinal, created_at
                    ) VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        str(turn_id),
                        str(self.project_id),
                        str(conversation_id),
                        turn_ordinal,
                        timestamp,
                    ),
                )
                connection.execute(
                    """
                    INSERT INTO transcript_turn_states(
                        turn_uuid, project_uuid, conversation_uuid, status
                    ) VALUES (?, ?, ?, 'OPEN')
                    """,
                    (str(turn_id), str(self.project_id), str(conversation_id)),
                )
                connection.execute(
                    """
                    UPDATE transcript_open_continuations
                    SET claimed_by_turn_uuid=?
                    WHERE source_turn_uuid=(
                        SELECT previous.turn_uuid
                        FROM conversation_turns AS previous
                        JOIN transcript_turn_states AS previous_state
                          ON previous_state.turn_uuid=previous.turn_uuid
                        WHERE previous.project_uuid=?
                          AND previous.conversation_uuid=?
                          AND previous.turn_ordinal=?
                          AND previous_state.status='COMPLETED'
                    )
                      AND project_uuid=? AND conversation_uuid=?
                      AND claimed_by_turn_uuid IS NULL AND consumed=0
                    """,
                    (
                        str(turn_id),
                        str(self.project_id),
                        str(conversation_id),
                        turn_ordinal - 1,
                        str(self.project_id),
                        str(conversation_id),
                    ),
                )
                connection.execute(
                    """
                    INSERT INTO transcript_entries(
                        entry_uuid, project_uuid, conversation_uuid, turn_uuid,
                        entry_ordinal, role, content, content_hash, created_at
                    ) VALUES (?, ?, ?, ?, ?, 'USER', ?, ?, ?)
                    """,
                    (
                        str(entry_id),
                        str(self.project_id),
                        str(conversation_id),
                        str(turn_id),
                        entry_ordinal,
                        text,
                        content_hash.value,
                        timestamp,
                    ),
                )
                self._insert_fts(
                    connection,
                    entry_id=entry_id,
                    conversation_id=conversation_id,
                    turn_id=turn_id,
                    content=text,
                )
        return StartedTurn(
            turn=TurnRecord(
                turn_id,
                self.project_id,
                conversation_id,
                turn_ordinal,
                timestamp,
                TurnStatus.OPEN,
            ),
            user_entry=TranscriptEntry(
                entry_id,
                self.project_id,
                conversation_id,
                turn_id,
                entry_ordinal,
                TranscriptRole.USER,
                text,
                content_hash,
                timestamp,
            ),
        )

    def commit_published_response(
        self,
        *,
        turn_id: CanonicalId,
        result_hash: Sha256Digest,
        exact_published_text: str,
        committed_at: datetime,
        completed_turn_requires_user_input: bool = False,
    ) -> CompletedExchange:
        self._require_id("turn_id", turn_id)
        if type(result_hash) is not Sha256Digest:
            raise TranscriptFieldError("result_hash must be a Sha256Digest")
        text = self._require_content(exact_published_text)
        if sha256_text(text) != result_hash:
            raise TranscriptIntegrityError("published text does not match immutable result hash")
        if type(completed_turn_requires_user_input) is not bool:
            raise TranscriptFieldError("completed_turn_requires_user_input must be an exact bool")
        timestamp = canonical_utc_timestamp(committed_at)
        with self.factory.connect() as connection:
            self._require_current_schema(connection)
            with connection.transaction():
                turn = self._find_turn_any_project(connection, turn_id)
                if turn is None or turn.project_id != self.project_id:
                    raise TranscriptNotFoundError("project turn does not exist")
                existing = self._find_publication(connection, turn_id)
                if existing is not None:
                    if existing.result_hash != result_hash:
                        raise TranscriptConflictError(
                            "turn already has a different immutable published result"
                        )
                    if (
                        self._continuation_exists(connection, turn_id)
                        != completed_turn_requires_user_input
                    ):
                        raise TranscriptConflictError(
                            "publication retry changes authoritative continuation posture"
                        )
                    return self._load_exchange(connection, turn)
                if turn.status is not TurnStatus.OPEN:
                    raise TranscriptIntegrityError(
                        "completed turn is missing its transcript publication relation"
                    )
                user_entry = self._single_entry(connection, turn_id, TranscriptRole.USER)
                if user_entry is None:
                    raise TranscriptIntegrityError("open turn has no exact user transcript entry")
                entry_ordinal = self._next_entry_ordinal(connection, turn.conversation_id)
                entry_id = CanonicalId.new()
                publication_id = CanonicalId.new()
                current_seq = self._read_commit_seq(connection)
                next_seq = current_seq + 1
                connection.execute(
                    """
                    INSERT INTO transcript_entries(
                        entry_uuid, project_uuid, conversation_uuid, turn_uuid,
                        entry_ordinal, role, content, content_hash, created_at
                    ) VALUES (?, ?, ?, ?, ?, 'ASSISTANT', ?, ?, ?)
                    """,
                    (
                        str(entry_id),
                        str(self.project_id),
                        str(turn.conversation_id),
                        str(turn_id),
                        entry_ordinal,
                        text,
                        result_hash.value,
                        timestamp,
                    ),
                )
                self._insert_fts(
                    connection,
                    entry_id=entry_id,
                    conversation_id=turn.conversation_id,
                    turn_id=turn_id,
                    content=text,
                )
                connection.execute(
                    """
                    INSERT INTO transcript_publications(
                        publication_uuid, project_uuid, conversation_uuid, turn_uuid,
                        assistant_entry_uuid, result_hash, transcript_commit_seq, committed_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        str(publication_id),
                        str(self.project_id),
                        str(turn.conversation_id),
                        str(turn_id),
                        str(entry_id),
                        result_hash.value,
                        next_seq,
                        timestamp,
                    ),
                )
                if completed_turn_requires_user_input:
                    connection.execute(
                        """
                        INSERT INTO transcript_open_continuations(
                            source_turn_uuid, project_uuid, conversation_uuid, reason_code
                        ) VALUES (?, ?, ?, 'USER_INFORMATION_NEEDED')
                        """,
                        (
                            str(turn_id),
                            str(self.project_id),
                            str(turn.conversation_id),
                        ),
                    )
                updated_seq = connection.execute(
                    """
                    UPDATE system_meta SET value=?
                    WHERE key='transcript_commit_seq' AND value=?
                    """,
                    (str(next_seq), str(current_seq)),
                )
                updated_turn = connection.execute(
                    """
                    UPDATE transcript_turn_states SET status='COMPLETED'
                    WHERE turn_uuid=? AND project_uuid=? AND status='OPEN'
                    """,
                    (str(turn_id), str(self.project_id)),
                )
                if updated_seq.rowcount != 1 or updated_turn.rowcount != 1:
                    raise TranscriptConflictError(
                        "transcript sequence or turn state changed during commit"
                    )
                completed_turn = TurnRecord(
                    turn.turn_id,
                    turn.project_id,
                    turn.conversation_id,
                    turn.turn_ordinal,
                    turn.created_at,
                    TurnStatus.COMPLETED,
                )
                assistant_entry = TranscriptEntry(
                    entry_id,
                    self.project_id,
                    turn.conversation_id,
                    turn_id,
                    entry_ordinal,
                    TranscriptRole.ASSISTANT,
                    text,
                    result_hash,
                    timestamp,
                )
                publication = TranscriptPublication(
                    publication_id,
                    self.project_id,
                    turn.conversation_id,
                    turn_id,
                    entry_id,
                    result_hash,
                    next_seq,
                    timestamp,
                )
        return CompletedExchange(completed_turn, user_entry, assistant_entry, publication)

    def continuation_state_for_turn(self, *, turn_id: CanonicalId) -> ContinuationState:
        """Return only a valid marker claimed by this immediately following turn."""

        self._require_id("turn_id", turn_id)
        with self.factory.connect(ConnectionAccess.READ_ONLY) as connection:
            self._require_current_schema(connection)
            turn = self._find_turn_any_project(connection, turn_id)
            if turn is None or turn.project_id != self.project_id:
                raise TranscriptNotFoundError("project turn does not exist")
            row = connection.execute(
                """
                SELECT marker.source_turn_uuid, marker.reason_code,
                       source.turn_ordinal AS source_ordinal
                FROM transcript_open_continuations AS marker
                JOIN conversation_turns AS source
                  ON source.turn_uuid=marker.source_turn_uuid
                JOIN transcript_turn_states AS source_state
                  ON source_state.turn_uuid=source.turn_uuid
                WHERE marker.project_uuid=?
                  AND marker.conversation_uuid=?
                  AND marker.claimed_by_turn_uuid=?
                  AND marker.consumed=0
                  AND source_state.status='COMPLETED'
                """,
                (str(self.project_id), str(turn.conversation_id), str(turn_id)),
            ).fetchone()
            if row is None:
                return ContinuationState.none()
            source_ordinal = row["source_ordinal"]
            if type(source_ordinal) is not int or source_ordinal + 1 != turn.turn_ordinal:
                raise TranscriptIntegrityError(
                    "continuation marker is not bound to the immediately prior exchange"
                )
            try:
                source_turn_id = CanonicalId.parse(self._row_text(row, "source_turn_uuid"))
                reason = ContinuationReason(self._row_text(row, "reason_code"))
            except ValueError as exc:
                raise TranscriptIntegrityError("continuation marker is malformed") from exc
            return ContinuationState(
                ContinuationStatus.AWAITING_USER_INPUT, source_turn_id, reason
            )

    def consume_continuation(self, *, turn_id: CanonicalId) -> ContinuationState:
        """Consume this turn's cue exactly once when Recipe 0 freezes its packet."""

        state = self.continuation_state_for_turn(turn_id=turn_id)
        if state.status is ContinuationStatus.NONE:
            return state
        with self.factory.connect() as connection:
            self._require_current_schema(connection)
            with connection.transaction():
                updated = connection.execute(
                    """
                    UPDATE transcript_open_continuations SET consumed=1
                    WHERE project_uuid=? AND claimed_by_turn_uuid=? AND consumed=0
                    """,
                    (str(self.project_id), str(turn_id)),
                )
                if updated.rowcount != 1:
                    raise TranscriptConflictError(
                        "continuation marker changed before packet freeze"
                    )
        return state

    def load_continuation_exchange(self, *, turn_id: CanonicalId) -> CompletedExchange | None:
        """Load the exact prior exchange named by an active continuation cue."""

        state = self.continuation_state_for_turn(turn_id=turn_id)
        if state.source_turn_id is None:
            return None
        with self.factory.connect(ConnectionAccess.READ_ONLY) as connection:
            self._require_current_schema(connection)
            source = self._find_turn_any_project(connection, state.source_turn_id)
            if source is None or source.project_id != self.project_id:
                raise TranscriptIntegrityError("continuation source turn is missing")
            return self._load_exchange(connection, source)

    def transcript_commit_seq(self) -> int:
        with self.factory.connect(ConnectionAccess.READ_ONLY) as connection:
            self._require_current_schema(connection)
            return self._read_commit_seq(connection)

    def completed_exchange_count(self, *, conversation_id: CanonicalId) -> int:
        self._require_id("conversation_id", conversation_id)
        with self.factory.connect(ConnectionAccess.READ_ONLY) as connection:
            self._require_current_schema(connection)
            self._require_conversation(connection, conversation_id)
            row = connection.execute(
                """
                SELECT COUNT(*) AS exchange_count
                FROM transcript_turn_states
                WHERE project_uuid=? AND conversation_uuid=? AND status='COMPLETED'
                """,
                (str(self.project_id), str(conversation_id)),
            ).fetchone()
            if row is None or type(row["exchange_count"]) is not int:
                raise TranscriptIntegrityError("SQLite returned a malformed exchange count")
            return row["exchange_count"]

    def load_recent_exchanges(
        self, *, conversation_id: CanonicalId, limit: int
    ) -> tuple[CompletedExchange, ...]:
        self._require_id("conversation_id", conversation_id)
        self._require_bound("limit", limit, MAX_RECENT_EXCHANGES)
        with self.factory.connect(ConnectionAccess.READ_ONLY) as connection:
            self._require_current_schema(connection)
            self._require_conversation(connection, conversation_id)
            rows = connection.execute(
                """
                SELECT t.turn_uuid, t.project_uuid, t.conversation_uuid,
                       t.turn_ordinal, t.created_at, s.status
                FROM conversation_turns AS t
                JOIN transcript_turn_states AS s ON s.turn_uuid=t.turn_uuid
                WHERE t.project_uuid=? AND t.conversation_uuid=? AND s.status='COMPLETED'
                ORDER BY turn_ordinal DESC
                LIMIT ?
                """,
                (str(self.project_id), str(conversation_id), limit),
            ).fetchall()
            exchanges = [
                self._load_exchange(connection, self._decode_turn(row)) for row in rows
            ]
        return tuple(reversed(exchanges))

    def search_targeted(
        self,
        *,
        conversation_id: CanonicalId,
        query: str,
        limit: int,
    ) -> tuple[TranscriptSearchHit, ...]:
        self._require_id("conversation_id", conversation_id)
        self._require_bound("limit", limit, MAX_TARGETED_TURNS)
        fts_query = self._fts_query(query)
        with self.factory.connect(ConnectionAccess.READ_ONLY) as connection:
            self._require_current_schema(connection)
            self._require_conversation(connection, conversation_id)
            rows = connection.execute(
                """
                SELECT e.entry_uuid, e.project_uuid, e.conversation_uuid, e.turn_uuid,
                       e.entry_ordinal, e.role, e.content, e.content_hash, e.created_at,
                       bm25(transcript_entries_fts) AS rank
                FROM transcript_entries_fts
                JOIN transcript_entries AS e
                  ON e.entry_uuid = transcript_entries_fts.entry_uuid
                JOIN transcript_turn_states AS t ON t.turn_uuid = e.turn_uuid
                WHERE transcript_entries_fts MATCH ?
                  AND e.project_uuid=? AND e.conversation_uuid=?
                  AND t.status='COMPLETED'
                ORDER BY rank, e.entry_ordinal DESC
                LIMIT ?
                """,
                (
                    fts_query,
                    str(self.project_id),
                    str(conversation_id),
                    limit * 4,
                ),
            ).fetchall()
            hits: list[TranscriptSearchHit] = []
            seen_turns: set[CanonicalId] = set()
            for row in rows:
                entry = self._decode_entry(row)
                if entry.turn_id in seen_turns:
                    continue
                rank = row["rank"]
                if type(rank) not in (int, float):
                    raise TranscriptIntegrityError("SQLite returned a nonnumeric FTS rank")
                seen_turns.add(entry.turn_id)
                hits.append(TranscriptSearchHit(entry, float(rank)))
                if len(hits) == limit:
                    break
        return tuple(hits)

    def _verify_idempotent_user_turn(
        self,
        connection: DatabaseConnection,
        turn: TurnRecord,
        *,
        conversation_id: CanonicalId,
        content: str,
        content_hash: Sha256Digest,
        created_at: str,
    ) -> StartedTurn:
        if turn.project_id != self.project_id or turn.conversation_id != conversation_id:
            raise TranscriptConflictError("turn UUID already belongs to another scope")
        user_entry = self._single_entry(connection, turn.turn_id, TranscriptRole.USER)
        if (
            user_entry is None
            or user_entry.content != content
            or user_entry.content_hash != content_hash
            or user_entry.created_at != created_at
            or turn.created_at != created_at
        ):
            raise TranscriptConflictError(
                "turn UUID retry differs from immutable user transcript input"
            )
        return StartedTurn(turn, user_entry)

    def _load_exchange(
        self, connection: DatabaseConnection, turn: TurnRecord
    ) -> CompletedExchange:
        user_entry = self._single_entry(connection, turn.turn_id, TranscriptRole.USER)
        assistant_entry = self._single_entry(
            connection, turn.turn_id, TranscriptRole.ASSISTANT
        )
        publication = self._find_publication(connection, turn.turn_id)
        if user_entry is None or assistant_entry is None or publication is None:
            raise TranscriptIntegrityError("completed turn lacks one exact exchange relation")
        return CompletedExchange(turn, user_entry, assistant_entry, publication)

    def _single_entry(
        self,
        connection: DatabaseConnection,
        turn_id: CanonicalId,
        role: TranscriptRole,
    ) -> TranscriptEntry | None:
        rows = connection.execute(
            """
            SELECT entry_uuid, project_uuid, conversation_uuid, turn_uuid,
                   entry_ordinal, role, content, content_hash, created_at
            FROM transcript_entries
            WHERE project_uuid=? AND turn_uuid=? AND role=?
            ORDER BY entry_ordinal
            """,
            (str(self.project_id), str(turn_id), role.value),
        ).fetchall()
        if not rows:
            return None
        if len(rows) != 1:
            raise TranscriptIntegrityError("turn has duplicate transcript roles")
        return self._decode_entry(rows[0])

    def _find_conversation(
        self, connection: DatabaseConnection, conversation_id: CanonicalId
    ) -> ConversationRecord | None:
        row = connection.execute(
            """
            SELECT conversation_uuid, project_uuid, created_at
            FROM conversations WHERE conversation_uuid=?
            """,
            (str(conversation_id),),
        ).fetchone()
        return None if row is None else self._decode_conversation(row)

    def _require_conversation(
        self, connection: DatabaseConnection, conversation_id: CanonicalId
    ) -> ConversationRecord:
        record = self._find_conversation(connection, conversation_id)
        if record is None or record.project_id != self.project_id:
            raise TranscriptNotFoundError("project conversation does not exist")
        return record

    def _find_turn_any_project(
        self, connection: DatabaseConnection, turn_id: CanonicalId
    ) -> TurnRecord | None:
        row = connection.execute(
            """
            SELECT t.turn_uuid, t.project_uuid, t.conversation_uuid,
                   t.turn_ordinal, t.created_at, s.status
            FROM conversation_turns AS t
            JOIN transcript_turn_states AS s ON s.turn_uuid=t.turn_uuid
            WHERE t.turn_uuid=?
            """,
            (str(turn_id),),
        ).fetchone()
        return None if row is None else self._decode_turn(row)

    def _find_publication(
        self, connection: DatabaseConnection, turn_id: CanonicalId
    ) -> TranscriptPublication | None:
        row = connection.execute(
            """
            SELECT publication_uuid, project_uuid, conversation_uuid, turn_uuid,
                   assistant_entry_uuid, result_hash, transcript_commit_seq, committed_at
            FROM transcript_publications WHERE turn_uuid=?
            """,
            (str(turn_id),),
        ).fetchone()
        return None if row is None else self._decode_publication(row)

    def _continuation_exists(
        self, connection: DatabaseConnection, source_turn_id: CanonicalId
    ) -> bool:
        row = connection.execute(
            """
            SELECT 1 AS present FROM transcript_open_continuations
            WHERE project_uuid=? AND source_turn_uuid=?
            """,
            (str(self.project_id), str(source_turn_id)),
        ).fetchone()
        return row is not None

    def _next_turn_ordinal(
        self, connection: DatabaseConnection, conversation_id: CanonicalId
    ) -> int:
        row = connection.execute(
            """
            SELECT COALESCE(MAX(turn_ordinal), 0) + 1 AS next_ordinal
            FROM conversation_turns WHERE project_uuid=? AND conversation_uuid=?
            """,
            (str(self.project_id), str(conversation_id)),
        ).fetchone()
        return self._strict_positive(row, "next_ordinal")

    def _next_entry_ordinal(
        self, connection: DatabaseConnection, conversation_id: CanonicalId
    ) -> int:
        row = connection.execute(
            """
            SELECT COALESCE(MAX(entry_ordinal), 0) + 1 AS next_ordinal
            FROM transcript_entries WHERE project_uuid=? AND conversation_uuid=?
            """,
            (str(self.project_id), str(conversation_id)),
        ).fetchone()
        return self._strict_positive(row, "next_ordinal")

    def _read_commit_seq(self, connection: DatabaseConnection) -> int:
        row = connection.execute(
            "SELECT value FROM system_meta WHERE key='transcript_commit_seq'"
        ).fetchone()
        if row is None or type(row["value"]) is not str:
            raise TranscriptIntegrityError("transcript_commit_seq metadata is missing")
        value = row["value"]
        if not value.isascii() or not value.isdecimal() or str(int(value)) != value:
            raise TranscriptIntegrityError("transcript_commit_seq is not canonical")
        return int(value)

    def _insert_fts(
        self,
        connection: DatabaseConnection,
        *,
        entry_id: CanonicalId,
        conversation_id: CanonicalId,
        turn_id: CanonicalId,
        content: str,
    ) -> None:
        connection.execute(
            """
            INSERT INTO transcript_entries_fts(
                entry_uuid, project_uuid, conversation_uuid, turn_uuid, content
            ) VALUES (?, ?, ?, ?, ?)
            """,
            (
                str(entry_id),
                str(self.project_id),
                str(conversation_id),
                str(turn_id),
                content,
            ),
        )

    @staticmethod
    def _decode_conversation(row: sqlite3.Row) -> ConversationRecord:
        return ConversationRecord(
            TranscriptRepository._row_id(row, "conversation_uuid"),
            TranscriptRepository._row_id(row, "project_uuid"),
            TranscriptRepository._row_timestamp(row, "created_at"),
        )

    @staticmethod
    def _decode_turn(row: sqlite3.Row) -> TurnRecord:
        ordinal = TranscriptRepository._row_positive(row, "turn_ordinal")
        try:
            status = TurnStatus(TranscriptRepository._row_text(row, "status"))
        except ValueError as exc:
            raise TranscriptIntegrityError("turn status is not recognized") from exc
        return TurnRecord(
            TranscriptRepository._row_id(row, "turn_uuid"),
            TranscriptRepository._row_id(row, "project_uuid"),
            TranscriptRepository._row_id(row, "conversation_uuid"),
            ordinal,
            TranscriptRepository._row_timestamp(row, "created_at"),
            status,
        )

    @staticmethod
    def _decode_entry(row: sqlite3.Row) -> TranscriptEntry:
        try:
            role = TranscriptRole(TranscriptRepository._row_text(row, "role"))
            digest = parse_sha256_digest(
                TranscriptRepository._row_text(row, "content_hash")
            )
        except ValueError as exc:
            raise TranscriptIntegrityError("transcript entry identity is malformed") from exc
        content = TranscriptRepository._row_text(row, "content")
        if sha256_text(content) != digest:
            raise TranscriptIntegrityError("transcript entry content hash does not match")
        return TranscriptEntry(
            TranscriptRepository._row_id(row, "entry_uuid"),
            TranscriptRepository._row_id(row, "project_uuid"),
            TranscriptRepository._row_id(row, "conversation_uuid"),
            TranscriptRepository._row_id(row, "turn_uuid"),
            TranscriptRepository._row_positive(row, "entry_ordinal"),
            role,
            content,
            digest,
            TranscriptRepository._row_timestamp(row, "created_at"),
        )

    @staticmethod
    def _decode_publication(row: sqlite3.Row) -> TranscriptPublication:
        try:
            result_hash = parse_sha256_digest(
                TranscriptRepository._row_text(row, "result_hash")
            )
        except ValueError as exc:
            raise TranscriptIntegrityError("publication result hash is malformed") from exc
        return TranscriptPublication(
            TranscriptRepository._row_id(row, "publication_uuid"),
            TranscriptRepository._row_id(row, "project_uuid"),
            TranscriptRepository._row_id(row, "conversation_uuid"),
            TranscriptRepository._row_id(row, "turn_uuid"),
            TranscriptRepository._row_id(row, "assistant_entry_uuid"),
            result_hash,
            TranscriptRepository._row_positive(row, "transcript_commit_seq"),
            TranscriptRepository._row_timestamp(row, "committed_at"),
        )

    @staticmethod
    def _row_text(row: sqlite3.Row, name: str) -> str:
        value = row[name]
        if type(value) is not str:
            raise TranscriptIntegrityError(f"durable {name} is not exact text")
        return value

    @staticmethod
    def _row_id(row: sqlite3.Row, name: str) -> CanonicalId:
        try:
            return CanonicalId.parse(TranscriptRepository._row_text(row, name))
        except ValueError as exc:
            raise TranscriptIntegrityError(f"durable {name} is not a canonical UUID") from exc

    @staticmethod
    def _row_positive(row: sqlite3.Row, name: str) -> int:
        value = row[name]
        if type(value) is not int or value < 1:
            raise TranscriptIntegrityError(f"durable {name} is not a positive integer")
        return value

    @staticmethod
    def _row_timestamp(row: sqlite3.Row, name: str) -> str:
        value = TranscriptRepository._row_text(row, name)
        try:
            parsed = datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=UTC)
        except ValueError as exc:
            raise TranscriptIntegrityError(f"durable {name} is not a real UTC time") from exc
        if canonical_utc_timestamp(parsed) != value:
            raise TranscriptIntegrityError(f"durable {name} is not canonical UTC")
        return value

    @staticmethod
    def _strict_positive(row: sqlite3.Row | None, name: str) -> int:
        if row is None:
            raise TranscriptIntegrityError(f"SQLite did not return {name}")
        return TranscriptRepository._row_positive(row, name)

    @staticmethod
    def _require_id(name: str, value: object) -> None:
        if type(value) is not CanonicalId:
            raise TranscriptFieldError(f"{name} must be a CanonicalId")

    @staticmethod
    def _require_content(value: object) -> str:
        if type(value) is not str or not value:
            raise TranscriptFieldError("transcript content must be nonempty exact text")
        sha256_text(value)
        return value

    @staticmethod
    def _require_bound(name: str, value: object, maximum: int) -> None:
        if type(value) is not int or not 1 <= value <= maximum:
            raise TranscriptFieldError(f"{name} must be between 1 and {maximum}")

    @staticmethod
    def _fts_query(query: object) -> str:
        if type(query) is not str or not query or len(query) > MAX_TARGETED_QUERY_CHARACTERS:
            raise TranscriptFieldError("targeted query must be bounded nonempty text")
        terms = _WORD_PATTERN.findall(query)
        if not terms or len(terms) > MAX_TARGETED_QUERY_TERMS:
            raise TranscriptFieldError("targeted query has no legal terms or exceeds term bound")
        return " AND ".join(f'"{term}"' for term in terms)

    @staticmethod
    def _require_current_schema(connection: DatabaseConnection) -> None:
        state = MigrationRunner().inspect(connection)
        if state.current_version != state.target_version:
            raise TranscriptRepositoryError("transcript repository schema is not current")
