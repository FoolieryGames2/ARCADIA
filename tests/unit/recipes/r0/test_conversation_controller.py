from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from arcadia.aa_runtime.invoker import SpecialistInvocation
from arcadia.contracts.aae.registry import MODE_SCOPE_PROPOSAL, MODE_SCOPE_VALIDATION
from arcadia.core.canonical_json import JsonValue
from arcadia.core.config import StorageConfig
from arcadia.core.hashing import sha256_text
from arcadia.core.ids import CanonicalId
from arcadia.recipes.r0.controller import (
    Recipe0ConversationController,
    Recipe0HistoryBoundExceeded,
    Recipe0Policy,
)
from arcadia.storage.connection import SQLiteConnectionFactory
from arcadia.storage.migrations import MigrationRunner
from arcadia.storage.transcript_repository import CompletedExchange, TranscriptRepository

NOW = datetime(2026, 9, 4, 14, 0, tzinfo=UTC)


def _repository(root: Path) -> TranscriptRepository:
    factory = SQLiteConnectionFactory(
        workspace_root=root,
        storage=StorageConfig(
            data_dir="data",
            database_name="r0-controller.sqlite3",
            busy_timeout_ms=1000,
            require_fts5=True,
        ),
    )
    with factory.connect() as connection:
        MigrationRunner().migrate(connection, applied_at=NOW)
    return TranscriptRepository(factory, CanonicalId.new())


def _conversation(repository: TranscriptRepository) -> CanonicalId:
    conversation_id = CanonicalId.new()
    repository.create_conversation(conversation_id=conversation_id, created_at=NOW)
    return conversation_id


def _complete(
    repository: TranscriptRepository,
    conversation_id: CanonicalId,
    *,
    user: str,
    assistant: str,
    offset: int,
    requires_input: bool = False,
) -> CompletedExchange:
    turn_id = CanonicalId.new()
    at = NOW + timedelta(minutes=offset)
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
        completed_turn_requires_user_input=requires_input,
    )


def _start_current(
    repository: TranscriptRepository,
    conversation_id: CanonicalId,
    prompt: str,
    *,
    offset: int = 30,
) -> CanonicalId:
    turn_id = CanonicalId.new()
    repository.append_user_turn(
        conversation_id=conversation_id,
        turn_id=turn_id,
        content=prompt,
        created_at=NOW + timedelta(minutes=offset),
    )
    return turn_id


def _proposal(
    status: str,
    *,
    recent: int = 0,
    targets: list[JsonValue] | None = None,
) -> dict[str, JsonValue]:
    return {
        "mode": MODE_SCOPE_PROPOSAL,
        "status": status,
        "recent_exchange_count": recent,
        "target_terms": [] if targets is None else targets,
        "reason_codes": ["TEST_SCOPE_DECISION"],
    }


def _validation(
    status: str,
    *,
    unresolved: list[JsonValue] | None = None,
) -> dict[str, JsonValue]:
    return {
        "mode": MODE_SCOPE_VALIDATION,
        "status": status,
        "reason_codes": ["TEST_VALIDATION_DECISION"],
        "unresolved_references": [] if unresolved is None else unresolved,
    }


@dataclass(slots=True)
class QueueInvoker:
    outputs: list[dict[str, JsonValue]]
    calls: list[tuple[str, JsonValue]] = field(default_factory=list)

    def invoke(self, *, mode: str, call_data: JsonValue) -> SpecialistInvocation:
        self.calls.append((mode, call_data))
        if not self.outputs:
            raise AssertionError("unexpected specialist invocation")
        output = self.outputs.pop(0)
        return SpecialistInvocation(
            attempt_id=CanonicalId.new(),
            mode=mode,
            call_data=call_data,
            output=output,
        )


def _tokens(turns: tuple[dict[str, JsonValue], ...]) -> int:
    total = 0
    for turn in turns:
        total += len(str(turn["user_message"])) + len(str(turn["final_response"]))
    return total


def _controller(
    repository: TranscriptRepository,
    invoker: QueueInvoker,
    *,
    max_history_tokens: int = 10_000,
    max_recent: int = 20,
    max_targeted: int = 8,
    max_cycles: int = 3,
) -> Recipe0ConversationController:
    return Recipe0ConversationController(
        transcript=repository,
        invoker=invoker,
        history_token_counter=_tokens,
        policy=Recipe0Policy(
            max_contiguous_lookback_exchanges=max_recent,
            max_targeted_candidate_turns_per_search=max_targeted,
            max_scope_expansion_cycles=max_cycles,
            max_total_injected_history_tokens=max_history_tokens,
        ),
    )


def test_zero_history_freezes_without_validation(tmp_path: Path) -> None:
    repository = _repository(tmp_path)
    conversation_id = _conversation(repository)
    prompt = "Explain the current task."
    turn_id = _start_current(repository, conversation_id, prompt)
    invoker = QueueInvoker([_proposal("SUFFICIENT_WITHOUT_HISTORY")])

    result = _controller(repository, invoker).run(
        turn_id=turn_id,
        conversation_id=conversation_id,
        raw_user_prompt=prompt,
    )

    assert result.packet.scope_status == "SUFFICIENT_WITHOUT_HISTORY"
    assert result.packet.included_turns == ()
    assert result.validation_invocation is None


def test_zero_available_history_request_continues_with_typed_unresolvable_packet(
    tmp_path: Path,
) -> None:
    repository = _repository(tmp_path)
    conversation_id = _conversation(repository)
    prompt = "Repeat what I said before."
    turn_id = _start_current(repository, conversation_id, prompt)
    invoker = QueueInvoker(
        [_proposal("REQUEST_TARGETED", targets=["what I said before"])]
    )

    result = _controller(repository, invoker).run(
        turn_id=turn_id,
        conversation_id=conversation_id,
        raw_user_prompt=prompt,
    )

    assert result.packet.scope_status == "UNRESOLVABLE_WITH_TRANSCRIPT"
    assert result.packet.included_turns == ()
    assert result.packet.unresolved_references == ("what I said before",)
    assert result.validation_invocations == ()
    assert result.proposal_invocation is not None
    assert result.proposal_invocation.host_corrections[0].code == (
        "R0_NO_COMPLETED_HISTORY_AVAILABLE"
    )
    assert [mode for mode, _ in invoker.calls] == [MODE_SCOPE_PROPOSAL]
    call = invoker.calls[0][1]
    assert type(call) is dict
    metadata = call["current_transcript_metadata"]
    assert type(metadata) is dict
    assert metadata["completed_exchange_count"] == 0


def test_recent_history_retrieves_exact_requested_exchange(tmp_path: Path) -> None:
    repository = _repository(tmp_path)
    conversation_id = _conversation(repository)
    _complete(
        repository,
        conversation_id,
        user="First question.",
        assistant="First answer.",
        offset=0,
    )
    latest = _complete(
        repository,
        conversation_id,
        user="Give me the exact status line.",
        assistant="Arcadia is ready for the next build.",
        offset=1,
    )
    prompt = "Say that exact line again."
    turn_id = _start_current(repository, conversation_id, prompt)
    invoker = QueueInvoker(
        [_proposal("REQUEST_RECENT", recent=1), _validation("SUFFICIENT")]
    )

    result = _controller(repository, invoker).run(
        turn_id=turn_id,
        conversation_id=conversation_id,
        raw_user_prompt=prompt,
    )

    assert result.packet.scope_status == "SUFFICIENT"
    assert len(result.packet.included_turns) == 1
    frozen = result.packet.included_turns[0]
    assert frozen["turn_uuid"] == str(latest.turn.turn_id)
    assert frozen["final_response"] == "Arcadia is ready for the next build."
    assert frozen["final_response_hash"] == latest.assistant_entry.content_hash.value
    assert [mode for mode, _ in invoker.calls] == [
        MODE_SCOPE_PROPOSAL,
        MODE_SCOPE_VALIDATION,
    ]


def test_targeted_history_uses_fts_and_freezes_exact_exchange(tmp_path: Path) -> None:
    repository = _repository(tmp_path)
    conversation_id = _conversation(repository)
    target = _complete(
        repository,
        conversation_id,
        user="We discussed black holes and the visualization yesterday.",
        assistant="Keep the accretion disk physically plausible.",
        offset=0,
    )
    _complete(
        repository,
        conversation_id,
        user="Unrelated note about groceries.",
        assistant="Milk and bananas.",
        offset=1,
    )
    prompt = "What did we decide about black holes?"
    turn_id = _start_current(repository, conversation_id, prompt)
    invoker = QueueInvoker(
        [
            _proposal("REQUEST_TARGETED", targets=["black holes"]),
            _validation("SUFFICIENT"),
        ]
    )

    result = _controller(repository, invoker).run(
        turn_id=turn_id,
        conversation_id=conversation_id,
        raw_user_prompt=prompt,
    )

    assert len(result.packet.included_turns) == 1
    assert result.packet.included_turns[0]["turn_uuid"] == str(target.turn.turn_id)


def test_targeted_history_with_no_hits_freezes_explicit_unresolved_state(tmp_path: Path) -> None:
    repository = _repository(tmp_path)
    conversation_id = _conversation(repository)
    _complete(
        repository,
        conversation_id,
        user="Only gardening was discussed.",
        assistant="Water the seedlings.",
        offset=0,
    )
    prompt = "What did we decide about neutron stars?"
    turn_id = _start_current(repository, conversation_id, prompt)
    invoker = QueueInvoker(
        [_proposal("REQUEST_TARGETED", targets=["neutron stars"])]
    )

    result = _controller(repository, invoker).run(
        turn_id=turn_id,
        conversation_id=conversation_id,
        raw_user_prompt=prompt,
    )

    assert result.packet.scope_status == "UNRESOLVABLE_WITH_TRANSCRIPT"
    assert result.packet.included_turns == ()
    assert result.packet.unresolved_references == ("neutron stars",)
    assert result.validation_invocation is None


def test_open_continuation_prefetches_exact_prior_exchange_and_consumes_marker(
    tmp_path: Path,
) -> None:
    repository = _repository(tmp_path)
    conversation_id = _conversation(repository)
    prior = _complete(
        repository,
        conversation_id,
        user="I want to edit my journal.",
        assistant="What would you like to add?",
        offset=0,
        requires_input=True,
    )
    prompt = "I dreamed of pink elephants again last night."
    turn_id = _start_current(repository, conversation_id, prompt)
    invoker = QueueInvoker([_validation("SUFFICIENT")])

    result = _controller(repository, invoker).run(
        turn_id=turn_id,
        conversation_id=conversation_id,
        raw_user_prompt=prompt,
    )

    assert result.proposal_invocation is None
    assert len(result.packet.included_turns) == 1
    assert result.packet.included_turns[0]["turn_uuid"] == str(prior.turn.turn_id)
    assert repository.continuation_state_for_turn(turn_id=turn_id).status.value == "NONE"
    assert [mode for mode, _ in invoker.calls] == [MODE_SCOPE_VALIDATION]


def test_open_continuation_can_drop_unrelated_prefetch(tmp_path: Path) -> None:
    repository = _repository(tmp_path)
    conversation_id = _conversation(repository)
    _complete(
        repository,
        conversation_id,
        user="Which file should I edit?",
        assistant="Tell me the filename.",
        offset=0,
        requires_input=True,
    )
    prompt = "Actually, what is a neutron star?"
    turn_id = _start_current(repository, conversation_id, prompt)
    invoker = QueueInvoker([_validation("SUFFICIENT_WITHOUT_HISTORY")])

    result = _controller(repository, invoker).run(
        turn_id=turn_id,
        conversation_id=conversation_id,
        raw_user_prompt=prompt,
    )

    assert result.packet.scope_status == "SUFFICIENT_WITHOUT_HISTORY"
    assert result.packet.included_turns == ()
    assert repository.continuation_state_for_turn(turn_id=turn_id).status.value == "NONE"


def test_needs_more_recent_adds_only_older_delta_then_revalidates(tmp_path: Path) -> None:
    repository = _repository(tmp_path)
    conversation_id = _conversation(repository)
    first = _complete(
        repository,
        conversation_id,
        user="Oldest detail.",
        assistant="Oldest response.",
        offset=0,
    )
    second = _complete(
        repository,
        conversation_id,
        user="Middle detail.",
        assistant="Middle response.",
        offset=1,
    )
    latest = _complete(
        repository,
        conversation_id,
        user="Latest detail.",
        assistant="Latest response.",
        offset=2,
    )
    prompt = "What about the thing before that?"
    turn_id = _start_current(repository, conversation_id, prompt)
    invoker = QueueInvoker(
        [
            _proposal("REQUEST_RECENT", recent=1),
            _validation("NEEDS_MORE_RECENT", unresolved=["the thing before that"]),
            _validation("SUFFICIENT"),
        ]
    )

    result = _controller(repository, invoker, max_recent=3).run(
        turn_id=turn_id,
        conversation_id=conversation_id,
        raw_user_prompt=prompt,
    )

    assert result.packet.scope_status == "SUFFICIENT"
    assert [turn["turn_uuid"] for turn in result.packet.included_turns] == [
        str(first.turn.turn_id),
        str(second.turn.turn_id),
        str(latest.turn.turn_id),
    ]
    assert len(result.validation_invocations) == 2
    first_validation = invoker.calls[1][1]
    second_validation = invoker.calls[2][1]
    assert type(first_validation) is dict
    assert type(second_validation) is dict
    assert len(first_validation["frozen_retrieved_turns"]) == 1
    assert len(second_validation["frozen_retrieved_turns"]) == 3
    first_limits = first_validation["host_policy_limits"]
    second_limits = second_validation["host_policy_limits"]
    assert type(first_limits) is dict
    assert type(second_limits) is dict
    assert first_limits["remaining_expansion_cycles"] == 2
    assert second_limits["remaining_expansion_cycles"] == 1


def test_needs_more_recent_at_end_of_transcript_freezes_bound_exhausted(
    tmp_path: Path,
) -> None:
    repository = _repository(tmp_path)
    conversation_id = _conversation(repository)
    only = _complete(
        repository,
        conversation_id,
        user="Only prior detail.",
        assistant="Only prior response.",
        offset=0,
    )
    prompt = "What about the thing before that?"
    turn_id = _start_current(repository, conversation_id, prompt)
    invoker = QueueInvoker(
        [
            _proposal("REQUEST_RECENT", recent=1),
            _validation("NEEDS_MORE_RECENT", unresolved=["the thing before that"]),
        ]
    )

    result = _controller(repository, invoker).run(
        turn_id=turn_id,
        conversation_id=conversation_id,
        raw_user_prompt=prompt,
    )

    assert result.packet.scope_status == "BOUND_EXHAUSTED"
    assert result.packet.unresolved_references == ("the thing before that",)
    assert [turn["turn_uuid"] for turn in result.packet.included_turns] == [
        str(only.turn.turn_id)
    ]
    assert len(result.validation_invocations) == 1


def test_needs_targeted_history_adds_fts_delta_then_revalidates(tmp_path: Path) -> None:
    repository = _repository(tmp_path)
    conversation_id = _conversation(repository)
    target = _complete(
        repository,
        conversation_id,
        user="We decided the black holes view needs lensing.",
        assistant="Keep the lensing physically plausible.",
        offset=0,
    )
    latest = _complete(
        repository,
        conversation_id,
        user="Unrelated groceries.",
        assistant="Milk and bananas.",
        offset=1,
    )
    prompt = "What did we decide about black holes?"
    turn_id = _start_current(repository, conversation_id, prompt)
    invoker = QueueInvoker(
        [
            _proposal("REQUEST_RECENT", recent=1),
            _validation("NEEDS_TARGETED_HISTORY", unresolved=["black holes"]),
            _validation("SUFFICIENT"),
        ]
    )

    result = _controller(repository, invoker).run(
        turn_id=turn_id,
        conversation_id=conversation_id,
        raw_user_prompt=prompt,
    )

    assert result.packet.scope_status == "SUFFICIENT"
    assert [turn["turn_uuid"] for turn in result.packet.included_turns] == [
        str(target.turn.turn_id),
        str(latest.turn.turn_id),
    ]
    assert len(result.validation_invocations) == 2


def test_needs_targeted_history_with_no_fts_hit_freezes_unresolvable(tmp_path: Path) -> None:
    repository = _repository(tmp_path)
    conversation_id = _conversation(repository)
    latest = _complete(
        repository,
        conversation_id,
        user="Only gardening was discussed.",
        assistant="Water the seedlings.",
        offset=0,
    )
    prompt = "What did we decide about neutron stars?"
    turn_id = _start_current(repository, conversation_id, prompt)
    invoker = QueueInvoker(
        [
            _proposal("REQUEST_RECENT", recent=1),
            _validation("NEEDS_TARGETED_HISTORY", unresolved=["neutron stars"]),
        ]
    )

    result = _controller(repository, invoker).run(
        turn_id=turn_id,
        conversation_id=conversation_id,
        raw_user_prompt=prompt,
    )

    assert result.packet.scope_status == "UNRESOLVABLE_WITH_TRANSCRIPT"
    assert result.packet.unresolved_references == ("neutron stars",)
    assert [turn["turn_uuid"] for turn in result.packet.included_turns] == [
        str(latest.turn.turn_id)
    ]


def test_targeted_expansion_that_only_rediscovers_included_turn_is_bound_exhausted(
    tmp_path: Path,
) -> None:
    repository = _repository(tmp_path)
    conversation_id = _conversation(repository)
    target = _complete(
        repository,
        conversation_id,
        user="We discussed black holes yesterday.",
        assistant="Use a compact lensing example.",
        offset=0,
    )
    prompt = "What else did we decide about black holes?"
    turn_id = _start_current(repository, conversation_id, prompt)
    invoker = QueueInvoker(
        [
            _proposal("REQUEST_TARGETED", targets=["black holes"]),
            _validation("NEEDS_TARGETED_HISTORY", unresolved=["black holes"]),
        ]
    )

    result = _controller(repository, invoker).run(
        turn_id=turn_id,
        conversation_id=conversation_id,
        raw_user_prompt=prompt,
    )

    assert result.packet.scope_status == "BOUND_EXHAUSTED"
    assert [turn["turn_uuid"] for turn in result.packet.included_turns] == [
        str(target.turn.turn_id)
    ]


def test_expansion_that_would_cross_history_token_budget_freezes_bound_exhausted(
    tmp_path: Path,
) -> None:
    repository = _repository(tmp_path)
    conversation_id = _conversation(repository)
    _complete(
        repository,
        conversation_id,
        user="This older message is intentionally very long.",
        assistant="This older answer is intentionally very long too.",
        offset=0,
    )
    latest = _complete(
        repository,
        conversation_id,
        user="A",
        assistant="B",
        offset=1,
    )
    prompt = "What about before that?"
    turn_id = _start_current(repository, conversation_id, prompt)
    invoker = QueueInvoker(
        [
            _proposal("REQUEST_RECENT", recent=1),
            _validation("NEEDS_MORE_RECENT", unresolved=["before that"]),
        ]
    )

    result = _controller(repository, invoker, max_history_tokens=10).run(
        turn_id=turn_id,
        conversation_id=conversation_id,
        raw_user_prompt=prompt,
    )

    assert result.packet.scope_status == "BOUND_EXHAUSTED"
    assert [turn["turn_uuid"] for turn in result.packet.included_turns] == [
        str(latest.turn.turn_id)
    ]


def test_open_continuation_can_expand_recent_scope_before_freeze(tmp_path: Path) -> None:
    repository = _repository(tmp_path)
    conversation_id = _conversation(repository)
    older = _complete(
        repository,
        conversation_id,
        user="Earlier we discussed the blue version.",
        assistant="The blue version was preferred.",
        offset=0,
    )
    prior = _complete(
        repository,
        conversation_id,
        user="Which version should I write down?",
        assistant="Which earlier version do you mean?",
        offset=1,
        requires_input=True,
    )
    prompt = "The one before that."
    turn_id = _start_current(repository, conversation_id, prompt)
    invoker = QueueInvoker(
        [
            _validation("NEEDS_MORE_RECENT", unresolved=["the one before that"]),
            _validation("SUFFICIENT"),
        ]
    )

    result = _controller(repository, invoker, max_recent=2).run(
        turn_id=turn_id,
        conversation_id=conversation_id,
        raw_user_prompt=prompt,
    )

    assert result.proposal_invocation is None
    assert result.packet.scope_status == "SUFFICIENT"
    assert [turn["turn_uuid"] for turn in result.packet.included_turns] == [
        str(older.turn.turn_id),
        str(prior.turn.turn_id),
    ]
    assert repository.continuation_state_for_turn(turn_id=turn_id).status.value == "NONE"
    assert len(result.validation_invocations) == 2


def test_injected_history_token_bound_fails_closed(tmp_path: Path) -> None:
    repository = _repository(tmp_path)
    conversation_id = _conversation(repository)
    _complete(
        repository,
        conversation_id,
        user="A long enough prior message.",
        assistant="A long enough prior answer.",
        offset=0,
    )
    prompt = "Repeat that."
    turn_id = _start_current(repository, conversation_id, prompt)
    invoker = QueueInvoker([_proposal("REQUEST_RECENT", recent=1)])

    with pytest.raises(Recipe0HistoryBoundExceeded, match="exceeds"):
        _controller(repository, invoker, max_history_tokens=1).run(
            turn_id=turn_id,
            conversation_id=conversation_id,
            raw_user_prompt=prompt,
        )
