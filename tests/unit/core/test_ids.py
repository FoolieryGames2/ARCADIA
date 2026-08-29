from __future__ import annotations

from uuid import UUID

import pytest
from hypothesis import given
from hypothesis import strategies as st

from arcadia.core.ids import (
    AliasAllocator,
    AliasKind,
    CanonicalId,
    IdentifierError,
    ScopedAlias,
)


def test_host_allocates_unique_canonical_uuid4_ids() -> None:
    first = CanonicalId.new()
    second = CanonicalId.new()

    assert first != second
    assert first.value.version == 4
    assert str(first) == str(first.value)


@given(st.uuids().filter(lambda value: value.int != 0))
def test_canonical_uuid_round_trip(value: UUID) -> None:
    identifier = CanonicalId.parse(str(value))

    assert identifier.value == value
    assert str(identifier) == str(value)


@pytest.mark.parametrize(
    "text",
    (
        "00000000-0000-0000-0000-000000000000",
        "550E8400-E29B-41D4-A716-446655440000",
        "{550e8400-e29b-41d4-a716-446655440000}",
        "550e8400e29b41d4a716446655440000",
        "not-a-uuid",
        "５50e8400-e29b-41d4-a716-446655440000",
    ),
)
def test_noncanonical_or_illegal_uuid_text_is_rejected(text: str) -> None:
    with pytest.raises(IdentifierError):
        CanonicalId.parse(text)


def test_aliases_allocate_deterministically_within_scope() -> None:
    scope = CanonicalId.new()
    allocator = AliasAllocator(scope)

    assert allocator.allocate(AliasKind.REQUIREMENT).text == "R001"
    assert allocator.allocate(AliasKind.REQUIREMENT).text == "R002"
    assert allocator.allocate(AliasKind.WORK_ITEM).text == "W001"
    assert allocator.allocate(AliasKind.EXECUTION_RECEIPT).text == "REC001"
    assert allocator.allocate(AliasKind.SEMANTIC_ENTITY).text == "E000001"


def test_same_display_alias_in_different_scopes_is_not_same_identity() -> None:
    first = ScopedAlias(CanonicalId.new(), AliasKind.REQUIREMENT, 1)
    second = ScopedAlias(CanonicalId.new(), AliasKind.REQUIREMENT, 1)

    assert first.text == second.text == "R001"
    assert first != second


@pytest.mark.parametrize(
    ("text", "kind"),
    (
        ("r001", AliasKind.REQUIREMENT),
        ("R000", AliasKind.REQUIREMENT),
        ("R01", AliasKind.REQUIREMENT),
        ("R0001", AliasKind.REQUIREMENT),
        ("W001", AliasKind.REQUIREMENT),
        ("R００１", AliasKind.REQUIREMENT),
        ("R001/../../x", AliasKind.REQUIREMENT),
        ("E001", AliasKind.SEMANTIC_ENTITY),
        ("E000001", AliasKind.EVIDENCE),
    ),
)
def test_illegal_aliases_fail_closed(text: str, kind: AliasKind) -> None:
    with pytest.raises(IdentifierError):
        ScopedAlias.parse(text, kind=kind, scope_id=CanonicalId.new())


def test_alias_parse_requires_declared_namespace_and_scope() -> None:
    scope = CanonicalId.new()

    parsed = ScopedAlias.parse("TRQ042", kind=AliasKind.TOOL_REQUEST, scope_id=scope)

    assert parsed.scope_id == scope
    assert parsed.kind is AliasKind.TOOL_REQUEST
    assert parsed.ordinal == 42
    assert str(parsed) == "TRQ042"
