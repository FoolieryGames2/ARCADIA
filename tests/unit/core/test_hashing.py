from __future__ import annotations

from io import BytesIO, StringIO
from pathlib import Path

import pytest

from arcadia.core.hashing import (
    SHA256_ALGORITHM,
    InvalidDigestError,
    InvalidHashInputError,
    Sha256Digest,
    parse_sha256_digest,
    sha256_bytes,
    sha256_canonical_json,
    sha256_chunks,
    sha256_file,
    sha256_stream,
    sha256_text,
    verify_sha256_bytes,
    verify_sha256_file,
)

EMPTY_SHA256 = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
ABC_SHA256 = "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"


def tagged(hex_digest: str) -> str:
    return f"sha256:{hex_digest}"


def test_known_sha256_vectors_and_typed_identity() -> None:
    empty = sha256_bytes(b"")
    abc = sha256_bytes(b"abc")

    assert empty == Sha256Digest.from_hex(EMPTY_SHA256)
    assert abc.value == tagged(ABC_SHA256)
    assert abc.hex_digest == ABC_SHA256
    assert abc.algorithm == SHA256_ALGORITHM
    assert str(abc) == abc.value
    assert parse_sha256_digest(abc.value) == abc


@pytest.mark.parametrize(
    "value",
    (
        ABC_SHA256,
        tagged(ABC_SHA256.upper()),
        f"SHA256:{ABC_SHA256}",
        f"sha-256:{ABC_SHA256}",
        f"sha256:{ABC_SHA256[:-1]}",
        f"sha256:{ABC_SHA256}0",
        "sha256:" + "g" * 64,
        " sha256:" + ABC_SHA256,
        "sha256:" + ABC_SHA256 + "\n",
    ),
)
def test_digest_parser_rejects_noncanonical_representations(value: str) -> None:
    with pytest.raises(InvalidDigestError):
        parse_sha256_digest(value)


def test_exact_utf8_text_is_hashed_without_normalization() -> None:
    composed = "é\n"
    decomposed = "e\u0301\r\n"

    assert sha256_text(composed) == sha256_bytes(composed.encode("utf-8"))
    assert sha256_text(composed) != sha256_text(decomposed)


def test_invalid_unicode_text_is_rejected() -> None:
    with pytest.raises(InvalidHashInputError, match="Unicode"):
        sha256_text("\ud800")


def test_canonical_json_hash_ignores_object_insertion_order_only() -> None:
    first = {"z": "☃", "a": [1, True, None]}
    second = {"a": [1, True, None], "z": "☃"}

    assert sha256_canonical_json(first) == sha256_canonical_json(second)
    assert sha256_canonical_json(first) == sha256_text(
        '{"a":[1,true,null],"z":"☃"}'
    )
    assert sha256_text('{"z":"☃","a":[1,true,null]}') != sha256_canonical_json(first)


def test_chunk_boundaries_do_not_change_digest() -> None:
    assert sha256_chunks([b"a", b"", b"b", b"c"]) == sha256_bytes(b"abc")
    assert sha256_chunks([]) == sha256_bytes(b"")


@pytest.mark.parametrize("bad_chunk", (bytearray(b"a"), memoryview(b"a"), "a"))
def test_chunks_reject_implicit_byte_coercion(bad_chunk: object) -> None:
    with pytest.raises(InvalidHashInputError):
        sha256_chunks([bad_chunk])  # type: ignore[list-item]


def test_stream_hashes_from_current_position() -> None:
    stream = BytesIO(b"prefix:abc")
    stream.seek(len(b"prefix:"))

    assert sha256_stream(stream, chunk_size=2) == sha256_bytes(b"abc")


@pytest.mark.parametrize("chunk_size", (0, -1, True, 1.5))
def test_stream_rejects_invalid_chunk_size(chunk_size: object) -> None:
    with pytest.raises(InvalidHashInputError):
        sha256_stream(BytesIO(), chunk_size=chunk_size)  # type: ignore[arg-type]


def test_stream_rejects_text_reads() -> None:
    with pytest.raises(InvalidHashInputError, match="bytes"):
        sha256_stream(StringIO("abc"))  # type: ignore[arg-type]


def test_file_hash_is_streamed_and_verifiable(tmp_path: Path) -> None:
    artifact = tmp_path / "artifact.bin"
    artifact.write_bytes(b"abc" * 10_000)
    expected = sha256_bytes(b"abc" * 10_000)

    assert sha256_file(artifact, chunk_size=7) == expected
    assert sha256_file(str(artifact)) == expected
    assert verify_sha256_file(artifact, expected)

    artifact.write_bytes(b"changed")
    assert not verify_sha256_file(artifact, expected)


def test_file_hash_rejects_non_files_and_ambiguous_path_types(tmp_path: Path) -> None:
    with pytest.raises(InvalidHashInputError, match="regular file"):
        sha256_file(tmp_path / "missing")
    with pytest.raises(InvalidHashInputError, match="str type or a Path"):
        sha256_file(123)  # type: ignore[arg-type]


def test_byte_verification_requires_typed_digest_and_detects_mismatch() -> None:
    expected = sha256_bytes(b"abc")

    assert verify_sha256_bytes(b"abc", expected)
    assert not verify_sha256_bytes(b"abd", expected)
    with pytest.raises(InvalidDigestError):
        verify_sha256_bytes(b"abc", expected.value)  # type: ignore[arg-type]


@pytest.mark.parametrize("payload", (bytearray(b"abc"), memoryview(b"abc"), "abc"))
def test_byte_hash_rejects_implicit_coercion(payload: object) -> None:
    with pytest.raises(InvalidHashInputError):
        sha256_bytes(payload)  # type: ignore[arg-type]
