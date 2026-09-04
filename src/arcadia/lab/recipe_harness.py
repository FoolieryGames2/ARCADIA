"""Honest executable Recipe 0 base-only qualification slice."""

from __future__ import annotations

from dataclasses import dataclass

from arcadia.contracts.aae.registry import MODE_SCOPE_PROPOSAL
from arcadia.core.canonical_json import JsonValue
from arcadia.core.ids import CanonicalId
from arcadia.core.work_budget import BudgetLimits, WorkBudgetLedger
from arcadia.lab.base_only_invoker import ActivationReceipt, BaseOnlySpecialistInvoker
from arcadia.recipes.r0.controller import ConversationPacket


@dataclass(frozen=True, slots=True)
class RecipeHarnessResult:
    conversation_packet: ConversationPacket
    scope_output: dict[str, JsonValue]
    activation_receipt: ActivationReceipt
    completed_recipes: tuple[str, ...]
    next_recipe: str
    next_standing: str


def _budget() -> WorkBudgetLedger:
    return WorkBudgetLedger.create(
        BudgetLimits(
            max_model_calls=2,
            max_repairs_per_call=0,
            max_reentries=0,
            max_history_expansions=0,
            max_context_retrieval_expansions=0,
            max_decision_work_items=0,
            max_reconciliation_discovery_depth=0,
            max_side_effect_retries=0,
            max_compensations=0,
            max_total_model_input_tokens=16_384,
            max_total_model_output_tokens=2_048,
        )
    )


def run_recipe0_base_only(
    prompt: str, *, invoker: BaseOnlySpecialistInvoker
) -> RecipeHarnessResult:
    """Run the implemented zero-history R0 path and stop before absent R1 authority."""

    if type(prompt) is not str or not prompt.strip():
        raise ValueError("recipe prompt must be nonempty text")
    turn_id = CanonicalId.new()
    conversation_id = CanonicalId.new()
    call_data: dict[str, JsonValue] = {
        "mode": MODE_SCOPE_PROPOSAL,
        "turn_uuid": str(turn_id),
        "conversation_uuid": str(conversation_id),
        "raw_user_prompt": prompt,
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
    invocation = invoker.invoke(
        specialist_mode_id=MODE_SCOPE_PROPOSAL,
        call_data=call_data,
        budget=_budget(),
    )
    if type(invocation.output) is not dict:
        raise RuntimeError("validated SCOPE_PROPOSAL output is not an object")
    packet = ConversationPacket.freeze(
        turn_id=turn_id,
        conversation_id=conversation_id,
        raw_user_prompt=prompt,
        transcript_commit_seq=0,
        included_turns=(),
        unresolved_references=(),
        scope_status="SUFFICIENT_WITHOUT_HISTORY",
    )
    return RecipeHarnessResult(
        conversation_packet=packet,
        scope_output=invocation.output,
        activation_receipt=invocation.receipt,
        completed_recipes=("R0",),
        next_recipe="R1",
        next_standing="NOT_IMPLEMENTED",
    )
