"""Final production-equivalent CALL_DATA reparse/revalidation gate."""

from __future__ import annotations

from dataclasses import dataclass

from arcadia.aa_runtime.serializer import SerializedAAECall
from arcadia.core.canonical_json import JsonValue, require_canonical_json
from arcadia.core.hashing import Sha256Digest, sha256_canonical_json
from arcadia.core.validation import StrictJsonSchema, ValidationReport


class CallDataGateError(ValueError):
    """The final rendered CALL_DATA cannot be proven identical to host input."""


@dataclass(frozen=True, slots=True)
class PreDispatchCallData:
    """Evidence that final message bytes survived strict parse/schema/equality checks."""

    value: JsonValue
    validation: ValidationReport
    instance_hash: Sha256Digest
    message_index: int


def require_pre_dispatch_call_data(
    prepared: SerializedAAECall,
    *,
    input_schema: StrictJsonSchema,
) -> PreDispatchCallData:
    """Reparse and revalidate the exact lower-role message immediately before dispatch.

    Extraction is by the host-owned structured message index. The human audit renderer
    is intentionally never scanned for delimiters.
    """

    index = prepared.call_data_message_index
    if index < 0 or index >= len(prepared.messages):
        raise CallDataGateError("CALL_DATA message index is outside the final message list")
    message = prepared.messages[index]
    if message.role != "user":
        raise CallDataGateError("CALL_DATA must remain in the lower-trust user-role message")

    expected_binding = (
        prepared.call.input_schema_version,
        prepared.input_validation.schema_id,
    )
    actual_binding = (input_schema.schema_version, input_schema.schema_id)
    if actual_binding != expected_binding:
        raise CallDataGateError("final CALL_DATA schema binding differs from prepared call")

    try:
        parsed = require_canonical_json(message.content)
        validation = input_schema.require_valid(parsed)
    except ValueError as exc:
        raise CallDataGateError(f"final CALL_DATA rejected: {exc}") from exc

    if message.content != prepared.canonical_call_data:
        raise CallDataGateError("final CALL_DATA bytes differ from the prepared canonical payload")
    if parsed != prepared.call.data_plane:
        raise CallDataGateError("final CALL_DATA value differs from the host AAE data plane")
    if validation.schema_hash != prepared.input_validation.schema_hash:
        raise CallDataGateError("final CALL_DATA schema snapshot differs from initial validation")
    if validation.instance_hash != prepared.input_validation.instance_hash:
        raise CallDataGateError("final CALL_DATA instance hash differs from initial validation")

    return PreDispatchCallData(
        value=parsed,
        validation=validation,
        instance_hash=sha256_canonical_json(parsed),
        message_index=index,
    )
