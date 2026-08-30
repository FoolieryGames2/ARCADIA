from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from arcadia.core.config import (
    ArcadiaConfig,
    AuthorityTier,
    ConfigurationError,
    RuntimeBackend,
    load_config,
    resolve_data_directory,
)

ROOT = Path(__file__).resolve().parents[3]


def test_workspace_runtime_config_is_strict_and_safe() -> None:
    config = load_config(ROOT / "configs" / "runtime.toml")

    assert config.config_version == 1
    assert config.project_version == "0.1-prototype"
    assert config.runtime.authority_tier is AuthorityTier.T0
    assert config.runtime.backend is RuntimeBackend.TEST_DOUBLE
    assert config.fast_path_enabled is False
    assert config.storage.require_fts5 is True
    assert resolve_data_directory(config, ROOT) == ROOT / "runtime-data"
    assert all(value == 0 for _, value in config.budgets)


def test_config_is_immutable() -> None:
    config = load_config(ROOT / "configs" / "runtime.toml")

    with pytest.raises(ValidationError):
        config.fast_path_enabled = True  # type: ignore[misc]


def test_unknown_config_field_is_rejected(tmp_path: Path) -> None:
    original = (ROOT / "configs" / "runtime.toml").read_text(encoding="utf-8")
    path = tmp_path / "runtime.toml"
    path.write_text(original + "\nundeclared_setting = true\n", encoding="utf-8")

    with pytest.raises(ConfigurationError, match="illegal runtime configuration"):
        load_config(path)


@pytest.mark.parametrize(
    "change",
    (
        ("config_version = 1", "config_version = 2"),
        ("config_version = 1", 'config_version = "1"'),
        ('data_dir = "runtime-data"', 'data_dir = "../outside"'),
        ('database_name = "arcadia.sqlite3"', 'database_name = "nested/arcadia.sqlite3"'),
        ("busy_timeout_ms = 5000", 'busy_timeout_ms = "5000"'),
        ("require_fts5 = true", "require_fts5 = 1"),
        ("max_model_calls = 0", "max_model_calls = -1"),
        ('backend = "test_double"', 'backend = "llama_cpp"'),
        ("serialized_manager_mutation = true", "serialized_manager_mutation = false"),
    ),
)
def test_illegal_config_values_fail_closed(tmp_path: Path, change: tuple[str, str]) -> None:
    original = (ROOT / "configs" / "runtime.toml").read_text(encoding="utf-8")
    path = tmp_path / "runtime.toml"
    path.write_text(original.replace(*change), encoding="utf-8")

    with pytest.raises(ConfigurationError):
        load_config(path)


def test_strict_model_rejects_coerced_boolean() -> None:
    payload = load_config(ROOT / "configs" / "runtime.toml").model_dump()
    payload["fast_path_enabled"] = "false"

    with pytest.raises(ValidationError):
        ArcadiaConfig.model_validate(payload)
