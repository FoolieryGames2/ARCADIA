"""Minimal ARCADIA operator entry point."""

from __future__ import annotations

import argparse

from arcadia.environment import print_environment_report


def main() -> int:
    parser = argparse.ArgumentParser(prog="arcadia")
    parser.add_argument("command", choices=("doctor",))
    args = parser.parse_args()
    if args.command == "doctor":
        return print_environment_report()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
