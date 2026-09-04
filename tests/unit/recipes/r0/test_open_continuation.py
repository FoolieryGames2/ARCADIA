from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path

from arcadia.core.config import StorageConfig
from arcadia.core.hashing import sha256_text
from arcadia.core.ids import CanonicalId
from arcadia.recipes.r0 import Recipe0ContinuationController
from arcadia.storage.connection import SQLiteConnectionFactory
from arcadia.storage.migrations import MigrationRunner
from arcadia.storage.transcript_repository import ContinuationStatus, TranscriptRepository

NOW = datetime(2026, 9, 4, 12, 0, tzinfo=UTC)


def _setup(tmp_path: Path) -> tuple[TranscriptRepository, CanonicalId]:
    factory = SQLiteConnectionFactory(
        workspace_root=tmp_path,
        storage=StorageConfig(
            data_dir="data",
            database_name="r0.sqlite3",
            busy_timeout_ms=1000,
            require_fts5=True,
        ),
    )
    with factory.connect() as connection:
        MigrationRunner().migrate(connection, applied_at=NOW)
    repository = TranscriptRepository(factory, CanonicalId.new())
    conversation_id = CanonicalId.new()
    repository.create_conversation(conversation_id=conversation_id, created_at=NOW)
    return repository, conversation_id


def _open_continuation(
    repository: TranscriptRepository, conversation_id: CanonicalId
) -> tuple[CanonicalId, CanonicalId]:
    source_turn_id = CanonicalId.new()
    repository.append_user_turn(
        conversation_id=conversation_id,
        turn_id=source_turn_id,
        content="Add a journal entry. What did I learn?",
        created_at=NOW,
    )
    response = "What did you learn?"
    repository.commit_published_response(
        turn_id=source_turn_id,
        result_hash=sha256_text(response),
        exact_published_text=response,
        committed_at=NOW + timedelta(seconds=1),
        completed_turn_requires_user_input=True,
    )
    current_turn_id = CanonicalId.new()
    repository.append_user_turn(
        conversation_id=conversation_id,
        turn_id=current_turn_id,
        content="I learned to keep evidence separate from conclusions.",
        created_at=NOW + timedelta(seconds=2),
    )
    return source_turn_id, current_turn_id


def _validation_call(
    controller: Recipe0ContinuationController,
    *,
    turn_id: CanonicalId,
    conversation_id: CanonicalId,
    prompt: str = "I learned to keep evidence separate from conclusions.",
) -> dict[str, object]:
    call = controller.build_open_continuation_validation_call_data(
        turn_id=turn_id,
        conversation_id=conversation_id,
        raw_user_prompt=prompt,
        host_policy_limits={
            "remaining_expansion_cycles": 2,
            "max_total_injected_history_tokens": 4096,
        },
    )
    assert call is not None
    return call  # type: ignore[return-value]


def _verdict(status: str) -> dict[str, object]:
    return {
        "mode": "SCOPE_VALIDATION",
        "status": status,
        "reason_codes": ["CONTINUATION_RELATION_CHECKED"],
        "unresolved_references": [],
    }


def test_r0_open_continuation_prefetches_exact_prior_exchange(tmp_path: Path) -> None:
    repository, conversation_id = _setup(tmp_path)
    source_turn_id, current_turn_id = _open_continuation(repository, conversation_id)
    controller = Recipe0ContinuationController(repository)

    proposal = controller.build_scope_proposal_call_data(
        turn_id=current_turn_id,
        conversation_id=conversation_id,
        raw_user_prompt="I learned to keep evidence separate from conclusions.",
        host_policy_limits={
            "max_contiguous_lookback_exchanges": 20,
            "max_targeted_candidate_turns_per_search": 8,
            "max_scope_expansion_cycles": 3,
            "max_total_injected_history_tokens": 4096,
        },
    )
    state = proposal["current_transcript_metadata"]["continuation_state"]  # type: ignore[index]
    assert state == {
        "status": "AWAITING_USER_INPUT",
        "source_turn_uuid": str(source_turn_id),
        "reason_code": "USER_INFORMATION_NEEDED",
    }

    call = _validation_call(
        controller,
        turn_id=current_turn_id,
        conversation_id=conversation_id,
    )
    assert len(call["frozen_retrieved_turns"]) == 1  # type: ignore[arg-type]
    assert call["frozen_retrieved_turns"][0]["turn_uuid"] == str(source_turn_id)  # type: ignore[index]


def test_r0_open_continuation_self_contained_payload_keeps_required_frame(
    tmp_path: Path,
) -> None:
    repository, conversation_id = _setup(tmp_path)
    _, current_turn_id = _open_continuation(repository, conversation_id)
    controller = Recipe0ContinuationController(repository)
    call = _validation_call(
        controller,
        turn_id=current_turn_id,
        conversation_id=conversation_id,
        prompt="Evidence and conclusions must stay separate.",
    )
    packet = controller.freeze_open_continuation_packet(
        call_data=call,  # type: ignore[arg-type]
        validation_output=_verdict("SUFFICIENT"),  # type: ignore[arg-type]
    )
    assert len(packet.included_turns) == 1


def test_r0_open_continuation_unrelated_turn_drops_prefetched_history(tmp_path: Path) -> None:
    repository, conversation_id = _setup(tmp_path)
    _, current_turn_id = _open_continuation(repository, conversation_id)
    controller = Recipe0ContinuationController(repository)
    call = _validation_call(
        controller,
        turn_id=current_turn_id,
        conversation_id=conversation_id,
        prompt="What is the current UTC time?",
    )
    packet = controller.freeze_open_continuation_packet(
        call_data=call,  # type: ignore[arg-type]
        validation_output=_verdict("SUFFICIENT_WITHOUT_HISTORY"),  # type: ignore[arg-type]
    )
    assert packet.included_turns == ()


def test_r0_open_continuation_marker_is_one_turn_only(tmp_path: Path) -> None:
    repository, conversation_id = _setup(tmp_path)
    _, current_turn_id = _open_continuation(repository, conversation_id)
    controller = Recipe0ContinuationController(repository)
    call = _validation_call(
        controller,
        turn_id=current_turn_id,
        conversation_id=conversation_id,
    )
    controller.freeze_open_continuation_packet(
        call_data=call,  # type: ignore[arg-type]
        validation_output=_verdict("SUFFICIENT"),  # type: ignore[arg-type]
    )
    assert repository.continuation_state_for_turn(
        turn_id=current_turn_id
    ).status is ContinuationStatus.NONE
    assert controller.build_open_continuation_validation_call_data(
        turn_id=current_turn_id,
        conversation_id=conversation_id,
        raw_user_prompt="I learned to keep evidence separate from conclusions.",
        host_policy_limits={
            "remaining_expansion_cycles": 2,
            "max_total_injected_history_tokens": 4096,
        },
    ) is None


def test_full_journal_edit_elicitation_then_exact_payload(tmp_path: Path) -> None:
    repository, conversation_id = _setup(tmp_path)
    _, current_turn_id = _open_continuation(repository, conversation_id)
    controller = Recipe0ContinuationController(repository)
    exact_payload = "I learned to keep evidence separate from conclusions."
    call = _validation_call(
        controller,
        turn_id=current_turn_id,
        conversation_id=conversation_id,
        prompt=exact_payload,
    )
    packet = controller.freeze_open_continuation_packet(
        call_data=call,  # type: ignore[arg-type]
        validation_output=_verdict("SUFFICIENT"),  # type: ignore[arg-type]
    )
    assert packet.raw_user_prompt == exact_payload
    assert packet.raw_prompt_hash == sha256_text(exact_payload)
    assert packet.included_turns[0]["final_response"] == "What did you learn?"
