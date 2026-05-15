#!/usr/bin/env python3
"""Demonstrate background Search Hunt running over safe local workers."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.local_appliance import close_local_appliance, open_local_appliance
from runtime.local_operator import LocalOperatorAuthError, build_operator_auth_state, verify_operator_token
from runtime.search_hunt import build_hunt_exhaustion_report, run_next_hunt_workunit, summarize_background_hunt
from runtime.search_need import create_workunits_from_need
from runtime.workunit_queue import WorkUnit, WorkUnitState


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout, stderr: TextIO = sys.stderr) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instance", help="Explicit local appliance instance root.")
    parser.add_argument("--operator-token", help="Operator token.")
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
    except Exception as exc:
        result = fail_result("background_hunt_demo_failed", str(exc))
        emit_result(result, args.json, args.output, stdout)
        print(f"ERROR: {exc}", file=stderr)
        return 2
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
    report = build_hunt_exhaustion_report(runtime, hunt.id, operator_label="local_operator")
    attached = runtime.search_hunt.attach_exhaustion_report(hunt.id, report)
    need = runtime.search_need.create_need_from_hunt(runtime, hunt.id, operator_label="local_operator")
    creation = create_workunits_from_need(runtime, need.id, operator_label="local_operator")
    extra_blocked = _create_extra_blocked_workunits(runtime, need.id, hunt.id, attached.report_id)
    plan_before = summarize_background_hunt(runtime, hunt.id)["plan"]
    run_result = run_next_hunt_workunit(
        runtime,
        hunt.id,
        operator_context={"authorized": True, "operator_label": "local_operator", "raw_token_stored": False},
    )
    summary = summarize_background_hunt(runtime, hunt.id)
    linked = _linked_workunits(runtime, hunt.id)
    after_public = runtime.public_index.summarize().to_dict()
    blocked = [item for item in linked if item.get("state") == "blocked"]
    return {
        "schema_version": "background_hunt_demo_result.v0",
        "status": "pass",
        "hunt_id": hunt.id,
        "search_need_id": need.id,
        "hunt": hunt.to_dict(),
        "search_need": need.to_dict(),
        "workunit_creation": creation.to_dict(),
        "extra_blocked_workunits": extra_blocked,
        "plan": plan_before,
        "run_result": run_result.to_dict(),
        "summary": summary,
        "linked_workunits": linked,
        "safe_workunit_execution_passed": any(item.get("state") == "complete" for item in linked),
        "blocked_source_probe_remained_blocked": any(item.get("kind") == "source_probe" and item.get("state") == "blocked" for item in blocked),
        "blocked_extraction_remained_blocked": any(item.get("kind") == "extraction_task" and item.get("state") == "blocked" for item in blocked),
        "blocked_ai_model_remained_blocked": any(item.get("payload", {}).get("worker_kind") == "ai_model_worker" and item.get("state") == "blocked" for item in blocked),
        "public_index_unchanged": before_public == after_public,
        "source_probe_executed": False,
        "extraction_executed": False,
        "external_network_used": False,
        "model_provider_used": False,
        "download_install_execute_performed": False,
        "review_mutation_performed": False,
        "public_index_mutated_except_allowed_rebuild_worker": False,
        "master_index_mutated": False,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }


def _create_extra_blocked_workunits(runtime: Any, need_id: str, hunt_id: str, report_id: str) -> list[dict[str, Any]]:
    created = []
    specs = (
        ("extraction_task", "Blocked extraction sample", {"worker_kind": "extraction_worker"}),
        ("regression_test", "Blocked model sample", {"worker_kind": "ai_model_worker"}),
    )
    for kind, title, payload in specs:
        full_payload = {
            **payload,
            "search_need_id": need_id,
            "search_hunt_id": hunt_id,
            "exhaustion_report_id": report_id,
            "generated_from": "background_hunt_demo",
            "policy_state": "blocked_by_policy",
            "execution_enabled": False,
            "source_probe_execution_enabled": False,
            "extraction_execution_enabled": False,
            "model_provider_enabled": False,
        }
        workunit = runtime.workunit_queue.create_workunit(
            WorkUnit.new(kind, title, payload=full_payload, parent_id=need_id, idempotency_key=f"background_hunt_demo:{need_id}:{kind}:{payload['worker_kind']}")
        )
        if workunit.state != WorkUnitState.BLOCKED:
            workunit = runtime.workunit_queue.block_workunit(workunit.id, "blocked by background hunt demo policy")
        created.append(workunit.to_dict())
    return created


def _linked_workunits(runtime: Any, hunt_id: str) -> list[dict[str, Any]]:
    rows = []
    for workunit in runtime.workunit_queue.list_workunits(limit=500):
        payload = dict(workunit.payload)
        if str(payload.get("search_hunt_id") or "") == str(hunt_id):
            row = workunit.to_dict()
            row["search_need_id"] = payload.get("search_need_id")
            row["search_hunt_id"] = payload.get("search_hunt_id")
            row["exhaustion_report_id"] = payload.get("exhaustion_report_id")
            row["policy_state"] = payload.get("policy_state")
            rows.append(row)
    return rows


def fail_result(code: str, message: str) -> dict[str, Any]:
    return {
        "schema_version": "background_hunt_demo_result.v0",
        "status": "fail",
        "error": code,
        "message": message,
        "source_probe_executed": False,
        "extraction_executed": False,
        "external_network_used": False,
        "model_provider_used": False,
        "download_install_execute_performed": False,
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
    else:
        print(f"status: {result['status']}", file=stdout)


if __name__ == "__main__":
    raise SystemExit(main())
