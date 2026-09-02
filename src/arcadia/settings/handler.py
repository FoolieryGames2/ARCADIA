"""Separate PRE-1 handler for tunable AAE operating limits.

Contract logic decides what is legal. This handler owns values that operators may
later tune without rewriting semantic contract logic: token ceilings, broad string/
array/nesting ceilings, source-excerpt ceilings, and context headroom.

Every resolved profile can be snapshotted and SHA-256 hashed so tests and traces can
prove exactly which settings were active for a learned call.
"""

from __future__ import annotations

import tomllib
from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from types import MappingProxyType
from typing import Final

from arcadia.core.canonical_json import JsonValue
from arcadia.core.hashing import Sha256Digest, sha256_canonical_json


class AAESettingsError(ValueError):
    """AAE tuning settings are missing, malformed, or internally inconsistent."""


class SettingsStatus(StrEnum):
    PRE_VERSION = "PRE_VERSION"
    FROZEN = "FROZEN"


class BudgetClass(StrEnum):
    TINY = "TINY"
    SMALL = "SMALL"
    MEDIUM = "MEDIUM"
    LARGE = "LARGE"
    FULL_CAPABLE = "FULL_CAPABLE"


_LIMIT_FIELDS: Final = (
    "max_input_tokens",
    "max_output_tokens",
    "max_string_chars",
    "max_array_items",
    "max_nesting_depth",
    "max_source_excerpt_chars",
    "context_headroom_tokens",
    "max_repair_attempts",
)


@dataclass(frozen=True, slots=True)
class TuningLimits:
    max_input_tokens: int | None = None
    max_output_tokens: int | None = None
    max_string_chars: int | None = None
    max_array_items: int | None = None
    max_nesting_depth: int | None = None
    max_source_excerpt_chars: int | None = None
    context_headroom_tokens: int | None = None
    max_repair_attempts: int | None = None

    def __post_init__(self) -> None:
        for name in _LIMIT_FIELDS:
            value = getattr(self, name)
            if value is None:
                continue
            if name == "max_repair_attempts":
                if type(value) is not int or value < 0:
                    raise AAESettingsError(
                        "max_repair_attempts must be a nonnegative integer when set"
                    )
            elif type(value) is not int or value < 1:
                raise AAESettingsError(f"{name} must be a positive integer when set")

    def overlay(self, override: TuningLimits) -> TuningLimits:
        return TuningLimits(
            **{
                name: getattr(override, name)
                if getattr(override, name) is not None
                else getattr(self, name)
                for name in _LIMIT_FIELDS
            }
        )

    @property
    def complete(self) -> bool:
        return all(getattr(self, name) is not None for name in _LIMIT_FIELDS)

    def to_value(self) -> dict[str, JsonValue]:
        return {name: getattr(self, name) for name in _LIMIT_FIELDS}


@dataclass(frozen=True, slots=True)
class ContractTuningProfile:
    profile_id: str
    specialist_mode_id: str
    budget_class: BudgetClass
    overrides: TuningLimits = TuningLimits()


@dataclass(frozen=True, slots=True)
class ResolvedTuningProfile:
    settings_id: str
    settings_status: SettingsStatus
    profile_id: str
    specialist_mode_id: str
    budget_class: BudgetClass
    limits: TuningLimits

    def to_value(self) -> dict[str, JsonValue]:
        return {
            "budget_class": self.budget_class.value,
            "limits": self.limits.to_value(),
            "profile_id": self.profile_id,
            "settings_id": self.settings_id,
            "settings_status": self.settings_status.value,
            "specialist_mode_id": self.specialist_mode_id,
        }


@dataclass(frozen=True, slots=True)
class SettingsSnapshot:
    resolved: ResolvedTuningProfile
    settings_hash: Sha256Digest

    def to_value(self) -> dict[str, JsonValue]:
        return {
            "profile": self.resolved.to_value(),
            "settings_hash": self.settings_hash.value,
        }


@dataclass(frozen=True, slots=True)
class AAESettingsHandler:
    settings_id: str
    status: SettingsStatus
    global_defaults: TuningLimits
    class_defaults: Mapping[BudgetClass, TuningLimits]
    profiles: Mapping[str, ContractTuningProfile]

    def __post_init__(self) -> None:
        object.__setattr__(self, "class_defaults", MappingProxyType(dict(self.class_defaults)))
        object.__setattr__(self, "profiles", MappingProxyType(dict(self.profiles)))

    def resolve(self, profile_id: str) -> ResolvedTuningProfile:
        try:
            profile = self.profiles[profile_id]
        except KeyError as exc:
            raise AAESettingsError(f"unknown AAE tuning profile: {profile_id}") from exc
        class_defaults = self.class_defaults.get(profile.budget_class, TuningLimits())
        effective = self.global_defaults.overlay(class_defaults).overlay(profile.overrides)
        return ResolvedTuningProfile(
            settings_id=self.settings_id,
            settings_status=self.status,
            profile_id=profile.profile_id,
            specialist_mode_id=profile.specialist_mode_id,
            budget_class=profile.budget_class,
            limits=effective,
        )

    def snapshot(self, profile_id: str) -> SettingsSnapshot:
        resolved = self.resolve(profile_id)
        return SettingsSnapshot(
            resolved=resolved,
            settings_hash=sha256_canonical_json(resolved.to_value()),
        )

    def require_complete(self, profile_id: str) -> ResolvedTuningProfile:
        resolved = self.resolve(profile_id)
        if not resolved.limits.complete:
            raise AAESettingsError(
                f"AAE tuning profile {profile_id} is incomplete; unresolved limits are not unlimited"
            )
        return resolved


def resolve_dynamic_ceiling(*, configured_ceiling: int, host_available: int) -> int:
    """Resolve a dynamic host bound without ever expanding beyond either limit."""

    if type(configured_ceiling) is not int or configured_ceiling < 0:
        raise AAESettingsError("configured_ceiling must be a nonnegative integer")
    if type(host_available) is not int or host_available < 0:
        raise AAESettingsError("host_available must be a nonnegative integer")
    return min(configured_ceiling, host_available)


def _require_exact_keys(payload: dict[str, object], *, allowed: set[str], label: str) -> None:
    unknown = set(payload) - allowed
    if unknown:
        raise AAESettingsError(f"unknown {label} setting(s): {sorted(unknown)!r}")


def _limits(payload: object, *, label: str) -> TuningLimits:
    if payload is None:
        return TuningLimits()
    if type(payload) is not dict:
        raise AAESettingsError(f"{label} must be a TOML table")
    _require_exact_keys(payload, allowed=set(_LIMIT_FIELDS), label=label)
    return TuningLimits(**payload)


def load_aae_settings(path: Path) -> AAESettingsHandler:
    """Load one strict TOML settings document. Unknown knobs fail closed."""

    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise AAESettingsError(f"cannot read AAE settings: {path}") from exc
    try:
        payload = tomllib.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, tomllib.TOMLDecodeError) as exc:
        raise AAESettingsError(f"invalid AAE settings TOML: {path}") from exc
    if type(payload) is not dict:
        raise AAESettingsError("AAE settings root must be a TOML table")
    _require_exact_keys(
        payload,
        allowed={
            "settings_format_version",
            "settings_id",
            "status",
            "global_defaults",
            "budget_classes",
            "profiles",
        },
        label="root",
    )
    if payload.get("settings_format_version") != 1:
        raise AAESettingsError("unsupported settings_format_version")
    settings_id = payload.get("settings_id")
    if type(settings_id) is not str or not settings_id:
        raise AAESettingsError("settings_id must be nonempty text")
    raw_status = payload.get("status")
    if type(raw_status) is not str:
        raise AAESettingsError("status must be PRE_VERSION or FROZEN")
    try:
        status = SettingsStatus(raw_status)
    except (TypeError, ValueError) as exc:
        raise AAESettingsError("status must be PRE_VERSION or FROZEN") from exc

    global_defaults = _limits(payload.get("global_defaults", {}), label="global_defaults")

    raw_classes = payload.get("budget_classes", {})
    if type(raw_classes) is not dict:
        raise AAESettingsError("budget_classes must be a TOML table")
    class_defaults: dict[BudgetClass, TuningLimits] = {}
    for raw_name, raw_limits in raw_classes.items():
        try:
            budget_class = BudgetClass(raw_name)
        except ValueError as exc:
            raise AAESettingsError(f"unknown budget class: {raw_name}") from exc
        class_defaults[budget_class] = _limits(
            raw_limits, label=f"budget_classes.{raw_name}"
        )

    raw_profiles = payload.get("profiles", {})
    if type(raw_profiles) is not dict:
        raise AAESettingsError("profiles must be a TOML table")
    profiles: dict[str, ContractTuningProfile] = {}
    seen_modes: set[str] = set()
    for profile_id, raw_profile in raw_profiles.items():
        if type(raw_profile) is not dict:
            raise AAESettingsError(f"profiles.{profile_id} must be a TOML table")
        _require_exact_keys(
            raw_profile,
            allowed={"specialist_mode_id", "budget_class", "overrides"},
            label=f"profiles.{profile_id}",
        )
        mode = raw_profile.get("specialist_mode_id")
        if type(mode) is not str or not mode:
            raise AAESettingsError(f"profiles.{profile_id}.specialist_mode_id must be text")
        if mode in seen_modes:
            raise AAESettingsError(f"duplicate specialist mode settings profile: {mode}")
        seen_modes.add(mode)
        raw_budget_class = raw_profile.get("budget_class")
        if type(raw_budget_class) is not str:
            raise AAESettingsError(
                f"profiles.{profile_id}.budget_class is invalid"
            )
        try:
            budget_class = BudgetClass(raw_budget_class)
        except (TypeError, ValueError) as exc:
            raise AAESettingsError(
                f"profiles.{profile_id}.budget_class is invalid"
            ) from exc
        profiles[profile_id] = ContractTuningProfile(
            profile_id=profile_id,
            specialist_mode_id=mode,
            budget_class=budget_class,
            overrides=_limits(
                raw_profile.get("overrides", {}), label=f"profiles.{profile_id}.overrides"
            ),
        )

    return AAESettingsHandler(
        settings_id=settings_id,
        status=status,
        global_defaults=global_defaults,
        class_defaults=class_defaults,
        profiles=profiles,
    )
