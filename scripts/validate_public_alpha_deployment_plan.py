#!/usr/bin/env python3
"""Validate PUBLIC-ALPHA-DEPLOYMENT-PLAN-01 artifacts."""

from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]

REQUIRED_CONFIG_KEYS = {
    "PUBLIC_SEARCH_ENABLED",
    "HOSTED_BACKEND_ENABLED",
    "LIVE_PROBES_ENABLED",
    "SOURCE_SYNC_ENABLED",
    "CONNECTOR_IA_ENABLED",
    "CONNECTOR_H1_ENABLED",
    "DOWNLOADS_ENABLED",
    "UPLOADS_ENABLED",
    "ACCOUNTS_ENABLED",
    "TELEMETRY_ENABLED",
    "PUBLIC_RELAY_ENABLED",
    "PUBLIC_INDEX_WRITE_ENABLED",
    "MASTER_INDEX_WRITE_ENABLED",
    "RATE_LIMIT_ENABLED",
    "KILL_SWITCH_GLOBAL",
    "KILL_SWITCH_CONNECTORS",
    "KILL_SWITCH_DOWNLOADS",
}
RISKY_DISABLED_KEYS = REQUIRED_CONFIG_KEYS - {"RATE_LIMIT_ENABLED", "KILL_SWITCH_GLOBAL", "KILL_SWITCH_CONNECTORS", "KILL_SWITCH_DOWNLOADS"}
REQUIRED_CONTRACTS = [
    "control/schemas/policies/hosting/public_alpha_deployment_plan.v0.json",
    "control/schemas/policies/hosting/public_alpha_deployment_step.v0.json",
    "control/schemas/policies/hosting/public_alpha_environment_matrix.v0.json",
    "contracts/hosting/public_alpha_config_manifest.v0.json",
    "control/schemas/policies/hosting/public_alpha_static_backend_split.v0.json",
    "control/schemas/policies/hosting/public_alpha_dns_readiness.v0.json",
    "contracts/hosting/public_alpha_provider_profile.v0.json",
    "control/schemas/policies/hosting/public_alpha_rollout_gate.v0.json",
    "control/schemas/policies/hosting/public_alpha_operator_checklist.v0.json",
    "control/schemas/audits/hosting/public_alpha_deployment_noop_report.v0.json",
]
REQUIRED_POLICIES = [
    "control/inventory/hosting/public_alpha_deployment_plan_policy.json",
    "control/inventory/hosting/public_alpha_environment_matrix_policy.json",
    "control/inventory/hosting/public_alpha_config_manifest_policy.json",
    "control/inventory/hosting/public_alpha_static_backend_split_policy.json",
    "control/inventory/hosting/public_alpha_dns_readiness_policy.json",
    "control/inventory/hosting/public_alpha_provider_profile_policy.json",
    "control/inventory/hosting/public_alpha_rollout_gate_policy.json",
    "control/inventory/hosting/public_alpha_operator_checklist_policy.json",
    "control/inventory/hosting/public_alpha_deployment_noop_policy.json",
    "control/inventory/hosting/public_alpha_planning_truth_policy.json",
    "control/inventory/hosting/public_alpha_planning_no_deploy_policy.json",
]
REQUIRED_EXAMPLES = [
    "examples/hosting/deployment/public_alpha_deployment_plan_v0.json",
    "examples/hosting/deployment/public_alpha_deployment_plan_blocked_v0.json",
    "examples/hosting/deployment/public_alpha_environment_matrix_v0.json",
    "examples/hosting/deployment/public_alpha_config_manifest_v0.json",
    "examples/hosting/deployment/public_alpha_static_backend_split_v0.json",
    "examples/hosting/deployment/public_alpha_dns_readiness_unknown_v0.json",
    "examples/hosting/deployment/public_alpha_provider_profile_provider_neutral_v0.json",
    "examples/hosting/deployment/public_alpha_rollout_gate_operator_required_v0.json",
    "examples/hosting/deployment/public_alpha_operator_checklist_v0.json",
    "examples/hosting/deployment/public_alpha_deployment_noop_report_v0.json",
]
REQUIRED_DOCS = [
    "docs/reference/PUBLIC_ALPHA_DEPLOYMENT_PLAN_CONTRACT.md",
    "docs/reference/PUBLIC_ALPHA_ENVIRONMENT_MATRIX_CONTRACT.md",
    "docs/reference/PUBLIC_ALPHA_CONFIG_MANIFEST_CONTRACT.md",
    "docs/reference/PUBLIC_ALPHA_STATIC_BACKEND_SPLIT_CONTRACT.md",
    "docs/reference/PUBLIC_ALPHA_ROLLOUT_GATE_CONTRACT.md",
    "docs/architecture/PUBLIC_ALPHA_DEPLOYMENT_MODEL.md",
    "docs/architecture/PUBLIC_ALPHA_STATIC_BACKEND_SPLIT.md",
    "docs/operations/PUBLIC_ALPHA_DEPLOYMENT_PLANNING.md",
    "docs/operations/PUBLIC_ALPHA_OPERATOR_CHECKLIST.md",
    "docs/operations/PUBLIC_ALPHA_DNS_READINESS.md",
    "docs/operations/PUBLIC_ALPHA_PROVIDER_NEUTRAL_STEPS.md",
    "docs/operations/PUBLIC_ALPHA_NO_DEPLOYMENT_POLICY.md",
]
REQUIRED_SCRIPTS = [
    "scripts/build_public_alpha_deployment_plan.py",
    "scripts/check_public_alpha_deployment_plan.py",
    "scripts/check_public_alpha_config_manifest.py",
    "scripts/check_public_alpha_dns_readiness.py",
    "scripts/validate_public_alpha_deployment_plan.py",
    "scripts/summarize_public_alpha_deployment_plan.py",
]
AUDIT_ROOT = "control/audits/public-alpha-deployment-plan-01-v0"
AUDIT_FILES = [
    "README.md",
    "public_alpha_deployment_plan_01_report.json",
    "deployment_architecture_summary.md",
    "static_backend_split_summary.md",
    "environment_config_summary.md",
    "dns_custom_domain_readiness.md",
    "provider_neutral_steps.md",
    "rollout_gate_summary.md",
    "operator_checklist.md",
    "no_deployment_report.md",
    "next_task_recommendation.md",
    "validation.md",
    "generated/sample_public_alpha_deployment_plan.json",
    "generated/sample_public_alpha_config_manifest.json",
    "generated/sample_public_alpha_rollout_gate.json",
    "generated/sample_public_alpha_deployment_noop_report.json",
    "generated/sample_public_alpha_deployment_summary.md",
]
FORBIDDEN_TRUE_KEYS = {
    "deployment_plan_is_launch",
    "operator_signoff_inferred",
    "public_alpha_live_claimed",
    "production_claimed",
    "public_index_mutated",
    "master_index_mutated",
    "rights_clearance_claimed",
    "malware_safety_claimed",
    "verified_installability_claimed",
    "changed_public_search_behavior",
    "enabled_live_source_fanout",
    "enabled_source_sync",
    "enabled_downloads",
    "enabled_uploads",
    "enabled_accounts",
    "enabled_telemetry",
    "enabled_public_relay",
    "enabled_hosting",
    "mutated_site_dist",
    "mutated_public_index",
    "mutated_master_index",
    "deployment_allowed_current",
    "launch_allowed_current",
    "deployment_performed",
    "provider_api_called",
    "dns_changed",
    "site_dist_mutated",
    "secrets_created",
    "public_backend_started",
    "custom_domain_claimed",
    "provider_credentials_committed",
    "secrets_committed",
}
FORBIDDEN_OUTPUT_ROOTS = [
    "site/dist",
    "data/public_index",
    "data/master_index",
    "master_index",
    ".aide.local",
    ".local/eureka",
    ".cache/eureka",
    "provider",
    "providers",
    "secrets",
    ".secrets",
    "deploy",
]
SECRET_VALUE_PATTERNS = [
    re.compile(r"(?<![A-Za-z0-9])sk-[A-Za-z0-9_-]{8,}"),
    re.compile(r"ghp_[A-Za-z0-9_]{8,}"),
    re.compile(r"xox[baprs]-[A-Za-z0-9-]{8,}"),
    re.compile(r"AKIA[A-Z0-9]{8,}"),
    re.compile(r"BEGIN (?:RSA |EC |OPENSSH |)?PRIVATE KEY"),
]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = validate_public_alpha_deployment_plan(REPO_ROOT)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(format_validation(report))
    return 0 if report["status"] == "pass" else 1


def validate_public_alpha_deployment_plan(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    _validate_json_files(repo_root, REQUIRED_CONTRACTS + REQUIRED_POLICIES + REQUIRED_EXAMPLES, errors)
    _validate_required_files(repo_root, REQUIRED_DOCS + REQUIRED_SCRIPTS, errors)
    _validate_audit_pack(repo_root, errors)
    _validate_plan(load_json(repo_root / "examples/hosting/deployment/public_alpha_deployment_plan_v0.json"), errors)
    _validate_config_manifest(load_json(repo_root / "examples/hosting/deployment/public_alpha_config_manifest_v0.json"), errors)
    _validate_dns_readiness(load_json(repo_root / "examples/hosting/deployment/public_alpha_dns_readiness_unknown_v0.json"), errors)
    _validate_rollout_gate(load_json(repo_root / "examples/hosting/deployment/public_alpha_rollout_gate_operator_required_v0.json"), errors)
    _validate_noop(load_json(repo_root / "examples/hosting/deployment/public_alpha_deployment_noop_report_v0.json"), errors)
    _validate_no_private_roots(repo_root, errors)
    return {
        "schema_version": "public_alpha_deployment_plan_validation.v0",
        "status": "fail" if errors else "pass",
        "contract_count": len(REQUIRED_CONTRACTS),
        "policy_count": len(REQUIRED_POLICIES),
        "example_count": len(REQUIRED_EXAMPLES),
        "script_count": len(REQUIRED_SCRIPTS),
        "doc_count": len(REQUIRED_DOCS),
        "errors": errors,
    }


def detect_forbidden_deployment_claims(payload: Any, path: str = "$") -> list[str]:
    errors: list[str] = []
    if isinstance(payload, dict):
        for key, value in payload.items():
            child = f"{path}.{key}"
            if key in FORBIDDEN_TRUE_KEYS and value is True:
                errors.append(f"{child}: forbidden deployment-planning claim is true.")
            errors.extend(detect_forbidden_deployment_claims(value, child))
    elif isinstance(payload, list):
        for index, value in enumerate(payload):
            errors.extend(detect_forbidden_deployment_claims(value, f"{path}[{index}]"))
    elif isinstance(payload, str):
        for pattern in SECRET_VALUE_PATTERNS:
            if pattern.search(payload):
                errors.append(f"{path}: secret-like value is forbidden.")
    return errors


def validate_output_path(raw_path: str, repo_root: Path = REPO_ROOT) -> Path:
    path = Path(raw_path)
    if not path.is_absolute():
        path = repo_root / path
    resolved = path.resolve()
    repo = repo_root.resolve()
    try:
        relative = resolved.relative_to(repo).as_posix()
    except ValueError:
        temp_root = Path(tempfile.gettempdir()).resolve()
        try:
            resolved.relative_to(temp_root)
        except ValueError as exc:
            raise SystemExit(f"Refusing output outside repository or temp directory: {raw_path}") from exc
    else:
        lower = relative.casefold()
        allowed = lower.startswith("examples/hosting/") or (lower.startswith("control/audits/") and "/generated/" in lower)
        if not allowed:
            raise SystemExit(f"Refusing output outside allowed public alpha planning roots: {relative}")
        for forbidden in FORBIDDEN_OUTPUT_ROOTS:
            key = forbidden.casefold().rstrip("/")
            if lower == key or lower.startswith(key + "/"):
                raise SystemExit(f"Refusing forbidden output path: {relative}")
    resolved.parent.mkdir(parents=True, exist_ok=True)
    return resolved


def write_json_output(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def format_validation(report: dict[str, Any]) -> str:
    lines = [
        "Public alpha deployment plan validation",
        f"status: {report['status']}",
        f"contracts: {report['contract_count']}",
        f"policies: {report['policy_count']}",
        f"examples: {report['example_count']}",
        f"scripts: {report['script_count']}",
        f"docs: {report['doc_count']}",
    ]
    lines.extend(f"ERROR: {error}" for error in report["errors"])
    return "\n".join(lines)


def _validate_json_files(repo_root: Path, relatives: list[str], errors: list[str]) -> None:
    for relative in relatives:
        path = repo_root / relative
        if not path.is_file():
            errors.append(f"{relative}: missing required file.")
            continue
        try:
            payload = load_json(path)
        except Exception as exc:
            errors.append(f"{relative}: invalid JSON: {exc}")
            continue
        if relative.startswith("examples/hosting/deployment") or relative.startswith(AUDIT_ROOT):
            errors.extend(detect_forbidden_deployment_claims(payload, relative))


def _validate_required_files(repo_root: Path, relatives: list[str], errors: list[str]) -> None:
    for relative in relatives:
        path = repo_root / relative
        if not path.is_file():
            errors.append(f"{relative}: missing required file.")
        elif not path.read_text(encoding="utf-8").strip():
            errors.append(f"{relative}: empty required file.")


def _validate_audit_pack(repo_root: Path, errors: list[str]) -> None:
    audit = repo_root / AUDIT_ROOT
    for filename in AUDIT_FILES:
        path = audit / filename
        if not path.is_file():
            errors.append(f"{AUDIT_ROOT}/{filename}: missing audit file.")
            continue
        if path.suffix == ".json":
            try:
                errors.extend(detect_forbidden_deployment_claims(load_json(path), f"{AUDIT_ROOT}/{filename}"))
            except Exception as exc:
                errors.append(f"{AUDIT_ROOT}/{filename}: invalid JSON: {exc}")


def _validate_plan(payload: dict[str, Any], errors: list[str]) -> None:
    if payload.get("plan_status") not in {"planning_only", "operator_review_required", "blocked", "ready_for_operator_review_future", "not_evaluable"}:
        errors.append("deployment plan status must be planning-only, operator-review, blocked, future-review, or not evaluable.")
    if not payload.get("deployment_steps"):
        errors.append("deployment plan must include deployment_steps.")
    for step in payload.get("deployment_steps", []):
        if step.get("external_provider_action") is not False:
            errors.append(f"{step.get('step_id')}: external provider action must be false current.")
        if step.get("secret_required") is not False:
            errors.append(f"{step.get('step_id')}: secret_required must be false current.")
    _require_false_boundaries(payload, errors, "deployment plan")


def _validate_config_manifest(payload: dict[str, Any], errors: list[str]) -> None:
    variables = {item.get("config_key"): item for item in payload.get("config_variables", [])}
    missing = sorted(REQUIRED_CONFIG_KEYS - set(variables))
    if missing:
        errors.append(f"config manifest missing keys: {missing}")
    for key in RISKY_DISABLED_KEYS:
        item = variables.get(key, {})
        if item.get("safe_default") is not False:
            errors.append(f"{key}: risky safe_default must be false.")
        if item.get("secret") is not False:
            errors.append(f"{key}: config entry must not be secret.")
    for key in ("RATE_LIMIT_ENABLED", "KILL_SWITCH_GLOBAL", "KILL_SWITCH_CONNECTORS", "KILL_SWITCH_DOWNLOADS"):
        item = variables.get(key, {})
        if item.get("safe_default") is not True:
            errors.append(f"{key}: protective control safe_default must be true.")
    _require_false_boundaries(payload, errors, "config manifest")


def _validate_dns_readiness(payload: dict[str, Any], errors: list[str]) -> None:
    if payload.get("custom_domain_status") not in {"unknown", "not_configured", "operator_required", "blocked", "not_evaluable"}:
        errors.append("current DNS readiness must not claim configured DNS.")
    if payload.get("current_records_known") is not False:
        errors.append("current_records_known must be false unless evidence exists.")
    if payload.get("verification_evidence_refs"):
        errors.append("current DNS readiness example must not include verification evidence.")
    _require_false_boundaries(payload, errors, "dns readiness")


def _validate_rollout_gate(payload: dict[str, Any], errors: list[str]) -> None:
    if payload.get("launch_allowed_current") is not False:
        errors.append("rollout gate launch_allowed_current must be false.")
    if payload.get("deployment_allowed_current") is not False:
        errors.append("rollout gate deployment_allowed_current must be false.")
    if not payload.get("missing_evidence"):
        errors.append("rollout gate must list missing evidence.")
    _require_false_boundaries(payload, errors, "rollout gate")


def _validate_noop(payload: dict[str, Any], errors: list[str]) -> None:
    for key in ("deployment_performed", "provider_api_called", "dns_changed", "site_dist_mutated", "secrets_created", "public_backend_started", "public_alpha_live_claimed", "production_claimed"):
        if payload.get(key) is not False:
            errors.append(f"noop report {key} must be false.")
    _require_false_boundaries(payload, errors, "noop report")


def _require_false_boundaries(payload: dict[str, Any], errors: list[str], label: str) -> None:
    for section in ("truth_boundary", "product_boundary"):
        values = payload.get(section, {})
        if not isinstance(values, dict):
            errors.append(f"{label}: {section} must be an object.")
            continue
        for key, value in values.items():
            if key in FORBIDDEN_TRUE_KEYS and value is not False:
                errors.append(f"{label}: {section}.{key} must be false.")


def _validate_no_private_roots(repo_root: Path, errors: list[str]) -> None:
    for relative in (".aide.local", ".local/eureka", ".cache/eureka"):
        if (repo_root / relative).exists():
            errors.append(f"{relative}: local private-state root must not be created.")


if __name__ == "__main__":
    raise SystemExit(main())
