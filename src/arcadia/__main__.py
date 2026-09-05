"""ARCADIA operator command-line entry point."""

from __future__ import annotations

import argparse
from dataclasses import dataclass, replace
from pathlib import Path

from arcadia.aa_runtime.serializer import ModelMessage
from arcadia.core.canonical_json import canonical_json_dumps
from arcadia.environment import print_environment_report
from arcadia.lab import (
    LabConfigError,
    LabResponse,
    LabRuntimeError,
    LabSettings,
    RuntimeIdentity,
    load_lab_settings,
    load_runtime_identity,
    reset_lab_settings,
    run_base_prompt,
    set_lab_setting,
    verify_runtime_files,
)
from arcadia.lab.base_only_invoker import (
    BaseOnlySpecialistInvoker,
    QualificationInvocationError,
)
from arcadia.lab.config import SETTING_NAMES, resolve_workspace
from arcadia.lab.recipe_harness import run_recipe0_base_only
from arcadia.lab.server import ResidentLlamaServer, ServerResponse, verify_server_files


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="arcadia")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("doctor", help="check the deterministic host environment")

    run = commands.add_parser(
        "run",
        help="run the pinned Qwen3 base model in explicit T0 lab mode",
    )
    run.add_argument("prompt", nargs="?", help="one prompt; omit for the interactive lab")
    run.add_argument("--workspace", type=Path, help=argparse.SUPPRESS)
    run.add_argument("--mode", choices=("direct", "recipe"))
    run.add_argument("--transport", choices=("process", "resident"))
    run.add_argument("--context-tokens", type=int)
    run.add_argument("--max-output-tokens", type=int)
    run.add_argument("--temperature", type=float)
    run.add_argument("--seed", type=int)
    run.add_argument("--gpu-layers", type=int)
    run.add_argument("--server-port", type=int)
    run.add_argument("--system-prompt")
    run.add_argument("--show-settings", action="store_true")
    run.add_argument("--set", nargs=2, metavar=("NAME", "VALUE"), dest="setting")
    run.add_argument("--reset-settings", action="store_true")
    run.add_argument(
        "--verify",
        action="store_true",
        help="hash the complete model and runtime, then exit",
    )
    run.add_argument("--no-metrics", action="store_true")
    return parser


def _print_settings(settings: LabSettings) -> None:
    print("ARCADIA lab settings")
    for name, value in settings.to_value().items():
        print(f"  {name:18} {value}")


def _apply_command_overrides(settings: LabSettings, args: argparse.Namespace) -> LabSettings:
    if args.mode is not None:
        settings = replace(settings, entry_mode=args.mode)
    if args.transport is not None:
        settings = replace(settings, runtime_transport=args.transport)
    if args.context_tokens is not None:
        settings = replace(settings, context_tokens=args.context_tokens)
    if args.max_output_tokens is not None:
        settings = replace(settings, max_output_tokens=args.max_output_tokens)
    if args.temperature is not None:
        settings = replace(settings, temperature=args.temperature)
    if args.seed is not None:
        settings = replace(settings, seed=args.seed)
    if args.gpu_layers is not None:
        settings = replace(settings, gpu_layers=args.gpu_layers)
    if args.server_port is not None:
        settings = replace(settings, server_port=args.server_port)
    if args.system_prompt is not None:
        settings = replace(settings, system_prompt=args.system_prompt)
    return settings


def _print_runtime_checks(
    identity: RuntimeIdentity, *, workspace: Path, full_model_hash: bool
) -> int:
    checks = (
        *verify_runtime_files(identity, full_model_hash=full_model_hash),
        *verify_server_files(workspace, identity),
    )
    for check in checks:
        standing = "PASS" if check.passed else "FAIL"
        print(f"{standing:4}  {check.name:16} {check.detail}")
    return 0 if all(check.passed for check in checks) else 1


def _print_response(response: LabResponse, settings: LabSettings, *, metrics: bool) -> None:
    print("\nARCADIA>")
    print(response.text)
    if metrics:
        print(
            f"\n[T0 BASE_ONLY | {response.elapsed_seconds:.2f}s | "
            f"ctx={settings.context_tokens} | max={settings.max_output_tokens} | "
            f"temp={settings.temperature:g} | seed={settings.seed}]"
        )


def _lab_response(response: ServerResponse, identity: RuntimeIdentity) -> LabResponse:
    return LabResponse(
        text=response.text,
        elapsed_seconds=response.elapsed_seconds,
        return_code=0,
        authority_tier="T0",
        model_sha256=identity.model_sha256,
        stderr_tail="",
    )


def _run_direct_resident(
    server: ResidentLlamaServer,
    identity: RuntimeIdentity,
    settings: LabSettings,
    prompt: str,
) -> LabResponse:
    response = server.complete(
        (
            ModelMessage(role="system", content=settings.system_prompt),
            ModelMessage(role="user", content=prompt),
        ),
        settings=settings,
    )
    return _lab_response(response, identity)


def _run_recipe_slice(
    server: ResidentLlamaServer,
    identity: RuntimeIdentity,
    settings: LabSettings,
    prompt: str,
) -> None:
    result = run_recipe0_base_only(
        prompt,
        invoker=BaseOnlySpecialistInvoker(server, identity, settings),
    )
    receipt = result.activation_receipt
    print("\nARCADIA RECIPE TRACE>")
    print(f"  R0 Conversation Resolver  PASS ({receipt.elapsed_seconds:.2f}s)")
    print(f"  SCOPE_PROPOSAL             {canonical_json_dumps(result.scope_output)}")
    print(f"  Conversation Packet hash  {result.conversation_packet.packet_hash.value}")
    print(f"  Activation receipt        {receipt.call_id}")
    print(f"  {result.next_recipe} Intent                 {result.next_standing}")
    print("\n[T0 BASE_ONLY | recipe harness stopped honestly before unimplemented R1]")


def _interactive_help() -> None:
    print("Commands:")
    print("  /mode recipe            use the implemented recipe pipeline")
    print("  /mode direct            talk directly to the base model")
    print("  /recipe PROMPT          run one prompt through recipe mode")
    print("  /direct PROMPT          run one prompt through direct mode")
    print("  /status                 show active mode, transport, and authority")
    print("  /config                 show current settings")
    print(f"  /set NAME VALUE          persist one setting ({', '.join(SETTING_NAMES)})")
    print("  /reset                  restore checked-in defaults")
    print("  /restart                restart the runtime with saved settings")
    print("  /verify                 hash-check the complete model and runtime")
    print("  /help                   show these commands")
    print("  /quit                   leave the lab")


@dataclass(frozen=True, slots=True)
class _InteractiveExit:
    code: int
    settings: LabSettings
    restart: bool = False


def _switch_mode(workspace: Path, settings: LabSettings, mode: str) -> LabSettings:
    try:
        updated = set_lab_setting(workspace, "entry_mode", mode)
    except LabConfigError as exc:
        print(f"Mode rejected: {exc}")
        return settings
    print(f"Mode changed to {updated.entry_mode}.")
    return updated


def _interactive_loop(
    workspace: Path,
    identity: RuntimeIdentity,
    settings: LabSettings,
    *,
    metrics: bool,
    server: ResidentLlamaServer | None,
) -> _InteractiveExit:
    while True:
        try:
            prompt = input("you> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nLab closed.")
            return _InteractiveExit(0, settings)
        if not prompt:
            continue
        if prompt in {"/quit", "/exit"}:
            print("Lab closed.")
            return _InteractiveExit(0, settings)
        if prompt == "/help":
            _interactive_help()
            continue
        if prompt == "/config":
            _print_settings(settings)
            continue
        if prompt == "/status":
            print(
                f"Mode: {settings.entry_mode} | Transport: {settings.runtime_transport} | "
                "Authority: T0 BASE_ONLY"
            )
            print("Implemented recipe span: R0; next boundary: R1 NOT_IMPLEMENTED")
            continue
        if prompt == "/restart":
            return _InteractiveExit(0, load_lab_settings(workspace), restart=True)
        if prompt.startswith("/mode ") or prompt.startswith("--mode "):
            parts = prompt.split()
            if len(parts) != 2:
                print("Usage: /mode recipe or /mode direct")
                continue
            settings = _switch_mode(workspace, settings, parts[1].lower())
            continue
        if prompt.lower().startswith("run_arcadia.bat --mode "):
            parts = prompt.split()
            if len(parts) == 3:
                settings = _switch_mode(workspace, settings, parts[2].lower())
            else:
                print("You are already inside ARCADIA. Use /mode recipe or /mode direct.")
            continue
        if prompt == "/reset":
            settings = reset_lab_settings(workspace)
            print("Restored checked-in lab defaults.")
            _print_settings(settings)
            continue
        if prompt == "/verify":
            _print_runtime_checks(identity, workspace=workspace, full_model_hash=True)
            continue
        if prompt.startswith("/set "):
            parts = prompt.split(maxsplit=2)
            if len(parts) != 3:
                print("Usage: /set NAME VALUE")
                continue
            try:
                settings = set_lab_setting(workspace, parts[1], parts[2])
            except LabConfigError as exc:
                print(f"Setting rejected: {exc}")
            else:
                print(f"Saved {parts[1]} = {settings.to_value()[parts[1]]}")
                if parts[1] in {"context_tokens", "gpu_layers", "server_port"} and server:
                    print("Use /restart to apply this resident-runtime setting.")
            continue
        forced_mode: str | None = None
        if prompt == "/recipe":
            settings = _switch_mode(workspace, settings, "recipe")
            continue
        if prompt.startswith("/recipe "):
            forced_mode, prompt = "recipe", prompt[len("/recipe ") :].strip()
        elif prompt == "/direct":
            settings = _switch_mode(workspace, settings, "direct")
            continue
        elif prompt.startswith("/direct "):
            forced_mode, prompt = "direct", prompt[len("/direct ") :].strip()
        elif prompt.startswith("/"):
            print("Unknown lab command. Type /help.")
            continue
        try:
            active_mode = settings.entry_mode if forced_mode is None else forced_mode
            if active_mode == "recipe":
                if server is None:
                    print("Recipe mode requires runtime_transport=resident.")
                    continue
                _run_recipe_slice(server, identity, settings, prompt)
                continue
            response = (
                run_base_prompt(identity, settings, prompt)
                if server is None
                else _run_direct_resident(server, identity, settings, prompt)
            )
        except (LabRuntimeError, QualificationInvocationError) as exc:
            print(f"ARCADIA runtime error: {exc}")
            continue
        _print_response(response, settings, metrics=metrics)


def _interactive(workspace: Path, settings: LabSettings, *, metrics: bool) -> int:
    identity = load_runtime_identity(workspace)
    print("ARCADIA v0.1 — local Qwen3 test lab")
    print("Standing: T0 BASE_ONLY_TEST_MODE; no adapter or production authority")
    while True:
        print(f"Mode: {settings.entry_mode} | Transport: {settings.runtime_transport}")
        print("Use /mode recipe or /mode direct. Type /help for all controls.\n")
        if settings.runtime_transport == "process":
            result = _interactive_loop(workspace, identity, settings, metrics=metrics, server=None)
        else:
            print("Loading the pinned model into GPU memory...")
            with ResidentLlamaServer(
                workspace=workspace, runtime=identity, settings=settings
            ) as server:
                print(f"Resident CUDA runtime ready in {server.load_seconds:.2f}s.\n")
                result = _interactive_loop(
                    workspace, identity, settings, metrics=metrics, server=server
                )
        if not result.restart:
            return result.code
        settings = result.settings
        print("Restarting ARCADIA with saved settings...\n")


def _run_command(args: argparse.Namespace) -> int:
    workspace = resolve_workspace(args.workspace)
    identity = load_runtime_identity(workspace)
    settings = load_lab_settings(workspace)
    exclusive_actions = sum(
        (
            bool(args.show_settings),
            args.setting is not None,
            bool(args.reset_settings),
            bool(args.verify),
        )
    )
    if exclusive_actions > 1 or (exclusive_actions and args.prompt is not None):
        raise LabConfigError("settings/verification actions cannot be combined with a prompt")
    if args.show_settings:
        _print_settings(settings)
        print(f"  model_sha256       {identity.model_sha256}")
        print(f"  runtime_commit     {identity.llama_commit}")
        return 0
    if args.setting is not None:
        name, value = args.setting
        updated = set_lab_setting(workspace, name, value)
        print(f"Saved {name} = {updated.to_value()[name]}")
        return 0
    if args.reset_settings:
        _print_settings(reset_lab_settings(workspace))
        return 0
    if args.verify:
        return _print_runtime_checks(identity, workspace=workspace, full_model_hash=True)

    settings = _apply_command_overrides(settings, args)
    if args.prompt is None:
        return _interactive(workspace, settings, metrics=not args.no_metrics)
    if settings.entry_mode == "recipe" and settings.runtime_transport != "resident":
        raise LabConfigError("recipe mode requires runtime_transport=resident")
    if settings.runtime_transport == "process":
        response = run_base_prompt(identity, settings, args.prompt)
        _print_response(response, settings, metrics=not args.no_metrics)
        return 0
    print("Loading the pinned model into GPU memory...")
    with ResidentLlamaServer(workspace=workspace, runtime=identity, settings=settings) as server:
        print(f"Resident CUDA runtime ready in {server.load_seconds:.2f}s.")
        if settings.entry_mode == "recipe":
            _run_recipe_slice(server, identity, settings, args.prompt)
        else:
            response = _run_direct_resident(server, identity, settings, args.prompt)
            _print_response(response, settings, metrics=not args.no_metrics)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "doctor":
            return print_environment_report()
        if args.command == "run":
            return _run_command(args)
    except (LabConfigError, LabRuntimeError, QualificationInvocationError) as exc:
        parser.error(str(exc))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
