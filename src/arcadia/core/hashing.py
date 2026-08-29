"""Host-owned SHA-256 hashing over exact or Canonical JSON V1 bytes."""

from __future__ import annotations

import hashlib
import hmac
import re
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO

from arcadia.core.canonical_json import JsonValue, canonical_json_dump_bytes

SHA256_ALGORITHM = "sha256"
SHA256_TAG = f"{SHA256_ALGORITHM}:"
SHA256_HEX_LENGTH = 64
DEFAULT_FILE_CHUNK_SIZE = 1024 * 1024

_SHA256_DIGEST_PATTERN = re.compile(r"sha256:[0-9a-f]{64}", flags=re.ASCII)


class HashingError(ValueError):
    """Base error for invalid hash inputs or identities."""


class InvalidDigestError(HashingError):
    """A digest does not use ARCADIA's exact tagged SHA-256 representation."""


class InvalidHashInputError(HashingError):
    """Input cannot be hashed without coercion or ambiguity."""


@dataclass(frozen=True, slots=True, order=True)
class Sha256Digest:
    """An immutable, canonical, algorithm-tagged SHA-256 digest."""

    value: str

    def __post_init__(self) -> None:
        if type(self.value) is not str or _SHA256_DIGEST_PATTERN.fullmatch(self.value) is None:
            raise InvalidDigestError(
                "digest must be 'sha256:' followed by 64 lowercase hexadecimal characters"
            )

    @classmethod
    def from_hex(cls, hex_digest: str) -> Sha256Digest:
        """Build a tagged digest from an exact lowercase SHA-256 hex value."""

        if type(hex_digest) is not str:
            raise InvalidDigestError("SHA-256 hexadecimal digest must be text")
        return cls(f"{SHA256_TAG}{hex_digest}")

    @property
    def algorithm(self) -> str:
        """Return the fixed algorithm identity."""

        return SHA256_ALGORITHM

    @property
    def hex_digest(self) -> str:
        """Return the 64-character lowercase digest without its algorithm tag."""

        return self.value[len(SHA256_TAG) :]

    def __str__(self) -> str:
        return self.value


def parse_sha256_digest(value: str) -> Sha256Digest:
    """Parse an exact canonical tagged SHA-256 digest."""

    return Sha256Digest(value)


def _finish(hasher: hashlib._Hash) -> Sha256Digest:
    return Sha256Digest.from_hex(hasher.hexdigest())


def sha256_bytes(payload: bytes) -> Sha256Digest:
    """Hash exact bytes without transformation."""

    if type(payload) is not bytes:
        raise InvalidHashInputError("byte hashing requires the exact bytes type")
    return Sha256Digest.from_hex(hashlib.sha256(payload).hexdigest())


def sha256_text(payload: str) -> Sha256Digest:
    """Hash exact UTF-8 text without Unicode or newline normalization."""

    if type(payload) is not str:
        raise InvalidHashInputError("text hashing requires the exact str type")
    try:
        encoded = payload.encode("utf-8", errors="strict")
    except UnicodeEncodeError as exc:
        raise InvalidHashInputError("text contains an invalid Unicode scalar") from exc
    return sha256_bytes(encoded)


def sha256_canonical_json(value: JsonValue) -> Sha256Digest:
    """Canonicalize a strict JSON value with V1, then hash its UTF-8 bytes."""

    return sha256_bytes(canonical_json_dump_bytes(value))


def sha256_chunks(chunks: Iterable[bytes]) -> Sha256Digest:
    """Hash an ordered stream of exact byte chunks without joining them in memory."""

    hasher = hashlib.sha256()
    try:
        iterator = iter(chunks)
    except TypeError as exc:
        raise InvalidHashInputError("chunks must be an iterable of bytes") from exc
    for chunk in iterator:
        if type(chunk) is not bytes:
            raise InvalidHashInputError("every hash chunk must use the exact bytes type")
        hasher.update(chunk)
    return _finish(hasher)


def sha256_stream(stream: BinaryIO, *, chunk_size: int = DEFAULT_FILE_CHUNK_SIZE) -> Sha256Digest:
    """Hash bytes read from the stream's current position through EOF."""

    if type(chunk_size) is not int or chunk_size <= 0:
        raise InvalidHashInputError("chunk_size must be a positive integer")

    hasher = hashlib.sha256()
    while True:
        chunk = stream.read(chunk_size)
        if type(chunk) is not bytes:
            raise InvalidHashInputError("binary stream read must return the exact bytes type")
        if not chunk:
            return _finish(hasher)
        hasher.update(chunk)


def sha256_file(path: str | Path, *, chunk_size: int = DEFAULT_FILE_CHUNK_SIZE) -> Sha256Digest:
    """Stream-hash the exact bytes of a regular file."""

    if type(path) is str:
        file_path = Path(path)
    elif isinstance(path, Path):
        file_path = path
    else:
        raise InvalidHashInputError("file path must use the exact str type or a Path instance")
    if not file_path.is_file():
        raise InvalidHashInputError(f"hash target is not a regular file: {file_path}")
    with file_path.open("rb") as stream:
        return sha256_stream(stream, chunk_size=chunk_size)


def verify_sha256_bytes(payload: bytes, expected: Sha256Digest) -> bool:
    """Constant-time verification of exact bytes against a typed digest."""

    if type(expected) is not Sha256Digest:
        raise InvalidDigestError("expected digest must be a Sha256Digest")
    actual = sha256_bytes(payload)
    return hmac.compare_digest(actual.value, expected.value)


def verify_sha256_file(
    path: str | Path,
    expected: Sha256Digest,
    *,
    chunk_size: int = DEFAULT_FILE_CHUNK_SIZE,
) -> bool:
    """Constant-time digest comparison after stream-hashing an exact file."""

    if type(expected) is not Sha256Digest:
        raise InvalidDigestError("expected digest must be a Sha256Digest")
    actual = sha256_file(path, chunk_size=chunk_size)
    return hmac.compare_digest(actual.value, expected.value)
