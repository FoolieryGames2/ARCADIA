"""Verify the immutable ARCADIA v0.1 architecture-freeze authority bundle."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "manifests" / "architecture_freeze_v0_1_2026-09-04.json"
SUM_LINE = re.compile(r"^([0-9a-f]{64})  \./(.+)$")


@dataclass(frozen=True, slots=True)
class Result:
    name: str
    passed: bool
    detail: str


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate manifest key: {key}")
        result[key] = value
    return result


def load_manifest(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as source:
        value = json.load(source, object_pairs_hook=_reject_duplicate_keys)
    if type(value) is not dict:
        raise ValueError("architecture manifest must be an object")
    return value


def _safe_relative_path(value: str) -> PurePosixPath:
    if "\\" in value:
        raise ValueError(f"manifest path must use forward slashes: {value}")
    path = PurePosixPath(value)
    if path.is_absolute() or not path.parts or any(part in {"", ".", ".."} for part in path.parts):
        raise ValueError(f"unsafe manifest path: {value}")
    return path


def _workspace_path(workspace: Path, value: str) -> Path:
    relative = _safe_relative_path(value)
    return workspace.joinpath(*relative.parts)


def _parse_payload_sums(path: Path) -> tuple[tuple[str, str], ...]:
    rows: list[tuple[str, str]] = []
    seen: set[str] = set()
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        match = SUM_LINE.fullmatch(line)
        if match is None:
            raise ValueError(f"malformed checksum line {line_number}")
        expected, relative = match.groups()
        normalized = _safe_relative_path(relative).as_posix()
        if normalized in seen:
            raise ValueError(f"duplicate checksum path: {normalized}")
        seen.add(normalized)
        rows.append((expected, normalized))
    return tuple(rows)


def verify(
    *,
    workspace: Path = ROOT,
    manifest_path: Path = MANIFEST_PATH,
    source_archive: Path | None = None,
) -> tuple[Result, ...]:
    manifest = load_manifest(manifest_path)
    payload_manifest = manifest["payload_manifest"]
    authority_root_value = manifest["authority_root"]
    if type(authority_root_value) is not str or type(payload_manifest) is not dict:
        raise ValueError("authority_root and payload_manifest have invalid types")

    authority_root = _workspace_path(workspace, authority_root_value)
    sums_path = _workspace_path(workspace, payload_manifest["path"])
    sums_exists = sums_path.is_file()
    sums_hash = sha256(sums_path) if sums_exists else "missing"
    sums_size = sums_path.stat().st_size if sums_exists else -1
    sums_ok = (
        sums_exists
        and sums_hash == payload_manifest["sha256"]
        and sums_size == payload_manifest["size_bytes"]
    )
    results: list[Result] = [
        Result("payload_manifest", sums_ok, f"bytes={sums_size} sha256={sums_hash}")
    ]
    if not sums_ok:
        return tuple(results)

    rows = _parse_payload_sums(sums_path)
    expected_count = payload_manifest["entry_count"]
    count_ok = type(expected_count) is int and len(rows) == expected_count
    results.append(Result("payload_count", count_ok, f"{len(rows)}/{expected_count}"))

    failures: list[str] = []
    for expected, relative in rows:
        path = authority_root.joinpath(*PurePosixPath(relative).parts)
        if not path.is_file() or sha256(path) != expected:
            failures.append(relative)
    results.append(
        Result(
            "payload_hashes",
            not failures,
            f"{len(rows) - len(failures)}/{len(rows)} verified"
            + (f"; failed: {', '.join(failures[:3])}" if failures else ""),
        )
    )

    actual_files = {
        path.relative_to(authority_root).as_posix()
        for path in authority_root.rglob("*")
        if path.is_file()
    }
    expected_files = {relative for _, relative in rows}
    expected_files.add(sums_path.relative_to(authority_root).as_posix())
    extras = sorted(actual_files - expected_files)
    missing = sorted(expected_files - actual_files)
    exact = not extras and not missing
    detail = f"{len(actual_files)} files; exact declared set"
    if not exact:
        detail = f"extras={extras[:3]} missing={missing[:3]}"
    results.append(Result("authority_file_set", exact, detail))

    if source_archive is not None:
        source = manifest["source_archive"]
        archive_exists = source_archive.is_file()
        archive_size = source_archive.stat().st_size if archive_exists else -1
        archive_hash = sha256(source_archive) if archive_exists else "missing"
        archive_ok = (
            archive_exists
            and source_archive.name == source["filename"]
            and archive_size == source["size_bytes"]
            and archive_hash == source["sha256"]
        )
        results.append(
            Result(
                "source_archive",
                archive_ok,
                f"bytes={archive_size} sha256={archive_hash}",
            )
        )

    return tuple(results)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-archive", type=Path)
    args = parser.parse_args()
    try:
        results = verify(source_archive=args.source_archive)
    except (KeyError, OSError, TypeError, ValueError) as exc:
        print(f"FAIL  architecture_freeze  {exc}")
        return 1
    for result in results:
        standing = "PASS" if result.passed else "FAIL"
        print(f"{standing:4}  {result.name:20} {result.detail}")
    return 0 if results and all(result.passed for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
