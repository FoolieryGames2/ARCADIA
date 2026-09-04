"""Subprocess boundary for qualification-only Qwen3 base-model experiments."""

from __future__ import annotations

import hashlib
import os
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path

from arcadia.lab.config import LabSettings, RuntimeIdentity


class LabRuntimeError(RuntimeError):
    """The pinned local runtime could not produce a valid lab response."""


@dataclass(frozen=True, slots=True)
class RuntimeFileCheck:
    name: str
    passed: bool
    detail: str


@dataclass(frozen=True, slots=True)
class LabResponse:
    text: str
    elapsed_seconds: float
    return_code: int
    authority_tier: str
    model_sha256: str
    stderr_tail: str


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(8 * 1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def verify_runtime_files(
    identity: RuntimeIdentity, *, full_model_hash: bool = False
) -> tuple[RuntimeFileCheck, ...]:
    checks: list[RuntimeFileCheck] = []
    for name, path, expected_size in (
        ("model", identity.model_path, identity.model_size_bytes),
        ("runtime", identity.executable_path, identity.executable_size_bytes),
        ("cuda", identity.cuda_bin_path / "cublas64_13.dll", None),
    ):
        if not path.is_file():
            checks.append(RuntimeFileCheck(name, False, f"missing: {path}"))
            continue
        size = path.stat().st_size
        passed = expected_size is None or size == expected_size
        detail = str(path) if expected_size is None else f"bytes={size}"
        checks.append(RuntimeFileCheck(name, passed, detail))

    if identity.executable_path.is_file():
        actual = _sha256_file(identity.executable_path)
        checks.append(
            RuntimeFileCheck(
                "runtime_sha256",
                actual == identity.executable_sha256,
                actual,
            )
        )
    if full_model_hash and identity.model_path.is_file():
        actual = _sha256_file(identity.model_path)
        checks.append(RuntimeFileCheck("model_sha256", actual == identity.model_sha256, actual))
    return tuple(checks)


def _clean_output(output: str) -> str:
    cleaned = output.replace("[end of text]", "").strip()
    if not cleaned:
        raise LabRuntimeError("the model returned no visible output")
    return cleaned


def run_base_prompt(
    identity: RuntimeIdentity,
    settings: LabSettings,
    prompt: str,
    *,
    timeout_seconds: int = 300,
) -> LabResponse:
    if type(prompt) is not str or not prompt.strip():
        raise LabRuntimeError("prompt must be nonempty text")
    if len(prompt) > 65_536:
        raise LabRuntimeError("prompt must not exceed 65536 characters")
    checks = verify_runtime_files(identity)
    failures = [check for check in checks if not check.passed]
    if failures:
        detail = "; ".join(f"{check.name}: {check.detail}" for check in failures)
        raise LabRuntimeError(f"runtime readiness failed: {detail}")

    environment = os.environ.copy()
    runtime_directory = identity.executable_path.parent
    environment["PATH"] = os.pathsep.join(
        (str(identity.cuda_bin_path), str(runtime_directory), environment.get("PATH", ""))
    )
    arguments = (
        str(identity.executable_path),
        "-m",
        str(identity.model_path),
        "-ngl",
        str(settings.gpu_layers),
        "-c",
        str(settings.context_tokens),
        "-n",
        str(settings.max_output_tokens),
        "--seed",
        str(settings.seed),
        "--temp",
        format(settings.temperature, ".6g"),
        "-cnv",
        "-st",
        "--simple-io",
        "--no-display-prompt",
        "-sys",
        settings.system_prompt,
        "-p",
        prompt,
    )
    started = time.perf_counter()
    try:
        completed = subprocess.run(
            arguments,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=environment,
            timeout=timeout_seconds,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise LabRuntimeError(f"runtime launch failed: {exc}") from exc
    elapsed = time.perf_counter() - started
    stderr_tail = completed.stderr[-2000:].strip()
    if completed.returncode != 0:
        raise LabRuntimeError(
            f"runtime exited with code {completed.returncode}: {stderr_tail or 'no diagnostics'}"
        )
    return LabResponse(
        text=_clean_output(completed.stdout),
        elapsed_seconds=elapsed,
        return_code=completed.returncode,
        authority_tier=identity.authority_tier,
        model_sha256=identity.model_sha256,
        stderr_tail=stderr_tail,
    )
