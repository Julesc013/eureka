#!/usr/bin/env python3
"""Validate dev-to-main promotion evidence for IA, layout canon, and blocker repair."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]
PROMOTION_SCOPE = "ia_metadata_pilot_plus_repo_layout_canon_plus_blocker_repair"
BLOCKER_REPAIR_COMMIT = "28128d489e4e8a4ddbadc98e73d6fcabb9b575b8"
LAYOUT_CANON_COMMIT = "fb0d8f9ff8534bf30e0e389da4db9bd19375b63d"
NEXT_TASK_ID = "REPO-LAYOUT-CANON-01"

REQUIRED_FILES = (
    "control/inventory/dev_and_ia_to_main_promotion_input_state.json",
    "control/inventory/dev_and_ia_to_main_promotion_branch_matrix.json",
    "control/inventory/dev_and_ia_to_main_promotion_validation_matrix.json",
    "control/inventory/dev_and_ia_to_main_promotion_boundary_matrix.json",
    "control/inventory/dev_and_ia_to_main_promotion_decision.json",
    "control/inventory/dev_and_ia_to_main_promotion_result.json",
    "control/inventory/dev_and_ia_to_main_next_task_decision.json",
    "control/inventory/dev_and_ia_promotion_blocker_result.json",
    "control/inventory/ia_pilot_closeout_result.json",
    "control/inventory/repo_layout_canon_result.json",
    "docs/operations/DEV_AND_IA_TO_MAIN_PROMOTION_REVIEW.md",
    "docs/operations/POST_DEV_IA_PROMOTION_PLAN.md",
)

REQUIRED_VALIDATION_IDS = {
    "ia_metadata_policy",
    "ia_fixture_replay",
    "ia_live_metadata_probe",
    "ia_source_cache",
    "ia_evidence",
    "ia_candidate",
    "ia_review_promotion",
    "ia_reviewed_index",
    "ia_pilot_closeout",
    "repo_structure_canon",
    "repo_structure_canon_tests",
    "promotion_blocker_result",
    "runtime_leakage_validators",
    "architecture_boundaries",
    "generated_artifact_cleanliness",
    "git_diff_check",
    "aide_doctor",
    "aide_validate",
    "aide_test",
    "aide_selftest",
    "aide_verify",
    "aide_review_pack",
    "aide_commit_check",
    "full_unittest_discovery",
}

FORBIDDEN_BOUNDARY_FALSE_FIELDS = (
    "raw_response_committed",
    "operator_instance_mutated",
    "instance_state_committed",
    "committed_data_public_index_mutated",
    "master_index_mutated",
    "hosted_public_search_mutated",
    "public_search_fanout_enabled",
    "download_performed",
    "upload_performed",
    "extraction_executed",
    "model_provider_used",
    "deployment_performed",
    "production_readiness_claimed",
    "public_launch_readiness_claimed",
    "full_archive_org_integration_claimed",
    "marketplace_or_app_store_readiness_claimed",
    "repo_layout_moves_performed",
)

REQUIRED_BOUNDARY_TRUE_FIELDS = (
    "ia_metadata_pilot_closeout_passed",
    "ia_metadata_full_vertical_slice_complete",
    "repo_layout_canon_present",
    "promotion_blocker_repair_present",
    "full_unittest_discovery_passed",
    "live_metadata_probe_performed",
    "source_cache_temp_write_passed",
    "evidence_temp_write_passed",
    "candidate_temp_write_passed",
    "review_temp_write_passed",
    "reviewed_index_temp_rebuild_passed",
    "search_result_proof_passed",
    "object_packet_proof_passed",
    "absence_packet_proof_passed",
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    _ = argv
    result = validate_dev_and_ia_to_main_promotion(REPO_ROOT)
    print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    return 0 if result["status"] == "pass" else 1


def validate_dev_and_ia_to_main_promotion(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    for rel_path in REQUIRED_FILES:
        if not (repo_root / rel_path).exists():
            errors.append(f"missing_file:{rel_path}")

    input_state = _load_json(repo_root / "control/inventory/dev_and_ia_to_main_promotion_input_state.json", errors)
    branch = _load_json(repo_root / "control/inventory/dev_and_ia_to_main_promotion_branch_matrix.json", errors)
    validation = _load_json(repo_root / "control/inventory/dev_and_ia_to_main_promotion_validation_matrix.json", errors)
    boundary = _load_json(repo_root / "control/inventory/dev_and_ia_to_main_promotion_boundary_matrix.json", errors)
    decision = _load_json(repo_root / "control/inventory/dev_and_ia_to_main_promotion_decision.json", errors)
    result = _load_json(repo_root / "control/inventory/dev_and_ia_to_main_promotion_result.json", errors)
    next_task = _load_json(repo_root / "control/inventory/dev_and_ia_to_main_next_task_decision.json", errors)
    blocker_result = _load_json(repo_root / "control/inventory/dev_and_ia_promotion_blocker_result.json", errors)
    ia_closeout = _load_json(repo_root / "control/inventory/ia_pilot_closeout_result.json", errors)
    layout_result = _load_json(repo_root / "control/inventory/repo_layout_canon_result.json", errors)

    errors.extend(validate_input_state(input_state))
    errors.extend(validate_branch_matrix(branch))
    errors.extend(validate_validation_matrix(validation, decision))
    errors.extend(validate_boundary_matrix(boundary))
    errors.extend(validate_decision(decision))
    errors.extend(validate_result(result))
    errors.extend(validate_next_task(next_task))
    errors.extend(validate_source_baselines(ia_closeout, layout_result, blocker_result))
    errors.extend(validate_docs(repo_root))
    errors.extend(validate_git_forbidden_paths(repo_root))

    return {
        "schema_version": "dev_and_ia_to_main_promotion_validation.v0",
        "task": "DEV-AND-IA-TO-MAIN-PROMOTION-REVIEW",
        "status": "pass" if not errors else "fail",
        "errors": errors,
        "warnings": warnings,
        "promotion_scope": PROMOTION_SCOPE,
        "ia_metadata_pilot_closeout_passed": ia_closeout.get("status") == "pass",
        "repo_layout_canon_present": layout_result.get("task_id") == "REPO-LAYOUT-CANON-01",
        "promotion_blocker_repair_present": blocker_result.get("task") == "DEV-AND-IA-PROMOTION-BLOCKER-01",
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
        "full_archive_org_integration_claimed": False,
        "marketplace_or_app_store_readiness_claimed": False,
    }


def validate_input_state(input_state: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    expected_true = (
        "local_dev_equals_origin_dev",
        "main_can_fast_forward_to_dev",
        "dev_contains_main",
        "ia_pilot_closeout_found",
        "repo_layout_canon_found",
        "promotion_blocker_repair_found",
        "full_unittest_discovery_previously_passed",
        "working_tree_clean_before",
    )
    for key in expected_true:
        if input_state.get(key) is not True:
            errors.append(f"input_expected_true:{key}")
    expected_false = (
        "local_instance_state_tracked",
        "deployment_performed",
        "production_readiness_claimed",
        "public_launch_readiness_claimed",
    )
    for key in expected_false:
        if input_state.get(key) is not False:
            errors.append(f"input_expected_false:{key}")
    if input_state.get("repo_layout_canon_commit") != LAYOUT_CANON_COMMIT:
        errors.append("input_repo_layout_canon_commit_mismatch")
    if input_state.get("promotion_blocker_repair_commit") != BLOCKER_REPAIR_COMMIT:
        errors.append("input_promotion_blocker_repair_commit_mismatch")
    return errors


def validate_branch_matrix(branch: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    expected_true = (
        "origin_dev_contains_ia_closeout",
        "origin_dev_contains_repo_layout_canon",
        "origin_dev_contains_promotion_blocker_repair",
        "main_can_fast_forward_to_dev",
    )
    for key in expected_true:
        if branch.get(key) is not True:
            errors.append(f"branch_expected_true:{key}")
    if not isinstance(branch.get("safe_to_promote"), bool):
        errors.append("branch_safe_to_promote_not_bool")
    expected_false = ("force_push_required", "history_rewrite_required", "branch_delete_required")
    for key in expected_false:
        if branch.get(key) is not False:
            errors.append(f"branch_expected_false:{key}")
    if branch.get("promotion_method") != "fast_forward_only":
        errors.append("branch_promotion_method_not_fast_forward_only")
    return errors


def validate_validation_matrix(matrix: Mapping[str, Any], decision: Mapping[str, Any] | None = None) -> list[str]:
    rows = matrix.get("rows", [])
    promotion_blocked = decision is not None and decision.get("decision") == "blocked"
    row_ids = {row.get("validation_id") for row in rows if isinstance(row, Mapping)}
    errors = [f"missing_validation:{item}" for item in sorted(REQUIRED_VALIDATION_IDS - row_ids)]
    for row in rows if isinstance(rows, list) else []:
        if not isinstance(row, Mapping):
            errors.append("validation_row_not_object")
            continue
        validation_id = row.get("validation_id")
        if row.get("status") not in {"pass", "warn", "fail", "not_run"}:
            errors.append(f"validation_bad_status:{validation_id}")
        if row.get("blocks_promotion") is True and row.get("status") != "pass" and not promotion_blocked:
            errors.append(f"blocking_validation_not_pass:{validation_id}")
        for key in ("validation_id", "command", "status", "blocks_promotion", "reason", "evidence_path"):
            if key not in row:
                errors.append(f"validation_missing_field:{validation_id}:{key}")
    return errors


def validate_boundary_matrix(boundary: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    for key in FORBIDDEN_BOUNDARY_FALSE_FIELDS:
        if boundary.get(key) is not False:
            errors.append(f"boundary_expected_false:{key}")
    for key in REQUIRED_BOUNDARY_TRUE_FIELDS:
        if boundary.get(key) is not True:
            errors.append(f"boundary_expected_true:{key}")
    if boundary.get("total_http_requests") != 2:
        errors.append("boundary_total_http_requests_not_two")
    return errors


def validate_decision(decision: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    decision_value = decision.get("decision")
    if decision_value not in {"promote_dev_to_main", "blocked"}:
        errors.append("decision_not_promote_or_blocked")
    if decision.get("promotion_scope") != PROMOTION_SCOPE:
        errors.append("decision_scope_mismatch")
    if decision.get("main_can_fast_forward_to_dev") is not True:
        errors.append("decision_expected_true:main_can_fast_forward_to_dev")
    if decision_value == "promote_dev_to_main" and decision.get("safe_to_push_main") is not True:
        errors.append("decision_expected_true:safe_to_push_main")
    if decision_value == "blocked" and decision.get("safe_to_push_main") is not False:
        errors.append("decision_expected_false_when_blocked:safe_to_push_main")
    for key in ("force_push_required", "history_rewrite_required", "delete_branch_required"):
        if decision.get(key) is not False:
            errors.append(f"decision_expected_false:{key}")
    if decision_value == "promote_dev_to_main" and decision.get("hard_blockers_remaining") != 0:
        errors.append("decision_hard_blockers_remaining_not_zero")
    if decision_value == "blocked" and int(decision.get("hard_blockers_remaining", 0)) <= 0:
        errors.append("decision_blocked_without_hard_blocker")
    if decision.get("warnings_remaining") != 0:
        errors.append("decision_warnings_remaining_not_zero")
    if decision.get("promotion_method") != "fast_forward_only":
        errors.append("decision_promotion_method_not_fast_forward_only")
    next_task = str(decision.get("recommended_next_task", ""))
    if decision_value == "promote_dev_to_main" and NEXT_TASK_ID not in next_task:
        errors.append("decision_next_task_not_repo_layout_canon")
    if decision_value == "blocked" and "PROMOTION-BLOCKER" not in next_task:
        errors.append("decision_blocked_next_task_not_blocker")
    return errors


def validate_result(result: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    if result.get("promotion_scope") != PROMOTION_SCOPE:
        errors.append("result_scope_mismatch")
    if result.get("status") not in {"pass", "pass_with_warnings", "partial", "blocked", "fail"}:
        errors.append("result_status_not_accepted")
    if result.get("promotion_method") != "fast_forward_only":
        errors.append("result_promotion_method_not_fast_forward_only")
    for key in (
        "force_push_performed",
        "history_rewrite_performed",
        "branch_deleted",
        "production_readiness_claimed",
        "public_launch_readiness_claimed",
        "full_archive_org_integration_claimed",
        "marketplace_or_app_store_readiness_claimed",
    ):
        if result.get(key) is not False:
            errors.append(f"result_expected_false:{key}")
    if result.get("promotion_performed") is True:
        for key in ("origin_main_equals_origin_dev", "main_pushed", "dev_pushed", "working_tree_clean_after"):
            if result.get(key) is not True:
                errors.append(f"result_expected_true_after_promotion:{key}")
    next_task = str(result.get("recommended_next_task", ""))
    if result.get("status") in {"pass", "pass_with_warnings"} and NEXT_TASK_ID not in next_task:
        errors.append("result_next_task_not_repo_layout_canon")
    if result.get("status") == "blocked" and "PROMOTION-BLOCKER" not in next_task:
        errors.append("result_blocked_next_task_not_blocker")
    return errors


def validate_next_task(next_task: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    decision_text = str(next_task.get("decision", ""))
    if NEXT_TASK_ID not in decision_text and "PROMOTION-BLOCKER" not in decision_text:
        errors.append("next_task_decision_not_repo_layout_or_blocker")
    if next_task.get("production_readiness_claimed") is not False:
        errors.append("next_task_production_claim_not_false")
    if next_task.get("public_launch_readiness_claimed") is not False:
        errors.append("next_task_public_launch_claim_not_false")
    return errors


def validate_source_baselines(
    ia_closeout: Mapping[str, Any],
    layout_result: Mapping[str, Any],
    blocker_result: Mapping[str, Any],
) -> list[str]:
    errors: list[str] = []
    if ia_closeout.get("status") != "pass":
        errors.append("ia_closeout_not_pass")
    if ia_closeout.get("full_ia_metadata_vertical_slice_complete") is not True:
        errors.append("ia_vertical_slice_not_complete")
    if ia_closeout.get("full_archive_org_integration_claimed") is not False:
        errors.append("ia_full_archive_claimed")
    if layout_result.get("task_id") != "REPO-LAYOUT-CANON-01":
        errors.append("layout_canon_task_missing")
    if layout_result.get("status") != "canon_defined":
        errors.append("layout_canon_not_defined")
    if layout_result.get("files_moved") is not False:
        errors.append("layout_files_moved")
    if layout_result.get("runtime_behavior_changed") is not False:
        errors.append("layout_runtime_behavior_changed")
    if blocker_result.get("task") != "DEV-AND-IA-PROMOTION-BLOCKER-01":
        errors.append("promotion_blocker_result_task_missing")
    if blocker_result.get("full_unittest_discovery_pass") is not True:
        errors.append("promotion_blocker_full_discovery_not_pass")
    for key in (
        "candidate_index_failures_resolved",
        "contract_taxonomy_failures_resolved",
        "runtime_source_observation_leakage_resolved",
        "hunt_local_promotion_state_failures_resolved",
    ):
        if blocker_result.get(key) is not True:
            errors.append(f"promotion_blocker_expected_true:{key}")
    return errors


def validate_docs(repo_root: Path) -> list[str]:
    errors: list[str] = []
    doc_paths = (
        "docs/operations/DEV_AND_IA_TO_MAIN_PROMOTION_REVIEW.md",
        "docs/operations/POST_DEV_IA_PROMOTION_PLAN.md",
    )
    required_phrases = (
        "metadata-only local vertical slice",
        "repo layout canon",
        "not production readiness",
        "not public launch readiness",
        "not full Archive.org integration",
        "not marketplace",
    )
    for rel_path in doc_paths:
        path = repo_root / rel_path
        if not path.exists():
            errors.append(f"missing_doc:{rel_path}")
            continue
        text = path.read_text(encoding="utf-8").lower()
        for phrase in required_phrases:
            if phrase.lower() not in text:
                errors.append(f"doc_missing_phrase:{rel_path}:{phrase}")
    return errors


def validate_git_forbidden_paths(repo_root: Path) -> list[str]:
    completed = subprocess.run(
        [
            "git",
            "status",
            "--short",
            "--",
            "eureka-instance",
            "instances",
            ".aide.local",
            "secrets",
            ".env",
            "site/dist",
            "site/dist/data/public_index",
            "runtime/connectors",
            "runtime/extraction",
            "runtime/search_quality",
            "native",
            "crates",
        ],
        cwd=repo_root,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        return ["git_status_forbidden_paths_failed"]
    return ["forbidden_path_modified:" + completed.stdout.strip().replace("\n", ";")] if completed.stdout.strip() else []


def _load_json(path: Path, errors: list[str]) -> Mapping[str, Any]:
    if not path.exists():
        errors.append(f"missing_json:{path.relative_to(REPO_ROOT).as_posix()}")
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"invalid_json:{path.relative_to(REPO_ROOT).as_posix()}:{exc}")
        return {}
    return payload if isinstance(payload, Mapping) else {}


if __name__ == "__main__":
    raise SystemExit(main())
