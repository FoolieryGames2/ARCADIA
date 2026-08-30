"""Recipe 0 strict schema definitions."""

from arcadia.contracts.schemas.r0.scope_proposal import (
    SCOPE_PROPOSAL_INPUT_SCHEMA,
    SCOPE_PROPOSAL_OUTPUT_SCHEMA,
    ScopeProposalSemanticError,
    require_valid_scope_proposal_output,
)

__all__ = [
    "SCOPE_PROPOSAL_INPUT_SCHEMA",
    "SCOPE_PROPOSAL_OUTPUT_SCHEMA",
    "ScopeProposalSemanticError",
    "require_valid_scope_proposal_output",
]
