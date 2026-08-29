"""Deterministic host environment validation."""

from __future__ import annotations

import importlib.metadata
import sqlite3
import sys
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Check:
    name: str
    passed: bool
    detail: str


def inspect_environment() -> tuple[Check, ...]:
    python_ok = sys.version_info[:2] == (3, 12)
    checks = [
        Check("python", python_ok, sys.version.split()[0]),
        _check_fts5(),
    ]
    for package in ("jsonschema", "pydantic", "platformdirs", "rapidfuzz"):
        checks.append(_check_package(package))
    return tuple(checks)


def _check_fts5() -> Check:
    try:
        with sqlite3.connect(":memory:") as connection:
            connection.execute("CREATE VIRTUAL TABLE probe USING fts5(content)")
    except sqlite3.Error as exc:
        return Check("sqlite_fts5", False, f"SQLite {sqlite3.sqlite_version}: {exc}")
    return Check("sqlite_fts5", True, f"SQLite {sqlite3.sqlite_version}")


def _check_package(name: str) -> Check:
    try:
        version = importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        return Check(name, False, "not installed")
    return Check(name, True, version)


def print_environment_report() -> int:
    checks = inspect_environment()
    for check in checks:
        standing = "PASS" if check.passed else "FAIL"
        print(f"{standing:4}  {check.name:16} {check.detail}")
    return 0 if all(check.passed for check in checks) else 1
