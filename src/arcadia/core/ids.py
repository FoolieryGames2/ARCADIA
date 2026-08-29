"""Host-authoritative UUIDs and scoped human-readable audit aliases."""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import StrEnum
from types import MappingProxyType
from typing import Final
from uuid import UUID, uuid4


class IdentifierError(ValueError):
    """Raised when an identifier is malformed, noncanonical, or out of scope."""


@dataclass(frozen=True, slots=True, order=True)
class CanonicalId:
    """An opaque canonical UUID; only the host creates new values."""

    value: UUID

    def __post_init__(self) -> None:
        if self.value.int == 0:
            raise IdentifierError("the nil UUID is not a legal canonical identity")

    @classmethod
    def new(cls) -> CanonicalId:
        return cls(uuid4())

    @classmethod
    def parse(cls, text: str) -> CanonicalId:
        if not isinstance(text, str) or not text.isascii():
            raise IdentifierError("canonical UUID text must be ASCII")
        try:
            parsed = UUID(text)
        except (ValueError, AttributeError) as exc:
            raise IdentifierError("invalid canonical UUID") from exc
        if text != str(parsed):
            raise IdentifierError("UUID must use lowercase canonical hyphenated form")
        return cls(parsed)

    def __str__(self) -> str:
        return str(self.value)


class AliasKind(StrEnum):
    SOURCE_SPAN = "source_span"
    TERM_CANDIDATE = "term_candidate"
    REQUIREMENT = "requirement"
    UNRESOLVED = "unresolved"
    INTENT_ARTIFACT = "intent_artifact"
    DIRECT_INPUT = "direct_input"
    EVIDENCE = "evidence"
    CONTEXT_POINT = "context_point"
    CONTEXT_LANE = "context_lane"
    DECISION_RUN = "decision_run"
    REQUIREMENT_ASSESSMENT = "requirement_assessment"
    WORK_ITEM = "work_item"
    DERIVED_NEED = "derived_need"
    TOOL_REQUEST = "tool_request"
    EXECUTION_RECEIPT = "execution_receipt"
    RECONCILIATION_RUN = "reconciliation_run"
    EVIDENCE_FINDING = "evidence_finding"
    CONTEXT_IMPACT_PROPOSAL = "context_impact_proposal"
    RECONCILIATION_REPAIR_REQUEST = "reconciliation_repair_request"
    PERSISTENCE_RECEIPT = "persistence_receipt"
    COMPLETION_ASSESSMENT = "completion_assessment"
    COMPLETION_PLAN = "completion_plan"
    FINAL_STANDING_PACKET = "final_standing_packet"
    RESULT_COMMENT = "result_comment"
    RESULT_ARTIFACT = "result_artifact"
    PUBLICATION_RECEIPT = "publication_receipt"
    SEMANTIC_ENTITY = "semantic_entity"


@dataclass(frozen=True, slots=True)
class AliasSpec:
    prefix: str
    width: int = 3


_ALIAS_SPECS: Final = MappingProxyType(
    {
        AliasKind.SOURCE_SPAN: AliasSpec("S"),
        AliasKind.TERM_CANDIDATE: AliasSpec("T"),
        AliasKind.REQUIREMENT: AliasSpec("R"),
        AliasKind.UNRESOLVED: AliasSpec("U"),
        AliasKind.INTENT_ARTIFACT: AliasSpec("I"),
        AliasKind.DIRECT_INPUT: AliasSpec("D"),
        AliasKind.EVIDENCE: AliasSpec("E"),
        AliasKind.CONTEXT_POINT: AliasSpec("C"),
        AliasKind.CONTEXT_LANE: AliasSpec("L"),
        AliasKind.DECISION_RUN: AliasSpec("DR"),
        AliasKind.REQUIREMENT_ASSESSMENT: AliasSpec("A"),
        AliasKind.WORK_ITEM: AliasSpec("W"),
        AliasKind.DERIVED_NEED: AliasSpec("DN"),
        AliasKind.TOOL_REQUEST: AliasSpec("TRQ"),
        AliasKind.EXECUTION_RECEIPT: AliasSpec("REC"),
        AliasKind.RECONCILIATION_RUN: AliasSpec("RCN"),
        AliasKind.EVIDENCE_FINDING: AliasSpec("EF"),
        AliasKind.CONTEXT_IMPACT_PROPOSAL: AliasSpec("CIP"),
        AliasKind.RECONCILIATION_REPAIR_REQUEST: AliasSpec("RRQ"),
        AliasKind.PERSISTENCE_RECEIPT: AliasSpec("PRC"),
        AliasKind.COMPLETION_ASSESSMENT: AliasSpec("CA"),
        AliasKind.COMPLETION_PLAN: AliasSpec("CP"),
        AliasKind.FINAL_STANDING_PACKET: AliasSpec("FSP"),
        AliasKind.RESULT_COMMENT: AliasSpec("RCM"),
        AliasKind.RESULT_ARTIFACT: AliasSpec("RST"),
        AliasKind.PUBLICATION_RECEIPT: AliasSpec("PUB"),
        AliasKind.SEMANTIC_ENTITY: AliasSpec("E", width=6),
    }
)
_ALIAS_PATTERN: Final = re.compile(r"[A-Z]+[0-9]+", flags=re.ASCII)


@dataclass(frozen=True, slots=True)
class ScopedAlias:
    """A non-authoritative readable alias whose identity includes its scope."""

    scope_id: CanonicalId
    kind: AliasKind
    ordinal: int

    def __post_init__(self) -> None:
        spec = _ALIAS_SPECS[self.kind]
        if not 1 <= self.ordinal <= (10**spec.width) - 1:
            raise IdentifierError(
                f"ordinal for {self.kind.value} must be between 1 and {(10**spec.width) - 1}"
            )

    @property
    def text(self) -> str:
        spec = _ALIAS_SPECS[self.kind]
        return f"{spec.prefix}{self.ordinal:0{spec.width}d}"

    @classmethod
    def parse(cls, text: str, *, kind: AliasKind, scope_id: CanonicalId) -> ScopedAlias:
        if not isinstance(text, str) or not text.isascii() or _ALIAS_PATTERN.fullmatch(text) is None:
            raise IdentifierError("alias must contain only uppercase ASCII letters and digits")
        spec = _ALIAS_SPECS[kind]
        expected_length = len(spec.prefix) + spec.width
        if len(text) != expected_length or not text.startswith(spec.prefix):
            raise IdentifierError(f"alias is not legal for {kind.value}")
        digits = text[len(spec.prefix) :]
        return cls(scope_id=scope_id, kind=kind, ordinal=int(digits))

    def __str__(self) -> str:
        return self.text


class AliasAllocator:
    """Host-only deterministic allocator for aliases within one canonical scope."""

    def __init__(self, scope_id: CanonicalId) -> None:
        self._scope_id = scope_id
        self._next_by_kind: dict[AliasKind, int] = {}

    @property
    def scope_id(self) -> CanonicalId:
        return self._scope_id

    def allocate(self, kind: AliasKind) -> ScopedAlias:
        ordinal = self._next_by_kind.get(kind, 1)
        alias = ScopedAlias(scope_id=self._scope_id, kind=kind, ordinal=ordinal)
        self._next_by_kind[kind] = ordinal + 1
        return alias
