from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime, timedelta, timezone

import pytest

from arcadia.core.artifact_envelope import (
    ARTIFACT_ENVELOPE_VERSION,
    ArtifactBasisRef,
    ArtifactEnvelope,
    ArtifactEnvelopeFieldError,
    ArtifactIntegrityError,
    RecipeId,
    canonical_utc_timestamp,
)
from arcadia.core.canonical_json import canonical_json_dumps
from arcadia.core.hashing import sha256_bytes
from arcadia.core.ids import AliasKind, CanonicalId, ScopedAlias

CREATED_AT = datetime(2026, 8, 29, 12, 34, 56, 123456, tzinfo=UTC)


def make_envelope(
    *,
    project_id: CanonicalId | None = None,
    turn_id: CanonicalId | None = None,
    payload: object | None = None,
    short_id: ScopedAlias | None = None,
    basis_refs: tuple[ArtifactBasisRef, ...] = (),
) -> ArtifactEnvelope:
    actual_turn_id = turn_id or CanonicalId.new()
    return ArtifactEnvelope.create(
        project_id=project_id or CanonicalId.new(),
        turn_id=actual_turn_id,
        recipe_id=RecipeId.INTENT,
        artifact_type="INTENT_PACKET",
        short_id=short_id,
        revision=1,
        project_version="0.1-prototype",
        contract_version="intent-contract-v1",
        schema_version="intent-schema-v1",
        recipe_version="recipe-r1-v0.1",
        registry_version="aae-registry-v1",
        runtime_identity_version="phase0-test-double-v1",
        created_at=CREATED_AT,
        basis_refs=basis_refs,
        payload={"requirements": []} if payload is None else payload,  # type: ignore[arg-type]
    )


def test_create_seals_complete_versioned_envelope() -> None:
    turn_id = CanonicalId.new()
    alias = ScopedAlias(scope_id=turn_id, kind=AliasKind.INTENT_ARTIFACT, ordinal=1)
    upstream = ArtifactBasisRef(
        artifact_id=CanonicalId.new(),
        revision=2,
        artifact_hash=sha256_bytes(b"upstream"),
    )

    envelope = make_envelope(turn_id=turn_id, short_id=alias, basis_refs=(upstream,))
    value = envelope.to_value()

    assert envelope.envelope_version == ARTIFACT_ENVELOPE_VERSION
    assert value["artifact_uuid"] == str(envelope.artifact_id)
    assert value["short_id"] == "I001"
    assert value["short_id_kind"] == AliasKind.INTENT_ARTIFACT.value
    assert value["created_at"] == "2026-08-29T12:34:56.123456Z"
    assert value["basis_refs"] == [upstream.to_value()]
    assert value["content_hash"] == envelope.content_hash.value
    assert value["artifact_hash"] == envelope.artifact_hash.value
    assert envelope.verify_integrity()


def test_round_trip_is_canonical_and_byte_stable() -> None:
    envelope = make_envelope(payload={"z": "☃", "a": [1, True, None]})
    rendered = envelope.to_json()

    assert rendered == canonical_json_dumps(envelope.to_value())
    assert ArtifactEnvelope.from_json(rendered) == envelope
    assert ArtifactEnvelope.from_bytes(rendered.encode("utf-8")) == envelope
    assert ArtifactEnvelope.from_json(rendered).to_json() == rendered


def test_payload_is_snapshotted_and_returned_as_a_fresh_value() -> None:
    payload = {"items": ["original"]}
    envelope = make_envelope(payload=payload)
    payload["items"].append("late mutation")

    first_read = envelope.payload
    assert first_read == {"items": ["original"]}
    assert isinstance(first_read, dict)
    first_read["items"].append("read mutation")  # type: ignore[union-attr]
    assert envelope.payload == {"items": ["original"]}
    assert envelope.verify_integrity()


def test_payload_and_metadata_tampering_are_detected() -> None:
    envelope = make_envelope()

    tampered_payload = envelope.to_value()
    tampered_payload["payload"] = {"requirements": ["fabricated"]}
    with pytest.raises(ArtifactIntegrityError, match="content_hash"):
        ArtifactEnvelope.from_value(tampered_payload)

    tampered_metadata = envelope.to_value()
    tampered_metadata["contract_version"] = "intent-contract-v2"
    with pytest.raises(ArtifactIntegrityError, match="artifact_hash"):
        ArtifactEnvelope.from_value(tampered_metadata)

    with pytest.raises(ArtifactIntegrityError, match="artifact_hash"):
        replace(envelope, artifact_hash=sha256_bytes(b"wrong"))


def test_unknown_missing_and_unsupported_version_fields_fail_closed() -> None:
    envelope = make_envelope()

    unknown = envelope.to_value()
    unknown["model_note"] = "trust me"
    with pytest.raises(ArtifactEnvelopeFieldError, match="unknown"):
        ArtifactEnvelope.from_value(unknown)

    missing = envelope.to_value()
    del missing["schema_version"]
    with pytest.raises(ArtifactEnvelopeFieldError, match="missing"):
        ArtifactEnvelope.from_value(missing)

    wrong_version = envelope.to_value()
    wrong_version["envelope_version"] = 2
    with pytest.raises(ArtifactEnvelopeFieldError, match="unsupported"):
        ArtifactEnvelope.from_value(wrong_version)

    with pytest.raises(ArtifactEnvelopeFieldError, match="unsupported"):
        replace(envelope, envelope_version=True)
    with pytest.raises(ArtifactEnvelopeFieldError, match="unsupported"):
        replace(envelope, envelope_version=1.0)  # type: ignore[arg-type]

    non_string_key: dict[object, object] = dict(envelope.to_value())
    non_string_key[1] = "fake field"
    with pytest.raises(ArtifactEnvelopeFieldError, match="field names"):
        ArtifactEnvelope.from_value(non_string_key)


def test_noncanonical_json_and_invalid_utf8_fail_before_envelope_acceptance() -> None:
    envelope = make_envelope()
    pretty = canonical_json_dumps(envelope.to_value()).replace(",", ", ", 1)

    with pytest.raises(ArtifactEnvelopeFieldError, match="Canonical"):
        ArtifactEnvelope.from_json(pretty)
    with pytest.raises(ArtifactEnvelopeFieldError, match="Canonical"):
        ArtifactEnvelope.from_bytes(pretty.encode())
    with pytest.raises(ArtifactEnvelopeFieldError, match="UTF-8"):
        ArtifactEnvelope.from_bytes(b"\xff")


@pytest.mark.parametrize(
    "artifact_type",
    ("intent_packet", "INTENT-PACKET", " INTENT_PACKET", "", "ÉVIDENCE"),
)
def test_artifact_type_is_a_bounded_ascii_authority_token(artifact_type: str) -> None:
    envelope = make_envelope()

    with pytest.raises(ArtifactEnvelopeFieldError, match="artifact_type"):
        replace(envelope, artifact_type=artifact_type)


@pytest.mark.parametrize(
    "field,value",
    (
        ("revision", 0),
        ("revision", True),
        ("project_version", ""),
        ("contract_version", "bad version"),
        ("schema_version", "é"),
        ("recipe_version", "../recipe"),
        ("registry_version", "registry/v1"),
        ("runtime_identity_version", "runtime\nv1"),
    ),
)
def test_revision_and_identity_versions_are_strict(field: str, value: object) -> None:
    envelope = make_envelope()

    with pytest.raises(ArtifactEnvelopeFieldError):
        replace(envelope, **{field: value})


def test_short_id_must_be_turn_scoped_and_kind_is_not_inferred() -> None:
    turn_id = CanonicalId.new()
    wrong_scope = ScopedAlias(
        scope_id=CanonicalId.new(), kind=AliasKind.INTENT_ARTIFACT, ordinal=1
    )
    with pytest.raises(ArtifactEnvelopeFieldError, match="scope"):
        make_envelope(turn_id=turn_id, short_id=wrong_scope)

    envelope = make_envelope(turn_id=turn_id)
    invalid_pair = envelope.to_value()
    invalid_pair["short_id"] = "I001"
    invalid_pair["short_id_kind"] = None
    with pytest.raises(ArtifactEnvelopeFieldError, match="both"):
        ArtifactEnvelope.from_value(invalid_pair)


def test_create_rejects_host_type_coercion_before_serialization() -> None:
    turn_id = CanonicalId.new()
    kwargs = {
        "project_id": CanonicalId.new(),
        "turn_id": turn_id,
        "recipe_id": RecipeId.INTENT,
        "artifact_type": "INTENT_PACKET",
        "revision": 1,
        "project_version": "0.1-prototype",
        "contract_version": "intent-contract-v1",
        "schema_version": "intent-schema-v1",
        "recipe_version": "recipe-r1-v0.1",
        "registry_version": "aae-registry-v1",
        "runtime_identity_version": "phase0-test-double-v1",
        "created_at": CREATED_AT,
        "payload": {},
    }

    with pytest.raises(ArtifactEnvelopeFieldError, match="recipe_id"):
        ArtifactEnvelope.create(**(kwargs | {"recipe_id": "R1"}))  # type: ignore[arg-type]
    with pytest.raises(ArtifactEnvelopeFieldError, match="short_id"):
        ArtifactEnvelope.create(**(kwargs | {"short_id": "I001"}))  # type: ignore[arg-type]
    with pytest.raises(ArtifactEnvelopeFieldError, match="basis_refs"):
        ArtifactEnvelope.create(**(kwargs | {"basis_refs": (object(),)}))  # type: ignore[arg-type]


def test_basis_refs_reject_duplicates_self_reference_and_malformed_fields() -> None:
    upstream = ArtifactBasisRef(
        artifact_id=CanonicalId.new(), revision=1, artifact_hash=sha256_bytes(b"upstream")
    )
    with pytest.raises(ArtifactEnvelopeFieldError, match="duplicates"):
        make_envelope(basis_refs=(upstream, upstream))

    envelope = make_envelope()
    self_ref = ArtifactBasisRef(
        artifact_id=envelope.artifact_id,
        revision=1,
        artifact_hash=envelope.artifact_hash,
    )
    with pytest.raises(ArtifactEnvelopeFieldError, match="cite itself"):
        replace(envelope, basis_refs=(self_ref,))

    malformed = envelope.to_value()
    malformed["basis_refs"] = [
        {
            "artifact_uuid": str(upstream.artifact_id),
            "revision": 0,
            "artifact_hash": upstream.artifact_hash.value,
        }
    ]
    with pytest.raises(ArtifactEnvelopeFieldError, match="revision"):
        ArtifactEnvelope.from_value(malformed)


def test_basis_reference_order_is_preserved_and_hash_significant() -> None:
    first = ArtifactBasisRef(CanonicalId.new(), 1, sha256_bytes(b"first"))
    second = ArtifactBasisRef(CanonicalId.new(), 1, sha256_bytes(b"second"))

    forward = make_envelope(basis_refs=(first, second))
    reverse_value = forward.to_value()
    reverse_value["basis_refs"] = [second.to_value(), first.to_value()]

    with pytest.raises(ArtifactIntegrityError, match="artifact_hash"):
        ArtifactEnvelope.from_value(reverse_value)


def test_timestamp_requires_real_utc_with_fixed_precision() -> None:
    assert canonical_utc_timestamp(CREATED_AT) == "2026-08-29T12:34:56.123456Z"

    with pytest.raises(ArtifactEnvelopeFieldError, match="aware"):
        canonical_utc_timestamp(datetime(2026, 8, 29))
    with pytest.raises(ArtifactEnvelopeFieldError, match="already use UTC"):
        canonical_utc_timestamp(
            datetime(2026, 8, 29, tzinfo=timezone(timedelta(hours=-4)))
        )

    envelope = make_envelope()
    impossible = envelope.to_value()
    impossible["created_at"] = "2026-02-30T12:00:00.000000Z"
    with pytest.raises(ArtifactEnvelopeFieldError, match="real UTC"):
        ArtifactEnvelope.from_value(impossible)
