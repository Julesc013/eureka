from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
from typing import Any, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]
WAITING_STATUS = "waiting_for_external_full_discovery"

PRIOR_RESULTS = {
    "deploy_dry_run": "control/inventory/public_alpha_deploy_dry_run_result.json",
    "launch_candidate": "control/inventory/public_alpha_launch_candidate_result.json",
    "readonly_closeout": "control/inventory/public_alpha_readonly_closeout_result.json",
    "readonly": "control/inventory/public_alpha_readonly_00_result.json",
    "hosting": "control/inventory/public_alpha_hosting_result.json",
    "snapshot_relay": "control/inventory/snapshot_relay_result.json",
    "source_wave": "control/inventory/source_wave_result.json",
    "source_action_kernel": "control/inventory/source_action_kernel_result.json",
    "promotion_04": "control/inventory/dev_to_main_promotion_04_result.json",
}

REQUIRED_JSON = [
    "control/inventory/dev_to_main_promotion_05_input_state.json",
    "control/inventory/dev_to_main_promotion_05_branch_state.json",
    "control/inventory/dev_to_main_promotion_05_scope_matrix.json",
    "control/inventory/dev_to_main_promotion_05_validation_matrix.json",
    "control/inventory/dev_to_main_promotion_05_boundary_report.json",
    "control/inventory/dev_to_main_promotion_05_full_discovery_handoff.json",
    "control/inventory/dev_to_main_promotion_05_full_discovery_result.json",
    "control/inventory/dev_to_main_promotion_05_result.json",
    "control/inventory/dev_to_main_promotion_05_next_task_decision.json",
    "control/inventory/dev_to_main_promotion_05_failure_repair_log.json",
]

REQUIRED_FILES = [
    "control/audits/dev-to-main-promotion-review-05-v0/README.md",
    "control/audits/dev-to-main-promotion-review-05-v0/dev_to_main_promotion_05_report.json",
    "control/audits/dev-to-main-promotion-review-05-v0/branch_state.md",
    "control/audits/dev-to-main-promotion-review-05-v0/scope_matrix.md",
    "control/audits/dev-to-main-promotion-review-05-v0/validation_matrix.md",
    "control/audits/dev-to-main-promotion-review-05-v0/boundary_report.md",
    "control/audits/dev-to-main-promotion-review-05-v0/full_discovery_evidence.md",
    "control/audits/dev-to-main-promotion-review-05-v0/external_full_discovery_handoff.json",
    "control/audits/dev-to-main-promotion-review-05-v0/promotion_result.md",
    "control/audits/dev-to-main-promotion-review-05-v0/validation.md",
    "control/audits/dev-to-main-promotion-review-05-v0/generated/sample_summary.md",
    "docs/operations/DEV_TO_MAIN_PROMOTION_REVIEW_05.md",
    "docs/operations/POST_PUBLIC_ALPHA_DEPLOY_DRY_RUN_PROMOTION_PLAN.md",
]

BOUNDARY_FALSE_FIELDS = [
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
    "site_dist_written",
    "dns_changed",
    "hosting_provider_called",
    "deployment_performed",
    "public_launch_performed",
    "production_readiness_claimed",
    "public_launch_readiness_claimed",
    "marketplace_or_app_store_readiness_claimed",
    "full_discovery_run_inside_ai",
    "raw_full_discovery_logs_committed",
]


def validate_dev_to_main_promotion_05(root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    payloads: dict[str, dict[str, Any]] = {}

    for rel in list(PRIOR_RESULTS.values()) + REQUIRED_JSON:
        path = root / rel
        if not path.exists():
            errors.append(f"missing required JSON: {rel}")
        else:
            payloads[rel] = _read_json(path, rel, errors)

    for rel in REQUIRED_FILES:
        if not (root / rel).exists():
            errors.append(f"missing required file: {rel}")

    _validate_branch_state(root, payloads, errors)
    _validate_prior_results(payloads, errors)
    _validate_boundary_report(payloads, errors)
    _validate_full_discovery_state(payloads, errors)
    _validate_promotion_result(payloads, errors)
    _validate_docs(root, errors)
    _validate_no_forbidden_changed_paths(root, errors)

    result = payloads.get("control/inventory/dev_to_main_promotion_05_result.json", {})
    full = payloads.get("control/inventory/dev_to_main_promotion_05_full_discovery_result.json", {})
    waiting = result.get("status") == WAITING_STATUS and full.get("external_summary_received") is False
    pass_ready = result.get("status") == "pass" and full.get("full_unittest_discovery_passed") is True
    if not waiting and not pass_ready:
        errors.append("promotion-05 result must be pass with full discovery or waiting with a handoff")

    status = "invalid" if errors else (WAITING_STATUS if waiting else "pass")
    return {
        "schema_version": "dev_to_main_promotion_05_validation.v0",
        "task": "DEV-TO-MAIN-PROMOTION-REVIEW-05",
        "status": status,
        "public_alpha_deploy_dry_run_verified": not errors,
        "public_alpha_launch_candidate_verified": not errors,
        "external_full_discovery_summary_received": bool(full.get("external_summary_received")),
        "full_unittest_discovery_passed": bool(full.get("full_unittest_discovery_passed")),
        "promotion_ready": bool(result.get("promotion_ready")),
        "promotion_performed": bool(result.get("promotion_performed")),
        "errors": errors,
    }


def _validate_branch_state(root: Path, payloads: dict[str, dict[str, Any]], errors: list[str]) -> None:
    branch = payloads.get("control/inventory/dev_to_main_promotion_05_branch_state.json", {})
    if branch.get("origin_main_can_fast_forward_to_origin_dev") is not True:
        errors.append("branch state must record origin/main can fast-forward to origin/dev")
    if branch.get("origin_main_ahead_of_origin_dev") is not False:
        errors.append("origin/main must not be ahead of origin/dev")
    if branch.get("origin_main_origin_dev_diverged") is not False:
        errors.append("origin/main and origin/dev must not be diverged")
    if branch.get("active_git_operation") is not False:
        errors.append("active git operation must be false")

    origin_main = _git(root, "rev-parse", "origin/main").stdout.strip()
    head = _git(root, "rev-parse", "HEAD").stdout.strip()
    ancestor = _git(root, "merge-base", "--is-ancestor", origin_main, head)
    if ancestor.returncode != 0:
        errors.append("current HEAD must contain origin/main for future fast-forward promotion")


def _validate_prior_results(payloads: dict[str, dict[str, Any]], errors: list[str]) -> None:
    dry_run = payloads.get(PRIOR_RESULTS["deploy_dry_run"], {})
    if dry_run.get("status") != "pass":
        errors.append("public alpha deploy dry-run result must be pass")
    for field in (
        "deploy_dry_run_rehearsal_passed",
        "deploy_smoke_passed",
        "rollback_rehearsal_passed",
        "deploy_manifest_verified",
        "environment_checklist_verified",
        "launch_candidate_verified",
    ):
        if dry_run.get(field) is not True:
            errors.append(f"deploy dry-run result must set {field}=true")
    for field in (
        "deployment_performed",
        "public_launch_performed",
        "production_readiness_claimed",
        "public_launch_readiness_claimed",
        "public_mutation_enabled",
        "public_live_source_fanout_enabled",
        "downloads_enabled",
        "extraction_enabled",
        "model_provider_enabled",
        "site_dist_written",
        "dns_changed",
    ):
        if dry_run.get(field) is not False:
            errors.append(f"deploy dry-run result must set {field}=false")

    launch = payloads.get(PRIOR_RESULTS["launch_candidate"], {})
    if launch.get("status") != "pass":
        errors.append("public alpha launch-candidate result must be pass")
    for field in (
        "launch_candidate_ready",
        "manual_approval_required_for_launch",
        "public_routes_read_only",
        "public_api_read_only",
    ):
        if launch.get(field) is not True:
            errors.append(f"launch-candidate result must set {field}=true")
    if launch.get("hard_blockers_remaining") != 0:
        errors.append("launch-candidate result must have zero hard blockers")
    for field in (
        "public_mutation_enabled",
        "public_live_source_fanout_enabled",
        "downloads_enabled",
        "extraction_enabled",
        "model_provider_enabled",
        "deployment_performed",
        "production_readiness_claimed",
        "public_launch_readiness_claimed",
    ):
        if launch.get(field) is not False:
            errors.append(f"launch-candidate result must set {field}=false")

    for key in ("readonly_closeout", "readonly", "hosting", "snapshot_relay", "source_wave", "source_action_kernel", "promotion_04"):
        status = payloads.get(PRIOR_RESULTS[key], {}).get("status")
        if status not in {"pass", "pass_with_warnings"}:
            errors.append(f"{key} result must be pass or pass_with_warnings")


def _validate_boundary_report(payloads: dict[str, dict[str, Any]], errors: list[str]) -> None:
    boundary = payloads.get("control/inventory/dev_to_main_promotion_05_boundary_report.json", {})
    for field in BOUNDARY_FALSE_FIELDS:
        if boundary.get(field) is not False:
            errors.append(f"boundary report must set {field}=false")


def _validate_full_discovery_state(payloads: dict[str, dict[str, Any]], errors: list[str]) -> None:
    handoff = payloads.get("control/inventory/dev_to_main_promotion_05_full_discovery_handoff.json", {})
    full = payloads.get("control/inventory/dev_to_main_promotion_05_full_discovery_result.json", {})
    if full.get("external_summary_received") is True:
        if full.get("full_unittest_discovery_passed") is not True:
            errors.append("received external full-discovery summary must pass")
    else:
        if handoff.get("status") != "WAITING_FOR_EXTERNAL_FULL_DISCOVERY":
            errors.append("missing external full-discovery waiting handoff")
        command = handoff.get("preferred_command", "")
        alternate = handoff.get("alternate_command", "")
        if "--gate promotion_gate" not in command:
            errors.append("handoff preferred command must use eureka_test_gate promotion_gate")
        if "../eureka-test-runs/dev_to_main_promotion_05" not in alternate:
            errors.append("handoff alternate command must use repo-external promotion output path")
    if full.get("full_discovery_run_inside_ai") is not False:
        errors.append("full discovery must not run inside AI")


def _validate_promotion_result(payloads: dict[str, dict[str, Any]], errors: list[str]) -> None:
    result = payloads.get("control/inventory/dev_to_main_promotion_05_result.json", {})
    if result.get("promotion_performed") is not False and result.get("status") == WAITING_STATUS:
        errors.append("waiting promotion result must not perform promotion")
    for field in (
        "deployment_performed",
        "public_launch_performed",
        "production_readiness_claimed",
        "public_launch_readiness_claimed",
        "public_mutation_enabled",
        "public_live_source_fanout_enabled",
        "download_performed",
        "extraction_executed",
        "model_provider_used",
        "site_dist_written",
        "dns_changed",
    ):
        if result.get(field) is not False:
            errors.append(f"promotion result must set {field}=false")


def _validate_docs(root: Path, errors: list[str]) -> None:
    docs = "\n".join(
        (root / rel).read_text(encoding="utf-8").lower()
        for rel in (
            "docs/operations/DEV_TO_MAIN_PROMOTION_REVIEW_05.md",
            "docs/operations/POST_PUBLIC_ALPHA_DEPLOY_DRY_RUN_PROMOTION_PLAN.md",
        )
        if (root / rel).exists()
    )
    for phrase in (
        "waiting",
        "external full discovery",
        "do not promote",
        "public-alpha-launch-00",
    ):
        if phrase not in docs:
            errors.append(f"promotion-05 docs missing required phrase: {phrase}")


def _validate_no_forbidden_changed_paths(root: Path, errors: list[str]) -> None:
    forbidden_prefixes = (
        ".aide.local/",
        "eureka-instance/",
        "instances/",
        "secrets/",
        "site/dist/",
        "site/dist/data/public_index/",
        "data/public_index/",
        "runtime/extraction/",
        "runtime/search_quality/",
        "native/",
        "crates/",
    )
    changed = _git(root, "diff", "--name-only", "HEAD", "--")
    untracked = _git(root, "ls-files", "--others", "--exclude-standard")
    if changed.returncode != 0 or untracked.returncode != 0:
        errors.append("unable to inspect changed files")
        return
    for rel in [*changed.stdout.splitlines(), *untracked.stdout.splitlines()]:
        normalized = rel.replace("\\", "/")
        if normalized.startswith(forbidden_prefixes):
            errors.append(f"forbidden changed path present: {normalized}")


def _read_json(path: Path, rel: str, errors: list[str]) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"invalid JSON in {rel}: {exc}")
    return {}


def _git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=root, text=True, capture_output=True, check=False)


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate DEV-TO-MAIN-PROMOTION-REVIEW-05.")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(list(argv) if argv is not None else None)

    report = validate_dev_to_main_promotion_05()
    output = stdout or sys.stdout
    if args.json:
        output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        output.write(f"dev-to-main promotion 05 validation: {report['status']}\n")
        for error in report["errors"]:
            output.write(f"ERROR: {error}\n")
    return 0 if report["status"] != "invalid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
