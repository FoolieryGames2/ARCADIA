"""Host-owned learned-call AAE preparation boundary."""

from arcadia.aa_runtime.call_data_gate import (
    CallDataGateError,
    PreDispatchCallData,
    require_pre_dispatch_call_data,
)
from arcadia.aa_runtime.human_renderer import render_aae_audit
from arcadia.aa_runtime.serializer import (
    AAECall,
    AuthorityPlane,
    ModelMessage,
    SerializedAAECall,
    build_aae_call,
    serialize_aae_call,
)

__all__ = [
    "AAECall",
    "AuthorityPlane",
    "CallDataGateError",
    "ModelMessage",
    "PreDispatchCallData",
    "SerializedAAECall",
    "build_aae_call",
    "render_aae_audit",
    "require_pre_dispatch_call_data",
    "serialize_aae_call",
]
