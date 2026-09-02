"""PRE-1 host-owned next-consumer routing policy.

The AAE contract registry defines the legal outgoing edges from each learned
specialist mode.  This policy validates those consumer identities, classifies
whether an edge ends at a deterministic host stage or another learned mode, and
requires the host to be the selector for every traversal.

It is intentionally *not* a recipe router.  Host controllers remain responsible
for deciding whether/when to traverse a legal edge and for building any later
learned call.  A model result can never authorize its own next destination.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from types import MappingProxyType
from typing import Final

from arcadia.contracts.aae import AAE_REGISTRY_PRE_V1


class NextConsumerPolicyStatus(StrEnum):
    """Lifecycle state for the PRE-1 next-consumer policy."""

    PRE_VERSION = "PRE_VERSION"
    FROZEN = "FROZEN"


class ConsumerKind(StrEnum):
    """Kind of host-owned routing destination."""

    HOST_STAGE = "HOST_STAGE"
    LEARNED_MODE = "LEARNED_MODE"


class RouteSelector(StrEnum):
    """Authority that attempted to choose the next route."""

    HOST = "HOST"
    MODEL_OUTPUT = "MODEL_OUTPUT"


@dataclass(frozen=True, slots=True)
class NextConsumerRef:
    """One validated consumer identity referenced by an AAE contract."""

    consumer_id: str
    kind: ConsumerKind
    target_specialist_mode_id: str | None = None


@dataclass(frozen=True, slots=True)
class NextConsumerPolicy:
    """Legal outgoing edges for one logical learned specialist mode."""

    policy_id: str
    policy_version: str
    status: NextConsumerPolicyStatus
    source_specialist_mode_id: str
    legal_consumers: tuple[NextConsumerRef, ...]
    host_selects_traversal: bool = True
    model_selected_routing_forbidden: bool = True


class NextConsumerPolicyError(ValueError):
    """A requested learned-boundary transition violates host routing policy."""


# These aliases are machine routing identities already present in the AAE registry
# whose destination is another learned specialist mode.  The alias is host-owned;
# the target mode is the canonical logical mode identity.
LEARNED_CONSUMER_TARGETS_PRE_V1: Final[Mapping[str, str]] = MappingProxyType(
    {
        "R1_TERM_MEANING": "TERM_MEANING",
        "R1_PROMPT_ANALYST": "PROMPT_ANALYSIS",
        "R1_INTENT_ORGANIZER": "INTENT_ORGANIZER",
        "R1_HOWARD_INTENT_COMMENT": "INTENT_COMMENT",
        "R2_HOWARD_CONTEXT_LANE": "CONTEXT_LANE_COMMENT",
        "R3_PLAN_COMPOSER": "PLAN_COMPOSITION",
        "R5_RECONCILIATION_COMPOSER": "RECONCILIATION_COMPOSITION",
        "R6_PERSISTENCE_COMPOSER": "PERSISTENCE_COMPOSITION",
        "R7_COMPLETION_COMPOSER": "COMPLETION_COMPOSITION",
        "R8_HOWARD_RESULT_FINAL": "RESULT_FINAL_COMPOSE",
    }
)


# Host-stage identities are deliberately registered independently from the AAE
# edges.  That makes a misspelling/new route in a contract fail closed instead of
# becoming valid merely because it appears in the same record being checked.
HOST_CONSUMER_IDS_PRE_V1: Final[frozenset[str]] = frozenset(
    {
        "R0_CONVERSATION_PACKET_FREEZER",
        "R0_HOST_RETRIEVER",
        "R0_HOST_SCOPE_VALIDATOR",
        "R1_HOST_ID_ALLOCATOR",
        "R1_HOST_INTENT_VALIDATOR",
        "R1_HOST_NORMALIZATION_VALIDATOR",
        "R1_PRESENTATION_SINK",
        "R2_CONTEXT",
        "R2_CONTEXT_REENTRY",
        "R2_HOST_CONTEXT_FREEZER",
        "R2_HOST_CONTEXT_ID_ALLOCATOR",
        "R2_HOST_CONTEXT_POINT_VALIDATOR",
        "R2_HOST_EVIDENCE_VALIDATOR",
        "R2_LANE_REPORT_FREEZER",
        "R3_DECISION",
        "R3_DECISION_REENTRY",
        "R3_HOST_ASSESSMENT_VALIDATOR",
        "R3_HOST_GRAPH_VALIDATOR",
        "R3_HOST_W_ID_ALLOCATOR",
        "R4_EXECUTION_HOST",
        "R5_HOST_EF_ALLOCATOR",
        "R5_HOST_EF_VALIDATOR",
        "R5_HOST_TRANSITION_VALIDATOR",
        "R6_ATOMIC_TRANSACTION_HOST",
        "R6_HOST_PA_VALIDATOR",
        "R6_HOST_PLAN_VALIDATOR",
        "R6_HOST_UUID_ALLOCATOR",
        "R6_PERSISTENCE",
        "R7_COMPLETION",
        "R7_FINAL_STANDING_PACKET_FREEZER",
        "R7_HOST_CA_ALLOCATOR",
        "R7_HOST_CA_VALIDATOR",
        "R7_HOST_COMPLETION_VALIDATOR",
        "R8_HOST_FINAL_VALIDATOR",
        "R8_HOST_RESULT_COMMENT_VALIDATOR",
        "R8_PUBLICATION_HOST",
        "R8_RESULT",
    }
)


def _resolve_consumer(consumer_id: str) -> NextConsumerRef:
    if consumer_id in LEARNED_CONSUMER_TARGETS_PRE_V1:
        target_mode = LEARNED_CONSUMER_TARGETS_PRE_V1[consumer_id]
        if target_mode not in AAE_REGISTRY_PRE_V1:
            raise RuntimeError(
                f"learned consumer {consumer_id} resolves to unknown mode {target_mode}"
            )
        return NextConsumerRef(
            consumer_id=consumer_id,
            kind=ConsumerKind.LEARNED_MODE,
            target_specialist_mode_id=target_mode,
        )

    if consumer_id in HOST_CONSUMER_IDS_PRE_V1:
        return NextConsumerRef(
            consumer_id=consumer_id,
            kind=ConsumerKind.HOST_STAGE,
            target_specialist_mode_id=None,
        )

    raise RuntimeError(f"unregistered next-consumer identity: {consumer_id}")


def _build_registry() -> Mapping[str, NextConsumerPolicy]:
    overlap = HOST_CONSUMER_IDS_PRE_V1.intersection(LEARNED_CONSUMER_TARGETS_PRE_V1)
    if overlap:
        raise RuntimeError(
            "next-consumer identities cannot be both host and learned: "
            + ", ".join(sorted(overlap))
        )

    policies: dict[str, NextConsumerPolicy] = {}
    for mode, contract in AAE_REGISTRY_PRE_V1.items():
        if len(contract.next_legal_consumers) != len(set(contract.next_legal_consumers)):
            raise RuntimeError(f"duplicate next consumer in {mode}")

        legal_consumers = tuple(
            _resolve_consumer(consumer_id) for consumer_id in contract.next_legal_consumers
        )
        policies[mode] = NextConsumerPolicy(
            policy_id=f"next_consumers.{mode.lower()}.pre1",
            policy_version="PRE-1",
            status=NextConsumerPolicyStatus.PRE_VERSION,
            source_specialist_mode_id=mode,
            legal_consumers=legal_consumers,
        )

    if set(policies) != set(AAE_REGISTRY_PRE_V1):
        raise RuntimeError("next-consumer policy registry must cover every AAE logical mode")

    return MappingProxyType(policies)


NEXT_CONSUMER_POLICY_REGISTRY_PRE_V1: Final[Mapping[str, NextConsumerPolicy]] = (
    _build_registry()
)


def get_next_consumer_policy(specialist_mode_id: str) -> NextConsumerPolicy:
    """Resolve the exact PRE-1 outgoing-edge policy for one learned mode."""

    try:
        return NEXT_CONSUMER_POLICY_REGISTRY_PRE_V1[specialist_mode_id]
    except KeyError as exc:
        raise KeyError(f"unknown next-consumer specialist mode: {specialist_mode_id}") from exc


def get_legal_next_consumers(specialist_mode_id: str) -> tuple[NextConsumerRef, ...]:
    """Return immutable legal outgoing edges; this does not choose a route."""

    return get_next_consumer_policy(specialist_mode_id).legal_consumers


def require_legal_next_consumer(
    source_specialist_mode_id: str,
    consumer_id: str,
    *,
    selected_by: RouteSelector,
) -> NextConsumerRef:
    """Fail closed unless the host selected an exact registry-authorized edge.

    Passing this gate confirms only routing legality.  It does not validate the
    source artifact, make a downstream call dispatchable, or bypass that target's
    schemas/trust/settings/runtime gates.
    """

    policy = get_next_consumer_policy(source_specialist_mode_id)

    if selected_by is not RouteSelector.HOST:
        raise NextConsumerPolicyError(
            "learned/model output may not choose A.R.C.A.D.I.A. routing"
        )

    for consumer in policy.legal_consumers:
        if consumer.consumer_id == consumer_id:
            return consumer

    raise NextConsumerPolicyError(
        f"illegal next consumer {consumer_id!r} for {source_specialist_mode_id}"
    )
