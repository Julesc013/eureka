#!/usr/bin/env python3
"""Validate MVP-ALPHA-OPERATOR-REVIEW-01 artifacts."""

from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]

DECISION_OPTIONS = {
    "approve_local_only_continuation",
    "approve_public_alpha_deployment_planning_only",
    "approve_operator_supervised_launch_future",
    "request_remediation",
    "block_launch",
    "defer_launch",
    "not_evaluable",
}
NEXT_TASK_MAPPING = {
    "approve_local_only_continuation": "LOCAL-MVP-ITERATION-01",
    "approve_public_alpha_deployment_planning_only": "PUBLIC-ALPHA-DEPLOYMENT-PLAN-01",
    "approve_operator_supervised_launch_future": "PUBLIC-ALPHA-LAUNCH-PREP-01",
    "request_remediation": "MVP-ALPHA-REMEDIATION-01",
    "block_launch": "MVP-ALPHA-BLOCKED-01",
    "defer_launch": "LOCAL-MVP-ITERATION-01",
    "not_evaluable": "LOCAL-MVP-ITERATION-01",
}
FORBIDDEN_CLAIMS = {
    "production_ready",
    "public_alpha_live",
    "exhaustive_index",
    "global_search_complete",
    "rights_cleared",
    "malware_safe",
    "installability_verified",
    "app_store",
    "downloader",
    "upload_service",
    "account_service",
    "telemetry_enabled",
    "live_source_fanout_enabled",
    "public_index_mutated",
    "master_index_mutated",
}
REQUIRED_CONTRACTS = [
    "contracts/audits/mvp_alpha_operator_decision.v0.json",
    "contracts/audits/mvp_alpha_operator_signoff_packet.v0.json",
    "contracts/audits/mvp_alpha_launch_blocker_register.v0.json",
    "contracts/audits/mvp_alpha_launch_decision_options.v0.json",
    "contracts/audits/mvp_alpha_public_claim_review.v0.json",
    "contracts/audits/mvp_alpha_operator_next_task.v0.json",
]
REQUIRED_POLICIES = [
    "control/inventory/audits/mvp_alpha_operator_decision_policy.json",
    "control/inventory/audits/mvp_alpha_operator_signoff_policy.json",
    "control/inventory/audits/mvp_alpha_launch_blocker_policy.json",
    "control/inventory/audits/mvp_alpha_launch_decision_options_policy.json",
    "control/inventory/audits/mvp_alpha_public_claim_review_policy.json",
    "control/inventory/audits/mvp_alpha_operator_next_task_policy.json",
    "control/inventory/audits/mvp_alpha_operator_review_truth_policy.json",
    "control/inventory/audits/mvp_alpha_operator_review_no_deploy_policy.json",
]
REQUIRED_EXAMPLES = [
    "examples/audits/mvp_alpha_operator/operator_decision_request_v0.json",
    "examples/audits/mvp_alpha_operator/operator_decision_approve_planning_only_v0.json",
    "examples/audits/mvp_alpha_operator/operator_decision_request_remediation_v0.json",
    "examples/audits/mvp_alpha_operator/operator_decision_block_launch_v0.json",
    "examples/audits/mvp_alpha_operator/operator_signoff_packet_required_v0.json",
    "examples/audits/mvp_alpha_operator/operator_signoff_packet_unsigned_v0.json",
    "examples/audits/mvp_alpha_operator/launch_blocker_register_v0.json",
    "examples/audits/mvp_alpha_operator/public_claim_review_v0.json",
    "examples/audits/mvp_alpha_operator/operator_next_task_planning_v0.json",
    "examples/audits/mvp_alpha_operator/operator_next_task_remediation_v0.json",
    "examples/audits/mvp_alpha_operator/policy_blocked_operator_review_v0.json",
]
REQUIRED_DOCS = [
    "docs/reference/MVP_ALPHA_OPERATOR_DECISION_CONTRACT.md",
    "docs/reference/MVP_ALPHA_OPERATOR_SIGNOFF_PACKET_CONTRACT.md",
    "docs/reference/MVP_ALPHA_LAUNCH_BLOCKER_REGISTER_CONTRACT.md",
    "docs/reference/MVP_ALPHA_PUBLIC_CLAIM_REVIEW_CONTRACT.md",
    "docs/operations/MVP_ALPHA_OPERATOR_DECISION.md",
    "docs/operations/MVP_ALPHA_LAUNCH_DECISION_OPTIONS.md",
    "docs/operations/MVP_ALPHA_LAUNCH_BLOCKERS.md",
    "docs/operations/MVP_ALPHA_PUBLIC_CLAIM_REVIEW.md",
    "docs/operations/MVP_ALPHA_OPERATOR_SIGNOFF_NO_INFERENCE_POLICY.md",
    "docs/operations/MVP_ALPHA_TO_DEPLOYMENT_HANDOFF.md",
]
REQUIRED_SCRIPTS = [
    "scripts/build_mvp_alpha_decision_packet.py",
    "scripts/check_mvp_alpha_operator_signoff.py",
    "scripts/check_mvp_alpha_public_claims.py",
    "scripts/route_mvp_alpha_next_task.py",
    "scripts/validate_mvp_alpha_operator_review.py",
    "scripts/summarize_mvp_alpha_operator_review.py",
]
AUDIT_ROOT = "control/audits/mvp-alpha-operator-review-01-v0"
AUDIT_FILES = [
    "README.md",
    "mvp_alpha_operator_review_01_report.json",
    "operator_decision_packet.md",
    "evidence_summary_for_operator.md",
    "public_claim_review.md",
    "launch_blocker_register.md",
    "risk_register.md",
    "remediation_options.md",
    "operator_signoff_template.md",
    "recommended_next_task.md",
    "no_deployment_report.md",
    "validation.md",
    "generated/sample_operator_decision_packet.json",
    "generated/sample_operator_signoff_packet.json",
    "generated/sample_launch_blocker_register.json",
    "generated/sample_public_claim_review.json",
    "generated/sample_operator_next_task.json",
    "generated/sample_operator_review_summary.md",
]
FORBIDDEN_TRUE_KEYS = {
    "operator_review_is_launch",
    "operator_signoff_inferred",
    "public_alpha_live_claimed",
    "production_claimed",
    "public_index_mutated",
    "master_index_mutated",
    "source_truth_accepted",
    "evidence_truth_accepted",
    "candidate_truth_accepted",
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
    "explicit_operator_approval",
    "deployment_performed",
    "provider_api_called",
    "dns_changed",
    "site_dist_mutated",
    "public_bind_enabled",
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
    report = validate_mvp_alpha_operator_review(REPO_ROOT)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(format_validation(report))
    return 0 if report["status"] == "pass" else 1


def validate_mvp_alpha_operator_review(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    _validate_json_files(repo_root, REQUIRED_CONTRACTS + REQUIRED_POLICIES + REQUIRED_EXAMPLES, errors)
    _validate_required_files(repo_root, REQUIRED_DOCS + REQUIRED_SCRIPTS, errors)
    _validate_audit_pack(repo_root, errors)
    _validate_operator_decision(load_json(repo_root / "examples/audits/mvp_alpha_operator/operator_decision_request_v0.json"), errors)
    _validate_operator_decision(load_json(repo_root / "examples/audits/mvp_alpha_operator/operator_decision_approve_planning_only_v0.json"), errors)
    _validate_signoff_packet(load_json(repo_root / "examples/audits/mvp_alpha_operator/operator_signoff_packet_unsigned_v0.json"), errors)
    _validate_public_claim_review(load_json(repo_root / "examples/audits/mvp_alpha_operator/public_claim_review_v0.json"), errors)
    _validate_blocker_register(load_json(repo_root / "examples/audits/mvp_alpha_operator/launch_blocker_register_v0.json"), errors)
    _validate_next_task(load_json(repo_root / "examples/audits/mvp_alpha_operator/operator_next_task_planning_v0.json"), errors)
    _validate_no_private_roots(repo_root, errors)
    return {
        "schema_version": "mvp_alpha_operator_review_validation.v0",
        "status": "fail" if errors else "pass",
        "contract_count": len(REQUIRED_CONTRACTS),
        "policy_count": len(REQUIRED_POLICIES),
        "example_count": len(REQUIRED_EXAMPLES),
        "script_count": len(REQUIRED_SCRIPTS),
        "doc_count": len(REQUIRED_DOCS),
        "errors": errors,
    }


def detect_forbidden_operator_review_claims(payload: Any, path: str = "$") -> list[str]:
    errors: list[str] = []
    if isinstance(payload, dict):
        for key, value in payload.items():
            child = f"{path}.{key}"
            if key in FORBIDDEN_TRUE_KEYS and value is True:
                errors.append(f"{child}: forbidden operator-review claim is true.")
            if key in FORBIDDEN_CLAIMS and value is True:
                errors.append(f"{child}: forbidden public claim is true.")
            errors.extend(detect_forbidden_operator_review_claims(value, child))
    elif isinstance(payload, list):
        for index, value in enumerate(payload):
            errors.extend(detect_forbidden_operator_review_claims(value, f"{path}[{index}]"))
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
        allowed = lower.startswith("examples/audits/") or (lower.startswith("control/audits/") and "/generated/" in lower)
        if not allowed:
            raise SystemExit(f"Refusing output outside allowed operator review roots: {relative}")
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
        "MVP alpha operator review validation",
        f"status: {report['status']}",
        f"contracts: {report['contract_count']}",
        f"policies: {report['policy_count']}",
        f"examples: {report['example_count']}",
        f"scripts: {report['script_count']}",
        f"docs: {report['doc_count']}",
    ]
    lines.extend(f"ERROR: {error}" for error in report["errors"])
    return "\n".join(lines)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


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
        if relative.startswith("examples/audits/") or relative.startswith(AUDIT_ROOT):
            errors.extend(detect_forbidden_operator_review_claims(payload, relative))


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
                errors.extend(detect_forbidden_operator_review_claims(load_json(path), f"{AUDIT_ROOT}/{filename}"))
            except Exception as exc:
                errors.append(f"{AUDIT_ROOT}/{filename}: invalid JSON: {exc}")
    report_path = audit / "mvp_alpha_operator_review_01_report.json"
    if report_path.is_file():
        report = load_json(report_path)
        scope = report.get("operator_review_scope", {})
        for key in ("operator_signoff_inferred", "deployment_allowed_current", "launch_allowed_current", "public_alpha_live_claimed", "production_claimed"):
            if scope.get(key) is not False:
                errors.append(f"mvp_alpha_operator_review_01_report.json: operator_review_scope.{key} must be false.")


def _validate_operator_decision(payload: dict[str, Any], errors: list[str]) -> None:
    if payload.get("selected_decision") not in DECISION_OPTIONS:
        errors.append("operator decision selected_decision is invalid.")
    if set(payload.get("decision_options", [])) != DECISION_OPTIONS:
        errors.append("operator decision must include the full decision option set.")
    for key in ("explicit_operator_approval", "launch_allowed_current", "deployment_allowed_current"):
        if payload.get(key) is not False:
            errors.append(f"operator decision {key} must be false.")
    _require_false_boundaries(payload, errors, "operator decision")


def _validate_signoff_packet(payload: dict[str, Any], errors: list[str]) -> None:
    if payload.get("signoff_status") in {"signed_future"}:
        errors.append("current examples must not be signed.")
    if payload.get("signed_at_future") is not None:
        errors.append("unsigned signoff packet must not include signed_at_future.")
    if payload.get("signature_or_confirmation_future") is not None:
        errors.append("unsigned signoff packet must not include signature_or_confirmation_future.")
    if not payload.get("required_acknowledgements"):
        errors.append("signoff packet must list acknowledgements.")
    _require_false_boundaries(payload, errors, "signoff packet")


def _validate_public_claim_review(payload: dict[str, Any], errors: list[str]) -> None:
    missing = sorted(FORBIDDEN_CLAIMS - set(payload.get("forbidden_claims", [])))
    if missing:
        errors.append(f"public claim review missing forbidden claims: {missing}")
    if payload.get("unsafe_claim_findings"):
        errors.append("public claim review must not include unsafe findings in current examples.")
    _require_false_boundaries(payload, errors, "public claim review")


def _validate_blocker_register(payload: dict[str, Any], errors: list[str]) -> None:
    for key in ("launch_blockers", "deployment_blockers", "operator_gated_items"):
        if not payload.get(key):
            errors.append(f"blocker register must include {key}.")
    _require_false_boundaries(payload, errors, "blocker register")


def _validate_next_task(payload: dict[str, Any], errors: list[str]) -> None:
    if payload.get("next_task_id") not in set(NEXT_TASK_MAPPING.values()):
        errors.append("next task id is not one of the mapped next tasks.")
    if not payload.get("next_task_forbidden_actions"):
        errors.append("next task must list forbidden actions.")


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
