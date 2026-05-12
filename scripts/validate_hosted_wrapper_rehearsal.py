#!/usr/bin/env python3
"""Validate E-BUNDLE-02 hosted-wrapper rehearsal artifacts without deployment."""

from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

REQUIRED_CONTRACTS = [
    "control/schemas/policies/hosting/hosted_wrapper_rehearsal.v0.json",
    "control/schemas/audits/hosting/hosted_wrapper_smoke_report.v0.json",
    "control/schemas/policies/hosting/public_alpha_smoke_matrix.v0.json",
    "control/schemas/audits/hosting/public_alpha_blocked_request_report.v0.json",
    "control/schemas/audits/hosting/public_alpha_status_report.v0.json",
    "control/schemas/audits/hosting/public_launch_readiness_audit.v0.json",
    "control/schemas/audits/hosting/public_launch_operator_signoff.v0.json",
    "control/schemas/policies/hosting/post_launch_remediation_plan.v0.json",
]
REQUIRED_POLICIES = [
    "control/inventory/hosting/hosted_wrapper_rehearsal_policy.json",
    "control/inventory/hosting/public_alpha_smoke_matrix_policy.json",
    "control/inventory/hosting/public_alpha_blocked_request_policy.json",
    "control/inventory/hosting/public_alpha_status_policy.json",
    "control/inventory/hosting/public_launch_readiness_policy.json",
    "control/inventory/hosting/public_launch_operator_signoff_policy.json",
    "control/inventory/hosting/post_launch_remediation_policy.json",
    "control/inventory/hosting/hosted_wrapper_rehearsal_path_policy.json",
    "control/inventory/hosting/hosted_wrapper_rehearsal_truth_policy.json",
    "control/inventory/hosting/hosted_wrapper_no_deploy_policy.json",
]
REQUIRED_EXAMPLES = [
    "examples/hosting/rehearsal/hosted_wrapper_rehearsal_local_fixture_v0.json",
    "examples/hosting/rehearsal/hosted_wrapper_rehearsal_policy_blocked_v0.json",
    "examples/hosting/rehearsal/hosted_wrapper_smoke_report_v0.json",
    "examples/hosting/smoke/public_alpha_smoke_matrix_v0.json",
    "examples/hosting/smoke/status_smoke_case_v0.json",
    "examples/hosting/smoke/search_smoke_case_v0.json",
    "examples/hosting/smoke/object_smoke_case_v0.json",
    "examples/hosting/smoke/source_smoke_case_v0.json",
    "examples/hosting/smoke/snapshot_smoke_case_v0.json",
    "examples/hosting/smoke/blocked_download_smoke_case_v0.json",
    "examples/hosting/smoke/blocked_upload_smoke_case_v0.json",
    "examples/hosting/smoke/blocked_account_smoke_case_v0.json",
    "examples/hosting/smoke/blocked_live_fanout_smoke_case_v0.json",
    "examples/hosting/blocked_requests/download_blocked_request_report_v0.json",
    "examples/hosting/blocked_requests/upload_blocked_request_report_v0.json",
    "examples/hosting/blocked_requests/account_blocked_request_report_v0.json",
    "examples/hosting/blocked_requests/live_probe_blocked_request_report_v0.json",
    "examples/hosting/blocked_requests/public_index_write_blocked_request_report_v0.json",
    "examples/hosting/blocked_requests/master_index_write_blocked_request_report_v0.json",
    "examples/hosting/status/public_alpha_status_report_local_rehearsal_v0.json",
    "examples/hosting/status/public_alpha_status_report_not_live_v0.json",
    "examples/hosting/status/public_alpha_status_report_policy_blocked_v0.json",
    "examples/hosting/launch/public_launch_readiness_audit_v0.json",
    "examples/hosting/launch/public_launch_operator_signoff_required_v0.json",
    "examples/hosting/launch/public_launch_evidence_packet_required_v0.json",
    "examples/hosting/launch/public_launch_evidence_policy_blocked_v0.json",
    "examples/hosting/launch/post_launch_remediation_plan_v0.json",
]
REQUIRED_DOCS = [
    "docs/reference/HOSTED_WRAPPER_REHEARSAL_CONTRACT.md",
    "docs/reference/PUBLIC_ALPHA_SMOKE_MATRIX_CONTRACT.md",
    "docs/reference/PUBLIC_ALPHA_BLOCKED_REQUEST_REPORT_CONTRACT.md",
    "docs/reference/PUBLIC_ALPHA_STATUS_REPORT_CONTRACT.md",
    "docs/reference/PUBLIC_LAUNCH_READINESS_AUDIT_CONTRACT.md",
    "docs/reference/PUBLIC_LAUNCH_OPERATOR_SIGNOFF_CONTRACT.md",
    "docs/reference/POST_LAUNCH_REMEDIATION_PLAN_CONTRACT.md",
    "docs/architecture/HOSTED_WRAPPER_REHEARSAL_MODEL.md",
    "docs/architecture/PUBLIC_ALPHA_LAUNCH_EVIDENCE_MODEL.md",
    "docs/operations/HOSTED_WRAPPER_REHEARSAL.md",
    "docs/operations/PUBLIC_ALPHA_SMOKE_MATRIX.md",
    "docs/operations/PUBLIC_ALPHA_BLOCKED_REQUESTS.md",
    "docs/operations/PUBLIC_LAUNCH_READINESS_AUDIT.md",
    "docs/operations/POST_LAUNCH_REMEDIATION.md",
    "docs/operations/E_TRACK_COMPLETION_AUDIT.md",
]
REQUIRED_RUNTIME_MODULES = [
    "runtime/hosting/__init__.py",
    "runtime/hosting/config_boundary.py",
    "runtime/hosting/readiness.py",
    "runtime/hosting/smoke_matrix.py",
    "runtime/hosting/blocked_requests.py",
    "runtime/hosting/launch_evidence.py",
    "runtime/hosting/rollback_rehearsal.py",
    "runtime/hosting/summaries.py",
]
REQUIRED_SCRIPTS = [
    "scripts/rehearse_hosted_wrapper.py",
    "scripts/run_public_alpha_smoke_matrix.py",
    "scripts/check_public_launch_evidence.py",
    "scripts/check_public_alpha_blocked_requests.py",
    "scripts/audit_public_alpha_readiness.py",
    "scripts/validate_hosted_wrapper_rehearsal.py",
    "scripts/summarize_public_alpha_readiness.py",
]
AUDIT_ROOT = "control/audits/e-bundle-02-hosted-wrapper-rehearsal-v0"
AUDIT_FILES = [
    "README.md",
    "e_bundle_02_report.json",
    "hosted_wrapper_rehearsal_summary.md",
    "public_alpha_smoke_matrix_report.md",
    "public_alpha_blocked_request_report.md",
    "public_alpha_status_report.md",
    "public_launch_evidence_report.md",
    "public_launch_readiness_audit.md",
    "rollback_rehearsal_report.md",
    "no_deployment_report.md",
    "mvp_alpha_integration_summary.md",
    "next_phase_recommendation.md",
    "validation.md",
]
FORBIDDEN_TRUE_KEYS = {
    "deployment_performed",
    "provider_api_called",
    "public_alpha_live_claimed",
    "production_claimed",
    "public_alpha_live",
    "production_live",
    "downloads_enabled",
    "uploads_enabled",
    "accounts_enabled",
    "telemetry_enabled",
    "live_fanout_enabled",
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
    "public_index_mutated",
    "master_index_mutated",
    "rights_clearance_claimed",
    "malware_safety_claimed",
    "verified_installability_claimed",
    "deployed_backend",
    "deployed_static_site",
    "dns_changed",
    "site_dist_mutated",
    "public_bind_used",
    "public_bind_enabled",
    "external_call_performed",
}
FORBIDDEN_OUTPUT_ROOTS = [
    "site/dist",
    "data/public_index",
    "data/master_index",
    "master_index",
    "runtime",
    "contracts",
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
    "provider token",
    "custom domain configured",
]
NEGATIONS = ["no ", "not ", "must not ", "without ", "does not ", "is not ", "not a ", "forbidden "]
REQUIRED_SMOKE_CASES = [
    "status",
    "search_fixture",
    "object_fixture",
    "source_fixture",
    "snapshot_fixture",
    "action_manifest_fixture",
    "blocked_download",
    "blocked_upload",
    "blocked_account",
    "blocked_live_probe",
    "blocked_public_index_write",
    "blocked_master_index_write",
    "non_claims_page_or_doc",
    "rate_limit_policy",
    "kill_switch_policy",
    "secret_scan_policy",
]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = validate_hosted_wrapper_rehearsal(REPO_ROOT)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(format_validation(report))
    return 0 if report["status"] == "pass" else 1


def validate_hosted_wrapper_rehearsal(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    _validate_json_files(repo_root, REQUIRED_CONTRACTS + REQUIRED_POLICIES + REQUIRED_EXAMPLES, errors)
    _validate_required_files(repo_root, REQUIRED_DOCS + REQUIRED_RUNTIME_MODULES + REQUIRED_SCRIPTS, errors)
    _validate_audit_pack(repo_root, errors)
    _validate_rehearsal(_load_json(repo_root / "examples/hosting/rehearsal/hosted_wrapper_rehearsal_local_fixture_v0.json"), errors)
    _validate_smoke_matrix(_load_json(repo_root / "examples/hosting/smoke/public_alpha_smoke_matrix_v0.json"), errors)
    _validate_blocked_requests(repo_root / "examples/hosting/blocked_requests", errors)
    _validate_status_reports(repo_root / "examples/hosting/status", errors)
    _validate_launch_evidence(_load_json(repo_root / "examples/hosting/launch/public_launch_evidence_packet_required_v0.json"), errors)
    _validate_readiness_audit(_load_json(repo_root / "examples/hosting/launch/public_launch_readiness_audit_v0.json"), errors)
    _validate_no_private_roots(repo_root, errors)
    _validate_runtime_imports(errors)
    return {
        "schema_version": "hosted_wrapper_rehearsal_validation.v0",
        "status": "fail" if errors else "pass",
        "contract_count": len(REQUIRED_CONTRACTS),
        "policy_count": len(REQUIRED_POLICIES),
        "example_count": len(REQUIRED_EXAMPLES),
        "runtime_module_count": len(REQUIRED_RUNTIME_MODULES),
        "script_count": len(REQUIRED_SCRIPTS),
        "doc_count": len(REQUIRED_DOCS),
        "errors": errors,
    }


def detect_forbidden_rehearsal_claims(payload: Any, path: str = "$") -> list[str]:
    errors: list[str] = []
    if isinstance(payload, dict):
        for key, value in payload.items():
            child = f"{path}.{key}"
            if key in FORBIDDEN_TRUE_KEYS and value is True:
                errors.append(f"{child}: forbidden rehearsal claim is true.")
            errors.extend(detect_forbidden_rehearsal_claims(value, child))
    elif isinstance(payload, list):
        for index, value in enumerate(payload):
            errors.extend(detect_forbidden_rehearsal_claims(value, f"{path}[{index}]"))
    elif isinstance(payload, str):
        lowered = payload.casefold()
        for pattern in SECRET_VALUE_PATTERNS:
            if pattern.search(payload):
                errors.append(f"{path}: secret-like value is forbidden.")
        for phrase in FORBIDDEN_PHRASES:
            if phrase in lowered and not _is_negated(lowered, phrase):
                errors.append(f"{path}: forbidden positive claim phrase '{phrase}'.")
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
            raise SystemExit(f"Refusing output outside allowed hosted wrapper roots: {relative}")
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
        "Hosted wrapper rehearsal validation",
        f"status: {report['status']}",
        f"contracts: {report['contract_count']}",
        f"policies: {report['policy_count']}",
        f"examples: {report['example_count']}",
        f"runtime modules: {report['runtime_module_count']}",
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
            payload = _load_json(path)
        except Exception as exc:
            errors.append(f"{relative}: invalid JSON: {exc}")
            continue
        if relative.startswith("examples/hosting/") or "e-bundle-02-hosted-wrapper-rehearsal-v0" in relative:
            errors.extend(detect_forbidden_rehearsal_claims(payload, relative))


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
        if not (audit / filename).is_file():
            errors.append(f"{AUDIT_ROOT}/{filename}: missing audit file.")
    report_path = audit / "e_bundle_02_report.json"
    if report_path.is_file():
        report = _load_json(report_path)
        if report.get("rehearsal_scope", {}).get("local_fixture_rehearsal_enabled") is not True:
            errors.append("e_bundle_02_report.json: local fixture rehearsal must be enabled.")
        if report.get("next_task") != "MVP-ALPHA-AUDIT-01 - End-to-end local MVP readiness audit":
            errors.append("e_bundle_02_report.json: next_task must point to MVP-ALPHA-AUDIT-01.")
        errors.extend(detect_forbidden_rehearsal_claims(report, "e_bundle_02_report.json"))


def _validate_rehearsal(payload: dict[str, Any], errors: list[str]) -> None:
    scope = payload.get("rehearsal_scope", {})
    for key in ("deployment_performed", "provider_api_called", "public_alpha_live_claimed", "production_claimed"):
        if scope.get(key) is not False:
            errors.append(f"hosted wrapper rehearsal scope {key} must be false.")
    if payload.get("rehearsal_status") not in {"local_fixture_rehearsal", "example_only", "loopback_rehearsal"}:
        errors.append("local rehearsal example must have a local/example status.")


def _validate_smoke_matrix(payload: dict[str, Any], errors: list[str]) -> None:
    seen = {case.get("case_kind") for case in payload.get("smoke_cases", [])}
    missing = sorted(set(REQUIRED_SMOKE_CASES) - seen)
    if missing:
        errors.append(f"smoke matrix missing cases: {missing}")
    if payload.get("live_url_required_current") is not False:
        errors.append("smoke matrix must not require live URL currently.")
    for case in payload.get("smoke_cases", []):
        if case.get("external_call_performed") is True:
            errors.append(f"{case.get('case_kind')}: external call must be false.")


def _validate_blocked_requests(root: Path, errors: list[str]) -> None:
    for path in sorted(root.glob("*.json")):
        payload = _load_json(path)
        if payload.get("blocked") is not True:
            errors.append(f"{path.relative_to(REPO_ROOT).as_posix()}: blocked must be true.")
        if not payload.get("safe_alternative"):
            errors.append(f"{path.relative_to(REPO_ROOT).as_posix()}: safe alternative required.")


def _validate_status_reports(root: Path, errors: list[str]) -> None:
    for path in sorted(root.glob("*.json")):
        payload = _load_json(path)
        for key in ("public_alpha_live", "production_live", "downloads_enabled", "uploads_enabled", "accounts_enabled", "telemetry_enabled", "live_fanout_enabled"):
            if payload.get(key) is not False:
                errors.append(f"{path.relative_to(REPO_ROOT).as_posix()}: {key} must be false.")


def _validate_launch_evidence(payload: dict[str, Any], errors: list[str]) -> None:
    if payload.get("operator_signoff_required") is not True:
        errors.append("public launch evidence must require operator signoff.")
    if payload.get("launch_evidence_status") in {"collected", "ready_for_launch"}:
        errors.append("public launch evidence must not be marked collected or launch ready.")


def _validate_readiness_audit(payload: dict[str, Any], errors: list[str]) -> None:
    if payload.get("readiness_status") == "ready_for_public_alpha_future" and payload.get("operator_signoff_required") is True:
        errors.append("audit cannot be ready for public alpha while signoff is required.")
    if not payload.get("missing_evidence"):
        errors.append("audit must keep missing evidence recorded.")


def _validate_runtime_imports(errors: list[str]) -> None:
    try:
        from runtime.hosting import blocked_requests, config_boundary, launch_evidence, readiness, rollback_rehearsal, smoke_matrix, summaries  # noqa: F401
    except Exception as exc:
        errors.append(f"runtime hosting modules failed to import: {exc}")


def _validate_no_private_roots(repo_root: Path, errors: list[str]) -> None:
    for relative in (".aide.local", ".local/eureka", ".cache/eureka"):
        if (repo_root / relative).exists():
            errors.append(f"{relative}: local private-state root must not be created.")


def _is_negated(text: str, phrase: str) -> bool:
    index = text.find(phrase)
    if index < 0:
        return False
    prefix = text[max(0, index - 30):index]
    return any(marker in prefix for marker in NEGATIONS)


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    raise SystemExit(main())
