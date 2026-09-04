from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path

import pytest

from arcadia.lab.config import LabSettings, RuntimeIdentity
from arcadia.lab.runner import LabRuntimeError, run_base_prompt, verify_runtime_files


def _settings() -> LabSettings:
    return LabSettings(
        context_tokens=2048,
        max_output_tokens=64,
        temperature=0.3,
        seed=7,
        gpu_layers=35,
        system_prompt="System boundary",
    )


def _identity(tmp_path: Path) -> RuntimeIdentity:
    model = tmp_path / "model.gguf"
    executable = tmp_path / "runtime" / "llama-completion.exe"
    cuda = tmp_path / "cuda"
    executable.parent.mkdir()
    cuda.mkdir()
    model.write_bytes(b"model")
    executable.write_bytes(b"runtime")
    (cuda / "cublas64_13.dll").write_bytes(b"cuda")
    return RuntimeIdentity(
        manifest_id="runtime-test",
        standing="CANDIDATE",
        authority_tier="T0",
        model_path=model,
        model_size_bytes=5,
        model_sha256=hashlib.sha256(b"model").hexdigest(),
        executable_path=executable,
        executable_size_bytes=7,
        executable_sha256=hashlib.sha256(b"runtime").hexdigest(),
        llama_commit="abc123",
        cuda_bin_path=cuda,
    )


def test_runtime_file_checks_verify_sizes_and_hashes(tmp_path: Path) -> None:
    checks = verify_runtime_files(_identity(tmp_path), full_model_hash=True)

    assert {check.name for check in checks} == {
        "model",
        "runtime",
        "cuda",
        "runtime_sha256",
        "model_sha256",
    }
    assert all(check.passed for check in checks)


def test_runner_uses_explicit_base_only_arguments(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    captured: tuple[str, ...] = ()

    def fake_run(arguments: tuple[str, ...], **_: object) -> subprocess.CompletedProcess[str]:
        nonlocal captured
        captured = arguments
        return subprocess.CompletedProcess(arguments, 0, "Arcadia answer [end of text]\n", "logs")

    monkeypatch.setattr(subprocess, "run", fake_run)
    response = run_base_prompt(_identity(tmp_path), _settings(), "Hello")

    assert response.text == "Arcadia answer"
    assert "-cnv" in captured
    assert "-st" in captured
    assert captured[captured.index("-ngl") + 1] == "35"
    assert captured[captured.index("--seed") + 1] == "7"
    assert "--lora" not in captured


def test_runner_fails_closed_on_nonzero_exit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def fake_run(arguments: tuple[str, ...], **_: object) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(arguments, 3, "", "CUDA failed")

    monkeypatch.setattr(subprocess, "run", fake_run)
    with pytest.raises(LabRuntimeError, match="CUDA failed"):
        run_base_prompt(_identity(tmp_path), _settings(), "Hello")


def test_runner_rejects_empty_model_output(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_run(arguments: tuple[str, ...], **_: object) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(arguments, 0, "[end of text]", "")

    monkeypatch.setattr(subprocess, "run", fake_run)
    with pytest.raises(LabRuntimeError, match="no visible output"):
        run_base_prompt(_identity(tmp_path), _settings(), "Hello")
