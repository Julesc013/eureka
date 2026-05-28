from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
from typing import Any, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]

PRIOR_RESULTS = {
    "dev_to_main_promotion_04": "control/inventory/dev_to_main_promotion_04_result.json",
    "public_alpha_readonly_closeout": "control/inventory/public_alpha_readonly_closeout_result.json",
    "public_alpha_readonly": "control/inventory/public_alpha_readonly_00_result.json",
    "public_alpha_hosting": "control/inventory/public_alpha_hosting_result.json",
    "snapshot_relay": "control/inventory/snapshot_relay_result.json",
    "source_wave": "control/inventory/source_wave_result.json",
    "source_action_kernel": "control/inventory/source_action_kernel_result.json",
    "source_snapshot_closeout": "control/inventory/source_snapshot_closeout_result.json",
    "ci_full_discovery_harness": "control/inventory/ci_full_discovery_harness_result.json",
}

REQUIRED_CONTRACTS = [
    "contracts/publication/public_alpha_launch_candidate.v0.json",
    "contracts/publication/public_alpha_launch_gate.v0.json",
    "contracts/publication/public_alpha_launch_decision.v0.json",
    "contracts/publication/public_alpha_deploy_dry_run_plan.v0.json",
    "contracts/publication/public_alpha_blocker_register.v0.json",
    "contracts/publication/public_alpha_go_no_go.v0.json",
]

REQUIRED_POLICIES = [
    "control/policies/public_alpha_launch_candidate_policy.json",
    "control/policies/public_alpha_no_deploy_policy.json",
    "control/policies/public_alpha_manual_approval_policy.json",
    "control/policies/public_alpha_launch_non_claim_policy.json",
    "control/policies/public_alpha_public_safety_policy.json",
]

REQUIRED_MATRICES = [
    "control/inventory/public_alpha_launch_candidate_input_state.json",
    "control/inventory/public_alpha_launch_candidate_branch_state.json",
    "control/inventory/public_alpha_launch_candidate_scope_matrix.json",
    "control/inventory/public_alpha_launch_candidate_route_matrix.json",
    "control/inventory/public_alpha_launch_candidate_api_matrix.json",
    "control/inventory/public_alpha_launch_candidate_security_matrix.json",
    "control/inventory/public_alpha_launch_candidate_ops_matrix.json",
    "control/inventory/public_alpha_launch_candidate_blocker_register.json",
    "control/inventory/public_alpha_launch_candidate_go_no_go_matrix.json",
    "control/inventory/public_alpha_launch_candidate_deploy_dry_run_plan.json",
    "control/inventory/public_alpha_launch_candidate_validation_matrix.json",
    "control/inventory/public_alpha_launch_candidate_boundary_report.json",
    "control/inventory/public_alpha_launch_candidate_result.json",
    "control/inventory/public_alpha_launch_candidate_next_task_decision.json",
    "control/inventory/public_alpha_launch_candidate_failure_repair_log.json",
]

REQUIRED_DOCS = [
    "docs/architecture/PUBLIC_ALPHA_LAUNCH_CANDIDATE.md",
    "docs/operations/PUBLIC_ALPHA_LAUNCH_CANDIDATE_RUNBOOK.md",
    "docs/operations/PUBLIC_ALPHA_GO_NO_GO_CHECKLIST.md",
    "docs/operations/PUBLIC_ALPHA_DEPLOY_DRY_RUN_PLAN.md",
    "docs/operations/PUBLIC_ALPHA_MANUAL_APPROVAL_GATE.md",
    "docs/operations/POST_PUBLIC_ALPHA_LAUNCH_CANDIDATE_PLAN.md",
    "docs/reference/PUBLIC_ALPHA_LAUNCH_GATES.md",
    "docs/reference/PUBLIC_ALPHA_BLOCKER_REGISTER.md",
    "release/hosting/public_alpha_launch_candidate.md",
    "release/hosting/public_alpha_deploy_dry_run_plan.md",
    "release/hosting/public_alpha_rollback_checklist.md",
    "release/hosting/public_alpha_environment_checklist.md",
]

REQUIRED_AUDIT_FILES = [
    "control/audits/public-alpha-launch-candidate-00-v0/README.md",
    "control/audits/public-alpha-launch-candidate-00-v0/public_alpha_launch_candidate_report.json",
    "control/audits/public-alpha-launch-candidate-00-v0/scope_matrix.md",
    "control/audits/public-alpha-launch-candidate-00-v0/route_matrix.md",
    "control/audits/public-alpha-launch-candidate-00-v0/api_matrix.md",
    "control/audits/public-alpha-launch-candidate-00-v0/security_matrix.md",
    "control/audits/public-alpha-launch-candidate-00-v0/ops_matrix.md",
    "control/audits/public-alpha-launch-candidate-00-v0/blocker_register.md",
    "control/audits/public-alpha-launch-candidate-00-v0/go_no_go_matrix.md",
    "control/audits/public-alpha-launch-candidate-00-v0/deploy_dry_run_plan.md",
    "control/audits/public-alpha-launch-candidate-00-v0/validation_matrix.md",
    "control/audits/public-alpha-launch-candidate-00-v0/boundary_report.md",
    "control/audits/public-alpha-launch-candidate-00-v0/validation.md",
    "control/audits/public-alpha-launch-candidate-00-v0/generated/sample_launch_candidate.json",
    "control/audits/public-alpha-launch-candidate-00-v0/generated/sample_go_no_go.json",
    "control/audits/public-alpha-launch-candidate-00-v0/generated/sample_blocker_register.json",
    "control/audits/public-alpha-launch-candidate-00-v0/generated/sample_summary.md",
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
    "deployment_performed",
    "production_readiness_claimed",
    "public_launch_readiness_claimed",
    "marketplace_or_app_store_readiness_claimed",
    "full_discovery_run_inside_ai",
    "raw_full_discovery_logs_committed",
]

RESULT_FALSE_FIELDS = [
    "public_mutation_enabled",
    "public_live_source_fanout_enabled",
    "downloads_enabled",
    "extraction_enabled",
    "model_provider_enabled",
    "deployment_performed",
    "production_readiness_claimed",
    "public_launch_readiness_claimed",
]


def validate_public_alpha_launch_candidate(root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    payloads: dict[str, dict[str, Any]] = {}

    json_files = list(PRIOR_RESULTS.values()) + REQUIRED_CONTRACTS + REQUIRED_POLICIES + REQUIRED_MATRICES
    for rel in json_files:
        path = root / rel
        if not path.exists():
            errors.append(f"missing required JSON: {rel}")
        else:
            payloads[rel] = _read_json(path, rel, errors)

    for rel in REQUIRED_DOCS + REQUIRED_AUDIT_FILES:
        if not (root / rel).exists():
            errors.append(f"missing required file: {rel}")

    _validate_branch_state(root, payloads, errors)
    _validate_prior_results(payloads, errors)
    _validate_launch_contracts_and_policies(payloads, errors)
    _validate_route_and_api_matrices(payloads, errors)
    _validate_security_and_ops(payloads, root, errors)
    _validate_blockers_and_result(payloads, errors)
    _validate_boundary_report(payloads, errors)
    _validate_docs(root, errors)
    _validate_no_forbidden_tracked_paths(root, errors)

    result = payloads.get("control/inventory/public_alpha_launch_candidate_result.json", {})
    status = "invalid" if errors else result.get("status", "pass")
    return {
        "schema_version": "public_alpha_launch_candidate_validation.v0",
        "task": "PUBLIC-ALPHA-LAUNCH-CANDIDATE-00",
        "status": status,
        "baseline_commit": result.get("baseline_commit"),
        "public_alpha_readonly_verified": bool(result.get("public_alpha_readonly_verified")),
        "public_alpha_hosting_verified": bool(result.get("public_alpha_hosting_verified")),
        "snapshot_relay_verified": bool(result.get("snapshot_relay_verified")),
        "external_full_discovery_verified": bool(result.get("external_full_discovery_verified")),
        "external_full_discovery_tests_run": int(result.get("external_full_discovery_tests_run") or 0),
        "public_routes_read_only": bool(result.get("public_routes_read_only")),
        "public_api_read_only": bool(result.get("public_api_read_only")),
        "hard_blockers_remaining": int(result.get("hard_blockers_remaining") or 0),
        "launch_warnings_remaining": int(result.get("launch_warnings_remaining") or 0),
        "launch_candidate_ready": bool(result.get("launch_candidate_ready")),
        "manual_approval_required_for_launch": bool(result.get("manual_approval_required_for_launch")),
        "errors": errors,
    }


def _validate_branch_state(root: Path, payloads: dict[str, dict[str, Any]], errors: list[str]) -> None:
    branch = payloads.get("control/inventory/public_alpha_launch_candidate_branch_state.json", {})
    baseline = branch.get("head")
    if branch.get("origin_main_equals_origin_dev") is not True:
        errors.append("recorded branch state must have origin_main_equals_origin_dev=true at promoted baseline")
    if branch.get("active_git_operation") is not False:
        errors.append("recorded branch state must have no active git operation")
    if branch.get("working_tree_clean_before") is not True:
        errors.append("recorded branch state must be clean before launch-candidate gate")
    if branch.get("deployment_performed") is not False:
        errors.append("branch state must not record deployment")
    if baseline:
        ancestor = _git(root, "merge-base", "--is-ancestor", str(baseline), "HEAD")
        if ancestor.returncode != 0:
            errors.append("baseline commit must be an ancestor of current HEAD")


def _validate_prior_results(payloads: dict[str, dict[str, Any]], errors: list[str]) -> None:
    promotion = payloads.get(PRIOR_RESULTS["dev_to_main_promotion_04"], {})
    if promotion.get("status") != "pass":
        errors.append("dev_to_main_promotion_04 must be pass")
    for field in (
        "promotion_performed",
        "origin_main_equals_origin_dev_after",
        "public_alpha_readonly_verified",
        "public_alpha_hosting_verified",
        "public_alpha_readonly_closeout_verified",
        "full_unittest_discovery_passed",
    ):
        if promotion.get(field) is not True:
            errors.append(f"dev_to_main_promotion_04 must set {field}=true")
    if int(promotion.get("full_unittest_discovery_count") or 0) < 5057:
        errors.append("promotion evidence must record external full discovery count >= 5057")
    if promotion.get("full_discovery_failures_remaining") != 0:
        errors.append("promotion evidence must record zero full discovery failures")
    if promotion.get("full_discovery_errors_remaining") != 0:
        errors.append("promotion evidence must record zero full discovery errors")

    closeout = payloads.get(PRIOR_RESULTS["public_alpha_readonly_closeout"], {})
    if closeout.get("status") not in {"pass", "pass_with_warnings"}:
        errors.append("public alpha readonly closeout must be pass or pass_with_warnings")
    for field in (
        "public_alpha_readonly_verified",
        "public_alpha_hosting_verified",
        "snapshot_relay_verified",
        "focused_validators_passed",
        "external_full_discovery_summary_received",
        "full_unittest_discovery_passed",
    ):
        if closeout.get(field) is not True:
            errors.append(f"public alpha closeout must set {field}=true")

    readonly = payloads.get(PRIOR_RESULTS["public_alpha_readonly"], {})
    if readonly.get("status") != "pass":
        errors.append("public alpha readonly result must be pass")
    for field in ("read_only", "snapshot_backed", "relay_backed", "reviewed_index_only"):
        if readonly.get(field) is not True:
            errors.append(f"public alpha readonly must set {field}=true")

    hosting = payloads.get(PRIOR_RESULTS["public_alpha_hosting"], {})
    if hosting.get("status") != "pass":
        errors.append("public alpha hosting result must be pass")
    for field in (
        "security_model_added",
        "rate_limit_model_added",
        "observability_model_added",
        "privacy_abuse_docs_added",
        "rollback_plan_added",
    ):
        if hosting.get(field) is not True:
            errors.append(f"hosting readiness must set {field}=true")

    for key in ("snapshot_relay", "source_wave", "source_action_kernel", "ci_full_discovery_harness"):
        status = payloads.get(PRIOR_RESULTS[key], {}).get("status")
        if status not in {"pass", "pass_with_warnings"}:
            errors.append(f"{key} result must be pass or pass_with_warnings")


def _validate_launch_contracts_and_policies(payloads: dict[str, dict[str, Any]], errors: list[str]) -> None:
    for rel in REQUIRED_POLICIES:
        policy = payloads.get(rel, {})
        for field in (
            "deployment_performed",
            "public_mutation_enabled",
            "public_live_source_fanout_enabled",
            "downloads_enabled",
            "extraction_enabled",
            "model_provider_enabled",
        ):
            if field in policy and policy.get(field) is not False:
                errors.append(f"{rel} must set {field}=false")
        if policy.get("manual_approval_required_for_launch") is False:
            errors.append(f"{rel} must require manual approval for launch")

    for rel in REQUIRED_CONTRACTS:
        contract = payloads.get(rel, {})
        properties = contract.get("properties", {})
        for field in ("deployment_performed", "production_readiness_claimed", "public_launch_readiness_claimed"):
            if field not in properties:
                errors.append(f"{rel} must define {field}")


def _validate_route_and_api_matrices(payloads: dict[str, dict[str, Any]], errors: list[str]) -> None:
    route_matrix = payloads.get("control/inventory/public_alpha_launch_candidate_route_matrix.json", {})
    routes = route_matrix.get("routes", [])
    if len(routes) < 6:
        errors.append("launch-candidate route matrix must include public web routes")
    for route in routes:
        for field in ("read_only", "snapshot_backed", "relay_backed"):
            if route.get(field) is not True:
                errors.append(f"route {route.get('route')} must set {field}=true")
        for field in ("public_mutation_enabled", "live_source_fanout_enabled"):
            if route.get(field) is not False:
                errors.append(f"route {route.get('route')} must set {field}=false")

    api_matrix = payloads.get("control/inventory/public_alpha_launch_candidate_api_matrix.json", {})
    if api_matrix.get("public_api_read_only") is not True:
        errors.append("api matrix must set public_api_read_only=true")
    if api_matrix.get("read_only_methods") != ["GET", "HEAD"]:
        errors.append("api matrix read_only_methods must be GET and HEAD")
    for field in (
        "public_write_actions_enabled",
        "public_mutation_enabled",
        "public_live_source_fanout_enabled",
        "download_enabled",
        "upload_enabled",
        "extraction_enabled",
        "model_provider_enabled",
        "accounts_enabled",
        "deployment_performed",
    ):
        if api_matrix.get(field) is not False:
            errors.append(f"api matrix must set {field}=false")


def _validate_security_and_ops(payloads: dict[str, dict[str, Any]], root: Path, errors: list[str]) -> None:
    security = payloads.get("control/inventory/public_alpha_launch_candidate_security_matrix.json", {})
    for field in (
        "security_model_exists",
        "security_headers_contract_exists",
        "csp_baseline_exists",
        "rate_limit_model_exists",
        "observability_model_exists",
        "privacy_notice_exists",
        "abuse_takedown_process_exists",
        "rollback_plan_exists",
        "manual_approval_gate_exists",
    ):
        if security.get(field) is not True:
            errors.append(f"security matrix must set {field}=true")
    for field in (
        "credentials_in_repo_allowed",
        "inline_secrets_allowed",
        "public_mutation_enabled",
        "public_live_source_fanout_enabled",
        "downloads_enabled",
        "extraction_enabled",
        "model_provider_enabled",
    ):
        if security.get(field) is not False:
            errors.append(f"security matrix must set {field}=false")

    ops = payloads.get("control/inventory/public_alpha_launch_candidate_ops_matrix.json", {})
    for field in (
        "health_check_defined",
        "smoke_check_defined",
        "rollback_check_defined",
        "environment_checklist_defined",
        "observability_plan_defined",
        "manual_approval_required_before_deploy",
    ):
        if ops.get(field) is not True:
            errors.append(f"ops matrix must set {field}=true")
    for field in ("deployment_performed", "public_launch_performed", "production_readiness_claimed", "public_launch_readiness_claimed"):
        if ops.get(field) is not False:
            errors.append(f"ops matrix must set {field}=false")

    required_plan_files = [
        "docs/operations/PUBLIC_ALPHA_DEPLOY_DRY_RUN_PLAN.md",
        "docs/operations/PUBLIC_ALPHA_MANUAL_APPROVAL_GATE.md",
        "release/hosting/public_alpha_rollback_checklist.md",
        "release/hosting/public_alpha_environment_checklist.md",
    ]
    for rel in required_plan_files:
        if not (root / rel).exists():
            errors.append(f"missing launch operations plan file: {rel}")


def _validate_blockers_and_result(payloads: dict[str, dict[str, Any]], errors: list[str]) -> None:
    blockers = payloads.get("control/inventory/public_alpha_launch_candidate_blocker_register.json", {})
    if blockers.get("hard_blockers_remaining") != 0:
        errors.append("blocker register must have zero hard blockers")
    if blockers.get("launch_warnings_remaining") != 0:
        errors.append("blocker register must have zero launch warnings")
    for item in blockers.get("register", []):
        if item.get("classification") == "hard_blocker" and item.get("active") is not False:
            errors.append(f"hard blocker must be inactive: {item.get('id')}")

    dry_run = payloads.get("control/inventory/public_alpha_launch_candidate_deploy_dry_run_plan.json", {})
    if dry_run.get("dry_run_id") != "PUBLIC-ALPHA-DEPLOY-DRY-RUN-00":
        errors.append("deploy dry-run plan must target PUBLIC-ALPHA-DEPLOY-DRY-RUN-00")
    if dry_run.get("manual_approval_required") is not True:
        errors.append("deploy dry-run plan must require manual approval")

    result = payloads.get("control/inventory/public_alpha_launch_candidate_result.json", {})
    if result.get("status") not in {"pass", "pass_with_warnings"}:
        errors.append("launch-candidate result must be pass or pass_with_warnings")
    for field in (
        "public_alpha_readonly_verified",
        "public_alpha_hosting_verified",
        "snapshot_relay_verified",
        "external_full_discovery_verified",
        "public_routes_read_only",
        "public_api_read_only",
        "manual_approval_required_for_launch",
        "launch_candidate_ready",
    ):
        if result.get(field) is not True:
            errors.append(f"launch-candidate result must set {field}=true")
    for field in RESULT_FALSE_FIELDS:
        if result.get(field) is not False:
            errors.append(f"launch-candidate result must set {field}=false")
    if result.get("hard_blockers_remaining") != 0:
        errors.append("launch-candidate result must have zero hard blockers")
    if result.get("launch_warnings_remaining") != 0:
        errors.append("launch-candidate result must have zero launch warnings")
    if not str(result.get("recommended_next_task", "")).startswith("PUBLIC-ALPHA-DEPLOY-DRY-RUN-00"):
        errors.append("launch-candidate result must recommend PUBLIC-ALPHA-DEPLOY-DRY-RUN-00")


def _validate_boundary_report(payloads: dict[str, dict[str, Any]], errors: list[str]) -> None:
    boundary = payloads.get("control/inventory/public_alpha_launch_candidate_boundary_report.json", {})
    for field in BOUNDARY_FALSE_FIELDS:
        if boundary.get(field) is not False:
            errors.append(f"boundary report must set {field}=false")


def _validate_docs(root: Path, errors: list[str]) -> None:
    docs = "\n".join(
        (root / rel).read_text(encoding="utf-8").lower()
        for rel in REQUIRED_DOCS
        if (root / rel).exists()
    )
    for phrase in (
        "not a launch",
        "not a deployment",
        "manual approval",
        "read-only",
        "no live source fanout",
        "no deployment",
    ):
        if phrase not in docs:
            errors.append(f"launch-candidate docs missing required phrase: {phrase}")


def _validate_no_forbidden_tracked_paths(root: Path, errors: list[str]) -> None:
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
        if normalized.startswith("../eureka-test-runs/"):
            errors.append(f"external test run path must not be changed: {normalized}")


def _read_json(path: Path, rel: str, errors: list[str]) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"invalid JSON in {rel}: {exc}")
    return {}


def _git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate PUBLIC-ALPHA-LAUNCH-CANDIDATE-00.")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(list(argv) if argv is not None else None)

    report = validate_public_alpha_launch_candidate()
    output = stdout or sys.stdout
    if args.json:
        output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        output.write(f"public alpha launch candidate validation: {report['status']}\n")
        for error in report["errors"]:
            output.write(f"ERROR: {error}\n")
    return 0 if report["status"] != "invalid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
