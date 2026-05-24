#!/usr/bin/env python3
"""Validate DEV-TO-MAIN-PROMOTION-REVIEW-02 evidence and branch gates."""

from __future__ import annotations

EUREKA_SCRIPT_COMPAT_WRAPPER = True

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
TASK = "DEV-TO-MAIN-PROMOTION-REVIEW-02"
PASS_STATUSES = {"pass", "pass_with_warnings", "canon_defined"}

RESULT_FILES = {
    "repo_layout_taxonomy": "control/inventory/repo_layout_canon_result.json",
    "test_lane_router": "control/inventory/test_lane_router_result.json",
    "ia_metadata_pilot": "control/inventory/ia_pilot_closeout_result.json",
    "ia_hunt_bridge": "control/inventory/ia_hunt_bridge_result.json",
    "workbench_foundation": "control/inventory/workbench_foundation_result.json",
    "search_interaction": "control/inventory/search_interaction_result.json",
    "workbench_result_lanes": "control/inventory/workbench_result_lanes_result.json",
    "syn_foundation": "control/inventory/syn_foundation_result.json",
    "domain_foundation": "control/inventory/domain_foundation_result.json",
    "scout_schema": "control/inventory/scout_schema_result.json",
    "f0_foundation": "control/inventory/f0_foundation_result.json",
    "g0_foundation": "control/inventory/g0_foundation_result.json",
    "resolution_run_kernel": "control/inventory/resolution_run_result.json",
    "workbench_live_run": "control/inventory/workbench_live_run_result.json",
    "ia_live_metadata_lane": "control/inventory/ia_live_metadata_lane_result.json",
    "workbench_review_promote": "control/inventory/workbench_review_promote_result.json",
    "local_apply_gate": "control/inventory/local_apply_gate_result.json",
    "workbench_local_loop_closeout": "control/inventory/workbench_local_loop_result.json",
}

REQUIRED_FILES = {
    "control/inventory/dev_to_main_promotion_02_input_state.json",
    "control/inventory/dev_to_main_promotion_02_branch_state.json",
    "control/inventory/dev_to_main_promotion_02_scope_matrix.json",
    "control/inventory/dev_to_main_promotion_02_validation_matrix.json",
    "control/inventory/dev_to_main_promotion_02_boundary_report.json",
    "control/inventory/dev_to_main_promotion_02_result.json",
    "control/inventory/dev_to_main_promotion_02_next_task_decision.json",
    "control/inventory/dev_to_main_promotion_02_failure_repair_log.json",
    "control/audits/dev-to-main-promotion-review-02-v0/README.md",
    "control/audits/dev-to-main-promotion-review-02-v0/dev_to_main_promotion_02_report.json",
    "control/audits/dev-to-main-promotion-review-02-v0/branch_state.md",
    "control/audits/dev-to-main-promotion-review-02-v0/scope_matrix.md",
    "control/audits/dev-to-main-promotion-review-02-v0/validation_matrix.md",
    "control/audits/dev-to-main-promotion-review-02-v0/boundary_report.md",
    "control/audits/dev-to-main-promotion-review-02-v0/full_discovery_summary.md",
    "control/audits/dev-to-main-promotion-review-02-v0/promotion_result.md",
    "control/audits/dev-to-main-promotion-review-02-v0/validation.md",
    "control/audits/dev-to-main-promotion-review-02-v0/generated/selected_tests.json",
    "control/audits/dev-to-main-promotion-review-02-v0/generated/promotion_selector.json",
    "control/audits/dev-to-main-promotion-review-02-v0/generated/full_unittest_summary.txt",
    "control/audits/dev-to-main-promotion-review-02-v0/generated/sample_summary.md",
    "docs/operations/DEV_TO_MAIN_PROMOTION_REVIEW_02.md",
    "docs/operations/POST_LOCAL_LOOP_PROMOTION_PLAN.md",
}

LOCAL_APPLY_TRUE_FIELDS = (
    "dry_run_preview_passed",
    "apply_without_token_blocked",
    "apply_without_confirmation_blocked",
    "repo_path_target_blocked",
    "temp_instance_apply_passed",
    "backup_created_before_apply",
    "mutation_manifest_created",
    "audit_log_created",
    "rollback_plan_created",
    "rollback_passed",
    "post_apply_validation_passed",
    "post_rollback_validation_passed",
    "public_projection_blocked",
    "native_read_only_projection_blocked",
)
LOCAL_LOOP_TRUE_FIELDS = (
    "dry_run_loop_passed",
    "temp_apply_loop_passed",
    "search_after_apply_passed",
    "rollback_passed",
    "search_after_rollback_passed",
    "public_projection_blocked",
    "native_read_only_projection_blocked",
)
BOUNDARY_FALSE_FIELDS = (
    "force_push_performed",
    "rebase_performed",
    "history_rewrite_performed",
    "branch_deleted",
    "secrets_committed",
    "operator_tokens_committed",
    "committed_instance_state",
    "master_index_mutated",
    "committed_data_public_index_mutated",
    "raw_live_source_response_committed",
    "live_source_probe_required",
    "download_performed",
    "upload_performed",
    "extraction_executed",
    "model_provider_used",
    "deployment_performed",
    "production_readiness_claimed",
    "public_launch_readiness_claimed",
    "marketplace_or_app_store_readiness_claimed",
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    result = validate(Path(args.repo_root).resolve())
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    else:
        print(f"dev to main promotion validation: {result['status']}", file=stdout)
        for error in result["errors"]:
            print(f"ERROR: {error}", file=stdout)
        for warning in result["warnings"]:
            print(f"WARN: {warning}", file=stdout)
    return 0 if result["status"] == "pass" else 1


def validate(root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    for rel in sorted(REQUIRED_FILES):
        require_file(root, rel, errors)
    result_payloads = {
        subsystem: load_json(root / rel, errors)
        for subsystem, rel in RESULT_FILES.items()
    }
    input_state = load_json(root / "control/inventory/dev_to_main_promotion_02_input_state.json", errors)
    branch_state = load_json(root / "control/inventory/dev_to_main_promotion_02_branch_state.json", errors)
    scope_matrix = load_json(root / "control/inventory/dev_to_main_promotion_02_scope_matrix.json", errors)
    validation_matrix = load_json(root / "control/inventory/dev_to_main_promotion_02_validation_matrix.json", errors)
    boundary = load_json(root / "control/inventory/dev_to_main_promotion_02_boundary_report.json", errors)
    result = load_json(root / "control/inventory/dev_to_main_promotion_02_result.json", errors)
    next_task = load_json(root / "control/inventory/dev_to_main_promotion_02_next_task_decision.json", errors)

    validate_result_files(result_payloads, errors)
    validate_hard_gates(result_payloads, errors)
    validate_scope_matrix(scope_matrix, errors)
    validate_validation_matrix(validation_matrix, result, errors)
    validate_boundary(boundary, result, errors)
    validate_next_task(next_task, errors)
    validate_input_state(input_state, errors)
    validate_branch_state(root, branch_state, errors, warnings)
    validate_git_hygiene(root, errors)

    return {
        "schema_version": "dev_to_main_promotion_02_validation.v0",
        "task": TASK,
        "status": "pass" if not errors else "fail",
        "errors": errors,
        "warnings": warnings,
        "branch_state": current_branch_state(root),
        "promotion_scope_count": len(scope_entries(scope_matrix)),
        "full_unittest_discovery_passed": result.get("full_unittest_discovery_passed") is True,
        "promotion_performed": result.get("promotion_performed") is True,
        "origin_main_equals_origin_dev_after": result.get("origin_main_equals_origin_dev_after") is True,
    }


def validate_result_files(payloads: Mapping[str, Mapping[str, Any]], errors: list[str]) -> None:
    for subsystem, payload in payloads.items():
        status = str(payload.get("status", ""))
        if status not in PASS_STATUSES:
            errors.append(f"{subsystem} result status must be pass/pass_with_warnings/canon_defined, got {status!r}")
        for field in (
            "production_readiness_claimed",
            "public_launch_readiness_claimed",
            "deployment_performed",
            "master_index_mutated",
            "committed_data_public_index_mutated",
            "committed_instance_state",
        ):
            if payload.get(field) is True:
                errors.append(f"{subsystem} result has unsafe flag {field}=true")


def validate_hard_gates(payloads: Mapping[str, Mapping[str, Any]], errors: list[str]) -> None:
    local_apply = payloads.get("local_apply_gate", {})
    local_loop = payloads.get("workbench_local_loop_closeout", {})
    review_promote = payloads.get("workbench_review_promote", {})
    ia_live = payloads.get("ia_live_metadata_lane", {})
    for field in LOCAL_APPLY_TRUE_FIELDS:
        if local_apply.get(field) is not True:
            errors.append(f"local apply gate requires {field}=true")
    for field in LOCAL_LOOP_TRUE_FIELDS:
        if local_loop.get(field) is not True:
            errors.append(f"local loop requires {field}=true")
    if review_promote.get("status") not in PASS_STATUSES:
        errors.append("workbench review/promote must pass")
    if ia_live.get("operator_token_required") is not True:
        errors.append("IA live metadata lane must remain operator-token gated")
    for payload_name, payload in (("local apply gate", local_apply), ("local loop", local_loop)):
        for field in (
            "operator_instance_mutated",
            "committed_instance_state",
            "master_index_mutated",
            "committed_data_public_index_mutated",
            "production_readiness_claimed",
            "public_launch_readiness_claimed",
        ):
            if payload.get(field) is not False:
                errors.append(f"{payload_name} requires {field}=false")


def validate_scope_matrix(payload: Mapping[str, Any], errors: list[str]) -> None:
    entries = scope_entries(payload)
    expected = set(RESULT_FILES)
    present = {str(item.get("subsystem_id", "")) for item in entries}
    for subsystem in sorted(expected - present):
        errors.append(f"scope matrix missing {subsystem}")
    for item in entries:
        subsystem = str(item.get("subsystem_id", ""))
        if subsystem in RESULT_FILES and item.get("result_file") != RESULT_FILES[subsystem]:
            errors.append(f"scope matrix result_file mismatch for {subsystem}")
        for field in ("production_claim", "public_launch_claim", "unsafe_actions_enabled"):
            if item.get(field) is not False:
                errors.append(f"scope matrix requires {subsystem}.{field}=false")


def validate_validation_matrix(payload: Mapping[str, Any], result: Mapping[str, Any], errors: list[str]) -> None:
    commands = payload.get("commands")
    if not isinstance(commands, list) or not commands:
        errors.append("validation matrix requires commands")
        return
    command_text = json.dumps(commands)
    for token in (
        "python -m unittest discover -s tests -t .",
        "python scripts/validate_workbench_local_loop_closeout.py",
        "python scripts/validate_local_apply_gate.py",
        "python scripts/check_architecture_boundaries.py",
        "python scripts/check_generated_artifact_cleanliness.py --check --json",
    ):
        if token not in command_text:
            errors.append(f"validation matrix missing {token}")
    full_status = payload.get("full_unittest_discovery_status")
    if full_status not in {"pass", "pending_current_task"}:
        errors.append("validation matrix requires full_unittest_discovery_status=pass or pending_current_task")
    if full_status == "pass" and result.get("full_unittest_discovery_passed") is not True:
        errors.append("result requires full_unittest_discovery_passed=true when full discovery has passed")


def validate_boundary(boundary: Mapping[str, Any], result: Mapping[str, Any], errors: list[str]) -> None:
    for payload_name, payload in (("boundary report", boundary), ("result", result)):
        for field in BOUNDARY_FALSE_FIELDS:
            if payload.get(field) is not False:
                errors.append(f"{payload_name} requires {field}=false")
    if result.get("branch_fast_forward_possible") is not True:
        errors.append("result requires branch_fast_forward_possible=true")
    if result.get("main_pushed") is True and result.get("origin_main_equals_origin_dev_after") is not True:
        errors.append("main_pushed=true requires origin_main_equals_origin_dev_after=true")


def validate_next_task(payload: Mapping[str, Any], errors: list[str]) -> None:
    next_task = str(payload.get("recommended_next_task", ""))
    if not next_task.startswith("SOURCE-ACTION-KERNEL-00"):
        errors.append("next task must be SOURCE-ACTION-KERNEL-00")
    if payload.get("production_readiness_claimed") is not False:
        errors.append("next task decision requires production_readiness_claimed=false")
    if payload.get("public_launch_readiness_claimed") is not False:
        errors.append("next task decision requires public_launch_readiness_claimed=false")


def validate_input_state(payload: Mapping[str, Any], errors: list[str]) -> None:
    if payload.get("branch") != "dev":
        errors.append("input state branch must be dev")
    for field in (
        "local_apply_gate_found",
        "workbench_local_loop_found",
        "workbench_review_promote_found",
        "ia_live_metadata_lane_found",
        "workbench_live_run_found",
        "resolution_run_kernel_found",
        "g0_foundation_found",
        "f0_foundation_found",
        "scout_schema_found",
        "domain_foundation_found",
        "syn_foundation_found",
        "ia_hunt_bridge_found",
        "workbench_result_lanes_found",
        "search_interaction_found",
        "workbench_foundation_found",
    ):
        if payload.get(field) is not True:
            errors.append(f"input state requires {field}=true")


def validate_branch_state(root: Path, payload: Mapping[str, Any], errors: list[str], warnings: list[str]) -> None:
    current = current_branch_state(root)
    if current.get("branch") != "dev":
        warnings.append(f"current branch is {current.get('branch')}, final promotion verification should return to dev")
    ahead_behind = current.get("origin_main_origin_dev_ahead_behind")
    if ahead_behind not in {"0 0", "0 1", "0 2", "0 3", "0 4", "0 5", payload.get("ahead_behind_origin_main_origin_dev")}:
        left = int(str(ahead_behind).split()[0]) if ahead_behind and str(ahead_behind).split() else 999
        if left != 0:
            errors.append(f"origin/main cannot fast-forward to origin/dev: {ahead_behind}")
    recorded = str(payload.get("ahead_behind_origin_main_origin_dev", ""))
    if recorded and not recorded.startswith("0 "):
        errors.append(f"recorded branch state is not fast-forwardable: {recorded}")
    if payload.get("working_tree_clean_before") is not True:
        errors.append("branch state requires working_tree_clean_before=true")


def validate_git_hygiene(root: Path, errors: list[str]) -> None:
    tracked = run_git(root, "ls-files").splitlines()
    forbidden_prefixes = ("instances/", "eureka-instance/", ".aide.local/", "secrets/", "data/public_index/")
    forbidden_exact = {".env"}
    for path in tracked:
        normalized = path.replace("\\", "/")
        if normalized in forbidden_exact or normalized.startswith(forbidden_prefixes):
            errors.append(f"forbidden tracked path: {normalized}")


def scope_entries(payload: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    entries = payload.get("promotion_scope", payload.get("subsystems", []))
    return entries if isinstance(entries, list) else []


def current_branch_state(root: Path) -> dict[str, str]:
    return {
        "branch": run_git(root, "branch", "--show-current"),
        "head": run_git(root, "rev-parse", "HEAD"),
        "origin_main": run_git(root, "rev-parse", "origin/main"),
        "origin_dev": run_git(root, "rev-parse", "origin/dev"),
        "merge_base": run_git(root, "merge-base", "origin/main", "origin/dev"),
        "origin_main_origin_dev_ahead_behind": run_git(root, "rev-list", "--left-right", "--count", "origin/main...origin/dev").replace("\t", " "),
        "origin_dev_head_ahead_behind": run_git(root, "rev-list", "--left-right", "--count", "origin/dev...HEAD").replace("\t", " "),
    }


def require_file(root: Path, rel: str, errors: list[str]) -> None:
    if not (root / rel).is_file():
        errors.append(f"missing required file: {rel}")


def load_json(path: Path, errors: list[str]) -> dict[str, Any]:
    if not path.is_file():
        errors.append(f"missing json file: {path.relative_to(REPO_ROOT) if path.is_absolute() else path}")
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"invalid json {path}: {exc}")
        return {}
    return payload if isinstance(payload, dict) else {}


def run_git(root: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=root,
        text=True,
        capture_output=True,
        check=True,
    )
    return completed.stdout.strip()


if __name__ == "__main__":
    raise SystemExit(main())
