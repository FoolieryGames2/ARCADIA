"""Host-owned Recipe 0 continuation projection, prefetch, and packet freezing."""

from __future__ import annotations

from dataclasses import dataclass

from arcadia.contracts.aae.registry import MODE_SCOPE_PROPOSAL, MODE_SCOPE_VALIDATION
from arcadia.contracts.schemas.r0.scope_proposal import SCOPE_PROPOSAL_INPUT_SCHEMA
from arcadia.contracts.schemas.r0.scope_validation import (
    ScopeValidationSemanticError,
    require_valid_scope_validation_call_data,
    require_valid_scope_validation_output,
)
from arcadia.core.canonical_json import JsonValue
from arcadia.core.hashing import Sha256Digest, sha256_canonical_json, sha256_text
from arcadia.core.ids import CanonicalId
from arcadia.storage.transcript_repository import CompletedExchange, TranscriptRepository


def _frozen_exchange(exchange: CompletedExchange) -> dict[str, JsonValue]:
    return {
        "turn_uuid": str(exchange.turn.turn_id),
        "turn_index": exchange.turn.turn_ordinal,
        "user_message": exchange.user_entry.content,
        "final_response": exchange.assistant_entry.content,
        "user_message_hash": exchange.user_entry.content_hash.value,
        "final_response_hash": exchange.assistant_entry.content_hash.value,
    }


@dataclass(frozen=True, slots=True)
class ConversationPacket:
    turn_id: CanonicalId
    conversation_id: CanonicalId
    raw_user_prompt: str
    raw_prompt_hash: Sha256Digest
    transcript_commit_seq: int
    included_turns: tuple[dict[str, JsonValue], ...]
    unresolved_references: tuple[str, ...]
    scope_status: str
    packet_hash: Sha256Digest

    @classmethod
    def freeze(
        cls,
        *,
        turn_id: CanonicalId,
        conversation_id: CanonicalId,
        raw_user_prompt: str,
        transcript_commit_seq: int,
        included_turns: tuple[dict[str, JsonValue], ...],
        unresolved_references: tuple[str, ...],
        scope_status: str,
    ) -> ConversationPacket:
        value: dict[str, JsonValue] = {
            "conversation_uuid": str(conversation_id),
            "included_turns": list(included_turns),
            "raw_prompt_hash": sha256_text(raw_user_prompt).value,
            "raw_user_prompt": raw_user_prompt,
            "scope_status": scope_status,
            "transcript_commit_seq": transcript_commit_seq,
            "turn_uuid": str(turn_id),
            "unresolved_references": list(unresolved_references),
        }
        return cls(
            turn_id=turn_id,
            conversation_id=conversation_id,
            raw_user_prompt=raw_user_prompt,
            raw_prompt_hash=sha256_text(raw_user_prompt),
            transcript_commit_seq=transcript_commit_seq,
            included_turns=included_turns,
            unresolved_references=unresolved_references,
            scope_status=scope_status,
            packet_hash=sha256_canonical_json(value),
        )


@dataclass(frozen=True, slots=True)
class Recipe0ContinuationController:
    """Implements only the accepted open-continuation correction, without Intent authority."""

    transcript: TranscriptRepository

    def build_scope_proposal_call_data(
        self,
        *,
        turn_id: CanonicalId,
        conversation_id: CanonicalId,
        raw_user_prompt: str,
        host_policy_limits: dict[str, JsonValue],
    ) -> dict[str, JsonValue]:
        state = self.transcript.continuation_state_for_turn(turn_id=turn_id)
        call_data: dict[str, JsonValue] = {
            "mode": MODE_SCOPE_PROPOSAL,
            "turn_uuid": str(turn_id),
            "conversation_uuid": str(conversation_id),
            "raw_user_prompt": raw_user_prompt,
            "current_transcript_metadata": {
                "transcript_commit_seq": self.transcript.transcript_commit_seq(),
                "completed_exchange_count": self.transcript.completed_exchange_count(
                    conversation_id=conversation_id
                ),
                "continuation_state": state.to_value(),
            },
            "host_policy_limits": host_policy_limits,
        }
        SCOPE_PROPOSAL_INPUT_SCHEMA.require_valid(call_data)
        return call_data

    def build_open_continuation_validation_call_data(
        self,
        *,
        turn_id: CanonicalId,
        conversation_id: CanonicalId,
        raw_user_prompt: str,
        host_policy_limits: dict[str, JsonValue],
    ) -> dict[str, JsonValue] | None:
        exchange = self.transcript.load_continuation_exchange(turn_id=turn_id)
        if exchange is None:
            return None
        call_data: dict[str, JsonValue] = {
            "mode": MODE_SCOPE_VALIDATION,
            "turn_uuid": str(turn_id),
            "conversation_uuid": str(conversation_id),
            "raw_user_prompt": raw_user_prompt,
            "frozen_retrieved_turns": [_frozen_exchange(exchange)],
            "host_policy_limits": host_policy_limits,
        }
        require_valid_scope_validation_call_data(call_data)
        return call_data

    def freeze_open_continuation_packet(
        self,
        *,
        call_data: dict[str, JsonValue],
        validation_output: dict[str, JsonValue],
    ) -> ConversationPacket:
        require_valid_scope_validation_output(validation_output, call_data=call_data)
        status = validation_output["status"]
        assert type(status) is str
        if status not in {"SUFFICIENT", "SUFFICIENT_WITHOUT_HISTORY"}:
            raise ScopeValidationSemanticError(
                f"cannot freeze Conversation Packet from unresolved status {status}"
            )
        turn_id = CanonicalId.parse(str(call_data["turn_uuid"]))
        conversation_id = CanonicalId.parse(str(call_data["conversation_uuid"]))
        turns = call_data["frozen_retrieved_turns"]
        unresolved = validation_output["unresolved_references"]
        assert type(turns) is list
        assert type(unresolved) is list
        included_turns: list[dict[str, JsonValue]] = []
        for turn in turns:
            if type(turn) is not dict:
                raise ScopeValidationSemanticError("validated transcript turn is not an object")
            included_turns.append(turn)
        included = () if status == "SUFFICIENT_WITHOUT_HISTORY" else tuple(included_turns)
        packet = ConversationPacket.freeze(
            turn_id=turn_id,
            conversation_id=conversation_id,
            raw_user_prompt=str(call_data["raw_user_prompt"]),
            transcript_commit_seq=self.transcript.transcript_commit_seq(),
            included_turns=included,
            unresolved_references=tuple(str(item) for item in unresolved),
            scope_status=status,
        )
        self.transcript.consume_continuation(turn_id=turn_id)
        return packet
