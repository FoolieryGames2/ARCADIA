from __future__ import annotations

from arcadia.aa_runtime.serializer import serialize_aae_call
from arcadia.contracts.aae.registry import MODE_TERM_MEANING, get_contract
from arcadia.contracts.schemas.r1 import R1_SCHEMAS


def test_term_meaning_model_message_contains_call_local_key_rules() -> None:
    contract = get_contract(MODE_TERM_MEANING)
    schemas = R1_SCHEMAS[MODE_TERM_MEANING]
    prepared = serialize_aae_call(
        contract,
        data_plane={
            "mode": MODE_TERM_MEANING,
            "raw_prompt": "I need milk.",
            "normalized_prompt": "I need milk.",
            "spell_uncertainties": [],
            "host_linguistic_map": {"source_spans": []},
            "r0_transcript_evidence": [],
        },
        input_schema=schemas.input,
        output_schema=schemas.output,
    )

    system_message = prepared.messages[0].content
    expected_rules = (
        "TERM_1, TERM_2, TERM_3",
        "REF_1, REF_2, REF_3",
        "temporary call-local aliases",
        "do not encode semantic meaning into a key or invent descriptive IDs",
        "Leave authoritative Txxx identifier allocation to the host after acceptance",
    )
    for rule in expected_rules:
        assert rule in system_message

    assert system_message.index("TERM_1, TERM_2, TERM_3") < system_message.index(
        "forbidden_responsibilities:"
    )
