"""Live qualification trace for recipe-mode learned calls.

This module is deliberately presentation-only. It exposes the exact model request and
raw model response to the local operator while preserving the existing deterministic
validation and authority boundaries.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from textwrap import wrap
from typing import Final, Protocol

from arcadia.aa_runtime.serializer import ModelMessage
from arcadia.core.canonical_json import JsonValue, canonical_json_dumps
from arcadia.core.validation import StrictJsonSchema
from arcadia.core.work_budget import WorkBudgetLedger
from arcadia.lab.base_only_invoker import ActivationReceipt, StructuredRuntime
from arcadia.lab.config import LabSettings
from arcadia.lab.server import ServerResponse

RECIPE_SLICE_BOX_CONTENT_WIDTH: Final = 76


@dataclass(frozen=True, slots=True)
class RecipeSlicePresentation:
    """Operator-facing identity for one implemented recipe slice."""

    recipe_id: str
    title: str
    description: str


RECIPE_SLICE_PRESENTATIONS: Final[dict[str, RecipeSlicePresentation]] = {
    "R0": RecipeSlicePresentation(
        recipe_id="R0",
        title="Conversation Resolver",
        description=(
            "Selects the minimum sufficient completed-transcript context for the current turn."
        ),
    ),
    "R1": RecipeSlicePresentation(
        recipe_id="R1",
        title="Intent",
        description=("Converts the resolved turn into immutable requirements and Context needs."),
    ),
}


def _slice_box_lines(presentation: RecipeSlicePresentation) -> tuple[str, ...]:
    border = "+" + "-" * (RECIPE_SLICE_BOX_CONTENT_WIDTH + 2) + "+"
    fields = (
        ("SLICE TITLE", presentation.title),
        ("IDENTITY", f"Recipe {presentation.recipe_id[1:]} ({presentation.recipe_id})"),
        ("DESCRIPTION", presentation.description),
    )
    content: list[str] = []
    for label, value in fields:
        prefix = f"{label}: "
        content.extend(
            wrap(
                value,
                width=RECIPE_SLICE_BOX_CONTENT_WIDTH,
                initial_indent=prefix,
                subsequent_indent=" " * len(prefix),
                break_long_words=False,
                break_on_hyphens=False,
            )
        )
    return (
        border,
        *(f"| {line:<{RECIPE_SLICE_BOX_CONTENT_WIDTH}} |" for line in content),
        border,
    )


class RecipeCallObserver(Protocol):
    """Observe qualification calls without acquiring recipe or model authority."""

    def slice_started(self, *, recipe_id: str) -> None: ...

    def slice_completed(self, *, recipe_id: str) -> None: ...

    def call_started(
        self,
        *,
        mode: str,
        call_data: JsonValue,
        budget: WorkBudgetLedger,
    ) -> None: ...

    def call_succeeded(
        self,
        *,
        mode: str,
        receipt: ActivationReceipt,
        budget: WorkBudgetLedger,
    ) -> None: ...

    def call_failed(self, *, mode: str, error: Exception) -> None: ...


@dataclass(slots=True)
class ConsoleRecipeTrace:
    """Print exact T0 learned-call evidence synchronously to the operator console."""

    call_ordinal: int = 0
    _active_mode: str | None = field(default=None, init=False)
    _active_slice: str | None = field(default=None, init=False)
    _slice_started_once: bool = field(default=False, init=False)

    @staticmethod
    def _emit(text: str = "") -> None:
        print(text, flush=True)

    def slice_started(self, *, recipe_id: str) -> None:
        presentation = RECIPE_SLICE_PRESENTATIONS.get(recipe_id)
        if presentation is None:
            raise ValueError(f"missing CLI presentation metadata for recipe slice {recipe_id}")
        if self._active_slice is not None:
            raise RuntimeError(
                f"cannot start recipe slice {recipe_id}; {self._active_slice} is still active"
            )
        if self._slice_started_once:
            # Exactly two empty lines separate the prior slice content/status from
            # the next slice title box.
            self._emit()
            self._emit()
        else:
            self._emit()
        for line in _slice_box_lines(presentation):
            self._emit(line)
        self._active_slice = recipe_id
        self._slice_started_once = True

    def slice_completed(self, *, recipe_id: str) -> None:
        if self._active_slice != recipe_id:
            raise RuntimeError(
                f"cannot complete recipe slice {recipe_id}; active slice is "
                f"{self._active_slice or 'NONE'}"
            )
        presentation = RECIPE_SLICE_PRESENTATIONS[recipe_id]
        self._emit(f"SLICE STATUS> {recipe_id} {presentation.title} COMPLETE")
        self._active_slice = None

    def call_started(
        self,
        *,
        mode: str,
        call_data: JsonValue,
        budget: WorkBudgetLedger,
    ) -> None:
        self.call_ordinal += 1
        self._active_mode = mode
        self._emit()
        self._emit(f"=== T0 LEARNED CALL {self.call_ordinal}: {mode} ===")
        self._emit("HOST CALL_DATA>")
        self._emit(canonical_json_dumps(call_data))
        self._emit("HOST BUDGET BEFORE>")
        self._emit(canonical_json_dumps(budget.usage.to_value()))

    def model_request(self, messages: Sequence[ModelMessage]) -> None:
        mode = self._active_mode or "UNKNOWN_MODE"
        self._emit(f"MODEL INPUT [{mode}]>")
        for message in messages:
            self._emit(f"[{message.role.upper()}]")
            self._emit(message.content)

    def model_response(self, response: ServerResponse) -> None:
        mode = self._active_mode or "UNKNOWN_MODE"
        self._emit(f"MODEL RAW OUTPUT [{mode}] [UNTRUSTED]>")
        self._emit(response.text)
        self._emit(
            "MODEL METRICS> "
            f"prompt_tokens={response.prompt_tokens} "
            f"completion_tokens={response.completion_tokens} "
            f"elapsed_seconds={response.elapsed_seconds:.3f}"
        )

    def runtime_failed(self, error: Exception) -> None:
        mode = self._active_mode or "UNKNOWN_MODE"
        self._emit(f"MODEL RUNTIME ERROR [{mode}]> {type(error).__name__}: {error}")

    def call_succeeded(
        self,
        *,
        mode: str,
        receipt: ActivationReceipt,
        budget: WorkBudgetLedger,
    ) -> None:
        for correction in receipt.host_corrections:
            self._emit(
                "HOST CORRECTION [NON-FATAL]> "
                f"code={correction.code} action={correction.action} "
                f"source_output_hash={correction.source_output_hash.value}"
            )
            self._emit(f"HOST CORRECTION DETAIL> {correction.detail}")
        standing = "PASS_WITH_HOST_CONTINUATION" if receipt.host_corrections else "PASS"
        self._emit(
            f"BASE_ONLY INVOKER> {standing} "
            f"mode={mode} call_uuid={receipt.call_id} output_hash={receipt.output_hash.value}"
        )
        self._emit("HOST BUDGET AFTER>")
        self._emit(canonical_json_dumps(budget.usage.to_value()))
        self._active_mode = None

    def call_failed(self, *, mode: str, error: Exception) -> None:
        self._emit(f"BASE_ONLY INVOKER> REJECTED mode={mode}")
        self._emit(f"HOST ERROR> {type(error).__name__}: {error}")
        self._active_mode = None


@dataclass(slots=True)
class TracingStructuredRuntime:
    """Mirror a structured runtime while exposing exact request/response text."""

    runtime: StructuredRuntime
    trace: ConsoleRecipeTrace

    def count_tokens(self, messages: Sequence[ModelMessage]) -> int:
        return self.runtime.count_tokens(messages)

    def complete(
        self,
        messages: Sequence[ModelMessage],
        *,
        output_schema: StrictJsonSchema | None = None,
        settings: LabSettings | None = None,
    ) -> ServerResponse:
        self.trace.model_request(messages)
        try:
            response = self.runtime.complete(
                messages,
                output_schema=output_schema,
                settings=settings,
            )
        except Exception as exc:
            self.trace.runtime_failed(exc)
            raise
        self.trace.model_response(response)
        return response
