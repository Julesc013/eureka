#!/usr/bin/env python3
"""Validate SOURCE-SNAPSHOT-BASELINE-CLOSEOUT-01 evidence and gates."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
TASK = "SOURCE-SNAPSHOT-BASELINE-CLOSEOUT-01"
PASS_STATUSES = {"pass", "pass_with_warnings"}

RESULT_FILES = {
    "source_action_kernel": "control/inventory/source_action_kernel_result.json",
    "source_wave": "control/inventory/source_wave_result.json",
    "snapshot_relay": "control/inventory/snapshot_relay_result.json",
}

REQUIRED_FILES = {
    "control/inventory/source_snapshot_closeout_input_state.json",
    "control/inventory/source_snapshot_closeout_branch_state.json",
    "control/inventory/source_snapshot_closeout_scope_matrix.json",
    "control/inventory/source_snapshot_closeout_failure_inventory.json",
    "control/inventory/source_snapshot_closeout_repair_matrix.json",
    "control/inventory/source_snapshot_closeout_validation_matrix.json",
    "control/inventory/source_snapshot_closeout_boundary_report.json",
    "control/inventory/source_snapshot_closeout_full_discovery_result.json",
    "control/inventory/source_snapshot_closeout_result.json",
    "control/inventory/source_snapshot_closeout_next_task_decision.json",
    "control/inventory/source_snapshot_closeout_failure_repair_log.json",
    "control/audits/source-snapshot-baseline-closeout-01-v0/README.md",
    "control/audits/source-snapshot-baseline-closeout-01-v0/source_snapshot_closeout_report.json",
    "control/audits/source-snapshot-baseline-closeout-01-v0/branch_state.md",
    "control/audits/source-snapshot-baseline-closeout-01-v0/scope_matrix.md",
    "control/audits/source-snapshot-baseline-closeout-01-v0/failure_inventory.md",
    "control/audits/source-snapshot-baseline-closeout-01-v0/repair_matrix.md",
    "control/audits/source-snapshot-baseline-closeout-01-v0/validation_matrix.md",
    "control/audits/source-snapshot-baseline-closeout-01-v0/boundary_report.md",
    "control/audits/source-snapshot-baseline-closeout-01-v0/full_discovery_summary.md",
    "control/audits/source-snapshot-baseline-closeout-01-v0/next_task_decision.md",
    "control/audits/source-snapshot-baseline-closeout-01-v0/validation.md",
    "control/audits/source-snapshot-baseline-closeout-01-v0/generated/selected_tests.json",
    "control/audits/source-snapshot-baseline-closeout-01-v0/generated/full_unittest_summary.txt",
    "control/audits/source-snapshot-baseline-closeout-01-v0/generated/sample_summary.md",
    "docs/operations/SOURCE_SNAPSHOT_BASELINE_CLOSEOUT.md",
    "docs/operations/POST_SOURCE_SNAPSHOT_CLOSEOUT_PLAN.md",
}

BOUNDARY_FALSE_FIELDS = (
    "secrets_committed",
    "operator_tokens_committed",
    "committed_instance_state",
    "master_index_mutated",
    "committed_data_public_index_mutated",
    "raw_live_source_response_committed",
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

RESULT_REQUIRED_BOOLEANS = (
    "source_action_kernel_verified",
    "source_wave_verified",
    "snapshot_relay_verified",
    "focused_validators_passed",
    "architecture_boundaries_passed",
    "generated_artifact_cleanliness_passed",
    "aide_checks_passed",
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
        print(f"source snapshot baseline closeout validation: {result['status']}", file=stdout)
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

    prior_results = {
        key: load_json(root / rel, errors)
        for key, rel in RESULT_FILES.items()
    }
    input_state = load_json(root / "control/inventory/source_snapshot_closeout_input_state.json", errors)
    branch_state = load_json(root / "control/inventory/source_snapshot_closeout_branch_state.json", errors)
    scope_matrix = load_json(root / "control/inventory/source_snapshot_closeout_scope_matrix.json", errors)
    failure_inventory = load_json(root / "control/inventory/source_snapshot_closeout_failure_inventory.json", errors)
    repair_matrix = load_json(root / "control/inventory/source_snapshot_closeout_repair_matrix.json", errors)
    validation_matrix = load_json(root / "control/inventory/source_snapshot_closeout_validation_matrix.json", errors)
    boundary = load_json(root / "control/inventory/source_snapshot_closeout_boundary_report.json", errors)
    full_discovery = load_json(root / "control/inventory/source_snapshot_closeout_full_discovery_result.json", errors)
    result = load_json(root / "control/inventory/source_snapshot_closeout_result.json", errors)
    next_task = load_json(root / "control/inventory/source_snapshot_closeout_next_task_decision.json", errors)
    repo_health = load_json(root / ".aide/reports/eureka-repo-health.json", errors)

    validate_prior_results(prior_results, errors)
    validate_input_state(input_state, errors)
    validate_branch_state(root, branch_state, errors, warnings)
    validate_scope_matrix(scope_matrix, errors)
    validate_failure_inventory(failure_inventory, full_discovery, result, errors)
    validate_repair_matrix(repair_matrix, errors)
    validate_validation_matrix(validation_matrix, errors)
    validate_boundary(boundary, result, errors)
    validate_full_discovery(full_discovery, result, errors)
    validate_result(result, errors)
    validate_next_task(next_task, result, errors)
    validate_repo_health(root, repo_health, result, errors)

    return {
        "schema_version": "source_snapshot_closeout_validation.v0",
        "task": TASK,
        "status": "pass" if not errors else "fail",
        "errors": errors,
        "warnings": warnings,
        "full_unittest_discovery_passed": full_discovery.get("status") == "pass",
        "remaining_failures": full_discovery.get("failures", 0),
        "remaining_errors": full_discovery.get("errors", 0),
    }


def validate_prior_results(payloads: Mapping[str, Mapping[str, Any]], errors: list[str]) -> None:
    for subsystem, payload in payloads.items():
        if payload.get("status") not in PASS_STATUSES:
            errors.append(f"{subsystem} status must be pass/pass_with_warnings")
        for field in (
            "production_readiness_claimed",
            "public_launch_readiness_claimed",
            "deployment_performed",
            "operator_instance_mutated",
            "master_index_mutated",
            "committed_data_public_index_mutated",
            "raw_live_source_response_committed",
            "download_performed",
            "extraction_executed",
            "model_provider_used",
        ):
            if payload.get(field) is True:
                errors.append(f"{subsystem} unsafe field is true: {field}")


def validate_input_state(payload: Mapping[str, Any], errors: list[str]) -> None:
    if payload.get("task") != TASK:
        errors.append("input state task mismatch")
    if payload.get("branch") != "dev":
        errors.append("input state branch must be dev")
    for field in ("source_action_kernel_found", "source_wave_found", "snapshot_relay_found", "working_tree_clean_before"):
        if payload.get(field) is not True:
            errors.append(f"input state requires {field}=true")
    for field in ("production_readiness_claimed", "public_launch_readiness_claimed"):
        if payload.get(field) is not False:
            errors.append(f"input state requires {field}=false")


def validate_branch_state(root: Path, payload: Mapping[str, Any], errors: list[str], warnings: list[str]) -> None:
    if payload.get("branch") != "dev":
        errors.append("branch state branch must be dev")
    if payload.get("working_tree_clean_before") is not True:
        errors.append("branch state requires working_tree_clean_before=true")
    ahead_behind = str(payload.get("ahead_behind_origin_main_origin_dev", ""))
    if not ahead_behind.startswith("0\t") and not ahead_behind.startswith("0 "):
        errors.append("origin/main must not be ahead of origin/dev")
    current = current_branch_state(root)
    if current.get("head") != payload.get("head"):
        warnings.append("branch state head is evidence-time only and differs from current working tree")


def validate_scope_matrix(payload: Mapping[str, Any], errors: list[str]) -> None:
    entries = payload.get("scope")
    if not isinstance(entries, list):
        errors.append("scope matrix requires scope list")
        return
    present = {item.get("subsystem_id") for item in entries if isinstance(item, Mapping)}
    for subsystem in RESULT_FILES:
        if subsystem not in present:
            errors.append(f"scope matrix missing {subsystem}")
    for item in entries:
        if not isinstance(item, Mapping):
            errors.append("scope entry must be object")
            continue
        if item.get("unsafe_boundaries_false") is not True:
            errors.append(f"scope entry {item.get('subsystem_id')} requires unsafe_boundaries_false=true")
        if item.get("closeout_needed") is not True:
            errors.append(f"scope entry {item.get('subsystem_id')} requires closeout_needed=true")


def validate_failure_inventory(
    payload: Mapping[str, Any],
    full_discovery: Mapping[str, Any],
    result: Mapping[str, Any],
    errors: list[str],
) -> None:
    entries = payload.get("failures")
    if not isinstance(entries, list):
        errors.append("failure inventory requires failures list")
        return
    expected = int(full_discovery.get("failures", 0) or 0) + int(full_discovery.get("errors", 0) or 0)
    if expected and len(entries) != expected:
        errors.append(f"failure inventory count {len(entries)} does not match full discovery red count {expected}")
    categories = {str(item.get("suspected_root_cause")) for item in entries if isinstance(item, Mapping)}
    for category in (
        "queue_handoff_drift",
        "checksum_manifest_drift",
        "public_index_generated_drift",
        "legacy_leakage_validator_drift",
    ):
        if category not in categories:
            errors.append(f"failure inventory missing category {category}")
    if result.get("status") == "pass" and entries:
        errors.append("result cannot pass while failure inventory contains failures")
    for item in entries:
        if not isinstance(item, Mapping):
            errors.append("failure inventory entry must be object")
            continue
        for key in ("test_module", "test_name", "failure_type", "owning_subsystem", "suspected_root_cause", "blocking_level", "rerun_command"):
            if not item.get(key):
                errors.append(f"failure inventory entry missing {key}")


def validate_repair_matrix(payload: Mapping[str, Any], errors: list[str]) -> None:
    repairs = payload.get("repairs")
    if not isinstance(repairs, list) or not repairs:
        errors.append("repair matrix requires repairs")
        return
    statuses = {str(item.get("repair_status")) for item in repairs if isinstance(item, Mapping)}
    if "blocked_forbidden_path" not in statuses:
        errors.append("repair matrix must record blocked_forbidden_path")


def validate_validation_matrix(payload: Mapping[str, Any], errors: list[str]) -> None:
    commands = payload.get("commands")
    if not isinstance(commands, list) or not commands:
        errors.append("validation matrix requires commands")
        return
    text = json.dumps(commands)
    for command in (
        "python scripts/validate_source_action_kernel.py",
        "python scripts/validate_source_wave.py",
        "python scripts/validate_snapshot_relay.py",
        "python -m unittest discover -s tests -t .",
    ):
        if command not in text:
            errors.append(f"validation matrix missing {command}")


def validate_boundary(boundary: Mapping[str, Any], result: Mapping[str, Any], errors: list[str]) -> None:
    for payload_name, payload in (("boundary report", boundary), ("result", result)):
        for field in BOUNDARY_FALSE_FIELDS:
            if payload.get(field) is not False:
                errors.append(f"{payload_name} requires {field}=false")


def validate_full_discovery(full_discovery: Mapping[str, Any], result: Mapping[str, Any], errors: list[str]) -> None:
    if full_discovery.get("command") != "python -m unittest discover -s tests -t .":
        errors.append("full discovery result command mismatch")
    status = full_discovery.get("status")
    if status not in {"pass", "fail"}:
        errors.append("full discovery status must be pass or fail")
    passed = status == "pass"
    if result.get("full_unittest_discovery_passed") is not passed:
        errors.append("result full_unittest_discovery_passed must match full discovery result")
    if not passed:
        if result.get("status") not in {"blocked", "fail", "partial"}:
            errors.append("red full discovery requires non-pass closeout status")
        if int(full_discovery.get("failures", 0) or 0) <= 0 and int(full_discovery.get("errors", 0) or 0) <= 0:
            errors.append("red full discovery requires failures/errors counts")


def validate_result(result: Mapping[str, Any], errors: list[str]) -> None:
    if result.get("task") != TASK:
        errors.append("result task mismatch")
    if result.get("status") not in {"pass", "pass_with_warnings", "partial", "blocked", "fail"}:
        errors.append("result status invalid")
    for field in RESULT_REQUIRED_BOOLEANS:
        if result.get(field) is not True:
            errors.append(f"result requires {field}=true")
    if result.get("status") == "pass":
        for field in (
            "full_unittest_discovery_passed",
            "source_action_warning_resolved",
            "source_wave_warning_resolved",
            "snapshot_relay_warning_resolved",
            "dev_ready_for_main_promotion",
            "public_alpha_can_start_after_promotion",
        ):
            if result.get(field) is not True:
                errors.append(f"pass result requires {field}=true")
    else:
        if result.get("dev_ready_for_main_promotion") is not False:
            errors.append("non-pass result requires dev_ready_for_main_promotion=false")
        if result.get("public_alpha_can_start_after_promotion") is not False:
            errors.append("non-pass result requires public_alpha_can_start_after_promotion=false")


def validate_next_task(payload: Mapping[str, Any], result: Mapping[str, Any], errors: list[str]) -> None:
    next_task = str(payload.get("recommended_next_task", ""))
    if result.get("status") == "pass":
        if not next_task.startswith("DEV-TO-MAIN-PROMOTION-REVIEW-03"):
            errors.append("passing closeout must recommend DEV-TO-MAIN-PROMOTION-REVIEW-03")
    elif not next_task.startswith("SOURCE-SNAPSHOT-BASELINE-CLOSEOUT-01-CONTINUE"):
        errors.append("blocked closeout must recommend SOURCE-SNAPSHOT-BASELINE-CLOSEOUT-01-CONTINUE")
    for field in ("production_readiness_claimed", "public_launch_readiness_claimed"):
        if payload.get(field) is not False:
            errors.append(f"next task requires {field}=false")


def validate_repo_health(root: Path, payload: Mapping[str, Any], result: Mapping[str, Any], errors: list[str]) -> None:
    current = current_branch_state(root)
    if payload.get("head") != current.get("head"):
        errors.append("repo health head must match current HEAD")
    if payload.get("origin_dev") != current.get("origin_dev"):
        errors.append("repo health origin_dev must match current origin/dev")
    task = str(payload.get("current_recommended_task", ""))
    if result.get("status") == "pass":
        if not task.startswith("DEV-TO-MAIN-PROMOTION-REVIEW-03"):
            errors.append("repo health must recommend promotion after passing closeout")
    elif not task.startswith("SOURCE-SNAPSHOT-BASELINE-CLOSEOUT-01-CONTINUE"):
        errors.append("repo health must recommend closeout continuation while blocked")


def current_branch_state(root: Path) -> dict[str, str]:
    def git(*args: str) -> str:
        completed = subprocess.run(
            ["git", *args],
            cwd=root,
            text=True,
            capture_output=True,
            check=True,
        )
        return completed.stdout.strip()

    return {
        "branch": git("branch", "--show-current"),
        "head": git("rev-parse", "HEAD"),
        "origin_main": git("rev-parse", "origin/main"),
        "origin_dev": git("rev-parse", "origin/dev"),
        "ahead_behind_origin_main_origin_dev": git("rev-list", "--left-right", "--count", "origin/main...origin/dev"),
    }


def require_file(root: Path, rel: str, errors: list[str]) -> None:
    if not (root / rel).is_file():
        errors.append(f"required file missing: {rel}")


def load_json(path: Path, errors: list[str]) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"missing JSON file: {path.relative_to(REPO_ROOT)}")
        return {}
    except json.JSONDecodeError as exc:
        errors.append(f"invalid JSON file: {path.relative_to(REPO_ROOT)}: {exc}")
        return {}
    if not isinstance(payload, dict):
        errors.append(f"JSON file must contain object: {path.relative_to(REPO_ROOT)}")
        return {}
    return payload


if __name__ == "__main__":
    raise SystemExit(main())
