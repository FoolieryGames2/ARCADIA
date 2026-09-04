"""Process-owned loopback llama.cpp server for warm T0 experiments."""

from __future__ import annotations

import os
import subprocess
import time
import urllib.error
import urllib.request
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from types import TracebackType
from typing import TextIO

from arcadia.aa_runtime.serializer import ModelMessage
from arcadia.core.canonical_json import JsonValue, canonical_json_dumps, strict_json_loads
from arcadia.core.validation import StrictJsonSchema
from arcadia.lab.config import LabSettings, RuntimeIdentity
from arcadia.lab.runner import LabRuntimeError, RuntimeFileCheck, _sha256_file

SERVER_MANIFEST_NAME = "manifests/qwen3_resident_server_b10796_2026-09-04.json"


@dataclass(frozen=True, slots=True)
class ResidentServerIdentity:
    executable_path: Path
    executable_size_bytes: int
    executable_sha256: str
    implementation_path: Path
    implementation_size_bytes: int
    implementation_sha256: str
    llama_commit: str


@dataclass(frozen=True, slots=True)
class ServerResponse:
    text: str
    elapsed_seconds: float
    prompt_tokens: int
    completion_tokens: int


def _object(value: JsonValue, label: str) -> dict[str, JsonValue]:
    if type(value) is not dict:
        raise LabRuntimeError(f"{label} must be a JSON object")
    return value


def _integer(value: JsonValue, label: str) -> int:
    if type(value) is not int:
        raise LabRuntimeError(f"{label} must be an integer")
    return value


def _text(value: JsonValue, label: str) -> str:
    if type(value) is not str:
        raise LabRuntimeError(f"{label} must be text")
    return value


def load_server_identity(workspace: Path) -> ResidentServerIdentity:
    path = workspace / SERVER_MANIFEST_NAME
    try:
        manifest = _object(strict_json_loads(path.read_text(encoding="utf-8")), "manifest")
        server = _object(manifest["server"], "manifest.server")
        implementation = _object(
            manifest["server_implementation"], "manifest.server_implementation"
        )
        relative_path = _text(server["path"], "manifest.server.path")
        return ResidentServerIdentity(
            executable_path=workspace / Path(relative_path),
            executable_size_bytes=_integer(server["size_bytes"], "manifest.server.size_bytes"),
            executable_sha256=_text(server["sha256"], "manifest.server.sha256"),
            implementation_path=workspace
            / Path(_text(implementation["path"], "manifest.server_implementation.path")),
            implementation_size_bytes=_integer(
                implementation["size_bytes"], "manifest.server_implementation.size_bytes"
            ),
            implementation_sha256=_text(
                implementation["sha256"], "manifest.server_implementation.sha256"
            ),
            llama_commit=_text(manifest["llama_cpp_commit"], "manifest.llama_cpp_commit"),
        )
    except (OSError, UnicodeDecodeError, KeyError, ValueError) as exc:
        raise LabRuntimeError(f"cannot load resident server identity: {path}") from exc


def verify_server_files(workspace: Path, runtime: RuntimeIdentity) -> tuple[RuntimeFileCheck, ...]:
    identity = load_server_identity(workspace)
    checks: list[RuntimeFileCheck] = []
    for name, path, expected_size, expected_hash in (
        (
            "server",
            identity.executable_path,
            identity.executable_size_bytes,
            identity.executable_sha256,
        ),
        (
            "server_impl",
            identity.implementation_path,
            identity.implementation_size_bytes,
            identity.implementation_sha256,
        ),
    ):
        if not path.is_file():
            checks.append(RuntimeFileCheck(name, False, f"missing: {path}"))
            continue
        size = path.stat().st_size
        if size != expected_size:
            checks.append(RuntimeFileCheck(name, False, f"bytes={size}"))
            continue
        actual_hash = _sha256_file(path)
        checks.append(RuntimeFileCheck(name, actual_hash == expected_hash, actual_hash))
    checks.append(
        RuntimeFileCheck(
            "server_commit",
            identity.llama_commit == runtime.llama_commit,
            identity.llama_commit,
        )
    )
    return tuple(checks)


class ResidentLlamaServer:
    """Own one loopback server process and issue stateless completion requests."""

    def __init__(
        self,
        *,
        workspace: Path,
        runtime: RuntimeIdentity,
        settings: LabSettings,
        startup_timeout_seconds: float = 120.0,
    ) -> None:
        self._workspace = workspace
        self._runtime = runtime
        self._settings = settings
        self._startup_timeout_seconds = startup_timeout_seconds
        self._identity = load_server_identity(workspace)
        self._process: subprocess.Popen[str] | None = None
        self._log: TextIO | None = None
        self._base_url = f"http://127.0.0.1:{settings.server_port}"
        self.load_seconds = 0.0

    def __enter__(self) -> ResidentLlamaServer:
        server = self._identity.executable_path
        failures = [
            check
            for check in verify_server_files(self._workspace, self._runtime)
            if not check.passed
        ]
        if failures:
            detail = "; ".join(f"{check.name}: {check.detail}" for check in failures)
            raise LabRuntimeError(
                f"resident runtime readiness failed: {detail}; run prepare_qwen3_server.bat"
            )

        log_path = self._workspace / "runtime-data" / "llama-server.log"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        self._log = log_path.open("w", encoding="utf-8")
        environment = os.environ.copy()
        environment["PATH"] = os.pathsep.join(
            (
                str(self._runtime.cuda_bin_path),
                str(server.parent),
                environment.get("PATH", ""),
            )
        )
        arguments = (
            str(server),
            "-m",
            str(self._runtime.model_path),
            "-ngl",
            str(self._settings.gpu_layers),
            "-c",
            str(self._settings.context_tokens),
            "--host",
            "127.0.0.1",
            "--port",
            str(self._settings.server_port),
            "--parallel",
            "1",
            "--no-webui",
            "--no-slots",
        )
        started = time.perf_counter()
        try:
            self._process = subprocess.Popen(
                arguments,
                stdin=subprocess.DEVNULL,
                stdout=self._log,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                env=environment,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
            self._wait_until_ready()
        except BaseException:
            self.close()
            raise
        self.load_seconds = time.perf_counter() - started
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.close()

    def _wait_until_ready(self) -> None:
        deadline = time.monotonic() + self._startup_timeout_seconds
        while time.monotonic() < deadline:
            if self._process is not None and self._process.poll() is not None:
                raise LabRuntimeError(
                    f"resident runtime exited during startup with code {self._process.returncode}"
                )
            try:
                self._request("GET", "/health", None, timeout=1.0)
                return
            except LabRuntimeError:
                time.sleep(0.1)
        raise LabRuntimeError("resident runtime did not become ready before its timeout")

    def close(self) -> None:
        if self._process is not None and self._process.poll() is None:
            self._process.terminate()
            try:
                self._process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self._process.kill()
                self._process.wait(timeout=10)
        self._process = None
        if self._log is not None:
            self._log.close()
            self._log = None

    def complete(
        self,
        messages: Sequence[ModelMessage],
        *,
        output_schema: StrictJsonSchema | None = None,
        settings: LabSettings | None = None,
    ) -> ServerResponse:
        active_settings = self._settings if settings is None else settings
        request_messages: list[JsonValue] = [
            {"role": message.role, "content": message.content} for message in messages
        ]
        payload: dict[str, JsonValue] = {
            "cache_prompt": False,
            "max_tokens": active_settings.max_output_tokens,
            "messages": request_messages,
            "seed": active_settings.seed,
            "stream": False,
            "temperature": active_settings.temperature,
        }
        if output_schema is not None:
            payload["response_format"] = {
                "type": "json_schema",
                "json_schema": {"schema": output_schema.schema_value()},
            }
        started = time.perf_counter()
        response = self._request("POST", "/v1/chat/completions", payload, timeout=300.0)
        elapsed = time.perf_counter() - started
        body = _object(response, "chat response")
        choices = body.get("choices")
        if type(choices) is not list or len(choices) != 1:
            raise LabRuntimeError("chat response must contain exactly one choice")
        choice = _object(choices[0], "chat response choice")
        message = _object(choice.get("message"), "chat response message")
        content = _text(message.get("content"), "chat response content").strip()
        if not content:
            raise LabRuntimeError("resident runtime returned no visible output")
        usage = _object(body.get("usage"), "chat response usage")
        return ServerResponse(
            text=content,
            elapsed_seconds=elapsed,
            prompt_tokens=_integer(usage.get("prompt_tokens"), "usage.prompt_tokens"),
            completion_tokens=_integer(usage.get("completion_tokens"), "usage.completion_tokens"),
        )

    def count_tokens(self, messages: Sequence[ModelMessage]) -> int:
        request_messages: list[JsonValue] = [
            {"role": message.role, "content": message.content} for message in messages
        ]
        response = self._request(
            "POST",
            "/v1/chat/completions/input_tokens",
            {"messages": request_messages},
            timeout=30.0,
        )
        body = _object(response, "token count response")
        return _integer(body.get("input_tokens"), "token count response.input_tokens")

    def _request(
        self,
        method: str,
        endpoint: str,
        payload: dict[str, JsonValue] | None,
        *,
        timeout: float,
    ) -> JsonValue:
        data = None if payload is None else canonical_json_dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            self._base_url + endpoint,
            data=data,
            headers={"Content-Type": "application/json"},
            method=method,
        )
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                raw = response.read().decode("utf-8")
        except (OSError, UnicodeDecodeError, urllib.error.URLError) as exc:
            raise LabRuntimeError(f"resident runtime request failed: {exc}") from exc
        try:
            return strict_json_loads(raw)
        except ValueError as exc:
            raise LabRuntimeError("resident runtime returned malformed JSON") from exc
