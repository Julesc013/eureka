#!/usr/bin/env python3
"""Validate HUNT-to-main promotion evidence."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
TASK = "HUNT-TO-MAIN-PROMOTION-REVIEW"
PASS_STATUSES = {"pass"}

INVENTORIES = {
    "control/inventory/hunt_main_promotion_input_state.json": "hunt_main_promotion_input_state.v0",
    "control/inventory/hunt_main_promotion_gate_matrix.json": "hunt_main_promotion_gate_matrix.v0",
    "control/inventory/hunt_main_promotion_validation_matrix.json": "hunt_main_promotion_validation_matrix.v0",
    "control/inventory/hunt_main_promotion_warning_disposition.json": "hunt_main_promotion_warning_disposition.v0",
    "control/inventory/hunt_main_promotion_blocker_register.json": "hunt_main_promotion_blocker_register.v0",
    "control/inventory/hunt_main_promotion_branch_plan.json": "hunt_main_promotion_branch_plan.v0",
    "control/inventory/hunt_main_promotion_result.json": "hunt_main_promotion_result.v0",
    "control/inventory/hunt_main_post_promotion_state.json": "hunt_main_post_promotion_state.v0",
    "control/inventory/hunt_main_next_task_decision.json": "hunt_main_next_task_decision.v0",
}

AUDIT_ROOT = Path("control/audits/hunt-to-main-promotion-review-v0")
AUDIT_FILES = (
    "README.md",
    "hunt_main_promotion_report.json",
    "input_state.md",
    "gate_matrix.md",
    "validation_matrix.md",
    "warning_disposition.md",
    "blocker_register.md",
    "branch_plan.md",
    "promotion_result.md",
    "post_promotion_state.md",
    "next_task_decision.md",
    "validation.md",
    "generated/sample_gate_matrix.json",
    "generated/sample_promotion_result.json",
    "generated/sample_post_promotion_state.json",
    "generated/sample_summary.md",
)

FORBIDDEN_TRUE_FIELDS = (
    "force_push_performed",
    "history_rewrite_performed",
    "source_probe_executed",
    "extraction_executed",
    "model_provider_used",
    "download_install_execute_performed",
    "master_index_mutated",
    "site_dist_mutated",
    "deployment_performed",
    "production_readiness_claimed",
    "public_launch_readiness_claimed",
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    report = validate(Path(args.repo_root).resolve())
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True), file=stdout)
    else:
        print("HUNT main promotion validation", file=stdout)
        print(f"status: {report['status']}", file=stdout)
        for error in report["errors"]:
            print(f"ERROR: {error}", file=stdout)
    return 0 if report["status"] in PASS_STATUSES else 1


def validate(root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    payloads = {rel: load_json(root / rel, schema, errors) for rel, schema in INVENTORIES.items()}
    audit_report = load_json(
        root / AUDIT_ROOT / "hunt_main_promotion_report.json",
        "hunt_main_promotion_report.v0",
        errors,
    )
    validate_audit_pack(root, errors)
    validate_result(payloads.get("control/inventory/hunt_main_promotion_result.json", {}), errors)
    validate_result(audit_report, errors, label="audit report")
    validate_gates(payloads.get("control/inventory/hunt_main_promotion_gate_matrix.json", {}), errors)
    validate_branch_plan(payloads.get("control/inventory/hunt_main_promotion_branch_plan.json", {}), errors)
    validate_post_state(payloads.get("control/inventory/hunt_main_post_promotion_state.json", {}), errors)
    validate_next_decision(payloads.get("control/inventory/hunt_main_next_task_decision.json", {}), errors)
    validate_live_branch_equality(root, payloads.get("control/inventory/hunt_main_promotion_result.json", {}), errors)
    return {
        "schema_version": "hunt_main_promotion_validation.v0",
        "task": TASK,
        "status": "pass" if not errors else "fail",
        "errors": errors,
    }


def validate_result(payload: Mapping[str, Any], errors: list[str], *, label: str = "result") -> None:
    required_true = (
        "promotion_review_completed",
        "promotion_gates_passed",
        "dev_pushed",
        "main_promoted",
        "origin_main_equals_origin_dev",
        "fast_forward_only",
    )
    if payload.get("status") != "pass":
        errors.append(f"{label} status must be pass")
    if payload.get("hard_blockers_remaining") != 0:
        errors.append(f"{label} hard blockers must be zero")
    if payload.get("warnings_remaining") != 0:
        errors.append(f"{label} warnings must be zero")
    for field in required_true:
        if payload.get(field) is not True:
            errors.append(f"{label} {field} must be true")
    for field in FORBIDDEN_TRUE_FIELDS:
        if payload.get(field) is not False:
            errors.append(f"{label} {field} must be false")
    if "SYN-00" not in str(payload.get("recommended_next_task", "")):
        errors.append(f"{label} must recommend SYN-00")


def validate_gates(payload: Mapping[str, Any], errors: list[str]) -> None:
    gates = payload.get("gates")
    if not isinstance(gates, list) or not gates:
        errors.append("gate matrix must include gates")
        return
    for gate in gates:
        if not isinstance(gate, dict):
            errors.append("gate matrix contains non-object row")
            continue
        if gate.get("blocks_promotion") and gate.get("status") != "pass":
            errors.append(f"promotion gate failed: {gate.get('gate_id')}")


def validate_branch_plan(payload: Mapping[str, Any], errors: list[str]) -> None:
    expectations = {
        "target_branch": "main",
        "promotion_method": "fast_forward_only",
        "source_branch_must_be_pushed_first": True,
        "force_push_allowed": False,
        "history_rewrite_allowed": False,
        "rebase_allowed": False,
        "squash_allowed": False,
        "branch_mutation_planned": True,
        "requires_manual_merge": False,
    }
    for field, expected in expectations.items():
        if payload.get(field) != expected:
            errors.append(f"branch plan {field} must be {expected!r}")
    if payload.get("promotion_source_branch") != "dev":
        errors.append("branch plan promotion source must be dev")


def validate_post_state(payload: Mapping[str, Any], errors: list[str]) -> None:
    if payload.get("expected_origin_main_equals_origin_dev") is not True:
        errors.append("post promotion state must expect origin/main == origin/dev")
    if payload.get("expected_fast_forward_only") is not True:
        errors.append("post promotion state must require fast-forward-only")


def validate_next_decision(payload: Mapping[str, Any], errors: list[str]) -> None:
    if "SYN-00" not in str(payload.get("recommended_next_task", "")):
        errors.append("next decision must recommend SYN-00")
    if payload.get("main_promoted") is not True:
        errors.append("next decision must record main_promoted true")
    if payload.get("syn_can_start") is not True:
        errors.append("next decision must allow SYN start")
    if payload.get("f0_recommended_now") is not False:
        errors.append("next decision must keep F0 not recommended now")


def validate_live_branch_equality(root: Path, result: Mapping[str, Any], errors: list[str]) -> None:
    if not (root / ".git").exists() or result.get("main_promoted") is not True:
        return
    if current_queue_has_advanced_past_hunt_promotion(root):
        return
    origin_main = run_git(root, "rev-parse", "origin/main")
    origin_dev = run_git(root, "rev-parse", "origin/dev")
    if origin_main and origin_dev and origin_main != origin_dev:
        errors.append("live git refs show origin/main and origin/dev differ")
    divergence = run_git(root, "rev-list", "--left-right", "--count", "origin/main...origin/dev")
    if divergence and divergence.strip() != "0\t0":
        errors.append(f"live git refs still diverge: {divergence}")


def current_queue_has_advanced_past_hunt_promotion(root: Path) -> bool:
    queue_path = root / ".aide/queue/index.yaml"
    if not queue_path.is_file():
        return False
    for line in queue_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped.startswith("current_recommended_task:"):
            continue
        current = stripped.split(":", 1)[1].strip()
        return current.startswith(
            (
                "DEV-AND-IA-",
                "IA-",
                "WORKBENCH-",
                "SEARCH-",
                "SYN-",
                "F0-",
            )
        )
    return False


def validate_audit_pack(root: Path, errors: list[str]) -> None:
    for rel in AUDIT_FILES:
        if not (root / AUDIT_ROOT / rel).is_file():
            errors.append(f"missing audit file: {AUDIT_ROOT / rel}")


def load_json(path: Path, schema: str, errors: list[str]) -> dict[str, Any]:
    if not path.is_file():
        errors.append(f"missing file: {path}")
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"invalid json {path}: {exc}")
        return {}
    if payload.get("schema_version") != schema:
        errors.append(f"{path} schema_version must be {schema}")
    return payload


def run_git(root: Path, *args: str) -> str:
    completed = subprocess.run(["git", *args], cwd=root, text=True, capture_output=True, check=False)
    return completed.stdout.strip()


if __name__ == "__main__":
    raise SystemExit(main())
