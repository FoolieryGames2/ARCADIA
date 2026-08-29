"""Strict, versioned loading for the single ARCADIA runtime configuration."""

from __future__ import annotations

import tomllib
from enum import StrEnum
from pathlib import Path, PurePath
from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StrictBool,
    StrictFloat,
    StrictInt,
    StrictStr,
    ValidationError,
    field_validator,
    model_validator,
)


class ConfigurationError(ValueError):
    """Raised when the runtime configuration is missing, malformed, or illegal."""


class EnvironmentName(StrEnum):
    DEVELOPMENT = "development"
    TEST = "test"
    QUALIFICATION = "qualification"
    PROTOTYPE = "prototype"


class AuthorityTier(StrEnum):
    T0 = "T0"
    T1 = "T1"
    T2 = "T2"
    T3 = "T3"
    T4 = "T4"
    T5 = "T5"
    T6 = "T6"


class RuntimeBackend(StrEnum):
    TEST_DOUBLE = "test_double"
    LLAMA_CPP = "llama_cpp"


class StrictConfigModel(BaseModel):
    """Base for immutable configuration sections with no accidental fields."""

    model_config = ConfigDict(extra="forbid", frozen=True)


class StorageConfig(StrictConfigModel):
    data_dir: StrictStr = Field(min_length=1, max_length=240)
    database_name: StrictStr = Field(min_length=1, max_length=128)
    busy_timeout_ms: StrictInt = Field(gt=0, le=120_000)
    require_fts5: StrictBool

    @field_validator("data_dir")
    @classmethod
    def validate_data_dir(cls, value: str) -> str:
        path = PurePath(value)
        if path.is_absolute() or ".." in path.parts:
            raise ValueError("data_dir must be a workspace-relative path without '..'")
        return value

    @field_validator("database_name")
    @classmethod
    def validate_database_name(cls, value: str) -> str:
        if PurePath(value).name != value or not value.endswith(".sqlite3"):
            raise ValueError("database_name must be a plain .sqlite3 filename")
        return value

    @field_validator("require_fts5")
    @classmethod
    def require_fts5_enabled(cls, value: bool) -> bool:
        if not value:
            raise ValueError("FTS5 is required by the frozen v0.1 host contract")
        return value


class RuntimeConfig(StrictConfigModel):
    authority_tier: AuthorityTier
    backend: RuntimeBackend
    base_model_path: StrictStr = Field(max_length=1024)
    max_hot_adapters: StrictInt = Field(ge=0, le=100)
    standard_active_adapters: StrictInt = Field(ge=1, le=1)
    standard_adapter_scale: StrictFloat = Field(ge=1.0, le=1.0)
    serialized_manager_mutation: StrictBool

    @model_validator(mode="after")
    def require_model_for_real_backend(self) -> RuntimeConfig:
        if self.backend is RuntimeBackend.LLAMA_CPP and not self.base_model_path:
            raise ValueError("base_model_path is required for the llama_cpp backend")
        if not self.serialized_manager_mutation:
            raise ValueError("v0.1 requires serialized manager mutation")
        return self


class BudgetConfig(StrictConfigModel):
    """Finite aggregate ceilings; zero explicitly denies that class of work."""

    max_model_calls: StrictInt = Field(ge=0)
    max_repairs_per_call: StrictInt = Field(ge=0)
    max_reentries: StrictInt = Field(ge=0)
    max_history_expansions: StrictInt = Field(ge=0)
    max_context_retrieval_expansions: StrictInt = Field(ge=0)
    max_decision_work_items: StrictInt = Field(ge=0)
    max_reconciliation_discovery_depth: StrictInt = Field(ge=0)
    max_side_effect_retries: StrictInt = Field(ge=0)
    max_compensations: StrictInt = Field(ge=0)
    max_total_model_input_tokens: StrictInt = Field(ge=0)
    max_total_model_output_tokens: StrictInt = Field(ge=0)


class TracingConfig(StrictConfigModel):
    enabled: StrictBool
    raw_trace_enabled: StrictBool
    raw_trace_retention_days: StrictInt = Field(ge=1, le=3650)
    training_export_enabled: StrictBool


class ArcadiaConfig(StrictConfigModel):
    config_version: Literal[1]
    project_version: Literal["0.1-prototype"]
    environment: EnvironmentName
    fast_path_enabled: StrictBool
    storage: StorageConfig
    runtime: RuntimeConfig
    budgets: BudgetConfig
    tracing: TracingConfig


def load_config(path: Path) -> ArcadiaConfig:
    """Load one TOML source and reject all malformed or undeclared settings."""

    try:
        payload = path.read_bytes()
    except OSError as exc:
        raise ConfigurationError(f"cannot read runtime configuration: {path}") from exc
    try:
        decoded = tomllib.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, tomllib.TOMLDecodeError) as exc:
        raise ConfigurationError(f"invalid TOML runtime configuration: {path}") from exc
    try:
        return ArcadiaConfig.model_validate(decoded)
    except ValidationError as exc:
        raise ConfigurationError(f"illegal runtime configuration: {path}: {exc}") from exc


def resolve_data_directory(config: ArcadiaConfig, workspace_root: Path) -> Path:
    """Resolve the validated relative data directory beneath a known workspace root."""

    root = workspace_root.resolve()
    resolved = (root / config.storage.data_dir).resolve()
    if not resolved.is_relative_to(root):
        raise ConfigurationError("resolved data directory escapes the workspace root")
    return resolved
