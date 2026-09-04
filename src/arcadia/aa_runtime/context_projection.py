"""Deterministic whole-candidate context projection for learned calls.

Projection never edits a string, slices an array, or drops an object field. Recipe
controllers provide complete schema-valid candidates in explicit policy order; this
boundary selects the first candidate that fits exact structural and tokenizer counts.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum

from arcadia.aa_runtime.call_data_gate import require_pre_dispatch_call_data
from arcadia.aa_runtime.serializer import ModelMessage, SerializedAAECall, serialize_aae_call
from arcadia.contracts.aae.types import AAEContractRecord
from arcadia.core.canonical_json import JsonValue
from arcadia.core.hashing import Sha256Digest, sha256_canonical_json
from arcadia.core.validation import StrictJsonSchema
from arcadia.settings import SettingsSnapshot, TuningLimits

CONTEXT_PROJECTION_VERSION = "arcadia-context-projection-pre1"


class ContextProjectionError(ValueError):
    """Projection inputs or identity bindings are invalid."""


class ProjectionStanding(StrEnum):
    """Typed host outcome; no failure standing contains a dispatchable call."""

    SELECTED = "SELECTED"
    SETTINGS_INCOMPLETE = "SETTINGS_INCOMPLETE"
    BUDGET_EXHAUSTED = "BUDGET_EXHAUSTED"


class CandidateFailure(StrEnum):
    """Deterministic reasons a complete candidate cannot be selected."""

    MAX_STRING_CHARS = "MAX_STRING_CHARS"
    MAX_ARRAY_ITEMS = "MAX_ARRAY_ITEMS"
    MAX_NESTING_DEPTH = "MAX_NESTING_DEPTH"
    MAX_SOURCE_EXCERPT_CHARS = "MAX_SOURCE_EXCERPT_CHARS"
    MAX_INPUT_TOKENS = "MAX_INPUT_TOKENS"
    CONTEXT_WINDOW_TOKENS = "CONTEXT_WINDOW_TOKENS"


@dataclass(frozen=True, slots=True)
class ProjectionCandidate:
    """One whole host-built CALL_DATA alternative in explicit policy order."""

    candidate_id: str
    policy_id: str
    rank: int
    data_plane: JsonValue
    omitted_item_refs: tuple[str, ...] = ()
    source_excerpt_chars: tuple[int, ...] = ()

    def __post_init__(self) -> None:
        if type(self.candidate_id) is not str or not self.candidate_id:
            raise ContextProjectionError("candidate_id must be nonempty text")
        if type(self.policy_id) is not str or not self.policy_id:
            raise ContextProjectionError("policy_id must be nonempty text")
        if type(self.rank) is not int or self.rank < 0:
            raise ContextProjectionError("candidate rank must be a nonnegative integer")
        if any(type(ref) is not str or not ref for ref in self.omitted_item_refs):
            raise ContextProjectionError("omitted item references must be nonempty text")
        if len(set(self.omitted_item_refs)) != len(self.omitted_item_refs):
            raise ContextProjectionError("omitted item references must be unique")
        if any(type(length) is not int or length < 0 for length in self.source_excerpt_chars):
            raise ContextProjectionError("source excerpt lengths must be nonnegative integers")


@dataclass(frozen=True, slots=True)
class StructuralMetrics:
    max_string_chars: int
    max_array_items: int
    max_nesting_depth: int
    max_source_excerpt_chars: int

    def to_value(self) -> dict[str, JsonValue]:
        return {
            "max_array_items": self.max_array_items,
            "max_nesting_depth": self.max_nesting_depth,
            "max_source_excerpt_chars": self.max_source_excerpt_chars,
            "max_string_chars": self.max_string_chars,
        }


@dataclass(frozen=True, slots=True)
class CandidateEvaluation:
    candidate_id: str
    rank: int
    call_data_hash: Sha256Digest
    omitted_item_refs: tuple[str, ...]
    model_input_tokens: int
    structural_metrics: StructuralMetrics
    failures: tuple[CandidateFailure, ...]

    @property
    def fits(self) -> bool:
        return not self.failures

    def to_value(self) -> dict[str, JsonValue]:
        return {
            "call_data_hash": self.call_data_hash.value,
            "candidate_id": self.candidate_id,
            "failures": [failure.value for failure in self.failures],
            "model_input_tokens": self.model_input_tokens,
            "omitted_item_refs": list(self.omitted_item_refs),
            "rank": self.rank,
            "structural_metrics": self.structural_metrics.to_value(),
        }


@dataclass(frozen=True, slots=True)
class ContextProjectionEvidence:
    projection_version: str
    contract_id: str
    specialist_mode_id: str
    policy_id: str
    settings_profile_id: str
    settings_hash: Sha256Digest
    standing: ProjectionStanding
    context_window_tokens: int
    max_input_tokens: int | None
    reserved_output_tokens: int | None
    context_headroom_tokens: int | None
    missing_limit_names: tuple[str, ...]
    evaluations: tuple[CandidateEvaluation, ...]
    selected_candidate_id: str | None

    def to_value(self) -> dict[str, JsonValue]:
        return {
            "context_headroom_tokens": self.context_headroom_tokens,
            "context_window_tokens": self.context_window_tokens,
            "contract_id": self.contract_id,
            "evaluations": [evaluation.to_value() for evaluation in self.evaluations],
            "max_input_tokens": self.max_input_tokens,
            "missing_limit_names": list(self.missing_limit_names),
            "policy_id": self.policy_id,
            "projection_version": self.projection_version,
            "reserved_output_tokens": self.reserved_output_tokens,
            "selected_candidate_id": self.selected_candidate_id,
            "settings_hash": self.settings_hash.value,
            "settings_profile_id": self.settings_profile_id,
            "specialist_mode_id": self.specialist_mode_id,
            "standing": self.standing.value,
        }


@dataclass(frozen=True, slots=True)
class ContextProjectionResult:
    standing: ProjectionStanding
    selected_call: SerializedAAECall | None
    evidence: ContextProjectionEvidence
    evidence_hash: Sha256Digest

    @property
    def dispatchable(self) -> bool:
        return self.standing is ProjectionStanding.SELECTED and self.selected_call is not None


TokenCounter = Callable[[tuple[ModelMessage, ...]], int]


def _structural_metrics(
    value: JsonValue, *, source_excerpt_chars: tuple[int, ...]
) -> StructuralMetrics:
    max_string = 0
    max_array = 0
    max_depth = 0

    def visit(item: JsonValue, container_depth: int) -> None:
        nonlocal max_string, max_array, max_depth
        if type(item) is str:
            max_string = max(max_string, len(item))
            return
        if type(item) is list:
            next_depth = container_depth + 1
            max_depth = max(max_depth, next_depth)
            max_array = max(max_array, len(item))
            for child in item:
                visit(child, next_depth)
            return
        if type(item) is dict:
            next_depth = container_depth + 1
            max_depth = max(max_depth, next_depth)
            for child in item.values():
                visit(child, next_depth)

    visit(value, 0)
    return StructuralMetrics(
        max_string_chars=max_string,
        max_array_items=max_array,
        max_nesting_depth=max_depth,
        max_source_excerpt_chars=max(source_excerpt_chars, default=0),
    )


def _missing_limits(limits: TuningLimits) -> tuple[str, ...]:
    return tuple(
        name
        for name in (
            "max_input_tokens",
            "max_output_tokens",
            "max_string_chars",
            "max_array_items",
            "max_nesting_depth",
            "max_source_excerpt_chars",
            "context_headroom_tokens",
        )
        if getattr(limits, name) is None
    )


def _result(
    *,
    contract: AAEContractRecord,
    settings: SettingsSnapshot,
    standing: ProjectionStanding,
    context_window_tokens: int,
    evaluations: tuple[CandidateEvaluation, ...],
    selected_candidate_id: str | None,
    selected_call: SerializedAAECall | None,
    missing_limit_names: tuple[str, ...] = (),
) -> ContextProjectionResult:
    limits = settings.resolved.limits
    evidence = ContextProjectionEvidence(
        projection_version=CONTEXT_PROJECTION_VERSION,
        contract_id=contract.contract_id,
        specialist_mode_id=contract.specialist_mode_id,
        policy_id=contract.context_projection_policy_id,
        settings_profile_id=settings.resolved.profile_id,
        settings_hash=settings.settings_hash,
        standing=standing,
        context_window_tokens=context_window_tokens,
        max_input_tokens=limits.max_input_tokens,
        reserved_output_tokens=limits.max_output_tokens,
        context_headroom_tokens=limits.context_headroom_tokens,
        missing_limit_names=missing_limit_names,
        evaluations=evaluations,
        selected_candidate_id=selected_candidate_id,
    )
    return ContextProjectionResult(
        standing=standing,
        selected_call=selected_call,
        evidence=evidence,
        evidence_hash=sha256_canonical_json(evidence.to_value()),
    )


def project_aae_context(
    contract: AAEContractRecord,
    *,
    candidates: tuple[ProjectionCandidate, ...],
    input_schema: StrictJsonSchema,
    output_schema: StrictJsonSchema,
    settings: SettingsSnapshot,
    context_window_tokens: int,
    count_tokens: TokenCounter,
) -> ContextProjectionResult:
    """Select the first complete candidate that fits all exact configured bounds."""

    if type(context_window_tokens) is not int or context_window_tokens < 1:
        raise ContextProjectionError("context_window_tokens must be a positive integer")
    if settings.resolved.profile_id != contract.settings_profile_id:
        raise ContextProjectionError("settings profile does not match the AAE contract")
    if settings.resolved.specialist_mode_id != contract.specialist_mode_id:
        raise ContextProjectionError("settings specialist mode does not match the AAE contract")
    if not candidates:
        raise ContextProjectionError("at least one projection candidate is required")
    if len({candidate.candidate_id for candidate in candidates}) != len(candidates):
        raise ContextProjectionError("projection candidate IDs must be unique")
    ordered = tuple(sorted(candidates, key=lambda candidate: candidate.rank))
    if tuple(candidate.rank for candidate in ordered) != tuple(range(len(ordered))):
        raise ContextProjectionError(
            "projection candidate ranks must be unique and contiguous from zero"
        )
    if any(candidate.policy_id != contract.context_projection_policy_id for candidate in ordered):
        raise ContextProjectionError("projection candidate policy does not match the AAE contract")

    missing = _missing_limits(settings.resolved.limits)
    if missing:
        return _result(
            contract=contract,
            settings=settings,
            standing=ProjectionStanding.SETTINGS_INCOMPLETE,
            context_window_tokens=context_window_tokens,
            evaluations=(),
            selected_candidate_id=None,
            selected_call=None,
            missing_limit_names=missing,
        )

    limits = settings.resolved.limits
    assert limits.max_input_tokens is not None
    assert limits.max_output_tokens is not None
    assert limits.max_string_chars is not None
    assert limits.max_array_items is not None
    assert limits.max_nesting_depth is not None
    assert limits.max_source_excerpt_chars is not None
    assert limits.context_headroom_tokens is not None

    evaluations: list[CandidateEvaluation] = []
    for candidate in ordered:
        prepared = serialize_aae_call(
            contract,
            data_plane=candidate.data_plane,
            input_schema=input_schema,
            output_schema=output_schema,
        )
        gated = require_pre_dispatch_call_data(prepared, input_schema=input_schema)
        metrics = _structural_metrics(
            gated.value, source_excerpt_chars=candidate.source_excerpt_chars
        )
        token_count = count_tokens(prepared.messages)
        if type(token_count) is not int or token_count < 0:
            raise ContextProjectionError("token counter must return a nonnegative integer")

        failures: list[CandidateFailure] = []
        if metrics.max_string_chars > limits.max_string_chars:
            failures.append(CandidateFailure.MAX_STRING_CHARS)
        if metrics.max_array_items > limits.max_array_items:
            failures.append(CandidateFailure.MAX_ARRAY_ITEMS)
        if metrics.max_nesting_depth > limits.max_nesting_depth:
            failures.append(CandidateFailure.MAX_NESTING_DEPTH)
        if metrics.max_source_excerpt_chars > limits.max_source_excerpt_chars:
            failures.append(CandidateFailure.MAX_SOURCE_EXCERPT_CHARS)
        if token_count > limits.max_input_tokens:
            failures.append(CandidateFailure.MAX_INPUT_TOKENS)
        if (
            token_count + limits.max_output_tokens + limits.context_headroom_tokens
            > context_window_tokens
        ):
            failures.append(CandidateFailure.CONTEXT_WINDOW_TOKENS)

        evaluation = CandidateEvaluation(
            candidate_id=candidate.candidate_id,
            rank=candidate.rank,
            call_data_hash=gated.instance_hash,
            omitted_item_refs=candidate.omitted_item_refs,
            model_input_tokens=token_count,
            structural_metrics=metrics,
            failures=tuple(failures),
        )
        evaluations.append(evaluation)
        if evaluation.fits:
            return _result(
                contract=contract,
                settings=settings,
                standing=ProjectionStanding.SELECTED,
                context_window_tokens=context_window_tokens,
                evaluations=tuple(evaluations),
                selected_candidate_id=candidate.candidate_id,
                selected_call=prepared,
            )

    return _result(
        contract=contract,
        settings=settings,
        standing=ProjectionStanding.BUDGET_EXHAUSTED,
        context_window_tokens=context_window_tokens,
        evaluations=tuple(evaluations),
        selected_candidate_id=None,
        selected_call=None,
    )
