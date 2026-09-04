"""Host-owned learned-call AAE preparation boundary."""

from arcadia.aa_runtime.call_data_gate import (
    CallDataGateError,
    PreDispatchCallData,
    require_pre_dispatch_call_data,
)
from arcadia.aa_runtime.context_projection import (
    CONTEXT_PROJECTION_VERSION,
    CandidateEvaluation,
    CandidateFailure,
    ContextProjectionError,
    ContextProjectionEvidence,
    ContextProjectionResult,
    ProjectionCandidate,
    ProjectionStanding,
    StructuralMetrics,
    project_aae_context,
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
    "CONTEXT_PROJECTION_VERSION",
    "CandidateEvaluation",
    "CandidateFailure",
    "ContextProjectionError",
    "ContextProjectionEvidence",
    "ContextProjectionResult",
    "ModelMessage",
    "PreDispatchCallData",
    "ProjectionCandidate",
    "ProjectionStanding",
    "SerializedAAECall",
    "StructuralMetrics",
    "build_aae_call",
    "render_aae_audit",
    "project_aae_context",
    "require_pre_dispatch_call_data",
    "serialize_aae_call",
]
