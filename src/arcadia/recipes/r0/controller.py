"""Host-owned Recipe 0 conversation-scope orchestration and packet freezing."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from arcadia.aa_runtime.invoker import SpecialistInvocation, SpecialistInvoker
from arcadia.contracts.aae.registry import MODE_SCOPE_PROPOSAL, MODE_SCOPE_VALIDATION
from arcadia.contracts.schemas.r0.scope_proposal import (
    SCOPE_PROPOSAL_INPUT_SCHEMA,
    ScopeProposalSemanticError,
    require_valid_scope_proposal_output,
)
from arcadia.contracts.schemas.r0.scope_validation import (
    PRE1_MAX_RETRIEVED_TURNS,
    ScopeValidationSemanticError,
    require_valid_scope_validation_call_data,
    require_valid_scope_validation_output,
)
from arcadia.core.canonical_json import JsonValue
from arcadia.core.hashing import Sha256Digest, sha256_canonical_json, sha256_text
from arcadia.core.ids import CanonicalId
from arcadia.storage.transcript_repository import (
    MAX_RECENT_EXCHANGES,
    MAX_TARGETED_TURNS,
    CompletedExchange,
    TranscriptFieldError,
    TranscriptRepository,
)

HistoryTokenCounter = Callable[[tuple[dict[str, JsonValue], ...]], int]


class Recipe0ControllerError(RuntimeError):
    """Recipe 0 host orchestration cannot safely complete the requested scope."""


class Recipe0HistoryBoundExceeded(Recipe0ControllerError):
    """Exact retrieved transcript evidence exceeds the configured injected-history bound."""


def _frozen_exchange(exchange: CompletedExchange) -> dict[str, JsonValue]:
    return {
        "turn_uuid": str(exchange.turn.turn_id),
        "turn_index": exchange.turn.turn_ordinal,
        "user_message": exchange.user_entry.content,
        "final_response": exchange.assistant_entry.content,
        "user_message_hash": exchange.user_entry.content_hash.value,
        "final_response_hash": exchange.assistant_entry.content_hash.value,
    }


def _frozen_exchanges(
    exchanges: tuple[CompletedExchange, ...],
) -> tuple[dict[str, JsonValue], ...]:
    return tuple(_frozen_exchange(exchange) for exchange in exchanges)


@dataclass(frozen=True, slots=True)
class Recipe0Policy:
    """Host-owned bounded transcript policy for the PRE-1 Recipe 0 slice."""

    max_contiguous_lookback_exchanges: int = MAX_RECENT_EXCHANGES
    max_targeted_candidate_turns_per_search: int = MAX_TARGETED_TURNS
    max_scope_expansion_cycles: int = 3
    max_total_injected_history_tokens: int = 4096

    def __post_init__(self) -> None:
        exact_ints = (
            self.max_contiguous_lookback_exchanges,
            self.max_targeted_candidate_turns_per_search,
            self.max_scope_expansion_cycles,
            self.max_total_injected_history_tokens,
        )
        if any(type(value) is not int for value in exact_ints):
            raise Recipe0ControllerError("Recipe 0 policy limits must be exact integers")
        if not 0 <= self.max_contiguous_lookback_exchanges <= MAX_RECENT_EXCHANGES:
            raise Recipe0ControllerError(
                f"max_contiguous_lookback_exchanges must be within 0..{MAX_RECENT_EXCHANGES}"
            )
        if not 0 <= self.max_targeted_candidate_turns_per_search <= MAX_TARGETED_TURNS:
            raise Recipe0ControllerError(
                "max_targeted_candidate_turns_per_search must be within "
                f"0..{MAX_TARGETED_TURNS}"
            )
        if self.max_scope_expansion_cycles < 0:
            raise Recipe0ControllerError("max_scope_expansion_cycles must be nonnegative")
        if self.max_total_injected_history_tokens < 1:
            raise Recipe0ControllerError(
                "max_total_injected_history_tokens must be at least 1"
            )

    def proposal_limits(self) -> dict[str, JsonValue]:
        return {
            "max_contiguous_lookback_exchanges": self.max_contiguous_lookback_exchanges,
            "max_targeted_candidate_turns_per_search": (
                self.max_targeted_candidate_turns_per_search
            ),
            "max_scope_expansion_cycles": self.max_scope_expansion_cycles,
            "max_total_injected_history_tokens": self.max_total_injected_history_tokens,
        }

    def validation_limits(self, *, remaining_expansion_cycles: int) -> dict[str, JsonValue]:
        return {
            "remaining_expansion_cycles": remaining_expansion_cycles,
            "max_total_injected_history_tokens": self.max_total_injected_history_tokens,
        }


@dataclass(frozen=True, slots=True)
class ConversationPacket:
    turn_id: CanonicalId
    conversation_id: CanonicalId
    raw_user_prompt: str
    raw_prompt_hash: Sha256Digest
    transcript_commit_seq: int
    included_turns: tuple[dict[str, JsonValue], ...]
    unresolved_references: tuple[str, ...]
    scope_status: str
    packet_hash: Sha256Digest

    @classmethod
    def freeze(
        cls,
        *,
        turn_id: CanonicalId,
        conversation_id: CanonicalId,
        raw_user_prompt: str,
        transcript_commit_seq: int,
        included_turns: tuple[dict[str, JsonValue], ...],
        unresolved_references: tuple[str, ...],
        scope_status: str,
    ) -> ConversationPacket:
        value: dict[str, JsonValue] = {
            "conversation_uuid": str(conversation_id),
            "included_turns": list(included_turns),
            "raw_prompt_hash": sha256_text(raw_user_prompt).value,
            "raw_user_prompt": raw_user_prompt,
            "scope_status": scope_status,
            "transcript_commit_seq": transcript_commit_seq,
            "turn_uuid": str(turn_id),
            "unresolved_references": list(unresolved_references),
        }
        return cls(
            turn_id=turn_id,
            conversation_id=conversation_id,
            raw_user_prompt=raw_user_prompt,
            raw_prompt_hash=sha256_text(raw_user_prompt),
            transcript_commit_seq=transcript_commit_seq,
            included_turns=included_turns,
            unresolved_references=unresolved_references,
            scope_status=scope_status,
            packet_hash=sha256_canonical_json(value),
        )


@dataclass(frozen=True, slots=True)
class Recipe0ContinuationController:
    """Accepted one-next-turn continuation projection and exact prefetch boundary."""

    transcript: TranscriptRepository

    def build_scope_proposal_call_data(
        self,
        *,
        turn_id: CanonicalId,
        conversation_id: CanonicalId,
        raw_user_prompt: str,
        host_policy_limits: dict[str, JsonValue],
    ) -> dict[str, JsonValue]:
        state = self.transcript.continuation_state_for_turn(turn_id=turn_id)
        call_data: dict[str, JsonValue] = {
            "mode": MODE_SCOPE_PROPOSAL,
            "turn_uuid": str(turn_id),
            "conversation_uuid": str(conversation_id),
            "raw_user_prompt": raw_user_prompt,
            "current_transcript_metadata": {
                "transcript_commit_seq": self.transcript.transcript_commit_seq(),
                "completed_exchange_count": self.transcript.completed_exchange_count(
                    conversation_id=conversation_id
                ),
                "continuation_state": state.to_value(),
            },
            "host_policy_limits": host_policy_limits,
        }
        SCOPE_PROPOSAL_INPUT_SCHEMA.require_valid(call_data)
        return call_data

    def build_open_continuation_validation_call_data(
        self,
        *,
        turn_id: CanonicalId,
        conversation_id: CanonicalId,
        raw_user_prompt: str,
        host_policy_limits: dict[str, JsonValue],
    ) -> dict[str, JsonValue] | None:
        exchange = self.transcript.load_continuation_exchange(turn_id=turn_id)
        if exchange is None:
            return None
        call_data: dict[str, JsonValue] = {
            "mode": MODE_SCOPE_VALIDATION,
            "turn_uuid": str(turn_id),
            "conversation_uuid": str(conversation_id),
            "raw_user_prompt": raw_user_prompt,
            "frozen_retrieved_turns": [_frozen_exchange(exchange)],
            "host_policy_limits": host_policy_limits,
        }
        require_valid_scope_validation_call_data(call_data)
        return call_data

    def freeze_open_continuation_packet(
        self,
        *,
        call_data: dict[str, JsonValue],
        validation_output: dict[str, JsonValue],
    ) -> ConversationPacket:
        require_valid_scope_validation_output(validation_output, call_data=call_data)
        status = validation_output["status"]
        assert type(status) is str
        if status not in {"SUFFICIENT", "SUFFICIENT_WITHOUT_HISTORY"}:
            raise ScopeValidationSemanticError(
                f"cannot freeze Conversation Packet from unresolved status {status}"
            )
        packet = _freeze_validation_packet(
            transcript=self.transcript,
            call_data=call_data,
            validation_output=validation_output,
        )
        self.transcript.consume_continuation(
            turn_id=CanonicalId.parse(str(call_data["turn_uuid"]))
        )
        return packet


@dataclass(frozen=True, slots=True)
class Recipe0Result:
    packet: ConversationPacket
    proposal_invocation: SpecialistInvocation | None
    validation_invocations: tuple[SpecialistInvocation, ...]

    @property
    def validation_invocation(self) -> SpecialistInvocation | None:
        """Compatibility view of the final validation attempt, if one ran."""

        return None if not self.validation_invocations else self.validation_invocations[-1]


@dataclass(slots=True)
class _HistoryState:
    included: dict[CanonicalId, CompletedExchange]
    recent_turn_ids: set[CanonicalId]

    @classmethod
    def empty(cls) -> _HistoryState:
        return cls({}, set())

    def add(
        self,
        exchanges: tuple[CompletedExchange, ...],
        *,
        recent_scope: bool,
    ) -> None:
        for exchange in exchanges:
            turn_id = exchange.turn.turn_id
            self.included.setdefault(turn_id, exchange)
            if recent_scope:
                self.recent_turn_ids.add(turn_id)

    def frozen(self) -> tuple[dict[str, JsonValue], ...]:
        ordered = tuple(
            sorted(self.included.values(), key=lambda exchange: exchange.turn.turn_ordinal)
        )
        return _frozen_exchanges(ordered)


def _freeze_validation_packet(
    *,
    transcript: TranscriptRepository,
    call_data: dict[str, JsonValue],
    validation_output: dict[str, JsonValue],
) -> ConversationPacket:
    require_valid_scope_validation_output(validation_output, call_data=call_data)
    status = validation_output["status"]
    turns = call_data["frozen_retrieved_turns"]
    unresolved = validation_output["unresolved_references"]
    assert type(status) is str
    assert type(turns) is list
    assert type(unresolved) is list
    included_turns: list[dict[str, JsonValue]] = []
    for turn in turns:
        if type(turn) is not dict:
            raise ScopeValidationSemanticError("validated transcript turn is not an object")
        included_turns.append(turn)
    included = () if status == "SUFFICIENT_WITHOUT_HISTORY" else tuple(included_turns)
    return ConversationPacket.freeze(
        turn_id=CanonicalId.parse(str(call_data["turn_uuid"])),
        conversation_id=CanonicalId.parse(str(call_data["conversation_uuid"])),
        raw_user_prompt=str(call_data["raw_user_prompt"]),
        transcript_commit_seq=transcript.transcript_commit_seq(),
        included_turns=included,
        unresolved_references=tuple(str(item) for item in unresolved),
        scope_status=status,
    )


@dataclass(frozen=True, slots=True)
class Recipe0ConversationController:
    """Execute bounded Recipe 0 transcript resolution with deterministic expansion.

    PRE-1 host policy resolves the validator's fixed-shape expansion requests without
    inventing model fields: NEEDS_MORE_RECENT expands the contiguous recent scope to
    the configured host maximum in one delta-only cycle; NEEDS_TARGETED_HISTORY uses
    the validator's unresolved-reference strings as bounded transcript-FTS queries.
    """

    transcript: TranscriptRepository
    invoker: SpecialistInvoker
    history_token_counter: HistoryTokenCounter
    policy: Recipe0Policy = Recipe0Policy()

    def _history_token_count(self, turns: tuple[dict[str, JsonValue], ...]) -> int:
        token_count = self.history_token_counter(turns)
        if type(token_count) is not int or token_count < 0:
            raise Recipe0ControllerError(
                "history token counter must return a nonnegative exact integer"
            )
        return token_count

    def _require_history_bound(self, turns: tuple[dict[str, JsonValue], ...]) -> None:
        if self._history_token_count(turns) > self.policy.max_total_injected_history_tokens:
            raise Recipe0HistoryBoundExceeded(
                "retrieved transcript evidence exceeds max_total_injected_history_tokens"
            )

    def _fits_history_bound(self, turns: tuple[dict[str, JsonValue], ...]) -> bool:
        return self._history_token_count(turns) <= self.policy.max_total_injected_history_tokens

    def _validation_call_data(
        self,
        *,
        turn_id: CanonicalId,
        conversation_id: CanonicalId,
        raw_user_prompt: str,
        frozen_turns: tuple[dict[str, JsonValue], ...],
        remaining_expansion_cycles: int,
    ) -> dict[str, JsonValue]:
        self._require_history_bound(frozen_turns)
        call_data: dict[str, JsonValue] = {
            "mode": MODE_SCOPE_VALIDATION,
            "turn_uuid": str(turn_id),
            "conversation_uuid": str(conversation_id),
            "raw_user_prompt": raw_user_prompt,
            "frozen_retrieved_turns": list(frozen_turns),
            "host_policy_limits": self.policy.validation_limits(
                remaining_expansion_cycles=remaining_expansion_cycles
            ),
        }
        require_valid_scope_validation_call_data(call_data)
        return call_data

    def _targeted_exchanges(
        self,
        *,
        conversation_id: CanonicalId,
        terms: tuple[str, ...],
        excluded_turn_ids: set[CanonicalId] | None = None,
        max_new_turns: int = PRE1_MAX_RETRIEVED_TURNS,
    ) -> tuple[tuple[CompletedExchange, ...], bool]:
        if type(max_new_turns) is not int or max_new_turns < 0:
            raise Recipe0ControllerError("max_new_turns must be a nonnegative exact integer")
        excluded = set() if excluded_turn_ids is None else excluded_turn_ids
        by_turn: dict[CanonicalId, CompletedExchange] = {}
        had_hits = False
        if max_new_turns == 0:
            return (), False
        for term in terms:
            try:
                hits = self.transcript.search_targeted(
                    conversation_id=conversation_id,
                    query=term,
                    limit=self.policy.max_targeted_candidate_turns_per_search,
                )
            except TranscriptFieldError:
                continue
            had_hits = had_hits or bool(hits)
            for hit in hits:
                turn_id = hit.entry.turn_id
                if turn_id in excluded or turn_id in by_turn:
                    continue
                by_turn[turn_id] = self.transcript.load_completed_exchange(turn_id=turn_id)
                if len(by_turn) == max_new_turns:
                    break
            if len(by_turn) == max_new_turns:
                break
        ordered = tuple(
            sorted(by_turn.values(), key=lambda exchange: exchange.turn.turn_ordinal)
        )
        return ordered, had_hits

    def _freeze_host_terminal(
        self,
        *,
        turn_id: CanonicalId,
        conversation_id: CanonicalId,
        raw_user_prompt: str,
        state: _HistoryState,
        status: str,
        unresolved_references: tuple[str, ...],
        consume_continuation: bool,
    ) -> ConversationPacket:
        packet = ConversationPacket.freeze(
            turn_id=turn_id,
            conversation_id=conversation_id,
            raw_user_prompt=raw_user_prompt,
            transcript_commit_seq=self.transcript.transcript_commit_seq(),
            included_turns=state.frozen(),
            unresolved_references=unresolved_references,
            scope_status=status,
        )
        if consume_continuation:
            self.transcript.consume_continuation(turn_id=turn_id)
        return packet

    def _recent_expansion_delta(
        self,
        *,
        conversation_id: CanonicalId,
        state: _HistoryState,
    ) -> tuple[CompletedExchange, ...]:
        max_recent = self.policy.max_contiguous_lookback_exchanges
        if max_recent == 0 or len(state.recent_turn_ids) >= max_recent:
            return ()

        if not state.recent_turn_ids:
            recent = self.transcript.load_recent_exchanges(
                conversation_id=conversation_id,
                limit=max_recent,
            )
            return tuple(
                exchange for exchange in recent if exchange.turn.turn_id not in state.included
            )

        recent_exchanges = tuple(
            state.included[turn_id]
            for turn_id in state.recent_turn_ids
            if turn_id in state.included
        )
        oldest_ordinal = min(exchange.turn.turn_ordinal for exchange in recent_exchanges)
        remaining_capacity = max_recent - len(state.recent_turn_ids)
        delta = self.transcript.load_recent_exchanges_before(
            conversation_id=conversation_id,
            before_turn_ordinal=oldest_ordinal,
            limit=remaining_capacity,
        )
        return tuple(
            exchange for exchange in delta if exchange.turn.turn_id not in state.included
        )

    def _validate_until_terminal(
        self,
        *,
        turn_id: CanonicalId,
        conversation_id: CanonicalId,
        raw_user_prompt: str,
        state: _HistoryState,
        remaining_expansion_cycles: int,
        consume_continuation: bool,
    ) -> tuple[ConversationPacket, tuple[SpecialistInvocation, ...]]:
        validations: list[SpecialistInvocation] = []
        remaining = remaining_expansion_cycles

        while True:
            call_data = self._validation_call_data(
                turn_id=turn_id,
                conversation_id=conversation_id,
                raw_user_prompt=raw_user_prompt,
                frozen_turns=state.frozen(),
                remaining_expansion_cycles=remaining,
            )
            invocation = self.invoker.invoke(mode=MODE_SCOPE_VALIDATION, call_data=call_data)
            validations.append(invocation)
            if type(invocation.output) is not dict:
                raise Recipe0ControllerError("SCOPE_VALIDATION output must be an object")
            try:
                require_valid_scope_validation_output(invocation.output, call_data=call_data)
            except ScopeValidationSemanticError as exc:
                raise Recipe0ControllerError(str(exc)) from exc

            status = invocation.output["status"]
            unresolved_raw = invocation.output["unresolved_references"]
            assert type(status) is str
            assert type(unresolved_raw) is list
            unresolved = tuple(str(item) for item in unresolved_raw)

            if status not in {"NEEDS_MORE_RECENT", "NEEDS_TARGETED_HISTORY"}:
                packet = _freeze_validation_packet(
                    transcript=self.transcript,
                    call_data=call_data,
                    validation_output=invocation.output,
                )
                if consume_continuation:
                    self.transcript.consume_continuation(turn_id=turn_id)
                return packet, tuple(validations)

            if status == "NEEDS_MORE_RECENT":
                delta = self._recent_expansion_delta(
                    conversation_id=conversation_id,
                    state=state,
                )
                if not delta:
                    return (
                        self._freeze_host_terminal(
                            turn_id=turn_id,
                            conversation_id=conversation_id,
                            raw_user_prompt=raw_user_prompt,
                            state=state,
                            status="BOUND_EXHAUSTED",
                            unresolved_references=unresolved,
                            consume_continuation=consume_continuation,
                        ),
                        tuple(validations),
                    )
                candidate = _HistoryState(dict(state.included), set(state.recent_turn_ids))
                candidate.add(delta, recent_scope=True)
            else:
                if self.policy.max_targeted_candidate_turns_per_search == 0:
                    return (
                        self._freeze_host_terminal(
                            turn_id=turn_id,
                            conversation_id=conversation_id,
                            raw_user_prompt=raw_user_prompt,
                            state=state,
                            status="BOUND_EXHAUSTED",
                            unresolved_references=unresolved,
                            consume_continuation=consume_continuation,
                        ),
                        tuple(validations),
                    )
                remaining_slots = PRE1_MAX_RETRIEVED_TURNS - len(state.included)
                if remaining_slots <= 0:
                    return (
                        self._freeze_host_terminal(
                            turn_id=turn_id,
                            conversation_id=conversation_id,
                            raw_user_prompt=raw_user_prompt,
                            state=state,
                            status="BOUND_EXHAUSTED",
                            unresolved_references=unresolved,
                            consume_continuation=consume_continuation,
                        ),
                        tuple(validations),
                    )
                delta, had_hits = self._targeted_exchanges(
                    conversation_id=conversation_id,
                    terms=unresolved,
                    excluded_turn_ids=set(state.included),
                    max_new_turns=remaining_slots,
                )
                if not delta:
                    terminal = "BOUND_EXHAUSTED" if had_hits else "UNRESOLVABLE_WITH_TRANSCRIPT"
                    return (
                        self._freeze_host_terminal(
                            turn_id=turn_id,
                            conversation_id=conversation_id,
                            raw_user_prompt=raw_user_prompt,
                            state=state,
                            status=terminal,
                            unresolved_references=unresolved,
                            consume_continuation=consume_continuation,
                        ),
                        tuple(validations),
                    )
                candidate = _HistoryState(dict(state.included), set(state.recent_turn_ids))
                candidate.add(delta, recent_scope=False)

            if not self._fits_history_bound(candidate.frozen()):
                return (
                    self._freeze_host_terminal(
                        turn_id=turn_id,
                        conversation_id=conversation_id,
                        raw_user_prompt=raw_user_prompt,
                        state=state,
                        status="BOUND_EXHAUSTED",
                        unresolved_references=unresolved,
                        consume_continuation=consume_continuation,
                    ),
                    tuple(validations),
                )

            state.included = candidate.included
            state.recent_turn_ids = candidate.recent_turn_ids
            remaining -= 1

    def run(
        self,
        *,
        turn_id: CanonicalId,
        conversation_id: CanonicalId,
        raw_user_prompt: str,
    ) -> Recipe0Result:
        if type(raw_user_prompt) is not str or not raw_user_prompt.strip():
            raise Recipe0ControllerError("Recipe 0 requires a nonempty raw user prompt")

        continuation = Recipe0ContinuationController(self.transcript)
        continuation_call = continuation.build_open_continuation_validation_call_data(
            turn_id=turn_id,
            conversation_id=conversation_id,
            raw_user_prompt=raw_user_prompt,
            host_policy_limits=self.policy.validation_limits(
                remaining_expansion_cycles=self.policy.max_scope_expansion_cycles
            ),
        )
        if continuation_call is not None:
            frozen = continuation_call["frozen_retrieved_turns"]
            assert type(frozen) is list
            if len(frozen) != 1 or type(frozen[0]) is not dict:
                raise Recipe0ControllerError("continuation prefetch must contain one exact turn")
            source_turn = CanonicalId.parse(str(frozen[0]["turn_uuid"]))
            source_exchange = self.transcript.load_completed_exchange(turn_id=source_turn)
            state = _HistoryState.empty()
            state.add((source_exchange,), recent_scope=True)
            self._require_history_bound(state.frozen())
            packet, validations = self._validate_until_terminal(
                turn_id=turn_id,
                conversation_id=conversation_id,
                raw_user_prompt=raw_user_prompt,
                state=state,
                remaining_expansion_cycles=self.policy.max_scope_expansion_cycles,
                consume_continuation=True,
            )
            return Recipe0Result(packet, None, validations)

        proposal_call = continuation.build_scope_proposal_call_data(
            turn_id=turn_id,
            conversation_id=conversation_id,
            raw_user_prompt=raw_user_prompt,
            host_policy_limits=self.policy.proposal_limits(),
        )
        proposal = self.invoker.invoke(mode=MODE_SCOPE_PROPOSAL, call_data=proposal_call)
        if type(proposal.output) is not dict:
            raise Recipe0ControllerError("SCOPE_PROPOSAL output must be an object")
        try:
            require_valid_scope_proposal_output(proposal.output, call_data=proposal_call)
        except ScopeProposalSemanticError as exc:
            raise Recipe0ControllerError(str(exc)) from exc

        status = proposal.output["status"]
        assert type(status) is str
        if status == "SUFFICIENT_WITHOUT_HISTORY":
            packet = ConversationPacket.freeze(
                turn_id=turn_id,
                conversation_id=conversation_id,
                raw_user_prompt=raw_user_prompt,
                transcript_commit_seq=self.transcript.transcript_commit_seq(),
                included_turns=(),
                unresolved_references=(),
                scope_status=status,
            )
            return Recipe0Result(packet, proposal, ())

        if self.policy.max_scope_expansion_cycles == 0:
            raise Recipe0HistoryBoundExceeded(
                "history was requested but max_scope_expansion_cycles is zero"
            )

        state = _HistoryState.empty()
        if status == "REQUEST_RECENT":
            count = proposal.output["recent_exchange_count"]
            assert type(count) is int
            exchanges = self.transcript.load_recent_exchanges(
                conversation_id=conversation_id,
                limit=count,
            )
            state.add(exchanges, recent_scope=True)
        elif status == "REQUEST_TARGETED":
            if self.policy.max_targeted_candidate_turns_per_search == 0:
                raise Recipe0HistoryBoundExceeded(
                    "targeted history was requested but its host retrieval bound is zero"
                )
            raw_terms = proposal.output["target_terms"]
            assert type(raw_terms) is list
            terms = tuple(str(item) for item in raw_terms)
            exchanges, _ = self._targeted_exchanges(
                conversation_id=conversation_id,
                terms=terms,
            )
            if not exchanges:
                packet = ConversationPacket.freeze(
                    turn_id=turn_id,
                    conversation_id=conversation_id,
                    raw_user_prompt=raw_user_prompt,
                    transcript_commit_seq=self.transcript.transcript_commit_seq(),
                    included_turns=(),
                    unresolved_references=terms,
                    scope_status="UNRESOLVABLE_WITH_TRANSCRIPT",
                )
                return Recipe0Result(packet, proposal, ())
            state.add(exchanges, recent_scope=False)
        else:  # pragma: no cover - proposal schema enum and validator make this unreachable.
            raise Recipe0ControllerError(f"unsupported SCOPE_PROPOSAL status {status}")

        self._require_history_bound(state.frozen())
        packet, validations = self._validate_until_terminal(
            turn_id=turn_id,
            conversation_id=conversation_id,
            raw_user_prompt=raw_user_prompt,
            state=state,
            remaining_expansion_cycles=self.policy.max_scope_expansion_cycles - 1,
            consume_continuation=False,
        )
        return Recipe0Result(packet, proposal, validations)
