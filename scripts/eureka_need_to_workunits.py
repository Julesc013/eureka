#!/usr/bin/env python3
"""Plan or persist local WorkUnits from a SearchNeed without running them."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.local_appliance import LocalApplianceError, close_local_appliance, open_local_appliance
from runtime.local_operator import LocalOperatorAuthError, build_operator_auth_state, verify_operator_token
from runtime.search_need import SearchNeedError, build_workunit_plan_for_need, create_workunits_from_need


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout, stderr: TextIO = sys.stderr) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instance", help="Explicit local appliance instance root.")
    parser.add_argument("--need-id", required=True)
    parser.add_argument("--operator-token")
    parser.add_argument("--plan-only", action="store_true")
    parser.add_argument("--create", action="store_true")
    parser.add_argument("--idempotency-key")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--output")
    args = parser.parse_args(argv)
    if not args.instance:
        result = fail_result("missing_instance", "--instance is required")
        emit_result(result, args.json, args.output, stdout)
        print("ERROR: --instance is required", file=stderr)
        return 2
    if args.plan_only == args.create:
        result = fail_result("mode_required", "choose exactly one of --plan-only or --create")
        emit_result(result, args.json, args.output, stdout)
        print("ERROR: choose exactly one of --plan-only or --create", file=stderr)
        return 2

    runtime = None
    try:
        runtime = open_local_appliance(Path(args.instance), read_only=args.plan_only)
        if args.create:
            require_cli_operator_token(runtime, args.operator_token)
            creation = create_workunits_from_need(
                runtime,
                args.need_id,
                operator_label="local_operator",
                idempotency_key=args.idempotency_key,
            )
            result = ok_result(
                "search_need_workunits_created",
                {
                    "need_id": args.need_id,
                    "result": creation.to_dict(),
                    "workunits": list(creation.workunits),
                    "workunit_creation_performed": True,
                },
            )
        else:
            plan = build_workunit_plan_for_need(runtime, args.need_id)
            result = ok_result(
                "search_need_workunit_plan",
                {
                    "need_id": args.need_id,
                    "plan": plan.to_dict(),
                    "workunit_creation_performed": False,
                },
            )
    except (LocalApplianceError, LocalOperatorAuthError, SearchNeedError, ValueError, json.JSONDecodeError) as exc:
        result = fail_result("need_to_workunits_failed", str(exc), instance=args.instance)
        emit_result(result, args.json, args.output, stdout)
        print(f"ERROR: {exc}", file=stderr)
        return 2
    except Exception as exc:  # pragma: no cover - defensive CLI boundary
        result = fail_result("need_to_workunits_failed", str(exc), instance=args.instance)
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
        "schema_version": "need_to_workunits_cli_result.v0",
        "status": "pass",
        "action": action,
        "operator_token_required_for_create": True,
        "localhost_only_creation": True,
        "lan_creation_enabled": False,
        "workunit_execution_performed": False,
        "source_probe_executed": False,
        "extraction_executed": False,
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
        "schema_version": "need_to_workunits_cli_result.v0",
        "status": "fail",
        "error": code,
        "message": message,
        "workunit_creation_performed": False,
        "workunit_execution_performed": False,
        "source_probe_executed": False,
        "extraction_executed": False,
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
    if result.get("plan"):
        print(f"plan_items: {result['plan']['item_count']}", file=stdout)
    if result.get("workunits"):
        print(f"workunits: {len(result['workunits'])}", file=stdout)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
