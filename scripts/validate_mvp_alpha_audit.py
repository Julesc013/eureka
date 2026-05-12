#!/usr/bin/env python3
"""Validate MVP-ALPHA-AUDIT-01 local readiness artifacts."""

from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]

REQUIRED_TRACKS = ["A", "B", "IA", "H0", "H1", "F", "G", "I", "J0", "D", "C", "E"]
REQUIRED_COMPONENTS = [
    "track_a_representation",
    "track_b_local_foundry",
    "ia_reference_connector",
    "h0_source_os",
    "h1_metadata_wave",
    "track_f_extraction",
    "track_g_search_quality",
    "track_i_pack_quarantine",
    "track_j0_safe_actions",
    "track_d_snapshots_relay",
    "track_c_native_clients",
    "track_e_hosting_readiness",
    "obs_side_lane_status",
]
REQUIRED_CONTRACTS = [
    "control/schemas/audits/audits/mvp_alpha_readiness_audit.v0.json",
    "control/schemas/audits/audits/mvp_alpha_gate_decision.v0.json",
    "control/schemas/audits/audits/mvp_alpha_integration_matrix.v0.json",
    "control/schemas/audits/audits/mvp_alpha_remediation_plan.v0.json",
    "control/schemas/audits/audits/mvp_alpha_operator_review_packet.v0.json",
]
REQUIRED_POLICIES = [
    "control/inventory/audits/mvp_alpha_readiness_policy.json",
    "control/inventory/audits/mvp_alpha_gate_policy.json",
    "control/inventory/audits/mvp_alpha_integration_matrix_policy.json",
    "control/inventory/audits/mvp_alpha_remediation_policy.json",
    "control/inventory/audits/mvp_alpha_operator_review_policy.json",
    "control/inventory/audits/mvp_alpha_truth_policy.json",
    "control/inventory/audits/mvp_alpha_no_deploy_policy.json",
]
REQUIRED_EXAMPLES = [
    "examples/audits/mvp_alpha/mvp_alpha_integration_matrix_v0.json",
    "examples/audits/mvp_alpha/mvp_alpha_readiness_audit_v0.json",
    "examples/audits/mvp_alpha/mvp_alpha_gate_decision_ready_for_operator_review_v0.json",
    "examples/audits/mvp_alpha/mvp_alpha_gate_decision_needs_remediation_v0.json",
    "examples/audits/mvp_alpha/mvp_alpha_remediation_plan_v0.json",
    "examples/audits/mvp_alpha/mvp_alpha_operator_review_packet_v0.json",
    "examples/audits/mvp_alpha/mvp_alpha_policy_blocked_audit_v0.json",
]
REQUIRED_DOCS = [
    "docs/reference/MVP_ALPHA_READINESS_AUDIT_CONTRACT.md",
    "docs/reference/MVP_ALPHA_GATE_DECISION_CONTRACT.md",
    "docs/reference/MVP_ALPHA_OPERATOR_REVIEW_PACKET_CONTRACT.md",
    "docs/architecture/MVP_ALPHA_STACK_MODEL.md",
    "docs/operations/MVP_ALPHA_READINESS_AUDIT.md",
    "docs/operations/MVP_ALPHA_OPERATOR_REVIEW.md",
    "docs/operations/MVP_ALPHA_REMEDIATION_POLICY.md",
    "docs/operations/MVP_ALPHA_NO_DEPLOYMENT_POLICY.md",
]
REQUIRED_SCRIPTS = [
    "scripts/audit_mvp_alpha_readiness.py",
    "scripts/validate_mvp_alpha_audit.py",
    "scripts/summarize_mvp_alpha_readiness.py",
    "scripts/build_mvp_alpha_operator_review_packet.py",
]
AUDIT_ROOT = "control/audits/mvp-alpha-audit-01-local-mvp-readiness-v0"
AUDIT_FILES = [
    "README.md",
    "mvp_alpha_audit_01_report.json",
    "mvp_alpha_integration_matrix.md",
    "track_gate_summary.md",
    "local_mvp_runtime_summary.md",
    "source_connector_summary.md",
    "extraction_search_quality_summary.md",
    "pack_action_snapshot_relay_summary.md",
    "native_hosting_summary.md",
    "unsafe_behavior_block_report.md",
    "public_claim_boundary_report.md",
    "operator_review_packet.md",
    "remediation_plan.md",
    "mvp_alpha_gate_decision.md",
    "validation.md",
    "generated/sample_mvp_alpha_readiness_audit.json",
    "generated/sample_mvp_alpha_integration_matrix.json",
    "generated/sample_mvp_alpha_gate_decision.json",
    "generated/sample_operator_review_packet.json",
    "generated/sample_remediation_plan.json",
    "generated/sample_mvp_alpha_summary.md",
]
FORBIDDEN_TRUE_KEYS = {
    "readiness_audit_is_launch",
    "operator_signoff_inferred",
    "public_alpha_live_claimed",
    "production_claimed",
    "production_readiness_claimed",
    "public_index_mutated",
    "master_index_mutated",
    "source_truth_accepted",
    "evidence_truth_accepted",
    "candidate_truth_accepted",
    "public_truth_created",
    "rights_clearance_claimed",
    "malware_safety_claimed",
    "verified_installability_claimed",
    "changed_public_search_behavior",
    "enabled_hosting",
    "enabled_live_source_fanout",
    "enabled_source_sync",
    "enabled_downloads",
    "enabled_uploads",
    "enabled_accounts",
    "enabled_telemetry",
    "enabled_public_relay",
    "enabled_installers",
    "enabled_execution",
    "enabled_mirroring",
    "enabled_emulation",
    "mutated_site_dist",
    "mutated_public_index",
    "mutated_master_index",
    "deployment_performed",
    "provider_api_called",
    "dns_changed",
    "site_dist_mutated",
    "public_bind_enabled",
    "launch_allowed_current",
    "deployment_allowed_current",
    "public_alpha_live_claim_allowed",
    "production_claim_allowed",
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
    "operator signoff is inferred",
]
NEGATIONS = ["no ", "not ", "must not ", "without ", "does not ", "is not ", "not a ", "remain absent", "not inferred"]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = validate_mvp_alpha_audit(REPO_ROOT)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(format_validation(report))
    return 0 if report["status"] == "pass" else 1


def validate_mvp_alpha_audit(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    _validate_json_files(repo_root, REQUIRED_CONTRACTS + REQUIRED_POLICIES + REQUIRED_EXAMPLES, errors)
    _validate_required_files(repo_root, REQUIRED_DOCS + REQUIRED_SCRIPTS, errors)
    _validate_audit_pack(repo_root, errors)
    _validate_matrix(_load_json(repo_root / "examples/audits/mvp_alpha/mvp_alpha_integration_matrix_v0.json"), errors)
    _validate_readiness_audit(_load_json(repo_root / "examples/audits/mvp_alpha/mvp_alpha_readiness_audit_v0.json"), errors)
    _validate_gate_decision(_load_json(repo_root / "examples/audits/mvp_alpha/mvp_alpha_gate_decision_ready_for_operator_review_v0.json"), errors)
    _validate_gate_decision(_load_json(repo_root / "examples/audits/mvp_alpha/mvp_alpha_gate_decision_needs_remediation_v0.json"), errors)
    _validate_remediation_plan(_load_json(repo_root / "examples/audits/mvp_alpha/mvp_alpha_remediation_plan_v0.json"), errors)
    _validate_operator_packet(_load_json(repo_root / "examples/audits/mvp_alpha/mvp_alpha_operator_review_packet_v0.json"), errors)
    _validate_no_private_roots(repo_root, errors)
    return {
        "schema_version": "mvp_alpha_audit_validation.v0",
        "status": "fail" if errors else "pass",
        "contract_count": len(REQUIRED_CONTRACTS),
        "policy_count": len(REQUIRED_POLICIES),
        "example_count": len(REQUIRED_EXAMPLES),
        "script_count": len(REQUIRED_SCRIPTS),
        "doc_count": len(REQUIRED_DOCS),
        "errors": errors,
    }


def detect_forbidden_mvp_claims(payload: Any, path: str = "$") -> list[str]:
    errors: list[str] = []
    if isinstance(payload, dict):
        for key, value in payload.items():
            child = f"{path}.{key}"
            if key in FORBIDDEN_TRUE_KEYS and value is True:
                errors.append(f"{child}: forbidden MVP readiness claim is true.")
            errors.extend(detect_forbidden_mvp_claims(value, child))
    elif isinstance(payload, list):
        for index, value in enumerate(payload):
            errors.extend(detect_forbidden_mvp_claims(value, f"{path}[{index}]"))
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
        allowed = lower.startswith("examples/audits/") or (lower.startswith("control/audits/") and "/generated/" in lower)
        if not allowed:
            raise SystemExit(f"Refusing output outside allowed MVP audit roots: {relative}")
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
        "MVP alpha audit validation",
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
            payload = _load_json(path)
        except Exception as exc:
            errors.append(f"{relative}: invalid JSON: {exc}")
            continue
        if relative.startswith("examples/audits/") or relative.startswith("control/audits/mvp-alpha-audit-01"):
            errors.extend(detect_forbidden_mvp_claims(payload, relative))


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
                errors.extend(detect_forbidden_mvp_claims(_load_json(path), f"{AUDIT_ROOT}/{filename}"))
            except Exception as exc:
                errors.append(f"{AUDIT_ROOT}/{filename}: invalid JSON: {exc}")
    report_path = audit / "mvp_alpha_audit_01_report.json"
    if report_path.is_file():
        report = _load_json(report_path)
        if report.get("deployment_scope", {}).get("deployment_performed") is not False:
            errors.append("mvp_alpha_audit_01_report.json: deployment_performed must be false.")
        if report.get("gate_decision") not in {"READY_FOR_OPERATOR_REVIEW", "READY_WITH_WARNINGS", "NEEDS_REMEDIATION", "BLOCKED", "FAIL"}:
            errors.append("mvp_alpha_audit_01_report.json: gate_decision is invalid.")


def _validate_matrix(payload: dict[str, Any], errors: list[str]) -> None:
    rows = payload.get("rows", [])
    seen = {row.get("component_id") for row in rows}
    missing = sorted(set(REQUIRED_COMPONENTS) - seen)
    if missing:
        errors.append(f"integration matrix missing rows: {missing}")
    tracks = {row.get("track") for row in rows}
    missing_tracks = sorted(set(REQUIRED_TRACKS) - tracks)
    if missing_tracks:
        errors.append(f"integration matrix missing tracks: {missing_tracks}")
    for row in rows:
        if not row.get("actual_status"):
            errors.append(f"{row.get('component_id')}: actual_status required.")
        if row.get("product_boundary_preserved") is not True:
            errors.append(f"{row.get('component_id')}: product boundary must be preserved.")
        if row.get("truth_boundary_preserved") is not True:
            errors.append(f"{row.get('component_id')}: truth boundary must be preserved.")
        if "blockers" not in row or "warnings" not in row:
            errors.append(f"{row.get('component_id')}: blockers and warnings arrays required.")


def _validate_readiness_audit(payload: dict[str, Any], errors: list[str]) -> None:
    if payload.get("audit_status") not in {"pass", "pass_with_warnings", "needs_remediation", "blocked", "fail", "not_evaluable"}:
        errors.append("readiness audit status is invalid.")
    missing = sorted(set(REQUIRED_TRACKS) - set(payload.get("audited_tracks", [])))
    if missing:
        errors.append(f"readiness audit missing tracks: {missing}")
    if payload.get("audit_status") in {"pass", "pass_with_warnings"} and payload.get("blockers"):
        errors.append("pass/pass_with_warnings audit cannot contain blockers.")
    _require_false_boundaries(payload, errors, "readiness audit")


def _validate_gate_decision(payload: dict[str, Any], errors: list[str]) -> None:
    if payload.get("operator_review_required") is not True:
        errors.append("gate decision must require operator review.")
    for key in ("launch_allowed_current", "deployment_allowed_current", "public_alpha_live_claim_allowed", "production_claim_allowed"):
        if payload.get(key) is not False:
            errors.append(f"gate decision {key} must be false.")
    _require_false_boundaries(payload, errors, "gate decision")


def _validate_remediation_plan(payload: dict[str, Any], errors: list[str]) -> None:
    if "remediation_items" not in payload:
        errors.append("remediation plan must include remediation_items.")
    for item in payload.get("remediation_items", []):
        for key in ("item_id", "owner_or_lane", "suggested_task_id", "action", "validation_required"):
            if key not in item:
                errors.append(f"remediation item missing {key}.")
    _require_false_boundaries(payload, errors, "remediation plan")


def _validate_operator_packet(payload: dict[str, Any], errors: list[str]) -> None:
    if payload.get("review_status") not in {"operator_review_required", "ready_for_operator_review", "needs_remediation", "blocked", "not_evaluable"}:
        errors.append("operator review status is invalid.")
    if not payload.get("required_signoffs"):
        errors.append("operator review packet must list required signoffs.")
    if payload.get("recommended_decision") not in {"READY_FOR_OPERATOR_REVIEW", "READY_WITH_WARNINGS", "NEEDS_REMEDIATION", "BLOCKED", "FAIL"}:
        errors.append("operator review packet recommended decision is invalid.")
    _require_false_boundaries(payload, errors, "operator review packet")


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


def _is_negated(text: str, phrase: str) -> bool:
    index = text.find(phrase)
    if index < 0:
        return False
    prefix = text[max(0, index - 40):index]
    suffix = text[index + len(phrase):index + len(phrase) + 30]
    return any(marker in prefix for marker in NEGATIONS) or any(marker in suffix for marker in NEGATIONS)


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    raise SystemExit(main())
