"""Immutable aggregate work-budget ledger with atomic fail-closed grants."""

from __future__ import annotations

import hmac
from dataclasses import dataclass
from enum import StrEnum
from typing import Final

from arcadia.core.canonical_json import JsonValue, canonical_json_dumps
from arcadia.core.config import BudgetConfig
from arcadia.core.hashing import Sha256Digest, sha256_canonical_json
from arcadia.core.ids import CanonicalId
from arcadia.core.repair_policy import RepairAttempt, RepairSession

WORK_BUDGET_VERSION = 1
BUDGET_EXHAUSTED_CODE: Final = "BUDGET_EXHAUSTED"


class BudgetDimension(StrEnum):
    MODEL_CALLS = "model_calls"
    REPAIR_ATTEMPTS = "repair_attempts"
    REENTRIES = "reentries"
    HISTORY_EXPANSIONS = "history_expansions"
    CONTEXT_RETRIEVAL_EXPANSIONS = "context_retrieval_expansions"
    DECISION_WORK_ITEMS = "decision_work_items"
    RECONCILIATION_DISCOVERY_DEPTH = "reconciliation_discovery_depth"
    SIDE_EFFECT_RETRIES = "side_effect_retries"
    COMPENSATIONS = "compensations"
    MODEL_INPUT_TOKENS = "model_input_tokens"
    MODEL_OUTPUT_TOKENS = "model_output_tokens"


class BudgetEventKind(StrEnum):
    MODEL_ATTEMPT = "MODEL_ATTEMPT"
    REPAIR_ATTEMPT = "REPAIR_ATTEMPT"
    REENTRY = "REENTRY"
    HISTORY_EXPANSION = "HISTORY_EXPANSION"
    CONTEXT_RETRIEVAL_EXPANSION = "CONTEXT_RETRIEVAL_EXPANSION"
    DECISION_WORK = "DECISION_WORK"
    RECONCILIATION_DISCOVERY = "RECONCILIATION_DISCOVERY"
    SIDE_EFFECT_RETRY = "SIDE_EFFECT_RETRY"
    COMPENSATION = "COMPENSATION"


class WorkBudgetError(ValueError):
    """Base error for invalid work-budget state or authorization."""


class BudgetFieldError(WorkBudgetError):
    """A budget field has an illegal type, range, or event shape."""


class BudgetIntegrityError(WorkBudgetError):
    """A budget identity, chain, ordering rule, or aggregate does not verify."""


class BudgetConflictError(WorkBudgetError):
    """A grant was requested against a stale or unexpected ledger head."""


class BudgetExhaustedError(WorkBudgetError):
    """An atomic grant would exceed a frozen budget ceiling."""

    code = BUDGET_EXHAUSTED_CODE

    def __init__(
        self,
        *,
        dimension: BudgetDimension,
        used: int,
        requested: int,
        limit: int,
    ) -> None:
        self.dimension = dimension
        self.used = used
        self.requested = requested
        self.limit = limit
        super().__init__(
            f"{self.code}: {dimension.value} used={used} requested={requested} limit={limit}"
        )

    def to_value(self) -> dict[str, JsonValue]:
        """Return a machine-readable denial for honest downstream degradation."""

        return {
            "code": self.code,
            "dimension": self.dimension.value,
            "limit": self.limit,
            "requested": self.requested,
            "used": self.used,
        }


def _nonnegative(name: str, value: object) -> int:
    if type(value) is not int or value < 0:
        raise BudgetFieldError(f"{name} must be a nonnegative integer")
    return value


def _positive(name: str, value: object) -> int:
    if type(value) is not int or value < 1:
        raise BudgetFieldError(f"{name} must be a positive integer")
    return value


def _digest_equal(left: Sha256Digest, right: Sha256Digest) -> bool:
    return hmac.compare_digest(left.value, right.value)


@dataclass(frozen=True, slots=True)
class BudgetLimits:
    """Frozen finite ceilings copied from Config V1."""

    max_model_calls: int
    max_repairs_per_call: int
    max_reentries: int
    max_history_expansions: int
    max_context_retrieval_expansions: int
    max_decision_work_items: int
    max_reconciliation_discovery_depth: int
    max_side_effect_retries: int
    max_compensations: int
    max_total_model_input_tokens: int
    max_total_model_output_tokens: int
    budget_version: int = WORK_BUDGET_VERSION

    def __post_init__(self) -> None:
        if type(self.budget_version) is not int or self.budget_version != WORK_BUDGET_VERSION:
            raise BudgetFieldError("unsupported work budget version")
        for name in (
            "max_model_calls",
            "max_repairs_per_call",
            "max_reentries",
            "max_history_expansions",
            "max_context_retrieval_expansions",
            "max_decision_work_items",
            "max_reconciliation_discovery_depth",
            "max_side_effect_retries",
            "max_compensations",
            "max_total_model_input_tokens",
            "max_total_model_output_tokens",
        ):
            _nonnegative(name, getattr(self, name))

    @classmethod
    def from_config(cls, config: BudgetConfig) -> BudgetLimits:
        """Copy validated Config V1 ceilings into an immutable runtime snapshot."""

        if type(config) is not BudgetConfig:
            raise BudgetFieldError("config must be a BudgetConfig")
        return cls(**config.model_dump())

    @property
    def limits_hash(self) -> Sha256Digest:
        return sha256_canonical_json(self.to_value())

    def ceiling(self, dimension: BudgetDimension) -> int | None:
        """Return the aggregate ceiling; repairs use a per-call ceiling."""

        if type(dimension) is not BudgetDimension:
            raise BudgetFieldError("dimension must be a BudgetDimension")
        mapping: dict[BudgetDimension, int | None] = {
            BudgetDimension.MODEL_CALLS: self.max_model_calls,
            BudgetDimension.REPAIR_ATTEMPTS: None,
            BudgetDimension.REENTRIES: self.max_reentries,
            BudgetDimension.HISTORY_EXPANSIONS: self.max_history_expansions,
            BudgetDimension.CONTEXT_RETRIEVAL_EXPANSIONS: (
                self.max_context_retrieval_expansions
            ),
            BudgetDimension.DECISION_WORK_ITEMS: self.max_decision_work_items,
            BudgetDimension.RECONCILIATION_DISCOVERY_DEPTH: (
                self.max_reconciliation_discovery_depth
            ),
            BudgetDimension.SIDE_EFFECT_RETRIES: self.max_side_effect_retries,
            BudgetDimension.COMPENSATIONS: self.max_compensations,
            BudgetDimension.MODEL_INPUT_TOKENS: self.max_total_model_input_tokens,
            BudgetDimension.MODEL_OUTPUT_TOKENS: self.max_total_model_output_tokens,
        }
        return mapping[dimension]

    def to_value(self) -> dict[str, JsonValue]:
        return {
            "budget_version": self.budget_version,
            "max_compensations": self.max_compensations,
            "max_context_retrieval_expansions": self.max_context_retrieval_expansions,
            "max_decision_work_items": self.max_decision_work_items,
            "max_history_expansions": self.max_history_expansions,
            "max_model_calls": self.max_model_calls,
            "max_reconciliation_discovery_depth": self.max_reconciliation_discovery_depth,
            "max_reentries": self.max_reentries,
            "max_repairs_per_call": self.max_repairs_per_call,
            "max_side_effect_retries": self.max_side_effect_retries,
            "max_total_model_input_tokens": self.max_total_model_input_tokens,
            "max_total_model_output_tokens": self.max_total_model_output_tokens,
        }


@dataclass(frozen=True, slots=True, order=True)
class BudgetCharge:
    """One exact dimension amount inside an atomic grant."""

    dimension: BudgetDimension
    amount: int

    def __post_init__(self) -> None:
        if type(self.dimension) is not BudgetDimension:
            raise BudgetFieldError("charge dimension must be a BudgetDimension")
        _nonnegative("charge amount", self.amount)

    def to_value(self) -> dict[str, JsonValue]:
        return {"amount": self.amount, "dimension": self.dimension.value}


@dataclass(frozen=True, slots=True)
class BudgetUsage:
    """Aggregate charged usage; discovery depth is a high-water mark."""

    model_calls: int = 0
    repair_attempts: int = 0
    reentries: int = 0
    history_expansions: int = 0
    context_retrieval_expansions: int = 0
    decision_work_items: int = 0
    reconciliation_discovery_depth: int = 0
    side_effect_retries: int = 0
    compensations: int = 0
    model_input_tokens: int = 0
    model_output_tokens: int = 0

    def __post_init__(self) -> None:
        for dimension in BudgetDimension:
            _nonnegative(dimension.value, self.amount(dimension))

    def amount(self, dimension: BudgetDimension) -> int:
        if type(dimension) is not BudgetDimension:
            raise BudgetFieldError("dimension must be a BudgetDimension")
        values = {
            BudgetDimension.MODEL_CALLS: self.model_calls,
            BudgetDimension.REPAIR_ATTEMPTS: self.repair_attempts,
            BudgetDimension.REENTRIES: self.reentries,
            BudgetDimension.HISTORY_EXPANSIONS: self.history_expansions,
            BudgetDimension.CONTEXT_RETRIEVAL_EXPANSIONS: (
                self.context_retrieval_expansions
            ),
            BudgetDimension.DECISION_WORK_ITEMS: self.decision_work_items,
            BudgetDimension.RECONCILIATION_DISCOVERY_DEPTH: (
                self.reconciliation_discovery_depth
            ),
            BudgetDimension.SIDE_EFFECT_RETRIES: self.side_effect_retries,
            BudgetDimension.COMPENSATIONS: self.compensations,
            BudgetDimension.MODEL_INPUT_TOKENS: self.model_input_tokens,
            BudgetDimension.MODEL_OUTPUT_TOKENS: self.model_output_tokens,
        }
        return values[dimension]

    def apply(self, charges: tuple[BudgetCharge, ...]) -> BudgetUsage:
        values = {dimension.value: self.amount(dimension) for dimension in BudgetDimension}
        for charge in charges:
            if charge.dimension is BudgetDimension.RECONCILIATION_DISCOVERY_DEPTH:
                values[charge.dimension.value] = max(
                    values[charge.dimension.value], charge.amount
                )
            else:
                values[charge.dimension.value] += charge.amount
        return BudgetUsage(**values)

    def to_value(self) -> dict[str, JsonValue]:
        return {dimension.value: self.amount(dimension) for dimension in BudgetDimension}


_EXPECTED_DIMENSIONS: Final = {
    BudgetEventKind.MODEL_ATTEMPT: frozenset(
        {
            BudgetDimension.MODEL_CALLS,
            BudgetDimension.MODEL_INPUT_TOKENS,
            BudgetDimension.MODEL_OUTPUT_TOKENS,
        }
    ),
    BudgetEventKind.REPAIR_ATTEMPT: frozenset(
        {
            BudgetDimension.MODEL_CALLS,
            BudgetDimension.REPAIR_ATTEMPTS,
            BudgetDimension.MODEL_INPUT_TOKENS,
            BudgetDimension.MODEL_OUTPUT_TOKENS,
        }
    ),
    BudgetEventKind.REENTRY: frozenset({BudgetDimension.REENTRIES}),
    BudgetEventKind.HISTORY_EXPANSION: frozenset({BudgetDimension.HISTORY_EXPANSIONS}),
    BudgetEventKind.CONTEXT_RETRIEVAL_EXPANSION: frozenset(
        {BudgetDimension.CONTEXT_RETRIEVAL_EXPANSIONS}
    ),
    BudgetEventKind.DECISION_WORK: frozenset({BudgetDimension.DECISION_WORK_ITEMS}),
    BudgetEventKind.RECONCILIATION_DISCOVERY: frozenset(
        {BudgetDimension.RECONCILIATION_DISCOVERY_DEPTH}
    ),
    BudgetEventKind.SIDE_EFFECT_RETRY: frozenset({BudgetDimension.SIDE_EFFECT_RETRIES}),
    BudgetEventKind.COMPENSATION: frozenset({BudgetDimension.COMPENSATIONS}),
}


@dataclass(frozen=True, slots=True)
class BudgetEntry:
    """One immutable atomic grant in the budget hash chain."""

    entry_id: CanonicalId
    sequence: int
    event_kind: BudgetEventKind
    operation_id: CanonicalId
    repair_call_id: CanonicalId | None
    repair_ordinal: int | None
    charges: tuple[BudgetCharge, ...]
    limits_hash: Sha256Digest
    previous_entry_hash: Sha256Digest | None
    entry_hash: Sha256Digest
    budget_version: int = WORK_BUDGET_VERSION

    def __post_init__(self) -> None:
        if type(self.budget_version) is not int or self.budget_version != WORK_BUDGET_VERSION:
            raise BudgetFieldError("unsupported work budget entry version")
        if type(self.entry_id) is not CanonicalId:
            raise BudgetFieldError("entry_id must be a CanonicalId")
        if type(self.operation_id) is not CanonicalId:
            raise BudgetFieldError("operation_id must be a CanonicalId")
        if self.entry_id == self.operation_id:
            raise BudgetIntegrityError("budget entry UUID must differ from operation UUID")
        _positive("sequence", self.sequence)
        if type(self.event_kind) is not BudgetEventKind:
            raise BudgetFieldError("event_kind must be a BudgetEventKind")
        if type(self.charges) is not tuple or not self.charges:
            raise BudgetFieldError("charges must be a nonempty immutable tuple")
        if any(type(charge) is not BudgetCharge for charge in self.charges):
            raise BudgetFieldError("every charge must be a BudgetCharge")
        ordered = tuple(sorted(self.charges, key=lambda charge: charge.dimension.value))
        if self.charges != ordered:
            raise BudgetFieldError("charges must use canonical dimension order")
        dimensions = [charge.dimension for charge in self.charges]
        if len(dimensions) != len(set(dimensions)):
            raise BudgetFieldError("an entry cannot repeat a budget dimension")
        if frozenset(dimensions) != _EXPECTED_DIMENSIONS[self.event_kind]:
            raise BudgetFieldError("charges do not match the event kind")
        model_call = next(
            (charge for charge in self.charges if charge.dimension is BudgetDimension.MODEL_CALLS),
            None,
        )
        if model_call is not None and model_call.amount != 1:
            raise BudgetFieldError("every model attempt must charge exactly one model call")
        amounts = {charge.dimension: charge.amount for charge in self.charges}
        unit_dimensions = {
            BudgetEventKind.REENTRY: BudgetDimension.REENTRIES,
            BudgetEventKind.HISTORY_EXPANSION: BudgetDimension.HISTORY_EXPANSIONS,
            BudgetEventKind.CONTEXT_RETRIEVAL_EXPANSION: (
                BudgetDimension.CONTEXT_RETRIEVAL_EXPANSIONS
            ),
            BudgetEventKind.SIDE_EFFECT_RETRY: BudgetDimension.SIDE_EFFECT_RETRIES,
            BudgetEventKind.COMPENSATION: BudgetDimension.COMPENSATIONS,
        }
        unit_dimension = unit_dimensions.get(self.event_kind)
        if unit_dimension is not None and amounts[unit_dimension] != 1:
            raise BudgetFieldError("this event must charge exactly one unit")
        if self.event_kind is BudgetEventKind.DECISION_WORK:
            _positive("decision work charge", amounts[BudgetDimension.DECISION_WORK_ITEMS])
        if self.event_kind is BudgetEventKind.RECONCILIATION_DISCOVERY:
            _positive(
                "reconciliation depth charge",
                amounts[BudgetDimension.RECONCILIATION_DISCOVERY_DEPTH],
            )
        if self.event_kind is BudgetEventKind.REPAIR_ATTEMPT:
            if type(self.repair_call_id) is not CanonicalId:
                raise BudgetFieldError("repair events require the original call UUID")
            if self.operation_id == self.repair_call_id:
                raise BudgetIntegrityError("repair operation UUID must differ from its call UUID")
            _positive("repair_ordinal", self.repair_ordinal)
            if amounts[BudgetDimension.REPAIR_ATTEMPTS] != 1:
                raise BudgetFieldError("every repair attempt must charge exactly one repair")
        elif self.repair_call_id is not None or self.repair_ordinal is not None:
            raise BudgetFieldError("non-repair events cannot carry repair lineage")
        if self.sequence == 1:
            if self.previous_entry_hash is not None:
                raise BudgetIntegrityError("the first budget entry cannot have a predecessor")
        elif type(self.previous_entry_hash) is not Sha256Digest:
            raise BudgetIntegrityError("later budget entries require a predecessor hash")
        if type(self.limits_hash) is not Sha256Digest:
            raise BudgetFieldError("limits_hash must be a Sha256Digest")
        if type(self.entry_hash) is not Sha256Digest:
            raise BudgetFieldError("entry_hash must be a Sha256Digest")
        expected_hash = sha256_canonical_json(self._unsigned_value())
        if not _digest_equal(expected_hash, self.entry_hash):
            raise BudgetIntegrityError("entry_hash does not match budget entry content")

    @classmethod
    def create(
        cls,
        *,
        sequence: int,
        event_kind: BudgetEventKind,
        operation_id: CanonicalId,
        repair_call_id: CanonicalId | None,
        repair_ordinal: int | None,
        charges: tuple[BudgetCharge, ...],
        limits_hash: Sha256Digest,
        previous_entry_hash: Sha256Digest | None,
    ) -> BudgetEntry:
        entry_id = CanonicalId.new()
        ordered = tuple(sorted(charges, key=lambda charge: charge.dimension.value))
        unsigned = _entry_value(
            entry_id=entry_id,
            sequence=sequence,
            event_kind=event_kind,
            operation_id=operation_id,
            repair_call_id=repair_call_id,
            repair_ordinal=repair_ordinal,
            charges=ordered,
            limits_hash=limits_hash,
            previous_entry_hash=previous_entry_hash,
        )
        return cls(
            entry_id=entry_id,
            sequence=sequence,
            event_kind=event_kind,
            operation_id=operation_id,
            repair_call_id=repair_call_id,
            repair_ordinal=repair_ordinal,
            charges=ordered,
            limits_hash=limits_hash,
            previous_entry_hash=previous_entry_hash,
            entry_hash=sha256_canonical_json(unsigned),
        )

    def _unsigned_value(self) -> dict[str, JsonValue]:
        return _entry_value(
            entry_id=self.entry_id,
            sequence=self.sequence,
            event_kind=self.event_kind,
            operation_id=self.operation_id,
            repair_call_id=self.repair_call_id,
            repair_ordinal=self.repair_ordinal,
            charges=self.charges,
            limits_hash=self.limits_hash,
            previous_entry_hash=self.previous_entry_hash,
        )

    def to_value(self) -> dict[str, JsonValue]:
        return {**self._unsigned_value(), "entry_hash": self.entry_hash.value}


def _entry_value(
    *,
    entry_id: CanonicalId,
    sequence: int,
    event_kind: BudgetEventKind,
    operation_id: CanonicalId,
    repair_call_id: CanonicalId | None,
    repair_ordinal: int | None,
    charges: tuple[BudgetCharge, ...],
    limits_hash: Sha256Digest,
    previous_entry_hash: Sha256Digest | None,
) -> dict[str, JsonValue]:
    return {
        "budget_version": WORK_BUDGET_VERSION,
        "charges": [charge.to_value() for charge in charges],
        "entry_uuid": str(entry_id),
        "event_kind": event_kind.value,
        "limits_hash": limits_hash.value,
        "operation_uuid": str(operation_id),
        "previous_entry_hash": (
            None if previous_entry_hash is None else previous_entry_hash.value
        ),
        "repair_call_uuid": None if repair_call_id is None else str(repair_call_id),
        "repair_ordinal": repair_ordinal,
        "sequence": sequence,
    }


@dataclass(frozen=True, slots=True)
class WorkBudgetLedger:
    """Immutable, append-only aggregate authorization ledger."""

    limits: BudgetLimits
    entries: tuple[BudgetEntry, ...] = ()

    def __post_init__(self) -> None:
        if type(self.limits) is not BudgetLimits:
            raise BudgetFieldError("limits must be BudgetLimits")
        if type(self.entries) is not tuple:
            raise BudgetFieldError("entries must be an immutable tuple")
        self._replay()

    @classmethod
    def create(cls, limits: BudgetLimits) -> WorkBudgetLedger:
        return cls(limits=limits)

    @property
    def head_hash(self) -> Sha256Digest | None:
        return None if not self.entries else self.entries[-1].entry_hash

    @property
    def usage(self) -> BudgetUsage:
        usage, _ = self._replay()
        return usage

    def remaining(self, dimension: BudgetDimension) -> int | None:
        """Return ungranted capacity; repairs are queried per original call."""

        ceiling = self.limits.ceiling(dimension)
        if ceiling is None:
            return None
        return ceiling - self.usage.amount(dimension)

    def repairs_used_for(self, call_id: CanonicalId) -> int:
        if type(call_id) is not CanonicalId:
            raise BudgetFieldError("call_id must be a CanonicalId")
        return sum(
            1
            for entry in self.entries
            if entry.event_kind is BudgetEventKind.REPAIR_ATTEMPT
            and entry.repair_call_id == call_id
        )

    def repairs_remaining_for(self, call_id: CanonicalId) -> int:
        return self.limits.max_repairs_per_call - self.repairs_used_for(call_id)

    def authorize_model_attempt(
        self,
        *,
        call_id: CanonicalId,
        input_tokens: int,
        reserved_output_tokens: int,
        expected_head: Sha256Digest | None,
    ) -> tuple[WorkBudgetLedger, BudgetEntry]:
        """Atomically reserve one learned call and its full token allowance."""

        return self._append(
            event_kind=BudgetEventKind.MODEL_ATTEMPT,
            operation_id=call_id,
            repair_call_id=None,
            repair_ordinal=None,
            charges=(
                BudgetCharge(BudgetDimension.MODEL_CALLS, 1),
                BudgetCharge(BudgetDimension.MODEL_INPUT_TOKENS, _nonnegative("input_tokens", input_tokens)),
                BudgetCharge(
                    BudgetDimension.MODEL_OUTPUT_TOKENS,
                    _nonnegative("reserved_output_tokens", reserved_output_tokens),
                ),
            ),
            expected_head=expected_head,
        )

    def authorize_repair_attempt(
        self,
        *,
        session: RepairSession,
        attempt: RepairAttempt,
        input_tokens: int,
        reserved_output_tokens: int,
        expected_head: Sha256Digest | None,
    ) -> tuple[WorkBudgetLedger, BudgetEntry]:
        """Atomically bind one repair authorization to aggregate call/token caps."""

        if type(session) is not RepairSession or type(attempt) is not RepairAttempt:
            raise BudgetFieldError("repair authorization requires typed session and attempt")
        if session.policy.max_repairs_per_call != self.limits.max_repairs_per_call:
            raise BudgetIntegrityError("repair policy cap differs from work-budget limits")
        if not session.attempts or session.attempts[-1] != attempt:
            raise BudgetIntegrityError("attempt must be the current repair-session head")
        return self._append(
            event_kind=BudgetEventKind.REPAIR_ATTEMPT,
            operation_id=attempt.attempt_id,
            repair_call_id=attempt.call_id,
            repair_ordinal=attempt.repair_ordinal,
            charges=(
                BudgetCharge(BudgetDimension.MODEL_CALLS, 1),
                BudgetCharge(BudgetDimension.REPAIR_ATTEMPTS, 1),
                BudgetCharge(BudgetDimension.MODEL_INPUT_TOKENS, _nonnegative("input_tokens", input_tokens)),
                BudgetCharge(
                    BudgetDimension.MODEL_OUTPUT_TOKENS,
                    _nonnegative("reserved_output_tokens", reserved_output_tokens),
                ),
            ),
            expected_head=expected_head,
        )

    def authorize_reentry(
        self, *, operation_id: CanonicalId, expected_head: Sha256Digest | None
    ) -> tuple[WorkBudgetLedger, BudgetEntry]:
        return self._single(BudgetEventKind.REENTRY, operation_id, 1, expected_head)

    def authorize_history_expansion(
        self, *, operation_id: CanonicalId, expected_head: Sha256Digest | None
    ) -> tuple[WorkBudgetLedger, BudgetEntry]:
        return self._single(BudgetEventKind.HISTORY_EXPANSION, operation_id, 1, expected_head)

    def authorize_context_retrieval_expansion(
        self, *, operation_id: CanonicalId, expected_head: Sha256Digest | None
    ) -> tuple[WorkBudgetLedger, BudgetEntry]:
        return self._single(
            BudgetEventKind.CONTEXT_RETRIEVAL_EXPANSION, operation_id, 1, expected_head
        )

    def authorize_decision_work(
        self,
        *,
        operation_id: CanonicalId,
        work_items: int,
        expected_head: Sha256Digest | None,
    ) -> tuple[WorkBudgetLedger, BudgetEntry]:
        return self._single(
            BudgetEventKind.DECISION_WORK,
            operation_id,
            _positive("work_items", work_items),
            expected_head,
        )

    def authorize_reconciliation_discovery(
        self,
        *,
        operation_id: CanonicalId,
        depth: int,
        expected_head: Sha256Digest | None,
    ) -> tuple[WorkBudgetLedger, BudgetEntry]:
        return self._single(
            BudgetEventKind.RECONCILIATION_DISCOVERY,
            operation_id,
            _positive("depth", depth),
            expected_head,
        )

    def authorize_side_effect_retry(
        self, *, operation_id: CanonicalId, expected_head: Sha256Digest | None
    ) -> tuple[WorkBudgetLedger, BudgetEntry]:
        return self._single(BudgetEventKind.SIDE_EFFECT_RETRY, operation_id, 1, expected_head)

    def authorize_compensation(
        self, *, operation_id: CanonicalId, expected_head: Sha256Digest | None
    ) -> tuple[WorkBudgetLedger, BudgetEntry]:
        return self._single(BudgetEventKind.COMPENSATION, operation_id, 1, expected_head)

    def _single(
        self,
        event_kind: BudgetEventKind,
        operation_id: CanonicalId,
        amount: int,
        expected_head: Sha256Digest | None,
    ) -> tuple[WorkBudgetLedger, BudgetEntry]:
        dimension = next(iter(_EXPECTED_DIMENSIONS[event_kind]))
        return self._append(
            event_kind=event_kind,
            operation_id=operation_id,
            repair_call_id=None,
            repair_ordinal=None,
            charges=(BudgetCharge(dimension, amount),),
            expected_head=expected_head,
        )

    def _append(
        self,
        *,
        event_kind: BudgetEventKind,
        operation_id: CanonicalId,
        repair_call_id: CanonicalId | None,
        repair_ordinal: int | None,
        charges: tuple[BudgetCharge, ...],
        expected_head: Sha256Digest | None,
    ) -> tuple[WorkBudgetLedger, BudgetEntry]:
        self._require_expected_head(expected_head)
        if type(operation_id) is not CanonicalId:
            raise BudgetFieldError("operation_id must be a CanonicalId")
        if any(entry.operation_id == operation_id for entry in self.entries):
            raise BudgetIntegrityError("operation UUID already has a budget grant")
        self._preflight(charges, repair_call_id, repair_ordinal)
        entry = BudgetEntry.create(
            sequence=len(self.entries) + 1,
            event_kind=event_kind,
            operation_id=operation_id,
            repair_call_id=repair_call_id,
            repair_ordinal=repair_ordinal,
            charges=charges,
            limits_hash=self.limits.limits_hash,
            previous_entry_hash=self.head_hash,
        )
        advanced = WorkBudgetLedger(limits=self.limits, entries=(*self.entries, entry))
        return advanced, entry

    def _require_expected_head(self, expected_head: Sha256Digest | None) -> None:
        actual = self.head_hash
        if actual is None:
            if expected_head is not None:
                raise BudgetConflictError("empty budget ledger requires expected_head=None")
            return
        if type(expected_head) is not Sha256Digest or not _digest_equal(actual, expected_head):
            raise BudgetConflictError("expected budget head does not match current head")

    def _preflight(
        self,
        charges: tuple[BudgetCharge, ...],
        repair_call_id: CanonicalId | None,
        repair_ordinal: int | None,
    ) -> None:
        usage = self.usage
        for charge in charges:
            ceiling = self.limits.ceiling(charge.dimension)
            if ceiling is None:
                continue
            used = usage.amount(charge.dimension)
            candidate = (
                max(used, charge.amount)
                if charge.dimension is BudgetDimension.RECONCILIATION_DISCOVERY_DEPTH
                else used + charge.amount
            )
            if candidate > ceiling:
                raise BudgetExhaustedError(
                    dimension=charge.dimension,
                    used=used,
                    requested=charge.amount,
                    limit=ceiling,
                )
        if repair_call_id is not None:
            assert repair_ordinal is not None
            if not any(
                entry.event_kind is BudgetEventKind.MODEL_ATTEMPT
                and entry.operation_id == repair_call_id
                for entry in self.entries
            ):
                raise BudgetIntegrityError(
                    "repair call UUID has no prior original model-attempt grant"
                )
            used = self.repairs_used_for(repair_call_id)
            if repair_ordinal != used + 1:
                raise BudgetIntegrityError("repair grant ordinal is not next for this call")
            if used + 1 > self.limits.max_repairs_per_call:
                raise BudgetExhaustedError(
                    dimension=BudgetDimension.REPAIR_ATTEMPTS,
                    used=used,
                    requested=1,
                    limit=self.limits.max_repairs_per_call,
                )

    def _replay(self) -> tuple[BudgetUsage, dict[CanonicalId, int]]:
        usage = BudgetUsage()
        repair_counts: dict[CanonicalId, int] = {}
        entry_ids: set[CanonicalId] = set()
        operation_ids: set[CanonicalId] = set()
        original_model_calls: set[CanonicalId] = set()
        previous: Sha256Digest | None = None
        for sequence, entry in enumerate(self.entries, start=1):
            if type(entry) is not BudgetEntry:
                raise BudgetFieldError("every ledger item must be a BudgetEntry")
            if entry.sequence != sequence:
                raise BudgetIntegrityError("budget sequences must be contiguous from one")
            if entry.entry_id in entry_ids or entry.operation_id in operation_ids:
                raise BudgetIntegrityError("budget entry and operation UUIDs must be unique")
            entry_ids.add(entry.entry_id)
            operation_ids.add(entry.operation_id)
            if not _digest_equal(entry.limits_hash, self.limits.limits_hash):
                raise BudgetIntegrityError("budget entry uses different frozen limits")
            if entry.previous_entry_hash != previous:
                raise BudgetIntegrityError("budget predecessor chain is broken")
            self._check_replay_ceiling(usage, entry.charges)
            if entry.event_kind is BudgetEventKind.REPAIR_ATTEMPT:
                assert entry.repair_call_id is not None
                assert entry.repair_ordinal is not None
                if entry.repair_call_id not in original_model_calls:
                    raise BudgetIntegrityError(
                        "repair call UUID has no prior original model-attempt grant"
                    )
                used = repair_counts.get(entry.repair_call_id, 0)
                if entry.repair_ordinal != used + 1:
                    raise BudgetIntegrityError("repair ordinals must be contiguous per call")
                if used + 1 > self.limits.max_repairs_per_call:
                    raise BudgetIntegrityError("repair history exceeds its per-call cap")
                repair_counts[entry.repair_call_id] = used + 1
            elif entry.event_kind is BudgetEventKind.MODEL_ATTEMPT:
                original_model_calls.add(entry.operation_id)
            usage = usage.apply(entry.charges)
            previous = entry.entry_hash
        return usage, repair_counts

    def _check_replay_ceiling(
        self, usage: BudgetUsage, charges: tuple[BudgetCharge, ...]
    ) -> None:
        for charge in charges:
            ceiling = self.limits.ceiling(charge.dimension)
            if ceiling is None:
                continue
            used = usage.amount(charge.dimension)
            candidate = (
                max(used, charge.amount)
                if charge.dimension is BudgetDimension.RECONCILIATION_DISCOVERY_DEPTH
                else used + charge.amount
            )
            if candidate > ceiling:
                raise BudgetIntegrityError("budget history exceeds frozen limits")

    def to_value(self) -> dict[str, JsonValue]:
        """Return a canonical snapshot retaining every grant and aggregate."""

        return {
            "budget_version": WORK_BUDGET_VERSION,
            "entries": [entry.to_value() for entry in self.entries],
            "entry_count": len(self.entries),
            "head_hash": None if self.head_hash is None else self.head_hash.value,
            "limits": self.limits.to_value(),
            "limits_hash": self.limits.limits_hash.value,
            "usage": self.usage.to_value(),
        }

    def to_json(self) -> str:
        return canonical_json_dumps(self.to_value())
