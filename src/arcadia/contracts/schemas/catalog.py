"""Complete non-dispatchable PRE-1 schema catalog for all learned modes."""

from __future__ import annotations

from types import MappingProxyType
from typing import Final

from arcadia.contracts.aae.registry import MODE_SCOPE_PROPOSAL, MODE_SCOPE_VALIDATION
from arcadia.contracts.schemas.common import ModeSchemas
from arcadia.contracts.schemas.r0.scope_proposal import (
    SCOPE_PROPOSAL_INPUT_SCHEMA,
    SCOPE_PROPOSAL_OUTPUT_SCHEMA,
)
from arcadia.contracts.schemas.r0.scope_validation import (
    SCOPE_VALIDATION_INPUT_SCHEMA,
    SCOPE_VALIDATION_OUTPUT_SCHEMA,
)
from arcadia.contracts.schemas.r1 import R1_SCHEMAS
from arcadia.contracts.schemas.r2 import R2_SCHEMAS
from arcadia.contracts.schemas.r3 import R3_SCHEMAS
from arcadia.contracts.schemas.r5 import R5_SCHEMAS
from arcadia.contracts.schemas.r6 import R6_SCHEMAS
from arcadia.contracts.schemas.r7 import R7_SCHEMAS
from arcadia.contracts.schemas.r8 import R8_SCHEMAS

_R0_SCHEMAS: Final = {
    MODE_SCOPE_PROPOSAL: ModeSchemas(
        MODE_SCOPE_PROPOSAL, SCOPE_PROPOSAL_INPUT_SCHEMA, SCOPE_PROPOSAL_OUTPUT_SCHEMA
    ),
    MODE_SCOPE_VALIDATION: ModeSchemas(
        MODE_SCOPE_VALIDATION,
        SCOPE_VALIDATION_INPUT_SCHEMA,
        SCOPE_VALIDATION_OUTPUT_SCHEMA,
    ),
}

LEARNED_MODE_SCHEMAS: Final = MappingProxyType(
    {
        **_R0_SCHEMAS,
        **R1_SCHEMAS,
        **R2_SCHEMAS,
        **R3_SCHEMAS,
        **R5_SCHEMAS,
        **R6_SCHEMAS,
        **R7_SCHEMAS,
        **R8_SCHEMAS,
    }
)
