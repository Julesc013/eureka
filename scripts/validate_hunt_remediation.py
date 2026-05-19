#!/usr/bin/env python3
"""Validate Search Hunt remediation evidence."""

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


TASK_ID = "HUNT-REMEDIATION"
PASS_STATUSES = {"pass"}

INVENTORIES = {
    "control/inventory/hunt_remediation_state_diagnosis.json": "hunt_remediation_state_diagnosis.v0",
    "control/inventory/hunt_remediation_blocker_register.json": "hunt_remediation_blocker_register.v0",
    "control/inventory/hunt_remediation_warning_disposition.json": "hunt_remediation_warning_disposition.v0",
    "control/inventory/hunt_remediation_repair_result.json": "hunt_remediation_repair_result.v0",
    "control/inventory/hunt_remediation_boundary_audit.json": "hunt_remediation_boundary_audit.v0",
    "control/inventory/hunt_remediation_validation_matrix.json": "hunt_remediation_validation_matrix.v0",
    "control/inventory/hunt_remediation_smoke_result.json": "hunt_remediation_smoke_result.v0",
    "control/inventory/hunt_remediation_result.json": "hunt_remediation_result.v0",
    "control/inventory/hunt_remediation_next_task_decision.json": "hunt_remediation_next_task_decision.v0",
}

AUDIT_ROOT = Path("control/audits/hunt-remediation-v0")
AUDIT_FILES = (
    "README.md",
    "hunt_remediation_report.json",
    "state_diagnosis.md",
    "blocker_register.md",
    "warning_disposition.md",
    "repair_result.md",
    "boundary_audit.md",
    "validation_matrix.md",
    "smoke_result.md",
    "next_task_decision.md",
    "validation.md",
    "generated/sample_hunt_remediation_result.json",
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
        print("HUNT remediation validation", file=stdout)
        print(f"status: {result['status']}", file=stdout)
        for error in result["errors"]:
            print(f"ERROR: {error}", file=stdout)
    return 0 if result["status"] in PASS_STATUSES else 1


def validate(root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    payloads = {rel: load_json(root / rel, schema, errors) for rel, schema in INVENTORIES.items()}
    report = load_json(root / AUDIT_ROOT / "hunt_remediation_report.json", "hunt_remediation_report.v0", errors)
    validate_audit_pack(root, errors)
    validate_remediation_payload(payloads.get("control/inventory/hunt_remediation_result.json", {}), errors)
    validate_remediation_payload(report, errors, label="audit report")
    validate_supporting_payloads(payloads, errors)
    validate_closeout_state(root, errors)
    validate_queue(root, errors)
    status = "fail" if errors else "pass"
    return {
        "schema_version": "hunt_remediation_validation.v0",
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


def validate_remediation_payload(payload: Mapping[str, Any], errors: list[str], *, label: str = "remediation result") -> None:
    expected_true = (
        "all_hunt_tasks_reviewed",
        "all_hunt_validators_pass",
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
    if "SYN-00" not in str(payload.get("recommended_next_task", "")):
        errors.append(f"{label} must recommend SYN-00")


def validate_supporting_payloads(payloads: Mapping[str, Mapping[str, Any]], errors: list[str]) -> None:
    diagnosis = payloads.get("control/inventory/hunt_remediation_state_diagnosis.json", {})
    tasks = diagnosis.get("tasks")
    if not isinstance(tasks, list) or len(tasks) < 13:
        errors.append("state diagnosis must cover HUNT-00 through HUNT-12")
    for row in tasks or []:
        if isinstance(row, Mapping) and row.get("classification") != "pass":
            errors.append(f"task did not classify as pass: {row.get('task_id')}")

    blockers = payloads.get("control/inventory/hunt_remediation_blocker_register.json", {})
    if blockers.get("hard_blockers_remaining") != 0 or blockers.get("blockers") != []:
        errors.append("remediation blocker register must be empty")

    warnings = payloads.get("control/inventory/hunt_remediation_warning_disposition.json", {})
    if warnings.get("warnings_remaining") != 0 or warnings.get("all_warnings_disposed") is not True:
        errors.append("remediation warnings must be fully disposed")

    validation = payloads.get("control/inventory/hunt_remediation_validation_matrix.json", {})
    for key in (
        "all_hunt_validators_pass",
        "hunt_workflow_smoke_pass",
        "full_unittest_discovery_pass",
        "generated_artifact_cleanliness_pass",
        "architecture_boundaries_pass",
        "runtime_leakage_gate_pass",
    ):
        if validation.get(key) is not True:
            errors.append(f"validation matrix {key} must be true")

    boundary = payloads.get("control/inventory/hunt_remediation_boundary_audit.json", {})
    for key in (
        "source_probe_executed",
        "extraction_executed",
        "model_provider_used",
        "download_install_execute_performed",
        "master_index_mutated",
        "site_dist_mutated",
        "deployment_performed",
        "production_readiness_claimed",
        "public_launch_readiness_claimed",
    ):
        if boundary.get(key) is not False:
            errors.append(f"boundary audit {key} must be false")

    decision = payloads.get("control/inventory/hunt_remediation_next_task_decision.json", {})
    if "SYN-00" not in str(decision.get("recommended_next_task", "")):
        errors.append("remediation next task decision must recommend SYN-00")
    if decision.get("f0_recommended_now") is not False:
        errors.append("remediation next task decision must keep F0 not recommended by default")


def validate_closeout_state(root: Path, errors: list[str]) -> None:
    audit = audit_closeout(root)
    if audit.get("status") != "pass":
        errors.append("Search Hunt closeout audit must pass after remediation")
    closeout = load_json(root / "control/inventory/search_hunt_closeout_result.json", "search_hunt_closeout_result.v0", errors)
    if closeout.get("status") != "pass":
        errors.append("Search Hunt closeout result must be pass after remediation")
    if closeout.get("warnings_remaining") != 0 or closeout.get("hard_blockers_remaining") != 0:
        errors.append("Search Hunt closeout must have zero warnings and hard blockers")


def validate_queue(root: Path, errors: list[str]) -> None:
    index = root / ".aide/queue/index.yaml"
    text = index.read_text(encoding="utf-8") if index.is_file() else ""
    if not queue_preserves_hunt_handoff(root, text):
        errors.append(
            "queue must recommend SYN-00, gated HUNT-TO-MAIN-PROMOTION-REVIEW, "
            "or the dev/IA promotion repair lane"
        )
    if "id: HUNT-REMEDIATION" not in text or "status: completed" not in text:
        errors.append("queue must mark HUNT-REMEDIATION completed")


def queue_preserves_hunt_handoff(root: Path, queue_text: str) -> bool:
    if "current_recommended_task: SYN-00" in queue_text:
        return True
    if "current_recommended_task: DEV-AND-IA-PROMOTION-BLOCKER-01" in queue_text:
        return True
    if "current_recommended_task: DEV-AND-IA-TO-MAIN-PROMOTION-REVIEW" in queue_text:
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
