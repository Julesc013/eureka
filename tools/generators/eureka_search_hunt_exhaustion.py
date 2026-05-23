#!/usr/bin/env python3
"""Show or generate local Search Hunt exhaustion reports."""

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
from runtime.search.hunt import SearchHuntError, build_hunt_exhaustion_report


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout, stderr: TextIO = sys.stderr) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instance", help="Explicit local appliance instance root.")
    parser.add_argument("--operator-token", help="Operator token for report generation.")
    parser.add_argument("--id", required=True, help="Search Hunt session id.")
    parser.add_argument("--generate", action="store_true", help="Generate and attach a deterministic exhaustion report.")
    parser.add_argument("--show", action="store_true", help="Show the latest exhaustion report.")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--output")
    args = parser.parse_args(argv)

    if not args.instance:
        result = fail_result("missing_instance", "--instance is required")
        emit_result(result, args.json, args.output, stdout)
        print("ERROR: --instance is required", file=stderr)
        return 2
    if not args.generate and not args.show:
        result = fail_result("missing_action", "--generate or --show is required")
        emit_result(result, args.json, args.output, stdout)
        print("ERROR: --generate or --show is required", file=stderr)
        return 2

    runtime = None
    try:
        runtime = open_local_appliance(Path(args.instance), read_only=not args.generate)
        if args.generate:
            require_cli_operator_token(runtime, args.operator_token)
            report = build_hunt_exhaustion_report(runtime, args.id, operator_label="local_operator")
            report = runtime.search_hunt.attach_exhaustion_report(args.id, report)
        else:
            report = runtime.search_hunt.get_latest_exhaustion_report(args.id)
        if report is None:
            result = fail_result("exhaustion_report_not_found", f"no exhaustion report found for hunt: {args.id}")
        else:
            result = ok_result("search_hunt_exhaustion_report", {"exhaustion_report": report.to_dict()})
    except (LocalApplianceError, LocalOperatorAuthError, SearchHuntError, ValueError, json.JSONDecodeError) as exc:
        result = fail_result("search_hunt_exhaustion_failed", str(exc), instance=args.instance)
        emit_result(result, args.json, args.output, stdout)
        print(f"ERROR: {exc}", file=stderr)
        return 2
    except Exception as exc:  # pragma: no cover - defensive CLI boundary
        result = fail_result("search_hunt_exhaustion_failed", str(exc), instance=args.instance)
        emit_result(result, args.json, args.output, stdout)
        print(f"ERROR: {exc}", file=stderr)
        return 1
    finally:
        if runtime is not None:
            close_local_appliance(runtime)

    emit_result(result, args.json, args.output, stdout)
    return 0 if result.get("status") == "pass" else 1


def require_cli_operator_token(runtime: Any, token: str | None) -> None:
    if not token:
        raise LocalOperatorAuthError("operator token is required")
    state = build_operator_auth_state(runtime.config)
    if not state.configured:
        raise LocalOperatorAuthError("operator token is not configured")
    if not verify_operator_token(str(token), state.token_hash, state.token_salt):
        raise LocalOperatorAuthError("operator token is invalid")


def ok_result(action: str, payload: dict[str, Any]) -> dict[str, Any]:
    result = {
        "schema_version": "search_hunt_exhaustion_cli_result.v0",
        "status": "pass",
        "action": action,
        "operator_token_required_for_generation": True,
        "localhost_only_generation": True,
        "lan_generation_enabled": False,
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
        "schema_version": "search_hunt_exhaustion_cli_result.v0",
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
