#!/usr/bin/env python3
"""Validate DEV-TO-MAIN-PROMOTION-REVIEW-03 evidence and branch gates."""

from __future__ import annotations

EUREKA_SCRIPT_COMPAT_WRAPPER = True

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
TASK = "DEV-TO-MAIN-PROMOTION-REVIEW-03"
PASS_STATUSES = {"pass", "pass_with_warnings"}
WAITING_STATUS = "WAITING_FOR_EXTERNAL_FULL_DISCOVERY"

RESULT_FILES = {
    "ci_full_discovery_harness": "control/inventory/ci_full_discovery_harness_result.json",
    "source_snapshot_baseline_closeout": "control/inventory/source_snapshot_closeout_result.json",
    "source_action_kernel": "control/inventory/source_action_kernel_result.json",
    "source_wave": "control/inventory/source_wave_result.json",
    "snapshot_relay": "control/inventory/snapshot_relay_result.json",
    "local_product_loop_baseline": "control/inventory/dev_to_main_promotion_02_result.json",
}

REQUIRED_FILES = {
    "control/inventory/dev_to_main_promotion_03_input_state.json",
    "control/inventory/dev_to_main_promotion_03_branch_state.json",
    "control/inventory/dev_to_main_promotion_03_scope_matrix.json",
    "control/inventory/dev_to_main_promotion_03_validation_matrix.json",
    "control/inventory/dev_to_main_promotion_03_boundary_report.json",
    "control/inventory/dev_to_main_promotion_03_result.json",
    "control/inventory/dev_to_main_promotion_03_next_task_decision.json",
    "control/inventory/dev_to_main_promotion_03_failure_repair_log.json",
    "control/audits/dev-to-main-promotion-review-03-v0/README.md",
    "control/audits/dev-to-main-promotion-review-03-v0/dev_to_main_promotion_03_report.json",
    "control/audits/dev-to-main-promotion-review-03-v0/branch_state.md",
    "control/audits/dev-to-main-promotion-review-03-v0/scope_matrix.md",
    "control/audits/dev-to-main-promotion-review-03-v0/validation_matrix.md",
    "control/audits/dev-to-main-promotion-review-03-v0/boundary_report.md",
    "control/audits/dev-to-main-promotion-review-03-v0/full_discovery_evidence.md",
    "control/audits/dev-to-main-promotion-review-03-v0/promotion_result.md",
    "control/audits/dev-to-main-promotion-review-03-v0/validation.md",
    "control/audits/dev-to-main-promotion-review-03-v0/generated/sample_summary.md",
    "docs/operations/DEV_TO_MAIN_PROMOTION_REVIEW_03.md",
    "docs/operations/POST_SOURCE_SNAPSHOT_PROMOTION_PLAN.md",
}

BOUNDARY_FALSE_FIELDS = (
    "force_push_performed",
    "rebase_performed",
    "history_rewrite_performed",
    "branch_deleted",
    "secrets_committed",
    "operator_tokens_committed",
    "raw_logs_committed",
    "raw_live_source_response_committed",
    "committed_instance_state",
    "master_index_mutated",
    "committed_data_public_index_mutated",
    "live_source_call_performed",
    "source_probe_executed",
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
        print(f"dev to main promotion 03 validation: {result['status']}", file=stdout)
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

    result_payloads = {name: load_json(root / rel, errors) for name, rel in RESULT_FILES.items()}
    input_state = load_json(root / "control/inventory/dev_to_main_promotion_03_input_state.json", errors)
    branch_state = load_json(root / "control/inventory/dev_to_main_promotion_03_branch_state.json", errors)
    scope_matrix = load_json(root / "control/inventory/dev_to_main_promotion_03_scope_matrix.json", errors)
    validation_matrix = load_json(root / "control/inventory/dev_to_main_promotion_03_validation_matrix.json", errors)
    boundary = load_json(root / "control/inventory/dev_to_main_promotion_03_boundary_report.json", errors)
    result = load_json(root / "control/inventory/dev_to_main_promotion_03_result.json", errors)
    next_task = load_json(root / "control/inventory/dev_to_main_promotion_03_next_task_decision.json", errors)
    repair_log = load_json(root / "control/inventory/dev_to_main_promotion_03_failure_repair_log.json", errors)
    report = load_json(root / "control/audits/dev-to-main-promotion-review-03-v0/dev_to_main_promotion_03_report.json", errors)

    validate_result_files(result_payloads, input_state, result, errors)
    validate_scope_matrix(scope_matrix, errors)
    validate_validation_matrix(validation_matrix, result, errors)
    validate_boundary(boundary, result, report, errors)
    validate_next_task(next_task, result, errors)
    validate_input_state(input_state, errors)
    validate_branch_state(root, branch_state, result, errors, warnings)
    validate_repair_log(repair_log, errors)
    validate_git_hygiene(root, errors)

    return {
        "schema_version": "dev_to_main_promotion_03_validation.v0",
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


def validate_result_files(
    payloads: Mapping[str, Mapping[str, Any]],
    input_state: Mapping[str, Any],
    result: Mapping[str, Any],
    errors: list[str],
) -> None:
    closeout = payloads.get("source_snapshot_baseline_closeout", {})
    for subsystem, payload in payloads.items():
        status = str(payload.get("status", ""))
        if subsystem == "source_snapshot_baseline_closeout":
            effective = input_state.get("source_snapshot_closeout_effective_status") == "pass"
            external_pass = result.get("full_unittest_discovery_passed") is True
            if status not in PASS_STATUSES and not (status == WAITING_STATUS and effective and external_pass):
                errors.append("source snapshot closeout must be pass or externally consumed waiting evidence")
        elif status not in PASS_STATUSES:
            errors.append(f"{subsystem} result status must be pass/pass_with_warnings, got {status!r}")
        for field in (
            "production_readiness_claimed",
            "public_launch_readiness_claimed",
            "deployment_performed",
            "master_index_mutated",
            "committed_data_public_index_mutated",
        ):
            if payload.get(field) is True:
                errors.append(f"{subsystem} result has unsafe flag {field}=true")

    if input_state.get("source_snapshot_closeout_validator_passed") is not True:
        errors.append("source snapshot closeout validator must pass")
    if closeout.get("task") != "SOURCE-SNAPSHOT-BASELINE-CLOSEOUT-01":
        errors.append("source snapshot closeout task mismatch")
    if payloads.get("source_action_kernel", {}).get("source_action_manifest_validation_passed") is not True:
        errors.append("source action kernel validator evidence missing")
    if payloads.get("source_wave", {}).get("source_wave_smoke_passed") is not True:
        errors.append("source wave smoke evidence missing")
    if payloads.get("snapshot_relay", {}).get("snapshot_validation_passed") is not True:
        errors.append("snapshot relay validation evidence missing")
    if payloads.get("ci_full_discovery_harness", {}).get("full_discovery_run_inside_ai") is not False:
        errors.append("CI full discovery harness must keep full_discovery_run_inside_ai=false")


def validate_scope_matrix(payload: Mapping[str, Any], errors: list[str]) -> None:
    entries = scope_entries(payload)
    present = {str(item.get("subsystem_id", "")) for item in entries}
    expected = set(RESULT_FILES)
    for subsystem in sorted(expected - present):
        errors.append(f"scope matrix missing {subsystem}")
    for item in entries:
        subsystem = str(item.get("subsystem_id", ""))
        if subsystem in RESULT_FILES and item.get("result_file") != RESULT_FILES[subsystem]:
            errors.append(f"scope matrix result_file mismatch for {subsystem}")
        if item.get("promotion_included") is not True:
            errors.append(f"scope matrix requires {subsystem}.promotion_included=true")
        for field in ("production_claim", "public_launch_claim", "unsafe_actions_enabled"):
            if item.get(field) is not False:
                errors.append(f"scope matrix requires {subsystem}.{field}=false")


def validate_validation_matrix(payload: Mapping[str, Any], result: Mapping[str, Any], errors: list[str]) -> None:
    if payload.get("full_unittest_discovery_status") != "pass":
        errors.append("validation matrix requires full_unittest_discovery_status=pass")
    for key, expected in (
        ("full_unittest_discovery_count", 5008),
        ("full_unittest_discovery_failures", 0),
        ("full_unittest_discovery_errors", 0),
        ("full_unittest_discovery_exit_code", 0),
    ):
        if payload.get(key) != expected:
            errors.append(f"validation matrix requires {key}={expected}")
        if result.get(key) != expected:
            errors.append(f"result requires {key}={expected}")
    if payload.get("full_discovery_run_inside_ai") is not False:
        errors.append("validation matrix requires full_discovery_run_inside_ai=false")
    if result.get("full_unittest_discovery_passed") is not True:
        errors.append("result requires full_unittest_discovery_passed=true")
    if payload.get("expected_refusal_trace_nonblocking") is not True:
        errors.append("expected refusal trace must be classified as nonblocking")
    commands = payload.get("commands")
    if not isinstance(commands, list) or not commands:
        errors.append("validation matrix requires commands")
        return
    command_text = json.dumps(commands)
    for token in (
        "python scripts/validate_dev_to_main_promotion_03.py",
        "python scripts/validate_source_snapshot_baseline_closeout.py",
        "python scripts/validate_source_action_kernel.py",
        "python scripts/validate_source_wave.py",
        "python scripts/validate_snapshot_relay.py",
        "python scripts/check_architecture_boundaries.py",
        "python scripts/check_generated_artifact_cleanliness.py --check --json",
    ):
        if token not in command_text:
            errors.append(f"validation matrix missing {token}")


def validate_boundary(
    boundary: Mapping[str, Any],
    result: Mapping[str, Any],
    report: Mapping[str, Any],
    errors: list[str],
) -> None:
    for payload_name, payload in (("boundary report", boundary), ("result", result), ("audit report", report)):
        for field in BOUNDARY_FALSE_FIELDS:
            if payload.get(field) is not False:
                errors.append(f"{payload_name} requires {field}=false")
    if result.get("branch_fast_forward_possible") is not True:
        errors.append("result requires branch_fast_forward_possible=true")
    if result.get("promotion_method") != "fast_forward_only":
        errors.append("result requires promotion_method=fast_forward_only")
    if result.get("promotion_performed") is True:
        for field in ("main_pushed", "dev_pushed", "origin_main_equals_origin_dev_after"):
            if result.get(field) is not True:
                errors.append(f"performed promotion requires {field}=true")
        if result.get("ahead_behind_after") != "0 0":
            errors.append("performed promotion requires ahead_behind_after=0 0")


def validate_next_task(payload: Mapping[str, Any], result: Mapping[str, Any], errors: list[str]) -> None:
    next_task = str(payload.get("recommended_next_task", ""))
    if not next_task.startswith("PUBLIC-ALPHA-READONLY-00"):
        errors.append("next task must be PUBLIC-ALPHA-READONLY-00")
    if not str(result.get("recommended_next_task", "")).startswith("PUBLIC-ALPHA-READONLY-00"):
        errors.append("result must recommend PUBLIC-ALPHA-READONLY-00")
    for field in ("production_readiness_claimed", "public_launch_readiness_claimed", "deployment_performed"):
        if payload.get(field) is not False:
            errors.append(f"next task decision requires {field}=false")


def validate_input_state(payload: Mapping[str, Any], errors: list[str]) -> None:
    if payload.get("branch") != "dev":
        errors.append("input state branch must be dev")
    for field in (
        "working_tree_clean_before",
        "source_snapshot_closeout_validator_passed",
        "external_full_discovery_summary_received",
        "external_full_discovery_git_working_tree_clean",
        "source_action_kernel_found",
        "source_wave_found",
        "snapshot_relay_found",
        "ci_full_discovery_harness_found",
        "local_product_loop_baseline_found",
        "expected_refusal_trace_nonblocking",
    ):
        if payload.get(field) is not True:
            errors.append(f"input state requires {field}=true")
    for key, expected in (
        ("external_full_discovery_summary_status", "pass"),
        ("external_full_discovery_tests_run", 5008),
        ("external_full_discovery_failures", 0),
        ("external_full_discovery_errors", 0),
        ("external_full_discovery_exit_code", 0),
    ):
        if payload.get(key) != expected:
            errors.append(f"input state requires {key}={expected!r}")
    for field in ("full_discovery_run_inside_ai", "production_readiness_claimed", "public_launch_readiness_claimed"):
        if payload.get(field) is not False:
            errors.append(f"input state requires {field}=false")


def validate_branch_state(
    root: Path,
    payload: Mapping[str, Any],
    result: Mapping[str, Any],
    errors: list[str],
    warnings: list[str],
) -> None:
    if payload.get("branch") != "dev":
        errors.append("branch state branch must be dev")
    if payload.get("working_tree_clean_before") is not True:
        errors.append("branch state requires working_tree_clean_before=true")
    if payload.get("active_git_operation") is not False:
        errors.append("branch state requires active_git_operation=false")
    recorded = str(payload.get("ahead_behind_origin_main_origin_dev_before", ""))
    if recorded and not recorded.startswith("0 "):
        errors.append(f"recorded origin/main...origin/dev is not fast-forwardable: {recorded}")
    if payload.get("origin_main_can_fast_forward_to_origin_dev") is not True:
        errors.append("origin/main must be fast-forwardable to origin/dev")
    if payload.get("origin_main_ahead_of_origin_dev") is not False:
        errors.append("origin/main must not be ahead of origin/dev")
    if payload.get("origin_main_origin_dev_diverged") is not False:
        errors.append("origin/main and origin/dev must not be diverged")

    current = current_branch_state(root)
    if current.get("branch") != "dev":
        warnings.append(f"current branch is {current.get('branch')}; final state should return to dev")
    current_ab = str(current.get("origin_main_origin_dev_ahead_behind", ""))
    if current_ab:
        parts = current_ab.split()
        if parts and parts[0] != "0":
            errors.append(f"origin/main cannot fast-forward to origin/dev: {current_ab}")
    if result.get("promotion_performed") is True and current_ab != "0 0" and not post_promotion_successor_state(root):
        errors.append(f"post-promotion origin/main and origin/dev must match: {current_ab}")


def validate_repair_log(payload: Mapping[str, Any], errors: list[str]) -> None:
    if payload.get("status") != "pass":
        errors.append("failure repair log status must be pass")
    if payload.get("full_discovery_failures_remaining") != 0:
        errors.append("failure repair log requires full_discovery_failures_remaining=0")
    if payload.get("full_discovery_errors_remaining") != 0:
        errors.append("failure repair log requires full_discovery_errors_remaining=0")
    text = json.dumps(payload)
    if "expected_refusal_trace_nonblocking" not in text:
        errors.append("failure repair log must classify expected refusal trace as nonblocking")


def validate_git_hygiene(root: Path, errors: list[str]) -> None:
    tracked = run_git(root, "ls-files").splitlines()
    forbidden_prefixes = ("instances/", "eureka-instance/", ".aide.local/", "secrets/", "data/public_index/")
    forbidden_exact = {".env"}
    forbidden_fragments = ("full_unittest_stdout.txt", "full_unittest_stderr.txt")
    for path in tracked:
        normalized = path.replace("\\", "/")
        if normalized in forbidden_exact or normalized.startswith(forbidden_prefixes):
            errors.append(f"forbidden tracked path: {normalized}")
        if any(fragment in normalized for fragment in forbidden_fragments):
            errors.append(f"raw full discovery log committed: {normalized}")


def scope_entries(payload: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    entries = payload.get("promotion_scope", [])
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


POST_PROMOTION_SUCCESSOR_PREFIXES = (
    "ARTIFACT-EVIDENCE-GAP-BATCH-",
    "EXTERNAL-FULL-DISCOVERY-RERUN-",
    "HISTORICAL-QUEUE-VALIDATOR-DRIFT-REPAIR-",
    "HUMAN-ARTIFACT-REVIEW-BATCH-",
    "MANUAL-ARTIFACT-OBSERVATION-BATCH-",
    "PUBLIC-ALPHA-READINESS-",
    "REVIEWED-ARTIFACT-CORPUS-BATCH-",
    "REVIEWED-ARTIFACT-RECORD-GATE-",
    "SOURCE-SNAPSHOT-FULL-DISCOVERY-INGEST-",
    "SOURCE-SNAPSHOT-RELEASE-GATE-CLOSEOUT-",
    "WAITING_FOR_EXTERNAL_ARTIFACT_EVIDENCE",
    "WAITING_FOR_EXTERNAL_FULL_DISCOVERY",
    "WAITING_FOR_USER_HARDWARE_DETAILS",
)


def post_promotion_successor_state(root: Path) -> bool:
    queue = root / ".aide" / "queue" / "index.yaml"
    if not queue.is_file():
        return False
    current = ""
    for line in queue.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("current_recommended_task:"):
            current = stripped.split(":", 1)[1].strip().split()[0]
            break
    return current in {
        "PUBLIC-ALPHA-READONLY-00",
        "PUBLIC-ALPHA-HOSTING-READINESS-00",
        "PUBLIC-ALPHA-READONLY-CLOSEOUT-01",
        "DEV-TO-MAIN-PROMOTION-REVIEW-04",
        "PUBLIC-ALPHA-LAUNCH-CANDIDATE-00",
        "PUBLIC-ALPHA-DEPLOY-DRY-RUN-00",
        "DEV-TO-MAIN-PROMOTION-REVIEW-05",
        "PUBLIC-ALPHA-LAUNCH-00",
        "PUBLIC-DEMAND-SIGNAL-00",
        "PUBLIC-SOURCE-REQUEST-QUEUE-00",
        "NATIVE-SNAPSHOT-CLIENT-00",
        "INDEXLESS-LIVE-SEARCH-FALLBACK-00",
        "REVIEW-LEDGER-00",
        "WORKBENCH-RUN-REVIEW-PROJECTION-00",
        "SURFACE-KERNEL-00",
        "BASELINE-RENDERERS-00",
        "HARD-QUERY-EVAL-00",
        "REVIEWED-SEED-CORPUS-00",
        "MANUAL-OBSERVATION-BATCH-00",
        "HUMAN-REVIEW-BATCH-00",
        "REVIEWED-CORPUS-SEED-BATCH-01",
        "MANUAL-OBSERVATION-BATCH-01",
        "HUMAN-REVIEW-BATCH-01",
        "REVIEWED-CORPUS-SEED-BATCH-02",
        "SOURCE-SNAPSHOT-FULL-DISCOVERY-INGEST-01",
        "ARCHITECTURE-BOUNDARY-DRIFT-REPAIR-01",
        "QUEUE-HANDOFF-DRIFT-REPAIR-01",
        "SOURCE-SNAPSHOT-BASELINE-DRIFT-REPAIR-01",
        "GENERATED-ARTIFACT-DRIFT-REPAIR-01",
        "CONTRACT-SCHEMA-DRIFT-REPAIR-01",
        "SOURCE-SNAPSHOT-FAILURE-REPAIR-01",
        "EXTERNAL-FULL-DISCOVERY-RERUN-02",
    } or any(current.startswith(prefix) for prefix in POST_PROMOTION_SUCCESSOR_PREFIXES)


def require_file(root: Path, rel: str, errors: list[str]) -> None:
    if not (root / rel).is_file():
        errors.append(f"missing required file: {rel}")


def load_json(path: Path, errors: list[str]) -> dict[str, Any]:
    if not path.is_file():
        errors.append(f"missing json file: {relative(path)}")
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"invalid json {relative(path)}: {exc}")
        return {}
    return payload if isinstance(payload, dict) else {}


def run_git(root: Path, *args: str) -> str:
    completed = subprocess.run(["git", *args], cwd=root, text=True, capture_output=True, check=True)
    return completed.stdout.strip()


def relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


if __name__ == "__main__":
    raise SystemExit(main())
