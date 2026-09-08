"""Recipe-facing adapter for the T0 BASE_ONLY qualification invoker."""

from __future__ import annotations

from dataclasses import dataclass, field

from arcadia.aa_runtime.invoker import SpecialistInvocation
from arcadia.core.canonical_json import JsonValue
from arcadia.core.work_budget import WorkBudgetLedger
from arcadia.lab.base_only_invoker import ActivationReceipt, BaseOnlySpecialistInvoker


@dataclass(slots=True)
class BudgetedBaseOnlyRecipeInvoker:
    """Carry one immutable work-budget chain across every learned recipe call."""

    base_invoker: BaseOnlySpecialistInvoker
    budget: WorkBudgetLedger
    _receipts: list[ActivationReceipt] = field(default_factory=list, init=False)

    def invoke(self, *, mode: str, call_data: JsonValue) -> SpecialistInvocation:
        invocation = self.base_invoker.invoke(
            specialist_mode_id=mode,
            call_data=call_data,
            budget=self.budget,
        )
        self.budget = invocation.budget
        self._receipts.append(invocation.receipt)
        return SpecialistInvocation(
            attempt_id=invocation.receipt.call_id,
            mode=mode,
            call_data=call_data,
            output=invocation.output,
        )

    @property
    def receipts(self) -> tuple[ActivationReceipt, ...]:
        return tuple(self._receipts)
