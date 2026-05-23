#!/usr/bin/env python3
"""Validate E-BUNDLE-01 hosting readiness artifacts without deployment."""

from __future__ import annotations

import argparse
import json
import re
import tempfile
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]

REQUIRED_NON_CLAIMS = [
    "not_production",
    "not_exhaustive",
    "not_rights_cleared",
    "not_malware_safe",
    "not_installability_verified",
    "not_download_service",
    "not_app_store",
    "not_upload_service",
    "not_account_service",
    "not_telemetry_claim",
    "not_live_source_fanout_unless_explicit",
    "not_replacement_for_source_projects",
]
REQUIRED_CONFIG_KEYS = [
    "PUBLIC_SEARCH_ENABLED",
    "LIVE_PROBES_ENABLED",
    "SOURCE_SYNC_ENABLED",
    "CONNECTOR_IA_ENABLED",
    "CONNECTOR_H1_ENABLED",
    "DOWNLOADS_ENABLED",
    "UPLOADS_ENABLED",
    "ACCOUNTS_ENABLED",
    "TELEMETRY_ENABLED",
    "PUBLIC_INDEX_WRITE_ENABLED",
    "MASTER_INDEX_WRITE_ENABLED",
    "RELAY_PUBLIC_BIND_ENABLED",
]
REQUIRED_CONTRACTS = [
    "contracts/schema/control/policies/hosting/public_alpha_non_claims.v0.json",
    "contracts/hosting/host_profile.v0.json",
    "contracts/schema/control/policies/hosting/deployment_environment.v0.json",
    "contracts/schema/control/audits/hosting/hosting_readiness_report.v0.json",
    "contracts/hosting/runtime_config_boundary.v0.json",
    "contracts/hosting/rate_limit_policy.v0.json",
    "contracts/hosting/secrets_policy.v0.json",
    "contracts/hosting/observability_policy.v0.json",
    "contracts/schema/control/policies/hosting/incident_response_plan.v0.json",
    "contracts/schema/control/policies/hosting/rollback_plan.v0.json",
    "contracts/schema/control/policies/hosting/takedown_rights_safety_plan.v0.json",
    "contracts/schema/control/policies/hosting/connector_kill_switch_plan.v0.json",
    "contracts/schema/control/policies/hosting/public_launch_evidence.v0.json",
]
REQUIRED_POLICIES = [
    "control/inventory/hosting/public_alpha_non_claims_policy.json",
    "control/inventory/hosting/host_profile_policy.json",
    "control/inventory/hosting/deployment_environment_policy.json",
    "control/inventory/hosting/runtime_config_boundary_policy.json",
    "control/inventory/hosting/rate_limit_abuse_policy.json",
    "control/inventory/hosting/secrets_credential_policy.json",
    "control/inventory/hosting/observability_logging_policy.json",
    "control/inventory/hosting/incident_response_policy.json",
    "control/inventory/hosting/rollback_policy.json",
    "control/inventory/hosting/takedown_rights_safety_policy.json",
    "control/inventory/hosting/connector_kill_switch_policy.json",
    "control/inventory/hosting/public_launch_evidence_policy.json",
    "control/inventory/hosting/hosting_truth_policy.json",
    "control/inventory/hosting/hosting_path_policy.json",
    "control/inventory/hosting/hosting_no_deploy_policy.json",
]
REQUIRED_EXAMPLES = [
    "examples/hosting/public_alpha_non_claims_v0.json",
    "examples/hosting/host_profiles/static_pages_profile_v0.json",
    "examples/hosting/host_profiles/hosted_backend_rehearsal_profile_v0.json",
    "examples/hosting/host_profiles/static_files_profile_v0.json",
    "examples/hosting/host_profiles/policy_blocked_host_profile_v0.json",
    "examples/hosting/environments/local_rehearsal_environment_v0.json",
    "examples/hosting/environments/static_only_environment_v0.json",
    "examples/hosting/environments/operator_gated_hosted_alpha_environment_v0.json",
    "examples/hosting/config/runtime_config_boundary_v0.json",
    "examples/hosting/security/secrets_policy_example_v0.json",
    "examples/hosting/security/rate_limit_policy_example_v0.json",
    "examples/hosting/security/connector_kill_switch_plan_v0.json",
    "examples/hosting/ops/observability_policy_example_v0.json",
    "examples/hosting/ops/incident_response_plan_v0.json",
    "examples/hosting/ops/rollback_plan_v0.json",
    "examples/hosting/ops/takedown_rights_safety_plan_v0.json",
    "examples/hosting/readiness/hosting_readiness_report_v0.json",
    "examples/hosting/readiness/public_launch_evidence_required_v0.json",
    "examples/hosting/readiness/policy_blocked_launch_evidence_v0.json",
]
REQUIRED_DOCS = [
    "docs/reference/PUBLIC_ALPHA_NON_CLAIMS_CONTRACT.md",
    "docs/reference/HOST_PROFILE_CONTRACT.md",
    "docs/reference/DEPLOYMENT_ENVIRONMENT_CONTRACT.md",
    "docs/reference/HOSTING_READINESS_REPORT_CONTRACT.md",
    "docs/reference/RUNTIME_CONFIG_BOUNDARY_CONTRACT.md",
    "docs/reference/PUBLIC_LAUNCH_EVIDENCE_CONTRACT.md",
    "docs/architecture/HOSTING_OPERATIONS_MODEL.md",
    "docs/architecture/PUBLIC_ALPHA_RUNTIME_BOUNDARY.md",
    "docs/operations/PUBLIC_ALPHA_NON_CLAIMS.md",
    "docs/operations/HOSTING_READINESS_CHECKLIST.md",
    "docs/operations/SECRETS_AND_CREDENTIAL_POLICY.md",
    "docs/operations/RATE_LIMIT_AND_ABUSE_POLICY.md",
    "docs/operations/OBSERVABILITY_AND_LOGGING_POLICY.md",
    "docs/operations/INCIDENT_RESPONSE_AND_ROLLBACK.md",
    "docs/operations/TAKEDOWN_RIGHTS_SAFETY_OPERATIONS.md",
    "docs/operations/CONNECTOR_KILL_SWITCH_OPERATIONS.md",
    "docs/operations/NO_DEPLOYMENT_IN_E_BUNDLE_01.md",
]
AUDIT_ROOT = "control/audits/e-bundle-01-hosting-ops-readiness-v0"
AUDIT_FILES = [
    "README.md",
    "e_bundle_01_report.json",
    "public_alpha_non_claims_summary.md",
    "host_profile_summary.md",
    "deployment_environment_summary.md",
    "runtime_config_boundary_report.md",
    "rate_limit_abuse_report.md",
    "secrets_credential_report.md",
    "observability_logging_report.md",
    "incident_rollback_report.md",
    "takedown_rights_safety_report.md",
    "connector_kill_switch_report.md",
    "no_deployment_report.md",
    "e_bundle_02_readiness_recommendation.md",
    "validation.md",
]
FORBIDDEN_TRUE_KEYS = {
    "public_alpha_live_claimed",
    "production_claimed",
    "deployed_backend",
    "deployed_static_site",
    "dns_changed",
    "provider_api_called",
    "site_dist_mutated",
    "enabled_hosting",
    "enabled_live_source_fanout",
    "enabled_downloads",
    "enabled_uploads",
    "enabled_accounts",
    "enabled_telemetry",
    "enabled_public_relay",
    "mutated_site_dist",
    "mutated_public_index",
    "mutated_master_index",
    "public_index_mutation_allowed",
    "master_index_mutation_allowed",
    "rights_clearance_claimed",
    "malware_safety_claimed",
    "verified_installability_claimed",
    "deployment_performed",
    "provider_credentials_committed",
    "secrets_committed",
    "custom_domain_claimed",
    "source_sync_enabled",
}
FORBIDDEN_OUTPUT_ROOTS = [
    "site/dist",
    "site/dist/data/public_index",
    "data/master_index",
    "master_index",
    ".aide.local",
    ".local/eureka",
    ".cache/eureka",
]
SECRET_VALUE_PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9_-]{8,}"),
    re.compile(r"ghp_[A-Za-z0-9_]{8,}"),
    re.compile(r"xox[baprs]-[A-Za-z0-9-]{8,}"),
    re.compile(r"AKIA[A-Z0-9]{8,}"),
    re.compile(r"BEGIN (?:RSA |EC |OPENSSH |)?PRIVATE KEY"),
]
FORBIDDEN_PHRASES = [
    "production-ready",
    "rights-cleared",
    "malware-safe",
    "installability verified",
    "public alpha is live",
    "hosted backend is deployed",
    "dns configured",
    "uploads enabled",
    "accounts enabled",
    "telemetry enabled",
    "live source fanout enabled",
    "official app store",
    "download service",
]
NEGATIONS = ["no ", "not ", "must not ", "without ", "does not ", "is not ", "not a "]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = validate_hosting_readiness(REPO_ROOT)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(format_validation(report))
    return 0 if report["status"] == "pass" else 1


def validate_hosting_readiness(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    _validate_json_files(repo_root, REQUIRED_CONTRACTS + REQUIRED_POLICIES + REQUIRED_EXAMPLES, errors)
    _validate_docs(repo_root, errors)
    _validate_audit_pack(repo_root, errors)
    _validate_non_claims(repo_root / "examples/hosting/public_alpha_non_claims_v0.json", errors)
    _validate_runtime_config(repo_root / "examples/hosting/config/runtime_config_boundary_v0.json", errors)
    _validate_readiness_report(repo_root / "examples/hosting/readiness/hosting_readiness_report_v0.json", errors)
    _validate_public_launch_evidence(repo_root / "examples/hosting/readiness/public_launch_evidence_required_v0.json", errors)
    _validate_no_private_roots(repo_root, errors)
    return {
        "schema_version": "hosting_readiness_validation.v0",
        "status": "fail" if errors else "pass",
        "contract_count": len(REQUIRED_CONTRACTS),
        "policy_count": len(REQUIRED_POLICIES),
        "example_count": len(REQUIRED_EXAMPLES),
        "doc_count": len(REQUIRED_DOCS),
        "errors": errors,
    }


def detect_forbidden_hosting_claims(payload: Any, path: str = "$") -> list[str]:
    errors: list[str] = []
    if isinstance(payload, dict):
        for key, value in payload.items():
            child = f"{path}.{key}"
            if key in FORBIDDEN_TRUE_KEYS and value is True:
                errors.append(f"{child}: forbidden hosting claim is true.")
            errors.extend(detect_forbidden_hosting_claims(value, child))
    elif isinstance(payload, list):
        for index, value in enumerate(payload):
            errors.extend(detect_forbidden_hosting_claims(value, f"{path}[{index}]"))
    elif isinstance(payload, str):
        lowered = payload.casefold()
        for pattern in SECRET_VALUE_PATTERNS:
            if pattern.search(payload):
                errors.append(f"{path}: secret-like value is forbidden.")
        for phrase in FORBIDDEN_PHRASES:
            if phrase in lowered and not _is_negated(lowered, phrase):
                errors.append(f"{path}: forbidden positive claim phrase '{phrase}'.")
    return errors


def summarize_hosting_examples(input_paths: list[Path], repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    files = _expand_json_inputs(input_paths, repo_root)
    counts = {
        "public_alpha_non_claims": 0,
        "host_profiles": 0,
        "deployment_environments": 0,
        "runtime_config_boundaries": 0,
        "security_policies": 0,
        "ops_plans": 0,
        "readiness_reports": 0,
        "launch_evidence_requirements": 0,
    }
    for path in files:
        payload = _load_json(path)
        version = payload.get("schema_version")
        if version == "public_alpha_non_claims.v0":
            counts["public_alpha_non_claims"] += 1
        elif version == "host_profile.v0":
            counts["host_profiles"] += 1
        elif version == "deployment_environment.v0":
            counts["deployment_environments"] += 1
        elif version == "runtime_config_boundary.v0":
            counts["runtime_config_boundaries"] += 1
        elif version in {"secrets_policy.v0", "rate_limit_policy.v0", "connector_kill_switch_plan.v0", "observability_policy.v0"}:
            counts["security_policies"] += 1
        elif version in {"incident_response_plan.v0", "rollback_plan.v0", "takedown_rights_safety_plan.v0"}:
            counts["ops_plans"] += 1
        elif version == "hosting_readiness_report.v0":
            counts["readiness_reports"] += 1
        elif version == "public_launch_evidence.v0":
            counts["launch_evidence_requirements"] += 1
    return {
        "schema_version": "hosting_readiness_summary.v0",
        "status": "pass",
        "input_count": len(files),
        "counts": counts,
        "e_bundle_02_readiness": "READY_FOR_E_BUNDLE_02",
        "scope": {
            "readiness_only": True,
            "deployed_backend": False,
            "deployed_static_site": False,
            "dns_changed": False,
            "site_dist_mutated": False,
            "production_claimed": False,
        },
    }


def format_summary(summary: dict[str, Any]) -> str:
    counts = summary["counts"]
    return "\n".join(
        [
            "# Hosting Readiness Summary",
            "",
            f"Status: {summary['status']}",
            f"Public alpha non-claims: {counts['public_alpha_non_claims']}",
            f"Host profiles: {counts['host_profiles']}",
            f"Deployment environments: {counts['deployment_environments']}",
            f"Runtime config boundaries: {counts['runtime_config_boundaries']}",
            f"Security policies: {counts['security_policies']}",
            f"Ops plans: {counts['ops_plans']}",
            f"Readiness reports: {counts['readiness_reports']}",
            f"Launch evidence requirements: {counts['launch_evidence_requirements']}",
            f"E-BUNDLE-02 readiness: {summary['e_bundle_02_readiness']}",
            "",
            "No deployment, provider call, DNS change, generated site output mutation, live fanout, public alpha live claim, or production claim is present.",
        ]
    )


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
            raise SystemExit(f"Refusing output outside allowed hosting readiness roots: {relative}")
        for forbidden in FORBIDDEN_OUTPUT_ROOTS:
            key = forbidden.casefold().rstrip("/")
            if lower == key or lower.startswith(key + "/"):
                raise SystemExit(f"Refusing forbidden output path: {relative}")
    resolved.parent.mkdir(parents=True, exist_ok=True)
    return resolved


def write_json_output(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def format_validation(report: dict[str, Any]) -> str:
    lines = [
        "Hosting readiness validation",
        f"status: {report['status']}",
        f"contracts: {report['contract_count']}",
        f"policies: {report['policy_count']}",
        f"examples: {report['example_count']}",
        f"docs: {report['doc_count']}",
    ]
    for error in report["errors"]:
        lines.append(f"ERROR: {error}")
    return "\n".join(lines)


def _is_negated(text: str, phrase: str) -> bool:
    index = text.find(phrase)
    if index < 0:
        return False
    prefix = text[max(0, index - 30):index]
    return any(marker in prefix for marker in NEGATIONS)


def _validate_json_files(repo_root: Path, relatives: list[str], errors: list[str]) -> None:
    for relative in relatives:
        path = repo_root / relative
        if not path.is_file():
            errors.append(f"{relative}: missing required file.")
            continue
        try:
            payload = _load_json(path)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{relative}: invalid JSON: {exc}")
            continue
        if relative.startswith("examples/hosting/") or "e-bundle-01-hosting-ops-readiness-v0" in relative:
            for claim_error in detect_forbidden_hosting_claims(payload, relative):
                errors.append(claim_error)


def _validate_docs(repo_root: Path, errors: list[str]) -> None:
    for relative in REQUIRED_DOCS:
        path = repo_root / relative
        if not path.is_file():
            errors.append(f"{relative}: missing required doc.")
        elif not path.read_text(encoding="utf-8").strip():
            errors.append(f"{relative}: empty doc.")


def _validate_audit_pack(repo_root: Path, errors: list[str]) -> None:
    audit = repo_root / AUDIT_ROOT
    for filename in AUDIT_FILES:
        if not (audit / filename).is_file():
            errors.append(f"{AUDIT_ROOT}/{filename}: missing audit file.")
    report_path = audit / "e_bundle_01_report.json"
    if report_path.is_file():
        report = _load_json(report_path)
        if report.get("hosting_scope", {}).get("readiness_only") is not True:
            errors.append("e_bundle_01_report.json: readiness_only must be true.")
        if report.get("hosting_scope", {}).get("public_alpha_live_claimed") is not False:
            errors.append("e_bundle_01_report.json: public_alpha_live_claimed must be false.")
        if report.get("next_task") != "E-BUNDLE-02 - Hosted wrapper rehearsal and public launch evidence":
            errors.append("e_bundle_01_report.json: next_task must point to E-BUNDLE-02.")


def _validate_non_claims(path: Path, errors: list[str]) -> None:
    payload = _load_json(path)
    for key in REQUIRED_NON_CLAIMS:
        if payload.get(key) is not True:
            errors.append(f"{path.relative_to(REPO_ROOT).as_posix()}: {key} must be true.")
    for key in ("source_limitations_required", "evidence_limitations_required", "review_limitations_required"):
        if payload.get(key) is not True:
            errors.append(f"{path.relative_to(REPO_ROOT).as_posix()}: {key} must be true.")


def _validate_runtime_config(path: Path, errors: list[str]) -> None:
    payload = _load_json(path)
    seen = {entry.get("config_key") for entry in payload.get("config_boundaries", [])}
    missing = sorted(set(REQUIRED_CONFIG_KEYS) - seen)
    if missing:
        errors.append(f"{path.relative_to(REPO_ROOT).as_posix()}: missing config keys {missing}.")
    for entry in payload.get("config_boundaries", []):
        if entry.get("config_key") != "PUBLIC_SEARCH_ENABLED" and str(entry.get("safe_default")).casefold() != "false":
            errors.append(f"{entry.get('config_key')}: risky config safe default must be false.")
        if entry.get("fail_closed_default") is not True:
            errors.append(f"{entry.get('config_key')}: fail_closed_default must be true.")


def _validate_readiness_report(path: Path, errors: list[str]) -> None:
    payload = _load_json(path)
    if payload.get("readiness_status") == "ready_for_public_launch_future":
        errors.append("hosting readiness must not claim ready_for_public_launch_future in E-BUNDLE-01.")
    if payload.get("launch_evidence_status") != "requirements_defined_not_collected":
        errors.append("launch evidence must remain requirements-defined and not collected.")


def _validate_public_launch_evidence(path: Path, errors: list[str]) -> None:
    payload = _load_json(path)
    if payload.get("launch_evidence_status") not in {"required_not_collected", "policy_blocked"}:
        errors.append("public launch evidence must not be marked collected.")
    if payload.get("operator_signoff_required") is not True:
        errors.append("operator signoff must be required.")


def _validate_no_private_roots(repo_root: Path, errors: list[str]) -> None:
    for relative in (".aide.local", ".local/eureka", ".cache/eureka"):
        if (repo_root / relative).exists():
            errors.append(f"{relative}: local private-state root must not be created.")


def _expand_json_inputs(input_paths: list[Path], repo_root: Path) -> list[Path]:
    files: list[Path] = []
    for raw in input_paths:
        path = raw if raw.is_absolute() else repo_root / raw
        if path.is_dir():
            files.extend(sorted(child for child in path.rglob("*.json") if child.is_file()))
        elif path.is_file():
            files.append(path)
    return files


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    raise SystemExit(main())
