from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path

from arcadia.core.canonical_json import JsonValue
from arcadia.core.config import StorageConfig
from arcadia.core.hashing import sha256_text
from arcadia.core.ids import CanonicalId
from arcadia.core.work_budget import WorkBudgetLedger
from arcadia.lab.base_only_invoker import ActivationReceipt, QualificationInvocation
from arcadia.lab.recipe_harness import run_recipe0_base_only
from arcadia.storage.connection import SQLiteConnectionFactory
from arcadia.storage.migrations import MigrationRunner
from arcadia.storage.transcript_repository import TranscriptRepository

NOW = datetime(2026, 9, 4, 20, 0, tzinfo=UTC)


class FakeRuntime:
    def count_tokens(self, _messages: object) -> int:
        return 12


class QueueBaseInvoker:
    def __init__(self, outputs: list[JsonValue]) -> None:
        self.outputs = list(outputs)
        self.runtime = FakeRuntime()
        self.incoming_model_calls: list[int] = []

    def invoke(
        self,
        *,
        specialist_mode_id: str,
        call_data: JsonValue,
        budget: WorkBudgetLedger,
    ) -> QualificationInvocation:
        self.incoming_model_calls.append(budget.usage.model_calls)
        call_id = CanonicalId.new()
        authorized, _ = budget.authorize_model_attempt(
            call_id=call_id,
            input_tokens=100,
            reserved_output_tokens=32,
            expected_head=budget.head_hash,
        )
        digest = sha256_text(f"{specialist_mode_id}:{call_id}")
        return QualificationInvocation(
            output=self.outputs.pop(0),
            receipt=ActivationReceipt(
                call_id=call_id,
                specialist_mode_id=specialist_mode_id,
                physical_adapter_id="BASE_MODEL",
                binding_kind="BASE_ONLY",
                adapter_lease_id=None,
                authority_tier="T0",
                runtime_manifest_id="test-runtime",
                model_sha256="a" * 64,
                llama_commit="test-commit",
                input_schema_hash=digest,
                call_data_hash=digest,
                output_schema_hash=digest,
                output_hash=digest,
                input_tokens=100,
                output_tokens=32,
                elapsed_seconds=0.01,
                fresh_context=True,
                fresh_sampler=True,
            ),
            budget=authorized,
        )


def _repository(root: Path) -> TranscriptRepository:
    factory = SQLiteConnectionFactory(
        workspace_root=root,
        storage=StorageConfig(
            data_dir="data",
            database_name="arcadia.sqlite3",
            busy_timeout_ms=1000,
            require_fts5=True,
        ),
    )
    with factory.connect() as connection:
        MigrationRunner().migrate(connection, applied_at=NOW)
    return TranscriptRepository(factory, CanonicalId.new())


def _complete(
    repository: TranscriptRepository,
    conversation_id: CanonicalId,
    *,
    user: str,
    assistant: str,
) -> CanonicalId:
    turn_id = CanonicalId.new()
    repository.append_user_turn(
        conversation_id=conversation_id,
        turn_id=turn_id,
        content=user,
        created_at=NOW,
    )
    repository.commit_published_response(
        turn_id=turn_id,
        result_hash=sha256_text(assistant),
        exact_published_text=assistant,
        committed_at=NOW + timedelta(seconds=1),
    )
    return turn_id


def test_harness_uses_real_transcript_and_leaves_current_turn_open(tmp_path: Path) -> None:
    repository = _repository(tmp_path)
    invoker = QueueBaseInvoker(
        [
            {
                "mode": "SCOPE_PROPOSAL",
                "status": "SUFFICIENT_WITHOUT_HISTORY",
                "recent_exchange_count": 0,
                "target_terms": [],
                "reason_codes": ["SELF_CONTAINED"],
            }
        ]
    )

    result = run_recipe0_base_only(
        "Hello Arcadia",
        invoker=invoker,  # type: ignore[arg-type]
        transcript=repository,
    )

    assert result.completed_recipes == ("R0",)
    assert result.next_recipe == "R1"
    assert result.next_standing == "NOT_IMPLEMENTED"
    assert result.conversation_packet.raw_user_prompt == "Hello Arcadia"
    assert repository.completed_exchange_count(
        conversation_id=result.conversation_packet.conversation_id
    ) == 0
    assert result.budget.usage.model_calls == 1
    assert len(result.activation_receipts) == 1
    assert invoker.incoming_model_calls == [0]


def test_harness_carries_one_budget_across_proposal_and_validation(tmp_path: Path) -> None:
    repository = _repository(tmp_path)
    conversation_id = CanonicalId.new()
    repository.create_conversation(conversation_id=conversation_id, created_at=NOW)
    prior_turn = _complete(
        repository,
        conversation_id,
        user="The launch word is amber.",
        assistant="Recorded: amber.",
    )
    invoker = QueueBaseInvoker(
        [
            {
                "mode": "SCOPE_PROPOSAL",
                "status": "REQUEST_RECENT",
                "recent_exchange_count": 1,
                "target_terms": [],
                "reason_codes": ["RECENT_REFERENCE"],
            },
            {
                "mode": "SCOPE_VALIDATION",
                "status": "SUFFICIENT",
                "reason_codes": ["REFERENCE_RESOLVED"],
                "unresolved_references": [],
            },
        ]
    )

    result = run_recipe0_base_only(
        "What was that launch word?",
        invoker=invoker,  # type: ignore[arg-type]
        transcript=repository,
        conversation_id=conversation_id,
    )

    assert invoker.incoming_model_calls == [0, 1]
    assert result.budget.usage.model_calls == 2
    assert len(result.activation_receipts) == 2
    assert len(result.r0_result.validation_invocations) == 1
    assert [turn["turn_uuid"] for turn in result.conversation_packet.included_turns] == [
        str(prior_turn)
    ]
