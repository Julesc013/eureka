#!/usr/bin/env python3
"""Validate DEV-TO-MAIN-PROMOTION-REVIEW-04 evidence and branch gates."""

from __future__ import annotations

EUREKA_SCRIPT_COMPAT_WRAPPER = True

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
TASK = "DEV-TO-MAIN-PROMOTION-REVIEW-04"
PASS_STATUSES = {"pass", "pass_with_warnings"}

RESULT_FILES = {
    "public_alpha_readonly_foundation": "control/inventory/public_alpha_readonly_00_result.json",
    "public_alpha_hosting_readiness": "control/inventory/public_alpha_hosting_result.json",
    "public_alpha_readonly_closeout": "control/inventory/public_alpha_readonly_closeout_result.json",
    "snapshot_relay": "control/inventory/snapshot_relay_result.json",
    "source_wave": "control/inventory/source_wave_result.json",
    "source_action_kernel": "control/inventory/source_action_kernel_result.json",
    "source_snapshot_closeout": "control/inventory/source_snapshot_closeout_result.json",
    "ci_full_discovery_harness": "control/inventory/ci_full_discovery_harness_result.json",
    "local_product_loop_baseline": "control/inventory/dev_to_main_promotion_03_result.json",
}

REQUIRED_FILES = {
    "control/inventory/dev_to_main_promotion_04_input_state.json",
    "control/inventory/dev_to_main_promotion_04_branch_state.json",
    "control/inventory/dev_to_main_promotion_04_scope_matrix.json",
    "control/inventory/dev_to_main_promotion_04_validation_matrix.json",
    "control/inventory/dev_to_main_promotion_04_boundary_report.json",
    "control/inventory/dev_to_main_promotion_04_result.json",
    "control/inventory/dev_to_main_promotion_04_next_task_decision.json",
    "control/inventory/dev_to_main_promotion_04_failure_repair_log.json",
    "control/audits/dev-to-main-promotion-review-04-v0/README.md",
    "control/audits/dev-to-main-promotion-review-04-v0/dev_to_main_promotion_04_report.json",
    "control/audits/dev-to-main-promotion-review-04-v0/branch_state.md",
    "control/audits/dev-to-main-promotion-review-04-v0/scope_matrix.md",
    "control/audits/dev-to-main-promotion-review-04-v0/validation_matrix.md",
    "control/audits/dev-to-main-promotion-review-04-v0/boundary_report.md",
    "control/audits/dev-to-main-promotion-review-04-v0/full_discovery_evidence.md",
    "control/audits/dev-to-main-promotion-review-04-v0/evidence_time_head_warning.md",
    "control/audits/dev-to-main-promotion-review-04-v0/promotion_result.md",
    "control/audits/dev-to-main-promotion-review-04-v0/validation.md",
    "control/audits/dev-to-main-promotion-review-04-v0/generated/sample_summary.md",
    "docs/operations/DEV_TO_MAIN_PROMOTION_REVIEW_04.md",
    "docs/operations/POST_PUBLIC_ALPHA_READONLY_PROMOTION_PLAN.md",
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
    "public_live_source_fanout_enabled",
    "public_mutation_enabled",
    "download_performed",
    "upload_performed",
    "extraction_executed",
    "model_provider_used",
    "deployment_performed",
    "production_readiness_claimed",
    "public_launch_readiness_claimed",
    "marketplace_or_app_store_readiness_claimed",
)

ALLOWED_EVIDENCE_DELTA_PREFIXES = (
    ".aide/queue/DEV-TO-MAIN-PROMOTION-REVIEW-04/",
    ".aide/queue/PUBLIC-ALPHA-LAUNCH-CANDIDATE-00/",
    ".aide/queue/PUBLIC-DEMAND-SIGNAL-00/",
    ".aide/queue/PUBLIC-SOURCE-REQUEST-QUEUE-00/",
    ".aide/queue/index.yaml",
    ".aide/context/latest-task-packet.md",
    ".aide/context/latest-review-packet.md",
    ".aide/reports/eureka-repo-health.",
    "control/inventory/dev_to_main_promotion_04_",
    "control/audits/dev-to-main-promotion-review-04-v0/",
    "control/policies/generated_artifact_policy.json",
    "docs/operations/DEV_TO_MAIN_PROMOTION_REVIEW_04.md",
    "docs/operations/POST_PUBLIC_ALPHA_READONLY_PROMOTION_PLAN.md",
    "scripts/validate_dev_to_main_promotion_04.py",
    "tests/operations/test_dev_to_main_promotion_04.py",
    "tests/scripts/test_validate_dev_to_main_promotion_04.py",
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
        print(f"dev to main promotion 04 validation: {result['status']}", file=stdout)
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

    payloads = {name: load_json(root / rel, errors) for name, rel in RESULT_FILES.items()}
    input_state = load_json(root / "control/inventory/dev_to_main_promotion_04_input_state.json", errors)
    branch_state = load_json(root / "control/inventory/dev_to_main_promotion_04_branch_state.json", errors)
    scope_matrix = load_json(root / "control/inventory/dev_to_main_promotion_04_scope_matrix.json", errors)
    validation_matrix = load_json(root / "control/inventory/dev_to_main_promotion_04_validation_matrix.json", errors)
    boundary = load_json(root / "control/inventory/dev_to_main_promotion_04_boundary_report.json", errors)
    result = load_json(root / "control/inventory/dev_to_main_promotion_04_result.json", errors)
    next_task = load_json(root / "control/inventory/dev_to_main_promotion_04_next_task_decision.json", errors)
    repair_log = load_json(root / "control/inventory/dev_to_main_promotion_04_failure_repair_log.json", errors)
    report = load_json(root / "control/audits/dev-to-main-promotion-review-04-v0/dev_to_main_promotion_04_report.json", errors)

    validate_result_files(payloads, input_state, errors)
    validate_scope_matrix(scope_matrix, errors)
    validate_full_discovery(input_state, validation_matrix, result, errors)
    validate_boundary(boundary, result, report, errors)
    validate_next_task(next_task, result, errors)
    validate_branch_state(root, branch_state, result, errors, warnings)
    validate_evidence_delta(root, input_state, errors)
    validate_repair_log(repair_log, errors)
    validate_git_hygiene(root, errors)

    return {
        "schema_version": "dev_to_main_promotion_04_validation.v0",
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


def validate_result_files(payloads: Mapping[str, Mapping[str, Any]], input_state: Mapping[str, Any], errors: list[str]) -> None:
    for subsystem, payload in payloads.items():
        status = str(payload.get("status", ""))
        if subsystem == "source_snapshot_closeout":
            prior_promotion_pass = payloads.get("local_product_loop_baseline", {}).get("status") in PASS_STATUSES
            if status not in PASS_STATUSES and not prior_promotion_pass:
                errors.append("source snapshot closeout must be pass or covered by prior promotion pass")
        elif status not in PASS_STATUSES:
            errors.append(f"{subsystem} result status must be pass/pass_with_warnings, got {status!r}")

    public_alpha = payloads.get("public_alpha_readonly_foundation", {})
    hosting = payloads.get("public_alpha_hosting_readiness", {})
    closeout = payloads.get("public_alpha_readonly_closeout", {})
    if public_alpha.get("read_only") is not True or public_alpha.get("reviewed_index_only") is not True:
        errors.append("public alpha foundation must be reviewed-index read-only")
    if hosting.get("validator_passed") is not True or hosting.get("focused_tests_passed") is not True:
        errors.append("public alpha hosting readiness must have validator and focused tests passed")
    for field in (
        "public_alpha_readonly_verified",
        "public_alpha_hosting_verified",
        "snapshot_relay_verified",
        "focused_validators_passed",
        "external_full_discovery_summary_received",
        "full_unittest_discovery_passed",
    ):
        if closeout.get(field) is not True:
            errors.append(f"public alpha closeout requires {field}=true")
    if input_state.get("public_alpha_readonly_result_file") != RESULT_FILES["public_alpha_readonly_foundation"]:
        errors.append("input state must map public_alpha_readonly_result_file to public_alpha_readonly_00_result.json")

    for subsystem, payload in payloads.items():
        for field in (
            "deployment_performed",
            "production_readiness_claimed",
            "public_launch_readiness_claimed",
            "live_source_call_performed",
            "source_probe_executed",
            "download_performed",
            "extraction_executed",
            "model_provider_used",
        ):
            if payload.get(field) is True:
                errors.append(f"{subsystem} result has unsafe flag {field}=true")


def validate_scope_matrix(payload: Mapping[str, Any], errors: list[str]) -> None:
    entries = scope_entries(payload)
    present = {str(item.get("subsystem_id", "")) for item in entries}
    for subsystem in sorted(set(RESULT_FILES) - present):
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


def validate_full_discovery(
    input_state: Mapping[str, Any],
    validation_matrix: Mapping[str, Any],
    result: Mapping[str, Any],
    errors: list[str],
) -> None:
    expected_count = 5057
    for payload_name, payload in (("input state", input_state), ("validation matrix", validation_matrix), ("result", result)):
        if payload.get("full_unittest_discovery_passed") is not True:
            errors.append(f"{payload_name} requires full_unittest_discovery_passed=true")
        if payload.get("full_unittest_discovery_count") != expected_count:
            errors.append(f"{payload_name} requires full_unittest_discovery_count={expected_count}")
        if payload.get("full_discovery_failures_remaining", payload.get("full_unittest_discovery_failures")) != 0:
            errors.append(f"{payload_name} requires zero full discovery failures")
        if payload.get("full_discovery_errors_remaining", payload.get("full_unittest_discovery_errors")) != 0:
            errors.append(f"{payload_name} requires zero full discovery errors")
        if payload.get("full_unittest_discovery_exit_code", payload.get("full_discovery_exit_code")) != 0:
            errors.append(f"{payload_name} requires full discovery exit code 0")
        if payload.get("full_discovery_run_inside_ai") is not False:
            errors.append(f"{payload_name} requires full_discovery_run_inside_ai=false")
        if payload.get("expected_refusal_trace_nonblocking") is not True:
            errors.append(f"{payload_name} must classify expected refusal trace as nonblocking")
    if input_state.get("external_full_discovery_head") != input_state.get("review_head"):
        errors.append("external full discovery head must match review head at evidence intake")
    if result.get("status") != "pass":
        errors.append("promotion result status must be pass")


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
    for source, candidate in (("next task decision", payload), ("result", result)):
        next_task = str(candidate.get("recommended_next_task", ""))
        if not next_task.startswith("PUBLIC-ALPHA-LAUNCH-CANDIDATE-00"):
            errors.append(f"{source} must recommend PUBLIC-ALPHA-LAUNCH-CANDIDATE-00")
        for field in ("production_readiness_claimed", "public_launch_readiness_claimed", "deployment_performed"):
            if candidate.get(field) is not False:
                errors.append(f"{source} requires {field}=false")


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
        left, _, _right = current_ab.partition(" ")
        if left != "0":
            errors.append(f"origin/main cannot fast-forward to origin/dev: {current_ab}")
    if result.get("promotion_performed") is True and current_ab != "0 0" and not post_promotion_successor_state(root):
        errors.append(f"post-promotion origin/main and origin/dev must match: {current_ab}")


def validate_evidence_delta(root: Path, input_state: Mapping[str, Any], errors: list[str]) -> None:
    if post_promotion_successor_state(root):
        return
    evidence_head = str(input_state.get("external_full_discovery_head") or "")
    if not evidence_head:
        errors.append("input state requires external_full_discovery_head")
        return
    head = run_git(root, "rev-parse", "HEAD")
    if evidence_head == head:
        return
    changed = run_git(root, "diff", "--name-only", f"{evidence_head}..HEAD").splitlines()
    invalid = [path for path in changed if not path_allowed_for_evidence_delta(path)]
    if invalid:
        errors.append(f"external full discovery evidence head delta includes non-promotion files: {invalid}")
    if input_state.get("evidence_time_head_warning_nonblocking") is not True:
        errors.append("input state must classify evidence-time head warning as nonblocking when heads differ")


def path_allowed_for_evidence_delta(path: str) -> bool:
    normalized = path.replace("\\", "/")
    return any(normalized.startswith(prefix) for prefix in ALLOWED_EVIDENCE_DELTA_PREFIXES)


def validate_repair_log(payload: Mapping[str, Any], errors: list[str]) -> None:
    if payload.get("status") != "pass":
        errors.append("failure repair log status must be pass")
    if payload.get("full_discovery_failures_remaining") != 0:
        errors.append("failure repair log requires full_discovery_failures_remaining=0")
    if payload.get("full_discovery_errors_remaining") != 0:
        errors.append("failure repair log requires full_discovery_errors_remaining=0")
    if payload.get("fresh_external_full_discovery_consumed") is not True:
        errors.append("failure repair log must record fresh external full discovery consumption")


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
        "PUBLIC-ALPHA-LAUNCH-CANDIDATE-00",
        "PUBLIC-ALPHA-DEPLOY-DRY-RUN-00",
        "DEV-TO-MAIN-PROMOTION-REVIEW-05",
        "PUBLIC-ALPHA-LAUNCH-00",
        "PUBLIC-DEMAND-SIGNAL-00",
        "PUBLIC-SOURCE-REQUEST-QUEUE-00",
        "NATIVE-SNAPSHOT-CLIENT-00",
    }


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
