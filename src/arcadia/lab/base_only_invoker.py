"""Qualification-only BASE_ONLY learned-call entry point for the local lab."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol

from arcadia.aa_runtime.call_data_gate import require_pre_dispatch_call_data
from arcadia.aa_runtime.serializer import ModelMessage, serialize_aae_call
from arcadia.contracts.aae.registry import get_contract
from arcadia.contracts.schemas.catalog import LEARNED_MODE_SCHEMAS
from arcadia.contracts.schemas.r0.scope_proposal import require_valid_scope_proposal_output
from arcadia.contracts.schemas.r0.scope_validation import require_valid_scope_validation_output
from arcadia.core.canonical_json import JsonValue, strict_json_loads
from arcadia.core.hashing import Sha256Digest, sha256_canonical_json
from arcadia.core.ids import CanonicalId
from arcadia.core.validation import StrictJsonSchema
from arcadia.core.work_budget import WorkBudgetLedger
from arcadia.lab.config import LabSettings, RuntimeIdentity
from arcadia.lab.server import ServerResponse


class QualificationInvocationError(RuntimeError):
    """A base-only qualification call failed a frozen host boundary."""


class StructuredRuntime(Protocol):
    def count_tokens(self, messages: Sequence[ModelMessage]) -> int: ...

    def complete(
        self,
        messages: Sequence[ModelMessage],
        *,
        output_schema: StrictJsonSchema | None = None,
        settings: LabSettings | None = None,
    ) -> ServerResponse: ...


@dataclass(frozen=True, slots=True)
class ActivationReceipt:
    call_id: CanonicalId
    specialist_mode_id: str
    physical_adapter_id: str
    binding_kind: str
    adapter_lease_id: None
    authority_tier: str
    runtime_manifest_id: str
    model_sha256: str
    llama_commit: str
    input_schema_hash: Sha256Digest
    call_data_hash: Sha256Digest
    output_schema_hash: Sha256Digest
    output_hash: Sha256Digest
    input_tokens: int
    output_tokens: int
    elapsed_seconds: float
    fresh_context: bool
    fresh_sampler: bool


@dataclass(frozen=True, slots=True)
class QualificationInvocation:
    output: JsonValue
    receipt: ActivationReceipt
    budget: WorkBudgetLedger


def _semantic_validate(mode: str, output: JsonValue, call_data: JsonValue) -> JsonValue:
    if mode == "SCOPE_PROPOSAL":
        return require_valid_scope_proposal_output(output, call_data=call_data)
    if mode == "SCOPE_VALIDATION":
        return require_valid_scope_validation_output(output, call_data=call_data)
    return LEARNED_MODE_SCHEMAS[mode].require_valid_output(output)


@dataclass(slots=True)
class BaseOnlySpecialistInvoker:
    """Use the base model for frozen calls without granting operational authority."""

    runtime: StructuredRuntime
    runtime_identity: RuntimeIdentity
    settings: LabSettings

    def invoke(
        self,
        *,
        specialist_mode_id: str,
        call_data: JsonValue,
        budget: WorkBudgetLedger,
    ) -> QualificationInvocation:
        try:
            contract = get_contract(specialist_mode_id)
            schemas = LEARNED_MODE_SCHEMAS[specialist_mode_id]
        except KeyError as exc:
            raise QualificationInvocationError(
                f"unknown learned specialist mode: {specialist_mode_id}"
            ) from exc
        if contract.dispatch_enabled or contract.runtime_ready:
            raise QualificationInvocationError(
                "BASE_ONLY qualification requires a non-dispatchable PRE-version contract"
            )

        prepared = serialize_aae_call(
            contract,
            data_plane=call_data,
            input_schema=schemas.input,
            output_schema=schemas.output,
        )
        gated = require_pre_dispatch_call_data(prepared, input_schema=schemas.input)
        call_id = CanonicalId.new()
        input_tokens = self.runtime.count_tokens(prepared.messages)
        authorized, _ = budget.authorize_model_attempt(
            call_id=call_id,
            input_tokens=input_tokens,
            reserved_output_tokens=self.settings.max_output_tokens,
            expected_head=budget.head_hash,
        )
        response = self.runtime.complete(
            prepared.messages,
            output_schema=schemas.output,
            settings=self.settings,
        )
        try:
            output = strict_json_loads(response.text)
            validated = _semantic_validate(specialist_mode_id, output, gated.value)
        except ValueError as exc:
            raise QualificationInvocationError(
                f"{specialist_mode_id} output rejected: {exc}"
            ) from exc
        receipt = ActivationReceipt(
            call_id=call_id,
            specialist_mode_id=specialist_mode_id,
            physical_adapter_id=contract.physical_adapter_id,
            binding_kind="BASE_ONLY",
            adapter_lease_id=None,
            authority_tier="T0",
            runtime_manifest_id=self.runtime_identity.manifest_id,
            model_sha256=self.runtime_identity.model_sha256,
            llama_commit=self.runtime_identity.llama_commit,
            input_schema_hash=schemas.input.schema_hash,
            call_data_hash=gated.instance_hash,
            output_schema_hash=schemas.output.schema_hash,
            output_hash=sha256_canonical_json(validated),
            input_tokens=input_tokens,
            output_tokens=response.completion_tokens,
            elapsed_seconds=response.elapsed_seconds,
            fresh_context=True,
            fresh_sampler=True,
        )
        return QualificationInvocation(output=validated, receipt=receipt, budget=authorized)
