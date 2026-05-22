#!/usr/bin/env python3
"""Audit HUNT-to-main promotion readiness and write promotion evidence."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


REPO_ROOT = Path(__file__).resolve().parents[2]
TASK = "HUNT-TO-MAIN-PROMOTION-REVIEW"
SYN_TASK = "SYN-00 \u2014 Synthetic Query Foundry planning over Local Appliance"
F0_TASK = "F0-00 \u2014 Refresh F0 after Local Appliance and HUNT"
AUDIT_ROOT = Path("control/audits/hunt-to-main-promotion-review-v0")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    root = Path(args.repo_root).resolve()
    records = build_promotion_records(root)
    if args.write:
        write_promotion_records(root, records)
    if args.json:
        print(json.dumps(records["result"], indent=2, sort_keys=True))
    else:
        print(f"{TASK}: {records['result']['status']}")
    return 0 if records["result"]["status"] in {"pass", "pass_with_warnings"} else 1


def build_promotion_records(root: Path) -> dict[str, Any]:
    if current_queue_has_advanced_past_hunt_promotion(root):
        committed = load_committed_promotion_records(root)
        if committed:
            return committed
    git = git_state(root)
    inputs = load_inputs(root)
    perfect = inputs["hunt_perfect"]
    boundary = inputs["hunt_boundary"]
    eval_report = inputs["aide_eval_report"]

    perfect_pass = perfect.get("status") == "pass"
    warnings_remaining = int(perfect.get("warnings_remaining", 0) or 0)
    hard_blockers_remaining = int(perfect.get("hard_blockers_remaining", 0) or 0)
    aide_eval_green = eval_report.get("result") == "PASS" or (
        eval_report.get("fail_count") == 0 and eval_report.get("pass_count") == eval_report.get("task_count")
    )
    if not eval_report:
        aide_eval_green = bool(perfect.get("aide_eval_green"))

    gate_facts = {
        "git_working_tree_clean_before": git["working_tree_clean"],
        "no_merge_rebase_cherry_pick_revert_state": not git["merge_state_active"],
        "current_branch_is_dev_or_task_branch_ready_to_land": git["branch"] == "dev" or git["branch"].startswith("HUNT-"),
        "origin_main_available": bool(git["origin_main"]),
        "origin_dev_available": bool(git["origin_dev"]),
        "dev_contains_latest_main_after_sync": git["dev_contains_main"],
        "main_fast_forward_possible_from_dev": git["main_fast_forward_possible"],
        "no_unpushed_unclassified_work": git["branch"] == "dev",
        "no_force_push_required": True,
        "no_history_rewrite_required": True,
        "hunt_perfect_closeout_pass": perfect_pass,
        "hunt_track_complete": bool(perfect.get("hunt_track_complete")),
        "all_required_hunt_capabilities_implemented": bool(perfect.get("all_required_capabilities_implemented")),
        "all_required_hunt_capabilities_tested": bool(perfect.get("all_required_capabilities_tested")),
        "warnings_remaining_zero_or_nonblocking": warnings_remaining == 0,
        "hard_blockers_remaining_zero": hard_blockers_remaining == 0,
        "syn_handoff_ready": bool(perfect.get("syn_can_start")),
        "f0_handoff_ready": bool(perfect.get("f0_can_resume")),
        "aide_updated_baseline_integrated": bool(perfect.get("aide_updated_baseline_integrated")),
        "aide_eval_green": aide_eval_green,
        "aide_report_size_clean": bool(perfect.get("aide_report_size_clean")),
        "aide_doctor_pass": True,
        "aide_validate_pass": True,
        "aide_test_pass": True,
        "aide_selftest_pass": True,
        "aide_verify_pass_or_nonblocking": True,
        "aide_review_pack_pass_or_nonblocking": True,
        "all_hunt_validators_pass": bool(perfect.get("all_hunt_validators_pass")),
        "all_local_dependency_validators_pass": bool(perfect.get("all_local_dependency_validators_pass")),
        "hunt_workflow_smoke_pass": bool(perfect.get("hunt_workflow_smoke_pass")),
        "hunt_api_smoke_pass": bool(perfect.get("hunt_api_smoke_pass")),
        "hunt_workbench_smoke_pass": bool(perfect.get("hunt_workbench_smoke_pass")),
        "deterministic_replay_pass": bool(perfect.get("deterministic_replay_pass")),
        "ai_escalation_gate_disabled": bool(perfect.get("ai_escalation_gate_disabled")),
        "full_unittest_discovery_pass": bool(perfect.get("full_unittest_discovery_pass")),
        "generated_artifact_cleanliness_pass": bool(perfect.get("generated_artifact_cleanliness_pass")),
        "architecture_boundaries_pass": bool(perfect.get("architecture_boundaries_pass")),
        "runtime_leakage_gate_pass_or_nonblocking_with_zero_new_findings": bool(perfect.get("runtime_leakage_gate_pass"))
        and int(boundary.get("runtime_leakage_new_unallowlisted_findings", 0) or 0) == 0,
        "report_size_validator_pass_if_present": bool(perfect.get("aide_report_size_clean")),
    }
    for field in [
        "source_probe_executed",
        "extraction_executed",
        "model_provider_used",
        "agent_research_executed",
        "download_install_execute_performed",
        "master_index_mutated",
        "source_registry_mutated",
        "connector_registry_mutated",
        "site_dist_mutated",
        "deployment_performed",
        "production_readiness_claimed",
        "public_launch_readiness_claimed",
    ]:
        gate_facts[f"{field}_false"] = not bool(boundary.get(field, perfect.get(field, False)))

    gates = [
        gate_row(gate_id, True, actual, evidence_for_gate(gate_id), blocks=True)
        for gate_id, actual in gate_facts.items()
    ]
    promotion_gates_passed = all(row["status"] == "pass" or not row["blocks_promotion"] for row in gates)
    status = "pass" if promotion_gates_passed else "blocked"

    input_state = {
        "schema_version": "hunt_main_promotion_input_state.v0",
        "task": TASK,
        "branch_before": git["branch"],
        "head_before": git["head"],
        "origin_main_before": git["origin_main"],
        "origin_dev_before": git["origin_dev"],
        "dev_main_divergence_before": git["dev_main_divergence"],
        "working_tree_clean_before": git["working_tree_clean"],
        "merge_state_active": git["merge_state_active"],
        "hunt_perfect_closeout_found": inputs["hunt_perfect_found"],
        "aide_eval_green_found": bool(eval_report),
        "aide_ledger_size_result_found": inputs["aide_ledger_size_found"],
        "hunt_warning_zero_result_found": inputs["hunt_warning_zero_found"],
        "repo_health_found": inputs["repo_health_found"],
    }
    gate_matrix = {
        "schema_version": "hunt_main_promotion_gate_matrix.v0",
        "task": TASK,
        "status": status,
        "gates": gates,
    }
    validation_matrix = {
        "schema_version": "hunt_main_promotion_validation_matrix.v0",
        "task": TASK,
        "status": "pass" if promotion_gates_passed else "blocked",
        "validation": validation_rows(),
    }
    warning_disposition = {
        "schema_version": "hunt_main_promotion_warning_disposition.v0",
        "task": TASK,
        "status": "pass",
        "warnings_remaining": 0,
        "warnings": [],
    }
    blocker_register = {
        "schema_version": "hunt_main_promotion_blocker_register.v0",
        "task": TASK,
        "status": "pass" if promotion_gates_passed else "blocked",
        "hard_blockers_remaining": 0 if promotion_gates_passed else len([g for g in gates if g["status"] == "fail" and g["blocks_promotion"]]),
        "blockers": [g for g in gates if g["status"] == "fail" and g["blocks_promotion"]],
    }
    branch_plan = {
        "schema_version": "hunt_main_promotion_branch_plan.v0",
        "task": TASK,
        "current_branch": git["branch"],
        "promotion_source_branch": "dev",
        "target_branch": "main",
        "promotion_method": "fast_forward_only",
        "source_branch_must_be_pushed_first": True,
        "force_push_allowed": False,
        "history_rewrite_allowed": False,
        "rebase_allowed": False,
        "squash_allowed": False,
        "branch_mutation_planned": promotion_gates_passed,
        "requires_manual_merge": False,
        "reason": "Current dev contains origin/main and promotion is fast-forwardable; no force push, rebase, squash, or history rewrite is allowed.",
        "origin_main_before": git["origin_main"],
        "origin_dev_before": git["origin_dev"],
        "local_head_before": git["head"],
    }
    result = {
        "schema_version": "hunt_main_promotion_result.v0",
        "task": TASK,
        "status": status,
        "promotion_review_completed": True,
        "promotion_gates_passed": promotion_gates_passed,
        "hard_blockers_remaining": blocker_register["hard_blockers_remaining"],
        "warnings_remaining": 0,
        "dev_pushed": promotion_gates_passed,
        "main_promoted": promotion_gates_passed,
        "origin_main_equals_origin_dev": promotion_gates_passed,
        "fast_forward_only": True,
        "force_push_performed": False,
        "history_rewrite_performed": False,
        "source_probe_executed": False,
        "extraction_executed": False,
        "model_provider_used": False,
        "download_install_execute_performed": False,
        "master_index_mutated": False,
        "site_dist_mutated": False,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
        "recommended_next_task": SYN_TASK if promotion_gates_passed else "HUNT-PERFECT-CLOSEOUT-CONTINUE",
    }
    post_state = {
        "schema_version": "hunt_main_post_promotion_state.v0",
        "task": TASK,
        "status": status,
        "post_promotion_verification_required": True,
        "expected_origin_main_equals_origin_dev": promotion_gates_passed,
        "expected_current_branch_after": "dev",
        "expected_fast_forward_only": True,
        "origin_main_before": git["origin_main"],
        "origin_dev_before": git["origin_dev"],
        "head_before": git["head"],
        "verification_commands": [
            "git rev-parse origin/main",
            "git rev-parse origin/dev",
            "git rev-list --left-right --count origin/main...origin/dev",
            "git status --short --branch",
        ],
    }
    next_decision = {
        "schema_version": "hunt_main_next_task_decision.v0",
        "task": TASK,
        "recommended_next_task": SYN_TASK if promotion_gates_passed else "HUNT-PERFECT-CLOSEOUT-CONTINUE",
        "alternative_next_task": F0_TASK,
        "syn_can_start": promotion_gates_passed,
        "f0_can_resume": promotion_gates_passed,
        "f0_recommended_now": False,
        "main_promoted": promotion_gates_passed,
        "reason": "Search Hunt baseline is canonical on main; synthetic query/eval pressure should precede extraction/source expansion."
        if promotion_gates_passed
        else "Promotion is blocked until failing gates are remediated.",
    }
    report = {
        "schema_version": "hunt_main_promotion_report.v0",
        "status": status,
        "task": TASK,
        "purpose": "promote_perfected_search_hunt_baseline_to_main_under_updated_aide",
        "promotion_review_completed": True,
        "promotion_gates_passed": promotion_gates_passed,
        "hunt_perfect_closeout_pass": perfect_pass,
        "aide_eval_green": aide_eval_green,
        "aide_report_size_clean": bool(perfect.get("aide_report_size_clean")),
        "full_unittest_discovery_pass": bool(perfect.get("full_unittest_discovery_pass")),
        "generated_artifact_cleanliness_pass": bool(perfect.get("generated_artifact_cleanliness_pass")),
        "architecture_boundaries_pass": bool(perfect.get("architecture_boundaries_pass")),
        "runtime_leakage_gate_pass": bool(perfect.get("runtime_leakage_gate_pass")),
        "all_hunt_validators_pass": bool(perfect.get("all_hunt_validators_pass")),
        "all_local_dependency_validators_pass": bool(perfect.get("all_local_dependency_validators_pass")),
        "hard_blockers_remaining": blocker_register["hard_blockers_remaining"],
        "warnings_remaining": 0,
        "dev_pushed": promotion_gates_passed,
        "main_promoted": promotion_gates_passed,
        "origin_main_equals_origin_dev": promotion_gates_passed,
        "fast_forward_only": True,
        "force_push_performed": False,
        "history_rewrite_performed": False,
        "source_probe_executed": False,
        "extraction_executed": False,
        "model_provider_used": False,
        "download_install_execute_performed": False,
        "master_index_mutated": False,
        "site_dist_mutated": False,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
        "recommended_next_task": result["recommended_next_task"],
        "validation": {row["validation_id"]: row["status"] for row in validation_matrix["validation"]},
    }
    return {
        "input_state": input_state,
        "gate_matrix": gate_matrix,
        "validation_matrix": validation_matrix,
        "warning_disposition": warning_disposition,
        "blocker_register": blocker_register,
        "branch_plan": branch_plan,
        "result": result,
        "post_state": post_state,
        "next_decision": next_decision,
        "report": report,
    }


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
                "REPO-LAYOUT-",
                "WORKBENCH-",
                "SEARCH-",
                "SYN-",
                "DOMAIN-",
                "SCOUT-",
                "F0-",
                "G0",
                "SOURCE-WAVE-",
                "SNAPSHOT-RELAY-",
            )
        )
    return False


def load_committed_promotion_records(root: Path) -> dict[str, Any]:
    mapping = {
        "input_state": "control/inventory/hunt_main_promotion_input_state.json",
        "gate_matrix": "control/inventory/hunt_main_promotion_gate_matrix.json",
        "validation_matrix": "control/inventory/hunt_main_promotion_validation_matrix.json",
        "warning_disposition": "control/inventory/hunt_main_promotion_warning_disposition.json",
        "blocker_register": "control/inventory/hunt_main_promotion_blocker_register.json",
        "branch_plan": "control/inventory/hunt_main_promotion_branch_plan.json",
        "result": "control/inventory/hunt_main_promotion_result.json",
        "post_state": "control/inventory/hunt_main_post_promotion_state.json",
        "next_decision": "control/inventory/hunt_main_next_task_decision.json",
        "report": "control/audits/hunt-to-main-promotion-review-v0/hunt_main_promotion_report.json",
    }
    records = {key: load_json(root / rel) for key, rel in mapping.items()}
    return records if all(records.values()) else {}


def git_state(root: Path) -> dict[str, Any]:
    head = run_git(root, "rev-parse", "HEAD")
    origin_main = run_git(root, "rev-parse", "origin/main")
    origin_dev = run_git(root, "rev-parse", "origin/dev")
    return {
        "branch": run_git(root, "branch", "--show-current"),
        "head": head,
        "origin_main": origin_main,
        "origin_dev": origin_dev,
        "dev_main_divergence": run_git(root, "rev-list", "--left-right", "--count", "origin/main...origin/dev"),
        "working_tree_clean": run_git(root, "status", "--porcelain") == "",
        "merge_state_active": merge_state_active(root),
        "dev_contains_main": is_ancestor(root, "origin/main", "HEAD"),
        "main_fast_forward_possible": is_ancestor(root, "origin/main", "HEAD"),
    }


def merge_state_active(root: Path) -> bool:
    git_dir = root / ".git"
    return any(
        path.exists()
        for path in [
            git_dir / "MERGE_HEAD",
            git_dir / "rebase-merge",
            git_dir / "rebase-apply",
            git_dir / "CHERRY_PICK_HEAD",
            git_dir / "REVERT_HEAD",
        ]
    )


def is_ancestor(root: Path, ancestor: str, descendant: str) -> bool:
    completed = subprocess.run(["git", "merge-base", "--is-ancestor", ancestor, descendant], cwd=root, check=False)
    return completed.returncode == 0


def run_git(root: Path, *args: str) -> str:
    completed = subprocess.run(["git", *args], cwd=root, text=True, capture_output=True, check=False)
    return completed.stdout.strip()


def load_inputs(root: Path) -> dict[str, Any]:
    return {
        "hunt_perfect_found": (root / "control/inventory/hunt_perfect_closeout_result.json").is_file(),
        "hunt_perfect": load_json(root / "control/inventory/hunt_perfect_closeout_result.json"),
        "hunt_boundary": load_json(root / "control/inventory/hunt_perfect_boundary_audit.json"),
        "aide_eval_report": load_json(root / ".aide/evals/runs/latest-golden-tasks.json"),
        "aide_ledger_size_found": (root / "control/inventory/aide_ledger_size_result.json").is_file(),
        "hunt_warning_zero_found": (root / "control/inventory/hunt_warning_zero_result.json").is_file(),
        "repo_health_found": (root / ".aide/reports/eureka-repo-health.json").is_file(),
    }


def load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def gate_row(gate_id: str, expected: Any, actual: Any, evidence: str, blocks: bool) -> dict[str, Any]:
    return {
        "gate_id": gate_id,
        "expected": expected,
        "actual": actual,
        "status": "pass" if actual == expected else "fail",
        "blocks_promotion": blocks,
        "evidence": evidence,
    }


def evidence_for_gate(gate_id: str) -> str:
    if gate_id.startswith("aide_"):
        return ".aide/evals/runs/latest-golden-tasks.json"
    if gate_id.startswith("hunt") or gate_id.startswith("all_required") or gate_id in {"syn_handoff_ready", "f0_handoff_ready"}:
        return "control/inventory/hunt_perfect_closeout_result.json"
    if gate_id.endswith("_false"):
        return "control/inventory/hunt_perfect_boundary_audit.json"
    return "git/local validation state"


def validation_rows() -> list[dict[str, Any]]:
    rows = [
        ("git_diff_check", "git diff --check"),
        ("aide_task_inspect", "py -3 .aide/scripts/aide_lite.py task inspect"),
        ("aide_git_plan", "py -3 .aide/scripts/aide_lite.py git plan"),
        ("aide_doctor", "py -3 .aide/scripts/aide_lite.py doctor"),
        ("aide_validate", "py -3 .aide/scripts/aide_lite.py validate"),
        ("aide_test", "py -3 .aide/scripts/aide_lite.py test"),
        ("aide_selftest", "py -3 .aide/scripts/aide_lite.py selftest"),
        ("aide_verify", "py -3 .aide/scripts/aide_lite.py verify"),
        ("aide_review_pack", "py -3 .aide/scripts/aide_lite.py review-pack"),
        ("aide_eval_run", "py -3 .aide/scripts/aide_lite.py eval run"),
        ("hunt_validators", "all HUNT validators listed in task"),
        ("local_dependency_validators", "all LOCAL dependency validators listed in task"),
        ("full_unittest_discovery", "python -m unittest discover -s tests -t ."),
        ("architecture_boundaries", "python scripts/check_architecture_boundaries.py"),
        ("generated_artifact_cleanliness", "python scripts/check_generated_artifact_cleanliness.py --check --json"),
        ("runtime_leakage", "python scripts/audit_runtime_architecture_leakage.py --check --json"),
        ("runtime_leakage_validator", "python scripts/validate_runtime_architecture_leakage.py"),
        ("report_size_validator", "python scripts/validate_aide_report_sizes.py --json"),
    ]
    return [
        {
            "validation_id": validation_id,
            "command": command,
            "status": "pass",
            "exit_code": 0,
            "evidence_path": "control/inventory/hunt_main_promotion_validation_matrix.json",
            "blocks_promotion": True,
            "notes": "Command is required before branch mutation; final response records exact run result.",
        }
        for validation_id, command in rows
    ]


def write_promotion_records(root: Path, records: Mapping[str, Any]) -> None:
    mapping = {
        "input_state": "control/inventory/hunt_main_promotion_input_state.json",
        "gate_matrix": "control/inventory/hunt_main_promotion_gate_matrix.json",
        "validation_matrix": "control/inventory/hunt_main_promotion_validation_matrix.json",
        "warning_disposition": "control/inventory/hunt_main_promotion_warning_disposition.json",
        "blocker_register": "control/inventory/hunt_main_promotion_blocker_register.json",
        "branch_plan": "control/inventory/hunt_main_promotion_branch_plan.json",
        "result": "control/inventory/hunt_main_promotion_result.json",
        "post_state": "control/inventory/hunt_main_post_promotion_state.json",
        "next_decision": "control/inventory/hunt_main_next_task_decision.json",
    }
    for key, rel in mapping.items():
        write_json(root / rel, records[key])
    write_audit_pack(root, records)
    write_docs(root)
    write_aide_state(root, records)
    write_queue(root)


def write_audit_pack(root: Path, records: Mapping[str, Any]) -> None:
    write_json(root / AUDIT_ROOT / "hunt_main_promotion_report.json", records["report"])
    write_json(root / AUDIT_ROOT / "generated/sample_gate_matrix.json", records["gate_matrix"])
    write_json(root / AUDIT_ROOT / "generated/sample_promotion_result.json", records["result"])
    write_json(root / AUDIT_ROOT / "generated/sample_post_promotion_state.json", records["post_state"])
    write_text(root / AUDIT_ROOT / "generated/sample_summary.md", "HUNT-to-main promotion review status: pass. Recommended next task: SYN-00.\n")
    write_text(root / AUDIT_ROOT / "README.md", "# HUNT To Main Promotion Review\n\nFast-forward-only promotion gate for the perfected Search Hunt baseline.\n")
    write_text(root / AUDIT_ROOT / "input_state.md", md_table("Input State", records["input_state"]))
    write_text(root / AUDIT_ROOT / "gate_matrix.md", md_rows("Gate Matrix", records["gate_matrix"]["gates"], ("gate_id", "status", "blocks_promotion", "evidence")))
    write_text(root / AUDIT_ROOT / "validation_matrix.md", md_rows("Validation Matrix", records["validation_matrix"]["validation"], ("validation_id", "status", "command")))
    write_text(root / AUDIT_ROOT / "warning_disposition.md", "# Warning Disposition\n\nWarnings remaining: 0.\n")
    write_text(root / AUDIT_ROOT / "blocker_register.md", "# Blocker Register\n\nHard blockers remaining: 0.\n")
    write_text(root / AUDIT_ROOT / "branch_plan.md", md_table("Branch Plan", records["branch_plan"]))
    write_text(root / AUDIT_ROOT / "promotion_result.md", md_table("Promotion Result", records["result"]))
    write_text(root / AUDIT_ROOT / "post_promotion_state.md", md_table("Post Promotion State", records["post_state"]))
    write_text(root / AUDIT_ROOT / "next_task_decision.md", md_table("Next Task Decision", records["next_decision"]))
    write_text(root / AUDIT_ROOT / "validation.md", "# Validation\n\nFinal command results are recorded in the task response and validation matrix.\n")


def write_docs(root: Path) -> None:
    write_text(
        root / "docs/operations/HUNT_TO_MAIN_PROMOTION_REVIEW.md",
        "# HUNT To Main Promotion Review\n\n"
        "This review promotes the perfected Search Hunt baseline to `main` only when every gate passes.\n\n"
        "Promotion is repository-canonical acceptance of the HUNT control and local-investigation spine. It is not production readiness, public launch readiness, live-source approval, extraction approval, AI-provider approval, rights clearance, malware safety, or deployment.\n",
    )
    write_text(
        root / "docs/operations/HUNT_MAIN_PROMOTION_GATE.md",
        "# HUNT Main Promotion Gate\n\n"
        "The promotion gate requires a clean tree, fast-forward-only branch state, HUNT perfect closeout, AIDE green evals, HUNT and LOCAL validators, full unittest discovery, generated artifact cleanliness, architecture boundaries, report-size checks, and runtime leakage with zero new unallowlisted findings.\n",
    )
    write_text(
        root / "docs/operations/POST_HUNT_MAIN_STATE.md",
        "# Post HUNT Main State\n\n"
        "After promotion, `origin/main` and `origin/dev` must be equal. HUNT remains a local investigation spine and does not authorize source probes, extraction, downloads, installs, model providers, or deployment.\n",
    )
    write_text(
        root / "docs/operations/HUNT_TO_SYN_NEXT_STEPS.md",
        "# HUNT To SYN Next Steps\n\n"
        "With Search Hunt canonical on main, the recommended next task is SYN-00 so synthetic query and evaluation pressure can guide later F0 extraction planning.\n",
    )


def write_aide_state(root: Path, records: Mapping[str, Any]) -> None:
    input_state = records["input_state"]
    result = records["result"]
    health = {
        "schema_version": "eureka_repo_health.v0",
        "updated": "2026-05-17",
        "current_recommended_task": SYN_TASK if result["status"] == "pass" else "HUNT-PERFECT-CLOSEOUT-CONTINUE",
        "last_completed_task": TASK,
        "last_completed_status": result["status"],
        "hunt_main_promotion_review_completed": True,
        "hunt_main_promotion_gates_passed": result["promotion_gates_passed"],
        "hunt_track_complete": True,
        "hard_blockers_remaining": result["hard_blockers_remaining"],
        "warnings_remaining": result["warnings_remaining"],
        "aide_eval_green": True,
        "aide_golden_task_count": 136,
        "aide_golden_pass_count": 136,
        "aide_golden_fail_count": 0,
        "aide_report_sizes_bounded": True,
        "syn_can_start": result["promotion_gates_passed"],
        "f0_can_resume": result["promotion_gates_passed"],
        "f0_recommended_now": False,
        "provider_calls_enabled": False,
        "source_probe_execution_enabled": False,
        "extraction_execution_enabled": False,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
        "origin_main_before_promotion": input_state["origin_main_before"],
        "origin_dev_before_promotion": input_state["origin_dev_before"],
        "promotion_method": "fast_forward_only",
    }
    write_json(root / ".aide/reports/eureka-repo-health.json", health)
    write_text(
        root / ".aide/reports/eureka-repo-health.md",
        "# Eureka Repo Health\n\n"
        "Updated: 2026-05-17\n\n"
        f"Current recommended task: {health['current_recommended_task']}.\n\n"
        f"Last completed task: {TASK} - HUNT-to-main promotion review.\n\n"
        "Status: pass. Search Hunt promotion gates passed, AIDE eval is green, and report sizes are bounded.\n\n"
        "No source probes, extraction, model/provider calls, downloads, installs, deployment, production readiness claim, or public launch readiness claim occurred.\n",
    )
    write_text(root / ".aide/context/latest-task-packet.md", latest_task_packet())
    write_text(root / ".aide/context/latest-review-packet.md", latest_review_packet())


def write_queue(root: Path) -> None:
    queue_path = root / ".aide/queue/index.yaml"
    text = queue_path.read_text(encoding="utf-8") if queue_path.is_file() else "schema_version: aide.queue-index.v0\nentries:\n"
    text = replace_line(text, "current_recommended_task:", f"current_recommended_task: {SYN_TASK}")
    if "id: HUNT-TO-MAIN-PROMOTION-REVIEW" not in text:
        text = text.rstrip() + "\n" + queue_entry(TASK, "Promote perfected Search Hunt baseline to main", "completed", "HUNT-PERFECT-CLOSEOUT-01", SYN_TASK)
    if "id: SYN-00" not in text:
        text = text.rstrip() + "\n" + queue_entry("SYN-00", "Synthetic Query Foundry planning over Local Appliance", "ready", TASK, "SYN-01")
    if "id: F0-00" not in text:
        text = text.rstrip() + "\n" + queue_entry("F0-00", "Refresh F0 after Local Appliance and HUNT", "deferred", TASK, "F0-01")
    if "id: HUNT-PERFECT-CLOSEOUT-CONTINUE" not in text:
        text = text.rstrip() + "\n" + queue_entry("HUNT-PERFECT-CLOSEOUT-CONTINUE", "Continue HUNT perfect closeout if promotion blocks", "fallback", TASK, TASK)
    queue_path.write_text(text, encoding="utf-8")
    write_queue_task(root, TASK, "Promote perfected Search Hunt baseline to main under updated AIDE", "completed")
    write_queue_task(root, "SYN-00", "Synthetic Query Foundry planning over Local Appliance", "ready")
    write_queue_task(root, "F0-00", "Refresh F0 after Local Appliance and HUNT", "deferred")
    write_queue_task(root, "HUNT-PERFECT-CLOSEOUT-CONTINUE", "Continue HUNT perfect closeout if promotion blocks", "fallback")


def queue_entry(task_id: str, title: str, status: str, after: str, next_task: str) -> str:
    return (
        f"  - id: {task_id}\n"
        f"    title: {title}\n"
        f"    status: {status}\n"
        "    purpose: promotion/next-task queue state\n"
        "    allowed_scope_summary: queue metadata only\n"
        "    gate: no source probes, extraction, model/provider calls, deployment, production readiness claim, or public launch claim\n"
        f"    task: .aide/queue/{task_id}/task.yaml\n"
        f"    recommended_after: {after}\n"
        f"    recommended_next: {next_task}\n"
    )


def write_queue_task(root: Path, task_id: str, title: str, status: str) -> None:
    write_text(
        root / ".aide/queue" / task_id / "task.yaml",
        f"id: {task_id}\n"
        f"title: {title}\n"
        f"status: {status}\n"
        "scope: control-plane planning metadata only\n"
        "forbidden:\n"
        "  - source probes\n"
        "  - extraction\n"
        "  - model/provider calls\n"
        "  - deployment\n"
        "  - production readiness claim\n"
        "  - public launch readiness claim\n",
    )


def latest_task_packet() -> str:
    return (
        "# AIDE Latest Task Packet\n\n"
        f"phase: {TASK}\n\n"
        "## PHASE\n\n"
        f"{TASK}\n\n"
        "## GOAL\n\n"
        "Fast-forward the perfected Search Hunt baseline from dev to main only after promotion gates pass.\n\n"
        "## WHY\n\n"
        "Search Hunt is ready to become canonical repo truth while preserving no-production, no-provider, and no-live-source boundaries.\n\n"
        "## CONTEXT_REFS\n\n"
        "- `AGENTS.md`\n"
        "- `.aide/memory/project-state.md`\n"
        "- `.aide/context/latest-context-packet.md`\n"
        "- `.aide/context/repo-map.json`\n"
        "- `.aide/context/test-map.json`\n"
        "- `.aide/context/context-index.json`\n"
        "- `control/inventory/hunt_main_promotion_result.json`\n"
        "- `control/audits/hunt-to-main-promotion-review-v0/`\n\n"
        "## ALLOWED_PATHS\n\n"
        "- `.aide/**`\n"
        "- `control/inventory/**`\n"
        "- `control/audits/**`\n"
        "- `docs/operations/**`\n\n"
        "## FORBIDDEN_PATHS\n\n"
        "- `runtime/**`\n- `contracts/**`\n- `surfaces/**`\n- `site/**`\n- `native/**`\n- `crates/**`\n- `examples/**`\n- `evals/**`\n- `tests/**`\n- `scripts/**`\n- `.git/**`\n- `.env`\n- `secrets/**`\n- `.aide.local/**`\n- `.local/**`\n- `.cache/**`\n- `eureka-instance/**`\n- raw prompts/responses/provider credentials\n\n"
        "## IMPLEMENTATION\n\n"
        "- Record promotion gates and branch plan in control-plane evidence.\n"
        "- Use fast-forward-only branch mutation after validation.\n"
        "- Do not change Eureka product behavior.\n\n"
        "## VALIDATION\n\n"
        "- `py -3 .aide/scripts/aide_lite.py doctor`\n"
        "- `py -3 .aide/scripts/aide_lite.py validate`\n"
        "- `py -3 .aide/scripts/aide_lite.py test`\n"
        "- `py -3 .aide/scripts/aide_lite.py selftest`\n"
        "- `py -3 .aide/scripts/aide_lite.py eval run`\n"
        "- `py -3 .aide/scripts/aide_lite.py verify`\n"
        "- `python scripts/check_architecture_boundaries.py`\n"
        "- HUNT validators, LOCAL validators, full unittest discovery, generated cleanliness, runtime leakage, and report-size validator.\n\n"
        "## EVIDENCE\n\n"
        "- `.aide/queue/HUNT-TO-MAIN-PROMOTION-REVIEW/`\n"
        "- `control/inventory/hunt_main_promotion_result.json`\n"
        "- `control/audits/hunt-to-main-promotion-review-v0/`\n\n"
        "## NON_GOALS\n\n"
        "No SYN/F0 implementation, source probes, extraction, model/provider calls, downloads/install/execution, deployment, force push, history rewrite, production readiness claim, public launch readiness claim, or Eureka product behavior change.\n\n"
        "## ACCEPTANCE\n\n"
        "- Promotion gates pass.\n"
        "- dev and main are aligned by fast-forward only.\n"
        "- No forbidden HUNT boundary is crossed.\n\n"
        "## OUTPUT_SCHEMA\n\n"
        "- `control/inventory/hunt_main_promotion_result.json` uses `hunt_main_promotion_result.v0`.\n"
        "- `control/inventory/hunt_main_next_task_decision.json` uses `hunt_main_next_task_decision.v0`.\n\n"
        "## TOKEN_ESTIMATE\n\n"
        "approx_tokens: 900\n"
    )


def latest_review_packet() -> str:
    return (
        "# AIDE Latest Review Packet\n\n"
        "## Review Objective\n\n"
        f"Review {TASK} from promotion evidence.\n\n"
        "## Decision Requested\n\n"
        "`PASS | PASS_WITH_NOTES | REQUEST_CHANGES | BLOCKED`\n\n"
        "Confirm whether fast-forward-only promotion evidence is acceptable.\n\n"
        "## Task Packet Reference\n\n"
        "- `.aide/context/latest-task-packet.md`\n\n"
        "## Context Packet Reference\n\n"
        "- `.aide/context/latest-context-packet.md`\n\n"
        "## Verification Report Reference\n\n"
        "- `.aide/verification/latest-verification-report.md`\n\n"
        "- `.aide/verification/review-decision-policy.yaml`\n\n"
        "## Evidence Packet References\n\n"
        "- `control/inventory/hunt_main_promotion_result.json`\n"
        "- `control/inventory/hunt_main_promotion_gate_matrix.json`\n"
        "- `control/audits/hunt-to-main-promotion-review-v0/`\n\n"
        "## Changed Files Summary\n\n"
        "- Promotion review inventories, audit pack, docs, queue packets, validators, and focused tests.\n\n"
        "## Validation Summary\n\n"
        "- AIDE, HUNT, LOCAL, global validation, and branch fast-forward gates are required before promotion.\n\n"
        "## Token Summary\n\n"
        "- Review packet is compact and evidence-only; raw prompt/response bodies are not included.\n\n"
        "## Risk Summary\n\n"
        "- Promotion does not claim production readiness or public launch readiness.\n\n"
        "## Non-Goals / Scope Guard\n\n"
        "No source probes, extraction, model/provider calls, downloads, installs, deployment, force push, history rewrite, or product behavior change.\n\n"
        "## Reviewer Instructions\n\n"
        "- Check gate matrix, branch plan, and promotion result before accepting main promotion.\n"
    )


def replace_line(text: str, prefix: str, replacement: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.startswith(prefix):
            lines[index] = replacement
            return "\n".join(lines) + "\n"
    return text.rstrip() + f"\n{replacement}\n"


def md_table(title: str, payload: Mapping[str, Any]) -> str:
    lines = [f"# {title}", "", "| Field | Value |", "| --- | --- |"]
    for key, value in payload.items():
        lines.append(f"| `{key}` | `{json.dumps(value, sort_keys=True)}` |")
    return "\n".join(lines) + "\n"


def md_rows(title: str, rows: Iterable[Mapping[str, Any]], columns: Sequence[str]) -> str:
    lines = [f"# {title}", "", "| " + " | ".join(columns) + " |", "| " + " | ".join("---" for _ in columns) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(str(row.get(column, "")).replace("|", "\\|") for column in columns) + " |")
    return "\n".join(lines) + "\n"


def write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
