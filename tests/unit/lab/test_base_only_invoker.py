from __future__ import annotations

from collections.abc import Sequence

import pytest

from arcadia.aa_runtime.serializer import ModelMessage
from arcadia.core.canonical_json import JsonValue, canonical_json_dumps
from arcadia.core.work_budget import BudgetLimits, WorkBudgetLedger
from arcadia.lab.base_only_invoker import (
    BaseOnlySpecialistInvoker,
    QualificationInvocationError,
)
from arcadia.lab.config import LabSettings, RuntimeIdentity
from arcadia.lab.server import ServerResponse


def _settings() -> LabSettings:
    return LabSettings("recipe", "resident", 2048, 128, 0.0, 42, 99, 18080, "T0")


def _identity() -> RuntimeIdentity:
    from pathlib import Path

    return RuntimeIdentity(
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


def _budget() -> WorkBudgetLedger:
    return WorkBudgetLedger.create(BudgetLimits(2, 0, 0, 0, 0, 0, 0, 0, 0, 4096, 512))


def _call_data() -> dict[str, JsonValue]:
    return {
        "mode": "SCOPE_PROPOSAL",
        "turn_uuid": "TURN-1",
        "conversation_uuid": "CONV-1",
        "raw_user_prompt": "Hello",
        "current_transcript_metadata": {
            "transcript_commit_seq": 0,
            "completed_exchange_count": 0,
            "continuation_state": {
                "status": "NONE",
                "source_turn_uuid": None,
                "reason_code": None,
            },
        },
        "host_policy_limits": {
            "max_contiguous_lookback_exchanges": 20,
            "max_targeted_candidate_turns_per_search": 8,
            "max_scope_expansion_cycles": 3,
            "max_total_injected_history_tokens": 4096,
        },
    }


class FakeRuntime:
    def __init__(self, output: JsonValue) -> None:
        self.output = output
        self.messages: Sequence[ModelMessage] = ()

    def count_tokens(self, messages: Sequence[ModelMessage]) -> int:
        self.messages = messages
        return 100

    def complete(self, messages: Sequence[ModelMessage], **_: object) -> ServerResponse:
        self.messages = messages
        return ServerResponse(canonical_json_dumps(self.output), 0.2, 100, 20)


def test_base_only_invoker_runs_final_gate_budget_schema_and_receipt() -> None:
    runtime = FakeRuntime(
        {
            "mode": "SCOPE_PROPOSAL",
            "status": "SUFFICIENT_WITHOUT_HISTORY",
            "recent_exchange_count": 0,
            "target_terms": [],
            "reason_codes": ["SELF_CONTAINED"],
        }
    )
    result = BaseOnlySpecialistInvoker(runtime, _identity(), _settings()).invoke(
        specialist_mode_id="SCOPE_PROPOSAL", call_data=_call_data(), budget=_budget()
    )

    assert tuple(message.role for message in runtime.messages) == ("system", "user")
    assert result.receipt.binding_kind == "BASE_ONLY"
    assert result.receipt.adapter_lease_id is None
    assert result.receipt.fresh_context is True
    assert result.receipt.fresh_sampler is True
    assert result.receipt.input_tokens == 100
    assert result.budget.usage.model_calls == 1
    assert result.budget.usage.model_input_tokens == 100


def test_base_only_invoker_rejects_semantically_illegal_schema_valid_output() -> None:
    runtime = FakeRuntime(
        {
            "mode": "SCOPE_PROPOSAL",
            "status": "REQUEST_RECENT",
            "recent_exchange_count": 1,
            "target_terms": [],
            "reason_codes": ["NEEDS_HISTORY"],
        }
    )
    with pytest.raises(QualificationInvocationError, match="history cannot be requested"):
        BaseOnlySpecialistInvoker(runtime, _identity(), _settings()).invoke(
            specialist_mode_id="SCOPE_PROPOSAL", call_data=_call_data(), budget=_budget()
        )
