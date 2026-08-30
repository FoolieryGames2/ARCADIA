from __future__ import annotations

from dataclasses import FrozenInstanceError, replace

import pytest

from arcadia.core.canonical_json import canonical_json_dumps
from arcadia.core.hashing import sha256_canonical_json, sha256_text
from arcadia.core.ids import CanonicalId
from arcadia.core.repair_policy import (
    REPAIR_POLICY_VERSION,
    RepairAttempt,
    RepairBasis,
    RepairExhaustedError,
    RepairFieldError,
    RepairIntegrityError,
    RepairPolicy,
    RepairSession,
)


def _basis(packet: dict[str, object] | None = None) -> RepairBasis:
    return RepairBasis.create(
        call_id=CanonicalId.new(),
        specialist_mode="intent.organize",
        inference_profile_id="qwen.intent.v1",
        inference_profile_hash=sha256_text("profile"),
        authoritative_packet={"requirements": ["keep exact facts"]} if packet is None else packet,
    )


def _error(code: str = "SCHEMA_REJECTION") -> dict[str, object]:
    return {
        "code": code,
        "issues": [{"instance_path": "/answer", "keyword": "required"}],
    }


def _attempt(session: RepairSession) -> tuple[RepairSession, RepairAttempt]:
    return session.authorize(
        previous_output={"wrong": True},
        validation_error=_error(),
    )


def test_policy_is_versioned_hashable_and_allows_zero_repairs() -> None:
    policy = RepairPolicy(max_repairs_per_call=0)

    assert policy.policy_version == REPAIR_POLICY_VERSION
    assert policy.policy_hash == sha256_canonical_json(policy.to_value())
    assert RepairSession.begin(policy=policy, basis=_basis()).exhausted


@pytest.mark.parametrize("limit", [-1, True, 1.5, "2"])
def test_policy_rejects_coerced_or_negative_limits(limit: object) -> None:
    with pytest.raises(RepairFieldError, match="nonnegative integer"):
        RepairPolicy(max_repairs_per_call=limit)


def test_policy_rejects_unknown_version() -> None:
    with pytest.raises(RepairFieldError, match="unsupported repair policy version"):
        RepairPolicy(max_repairs_per_call=2, policy_version=2)


def test_basis_snapshots_packet_and_binds_mode_and_profile() -> None:
    packet = {"requirements": ["original"]}
    basis = _basis(packet)
    basis_hash = basis.basis_hash
    packet["requirements"].append("later expansion")

    assert basis.packet_value() == {"requirements": ["original"]}
    assert basis.authoritative_packet_hash == sha256_canonical_json(basis.packet_value())
    assert basis.basis_hash == basis_hash
    assert basis.to_value()["specialist_mode"] == "intent.organize"
    assert basis.to_value()["inference_profile_id"] == "qwen.intent.v1"


@pytest.mark.parametrize("field", ["specialist_mode", "inference_profile_id"])
def test_basis_rejects_illegal_binding_tokens(field: str) -> None:
    values = {
        "call_id": CanonicalId.new(),
        "specialist_mode": "intent.organize",
        "inference_profile_id": "qwen.intent.v1",
        "inference_profile_hash": sha256_text("profile"),
        "authoritative_packet": {},
    }
    values[field] = "has space"

    with pytest.raises(RepairFieldError, match="canonical token"):
        RepairBasis.create(**values)


def test_basis_rejects_non_json_packet() -> None:
    with pytest.raises(RepairFieldError, match="strict JSON data model"):
        _basis({"bad": ()})


def test_basis_rejects_snapshot_hash_tampering() -> None:
    basis = _basis()

    with pytest.raises(RepairIntegrityError, match="does not match"):
        replace(basis, authoritative_packet_hash=sha256_text("wrong"))


def test_authorize_adds_only_failure_material_to_unchanged_basis() -> None:
    initial = RepairSession.begin(policy=RepairPolicy(2), basis=_basis())
    advanced, attempt = initial.authorize(
        previous_output="not even structured",
        validation_error=_error(),
    )

    assert initial.repairs_used == 0
    assert advanced.repairs_used == 1
    assert advanced.repairs_remaining == 1
    assert attempt.basis_hash == initial.basis.basis_hash
    assert attempt.call_id == initial.basis.call_id
    assert attempt.previous_output_value() == "not even structured"
    assert attempt.validation_error_value() == _error()
    assert attempt.requires_fresh_context
    assert attempt.requires_fresh_sampler


def test_each_repair_has_unique_uuid_contiguous_ordinal_and_predecessor() -> None:
    session = RepairSession.begin(policy=RepairPolicy(2), basis=_basis())
    session, first = _attempt(session)
    session, second = session.authorize(
        previous_output={"still": "wrong"}, validation_error=_error("SEMANTIC_REJECTION")
    )

    assert first.attempt_id != second.attempt_id
    assert first.repair_ordinal == 1
    assert first.previous_attempt_id is None
    assert second.repair_ordinal == 2
    assert second.previous_attempt_id == first.attempt_id
    assert session.repairs_used == 2
    assert session.exhausted


def test_repair_cap_is_aggregate_and_exhaustion_does_not_mutate_state() -> None:
    session = RepairSession.begin(policy=RepairPolicy(1), basis=_basis())
    session, _ = _attempt(session)
    before = session.to_value()

    with pytest.raises(RepairExhaustedError, match="repair cap exhausted"):
        _attempt(session)

    assert session.to_value() == before
    assert session.repairs_used == 1


def test_zero_cap_denies_first_repair() -> None:
    session = RepairSession.begin(policy=RepairPolicy(0), basis=_basis())

    with pytest.raises(RepairExhaustedError):
        _attempt(session)


@pytest.mark.parametrize("validation_error", [{}, [], "error", None])
def test_authorize_requires_nonempty_machine_error_object(validation_error: object) -> None:
    session = RepairSession.begin(policy=RepairPolicy(1), basis=_basis())

    with pytest.raises(RepairFieldError, match="nonempty machine error object"):
        session.authorize(previous_output={}, validation_error=validation_error)


def test_authorize_rejects_non_json_previous_output() -> None:
    session = RepairSession.begin(policy=RepairPolicy(1), basis=_basis())

    with pytest.raises(RepairFieldError, match="strict JSON data model"):
        session.authorize(previous_output={"bad": object()}, validation_error=_error())


def test_attempt_snapshots_and_hashes_exact_failure_material() -> None:
    output = {"answer": ["bad"]}
    error = _error()
    session = RepairSession.begin(policy=RepairPolicy(1), basis=_basis())
    session, attempt = session.authorize(
        previous_output=output,
        validation_error=error,
    )
    output["answer"].append("mutated")
    error["issues"].append({"later": True})

    assert attempt.previous_output_value() == {"answer": ["bad"]}
    assert attempt.validation_error_value() == _error()
    assert attempt.previous_output_hash == sha256_canonical_json({"answer": ["bad"]})
    assert attempt.validation_error_hash == sha256_canonical_json(_error())
    assert session.attempts == (attempt,)


def test_session_and_attempt_are_immutable() -> None:
    session = RepairSession.begin(policy=RepairPolicy(1), basis=_basis())
    session, attempt = _attempt(session)

    with pytest.raises(FrozenInstanceError):
        session.attempts = ()
    with pytest.raises(FrozenInstanceError):
        attempt.repair_ordinal = 2


def test_session_rejects_history_over_cap() -> None:
    session = RepairSession.begin(policy=RepairPolicy(2), basis=_basis())
    session, _ = _attempt(session)
    session, _ = _attempt(session)

    with pytest.raises(RepairIntegrityError, match="exceeds"):
        RepairSession(policy=RepairPolicy(1), basis=session.basis, attempts=session.attempts)


def test_session_rejects_wrong_call_basis_policy_ordinal_and_predecessor() -> None:
    session = RepairSession.begin(policy=RepairPolicy(2), basis=_basis())
    session, first = _attempt(session)

    mutations = [
        replace(first, call_id=CanonicalId.new()),
        replace(first, basis_hash=sha256_text("wrong basis")),
        replace(first, policy_hash=sha256_text("wrong policy")),
        replace(first, repair_ordinal=2, previous_attempt_id=CanonicalId.new()),
    ]
    for changed in mutations:
        with pytest.raises(RepairIntegrityError):
            RepairSession(policy=session.policy, basis=session.basis, attempts=(changed,))


def test_session_rejects_duplicate_attempt_uuid_and_broken_chain() -> None:
    session = RepairSession.begin(policy=RepairPolicy(2), basis=_basis())
    session, first = _attempt(session)
    session, second = _attempt(session)

    duplicate = replace(second, attempt_id=first.attempt_id, previous_attempt_id=first.attempt_id)
    broken = replace(second, previous_attempt_id=CanonicalId.new())

    with pytest.raises(RepairIntegrityError, match="unique"):
        RepairSession(policy=session.policy, basis=session.basis, attempts=(first, duplicate))
    with pytest.raises(RepairIntegrityError, match="predecessor"):
        RepairSession(policy=session.policy, basis=session.basis, attempts=(first, broken))


def test_attempt_rejects_tampered_failure_hashes_and_noncanonical_snapshots() -> None:
    session = RepairSession.begin(policy=RepairPolicy(1), basis=_basis())
    session, attempt = _attempt(session)

    with pytest.raises(RepairIntegrityError, match="previous output hash"):
        replace(attempt, previous_output_hash=sha256_text("wrong"))
    with pytest.raises(RepairIntegrityError, match="validation error hash"):
        replace(attempt, validation_error_hash=sha256_text("wrong"))
    with pytest.raises(RepairFieldError, match="Canonical JSON V1"):
        replace(attempt, previous_output_json='{ "wrong": true }')


def test_attempt_rejects_empty_validation_error_snapshot() -> None:
    session = RepairSession.begin(policy=RepairPolicy(1), basis=_basis())
    session, attempt = _attempt(session)
    empty_hash = sha256_canonical_json({})

    with pytest.raises(RepairFieldError, match="nonempty machine error object"):
        replace(attempt, validation_error_json="{}", validation_error_hash=empty_hash)


def test_attempt_uuid_must_differ_from_original_call_uuid() -> None:
    session = RepairSession.begin(policy=RepairPolicy(1), basis=_basis())
    session, attempt = _attempt(session)

    with pytest.raises(RepairIntegrityError, match="must differ"):
        replace(attempt, attempt_id=attempt.call_id)


def test_to_value_is_canonical_json_compatible_and_hash_bound() -> None:
    session = RepairSession.begin(policy=RepairPolicy(1), basis=_basis())
    session, attempt = _attempt(session)

    rendered = canonical_json_dumps(session.to_value())

    assert str(attempt.attempt_id) in rendered
    assert attempt.previous_output_hash.value in rendered
    assert attempt.validation_error_hash.value in rendered


def test_low_level_constructor_rejects_wrong_typed_hash() -> None:
    basis = _basis()

    with pytest.raises(RepairFieldError, match="Sha256Digest"):
        RepairBasis(
            call_id=basis.call_id,
            specialist_mode=basis.specialist_mode,
            inference_profile_id=basis.inference_profile_id,
            inference_profile_hash="sha256:" + "0" * 64,
            authoritative_packet_json=basis.authoritative_packet_json,
            authoritative_packet_hash=basis.authoritative_packet_hash,
        )
