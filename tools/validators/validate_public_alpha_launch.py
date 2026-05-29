from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]
WAITING_STATUS = "waiting_for_manual_launch_approval"
APPROVAL_PHRASE = "LAUNCH_READ_ONLY_PUBLIC_ALPHA"

REQUIRED_RESULTS = [
    "control/inventory/dev_to_main_promotion_05_result.json",
    "control/inventory/public_alpha_deploy_dry_run_result.json",
    "control/inventory/public_alpha_launch_candidate_result.json",
    "control/inventory/public_alpha_readonly_closeout_result.json",
    "control/inventory/public_alpha_readonly_00_result.json",
    "control/inventory/public_alpha_hosting_result.json",
    "control/inventory/snapshot_relay_result.json",
    "control/inventory/source_wave_result.json",
    "control/inventory/source_action_kernel_result.json",
]

REQUIRED_LAUNCH_FILES = [
    "control/inventory/public_alpha_launch_input_state.json",
    "control/inventory/public_alpha_launch_branch_state.json",
    "control/inventory/public_alpha_launch_boundary_report.json",
    "control/inventory/public_alpha_launch_validation_matrix.json",
    "control/inventory/public_alpha_launch_result.json",
    "control/inventory/public_alpha_launch_next_task_decision.json",
    "control/audits/public-alpha-launch-00-v0/README.md",
    "control/audits/public-alpha-launch-00-v0/manual_approval_missing.md",
]

APPROVAL_PATHS = [
    "control/approvals/public-alpha-launch-00-approval.json",
    "control/inventory/public_alpha_launch_manual_approval.json",
]

FALSE_BOUNDARY_FIELDS = [
    "deployment_performed",
    "public_launch_performed",
    "production_readiness_claimed",
    "public_launch_readiness_claimed",
    "public_mutation_enabled",
    "public_live_source_fanout_enabled",
    "live_source_call_performed",
    "source_probe_executed",
    "download_performed",
    "upload_performed",
    "extraction_executed",
    "model_provider_used",
    "accounts_enabled_by_default",
    "site_dist_written",
    "dns_changed",
    "hosting_provider_called",
    "credentials_committed",
    "operator_tokens_committed",
    "secrets_committed",
    "committed_instance_state",
    "master_index_mutated",
    "data_public_index_mutated",
    "raw_live_source_response_committed",
    "raw_full_discovery_logs_committed",
]

REQUIRED_ACKNOWLEDGED_BOUNDARIES = {
    "read_only",
    "no_public_mutation",
    "no_live_source_fanout",
    "no_downloads",
    "no_extraction",
    "no_model_provider_calls",
    "alpha_limited_corpus",
    "manual_rollback_required",
}

ALLOWED_DEPLOYMENT_MODES = {
    "static_snapshot_site",
    "read_only_relay_service",
    "local_public_preview",
    "other_explicitly_approved",
}


def validate_public_alpha_launch(root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    payloads: dict[str, dict[str, Any]] = {}

    for rel in REQUIRED_RESULTS + REQUIRED_LAUNCH_FILES:
        path = root / rel
        if not path.exists():
            errors.append(f"missing required file: {rel}")
        elif path.suffix == ".json":
            payloads[rel] = _read_json(path, rel, errors)

    _validate_prior_results(payloads, errors)
    _validate_launch_result(payloads, errors)
    _validate_boundaries(payloads, errors)
    _validate_branch_state(payloads, errors)
    approval = _find_approval(root, errors)
    _validate_approval_state(root, payloads, approval, errors)
    _validate_docs(root, errors)
    _validate_no_forbidden_changed_paths(root, errors)

    result = payloads.get("control/inventory/public_alpha_launch_result.json", {})
    status = "invalid" if errors else str(result.get("status", WAITING_STATUS))
    return {
        "schema_version": "public_alpha_launch_validation.v0",
        "task": "PUBLIC-ALPHA-LAUNCH-00",
        "status": status,
        "manual_approval_verified": bool(result.get("manual_approval_verified")),
        "deployment_performed": bool(result.get("deployment_performed")),
        "public_launch_performed": bool(result.get("public_launch_performed")),
        "production_readiness_claimed": bool(result.get("production_readiness_claimed")),
        "public_launch_readiness_claimed": bool(result.get("public_launch_readiness_claimed")),
        "errors": errors,
    }


def _validate_prior_results(payloads: Mapping[str, dict[str, Any]], errors: list[str]) -> None:
    promotion = payloads.get("control/inventory/dev_to_main_promotion_05_result.json", {})
    if promotion.get("status") != "pass":
        errors.append("promotion-05 result must be pass")
    for field in (
        "promotion_performed",
        "main_pushed",
        "dev_pushed",
        "origin_main_equals_origin_dev",
        "full_unittest_discovery_passed",
    ):
        if promotion.get(field) is not True:
            errors.append(f"promotion-05 result must set {field}=true")

    dry_run = payloads.get("control/inventory/public_alpha_deploy_dry_run_result.json", {})
    if dry_run.get("status") != "pass":
        errors.append("deploy dry-run result must be pass")
    for field in (
        "deploy_dry_run_rehearsal_passed",
        "deploy_smoke_passed",
        "rollback_rehearsal_passed",
        "manual_approval_required_for_launch",
    ):
        if dry_run.get(field) is not True:
            errors.append(f"deploy dry-run result must set {field}=true")

    launch_candidate = payloads.get("control/inventory/public_alpha_launch_candidate_result.json", {})
    if launch_candidate.get("status") != "pass":
        errors.append("launch-candidate result must be pass")
    if launch_candidate.get("hard_blockers_remaining") != 0:
        errors.append("launch-candidate result must have zero hard blockers")
    for field in (
        "launch_candidate_ready",
        "manual_approval_required_for_launch",
        "public_routes_read_only",
        "public_api_read_only",
    ):
        if launch_candidate.get(field) is not True:
            errors.append(f"launch-candidate result must set {field}=true")

    for rel in (
        "control/inventory/public_alpha_readonly_closeout_result.json",
        "control/inventory/public_alpha_readonly_00_result.json",
        "control/inventory/public_alpha_hosting_result.json",
        "control/inventory/snapshot_relay_result.json",
        "control/inventory/source_wave_result.json",
        "control/inventory/source_action_kernel_result.json",
    ):
        status = payloads.get(rel, {}).get("status")
        if status not in {"pass", "pass_with_warnings"}:
            errors.append(f"{rel} must be pass or pass_with_warnings")


def _validate_launch_result(payloads: Mapping[str, dict[str, Any]], errors: list[str]) -> None:
    result = payloads.get("control/inventory/public_alpha_launch_result.json", {})
    if result.get("status") != WAITING_STATUS:
        errors.append(f"launch result must be {WAITING_STATUS} until approval is present")
    for field in (
        "promotion_05_verified",
        "public_alpha_deploy_dry_run_verified",
        "public_alpha_launch_candidate_verified",
        "public_alpha_readonly_verified",
        "public_alpha_hosting_verified",
    ):
        if result.get(field) is not True:
            errors.append(f"launch result must set {field}=true")
    for field in (
        "manual_approval_verified",
        "deployment_target_verified",
        "deployment_command_verified",
        "rollback_command_verified",
        "deployment_performed",
        "public_launch_performed",
        "production_readiness_claimed",
        "public_launch_readiness_claimed",
        "public_mutation_enabled",
        "public_live_source_fanout_enabled",
        "download_performed",
        "extraction_executed",
        "model_provider_used",
    ):
        if result.get(field) is not False:
            errors.append(f"launch result must set {field}=false")


def _validate_boundaries(payloads: Mapping[str, dict[str, Any]], errors: list[str]) -> None:
    boundary = payloads.get("control/inventory/public_alpha_launch_boundary_report.json", {})
    for field in FALSE_BOUNDARY_FIELDS:
        if boundary.get(field) is not False:
            errors.append(f"launch boundary report must set {field}=false")


def _validate_branch_state(payloads: Mapping[str, dict[str, Any]], errors: list[str]) -> None:
    branch = payloads.get("control/inventory/public_alpha_launch_branch_state.json", {})
    if branch.get("launch_baseline_origin_main_equals_origin_dev") is not True:
        errors.append("launch branch state must record baseline main/dev equality")
    if branch.get("dev_ahead_of_main_only_by_waiting_evidence") is not True:
        errors.append("launch branch state must classify dev ahead as waiting evidence only")
    if branch.get("deployment_performed") is not False:
        errors.append("launch branch state must set deployment_performed=false")
    if branch.get("public_launch_performed") is not False:
        errors.append("launch branch state must set public_launch_performed=false")


def _find_approval(root: Path, errors: list[str]) -> dict[str, Any] | None:
    found: dict[str, Any] | None = None
    for rel in APPROVAL_PATHS:
        path = root / rel
        if not path.exists():
            continue
        if found is not None:
            errors.append("only one public alpha launch approval record may be present")
            continue
        found = _read_json(path, rel, errors)
    return found


def _validate_approval_state(
    root: Path,
    payloads: Mapping[str, dict[str, Any]],
    approval: Mapping[str, Any] | None,
    errors: list[str],
) -> None:
    result = payloads.get("control/inventory/public_alpha_launch_result.json", {})
    input_state = payloads.get("control/inventory/public_alpha_launch_input_state.json", {})
    if approval is None:
        if result.get("manual_approval_verified") is not False:
            errors.append("missing approval must leave manual_approval_verified=false")
        if input_state.get("manual_approval_file_present") is not False:
            errors.append("input state must record missing committed approval")
        if input_state.get("task_local_manual_approval_present") is not False:
            errors.append("input state must record missing task-local approval")
        return

    if approval.get("task") != "PUBLIC-ALPHA-LAUNCH-00":
        errors.append("approval task must be PUBLIC-ALPHA-LAUNCH-00")
    if approval.get("approval_phrase") != APPROVAL_PHRASE:
        errors.append(f"approval_phrase must be {APPROVAL_PHRASE}")
    if approval.get("deployment_mode") not in ALLOWED_DEPLOYMENT_MODES:
        errors.append("approval deployment_mode is not allowed")
    if approval.get("target_environment") not in {"staging", "public_alpha"}:
        errors.append("approval target_environment must be staging or public_alpha")
    for field in ("approved_by", "approved_at", "domain_or_url", "deployment_command", "rollback_command", "rollback_contact"):
        if not approval.get(field):
            errors.append(f"approval requires {field}")
    acknowledged = set(approval.get("acknowledged_boundaries", []))
    missing = sorted(REQUIRED_ACKNOWLEDGED_BOUNDARIES - acknowledged)
    if missing:
        errors.append(f"approval missing acknowledged boundaries: {', '.join(missing)}")


def _validate_docs(root: Path, errors: list[str]) -> None:
    text = "\n".join(
        (root / rel).read_text(encoding="utf-8").lower()
        for rel in (
            "control/audits/public-alpha-launch-00-v0/README.md",
            "control/audits/public-alpha-launch-00-v0/manual_approval_missing.md",
        )
        if (root / rel).exists()
    )
    for phrase in (
        "waiting_for_manual_launch_approval",
        "launch_read_only_public_alpha",
        "no deployment",
        "no_live_source_fanout",
    ):
        if phrase not in text:
            errors.append(f"launch audit docs missing required phrase: {phrase}")


def _validate_no_forbidden_changed_paths(root: Path, errors: list[str]) -> None:
    forbidden_prefixes = (
        ".aide.local/",
        "eureka-instance/",
        "instances/",
        "secrets/",
        "data/public_index/",
        "runtime/extraction/",
        "runtime/search_quality/",
        "native/",
        "crates/",
    )
    completed = _git(root, "diff", "--name-only", "HEAD", "--")
    if completed.returncode != 0:
        errors.append("unable to inspect changed files")
        return
    for rel in completed.stdout.splitlines():
        normalized = rel.replace("\\", "/")
        if normalized.startswith(forbidden_prefixes):
            errors.append(f"forbidden changed path present: {normalized}")


def _read_json(path: Path, rel: str, errors: list[str]) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"invalid JSON in {rel}: {exc}")
        return {}
    return payload if isinstance(payload, dict) else {}


def _git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=root, text=True, capture_output=True, check=False)


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate PUBLIC-ALPHA-LAUNCH-00.")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(list(argv) if argv is not None else None)

    report = validate_public_alpha_launch()
    output = stdout or sys.stdout
    if args.json:
        output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        output.write(f"public alpha launch validation: {report['status']}\n")
        for error in report["errors"]:
            output.write(f"ERROR: {error}\n")
    return 0 if report["status"] != "invalid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
