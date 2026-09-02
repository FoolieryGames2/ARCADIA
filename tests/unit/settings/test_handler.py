from __future__ import annotations

from pathlib import Path

import pytest

from arcadia.settings import (
    AAESettingsError,
    BudgetClass,
    SettingsStatus,
    load_aae_settings,
    resolve_dynamic_ceiling,
)

ROOT = Path(__file__).resolve().parents[3]
PRE1_SETTINGS = ROOT / "configs" / "aae_tuning.pre1.toml"


def test_pre1_settings_load_separately_from_contract_logic() -> None:
    handler = load_aae_settings(PRE1_SETTINGS)
    assert handler.settings_id == "AAE-TUNING-PRE-1"
    assert handler.status is SettingsStatus.PRE_VERSION
    assert set(handler.class_defaults) == set(BudgetClass)


def test_r0_profiles_resolve_current_known_broad_safety_ceilings() -> None:
    handler = load_aae_settings(PRE1_SETTINGS)
    proposal = handler.resolve("settings.scope_proposal.pre1")
    validation = handler.resolve("settings.scope_validation.pre1")
    assert proposal.specialist_mode_id == "SCOPE_PROPOSAL"
    assert proposal.budget_class is BudgetClass.SMALL
    assert proposal.limits.max_string_chars == 65_536
    assert proposal.limits.max_array_items == 16
    assert validation.specialist_mode_id == "SCOPE_VALIDATION"
    assert validation.budget_class is BudgetClass.MEDIUM
    assert validation.limits.max_array_items == 64


def test_missing_numeric_knobs_are_unresolved_not_unlimited() -> None:
    handler = load_aae_settings(PRE1_SETTINGS)
    resolved = handler.resolve("settings.scope_proposal.pre1")
    assert resolved.limits.max_input_tokens is None
    assert resolved.limits.complete is False
    with pytest.raises(AAESettingsError, match="incomplete"):
        handler.require_complete("settings.scope_proposal.pre1")


def test_settings_snapshot_is_deterministic_and_hash_bound() -> None:
    handler = load_aae_settings(PRE1_SETTINGS)
    left = handler.snapshot("settings.scope_proposal.pre1")
    right = handler.snapshot("settings.scope_proposal.pre1")
    assert left.settings_hash == right.settings_hash
    assert left.to_value()["settings_hash"].startswith("sha256:")


def test_dynamic_ceiling_never_expands_past_config_or_host_availability() -> None:
    assert resolve_dynamic_ceiling(configured_ceiling=8, host_available=3) == 3
    assert resolve_dynamic_ceiling(configured_ceiling=3, host_available=8) == 3
    assert resolve_dynamic_ceiling(configured_ceiling=0, host_available=8) == 0


def test_unknown_settings_knobs_fail_closed(tmp_path: Path) -> None:
    path = tmp_path / "bad.toml"
    path.write_text(
        '''settings_format_version = 1\nsettings_id = "BAD"\nstatus = "PRE_VERSION"\nbanana = 5\n''',
        encoding="utf-8",
    )
    with pytest.raises(AAESettingsError, match="unknown root setting"):
        load_aae_settings(path)


def test_duplicate_mode_profiles_are_rejected(tmp_path: Path) -> None:
    path = tmp_path / "dupe.toml"
    path.write_text(
        '''settings_format_version = 1\nsettings_id = "DUP"\nstatus = "PRE_VERSION"\n\n[profiles.a]\nspecialist_mode_id = "SCOPE_PROPOSAL"\nbudget_class = "SMALL"\n\n[profiles.b]\nspecialist_mode_id = "SCOPE_PROPOSAL"\nbudget_class = "MEDIUM"\n''',
        encoding="utf-8",
    )
    with pytest.raises(AAESettingsError, match="duplicate specialist mode"):
        load_aae_settings(path)


def test_repair_attempt_limit_is_a_tunable_nonnegative_setting() -> None:
    from arcadia.settings import TuningLimits

    assert TuningLimits(max_repair_attempts=0).max_repair_attempts == 0
    assert TuningLimits(max_repair_attempts=2).max_repair_attempts == 2
    with pytest.raises(AAESettingsError, match="nonnegative integer"):
        TuningLimits(max_repair_attempts=-1)
    with pytest.raises(AAESettingsError, match="nonnegative integer"):
        TuningLimits(max_repair_attempts=True)


def test_pre1_repair_limits_remain_unresolved_until_measured() -> None:
    handler = load_aae_settings(PRE1_SETTINGS)
    assert handler.resolve("settings.scope_proposal.pre1").limits.max_repair_attempts is None
    assert handler.resolve("settings.scope_validation.pre1").limits.max_repair_attempts is None
