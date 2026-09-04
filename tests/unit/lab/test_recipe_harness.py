from collections.abc import Sequence
from pathlib import Path

from arcadia.aa_runtime.serializer import ModelMessage
from arcadia.core.canonical_json import JsonValue, canonical_json_dumps
from arcadia.lab.base_only_invoker import BaseOnlySpecialistInvoker
from arcadia.lab.config import LabSettings, RuntimeIdentity
from arcadia.lab.recipe_harness import run_recipe0_base_only
from arcadia.lab.server import ServerResponse


class FakeRuntime:
    def __init__(self, output: JsonValue) -> None:
        self.output = output

    def count_tokens(self, messages: Sequence[ModelMessage]) -> int:
        return 100

    def complete(self, messages: Sequence[ModelMessage], **_: object) -> ServerResponse:
        return ServerResponse(canonical_json_dumps(self.output), 0.2, 100, 20)


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


def test_recipe_harness_runs_real_r0_boundary_and_stops_before_r1() -> None:
    output: JsonValue = {
        "mode": "SCOPE_PROPOSAL",
        "status": "SUFFICIENT_WITHOUT_HISTORY",
        "recent_exchange_count": 0,
        "target_terms": [],
        "reason_codes": ["SELF_CONTAINED"],
    }
    runtime = FakeRuntime(output)
    settings = LabSettings("recipe", "resident", 2048, 128, 0.0, 42, 99, 18080, "T0")
    result = run_recipe0_base_only(
        "Hello", invoker=BaseOnlySpecialistInvoker(runtime, _identity(), settings)
    )

    assert result.completed_recipes == ("R0",)
    assert result.next_recipe == "R1"
    assert result.next_standing == "NOT_IMPLEMENTED"
    assert result.conversation_packet.raw_user_prompt == "Hello"
