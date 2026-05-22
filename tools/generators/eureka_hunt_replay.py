#!/usr/bin/env python3
"""Plan, run, and inspect deterministic local Search Hunt replay."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.local_appliance import LocalApplianceError, close_local_appliance, open_local_appliance
from runtime.local_operator import LocalOperatorAuthError, build_operator_auth_state, verify_operator_token
from runtime.search_hunt import build_replay_fixture_from_hunt, run_hunt_replay, verify_existing_hunt_against_replay


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout, stderr: TextIO = sys.stderr) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instance", help="Explicit local appliance instance root.")
    parser.add_argument("--hunt-id", help="Search Hunt Session id.")
    parser.add_argument("--operator-token", help="Operator token for replay-local.")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--output")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("plan")
    sub.add_parser("replay-local")
    sub.add_parser("verify-existing")
    sub.add_parser("list")
    show = sub.add_parser("show")
    show.add_argument("--replay-id", required=True)
    args = parser.parse_args(_normalize_global_options(sys.argv[1:] if argv is None else argv))

    if not args.instance:
        result = fail_result("missing_instance", "--instance is required")
        emit_result(result, args.json, args.output, stdout)
        print("ERROR: --instance is required", file=stderr)
        return 2

    runtime = None
    try:
        read_only = args.command in {"plan", "verify-existing", "list", "show"}
        runtime = open_local_appliance(Path(args.instance), read_only=read_only)
        result = _run_command(runtime, args)
    except (LocalApplianceError, LocalOperatorAuthError, ValueError) as exc:
        result = fail_result("hunt_replay_failed", str(exc))
        emit_result(result, args.json, args.output, stdout)
        print(f"ERROR: {exc}", file=stderr)
        return 2
    except Exception as exc:  # pragma: no cover - defensive CLI boundary
        result = fail_result("hunt_replay_failed", str(exc))
        emit_result(result, args.json, args.output, stdout)
        print(f"ERROR: {exc}", file=stderr)
        return 1
    finally:
        if runtime is not None:
            close_local_appliance(runtime)
    emit_result(result, args.json, args.output, stdout)
    return 0 if result.get("status") in {"pass", "planned"} else 1


def _run_command(runtime: Any, args: argparse.Namespace) -> dict[str, Any]:
    command = str(args.command)
    if command == "list":
        records = [item.to_dict() for item in runtime.search_hunt.list_replay_results(hunt_id=args.hunt_id or None, limit=100)]
        return replay_payload("hunt_replay_list", {"replay_count": len(records), "replays": records})
    if command == "show":
        record = runtime.search_hunt.get_replay_result(args.replay_id)
        return replay_payload("hunt_replay_show", {"found": record is not None, "replay": record.to_dict() if record else None})
    if not args.hunt_id:
        raise ValueError("--hunt-id is required")
    fixture = build_replay_fixture_from_hunt(runtime, args.hunt_id)
    if command == "plan":
        result = run_hunt_replay(runtime, fixture, mode="plan_only")
        return replay_payload("hunt_replay_plan", {"hunt_id": args.hunt_id, "fixture": fixture.to_dict(), "plan": result.to_dict()})
    if command == "verify-existing":
        result = verify_existing_hunt_against_replay(runtime, args.hunt_id, fixture)
        return replay_payload("hunt_replay_verify_existing", {"hunt_id": args.hunt_id, "result": result.to_dict()})
    if command == "replay-local":
        require_cli_operator_token(runtime, args.operator_token)
        result = run_hunt_replay(
            runtime,
            fixture,
            operator_context={"authorized": True, "operator_label": "local_operator", "raw_token_stored": False},
            mode="replay_local",
        )
        return replay_payload("hunt_replay_local", {"hunt_id": args.hunt_id, "result": result.to_dict(), "record": result.record.to_dict()})
    raise ValueError("unknown replay command")


def _normalize_global_options(argv: Sequence[str]) -> list[str]:
    normalized: list[str] = []
    hoisted: list[str] = []
    items = list(argv)
    index = 0
    while index < len(items):
        item = items[index]
        if item == "--json":
            if "--json" not in hoisted:
                hoisted.append("--json")
            index += 1
            continue
        if item == "--output":
            if index + 1 >= len(items):
                normalized.append(item)
                index += 1
                continue
            hoisted.extend((item, items[index + 1]))
            index += 2
            continue
        if item.startswith("--output="):
            hoisted.append(item)
            index += 1
            continue
        normalized.append(item)
        index += 1
    return hoisted + normalized


def require_cli_operator_token(runtime: Any, token: str | None) -> None:
    if not token:
        raise LocalOperatorAuthError("operator token is required")
    state = build_operator_auth_state(runtime.config)
    if not state.configured:
        raise LocalOperatorAuthError("operator token is not configured")
    if not verify_operator_token(str(token), state.token_hash, state.token_salt):
        raise LocalOperatorAuthError("operator token is invalid")


def replay_payload(action: str, payload: dict[str, Any]) -> dict[str, Any]:
    result = {
        "schema_version": "hunt_replay_cli_result.v0",
        "status": "pass",
        "action": action,
        "source_probe_executed": False,
        "extraction_executed": False,
        "external_network_used": False,
        "model_provider_used": False,
        "download_install_execute_performed": False,
        "master_index_mutated": False,
        "site_dist_mutated": False,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
        "warnings": [],
        "limitations": ["deterministic local replay only", "blocked future actions remain blocked"],
    }
    result.update(payload)
    return result


def fail_result(code: str, message: str) -> dict[str, Any]:
    return {
        "schema_version": "hunt_replay_cli_result.v0",
        "status": "fail",
        "error": code,
        "message": message,
        "source_probe_executed": False,
        "extraction_executed": False,
        "external_network_used": False,
        "model_provider_used": False,
        "download_install_execute_performed": False,
        "master_index_mutated": False,
        "site_dist_mutated": False,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }


def emit_result(result: dict[str, Any], as_json: bool, output: str | None, stdout: TextIO) -> None:
    if output:
        Path(output).parent.mkdir(parents=True, exist_ok=True)
        Path(output).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if as_json:
        print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
        return
    print(f"status: {result['status']}", file=stdout)
    if result.get("hunt_id"):
        print(f"hunt_id: {result['hunt_id']}", file=stdout)
    if result.get("record"):
        print(f"replay_id: {result['record']['replay_id']}", file=stdout)


if __name__ == "__main__":
    raise SystemExit(main())
