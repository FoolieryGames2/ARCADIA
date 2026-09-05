from __future__ import annotations

from pathlib import Path

import pytest

from arcadia.aa_runtime.serializer import ModelMessage
from arcadia.core.canonical_json import JsonValue
from arcadia.lab.config import LabSettings, RuntimeIdentity
from arcadia.lab.runner import LabRuntimeError
from arcadia.lab.server import ResidentLlamaServer


def _settings() -> LabSettings:
    return LabSettings("direct", "resident", 2048, 64, 0.1, 9, 99, 18080, "T0")


def _runtime(tmp_path: Path) -> RuntimeIdentity:
    return RuntimeIdentity(
        "manifest",
        "CANDIDATE",
        "T0",
        tmp_path / "model",
        1,
        "a" * 64,
        tmp_path / "runtime",
        1,
        "b" * 64,
        "commit",
        tmp_path / "cuda",
    )


def _server_manifest(tmp_path: Path) -> None:
    path = tmp_path / "manifests" / "qwen3_resident_server_b10796_2026-09-04.json"
    path.parent.mkdir()
    path.write_text(
        '{"llama_cpp_commit":"commit","server":{"path":"server.exe",'
        '"sha256":"' + "c" * 64 + '","size_bytes":1},"server_implementation":{"path":"impl.dll",'
        '"sha256":"' + "d" * 64 + '","size_bytes":1}}',
        encoding="utf-8",
    )


def test_resident_completion_decodes_text_and_usage(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _server_manifest(tmp_path)
    server = ResidentLlamaServer(
        workspace=tmp_path, runtime=_runtime(tmp_path), settings=_settings()
    )
    response: dict[str, JsonValue] = {
        "choices": [{"message": {"content": "Ready"}}],
        "usage": {"prompt_tokens": 12, "completion_tokens": 2},
    }
    monkeypatch.setattr(server, "_request", lambda *_args, **_kwargs: response)

    result = server.complete((ModelMessage("user", "test"),))
    assert result.text == "Ready"
    assert result.prompt_tokens == 12
    assert result.completion_tokens == 2


def test_resident_token_count_uses_chat_template_endpoint(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _server_manifest(tmp_path)
    server = ResidentLlamaServer(
        workspace=tmp_path, runtime=_runtime(tmp_path), settings=_settings()
    )
    monkeypatch.setattr(
        server,
        "_request",
        lambda method, endpoint, payload, **kwargs: {"input_tokens": 17},
    )
    assert server.count_tokens((ModelMessage("user", "test"),)) == 17


def test_resident_server_rejects_an_already_occupied_port(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _server_manifest(tmp_path)
    server = ResidentLlamaServer(
        workspace=tmp_path, runtime=_runtime(tmp_path), settings=_settings()
    )
    monkeypatch.setattr(
        "arcadia.lab.server.verify_server_files",
        lambda *_args: (),
    )
    monkeypatch.setattr(server, "_port_is_occupied", lambda: True)

    with pytest.raises(LabRuntimeError, match="port 18080 is already in use"):
        server.__enter__()
