from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
from typing import Any, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]

REQUIRED_PRIOR_RESULTS = [
    "control/inventory/public_alpha_launch_candidate_result.json",
    "control/inventory/public_alpha_readonly_00_result.json",
    "control/inventory/public_alpha_hosting_result.json",
    "control/inventory/public_alpha_readonly_closeout_result.json",
]

REQUIRED_CONTRACTS = [
    "contracts/publication/public_alpha_deploy_dry_run.v0.json",
    "contracts/publication/public_alpha_deploy_manifest.v0.json",
    "contracts/publication/public_alpha_environment_checklist.v0.json",
    "contracts/publication/public_alpha_smoke_check.v0.json",
    "contracts/publication/public_alpha_rollback_rehearsal.v0.json",
    "contracts/publication/public_alpha_deploy_dry_run_gate.v0.json",
]

REQUIRED_POLICIES = [
    "control/policies/public_alpha_deploy_dry_run_policy.json",
    "control/policies/public_alpha_dry_run_no_deploy_policy.json",
    "control/policies/public_alpha_deploy_smoke_policy.json",
    "control/policies/public_alpha_rollback_rehearsal_policy.json",
    "control/policies/public_alpha_no_deploy_policy.json",
    "control/policies/public_alpha_manual_approval_policy.json",
]

REQUIRED_INVENTORY = [
    "control/inventory/public_alpha_deploy_dry_run_input_state.json",
    "control/inventory/public_alpha_deploy_dry_run_branch_state.json",
    "control/inventory/public_alpha_deploy_dry_run_launch_candidate_matrix.json",
    "control/inventory/public_alpha_deploy_dry_run_manifest.json",
    "control/inventory/public_alpha_deploy_dry_run_environment_checklist.json",
    "control/inventory/public_alpha_deploy_dry_run_smoke_checklist.json",
    "control/inventory/public_alpha_deploy_dry_run_rollback_rehearsal.json",
    "control/inventory/public_alpha_deploy_dry_run_security_headers_matrix.json",
    "control/inventory/public_alpha_deploy_dry_run_validation_matrix.json",
    "control/inventory/public_alpha_deploy_dry_run_boundary_report.json",
    "control/inventory/public_alpha_deploy_dry_run_result.json",
    "control/inventory/public_alpha_deploy_dry_run_next_task_decision.json",
    "control/inventory/public_alpha_deploy_dry_run_failure_repair_log.json",
]

REQUIRED_DOCS = [
    "docs/operations/PUBLIC_ALPHA_DEPLOY_DRY_RUN_RUNBOOK.md",
    "docs/operations/PUBLIC_ALPHA_DEPLOY_MANIFEST.md",
    "docs/operations/PUBLIC_ALPHA_DEPLOY_SMOKE_CHECKS.md",
    "docs/operations/PUBLIC_ALPHA_DEPLOY_ROLLBACK_REHEARSAL.md",
    "docs/operations/POST_PUBLIC_ALPHA_DEPLOY_DRY_RUN_PLAN.md",
    "docs/reference/PUBLIC_ALPHA_DEPLOY_DRY_RUN_GATES.md",
    "release/hosting/public_alpha_deploy_dry_run_report.md",
    "release/hosting/public_alpha_dry_run_smoke_checklist.md",
    "release/hosting/public_alpha_dry_run_rollback_rehearsal.md",
    "release/hosting/public_alpha_dry_run_environment.md",
]

REQUIRED_AUDIT_FILES = [
    "control/audits/public-alpha-deploy-dry-run-00-v0/README.md",
    "control/audits/public-alpha-deploy-dry-run-00-v0/public_alpha_deploy_dry_run_report.json",
    "control/audits/public-alpha-deploy-dry-run-00-v0/launch_candidate_matrix.md",
    "control/audits/public-alpha-deploy-dry-run-00-v0/deploy_manifest.md",
    "control/audits/public-alpha-deploy-dry-run-00-v0/environment_checklist.md",
    "control/audits/public-alpha-deploy-dry-run-00-v0/smoke_checklist.md",
    "control/audits/public-alpha-deploy-dry-run-00-v0/rollback_rehearsal.md",
    "control/audits/public-alpha-deploy-dry-run-00-v0/boundary_report.md",
    "control/audits/public-alpha-deploy-dry-run-00-v0/validation_matrix.md",
    "control/audits/public-alpha-deploy-dry-run-00-v0/next_task_decision.md",
    "control/audits/public-alpha-deploy-dry-run-00-v0/validation.md",
    "control/audits/public-alpha-deploy-dry-run-00-v0/generated/sample_deploy_manifest.json",
    "control/audits/public-alpha-deploy-dry-run-00-v0/generated/sample_smoke_check.json",
    "control/audits/public-alpha-deploy-dry-run-00-v0/generated/sample_rollback_rehearsal.json",
    "control/audits/public-alpha-deploy-dry-run-00-v0/generated/sample_summary.md",
]

FALSE_BOUNDARY_FIELDS = [
    "deployment_performed",
    "public_launch_performed",
    "production_readiness_claimed",
    "public_launch_readiness_claimed",
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
    "hosting_provider_mutated",
    "master_index_mutated",
    "committed_data_public_index_mutated",
    "committed_instance_state",
    "raw_live_source_response_committed",
    "raw_full_discovery_logs_committed",
    "secrets_committed",
    "operator_tokens_committed",
    "full_discovery_run_inside_ai",
]


def validate_public_alpha_deploy_dry_run(root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    payloads: dict[str, dict[str, Any]] = {}

    for rel in REQUIRED_PRIOR_RESULTS + REQUIRED_CONTRACTS + REQUIRED_POLICIES + REQUIRED_INVENTORY:
        path = root / rel
        if not path.exists():
            errors.append(f"missing required JSON: {rel}")
        else:
            payloads[rel] = _read_json(path, rel, errors)

    for rel in REQUIRED_DOCS + REQUIRED_AUDIT_FILES:
        if not (root / rel).exists():
            errors.append(f"missing required file: {rel}")

    _validate_prior_launch_candidate(payloads, errors)
    _validate_manifest(payloads, errors)
    _validate_environment_smoke_and_rollback(payloads, errors)
    _validate_policies(payloads, errors)
    _validate_boundaries(payloads, errors)
    _validate_result(payloads, errors)
    _validate_docs(root, errors)
    _validate_no_forbidden_changed_paths(root, errors)

    result = payloads.get("control/inventory/public_alpha_deploy_dry_run_result.json", {})
    status = "invalid" if errors else result.get("status", "pass")
    return {
        "schema_version": "public_alpha_deploy_dry_run_validation.v0",
        "task": "PUBLIC-ALPHA-DEPLOY-DRY-RUN-00",
        "status": status,
        "deploy_dry_run_rehearsal_passed": bool(result.get("deploy_dry_run_rehearsal_passed")),
        "deploy_smoke_passed": bool(result.get("deploy_smoke_passed")),
        "rollback_rehearsal_passed": bool(result.get("rollback_rehearsal_passed")),
        "deployment_performed": bool(result.get("deployment_performed")),
        "public_launch_performed": bool(result.get("public_launch_performed")),
        "production_readiness_claimed": bool(result.get("production_readiness_claimed")),
        "public_launch_readiness_claimed": bool(result.get("public_launch_readiness_claimed")),
        "errors": errors,
    }


def _validate_prior_launch_candidate(payloads: dict[str, dict[str, Any]], errors: list[str]) -> None:
    launch = payloads.get("control/inventory/public_alpha_launch_candidate_result.json", {})
    if launch.get("status") != "pass":
        errors.append("launch-candidate result must be pass")
    for field in (
        "launch_candidate_ready",
        "public_alpha_readonly_verified",
        "public_alpha_hosting_verified",
        "external_full_discovery_verified",
        "public_routes_read_only",
        "public_api_read_only",
    ):
        if launch.get(field) is not True:
            errors.append(f"launch-candidate result must set {field}=true")
    for field in (
        "deployment_performed",
        "production_readiness_claimed",
        "public_launch_readiness_claimed",
        "public_mutation_enabled",
        "public_live_source_fanout_enabled",
        "downloads_enabled",
        "extraction_enabled",
        "model_provider_enabled",
    ):
        if launch.get(field) is not False:
            errors.append(f"launch-candidate result must set {field}=false")


def _validate_manifest(payloads: dict[str, dict[str, Any]], errors: list[str]) -> None:
    manifest = payloads.get("control/inventory/public_alpha_deploy_dry_run_manifest.json", {})
    if manifest.get("hosting_mode") not in {"static_snapshot_site", "read_only_relay_service", "local_preview_server"}:
        errors.append("deploy manifest must use an allowed hosting mode")
    if not manifest.get("inputs"):
        errors.append("deploy manifest must record inputs")
    if not manifest.get("outputs"):
        errors.append("deploy manifest must record outputs")
    for field in (
        "site_dist_write_planned",
        "site_dist_written",
        "deployment_performed",
        "public_launch_performed",
        "provider_credentials_required",
        "dns_change_required",
        "public_mutation_enabled",
        "public_live_source_fanout_enabled",
    ):
        if manifest.get(field) is not False:
            errors.append(f"deploy manifest must set {field}=false")


def _validate_environment_smoke_and_rollback(payloads: dict[str, dict[str, Any]], errors: list[str]) -> None:
    environment = payloads.get("control/inventory/public_alpha_deploy_dry_run_environment_checklist.json", {})
    if len(environment.get("checks", [])) < 5:
        errors.append("environment checklist must include dry-run checks")
    for field in ("credentials_committed", "provider_credentials_required", "deployment_performed", "public_launch_performed", "dns_changed"):
        if environment.get(field) is not False:
            errors.append(f"environment checklist must set {field}=false")

    smoke = payloads.get("control/inventory/public_alpha_deploy_dry_run_smoke_checklist.json", {})
    if smoke.get("deploy_smoke_passed") is not True:
        errors.append("smoke checklist must pass")
    if len(smoke.get("checks", [])) < 6:
        errors.append("smoke checklist must include route and disabled-capability checks")
    for field in ("live_http_used", "deployment_performed", "public_launch_performed"):
        if smoke.get(field) is not False:
            errors.append(f"smoke checklist must set {field}=false")

    rollback = payloads.get("control/inventory/public_alpha_deploy_dry_run_rollback_rehearsal.json", {})
    if rollback.get("rollback_rehearsal_passed") is not True:
        errors.append("rollback rehearsal must pass")
    if len(rollback.get("steps", [])) < 5:
        errors.append("rollback rehearsal must include plan steps")
    for field in ("deployment_performed", "public_launch_performed", "public_mutation_state_created"):
        if rollback.get(field) is not False:
            errors.append(f"rollback rehearsal must set {field}=false")


def _validate_policies(payloads: dict[str, dict[str, Any]], errors: list[str]) -> None:
    for rel in REQUIRED_POLICIES:
        policy = payloads.get(rel, {})
        for field in (
            "deployment_performed",
            "public_launch_performed",
            "public_mutation_enabled",
            "public_live_source_fanout_enabled",
            "downloads_enabled",
            "extraction_enabled",
            "model_provider_enabled",
        ):
            if field in policy and policy.get(field) is not False:
                errors.append(f"{rel} must set {field}=false")
        if policy.get("dry_run_only") is False:
            errors.append(f"{rel} must not disable dry_run_only")


def _validate_boundaries(payloads: dict[str, dict[str, Any]], errors: list[str]) -> None:
    boundary = payloads.get("control/inventory/public_alpha_deploy_dry_run_boundary_report.json", {})
    for field in FALSE_BOUNDARY_FIELDS:
        if boundary.get(field) is not False:
            errors.append(f"boundary report must set {field}=false")


def _validate_result(payloads: dict[str, dict[str, Any]], errors: list[str]) -> None:
    result = payloads.get("control/inventory/public_alpha_deploy_dry_run_result.json", {})
    if result.get("status") != "pass":
        errors.append("dry-run result must be pass")
    for field in (
        "launch_candidate_verified",
        "deploy_manifest_verified",
        "environment_checklist_verified",
        "deploy_smoke_passed",
        "rollback_rehearsal_passed",
        "deploy_dry_run_rehearsal_passed",
        "focused_validators_passed",
        "manual_approval_required_for_deploy",
        "manual_approval_required_for_launch",
    ):
        if result.get(field) is not True:
            errors.append(f"dry-run result must set {field}=true")
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
        if result.get(field) is not False:
            errors.append(f"dry-run result must set {field}=false")
    if not str(result.get("recommended_next_task", "")).startswith("DEV-TO-MAIN-PROMOTION-REVIEW-05"):
        errors.append("dry-run result must recommend DEV-TO-MAIN-PROMOTION-REVIEW-05")


def _validate_docs(root: Path, errors: list[str]) -> None:
    docs = "\n".join(
        (root / rel).read_text(encoding="utf-8").lower()
        for rel in REQUIRED_DOCS
        if (root / rel).exists()
    )
    for phrase in (
        "without deploying",
        "no deployment",
        "no live source fanout",
        "manual approval",
        "dev-to-main-promotion-review-05",
    ):
        if phrase not in docs:
            errors.append(f"dry-run docs missing required phrase: {phrase}")


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
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"invalid JSON in {rel}: {exc}")
    return {}


def _git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=root, text=True, capture_output=True, check=False)


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate PUBLIC-ALPHA-DEPLOY-DRY-RUN-00.")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(list(argv) if argv is not None else None)

    report = validate_public_alpha_deploy_dry_run()
    output = stdout or sys.stdout
    if args.json:
        output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        output.write(f"public alpha deploy dry-run validation: {report['status']}\n")
        for error in report["errors"]:
            output.write(f"ERROR: {error}\n")
    return 0 if report["status"] != "invalid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
