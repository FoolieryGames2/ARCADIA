"""Validated operator settings and pinned runtime discovery for the T0 lab."""

from __future__ import annotations

import os
import tempfile
import tomllib
from collections.abc import Mapping
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Final, cast

from arcadia.core.canonical_json import JsonValue, canonical_json_dumps, strict_json_loads

LAB_CONFIG_NAME: Final = "configs/lab.toml"
RUNTIME_MANIFEST_NAME: Final = "manifests/qwen3_runtime_candidate_b10796_q4_k_m_2026-09-04.json"
LOCAL_SETTINGS_NAME: Final = "runtime-data/lab_settings.json"
SETTING_NAMES: Final = (
    "entry_mode",
    "runtime_transport",
    "context_tokens",
    "max_output_tokens",
    "temperature",
    "seed",
    "gpu_layers",
    "server_port",
    "system_prompt",
)


class LabConfigError(ValueError):
    """Lab configuration is missing, malformed, or outside safe experiment bounds."""


@dataclass(frozen=True, slots=True)
class LabSettings:
    entry_mode: str
    runtime_transport: str
    context_tokens: int
    max_output_tokens: int
    temperature: float
    seed: int
    gpu_layers: int
    server_port: int
    system_prompt: str

    def __post_init__(self) -> None:
        if self.entry_mode not in {"direct", "recipe"}:
            raise LabConfigError("entry_mode must be direct or recipe")
        if self.runtime_transport not in {"process", "resident"}:
            raise LabConfigError("runtime_transport must be process or resident")
        if type(self.context_tokens) is not int or not 512 <= self.context_tokens <= 16_384:
            raise LabConfigError("context_tokens must be an integer from 512 through 16384")
        if type(self.max_output_tokens) is not int or not 1 <= self.max_output_tokens <= 2048:
            raise LabConfigError("max_output_tokens must be an integer from 1 through 2048")
        if self.max_output_tokens + 128 > self.context_tokens:
            raise LabConfigError("max_output_tokens must leave at least 128 context tokens free")
        if type(self.temperature) not in (int, float) or isinstance(self.temperature, bool):
            raise LabConfigError("temperature must be a number from 0 through 2")
        if not 0 <= float(self.temperature) <= 2:
            raise LabConfigError("temperature must be a number from 0 through 2")
        object.__setattr__(self, "temperature", float(self.temperature))
        if type(self.seed) is not int or not 0 <= self.seed <= 4_294_967_295:
            raise LabConfigError("seed must be an integer from 0 through 4294967295")
        if type(self.gpu_layers) is not int or not 0 <= self.gpu_layers <= 99:
            raise LabConfigError("gpu_layers must be an integer from 0 through 99")
        if type(self.server_port) is not int or not 1024 <= self.server_port <= 65_535:
            raise LabConfigError("server_port must be an integer from 1024 through 65535")
        if type(self.system_prompt) is not str or not self.system_prompt.strip():
            raise LabConfigError("system_prompt must be nonempty text")
        if len(self.system_prompt) > 4096:
            raise LabConfigError("system_prompt must not exceed 4096 characters")

    def to_value(self) -> dict[str, JsonValue]:
        return {
            "entry_mode": self.entry_mode,
            "runtime_transport": self.runtime_transport,
            "context_tokens": self.context_tokens,
            "max_output_tokens": self.max_output_tokens,
            "temperature": self.temperature,
            "seed": self.seed,
            "gpu_layers": self.gpu_layers,
            "server_port": self.server_port,
            "system_prompt": self.system_prompt,
        }


@dataclass(frozen=True, slots=True)
class RuntimeIdentity:
    manifest_id: str
    standing: str
    authority_tier: str
    model_path: Path
    model_size_bytes: int
    model_sha256: str
    executable_path: Path
    executable_size_bytes: int
    executable_sha256: str
    llama_commit: str
    cuda_bin_path: Path


def resolve_workspace(explicit: Path | None = None) -> Path:
    if explicit is not None:
        root = explicit.resolve()
        if not (root / LAB_CONFIG_NAME).is_file():
            raise LabConfigError(f"ARCADIA workspace is missing {LAB_CONFIG_NAME}: {root}")
        return root
    for candidate in (Path.cwd(), *Path.cwd().parents):
        if (candidate / LAB_CONFIG_NAME).is_file():
            return candidate
    package_root = Path(__file__).resolve().parents[3]
    if (package_root / LAB_CONFIG_NAME).is_file():
        return package_root
    raise LabConfigError("cannot locate the ARCADIA workspace")


def _exact_keys(payload: Mapping[str, object], expected: set[str], label: str) -> None:
    if set(payload) != expected:
        missing = sorted(expected - set(payload))
        unknown = sorted(set(payload) - expected)
        raise LabConfigError(f"{label} keys differ; missing={missing!r} unknown={unknown!r}")


def _require_int(value: object, label: str) -> int:
    if type(value) is not int:
        raise LabConfigError(f"{label} must be an integer")
    return value


def _require_number(value: object, label: str) -> float:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise LabConfigError(f"{label} must be a number")
    return float(value)


def _require_string(value: object, label: str) -> str:
    if type(value) is not str:
        raise LabConfigError(f"{label} must be text")
    return value


def _require_object(value: object, label: str) -> dict[str, JsonValue]:
    if type(value) is not dict:
        raise LabConfigError(f"{label} must be an object")
    return cast(dict[str, JsonValue], value)


def _require_array(value: object, label: str) -> list[JsonValue]:
    if type(value) is not list:
        raise LabConfigError(f"{label} must be an array")
    return cast(list[JsonValue], value)


def _settings_from_mapping(payload: Mapping[str, object], label: str) -> LabSettings:
    _exact_keys(payload, set(SETTING_NAMES), label)
    return LabSettings(
        entry_mode=_require_string(payload["entry_mode"], "entry_mode"),
        runtime_transport=_require_string(payload["runtime_transport"], "runtime_transport"),
        context_tokens=_require_int(payload["context_tokens"], "context_tokens"),
        max_output_tokens=_require_int(payload["max_output_tokens"], "max_output_tokens"),
        temperature=_require_number(payload["temperature"], "temperature"),
        seed=_require_int(payload["seed"], "seed"),
        gpu_layers=_require_int(payload["gpu_layers"], "gpu_layers"),
        server_port=_require_int(payload["server_port"], "server_port"),
        system_prompt=_require_string(payload["system_prompt"], "system_prompt"),
    )


def load_lab_settings(workspace: Path) -> LabSettings:
    try:
        raw = tomllib.loads((workspace / LAB_CONFIG_NAME).read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, tomllib.TOMLDecodeError) as exc:
        raise LabConfigError(f"cannot load {LAB_CONFIG_NAME}") from exc
    if type(raw) is not dict:
        raise LabConfigError("lab defaults must be a TOML table")
    _exact_keys(raw, {"config_version", *SETTING_NAMES}, "lab defaults")
    if raw.pop("config_version") != 1:
        raise LabConfigError("unsupported lab config_version")
    settings = _settings_from_mapping(raw, "lab defaults")

    local_path = workspace / LOCAL_SETTINGS_NAME
    if not local_path.exists():
        return settings
    try:
        override = strict_json_loads(local_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, ValueError) as exc:
        raise LabConfigError(f"cannot load local lab settings: {local_path}") from exc
    if type(override) is not dict:
        raise LabConfigError("local lab settings must be a JSON object")
    return _settings_from_mapping(override, "local lab settings")


def _parse_setting(name: str, value: str) -> int | float | str:
    if name in {
        "context_tokens",
        "max_output_tokens",
        "seed",
        "gpu_layers",
        "server_port",
    }:
        try:
            return int(value)
        except ValueError as exc:
            raise LabConfigError(f"{name} requires an integer") from exc
    if name == "temperature":
        try:
            return float(value)
        except ValueError as exc:
            raise LabConfigError("temperature requires a number") from exc
    if name in {"entry_mode", "runtime_transport", "system_prompt"}:
        return value
    raise LabConfigError(f"unknown lab setting: {name}")


def _save_settings(path: Path, settings: LabSettings) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = canonical_json_dumps(settings.to_value()) + "\n"
    temporary_name: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", newline="\n", dir=path.parent, delete=False
        ) as handle:
            temporary_name = handle.name
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_name, path)
    finally:
        if temporary_name is not None:
            Path(temporary_name).unlink(missing_ok=True)


def set_lab_setting(workspace: Path, name: str, raw_value: str) -> LabSettings:
    settings = load_lab_settings(workspace)
    parsed = _parse_setting(name, raw_value)
    if name == "context_tokens":
        assert type(parsed) is int
        updated = replace(settings, context_tokens=parsed)
    elif name == "max_output_tokens":
        assert type(parsed) is int
        updated = replace(settings, max_output_tokens=parsed)
    elif name == "temperature":
        assert type(parsed) is float
        updated = replace(settings, temperature=parsed)
    elif name == "seed":
        assert type(parsed) is int
        updated = replace(settings, seed=parsed)
    elif name == "gpu_layers":
        assert type(parsed) is int
        updated = replace(settings, gpu_layers=parsed)
    elif name == "server_port":
        assert type(parsed) is int
        updated = replace(settings, server_port=parsed)
    elif name == "entry_mode" and type(parsed) is str:
        updated = replace(settings, entry_mode=parsed)
    elif name == "runtime_transport" and type(parsed) is str:
        updated = replace(settings, runtime_transport=parsed)
    elif name == "system_prompt" and type(parsed) is str:
        updated = replace(settings, system_prompt=parsed)
    else:  # pragma: no cover - _parse_setting rejects this state first
        raise LabConfigError(f"invalid parsed lab setting: {name}")
    _save_settings(workspace / LOCAL_SETTINGS_NAME, updated)
    return updated


def reset_lab_settings(workspace: Path) -> LabSettings:
    (workspace / LOCAL_SETTINGS_NAME).unlink(missing_ok=True)
    return load_lab_settings(workspace)


def load_runtime_identity(workspace: Path) -> RuntimeIdentity:
    try:
        manifest = strict_json_loads(
            (workspace / RUNTIME_MANIFEST_NAME).read_text(encoding="utf-8")
        )
    except (OSError, UnicodeDecodeError, ValueError) as exc:
        raise LabConfigError(f"cannot load {RUNTIME_MANIFEST_NAME}") from exc
    if type(manifest) is not dict:
        raise LabConfigError("runtime manifest must be a JSON object")
    try:
        conversion = _require_object(manifest["conversion"], "conversion")
        llama_cpp = _require_object(manifest["llama_cpp"], "llama_cpp")
        runtime_files = _require_array(manifest["runtime_files"], "runtime_files")
        candidate = _require_object(conversion["candidate"], "conversion.candidate")
        executable = next(
            _require_object(item, "runtime_files item")
            for item in runtime_files
            if type(item) is dict and item.get("name") == "llama-completion.exe"
        )
        program_files = Path(os.environ.get("ProgramFiles", r"C:\Program Files"))
        return RuntimeIdentity(
            manifest_id=_require_string(manifest["manifest_id"], "manifest_id"),
            standing=_require_string(manifest["standing"], "standing"),
            authority_tier=_require_string(manifest["runtime_authority"], "runtime_authority"),
            model_path=workspace
            / "models"
            / "qwen3-4b-instruct-2507"
            / _require_string(candidate["filename"], "candidate.filename"),
            model_size_bytes=_require_int(candidate["size_bytes"], "candidate.size_bytes"),
            model_sha256=_require_string(candidate["sha256"], "candidate.sha256"),
            executable_path=workspace
            / "build"
            / "qwen3-runtime-b10796"
            / "build"
            / "bin"
            / "Release"
            / "llama-completion.exe",
            executable_size_bytes=_require_int(
                executable["size_bytes"], "runtime executable.size_bytes"
            ),
            executable_sha256=_require_string(executable["sha256"], "runtime executable.sha256"),
            llama_commit=_require_string(llama_cpp["commit"], "llama_cpp.commit"),
            cuda_bin_path=program_files
            / "NVIDIA GPU Computing Toolkit"
            / "CUDA"
            / "v13.3"
            / "bin"
            / "x64",
        )
    except (KeyError, StopIteration, TypeError, ValueError) as exc:
        raise LabConfigError("runtime manifest is missing required candidate identity") from exc
