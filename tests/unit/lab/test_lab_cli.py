from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest

import arcadia.__main__ as cli
from arcadia.lab import LabResponse, LabSettings, RuntimeIdentity


def _settings() -> LabSettings:
    return LabSettings("direct", "process", 2048, 128, 0.2, 42, 99, 18080, "T0 test")


def _identity(tmp_path: Path) -> RuntimeIdentity:
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


def test_one_shot_run_prints_arcadia_and_t0_standing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(cli, "resolve_workspace", lambda _: tmp_path)
    monkeypatch.setattr(cli, "load_lab_settings", lambda _: _settings())
    monkeypatch.setattr(cli, "load_runtime_identity", lambda _: _identity(tmp_path))
    monkeypatch.setattr(
        cli,
        "run_base_prompt",
        lambda *_: LabResponse("Hello", 1.25, 0, "T0", "a" * 64, ""),
    )

    assert cli.main(["run", "Say hello"]) == 0
    output = capsys.readouterr().out
    assert "ARCADIA>" in output
    assert "Hello" in output
    assert "T0 BASE_ONLY" in output


def test_command_line_overrides_are_not_persisted(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    observed: list[LabSettings] = []
    monkeypatch.setattr(cli, "resolve_workspace", lambda _: tmp_path)
    monkeypatch.setattr(cli, "load_lab_settings", lambda _: _settings())
    monkeypatch.setattr(cli, "load_runtime_identity", lambda _: _identity(tmp_path))

    def fake_run(_: RuntimeIdentity, settings: LabSettings, __: str) -> LabResponse:
        observed.append(settings)
        return LabResponse("ok", 0.1, 0, "T0", "a" * 64, "")

    monkeypatch.setattr(cli, "run_base_prompt", fake_run)
    assert cli.main(["run", "test", "--temperature", "0.7", "--seed", "9"]) == 0
    assert observed[0].temperature == 0.7
    assert observed[0].seed == 9


def test_interactive_quit_does_not_launch_model(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(cli, "resolve_workspace", lambda _: tmp_path)
    monkeypatch.setattr(cli, "load_lab_settings", lambda _: _settings())
    monkeypatch.setattr(cli, "load_runtime_identity", lambda _: _identity(tmp_path))
    monkeypatch.setattr("builtins.input", lambda _: "/quit")
    monkeypatch.setattr(cli, "run_base_prompt", lambda *_: pytest.fail("model was launched"))

    assert cli.main(["run"]) == 0
    output = capsys.readouterr().out
    assert "T0 BASE_ONLY_TEST_MODE" in output
    assert "Lab closed." in output


def test_in_session_mode_command_switches_without_reaching_model(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    settings = _settings()
    inputs = iter(("--mode recipe", "/status", "/quit"))
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    monkeypatch.setattr(
        cli,
        "set_lab_setting",
        lambda _workspace, _name, value: replace(settings, entry_mode=value),
    )
    monkeypatch.setattr(cli, "run_base_prompt", lambda *_: pytest.fail("model was launched"))

    result = cli._interactive_loop(
        tmp_path,
        _identity(tmp_path),
        settings,
        metrics=False,
        server=None,
    )

    assert result.code == 0
    output = capsys.readouterr().out
    assert "Mode changed to recipe." in output
    assert "Implemented recipe span: R0" in output


def test_explicit_in_session_routes_do_not_change_the_saved_default(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    settings = replace(_settings(), runtime_transport="resident")
    inputs = iter(("/recipe inspect this", "/direct explain this", "/quit"))
    routed: list[tuple[str, str]] = []
    server = object()
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    monkeypatch.setattr(
        cli,
        "_run_recipe_slice",
        lambda _server, _identity, _settings, prompt: routed.append(("recipe", prompt)),
    )
    monkeypatch.setattr(
        cli,
        "_run_direct_resident",
        lambda _server, _identity, _settings, prompt: (
            routed.append(("direct", prompt))
            or LabResponse("ok", 0.1, 0, "T0", "a" * 64, "")
        ),
    )

    result = cli._interactive_loop(
        tmp_path,
        _identity(tmp_path),
        settings,
        metrics=False,
        server=server,  # type: ignore[arg-type]
    )

    assert result.settings.entry_mode == "direct"
    assert routed == [("recipe", "inspect this"), ("direct", "explain this")]
