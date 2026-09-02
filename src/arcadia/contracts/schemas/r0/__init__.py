"""Recipe 0 strict schema definitions."""

from arcadia.contracts.schemas.r0.scope_proposal import (
    SCOPE_PROPOSAL_INPUT_SCHEMA,
    SCOPE_PROPOSAL_OUTPUT_SCHEMA,
    ScopeProposalSemanticError,
    require_valid_scope_proposal_output,
)
from arcadia.contracts.schemas.r0.scope_validation import (
    SCOPE_VALIDATION_INPUT_SCHEMA,
    SCOPE_VALIDATION_OUTPUT_SCHEMA,
    ScopeValidationSemanticError,
    require_valid_scope_validation_call_data,
    require_valid_scope_validation_output,
)

__all__ = [
    "SCOPE_PROPOSAL_INPUT_SCHEMA",
    "SCOPE_PROPOSAL_OUTPUT_SCHEMA",
    "SCOPE_VALIDATION_INPUT_SCHEMA",
    "SCOPE_VALIDATION_OUTPUT_SCHEMA",
    "ScopeProposalSemanticError",
    "ScopeValidationSemanticError",
    "require_valid_scope_proposal_output",
    "require_valid_scope_validation_call_data",
    "require_valid_scope_validation_output",
]
