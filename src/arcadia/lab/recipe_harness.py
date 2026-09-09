"""Honest executable Recipe 0 -> Recipe 1 BASE_ONLY qualification harness."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Final

from arcadia.aa_runtime.serializer import ModelMessage
from arcadia.core.canonical_json import JsonValue, canonical_json_dumps
from arcadia.core.config import StorageConfig, load_config
from arcadia.core.ids import CanonicalId
from arcadia.core.work_budget import BudgetLimits, WorkBudgetLedger
from arcadia.lab.base_only_invoker import ActivationReceipt, BaseOnlySpecialistInvoker
from arcadia.lab.config import resolve_workspace
from arcadia.lab.recipe_bridge import BudgetedBaseOnlyRecipeInvoker
from arcadia.lab.recipe_trace import RecipeCallObserver
from arcadia.recipes.r0.controller import (
    ConversationPacket,
    Recipe0ConversationController,
    Recipe0Policy,
    Recipe0Result,
)
from arcadia.recipes.r1.controller import Recipe1IntentController, Recipe1Result
from arcadia.storage.connection import SQLiteConnectionFactory
from arcadia.storage.migrations import MigrationRunner
from arcadia.storage.transcript_repository import TranscriptRepository

RUNTIME_CONFIG_NAME: Final = "configs/runtime.toml"
RECIPE0_LAB_DATABASE_NAME: Final = "arcadia_recipe0_lab.sqlite3"
RECIPE0_LAB_PROJECT_ID: Final = CanonicalId.parse(
    "48003a9b-1516-4ac3-bbb3-e3366f63bde8"
)
R1_REQUIRED_MODEL_CALLS: Final = 4
R1_INTENT_COMMENT_MODEL_CALLS: Final = 1


@dataclass(frozen=True, slots=True)
class RecipeHarnessResult:
    """Recipe 0-only compatibility result retained for isolated R0 qualification."""

    conversation_packet: ConversationPacket
    r0_result: Recipe0Result
    activation_receipts: tuple[ActivationReceipt, ...]
    budget: WorkBudgetLedger
    completed_recipes: tuple[str, ...]
    next_recipe: str
    next_standing: str

    @property
    def activation_receipt(self) -> ActivationReceipt:
        """Compatibility view of the final R0 learned-call receipt."""

        if not self.activation_receipts:
            raise RuntimeError("Recipe 0 completed without a learned-call activation receipt")
        return self.activation_receipts[-1]

    @property
    def scope_output(self) -> dict[str, JsonValue]:
        """Compatibility view of the proposal or final validation output."""

        invocation = self.r0_result.proposal_invocation
        if invocation is None:
            invocation = self.r0_result.validation_invocation
        if invocation is None or type(invocation.output) is not dict:
            raise RuntimeError("Recipe 0 completed without a structured scope output")
        return invocation.output


@dataclass(frozen=True, slots=True)
class Recipe01HarnessResult:
    """Complete executable R0 -> R1 qualification result, stopping before R2."""

    conversation_packet: ConversationPacket
    r0_result: Recipe0Result
    r1_result: Recipe1Result
    r0_activation_receipts: tuple[ActivationReceipt, ...]
    r1_activation_receipts: tuple[ActivationReceipt, ...]
    activation_receipts: tuple[ActivationReceipt, ...]
    budget: WorkBudgetLedger
    completed_recipes: tuple[str, ...]
    next_recipe: str
    next_standing: str


def _budget(policy: Recipe0Policy, *, extra_model_calls: int = 0) -> WorkBudgetLedger:
    if type(extra_model_calls) is not int or extra_model_calls < 0:
        raise ValueError("extra_model_calls must be a nonnegative integer")
    max_r0_model_calls = max(1, policy.max_scope_expansion_cycles + 1)
    max_model_calls = max_r0_model_calls + extra_model_calls
    return WorkBudgetLedger.create(
        BudgetLimits(
            max_model_calls=max_model_calls,
            max_repairs_per_call=0,
            max_reentries=0,
            max_history_expansions=policy.max_scope_expansion_cycles,
            max_context_retrieval_expansions=0,
            max_decision_work_items=0,
            max_reconciliation_discovery_depth=0,
            max_side_effect_retries=0,
            max_compensations=0,
            max_total_model_input_tokens=16_384 * max_model_calls,
            max_total_model_output_tokens=2_048 * max_model_calls,
        )
    )


def _default_transcript(workspace: Path) -> TranscriptRepository:
    config = load_config(workspace / RUNTIME_CONFIG_NAME)
    storage = StorageConfig(
        data_dir=config.storage.data_dir,
        database_name=RECIPE0_LAB_DATABASE_NAME,
        busy_timeout_ms=config.storage.busy_timeout_ms,
        require_fts5=config.storage.require_fts5,
    )
    factory = SQLiteConnectionFactory(workspace_root=workspace, storage=storage)
    with factory.connect() as connection:
        MigrationRunner().migrate(connection, applied_at=datetime.now(UTC))
    return TranscriptRepository(factory, RECIPE0_LAB_PROJECT_ID)


@dataclass(frozen=True, slots=True)
class RecipeLabSession:
    """Host-owned interactive recipe conversation over the isolated lab transcript."""

    transcript: TranscriptRepository
    conversation_id: CanonicalId

    @classmethod
    def create(cls, workspace: Path | None = None) -> RecipeLabSession:
        transcript = _default_transcript(resolve_workspace(workspace))
        conversation_id = CanonicalId.new()
        transcript.create_conversation(
            conversation_id=conversation_id,
            created_at=datetime.now(UTC),
        )
        return cls(transcript=transcript, conversation_id=conversation_id)

    def new_conversation(self) -> RecipeLabSession:
        conversation_id = CanonicalId.new()
        self.transcript.create_conversation(
            conversation_id=conversation_id,
            created_at=datetime.now(UTC),
        )
        return RecipeLabSession(
            transcript=self.transcript,
            conversation_id=conversation_id,
        )


def _history_token_counter(
    invoker: BaseOnlySpecialistInvoker,
    turns: tuple[dict[str, JsonValue], ...],
) -> int:
    """Conservatively count the exact frozen history JSON with the resident tokenizer."""

    payload = canonical_json_dumps(list(turns))
    return invoker.runtime.count_tokens((ModelMessage(role="user", content=payload),))


def _start_turn(
    prompt: str,
    *,
    transcript: TranscriptRepository | None,
    conversation_id: CanonicalId | None,
    workspace: Path | None,
) -> tuple[TranscriptRepository, CanonicalId, CanonicalId]:
    if type(prompt) is not str or not prompt.strip():
        raise ValueError("recipe prompt must be nonempty text")

    active_transcript = transcript
    if active_transcript is None:
        active_transcript = _default_transcript(resolve_workspace(workspace))

    now = datetime.now(UTC)
    active_conversation_id = conversation_id
    if active_conversation_id is None:
        active_conversation_id = CanonicalId.new()
        active_transcript.create_conversation(
            conversation_id=active_conversation_id,
            created_at=now,
        )

    turn_id = CanonicalId.new()
    active_transcript.append_user_turn(
        conversation_id=active_conversation_id,
        turn_id=turn_id,
        content=prompt,
        created_at=now,
    )
    return active_transcript, active_conversation_id, turn_id


def _run_r0(
    prompt: str,
    *,
    invoker: BaseOnlySpecialistInvoker,
    active_transcript: TranscriptRepository,
    conversation_id: CanonicalId,
    turn_id: CanonicalId,
    recipe_invoker: BudgetedBaseOnlyRecipeInvoker,
    policy: Recipe0Policy,
) -> Recipe0Result:
    controller = Recipe0ConversationController(
        transcript=active_transcript,
        invoker=recipe_invoker,
        history_token_counter=lambda turns: _history_token_counter(invoker, turns),
        policy=policy,
    )
    return controller.run(
        turn_id=turn_id,
        conversation_id=conversation_id,
        raw_user_prompt=prompt,
    )


def run_recipe0_base_only(
    prompt: str,
    *,
    invoker: BaseOnlySpecialistInvoker,
    transcript: TranscriptRepository | None = None,
    conversation_id: CanonicalId | None = None,
    workspace: Path | None = None,
    observer: RecipeCallObserver | None = None,
) -> RecipeHarnessResult:
    """Run the real bounded R0 controller and stop before Recipe 1.

    This compatibility entry point remains useful for isolated Recipe 0 qualification.
    The current USER turn is started in the real transcript repository but deliberately
    remains OPEN because R8/publication authority is not implemented here.
    """

    active_transcript, active_conversation_id, turn_id = _start_turn(
        prompt,
        transcript=transcript,
        conversation_id=conversation_id,
        workspace=workspace,
    )
    policy = Recipe0Policy()
    recipe_invoker = BudgetedBaseOnlyRecipeInvoker(invoker, _budget(policy), observer)
    r0_result = _run_r0(
        prompt,
        invoker=invoker,
        active_transcript=active_transcript,
        conversation_id=active_conversation_id,
        turn_id=turn_id,
        recipe_invoker=recipe_invoker,
        policy=policy,
    )
    return RecipeHarnessResult(
        conversation_packet=r0_result.packet,
        r0_result=r0_result,
        activation_receipts=recipe_invoker.receipts,
        budget=recipe_invoker.budget,
        completed_recipes=("R0",),
        next_recipe="R1",
        next_standing="NOT_IMPLEMENTED",
    )


def run_recipe01_base_only(
    prompt: str,
    *,
    invoker: BaseOnlySpecialistInvoker,
    transcript: TranscriptRepository | None = None,
    conversation_id: CanonicalId | None = None,
    workspace: Path | None = None,
    capability_availability: tuple[dict[str, JsonValue], ...] = (),
    include_intent_comment: bool = True,
    observer: RecipeCallObserver | None = None,
) -> Recipe01HarnessResult:
    """Run R0 then R1 through one BASE_ONLY invoker/budget chain and stop at R2.

    Capability availability is host-supplied knowledge only. The T0 lab defaults to an
    empty availability set until a separate host capability-registry bridge is wired.
    The current transcript turn remains OPEN; this slice does not impersonate R8.
    """

    if type(include_intent_comment) is not bool:
        raise ValueError("include_intent_comment must be an exact bool")

    active_transcript, active_conversation_id, turn_id = _start_turn(
        prompt,
        transcript=transcript,
        conversation_id=conversation_id,
        workspace=workspace,
    )
    policy = Recipe0Policy()
    r1_calls = R1_REQUIRED_MODEL_CALLS + (
        R1_INTENT_COMMENT_MODEL_CALLS if include_intent_comment else 0
    )
    recipe_invoker = BudgetedBaseOnlyRecipeInvoker(
        invoker,
        _budget(policy, extra_model_calls=r1_calls),
        observer,
    )

    r0_result = _run_r0(
        prompt,
        invoker=invoker,
        active_transcript=active_transcript,
        conversation_id=active_conversation_id,
        turn_id=turn_id,
        recipe_invoker=recipe_invoker,
        policy=policy,
    )
    r0_receipt_count = len(recipe_invoker.receipts)

    r1_result = Recipe1IntentController(invoker=recipe_invoker).run(
        packet=r0_result.packet,
        capability_availability=capability_availability,
        include_intent_comment=include_intent_comment,
    )
    receipts = recipe_invoker.receipts
    return Recipe01HarnessResult(
        conversation_packet=r0_result.packet,
        r0_result=r0_result,
        r1_result=r1_result,
        r0_activation_receipts=receipts[:r0_receipt_count],
        r1_activation_receipts=receipts[r0_receipt_count:],
        activation_receipts=receipts,
        budget=recipe_invoker.budget,
        completed_recipes=("R0", "R1"),
        next_recipe="R2",
        next_standing="NOT_IMPLEMENTED",
    )
