#!/usr/bin/env python3
"""Demonstrate SearchNeed-to-WorkUnit planning and persistence without running work."""

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
from runtime.search_need import SearchNeedError, build_workunit_plan_for_need, create_workunits_from_need, list_workunits_for_need


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout, stderr: TextIO = sys.stderr) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instance", help="Explicit local appliance instance root.")
    parser.add_argument("--operator-token", help="Operator token for WorkUnit persistence.")
    parser.add_argument("--query", default="sampleproject")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--output")
    args = parser.parse_args(argv)
    if not args.instance:
        result = fail_result("missing_instance", "--instance is required")
        emit_result(result, args.json, args.output, stdout)
        print("ERROR: --instance is required", file=stderr)
        return 2

    runtime = None
    try:
        runtime = open_local_appliance(Path(args.instance))
        require_cli_operator_token(runtime, args.operator_token)
        result = run_demo(runtime, args.query)
    except (LocalApplianceError, LocalOperatorAuthError, SearchNeedError, ValueError) as exc:
        result = fail_result("demo_failed", str(exc), instance=args.instance)
        emit_result(result, args.json, args.output, stdout)
        print(f"ERROR: {exc}", file=stderr)
        return 2
    except Exception as exc:  # pragma: no cover - defensive CLI boundary
        result = fail_result("demo_failed", str(exc), instance=args.instance)
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


def run_demo(runtime: Any, query: str) -> dict[str, Any]:
    before_public = runtime.public_index.summarize().to_dict()
    hunt = runtime.search_hunt.create_session_from_query(query, runtime=runtime)
    need = runtime.search_need.create_need_from_hunt(runtime, hunt.id, operator_label="demo_operator")
    plan = build_workunit_plan_for_need(runtime, need.id, operator_label="demo_operator")
    creation = create_workunits_from_need(runtime, need.id, operator_label="demo_operator")
    linked = list_workunits_for_need(runtime, need.id, limit=100)
    after_public = runtime.public_index.summarize().to_dict()
    blocked = [item for item in linked if item.get("policy_state") in {"blocked_by_policy", "blocked_until_evidence"}]
    running = [item for item in linked if item.get("state") in {"running", "complete", "failed"}]
    passed = (
        bool(plan.items)
        and creation.created_count == len(plan.items)
        and len(linked) == len(plan.items)
        and bool(blocked)
        and not running
        and before_public == after_public
    )
    return {
        "schema_version": "hunt_to_workunit_demo_result.v0",
        "status": "pass" if passed else "fail",
        "hunt": hunt.to_dict(),
        "search_need": need.to_dict(),
        "workunit_plan": plan.to_dict(),
        "creation_result": creation.to_dict(),
        "linked_workunits": linked,
        "blocked_policy_workunits_created_as_blocked": all(item.get("state") == "blocked" for item in blocked),
        "workunit_execution_performed": False,
        "workunits_executed": False,
        "source_probe_executed": False,
        "extraction_executed": False,
        "external_network_used": False,
        "model_provider_used": False,
        "review_mutation_performed": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
        "public_index_unchanged": before_public == after_public,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }


def fail_result(code: str, message: str, *, instance: str | None = None) -> dict[str, Any]:
    result = {
        "schema_version": "hunt_to_workunit_demo_result.v0",
        "status": "fail",
        "error": code,
        "message": message,
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
    if result.get("creation_result"):
        print(f"workunits: {result['creation_result']['workunit_count']}", file=stdout)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
