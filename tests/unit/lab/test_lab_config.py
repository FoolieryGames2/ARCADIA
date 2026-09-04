from pathlib import Path

import pytest

from arcadia.lab.config import (
    LOCAL_SETTINGS_NAME,
    LabConfigError,
    load_lab_settings,
    reset_lab_settings,
    set_lab_setting,
)

DEFAULTS = """\
config_version = 1
context_tokens = 2048
max_output_tokens = 256
temperature = 0.2
seed = 42
gpu_layers = 99
system_prompt = "T0 only"
"""


def _workspace(tmp_path: Path) -> Path:
    config = tmp_path / "configs" / "lab.toml"
    config.parent.mkdir()
    config.write_text(DEFAULTS, encoding="utf-8")
    return tmp_path


def test_defaults_are_loaded_and_validated(tmp_path: Path) -> None:
    settings = load_lab_settings(_workspace(tmp_path))

    assert settings.context_tokens == 2048
    assert settings.max_output_tokens == 256
    assert settings.temperature == 0.2
    assert settings.system_prompt == "T0 only"


def test_setting_is_persisted_atomically_and_reset(tmp_path: Path) -> None:
    workspace = _workspace(tmp_path)

    updated = set_lab_setting(workspace, "temperature", "0.65")
    assert updated.temperature == 0.65
    assert load_lab_settings(workspace).temperature == 0.65
    assert (workspace / LOCAL_SETTINGS_NAME).is_file()

    restored = reset_lab_settings(workspace)
    assert restored.temperature == 0.2
    assert not (workspace / LOCAL_SETTINGS_NAME).exists()


def test_invalid_setting_does_not_replace_good_settings(tmp_path: Path) -> None:
    workspace = _workspace(tmp_path)
    set_lab_setting(workspace, "max_output_tokens", "500")

    with pytest.raises(LabConfigError, match="leave at least 128"):
        set_lab_setting(workspace, "context_tokens", "512")

    assert load_lab_settings(workspace).max_output_tokens == 500


def test_local_override_rejects_unknown_keys(tmp_path: Path) -> None:
    workspace = _workspace(tmp_path)
    local = workspace / LOCAL_SETTINGS_NAME
    local.parent.mkdir()
    local.write_text('{"surprise":true}', encoding="utf-8")

    with pytest.raises(LabConfigError, match="keys differ"):
        load_lab_settings(workspace)


@pytest.mark.parametrize(
    ("name", "value", "message"),
    (
        ("temperature", "warm", "requires a number"),
        ("gpu_layers", "many", "requires an integer"),
        ("unknown", "1", "unknown lab setting"),
    ),
)
def test_cli_setting_parser_rejects_bad_values(
    tmp_path: Path, name: str, value: str, message: str
) -> None:
    workspace = _workspace(tmp_path)
    with pytest.raises(LabConfigError, match=message):
        set_lab_setting(workspace, name, value)
