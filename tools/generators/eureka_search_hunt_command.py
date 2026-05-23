#!/usr/bin/env python3
"""Apply operator-gated local Search Hunt commands."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.local.appliance import LocalApplianceError, close_local_appliance, open_local_appliance
from runtime.local.operator import LocalOperatorAuthError, build_operator_auth_state, verify_operator_token
from runtime.search.hunt import SearchHuntError


MUTATION_COMMANDS = {
    "pause",
    "resume",
    "cancel",
    "block",
    "wait-for-user",
    "wait-for-policy",
    "complete",
    "fail",
    "steer",
    "unsteer",
}


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout, stderr: TextIO = sys.stderr) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.instance:
        result = fail_result("missing_instance", "--instance is required")
        emit_result(result, args.json, args.output, stdout)
        print("ERROR: --instance is required", file=stderr)
        return 2
    if not args.command:
        result = fail_result("missing_command", "a Search Hunt command is required")
        emit_result(result, args.json, args.output, stdout)
        print("ERROR: a Search Hunt command is required", file=stderr)
        return 2

    runtime = None
    try:
        runtime = open_local_appliance(Path(args.instance), read_only=args.command not in MUTATION_COMMANDS)
        if args.command in MUTATION_COMMANDS:
            require_cli_operator_token(runtime, args.operator_token)
        result = dispatch(runtime, args)
    except (LocalApplianceError, LocalOperatorAuthError, SearchHuntError, ValueError, json.JSONDecodeError) as exc:
        result = fail_result("search_hunt_command_failed", str(exc), instance=args.instance)
        emit_result(result, args.json, args.output, stdout)
        print(f"ERROR: {exc}", file=stderr)
        return 2
    except Exception as exc:  # pragma: no cover - defensive CLI boundary
        result = fail_result("search_hunt_command_failed", str(exc), instance=args.instance)
        emit_result(result, args.json, args.output, stdout)
        print(f"ERROR: {exc}", file=stderr)
        return 1
    finally:
        if runtime is not None:
            close_local_appliance(runtime)

    emit_result(result, args.json, args.output, stdout)
    return 0 if result.get("status") == "pass" else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instance", help="Explicit local appliance instance root.")
    parser.add_argument("--operator-token", help="Operator token for mutating commands.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    parser.add_argument("--output", help="Optional JSON output path.")
    subparsers = parser.add_subparsers(dest="command")

    for name in ("pause", "resume", "cancel", "wait-for-user", "wait-for-policy", "complete"):
        command = subparsers.add_parser(name, help=f"Apply {name} to a Search Hunt session.")
        command.add_argument("--id", required=True)
        command.add_argument("--reason")
        add_output_options(command)

    for name in ("block", "fail"):
        command = subparsers.add_parser(name, help=f"Apply {name} to a Search Hunt session.")
        command.add_argument("--id", required=True)
        command.add_argument("--reason", required=True)
        add_output_options(command)

    steer = subparsers.add_parser("steer", help="Record a Search Hunt steering preference.")
    steer.add_argument("--id", required=True)
    steer.add_argument("--type", required=True)
    steer.add_argument("--value")
    steer.add_argument("--reason")
    add_output_options(steer)

    unsteer = subparsers.add_parser("unsteer", help="Deactivate a Search Hunt steering preference.")
    unsteer.add_argument("--id", required=True)
    unsteer.add_argument("--steering-id", required=True)
    unsteer.add_argument("--reason")
    add_output_options(unsteer)

    commands = subparsers.add_parser("commands", help="List Search Hunt command history.")
    commands.add_argument("--id")
    commands.add_argument("--limit", type=int, default=100)
    add_output_options(commands)

    steering = subparsers.add_parser("steering", help="List Search Hunt steering preferences.")
    steering.add_argument("--id", required=True)
    steering.add_argument("--include-inactive", action="store_true")
    add_output_options(steering)
    return parser


def add_output_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--json", action="store_true", default=argparse.SUPPRESS, help=argparse.SUPPRESS)
    parser.add_argument("--output", default=argparse.SUPPRESS, help=argparse.SUPPRESS)


def require_cli_operator_token(runtime: Any, token: str | None) -> None:
    if not token:
        raise LocalOperatorAuthError("operator token is required")
    state = build_operator_auth_state(runtime.config)
    if not state.configured:
        raise LocalOperatorAuthError("operator token is not configured")
    if not verify_operator_token(str(token), state.token_hash, state.token_salt):
        raise LocalOperatorAuthError("operator token is invalid")


def dispatch(runtime: Any, args: argparse.Namespace) -> dict[str, Any]:
    store = runtime.search_hunt
    command = args.command
    operator_label = "local_operator"
    if command in {"pause", "resume", "cancel", "block", "wait-for-user", "wait-for-policy", "complete", "fail"}:
        result = store.apply_command(args.id, command.replace("-", "_"), reason=args.reason, operator_label=operator_label)
        return ok_result("search_hunt_command_applied", {"result": result.to_dict()})
    if command == "steer":
        preference = store.add_steering_preference(args.id, args.type, value=args.value, reason=args.reason, operator_label=operator_label)
        return ok_result("search_hunt_steering_recorded", {"steering_preference": preference.to_dict()})
    if command == "unsteer":
        preference = store.remove_steering_preference(args.id, args.steering_id, reason=args.reason, operator_label=operator_label)
        return ok_result("search_hunt_steering_deactivated", {"steering_preference": preference.to_dict()})
    if command == "commands":
        commands = [item.to_dict() for item in store.list_commands(args.id, limit=args.limit)]
        return ok_result("search_hunt_command_history", {"count": len(commands), "commands": commands})
    if command == "steering":
        preferences = [item.to_dict() for item in store.list_steering_preferences(args.id, active_only=not args.include_inactive)]
        return ok_result("search_hunt_steering_preferences", {"count": len(preferences), "steering_preferences": preferences})
    raise ValueError(f"unsupported command: {command}")


def ok_result(action: str, payload: dict[str, Any]) -> dict[str, Any]:
    result = {
        "schema_version": "search_hunt_command_cli_result.v0",
        "status": "pass",
        "action": action,
        "operator_token_required": action not in {"search_hunt_command_history", "search_hunt_steering_preferences"},
        "localhost_only_mutations": True,
        "lan_command_mutations_enabled": False,
        "workunit_creation_performed": False,
        "source_probe_executed": False,
        "external_network_used": False,
        "model_provider_used": False,
        "review_mutation_performed": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }
    result.update(payload)
    return result


def fail_result(code: str, message: str, *, instance: str | None = None) -> dict[str, Any]:
    result = {
        "schema_version": "search_hunt_command_cli_result.v0",
        "status": "fail",
        "error": code,
        "message": message,
        "workunit_creation_performed": False,
        "source_probe_executed": False,
        "external_network_used": False,
        "model_provider_used": False,
        "review_mutation_performed": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }
    if instance is not None:
        result["instance"] = instance
    return result


def emit_result(result: dict[str, Any], as_json: bool, output: str | None, stdout: TextIO) -> None:
    if output:
        write_json(Path(output), result)
    if as_json:
        print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
        return
    print(f"status: {result['status']}", file=stdout)
    if result.get("action"):
        print(f"action: {result['action']}", file=stdout)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
