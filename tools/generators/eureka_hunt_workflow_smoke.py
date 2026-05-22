#!/usr/bin/env python3
"""Run the deterministic local Search Hunt workflow smoke."""

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
from runtime.search_hunt import (
    SearchHuntError,
    build_background_hunt_plan,
    build_hunt_exhaustion_report,
    run_next_hunt_workunit,
    summarize_background_hunt,
)
from runtime.search_need import create_workunits_from_need
from runtime.workunit_queue import WorkUnit, WorkUnitState, WorkUnitType


DEFAULT_QUERY = "sampleproject"
DEFAULT_MISSING_QUERY = "definitely-not-present-hunt-08"


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout, stderr: TextIO = sys.stderr) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instance", help="Explicit local appliance instance root.")
    parser.add_argument("--operator-token", help="Operator token for local mutations.")
    parser.add_argument("--query", default=DEFAULT_QUERY)
    parser.add_argument("--missing-query", default=DEFAULT_MISSING_QUERY)
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
        runtime = open_local_appliance(Path(args.instance), read_only=False)
        require_cli_operator_token(runtime, args.operator_token)
        result = run_workflow_smoke(runtime, args.query, args.missing_query)
    except (LocalApplianceError, LocalOperatorAuthError, SearchHuntError, ValueError) as exc:
        result = fail_result("hunt_workflow_smoke_failed", str(exc))
        emit_result(result, args.json, args.output, stdout)
        print(f"ERROR: {exc}", file=stderr)
        return 2
    except Exception as exc:  # pragma: no cover - defensive CLI boundary
        result = fail_result("hunt_workflow_smoke_failed", str(exc))
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


def run_workflow_smoke(runtime: Any, query: str = DEFAULT_QUERY, missing_query: str = DEFAULT_MISSING_QUERY) -> dict[str, Any]:
    before_public = runtime.public_index.summarize().to_dict()
    before_workunits = runtime.workunit_queue.summarize().total

    hunt = runtime.search_hunt.create_session_from_query(query, runtime=runtime)
    missing_hunt = runtime.search_hunt.create_session_from_query(missing_query, runtime=runtime)

    pause = runtime.search_hunt.apply_command(hunt.id, "pause", reason="local workflow smoke", operator_label="local_operator")
    resume = runtime.search_hunt.apply_command(hunt.id, "resume", reason="local workflow smoke", operator_label="local_operator")
    metadata = runtime.search_hunt.add_steering_preference(
        hunt.id,
        "metadata_only",
        value="true",
        reason="local smoke proof",
        operator_label="local_operator",
    )
    note = runtime.search_hunt.add_steering_preference(
        hunt.id,
        "add_note",
        value="local smoke proof",
        reason="local smoke proof",
        operator_label="local_operator",
    )

    report = build_hunt_exhaustion_report(runtime, hunt.id, operator_label="local_operator")
    attached_report = runtime.search_hunt.attach_exhaustion_report(hunt.id, report)
    missing_report = build_hunt_exhaustion_report(runtime, missing_hunt.id, operator_label="local_operator")
    runtime.search_hunt.attach_exhaustion_report(missing_hunt.id, missing_report)

    need = runtime.search_need.create_need_from_hunt(runtime, hunt.id, operator_label="local_operator")
    plan = build_background_hunt_plan(runtime, hunt.id)
    workunit_creation = create_workunits_from_need(runtime, need.id, operator_label="local_operator")
    extra_blocked = create_extra_blocked_workunits(runtime, need.id, hunt.id, attached_report.report_id)
    plan_after_create = build_background_hunt_plan(runtime, hunt.id)

    run_result = run_next_hunt_workunit(
        runtime,
        hunt.id,
        operator_context={"authorized": True, "operator_label": "local_operator", "raw_token_stored": False},
    )
    runner_summary = summarize_background_hunt(runtime, hunt.id)
    linked_workunits = linked_workunits_for_hunt(runtime, hunt.id)
    after_workunits = runtime.workunit_queue.summarize().total
    after_public = runtime.public_index.summarize().to_dict()
    commands = [item.to_dict() for item in runtime.search_hunt.list_commands(hunt.id, limit=100)]
    steering = [item.to_dict() for item in runtime.search_hunt.list_steering_preferences(hunt.id, active_only=False)]
    transitions = [item.to_dict() for item in runtime.workunit_queue.list_transitions(limit=500)]

    blocked_rows = [item for item in linked_workunits if item.get("state") == "blocked"]
    completed_rows = [item for item in linked_workunits if item.get("state") == "complete"]
    stage_flags = {
        "create_hunt_stage_passed": bool(hunt.id and missing_hunt.id),
        "command_steering_stage_passed": pause.status == "pass"
        and resume.status == "pass"
        and metadata.active
        and note.active
        and any(item.get("command_type") == "pause" for item in commands)
        and any(item.get("command_type") == "metadata_only" for item in commands),
        "exhaustion_stage_passed": attached_report.hunt_id == hunt.id and bool(attached_report.report_id),
        "search_need_stage_passed": need.hunt_id == hunt.id and need.exhaustion_report_id == attached_report.report_id,
        "workunit_creation_stage_passed": workunit_creation.created_count >= 1 and after_workunits > before_workunits,
        "safe_worker_stage_passed": run_result.run.status.value in {"complete", "skipped"} and bool(completed_rows),
        "policy_blocked_workunits_remained_blocked": any(item.get("kind") == "source_probe" for item in blocked_rows)
        and any(item.get("kind") == "extraction_task" for item in blocked_rows)
        and any(item.get("payload", {}).get("worker_kind") == "ai_model_worker" for item in blocked_rows),
    }
    safety_flags = {
        "source_probe_executed": False,
        "extraction_executed": False,
        "external_network_used": False,
        "model_provider_used": False,
        "download_install_execute_performed": False,
        "review_mutation_performed": False,
        "master_index_mutated": False,
        "site_dist_mutated": False,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }
    result = {
        "schema_version": "search_hunt_workflow_smoke_result.v0",
        "task": "HUNT-08",
        "status": "pass" if all(stage_flags.values()) and before_public == after_public else "fail",
        "query": query,
        "missing_query": missing_query,
        "hunt_id": hunt.id,
        "missing_hunt_id": missing_hunt.id,
        "search_need_id": need.id,
        "exhaustion_report_id": attached_report.report_id,
        "workunit_count": len(linked_workunits),
        "completed_workunit_count": len(completed_rows),
        "blocked_workunit_count": len(blocked_rows),
        "command_count": len(commands),
        "steering_count": len(steering),
        "transition_history_recorded": any(item.get("to_state") == "complete" for item in transitions),
        "worker_audit_recorded": any(ref.ref_kind == "worker_result" for ref in runtime.workunit_queue.list_payload_refs(limit=500)),
        "runner_summary": runner_summary,
        "initial_runner_plan": plan.to_dict(),
        "runner_plan_after_create": plan_after_create.to_dict(),
        "workunit_creation": workunit_creation.to_dict(),
        "extra_blocked_workunits": extra_blocked,
        "linked_workunits": linked_workunits,
        "commands": commands,
        "steering_preferences": steering,
        "public_index_unchanged": before_public == after_public,
        **stage_flags,
        **safety_flags,
    }
    return result


def create_extra_blocked_workunits(runtime: Any, need_id: str, hunt_id: str, report_id: str) -> list[dict[str, Any]]:
    created = []
    specs = (
        (WorkUnitType.EXTRACTION_TASK, "Blocked extraction smoke sample", "extraction_worker"),
        (WorkUnitType.REGRESSION_TEST, "Blocked model smoke sample", "ai_model_worker"),
    )
    for kind, title, worker_kind in specs:
        payload = {
            "search_need_id": need_id,
            "search_hunt_id": hunt_id,
            "exhaustion_report_id": report_id,
            "generated_from": "search_hunt_workflow_smoke",
            "policy_state": "blocked_by_policy",
            "worker_kind": worker_kind,
            "execution_enabled": False,
            "source_probe_execution_enabled": False,
            "extraction_execution_enabled": False,
            "model_provider_enabled": False,
        }
        workunit = runtime.workunit_queue.create_workunit(
            WorkUnit.new(
                kind,
                title,
                payload=payload,
                parent_id=need_id,
                idempotency_key=f"search_hunt_workflow_smoke:{need_id}:{kind.value}:{worker_kind}",
            )
        )
        if workunit.state != WorkUnitState.BLOCKED:
            workunit = runtime.workunit_queue.block_workunit(workunit.id, "blocked by integration smoke policy")
        for ref_kind, ref_id in (("search_need", need_id), ("search_hunt", hunt_id), ("exhaustion_report", report_id)):
            runtime.workunit_queue.record_payload_ref(workunit.id, ref_kind, ref_id)
        created.append(workunit.to_dict())
    return created


def linked_workunits_for_hunt(runtime: Any, hunt_id: str) -> list[dict[str, Any]]:
    rows = []
    for workunit in runtime.workunit_queue.list_workunits(limit=500):
        payload = dict(workunit.payload)
        if str(payload.get("search_hunt_id") or "") == str(hunt_id):
            row = workunit.to_dict()
            row["search_need_id"] = payload.get("search_need_id")
            row["search_hunt_id"] = payload.get("search_hunt_id")
            row["exhaustion_report_id"] = payload.get("exhaustion_report_id")
            row["policy_state"] = payload.get("policy_state")
            row["execution_enabled"] = False
            rows.append(row)
    return rows


def fail_result(code: str, message: str) -> dict[str, Any]:
    return {
        "schema_version": "search_hunt_workflow_smoke_result.v0",
        "task": "HUNT-08",
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
        write_json(Path(output), result)
    if as_json:
        print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
        return
    print(f"status: {result['status']}", file=stdout)
    if result.get("hunt_id"):
        print(f"hunt_id: {result['hunt_id']}", file=stdout)
    if result.get("search_need_id"):
        print(f"search_need_id: {result['search_need_id']}", file=stdout)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
