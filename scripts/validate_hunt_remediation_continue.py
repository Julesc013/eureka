#!/usr/bin/env python3
"""Validate Search Hunt remediation continuation evidence."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.audit_search_hunt_closeout import audit_closeout
from scripts.hunt_queue_progress import current_recommended_task_id, post_hunt_current_allowed
from scripts.validate_hunt_remediation import validate as validate_previous_remediation


TASK_ID = "HUNT-REMEDIATION-CONTINUE"
PASS_STATUSES = {"pass"}

INVENTORIES = {
    "control/inventory/hunt_remediation_continue_input_state.json": "hunt_remediation_continue_input_state.v0",
    "control/inventory/hunt_remediation_continue_issue_register.json": "hunt_remediation_continue_issue_register.v0",
    "control/inventory/hunt_remediation_continue_repair_result.json": "hunt_remediation_continue_repair_result.v0",
    "control/inventory/hunt_remediation_continue_validation_matrix.json": "hunt_remediation_continue_validation_matrix.v0",
    "control/inventory/hunt_remediation_continue_smoke_result.json": "hunt_remediation_continue_smoke_result.v0",
    "control/inventory/hunt_remediation_continue_boundary_audit.json": "hunt_remediation_continue_boundary_audit.v0",
    "control/inventory/hunt_remediation_continue_result.json": "hunt_remediation_continue_result.v0",
    "control/inventory/hunt_remediation_continue_next_task_decision.json": "hunt_remediation_continue_next_task_decision.v0",
}

AUDIT_ROOT = Path("control/audits/hunt-remediation-continue-v0")
AUDIT_FILES = (
    "README.md",
    "hunt_remediation_continue_report.json",
    "input_state.md",
    "issue_register.md",
    "repair_result.md",
    "boundary_audit.md",
    "validation_matrix.md",
    "smoke_result.md",
    "updated_handoff.md",
    "next_task_decision.md",
    "validation.md",
    "generated/sample_hunt_remediation_continue_result.json",
    "generated/sample_issue_register.json",
    "generated/sample_validation_matrix.json",
    "generated/sample_summary.md",
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--output")
    args = parser.parse_args(argv)

    result = validate(Path(args.repo_root).resolve())
    if args.output:
        write_json(Path(args.output), result)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    else:
        print("HUNT remediation continuation validation", file=stdout)
        print(f"status: {result['status']}", file=stdout)
        for error in result["errors"]:
            print(f"ERROR: {error}", file=stdout)
    return 0 if result["status"] in PASS_STATUSES else 1


def validate(root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    payloads = {rel: load_json(root / rel, schema, errors) for rel, schema in INVENTORIES.items()}
    report = load_json(
        root / AUDIT_ROOT / "hunt_remediation_continue_report.json",
        "hunt_remediation_continue_report.v0",
        errors,
    )
    validate_audit_pack(root, errors)
    validate_continue_payload(payloads.get("control/inventory/hunt_remediation_continue_result.json", {}), errors)
    validate_continue_payload(report, errors, label="audit report")
    validate_supporting_payloads(payloads, errors)
    validate_previous_state(root, errors)
    validate_closeout_state(root, errors)
    validate_queue(root, errors)
    status = "fail" if errors else "pass"
    return {
        "schema_version": "hunt_remediation_continue_validation.v0",
        "task": TASK_ID,
        "status": status,
        "errors": errors,
        "warnings": [],
        "source_probe_executed": False,
        "extraction_executed": False,
        "model_provider_used": False,
        "download_install_execute_performed": False,
        "master_index_mutated": False,
        "site_dist_mutated": False,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }


def validate_continue_payload(payload: Mapping[str, Any], errors: list[str], *, label: str = "continuation result") -> None:
    expected_true = (
        "all_remaining_issues_reviewed",
        "all_hunt_validators_pass",
        "all_local_dependency_validators_pass",
        "hunt_workflow_smoke_pass",
        "full_unittest_discovery_pass",
        "generated_artifact_cleanliness_pass",
        "architecture_boundaries_pass",
        "runtime_leakage_gate_pass",
        "syn_can_start",
        "f0_can_resume",
    )
    for key in expected_true:
        if payload.get(key) is not True:
            errors.append(f"{label} {key} must be true")
    expected_false = (
        "source_probe_executed",
        "extraction_executed",
        "model_provider_used",
        "download_install_execute_performed",
        "master_index_mutated",
        "site_dist_mutated",
        "deployment_performed",
        "production_readiness_claimed",
        "public_launch_readiness_claimed",
        "f0_recommended_now",
    )
    for key in expected_false:
        if payload.get(key) is not False:
            errors.append(f"{label} {key} must be false")
    if payload.get("status") != "pass":
        errors.append(f"{label} status must be pass")
    if payload.get("hard_blockers_remaining") != 0:
        errors.append(f"{label} hard blockers must be zero")
    if payload.get("warnings_remaining") != 0:
        errors.append(f"{label} warnings must be zero")
    if int(payload.get("child_tasks_created", 0) or 0) != 0:
        errors.append(f"{label} child tasks created must be zero")
    if "SYN-00" not in str(payload.get("recommended_next_task", "")):
        errors.append(f"{label} must recommend SYN-00")


def validate_supporting_payloads(payloads: Mapping[str, Mapping[str, Any]], errors: list[str]) -> None:
    input_state = payloads.get("control/inventory/hunt_remediation_continue_input_state.json", {})
    if input_state.get("previous_remediation_found") is not True:
        errors.append("continuation input state must find previous remediation")
    if input_state.get("previous_status") != "pass":
        errors.append("continuation input state previous status must be pass")
    if input_state.get("previous_hard_blockers") != 0 or input_state.get("previous_warnings") != 0:
        errors.append("continuation input state must start from zero blockers and warnings")
    if input_state.get("state_reconstructed") is not False:
        errors.append("continuation input state should not require reconstruction")

    issue_register = payloads.get("control/inventory/hunt_remediation_continue_issue_register.json", {})
    if issue_register.get("all_remaining_issues_reviewed") is not True:
        errors.append("continuation issue register must review all remaining issues")
    if issue_register.get("hard_blockers_remaining") != 0 or issue_register.get("warnings_remaining") != 0:
        errors.append("continuation issue register must have zero blockers and warnings")
    if issue_register.get("issues") != []:
        errors.append("continuation issue register must have no open issues")

    repair = payloads.get("control/inventory/hunt_remediation_continue_repair_result.json", {})
    if repair.get("issues_remaining") != []:
        errors.append("continuation repair result must have no remaining issues")
    if repair.get("child_tasks_created") != []:
        errors.append("continuation repair result must not create child tasks")
    if repair.get("unsafe_repairs_deferred") != []:
        errors.append("continuation repair result must not defer unsafe repairs")
    if repair.get("policy_weakened") is not False:
        errors.append("continuation repair result must not weaken policy")
    if repair.get("forbidden_side_effects_introduced") is not False:
        errors.append("continuation repair result must not introduce forbidden side effects")

    validation = payloads.get("control/inventory/hunt_remediation_continue_validation_matrix.json", {})
    for key in (
        "all_hunt_validators_pass",
        "all_local_dependency_validators_pass",
        "hunt_workflow_smoke_pass",
        "full_unittest_discovery_pass",
        "generated_artifact_cleanliness_pass",
        "architecture_boundaries_pass",
        "runtime_leakage_gate_pass",
    ):
        if validation.get(key) is not True:
            errors.append(f"continuation validation matrix {key} must be true")

    smoke = payloads.get("control/inventory/hunt_remediation_continue_smoke_result.json", {})
    for key in (
        "hunt_workflow_smoke_pass",
        "demo_search_hunt_workflow_pass",
        "background_hunt_runner_demo_pass",
        "hunt_replay_demo_pass",
        "ai_escalation_demo_pass",
        "hunt_workbench_smoke_pass",
        "api_smoke_pass",
        "local_auto_test_pass",
    ):
        if smoke.get(key) is not True:
            errors.append(f"continuation smoke result {key} must be true")

    boundary = payloads.get("control/inventory/hunt_remediation_continue_boundary_audit.json", {})
    for key in (
        "source_probe_executed",
        "extraction_executed",
        "model_provider_used",
        "agent_research_executed",
        "external_internet_search_used",
        "download_install_execute_performed",
        "source_sync_performed",
        "master_index_mutated",
        "site_dist_mutated",
        "deployment_performed",
        "production_readiness_claimed",
        "public_launch_readiness_claimed",
    ):
        if boundary.get(key) is not False:
            errors.append(f"continuation boundary audit {key} must be false")

    decision = payloads.get("control/inventory/hunt_remediation_continue_next_task_decision.json", {})
    if "SYN-00" not in str(decision.get("recommended_next_task", "")):
        errors.append("continuation next task decision must recommend SYN-00")
    if decision.get("f0_can_resume") is not True or decision.get("f0_recommended_now") is not False:
        errors.append("continuation next task decision must keep F0 resumable but not recommended")
    if decision.get("main_promotion_review_required") is not True:
        errors.append("continuation next task decision must require main promotion review")


def validate_previous_state(root: Path, errors: list[str]) -> None:
    previous = validate_previous_remediation(root)
    if previous.get("status") != "pass":
        errors.append("previous HUNT remediation validator must still pass")


def validate_closeout_state(root: Path, errors: list[str]) -> None:
    audit = audit_closeout(root)
    if audit.get("status") != "pass":
        errors.append("Search Hunt closeout audit must pass after continuation")
    closeout = load_json(root / "control/inventory/search_hunt_closeout_result.json", "search_hunt_closeout_result.v0", errors)
    if closeout.get("status") != "pass":
        errors.append("Search Hunt closeout result must remain pass")
    if closeout.get("warnings_remaining") != 0 or closeout.get("hard_blockers_remaining") != 0:
        errors.append("Search Hunt closeout must keep zero warnings and hard blockers")


def validate_queue(root: Path, errors: list[str]) -> None:
    index = root / ".aide/queue/index.yaml"
    text = index.read_text(encoding="utf-8") if index.is_file() else ""
    if not queue_preserves_hunt_handoff(root, text):
        errors.append(
            "queue must recommend SYN-00, DOMAIN-00, gated HUNT-TO-MAIN-PROMOTION-REVIEW, "
            "or the dev/IA promotion repair lane"
        )
    if "id: HUNT-REMEDIATION-CONTINUE" not in text or "status: completed" not in text:
        errors.append("queue must mark HUNT-REMEDIATION-CONTINUE completed")
    if not (root / ".aide/queue/HUNT-REMEDIATION-CONTINUE/task.yaml").is_file():
        errors.append("missing queue task stub: .aide/queue/HUNT-REMEDIATION-CONTINUE/task.yaml")


def queue_preserves_hunt_handoff(root: Path, queue_text: str) -> bool:
    if current_recommended_task_id(root) == "F0-00" and post_hunt_current_allowed(root):
        return True
    if "current_recommended_task: SYN-00" in queue_text:
        return True
    if "current_recommended_task: DOMAIN-00" in queue_text:
        return True
    if "current_recommended_task: SCOUT-SCHEMA-00" in queue_text:
        return True
    if "current_recommended_task: DEV-AND-IA-PROMOTION-BLOCKER-01" in queue_text:
        return True
    if "current_recommended_task: DEV-AND-IA-TO-MAIN-PROMOTION-REVIEW" in queue_text:
        return True
    if "current_recommended_task: REPO-LAYOUT-CANON-01" in queue_text:
        return True
    if "current_recommended_task: IA-HUNT-BRIDGE-00" in queue_text:
        return True
    if "current_recommended_task: HUNT-TO-MAIN-PROMOTION-REVIEW" not in queue_text:
        return False
    aide = load_json(root / "control/inventory/aide_eval_green_result.json", "aide_eval_green_result.v0", [])
    closeout = load_json(root / "control/inventory/search_hunt_closeout_result.json", "search_hunt_closeout_result.v0", [])
    return (
        aide.get("aide_eval_green") is True
        and aide.get("eval_fail_count_after") == 0
        and aide.get("product_behavior_changed") is False
        and closeout.get("syn_can_start") is True
        and closeout.get("hard_blockers_remaining") == 0
    )


def validate_audit_pack(root: Path, errors: list[str]) -> None:
    for rel in AUDIT_FILES:
        path = root / AUDIT_ROOT / rel
        if not path.is_file():
            errors.append(f"missing audit file: {(AUDIT_ROOT / rel).as_posix()}")
        elif path.stat().st_size == 0:
            errors.append(f"empty audit file: {(AUDIT_ROOT / rel).as_posix()}")


def load_json(path: Path, schema_version: str, errors: list[str]) -> dict[str, Any]:
    if not path.is_file():
        errors.append(f"missing JSON file: {path.as_posix()}")
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"invalid JSON {path.as_posix()}: {exc}")
        return {}
    if not isinstance(payload, dict):
        errors.append(f"JSON root must be object: {path.as_posix()}")
        return {}
    if payload.get("schema_version") != schema_version:
        errors.append(f"{path.as_posix()} schema_version must be {schema_version}")
    return payload


def write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
