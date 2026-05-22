#!/usr/bin/env python3
"""Inspect disabled AI escalation preflight and gate records."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.ai_escalation import (
    ALLOWED_AI_ESCALATION_GATE_STATES,
    AIEscalationError,
    build_ai_escalation_preflight,
    create_ai_escalation_gate,
    evaluate_ai_escalation_eligibility,
)
from runtime.local_appliance import LocalApplianceError, close_local_appliance, open_local_appliance
from runtime.local_operator import LocalOperatorAuthError, build_operator_auth_state, verify_operator_token


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout, stderr: TextIO = sys.stderr) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.instance:
        result = fail_result("missing_instance", "--instance is required")
        emit_result(result, args.json, args.output, stdout)
        print("ERROR: --instance is required", file=stderr)
        return 2
    if not args.command:
        result = fail_result("missing_command", "an AI escalation command is required")
        emit_result(result, args.json, args.output, stdout)
        print("ERROR: an AI escalation command is required", file=stderr)
        return 2

    runtime = None
    try:
        runtime = open_local_appliance(Path(args.instance), read_only=args.command in {"list", "show"})
        if args.command in {"preflight-hunt", "preflight-need", "create-gate-from-hunt", "create-gate-from-need"}:
            require_cli_operator_token(runtime, args.operator_token)
        result = dispatch(runtime, args)
    except (LocalApplianceError, LocalOperatorAuthError, AIEscalationError, ValueError, json.JSONDecodeError) as exc:
        result = fail_result("ai_escalation_gate_failed", str(exc), instance=args.instance)
        emit_result(result, args.json, args.output, stdout)
        print(f"ERROR: {exc}", file=stderr)
        return 2
    except Exception as exc:  # pragma: no cover - defensive CLI boundary
        result = fail_result("ai_escalation_gate_failed", str(exc), instance=args.instance)
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
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    parser.add_argument("--output", help="Optional JSON output path.")
    subparsers = parser.add_subparsers(dest="command")

    preflight_hunt = subparsers.add_parser("preflight-hunt", help="Write disabled preflight for a Search Hunt.")
    preflight_hunt.add_argument("--hunt-id", required=True)
    preflight_hunt.add_argument("--operator-token", required=True)
    add_output_options(preflight_hunt)

    preflight_need = subparsers.add_parser("preflight-need", help="Write disabled preflight for a SearchNeed.")
    preflight_need.add_argument("--need-id", required=True)
    preflight_need.add_argument("--operator-token", required=True)
    add_output_options(preflight_need)

    create_hunt = subparsers.add_parser("create-gate-from-hunt", help="Create a disabled gate for a Search Hunt.")
    create_hunt.add_argument("--hunt-id", required=True)
    create_hunt.add_argument("--operator-token", required=True)
    add_output_options(create_hunt)

    create_need = subparsers.add_parser("create-gate-from-need", help="Create a disabled gate for a SearchNeed.")
    create_need.add_argument("--need-id", required=True)
    create_need.add_argument("--operator-token", required=True)
    add_output_options(create_need)

    list_cmd = subparsers.add_parser("list", help="List disabled AI escalation gates.")
    list_cmd.add_argument("--hunt-id")
    list_cmd.add_argument("--need-id")
    list_cmd.add_argument("--state", choices=ALLOWED_AI_ESCALATION_GATE_STATES)
    list_cmd.add_argument("--limit", type=int, default=100)
    add_output_options(list_cmd)

    show = subparsers.add_parser("show", help="Show one disabled AI escalation gate.")
    show.add_argument("--id", required=True)
    add_output_options(show)
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
    if args.command == "preflight-hunt":
        preflight = build_ai_escalation_preflight(runtime, hunt_id=args.hunt_id, operator_label="local_operator")
        written = runtime.ai_escalation.write_preflight(preflight)
        return ok_result("ai_escalation_preflight_from_hunt", {"preflight": written.to_dict(), "hunt_id": args.hunt_id})
    if args.command == "preflight-need":
        preflight = build_ai_escalation_preflight(runtime, need_id=args.need_id, operator_label="local_operator")
        written = runtime.ai_escalation.write_preflight(preflight)
        return ok_result("ai_escalation_preflight_from_need", {"preflight": written.to_dict(), "need_id": args.need_id})
    if args.command == "create-gate-from-hunt":
        gate = create_ai_escalation_gate(runtime, hunt_id=args.hunt_id, operator_label="local_operator")
        return ok_result("ai_escalation_gate_created_from_hunt", {"gate": gate.to_dict(), "hunt_id": args.hunt_id})
    if args.command == "create-gate-from-need":
        gate = create_ai_escalation_gate(runtime, need_id=args.need_id, operator_label="local_operator")
        return ok_result("ai_escalation_gate_created_from_need", {"gate": gate.to_dict(), "need_id": args.need_id})
    if args.command == "list":
        gates = [item.to_dict() for item in runtime.ai_escalation.list_gates(hunt_id=args.hunt_id, need_id=args.need_id, limit=args.limit)]
        if args.state:
            gates = [item for item in gates if item.get("state") == args.state]
        eligibility = evaluate_ai_escalation_eligibility(runtime, hunt_id=args.hunt_id, need_id=args.need_id) if (args.hunt_id or args.need_id) else None
        return ok_result("ai_escalation_gate_list", {"gate_count": len(gates), "gates": gates, "eligibility": eligibility.to_dict() if eligibility else None})
    if args.command == "show":
        gate = runtime.ai_escalation.get_gate(args.id)
        if gate is None:
            return fail_result("ai_escalation_gate_not_found", f"AI escalation gate not found: {args.id}")
        return ok_result("ai_escalation_gate_show", {"gate": gate.to_dict()})
    raise ValueError(f"unsupported command: {args.command}")


def ok_result(action: str, payload: dict[str, Any]) -> dict[str, Any]:
    result = {
        "schema_version": "ai_escalation_gate_cli_result.v0",
        "status": "pass",
        "action": action,
        "provider_enabled": False,
        "execution_enabled": False,
        "browser_enabled": False,
        "source_probe_enabled": False,
        "extraction_enabled": False,
        "output_candidate_only": True,
        "review_required": True,
        "execute_route_exists": False,
        "model_provider_used": False,
        "external_network_used": False,
        "source_probe_executed": False,
        "extraction_executed": False,
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
        "schema_version": "ai_escalation_gate_cli_result.v0",
        "status": "fail",
        "error": code,
        "message": message,
        "provider_enabled": False,
        "execution_enabled": False,
        "browser_enabled": False,
        "source_probe_enabled": False,
        "extraction_enabled": False,
        "model_provider_used": False,
        "external_network_used": False,
        "source_probe_executed": False,
        "extraction_executed": False,
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
    if result.get("gate"):
        print(f"gate: {result['gate']['gate_id']}", file=stdout)
    if result.get("preflight"):
        print(f"preflight: {result['preflight']['preflight_id']}", file=stdout)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
