"""Verify the immutable inputs required by ARCADIA Gate 0."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import sqlite3
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "manifests" / "phase0_inputs.json"


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


def load_manifest() -> dict[str, Any]:
    with MANIFEST_PATH.open("r", encoding="utf-8") as source:
        value: dict[str, Any] = json.load(source)
    return value


def check_file(name: str, relative: str, expected_hash: str) -> Result:
    path = ROOT / relative
    if not path.is_file():
        return Result(name, False, f"missing: {relative}")
    actual = sha256(path)
    return Result(name, actual == expected_hash, actual)


def check_authority_files(manifest: dict[str, Any]) -> Result:
    authority = manifest["authority"]
    bundle = ROOT / authority["bundle_path"]
    sums = bundle / "SHA256SUMS.txt"
    failures: list[str] = []
    rows = [line for line in sums.read_text(encoding="utf-8").splitlines() if line.strip()]
    for line in rows:
        expected, relative = line.split("  ", 1)
        path = bundle / relative
        if not path.is_file() or sha256(path) != expected:
            failures.append(relative)
    detail = f"{len(rows) - len(failures)}/{len(rows)} authority files verified"
    if failures:
        detail += f"; failed: {', '.join(failures[:3])}"
    return Result("authority_bundle", not failures, detail)


def check_model(manifest: dict[str, Any]) -> Result:
    model = manifest["base_model"]
    path = ROOT / model["local_path"]
    if not path.is_file():
        return Result("base_model", False, f"missing: {model['local_path']}")
    size_ok = path.stat().st_size == model["size_bytes"]
    actual_hash = sha256(path)
    hash_ok = actual_hash == model["sha256"]
    return Result(
        "base_model",
        size_ok and hash_ok,
        f"bytes={path.stat().st_size} sha256={actual_hash}",
    )


def check_submodule(manifest: dict[str, Any]) -> Result:
    runtime = manifest["llama_cpp"]
    path = ROOT / runtime["submodule_path"]
    if not path.is_dir():
        return Result("llama_cpp_source", False, "submodule missing")
    completed = subprocess.run(
        ["git", "-C", str(path), "rev-parse", "HEAD"],
        check=False,
        capture_output=True,
        text=True,
    )
    actual = completed.stdout.strip()
    return Result("llama_cpp_source", completed.returncode == 0 and actual == runtime["commit"], actual)


def check_fts5() -> Result:
    try:
        with sqlite3.connect(":memory:") as connection:
            connection.execute("CREATE VIRTUAL TABLE probe USING fts5(content)")
    except sqlite3.Error as exc:
        return Result("sqlite_fts5", False, str(exc))
    return Result("sqlite_fts5", True, sqlite3.sqlite_version)


def check_cuda(manifest: dict[str, Any]) -> Result:
    expected = manifest["native_toolchain"]["cuda_toolkit_version"]
    nvcc = shutil.which("nvcc")
    if nvcc is None:
        configured_root = manifest["native_toolchain"].get("cuda_install_root")
        if configured_root:
            nvcc_path = Path(configured_root) / "bin" / "nvcc.exe"
        else:
            program_files = Path(os.environ.get("ProgramFiles", r"C:\Program Files"))
            nvcc_path = (
                program_files
                / "NVIDIA GPU Computing Toolkit"
                / "CUDA"
                / "v13.3"
                / "bin"
                / "nvcc.exe"
            )
        if not nvcc_path.is_file():
            return Result("cuda_toolkit", False, f"nvcc missing; expected {expected}")
        nvcc = str(nvcc_path)
    completed = subprocess.run(
        [nvcc, "--version"], check=False, capture_output=True, text=True
    )
    detail = completed.stdout.strip().splitlines()[-1]
    version_ok = "release 13.3" in completed.stdout
    return Result("cuda_toolkit", completed.returncode == 0 and version_ok, detail)


def check_library(manifest: dict[str, Any]) -> Result:
    artifacts = manifest["llama_cpp"].get("runtime_artifacts", [])
    if not artifacts:
        return Result("llama_runtime", False, "runtime_artifacts are not frozen")
    failures: list[str] = []
    for artifact in artifacts:
        path = ROOT / artifact["path"]
        if not path.is_file():
            failures.append(f"missing:{artifact['path']}")
            continue
        if path.stat().st_size != artifact["size_bytes"]:
            failures.append(f"size:{artifact['path']}")
            continue
        if sha256(path) != artifact["sha256"]:
            failures.append(f"hash:{artifact['path']}")
    detail = f"{len(artifacts) - len(failures)}/{len(artifacts)} artifacts verified"
    if failures:
        detail += f"; failed: {', '.join(failures[:3])}"
    return Result("llama_runtime", not failures, detail)


def verify() -> tuple[Result, ...]:
    manifest = load_manifest()
    return (
        check_file(
            "authority_manifest",
            manifest["authority"]["sha256_manifest_path"],
            manifest["authority"]["sha256_manifest_sha256"],
        ),
        check_authority_files(manifest),
        check_file(
            "requirements_lock",
            manifest["host"]["requirements_lock_path"],
            manifest["host"]["requirements_lock_sha256"],
        ),
        check_file(
            "runtime_config",
            manifest["host"]["runtime_config_path"],
            manifest["host"]["runtime_config_sha256"],
        ),
        check_fts5(),
        check_model(manifest),
        check_submodule(manifest),
        check_cuda(manifest),
        check_library(manifest),
    )


def main() -> int:
    results = verify()
    for result in results:
        standing = "PASS" if result.passed else "FAIL"
        print(f"{standing:4}  {result.name:20} {result.detail}")
    return 0 if all(result.passed for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
