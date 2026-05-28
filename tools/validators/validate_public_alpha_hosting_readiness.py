from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]

REQUIRED_CONTRACTS = [
    "contracts/publication/public_alpha_hosting_plan.v0.json",
    "contracts/publication/public_alpha_environment.v0.json",
    "contracts/publication/public_alpha_security_headers.v0.json",
    "contracts/publication/public_alpha_rate_limit_policy.v0.json",
    "contracts/publication/public_alpha_observability.v0.json",
    "contracts/publication/public_alpha_rollback_plan.v0.json",
    "contracts/publication/public_alpha_abuse_policy.v0.json",
    "contracts/publication/public_alpha_privacy_notice.v0.json",
    "contracts/publication/public_alpha_launch_gate.v0.json",
]

REQUIRED_POLICIES = [
    "control/policies/public_alpha_hosting_policy.json",
    "control/policies/public_alpha_no_deploy_policy.json",
    "control/policies/public_alpha_security_policy.json",
    "control/policies/public_alpha_rate_limit_policy.json",
    "control/policies/public_alpha_observability_policy.json",
    "control/policies/public_alpha_abuse_policy.json",
    "control/policies/public_alpha_non_claim_policy.json",
]

REQUIRED_MATRICES = [
    "control/inventory/public_alpha_hosting_input_state.json",
    "control/inventory/public_alpha_hosting_route_matrix.json",
    "control/inventory/public_alpha_hosting_api_matrix.json",
    "control/inventory/public_alpha_hosting_security_matrix.json",
    "control/inventory/public_alpha_hosting_rate_limit_matrix.json",
    "control/inventory/public_alpha_hosting_observability_matrix.json",
    "control/inventory/public_alpha_hosting_privacy_abuse_matrix.json",
    "control/inventory/public_alpha_hosting_rollback_matrix.json",
    "control/inventory/public_alpha_hosting_environment_matrix.json",
    "control/inventory/public_alpha_hosting_validation_matrix.json",
    "control/inventory/public_alpha_hosting_boundary_report.json",
    "control/inventory/public_alpha_hosting_result.json",
    "control/inventory/public_alpha_hosting_next_task_decision.json",
]

REQUIRED_DOCS = [
    "docs/architecture/PUBLIC_ALPHA_HOSTING.md",
    "docs/architecture/PUBLIC_ALPHA_SECURITY_MODEL.md",
    "docs/operations/PUBLIC_ALPHA_HOSTING_RUNBOOK.md",
    "docs/operations/PUBLIC_ALPHA_ROLLBACK_RUNBOOK.md",
    "docs/operations/PUBLIC_ALPHA_ABUSE_AND_TAKEDOWN.md",
    "docs/operations/POST_PUBLIC_ALPHA_HOSTING_PLAN.md",
    "docs/reference/PUBLIC_ALPHA_ENVIRONMENT.md",
    "docs/reference/PUBLIC_ALPHA_LAUNCH_GATES.md",
]

REQUIRED_AUDIT_FILES = [
    "control/audits/public-alpha-hosting-readiness-00-v0/README.md",
    "control/audits/public-alpha-hosting-readiness-00-v0/public_alpha_hosting_readiness_report.json",
    "control/audits/public-alpha-hosting-readiness-00-v0/hosting_modes.md",
    "control/audits/public-alpha-hosting-readiness-00-v0/security_model.md",
    "control/audits/public-alpha-hosting-readiness-00-v0/operations_model.md",
    "control/audits/public-alpha-hosting-readiness-00-v0/launch_gates.md",
    "control/audits/public-alpha-hosting-readiness-00-v0/validation.md",
    "control/audits/public-alpha-hosting-readiness-00-v0/generated/sample_summary.md",
]

HOSTING_MODES = {
    "static_snapshot_site",
    "read_only_relay_service",
    "local_preview_server",
    "future_dynamic_gateway",
}

BOUNDARY_FALSE_FIELDS = [
    "deployment_performed",
    "production_readiness_claimed",
    "public_launch_readiness_claimed",
    "live_source_call_performed",
    "source_probe_executed",
    "download_performed",
    "upload_performed",
    "extraction_executed",
    "model_provider_used",
    "public_mutation_enabled",
    "accounts_enabled",
    "master_index_mutated",
    "data_public_index_mutated",
    "site_dist_mutated",
    "committed_instance_state",
    "operator_tokens_committed",
    "secrets_committed",
    "raw_logs_committed",
    "raw_live_source_response_committed",
    "force_push_performed",
    "rebase_performed",
    "history_rewrite_performed",
    "branch_deleted",
]


def validate_public_alpha_hosting_readiness() -> dict[str, Any]:
    errors: list[str] = []

    for rel in REQUIRED_CONTRACTS + REQUIRED_POLICIES + REQUIRED_MATRICES + REQUIRED_DOCS + REQUIRED_AUDIT_FILES:
        if not (REPO_ROOT / rel).exists():
            errors.append(f"missing required file: {rel}")

    json_payloads: dict[str, dict[str, Any]] = {}
    for rel in REQUIRED_CONTRACTS + REQUIRED_POLICIES + REQUIRED_MATRICES:
        if (REPO_ROOT / rel).exists():
            json_payloads[rel] = _read_json(rel, errors)

    readonly = _read_json("control/inventory/public_alpha_readonly_00_result.json", errors)
    if readonly.get("status") != "pass":
        errors.append("public alpha read-only result must be pass")
    for key in ("snapshot_backed", "relay_backed", "reviewed_index_only", "read_only"):
        if readonly.get(key) is not True:
            errors.append(f"public alpha read-only result must set {key}=true")
    for key in (
        "deployment_performed",
        "production_readiness_claimed",
        "public_launch_readiness_claimed",
        "live_source_call_performed",
        "download_performed",
        "extraction_executed",
        "model_provider_used",
    ):
        if readonly.get(key) is not False:
            errors.append(f"public alpha read-only result must set {key}=false")

    snapshot = _read_json("control/inventory/snapshot_relay_result.json", errors)
    if snapshot.get("status") not in {"pass", "pass_with_warnings"}:
        errors.append("snapshot relay result must be pass or pass_with_warnings")
    if snapshot.get("public_projection_read_only") is not True:
        errors.append("snapshot relay result must keep public_projection_read_only=true")

    result = json_payloads.get("control/inventory/public_alpha_hosting_result.json", {})
    if result.get("status") != "pass":
        errors.append("hosting result status must be pass")
    if result.get("contracts_added") != len(REQUIRED_CONTRACTS):
        errors.append("hosting result contracts_added must match required contracts")
    if result.get("policies_added") != len(REQUIRED_POLICIES):
        errors.append("hosting result policies_added must match required policies")
    if set(result.get("hosting_modes_defined", [])) != HOSTING_MODES:
        errors.append("hosting result must define all required hosting modes")
    if result.get("recommended_next_task") != "PUBLIC-ALPHA-READONLY-CLOSEOUT-01":
        errors.append("recommended next task must be PUBLIC-ALPHA-READONLY-CLOSEOUT-01")

    boundary = json_payloads.get("control/inventory/public_alpha_hosting_boundary_report.json", {})
    for field in BOUNDARY_FALSE_FIELDS:
        if boundary.get(field) is not False:
            errors.append(f"boundary report must set {field}=false")

    launch_gate = _read_json("contracts/publication/public_alpha_launch_gate.v0.json", errors)
    launch_props = launch_gate.get("properties", {})
    if launch_props.get("launch_allowed_current", {}).get("const") is not False:
        errors.append("launch gate contract must keep launch_allowed_current=false")
    if launch_props.get("deployment_approval_required", {}).get("const") is not True:
        errors.append("launch gate contract must require deployment approval")
    if launch_props.get("external_full_discovery_required", {}).get("const") is not True:
        errors.append("launch gate contract must require external full discovery")

    no_deploy = _read_json("control/policies/public_alpha_no_deploy_policy.json", errors)
    if no_deploy.get("deployment_allowed_current") is not False:
        errors.append("no-deploy policy must keep deployment_allowed_current=false")
    if no_deploy.get("requires_future_operator_approval") is not True:
        errors.append("no-deploy policy must require future operator approval")

    api_matrix = json_payloads.get("control/inventory/public_alpha_hosting_api_matrix.json", {})
    if api_matrix.get("public_write_actions_enabled") is not False:
        errors.append("api matrix must keep public_write_actions_enabled=false")
    if api_matrix.get("live_source_fanout_enabled") is not False:
        errors.append("api matrix must keep live_source_fanout_enabled=false")
    for route in readonly.get("public_api_routes_added", []):
        if route not in api_matrix.get("api_routes", []):
            errors.append(f"api matrix missing route from read-only result: {route}")

    route_matrix = json_payloads.get("control/inventory/public_alpha_hosting_route_matrix.json", {})
    for route in readonly.get("public_web_routes_added", []):
        if route not in [item.get("route") for item in route_matrix.get("web_routes", [])]:
            errors.append(f"route matrix missing route from read-only result: {route}")

    _validate_route_sources(errors)
    _validate_docs(errors)
    _validate_no_private_root(errors)

    return {
        "schema_version": "public_alpha_hosting_readiness_validation.v0",
        "task": "PUBLIC-ALPHA-HOSTING-READINESS-00",
        "status": "valid" if not errors else "invalid",
        "contracts_checked": len(REQUIRED_CONTRACTS),
        "policies_checked": len(REQUIRED_POLICIES),
        "matrices_checked": len(REQUIRED_MATRICES),
        "docs_checked": len(REQUIRED_DOCS),
        "audit_files_checked": len(REQUIRED_AUDIT_FILES),
        "hosting_modes_defined": sorted(HOSTING_MODES),
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
        "public_mutation_enabled": False,
        "live_source_fanout_enabled": False,
        "errors": errors,
    }


def _read_json(rel: str, errors: list[str]) -> dict[str, Any]:
    path = REPO_ROOT / rel
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"missing required JSON: {rel}")
    except json.JSONDecodeError as exc:
        errors.append(f"invalid JSON in {rel}: {exc}")
    return {}


def _validate_route_sources(errors: list[str]) -> None:
    api_routes = (REPO_ROOT / "surfaces/web/server/api_routes.py").read_text(encoding="utf-8")
    web_routes = (REPO_ROOT / "surfaces/web/server/workbench_server.py").read_text(encoding="utf-8")
    for route in (
        "/api/v1/alpha/status",
        "/api/v1/alpha/search",
        "/api/v1/alpha/object/",
        "/api/v1/alpha/source/",
        "/api/v1/alpha/evidence/",
        "/api/v1/alpha/absence/",
        "/api/v1/alpha/needs",
    ):
        if route not in api_routes:
            errors.append(f"api route source missing {route}")
    for route in ("/alpha", "/alpha/object", "/alpha/source", "/alpha/evidence", "/alpha/absence", "/alpha/needs"):
        if route not in web_routes:
            errors.append(f"web route source missing {route}")


def _validate_docs(errors: list[str]) -> None:
    docs_text = "\n".join(
        (REPO_ROOT / rel).read_text(encoding="utf-8").lower()
        for rel in REQUIRED_DOCS
        if (REPO_ROOT / rel).exists()
    )
    required_phrases = [
        "no deployment",
        "production readiness",
        "public launch readiness",
        "live source fanout",
        "rate limits",
        "security headers",
        "rollback",
        "abuse",
        "takedown",
        "privacy",
    ]
    for phrase in required_phrases:
        if phrase not in docs_text:
            errors.append(f"docs missing required phrase: {phrase}")


def _validate_no_private_root(errors: list[str]) -> None:
    if (REPO_ROOT / ".aide.local").exists():
        errors.append(".aide.local must not exist in the repo root")


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate PUBLIC-ALPHA-HOSTING-READINESS-00.")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(list(argv) if argv is not None else None)

    report = validate_public_alpha_hosting_readiness()
    output = stdout or sys.stdout
    if args.json:
        output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        output.write(f"public alpha hosting readiness validation: {report['status']}\n")
        for error in report["errors"]:
            output.write(f"ERROR: {error}\n")
    return 0 if report["status"] == "valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
