from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

import pytest

from arcadia.aa_runtime.serializer import ModelMessage
from arcadia.core.canonical_json import JsonValue, canonical_json_dumps
from arcadia.core.work_budget import BudgetLimits, WorkBudgetLedger
from arcadia.lab.base_only_invoker import (
    BaseOnlySpecialistInvoker,
)
from arcadia.lab.config import LabSettings, RuntimeIdentity
from arcadia.lab.recipe_bridge import BudgetedBaseOnlyRecipeInvoker
from arcadia.lab.recipe_trace import ConsoleRecipeTrace, TracingStructuredRuntime
from arcadia.lab.server import ServerResponse


def _settings() -> LabSettings:
    return LabSettings("recipe", "resident", 2048, 128, 0.0, 42, 99, 18080, "T0")


def _identity() -> RuntimeIdentity:
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
    return WorkBudgetLedger.create(
        BudgetLimits(
            max_model_calls=1,
            max_repairs_per_call=0,
            max_reentries=0,
            max_history_expansions=0,
            max_context_retrieval_expansions=0,
            max_decision_work_items=0,
            max_reconciliation_discovery_depth=0,
            max_side_effect_retries=0,
            max_compensations=0,
            max_total_model_input_tokens=4096,
            max_total_model_output_tokens=512,
        )
    )


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

    def count_tokens(self, _messages: Sequence[ModelMessage]) -> int:
        return 100

    def complete(
        self,
        _messages: Sequence[ModelMessage],
        **_: object,
    ) -> ServerResponse:
        return ServerResponse(canonical_json_dumps(self.output), 0.2, 100, 20)


def test_live_trace_logs_nonfatal_zero_history_continuation(
    capsys: pytest.CaptureFixture[str],
) -> None:
    runtime = FakeRuntime(
        {
            "mode": "SCOPE_PROPOSAL",
            "status": "REQUEST_RECENT",
            "recent_exchange_count": 1,
            "target_terms": [],
            "reason_codes": ["NEEDS_HISTORY"],
        }
    )
    trace = ConsoleRecipeTrace()
    base = BaseOnlySpecialistInvoker(TracingStructuredRuntime(runtime, trace), _identity(), _settings())
    invoker = BudgetedBaseOnlyRecipeInvoker(base, _budget(), trace)

    result = invoker.invoke(mode="SCOPE_PROPOSAL", call_data=_call_data())

    output = capsys.readouterr().out
    assert result.host_corrections[0].code == "R0_NO_COMPLETED_HISTORY_AVAILABLE"
    assert "HOST CALL_DATA>" in output
    assert "MODEL INPUT [SCOPE_PROPOSAL]>" in output
    assert "MODEL RAW OUTPUT [SCOPE_PROPOSAL] [UNTRUSTED]>" in output
    assert '"status":"REQUEST_RECENT"' in output
    assert "HOST CORRECTION [NON-FATAL]>" in output
    assert "CONTINUE_TO_INTENT_WITH_UNRESOLVABLE_TRANSCRIPT" in output
    assert "BASE_ONLY INVOKER> PASS_WITH_HOST_CONTINUATION" in output
    assert output.index("MODEL RAW OUTPUT") < output.index("HOST CORRECTION [NON-FATAL]")


def test_live_trace_reports_accepted_call_and_budget(
    capsys: pytest.CaptureFixture[str],
) -> None:
    runtime = FakeRuntime(
        {
            "mode": "SCOPE_PROPOSAL",
            "status": "SUFFICIENT_WITHOUT_HISTORY",
            "recent_exchange_count": 0,
            "target_terms": [],
            "reason_codes": ["SELF_CONTAINED"],
        }
    )
    trace = ConsoleRecipeTrace()
    base = BaseOnlySpecialistInvoker(TracingStructuredRuntime(runtime, trace), _identity(), _settings())
    invoker = BudgetedBaseOnlyRecipeInvoker(base, _budget(), trace)

    result = invoker.invoke(mode="SCOPE_PROPOSAL", call_data=_call_data())

    output = capsys.readouterr().out
    assert result.output == runtime.output
    assert "MODEL METRICS> prompt_tokens=100 completion_tokens=20 elapsed_seconds=0.200" in output
    assert "BASE_ONLY INVOKER> PASS mode=SCOPE_PROPOSAL" in output
    assert '"model_calls":1' in output
    assert output.index("MODEL RAW OUTPUT") < output.index("BASE_ONLY INVOKER> PASS")
