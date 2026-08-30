"""Project-scoped immutable persistence for Artifact Envelope V1 revisions."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass

from arcadia.core.artifact_envelope import (
    ArtifactEnvelope,
    ArtifactEnvelopeError,
    RecipeId,
)
from arcadia.core.ids import CanonicalId
from arcadia.storage.connection import (
    ConnectionAccess,
    DatabaseConnection,
    SQLiteConnectionFactory,
)
from arcadia.storage.migrations import MigrationRunner

MAX_TURN_ARTIFACT_REVISIONS = 200


class ArtifactRepositoryError(RuntimeError):
    """Base error for artifact repository input, state, or integrity failure."""


class ArtifactRepositoryFieldError(ArtifactRepositoryError):
    """A repository argument is malformed or would require coercion."""


class ArtifactNotFoundError(ArtifactRepositoryError):
    """A requested project-scoped artifact, revision, or turn does not exist."""


class ArtifactConflictError(ArtifactRepositoryError):
    """An immutable identity, revision, or optimistic head conflicts."""


class ArtifactRepositoryIntegrityError(ArtifactRepositoryError):
    """Durable artifact rows do not reproduce their verified envelope."""


@dataclass(frozen=True, slots=True)
class ArtifactRepository:
    """Owns immutable technical artifact revisions for one project UUID."""

    factory: SQLiteConnectionFactory
    project_id: CanonicalId

    def __post_init__(self) -> None:
        if type(self.factory) is not SQLiteConnectionFactory:
            raise ArtifactRepositoryFieldError(
                "factory must be a SQLiteConnectionFactory"
            )
        if type(self.project_id) is not CanonicalId:
            raise ArtifactRepositoryFieldError("project_id must be a CanonicalId")

    def store(
        self,
        envelope: ArtifactEnvelope,
        *,
        expected_latest_revision: int,
    ) -> ArtifactEnvelope:
        """Atomically append one exact envelope, guarded by the caller's head."""

        if type(envelope) is not ArtifactEnvelope:
            raise ArtifactRepositoryFieldError("envelope must be an ArtifactEnvelope")
        self._require_nonnegative("expected_latest_revision", expected_latest_revision)
        if envelope.project_id != self.project_id:
            raise ArtifactConflictError("artifact envelope belongs to another project")
        if not envelope.verify_integrity():
            raise ArtifactRepositoryIntegrityError("artifact envelope integrity failed")

        envelope_json = envelope.to_json()
        with self.factory.connect() as connection:
            self._require_current_schema(connection)
            with connection.transaction():
                existing_revision = self._find_revision(
                    connection, envelope.artifact_id, envelope.revision
                )
                if existing_revision is not None:
                    if (
                        existing_revision.artifact_hash == envelope.artifact_hash
                        and existing_revision.to_json() == envelope_json
                    ):
                        return existing_revision
                    raise ArtifactConflictError(
                        "artifact revision already exists with different immutable content"
                    )

                identity = self._find_identity(connection, envelope.artifact_id)
                latest = self._latest_revision_number(connection, envelope.artifact_id)
                if identity is None:
                    if expected_latest_revision != 0 or envelope.revision != 1:
                        raise ArtifactConflictError(
                            "new artifact must begin at revision 1 from expected head 0"
                        )
                    self._require_turn(connection, envelope.turn_id)
                    self._reject_duplicate_envelope_hash(connection, envelope)
                    self._verify_basis_refs(connection, envelope)
                    connection.execute(
                        """
                        INSERT INTO artifacts(
                            artifact_uuid, project_uuid, turn_uuid,
                            recipe_id, artifact_type, created_at
                        ) VALUES (?, ?, ?, ?, ?, ?)
                        """,
                        (
                            str(envelope.artifact_id),
                            str(self.project_id),
                            str(envelope.turn_id),
                            envelope.recipe_id.value,
                            envelope.artifact_type,
                            envelope.created_at,
                        ),
                    )
                else:
                    if latest == 0:
                        raise ArtifactRepositoryIntegrityError(
                            "artifact identity has no durable revision"
                        )
                    self._verify_identity(identity, envelope)
                    if latest != expected_latest_revision:
                        raise ArtifactConflictError(
                            "expected artifact head does not match durable latest revision"
                        )
                    if envelope.revision != latest + 1:
                        raise ArtifactConflictError(
                            "artifact revisions must append contiguously"
                        )
                    previous = self._find_revision(
                        connection, envelope.artifact_id, latest
                    )
                    if previous is None:
                        raise ArtifactRepositoryIntegrityError(
                            "artifact head revision cannot be loaded"
                        )
                    if previous.short_id != envelope.short_id:
                        raise ArtifactConflictError(
                            "artifact revision changes its scoped alias identity"
                        )
                    if envelope.created_at < previous.created_at:
                        raise ArtifactConflictError(
                            "artifact revision time precedes the durable head"
                        )
                    self._reject_duplicate_envelope_hash(connection, envelope)
                    self._verify_basis_refs(connection, envelope)

                connection.execute(
                    """
                    INSERT INTO artifact_revisions(
                        artifact_uuid, revision, envelope_json,
                        content_hash, envelope_hash, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        str(envelope.artifact_id),
                        envelope.revision,
                        envelope_json,
                        envelope.content_hash.value,
                        envelope.artifact_hash.value,
                        envelope.created_at,
                    ),
                )
                for ordinal, basis_ref in enumerate(envelope.basis_refs, start=1):
                    connection.execute(
                        """
                        INSERT INTO artifact_links(
                            artifact_uuid, artifact_revision, link_ordinal,
                            basis_artifact_uuid, basis_revision, basis_envelope_hash
                        ) VALUES (?, ?, ?, ?, ?, ?)
                        """,
                        (
                            str(envelope.artifact_id),
                            envelope.revision,
                            ordinal,
                            str(basis_ref.artifact_id),
                            basis_ref.revision,
                            basis_ref.artifact_hash.value,
                        ),
                    )
        return envelope

    def load(self, *, artifact_id: CanonicalId, revision: int) -> ArtifactEnvelope:
        self._require_id("artifact_id", artifact_id)
        self._require_positive("revision", revision)
        with self.factory.connect(ConnectionAccess.READ_ONLY) as connection:
            self._require_current_schema(connection)
            envelope = self._find_revision(connection, artifact_id, revision)
            if envelope is None or envelope.project_id != self.project_id:
                raise ArtifactNotFoundError("project artifact revision does not exist")
            return envelope

    def load_latest(self, *, artifact_id: CanonicalId) -> ArtifactEnvelope:
        self._require_id("artifact_id", artifact_id)
        with self.factory.connect(ConnectionAccess.READ_ONLY) as connection:
            self._require_current_schema(connection)
            identity = self._find_identity(connection, artifact_id)
            if identity is None or identity.project_id != self.project_id:
                raise ArtifactNotFoundError("project artifact does not exist")
            latest = self._latest_revision_number(connection, artifact_id)
            envelope = self._find_revision(connection, artifact_id, latest)
            if envelope is None:
                raise ArtifactRepositoryIntegrityError(
                    "artifact identity has no durable revision"
                )
            return envelope

    def list_turn(
        self,
        *,
        turn_id: CanonicalId,
        limit: int,
        recipe_id: RecipeId | None = None,
    ) -> tuple[ArtifactEnvelope, ...]:
        """Return bounded immutable revisions in durable chronological order."""

        self._require_id("turn_id", turn_id)
        self._require_positive("limit", limit, maximum=MAX_TURN_ARTIFACT_REVISIONS)
        if recipe_id is not None and type(recipe_id) is not RecipeId:
            raise ArtifactRepositoryFieldError("recipe_id must be a RecipeId or None")
        with self.factory.connect(ConnectionAccess.READ_ONLY) as connection:
            self._require_current_schema(connection)
            self._require_turn(connection, turn_id)
            parameters: tuple[object, ...]
            if recipe_id is None:
                where_recipe = ""
                parameters = (str(self.project_id), str(turn_id), limit)
            else:
                where_recipe = "AND a.recipe_id=?"
                parameters = (
                    str(self.project_id),
                    str(turn_id),
                    recipe_id.value,
                    limit,
                )
            rows = connection.execute(
                f"""
                {self._revision_select()}
                WHERE a.project_uuid=? AND a.turn_uuid=? {where_recipe}
                ORDER BY r.created_at, a.artifact_uuid, r.revision
                LIMIT ?
                """,
                parameters,
            ).fetchall()
            return tuple(self._decode_revision(connection, row) for row in rows)

    def _verify_basis_refs(
        self, connection: DatabaseConnection, envelope: ArtifactEnvelope
    ) -> None:
        for basis_ref in envelope.basis_refs:
            basis = self._find_revision(
                connection, basis_ref.artifact_id, basis_ref.revision
            )
            if basis is None:
                raise ArtifactNotFoundError("upstream basis revision does not exist")
            if basis.project_id != self.project_id:
                raise ArtifactConflictError("upstream basis belongs to another project")
            if basis.artifact_hash != basis_ref.artifact_hash:
                raise ArtifactConflictError("upstream basis hash does not match durable revision")

    def _reject_duplicate_envelope_hash(
        self, connection: DatabaseConnection, envelope: ArtifactEnvelope
    ) -> None:
        row = connection.execute(
            "SELECT artifact_uuid, revision FROM artifact_revisions WHERE envelope_hash=?",
            (envelope.artifact_hash.value,),
        ).fetchone()
        if row is not None:
            raise ArtifactConflictError("artifact hash already identifies another revision")

    def _find_revision(
        self, connection: DatabaseConnection, artifact_id: CanonicalId, revision: int
    ) -> ArtifactEnvelope | None:
        row = connection.execute(
            f"""
            {self._revision_select()}
            WHERE a.artifact_uuid=? AND r.revision=?
            """,
            (str(artifact_id), revision),
        ).fetchone()
        return None if row is None else self._decode_revision(connection, row)

    def _decode_revision(
        self, connection: DatabaseConnection, row: sqlite3.Row
    ) -> ArtifactEnvelope:
        envelope_json = self._row_text(row, "envelope_json")
        try:
            envelope = ArtifactEnvelope.from_json(envelope_json)
        except ArtifactEnvelopeError as exc:
            raise ArtifactRepositoryIntegrityError(
                "durable envelope is not valid canonical Artifact Envelope V1"
            ) from exc
        expected = {
            "artifact_uuid": str(envelope.artifact_id),
            "project_uuid": str(envelope.project_id),
            "turn_uuid": str(envelope.turn_id),
            "recipe_id": envelope.recipe_id.value,
            "artifact_type": envelope.artifact_type,
            "revision": envelope.revision,
            "content_hash": envelope.content_hash.value,
            "envelope_hash": envelope.artifact_hash.value,
            "revision_created_at": envelope.created_at,
        }
        for name, value in expected.items():
            if row[name] != value or type(row[name]) is not type(value):
                raise ArtifactRepositoryIntegrityError(
                    f"durable {name} differs from the immutable envelope"
                )
        identity_created_at = self._row_text(row, "identity_created_at")
        first_created_at = self._row_text(row, "first_created_at")
        if identity_created_at != first_created_at or (
            envelope.revision == 1 and first_created_at != envelope.created_at
        ):
            raise ArtifactRepositoryIntegrityError(
                "artifact identity timestamp differs from revision 1"
            )
        link_rows = connection.execute(
            """
            SELECT link_ordinal, basis_artifact_uuid, basis_revision, basis_envelope_hash
            FROM artifact_links
            WHERE artifact_uuid=? AND artifact_revision=?
            ORDER BY link_ordinal
            """,
            (str(envelope.artifact_id), envelope.revision),
        ).fetchall()
        if len(link_rows) != len(envelope.basis_refs):
            raise ArtifactRepositoryIntegrityError(
                "durable basis links differ from envelope basis refs"
            )
        for ordinal, (link, basis_ref) in enumerate(
            zip(link_rows, envelope.basis_refs, strict=True), start=1
        ):
            if (
                link["link_ordinal"] != ordinal
                or link["basis_artifact_uuid"] != str(basis_ref.artifact_id)
                or link["basis_revision"] != basis_ref.revision
                or link["basis_envelope_hash"] != basis_ref.artifact_hash.value
            ):
                raise ArtifactRepositoryIntegrityError(
                    "durable basis link differs from envelope basis ref"
                )
            basis_row = connection.execute(
                """
                SELECT a.project_uuid, r.envelope_hash
                FROM artifact_revisions AS r
                JOIN artifacts AS a ON a.artifact_uuid=r.artifact_uuid
                WHERE r.artifact_uuid=? AND r.revision=?
                """,
                (str(basis_ref.artifact_id), basis_ref.revision),
            ).fetchone()
            if (
                basis_row is None
                or basis_row["project_uuid"] != str(self.project_id)
                or basis_row["envelope_hash"] != basis_ref.artifact_hash.value
            ):
                raise ArtifactRepositoryIntegrityError(
                    "durable upstream basis no longer matches its exact reference"
                )
        return envelope

    @staticmethod
    def _revision_select() -> str:
        return """
            SELECT r.envelope_json, r.revision, r.content_hash, r.envelope_hash,
                   r.created_at AS revision_created_at,
                   a.artifact_uuid, a.project_uuid, a.turn_uuid,
                   a.recipe_id, a.artifact_type, a.created_at AS identity_created_at,
                   first.created_at AS first_created_at
            FROM artifact_revisions AS r
            JOIN artifacts AS a ON a.artifact_uuid=r.artifact_uuid
            JOIN artifact_revisions AS first
              ON first.artifact_uuid=a.artifact_uuid AND first.revision=1
        """

    def _require_turn(
        self, connection: DatabaseConnection, turn_id: CanonicalId
    ) -> None:
        row = connection.execute(
            "SELECT project_uuid FROM conversation_turns WHERE turn_uuid=?",
            (str(turn_id),),
        ).fetchone()
        if row is None or row["project_uuid"] != str(self.project_id):
            raise ArtifactNotFoundError("project turn does not exist")

    @dataclass(frozen=True, slots=True)
    class _Identity:
        project_id: CanonicalId
        turn_id: CanonicalId
        recipe_id: RecipeId
        artifact_type: str

    def _find_identity(
        self, connection: DatabaseConnection, artifact_id: CanonicalId
    ) -> _Identity | None:
        row = connection.execute(
            """
            SELECT project_uuid, turn_uuid, recipe_id, artifact_type
            FROM artifacts WHERE artifact_uuid=?
            """,
            (str(artifact_id),),
        ).fetchone()
        if row is None:
            return None
        try:
            return self._Identity(
                CanonicalId.parse(self._row_text(row, "project_uuid")),
                CanonicalId.parse(self._row_text(row, "turn_uuid")),
                RecipeId(self._row_text(row, "recipe_id")),
                self._row_text(row, "artifact_type"),
            )
        except ValueError as exc:
            raise ArtifactRepositoryIntegrityError(
                "durable artifact identity is malformed"
            ) from exc

    @staticmethod
    def _verify_identity(identity: _Identity, envelope: ArtifactEnvelope) -> None:
        if (
            identity.project_id != envelope.project_id
            or identity.turn_id != envelope.turn_id
            or identity.recipe_id is not envelope.recipe_id
            or identity.artifact_type != envelope.artifact_type
        ):
            raise ArtifactConflictError(
                "artifact revision changes immutable identity metadata"
            )

    @staticmethod
    def _latest_revision_number(
        connection: DatabaseConnection, artifact_id: CanonicalId
    ) -> int:
        row = connection.execute(
            """
            SELECT MAX(revision) AS latest, count(*) AS revision_count
            FROM artifact_revisions WHERE artifact_uuid=?
            """,
            (str(artifact_id),),
        ).fetchone()
        if row is None:
            raise ArtifactRepositoryIntegrityError("SQLite did not return artifact head")
        value = row["latest"]
        count = row["revision_count"]
        if type(count) is not int or count < 0:
            raise ArtifactRepositoryIntegrityError("artifact revision count is malformed")
        if value is None:
            if count != 0:
                raise ArtifactRepositoryIntegrityError("artifact head and count disagree")
            return 0
        if type(value) is not int or value < 1:
            raise ArtifactRepositoryIntegrityError("artifact head is not a positive integer")
        if count != value:
            raise ArtifactRepositoryIntegrityError("artifact revision history has a gap")
        return value

    @staticmethod
    def _row_text(row: sqlite3.Row, name: str) -> str:
        value = row[name]
        if type(value) is not str:
            raise ArtifactRepositoryIntegrityError(f"durable {name} is not exact text")
        return value

    @staticmethod
    def _require_id(name: str, value: object) -> None:
        if type(value) is not CanonicalId:
            raise ArtifactRepositoryFieldError(f"{name} must be a CanonicalId")

    @staticmethod
    def _require_nonnegative(name: str, value: object) -> None:
        if type(value) is not int or value < 0:
            raise ArtifactRepositoryFieldError(f"{name} must be a nonnegative integer")

    @staticmethod
    def _require_positive(name: str, value: object, *, maximum: int | None = None) -> None:
        if type(value) is not int or value < 1 or (maximum is not None and value > maximum):
            suffix = "" if maximum is None else f" no greater than {maximum}"
            raise ArtifactRepositoryFieldError(
                f"{name} must be a positive integer{suffix}"
            )

    @staticmethod
    def _require_current_schema(connection: DatabaseConnection) -> None:
        state = MigrationRunner().inspect(connection)
        if state.current_version != state.target_version:
            raise ArtifactRepositoryError("artifact repository schema is not current")
