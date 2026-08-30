"""AAE contract registry primitives and pre-version registry definitions."""

from arcadia.contracts.aae.global_awareness import GLOBAL_AWARENESS_PRE_V1
from arcadia.contracts.aae.registry import AAE_REGISTRY_PRE_V1, get_contract
from arcadia.contracts.aae.types import AAEContractRecord

__all__ = [
    "AAEContractRecord",
    "AAE_REGISTRY_PRE_V1",
    "GLOBAL_AWARENESS_PRE_V1",
    "get_contract",
]
