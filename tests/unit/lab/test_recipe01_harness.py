from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from arcadia.contracts.aae.registry import (
    MODE_HOWARD_INTENT_COMMENT,
    MODE_INTENT_ORGANIZER,
    MODE_PROMPT_ANALYSIS,
    MODE_SCOPE_PROPOSAL,
    MODE_SPELL,
    MODE_TERM_MEANING,
)
from arcadia.core.canonical_json import JsonValue
from arcadia.core.config import StorageConfig
from arcadia.core.hashing import sha256_text
from arcadia.core.ids import CanonicalId
from arcadia.core.work_budget import WorkBudgetLedger
from arcadia.lab.base_only_invoker import ActivationReceipt, QualificationInvocation
from arcadia.lab.recipe_harness import run_recipe01_base_only
from arcadia.storage.connection import SQLiteConnectionFactory
from arcadia.storage.migrations import MigrationRunner
from arcadia.storage.transcript_repository import TranscriptRepository

NOW = datetime(2026, 9, 6, 4, 0, tzinfo=UTC)
PROMPT = "Fix my projet. Then save it."


class FakeRuntime:
    def count_tokens(self, _messages: object) -> int:
        return 12


class QueueBaseInvoker:
    def __init__(self, outputs: list[JsonValue]) -> None:
        self.outputs = list(outputs)
        self.runtime = FakeRuntime()
        self.incoming_model_calls: list[int] = []
        self.modes: list[str] = []

    def invoke(
        self,
        *,
        specialist_mode_id: str,
        call_data: JsonValue,
        budget: WorkBudgetLedger,
    ) -> QualificationInvocation:
        self.incoming_model_calls.append(budget.usage.model_calls)
        self.modes.append(specialist_mode_id)
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


def _capabilities() -> tuple[dict[str, JsonValue], ...]:
    return (
        {"capability_id": "project_edit", "capability_class": "PROJECT", "available": True},
        {"capability_id": "project_save", "capability_class": "PROJECT", "available": True},
    )


def _outputs(*, include_comment: bool = True) -> list[JsonValue]:
    values: list[JsonValue] = [
        {
            "mode": MODE_SCOPE_PROPOSAL,
            "status": "SUFFICIENT_WITHOUT_HISTORY",
            "recent_exchange_count": 0,
            "target_terms": [],
            "reason_codes": ["SELF_CONTAINED"],
        },
        {
            "mode": MODE_SPELL,
            "raw_prompt": PROMPT,
            "normalized_prompt": "Fix my project. Then save it.",
            "spell_edits": [
                {"start": 7, "end": 13, "source": "projet", "replacement": "project"}
            ],
            "uncertain_corrections": [],
        },
        {
            "mode": MODE_TERM_MEANING,
            "terms": [
                {
                    "term_key": "TERM_1",
                    "source_ref": "S001",
                    "surface": "projet",
                    "type_guess": "PROJECT",
                    "current_use_guess": "The user refers to a project target.",
                    "meaning_status": "provisional",
                    "context_lookup_needed": True,
                    "confidence": 0.6,
                }
            ],
            "unresolved_references": [],
        },
        {
            "mode": MODE_PROMPT_ANALYSIS,
            "topics": [{"text": "project work", "source_refs": ["S001"]}],
            "goals": [
                {"text": "project work", "source_refs": ["S001"]},
                {"text": "save result", "source_refs": ["S002"]},
            ],
            "tasks": [
                {"text": "project work", "source_refs": ["S001"]},
                {"text": "save result", "source_refs": ["S002"]},
            ],
            "statements": [],
            "questions": [],
            "directions": [
                {"text": "project work", "source_refs": ["S001"]},
                {"text": "save result", "source_refs": ["S002"]},
            ],
            "approvals": [],
            "interaction_mode": "ordering_or_directive",
            "important_claims": [],
            "unresolved_items": [],
            "control_signals": [],
        },
        {
            "mode": MODE_INTENT_ORGANIZER,
            "primary_intent": "Edit the referenced project and save the result.",
            "secondary_intents": [],
            "requirements": [
                {
                    "requirement_key": "REQ_1",
                    "requested_outcome": "Fix the referenced project.",
                    "constraints": [],
                    "source_refs": ["S001"],
                    "depends_on": [],
                    "group": "PROJECT_WORK",
                    "priority": 100,
                    "context_needs": ["Resolve the referenced project target."],
                    "capability_candidates": ["project_edit"],
                    "memory_candidates": [],
                },
                {
                    "requirement_key": "REQ_2",
                    "requested_outcome": "Save the resulting project state.",
                    "constraints": [],
                    "source_refs": ["S002"],
                    "depends_on": ["REQ_1"],
                    "group": "PROJECT_WORK",
                    "priority": 90,
                    "context_needs": [],
                    "capability_candidates": ["project_save"],
                    "memory_candidates": [],
                },
            ],
            "clarification_required": False,
            "context_resolution_first": True,
            "unresolved_blockers": ["Project target must be grounded by Context."],
            "control_signals": [],
        },
    ]
    if include_comment:
        values.append(
            {
                "mode": MODE_HOWARD_INTENT_COMMENT,
                "comment": "I understand: fix the referenced project first, then save the result.",
            }
        )
    return values


def test_r0_r1_harness_carries_one_budget_and_stops_at_r2(tmp_path: Path) -> None:
    repository = _repository(tmp_path)
    invoker = QueueBaseInvoker(_outputs())

    result = run_recipe01_base_only(
        PROMPT,
        invoker=invoker,  # type: ignore[arg-type]
        transcript=repository,
        capability_availability=_capabilities(),
    )

    assert result.completed_recipes == ("R0", "R1")
    assert result.next_recipe == "R2"
    assert result.next_standing == "NOT_IMPLEMENTED"
    assert invoker.modes == [
        MODE_SCOPE_PROPOSAL,
        MODE_SPELL,
        MODE_TERM_MEANING,
        MODE_PROMPT_ANALYSIS,
        MODE_INTENT_ORGANIZER,
        MODE_HOWARD_INTENT_COMMENT,
    ]
    assert invoker.incoming_model_calls == [0, 1, 2, 3, 4, 5]
    assert result.budget.usage.model_calls == 6
    assert len(result.r0_activation_receipts) == 1
    assert len(result.r1_activation_receipts) == 5
    assert result.r1_result.artifact.normalized_prompt == "Fix my project. Then save it."
    assert [item["requirement_ref"] for item in result.r1_result.artifact.requirements] == [
        "R001",
        "R002",
    ]
    assert result.r1_result.artifact.conversation_packet_hash == result.conversation_packet.packet_hash
    assert repository.completed_exchange_count(
        conversation_id=result.conversation_packet.conversation_id
    ) == 0


def test_zero_history_request_logs_correction_and_continues_into_r1(
    tmp_path: Path,
) -> None:
    repository = _repository(tmp_path)
    outputs = _outputs()
    outputs[0] = {
        "mode": MODE_SCOPE_PROPOSAL,
        "status": "REQUEST_RECENT",
        "recent_exchange_count": 0,
        "target_terms": ["what did i say before"],
        "reason_codes": ["RECENT_EXCHANGE_MISSING"],
    }
    invoker = QueueBaseInvoker(outputs)

    result = run_recipe01_base_only(
        PROMPT,
        invoker=invoker,  # type: ignore[arg-type]
        transcript=repository,
        capability_availability=_capabilities(),
    )

    assert result.completed_recipes == ("R0", "R1")
    assert result.conversation_packet.scope_status == "UNRESOLVABLE_WITH_TRANSCRIPT"
    assert result.conversation_packet.unresolved_references == ("what did i say before",)
    assert result.r0_result.proposal_invocation is not None
    assert result.r0_result.proposal_invocation.host_corrections[0].code == (
        "R0_NO_COMPLETED_HISTORY_AVAILABLE"
    )
    assert invoker.modes[1] == MODE_SPELL


def test_r0_r1_harness_can_skip_non_authoritative_intent_comment(tmp_path: Path) -> None:
    repository = _repository(tmp_path)
    invoker = QueueBaseInvoker(_outputs(include_comment=False))

    result = run_recipe01_base_only(
        PROMPT,
        invoker=invoker,  # type: ignore[arg-type]
        transcript=repository,
        capability_availability=_capabilities(),
        include_intent_comment=False,
    )

    assert result.r1_result.intent_comment is None
    assert len(result.r1_activation_receipts) == 4
    assert result.budget.usage.model_calls == 5
    assert invoker.incoming_model_calls == [0, 1, 2, 3, 4]


def test_r0_r1_harness_runs_through_actual_base_only_invoker_boundary(tmp_path: Path) -> None:
    from types import SimpleNamespace

    from arcadia.core.canonical_json import canonical_json_dumps
    from arcadia.lab.base_only_invoker import BaseOnlySpecialistInvoker
    from arcadia.lab.config import LabSettings, RuntimeIdentity

    class StructuredFakeRuntime:
        def __init__(self, outputs: list[JsonValue]) -> None:
            self.outputs = list(outputs)
            self.calls = 0

        def count_tokens(self, _messages: object) -> int:
            return 100

        def complete(self, _messages: object, **_: object) -> object:
            self.calls += 1
            return SimpleNamespace(
                text=canonical_json_dumps(self.outputs.pop(0)),
                completion_tokens=32,
                elapsed_seconds=0.01,
            )

    runtime = StructuredFakeRuntime(_outputs())
    if "entry_mode" in LabSettings.__dataclass_fields__:
        settings = LabSettings(
            entry_mode="recipe",
            runtime_transport="resident",
            context_tokens=2048,
            max_output_tokens=128,
            temperature=0.0,
            seed=42,
            gpu_layers=99,
            server_port=18080,
            system_prompt="T0 test",
        )
    else:  # compatibility with the older local reconstruction used by this package test
        settings = LabSettings(2048, 128, 0.0, 42, 99, "T0 test")
    identity = RuntimeIdentity(
        "runtime-manifest",
        "CANDIDATE",
        "T0",
        Path("model"),
        1,
        "a" * 64,
        Path("runtime"),
        1,
        "b" * 64,
        "commit",
        Path("cuda"),
    )

    result = run_recipe01_base_only(
        PROMPT,
        invoker=BaseOnlySpecialistInvoker(runtime, identity, settings),
        transcript=_repository(tmp_path),
        capability_availability=_capabilities(),
    )

    assert runtime.calls == 6
    assert result.budget.usage.model_calls == 6
    assert [receipt.specialist_mode_id for receipt in result.activation_receipts] == [
        MODE_SCOPE_PROPOSAL,
        MODE_SPELL,
        MODE_TERM_MEANING,
        MODE_PROMPT_ANALYSIS,
        MODE_INTENT_ORGANIZER,
        MODE_HOWARD_INTENT_COMMENT,
    ]
    assert all(receipt.binding_kind == "BASE_ONLY" for receipt in result.activation_receipts)
    assert all(receipt.authority_tier == "T0" for receipt in result.activation_receipts)
