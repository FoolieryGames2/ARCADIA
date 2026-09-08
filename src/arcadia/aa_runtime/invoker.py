"""Typed learned-call invoker boundary consumed by recipe controllers.

The concrete model/runtime/adapter state machine is intentionally implemented behind
this interface. Recipe controllers receive only validated invocation records and do
not own model residency, adapter activation, parsing, repair, or runtime authority.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from arcadia.core.canonical_json import JsonValue
from arcadia.core.ids import CanonicalId


@dataclass(frozen=True, slots=True)
class SpecialistInvocation:
    """One learned-call attempt returned by the host-owned SpecialistInvoker boundary."""

    attempt_id: CanonicalId
    mode: str
    call_data: JsonValue
    output: JsonValue


class SpecialistInvoker(Protocol):
    """Recipe-facing contract for one isolated learned specialist call."""

    def invoke(
        self,
        *,
        mode: str,
        call_data: JsonValue,
    ) -> SpecialistInvocation:
        """Run one fresh learned attempt and return its host-validated structured output."""
        ...
