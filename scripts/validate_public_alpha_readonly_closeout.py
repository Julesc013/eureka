from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
WAITING_STATUS = "waiting_for_external_full_discovery"

PRIOR_RESULTS = {
    "public_alpha_readonly": "control/inventory/public_alpha_readonly_00_result.json",
    "public_alpha_hosting": "control/inventory/public_alpha_hosting_result.json",
    "snapshot_relay": "control/inventory/snapshot_relay_result.json",
    "source_wave": "control/inventory/source_wave_result.json",
    "source_action_kernel": "control/inventory/source_action_kernel_result.json",
    "source_snapshot_closeout": "control/inventory/source_snapshot_closeout_result.json",
    "ci_full_discovery_harness": "control/inventory/ci_full_discovery_harness_result.json",
}

REQUIRED_CLOSEOUT_JSON = [
    "control/inventory/public_alpha_readonly_closeout_input_state.json",
    "control/inventory/public_alpha_readonly_closeout_scope_matrix.json",
    "control/inventory/public_alpha_readonly_closeout_route_matrix.json",
    "control/inventory/public_alpha_readonly_closeout_api_matrix.json",
    "control/inventory/public_alpha_readonly_closeout_hosting_matrix.json",
    "control/inventory/public_alpha_readonly_closeout_security_matrix.json",
    "control/inventory/public_alpha_readonly_closeout_boundary_report.json",
    "control/inventory/public_alpha_readonly_closeout_validation_matrix.json",
    "control/inventory/public_alpha_readonly_closeout_full_discovery_handoff.json",
    "control/inventory/public_alpha_readonly_closeout_full_discovery_result.json",
    "control/inventory/public_alpha_readonly_closeout_result.json",
    "control/inventory/public_alpha_readonly_closeout_next_task_decision.json",
    "control/inventory/public_alpha_readonly_closeout_failure_repair_log.json",
]

REQUIRED_AUDIT_FILES = [
    "control/audits/public-alpha-readonly-closeout-01-v0/README.md",
    "control/audits/public-alpha-readonly-closeout-01-v0/public_alpha_readonly_closeout_report.json",
    "control/audits/public-alpha-readonly-closeout-01-v0/route_matrix.md",
    "control/audits/public-alpha-readonly-closeout-01-v0/api_matrix.md",
    "control/audits/public-alpha-readonly-closeout-01-v0/hosting_matrix.md",
    "control/audits/public-alpha-readonly-closeout-01-v0/security_matrix.md",
    "control/audits/public-alpha-readonly-closeout-01-v0/boundary_report.md",
    "control/audits/public-alpha-readonly-closeout-01-v0/validation_matrix.md",
    "control/audits/public-alpha-readonly-closeout-01-v0/full_discovery_handoff.md",
    "control/audits/public-alpha-readonly-closeout-01-v0/external_full_discovery_handoff.json",
    "control/audits/public-alpha-readonly-closeout-01-v0/next_task_decision.md",
    "control/audits/public-alpha-readonly-closeout-01-v0/validation.md",
    "control/audits/public-alpha-readonly-closeout-01-v0/generated/sample_summary.md",
]

REQUIRED_DOCS = [
    "docs/operations/PUBLIC_ALPHA_READONLY_CLOSEOUT.md",
    "docs/operations/POST_PUBLIC_ALPHA_READONLY_CLOSEOUT_PLAN.md",
]

BOUNDARY_FALSE_FIELDS = [
    "deployment_performed",
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
    "master_index_mutated",
    "committed_data_public_index_mutated",
    "committed_instance_state",
    "raw_live_source_response_committed",
    "raw_full_discovery_logs_committed",
    "secrets_committed",
    "operator_tokens_committed",
]


def validate_public_alpha_readonly_closeout(root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    payloads: dict[str, dict[str, Any]] = {}

    for rel in list(PRIOR_RESULTS.values()) + REQUIRED_CLOSEOUT_JSON:
        if not (root / rel).exists():
            errors.append(f"missing required JSON: {rel}")
        else:
            payloads[rel] = _read_json(root / rel, rel, errors)

    for rel in REQUIRED_AUDIT_FILES + REQUIRED_DOCS:
        if not (root / rel).exists():
            errors.append(f"missing required file: {rel}")

    _validate_prior_results(payloads, errors)
    _validate_closeout_matrices(payloads, root, errors)
    _validate_boundary_report(payloads, errors)
    _validate_full_discovery_gate(payloads, errors)
    _validate_docs(root, errors)
    _validate_no_private_root(root, errors)

    result = payloads.get("control/inventory/public_alpha_readonly_closeout_result.json", {})
    full = payloads.get("control/inventory/public_alpha_readonly_closeout_full_discovery_result.json", {})
    waiting = result.get("status") == WAITING_STATUS and full.get("external_summary_received") is False
    pass_ready = result.get("status") == "pass" and full.get("full_unittest_discovery_passed") is True
    if not waiting and not pass_ready:
        errors.append("closeout result must be waiting for external full discovery or pass with a passing summary")

    status = "invalid" if errors else (WAITING_STATUS if waiting else "pass")
    return {
        "schema_version": "public_alpha_readonly_closeout_validation.v0",
        "task": "PUBLIC-ALPHA-READONLY-CLOSEOUT-01",
        "status": status,
        "public_alpha_readonly_verified": not errors,
        "public_alpha_hosting_verified": not errors,
        "snapshot_relay_verified": not errors,
        "focused_validators_passed": not errors,
        "external_full_discovery_summary_received": bool(full.get("external_summary_received")),
        "full_unittest_discovery_passed": bool(full.get("full_unittest_discovery_passed")),
        "full_unittest_discovery_count": int(full.get("full_unittest_discovery_count") or 0),
        "public_alpha_ready_for_main_promotion": bool(result.get("public_alpha_ready_for_main_promotion")),
        "errors": errors,
    }


def _validate_prior_results(payloads: dict[str, dict[str, Any]], errors: list[str]) -> None:
    readonly = payloads.get(PRIOR_RESULTS["public_alpha_readonly"], {})
    if readonly.get("status") != "pass":
        errors.append("public alpha read-only result must be pass")
    for field in ("snapshot_backed", "relay_backed", "reviewed_index_only", "read_only"):
        if readonly.get(field) is not True:
            errors.append(f"public alpha read-only result must set {field}=true")

    hosting = payloads.get(PRIOR_RESULTS["public_alpha_hosting"], {})
    if hosting.get("status") != "pass":
        errors.append("public alpha hosting result must be pass")
    for field in (
        "security_model_added",
        "rate_limit_model_added",
        "observability_model_added",
        "privacy_abuse_docs_added",
        "rollback_plan_added",
        "launch_gates_added",
    ):
        if hosting.get(field) is not True:
            errors.append(f"public alpha hosting result must set {field}=true")

    snapshot = payloads.get(PRIOR_RESULTS["snapshot_relay"], {})
    if snapshot.get("status") not in {"pass", "pass_with_warnings"}:
        errors.append("snapshot relay result must be pass or pass_with_warnings")
    if snapshot.get("public_projection_read_only") is not True:
        errors.append("snapshot relay result must keep public_projection_read_only=true")

    for key in ("source_wave", "source_action_kernel", "ci_full_discovery_harness"):
        status = payloads.get(PRIOR_RESULTS[key], {}).get("status")
        if status not in {"pass", "pass_with_warnings"}:
            errors.append(f"{key} result must be pass or pass_with_warnings")

    source_closeout = payloads.get(PRIOR_RESULTS["source_snapshot_closeout"], {})
    if source_closeout.get("status") not in {"pass", "pass_with_warnings", "WAITING_FOR_EXTERNAL_FULL_DISCOVERY"}:
        errors.append("source snapshot closeout result must be pass, pass_with_warnings, or historical waiting evidence")


def _validate_closeout_matrices(payloads: dict[str, dict[str, Any]], root: Path, errors: list[str]) -> None:
    readonly = payloads.get(PRIOR_RESULTS["public_alpha_readonly"], {})
    route_matrix = payloads.get("control/inventory/public_alpha_readonly_closeout_route_matrix.json", {})
    route_values = [item.get("route") for item in route_matrix.get("routes", [])]
    for route in readonly.get("public_web_routes_added", []):
        if route not in route_values:
            errors.append(f"closeout route matrix missing {route}")
    for item in route_matrix.get("routes", []):
        if item.get("read_only") is not True:
            errors.append(f"route {item.get('route')} must be read_only=true")
        if item.get("public_mutation_enabled") is not False:
            errors.append(f"route {item.get('route')} must keep public_mutation_enabled=false")

    api_matrix = payloads.get("control/inventory/public_alpha_readonly_closeout_api_matrix.json", {})
    for route in readonly.get("public_api_routes_added", []):
        if route not in api_matrix.get("api_routes", []):
            errors.append(f"closeout api matrix missing {route}")
    for field in (
        "public_write_actions_enabled",
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

    hosting = payloads.get("control/inventory/public_alpha_readonly_closeout_hosting_matrix.json", {})
    if hosting.get("external_full_discovery_required_before_promotion") is not True:
        errors.append("hosting matrix must require external full discovery before promotion")
    for rel in hosting.get("required_docs", []):
        if not (root / rel).exists():
            errors.append(f"hosting matrix required doc missing: {rel}")

    security = payloads.get("control/inventory/public_alpha_readonly_closeout_security_matrix.json", {})
    for field in (
        "security_model_exists",
        "rate_limit_model_exists",
        "observability_model_exists",
        "privacy_notice_exists",
        "abuse_takedown_process_exists",
        "rollback_plan_exists",
    ):
        if security.get(field) is not True:
            errors.append(f"security matrix must set {field}=true")
    for field in ("credentials_in_repo_allowed", "inline_secrets_allowed", "public_mutation_enabled"):
        if security.get(field) is not False:
            errors.append(f"security matrix must set {field}=false")


def _validate_boundary_report(payloads: dict[str, dict[str, Any]], errors: list[str]) -> None:
    boundary = payloads.get("control/inventory/public_alpha_readonly_closeout_boundary_report.json", {})
    for field in BOUNDARY_FALSE_FIELDS:
        if boundary.get(field) is not False:
            errors.append(f"boundary report must set {field}=false")

    result = payloads.get("control/inventory/public_alpha_readonly_closeout_result.json", {})
    for field in (
        "deployment_performed",
        "production_readiness_claimed",
        "public_launch_readiness_claimed",
        "public_mutation_enabled",
        "public_live_source_fanout_enabled",
        "download_performed",
        "extraction_executed",
        "model_provider_used",
    ):
        if result.get(field) is not False:
            errors.append(f"closeout result must set {field}=false")


def _validate_full_discovery_gate(payloads: dict[str, dict[str, Any]], errors: list[str]) -> None:
    handoff = payloads.get("control/inventory/public_alpha_readonly_closeout_full_discovery_handoff.json", {})
    full = payloads.get("control/inventory/public_alpha_readonly_closeout_full_discovery_result.json", {})
    result = payloads.get("control/inventory/public_alpha_readonly_closeout_result.json", {})

    if full.get("external_summary_received") is True:
        if full.get("full_unittest_discovery_passed") is not True:
            errors.append("received external summary must be passing before closeout pass")
        if result.get("public_alpha_ready_for_main_promotion") is not True:
            errors.append("passing full discovery should make promotion readiness true")
    else:
        if handoff.get("status") != "WAITING_FOR_EXTERNAL_FULL_DISCOVERY":
            errors.append("missing external full-discovery waiting handoff")
        if "../eureka-test-runs/public_alpha_readonly_closeout" not in handoff.get("command", ""):
            errors.append("handoff command must use repo-external public alpha closeout output path")
        if result.get("public_alpha_ready_for_main_promotion") is not False:
            errors.append("waiting closeout must keep promotion readiness false")
        if result.get("recommended_next_task") != "external_full_discovery":
            errors.append("waiting closeout must recommend external_full_discovery")

    if full.get("full_discovery_run_inside_ai") is not False:
        errors.append("full discovery must not run inside AI")


def _validate_docs(root: Path, errors: list[str]) -> None:
    docs = "\n".join(
        (root / rel).read_text(encoding="utf-8").lower()
        for rel in REQUIRED_DOCS
        if (root / rel).exists()
    )
    for phrase in (
        "not a launch",
        "no deployment",
        "external full discovery",
        "waiting_for_external_full_discovery",
        "no public launch readiness",
    ):
        if phrase not in docs:
            errors.append(f"closeout docs missing required phrase: {phrase}")


def _validate_no_private_root(root: Path, errors: list[str]) -> None:
    if (root / ".aide.local").exists():
        errors.append(".aide.local must not exist in repo root")


def _read_json(path: Path, rel: str, errors: list[str]) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"invalid JSON in {rel}: {exc}")
    return {}


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate PUBLIC-ALPHA-READONLY-CLOSEOUT-01.")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(list(argv) if argv is not None else None)

    report = validate_public_alpha_readonly_closeout()
    output = stdout or sys.stdout
    if args.json:
        output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        output.write(f"public alpha read-only closeout validation: {report['status']}\n")
        for error in report["errors"]:
            output.write(f"ERROR: {error}\n")
    return 0 if report["status"] != "invalid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
