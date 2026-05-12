#!/usr/bin/env python3
"""Validate LOCAL-MVP-ITERATION-01 artifacts."""

from __future__ import annotations

import argparse
import json
import re
import tempfile
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]

REQUIRED_OPTIONS = {
    "H2-BUNDLE-01",
    "H3-BUNDLE-01",
    "J1-POLICY-01",
    "K0-BUNDLE-01",
    "L0-BUNDLE-01",
    "PUBLIC-ALPHA-OPERATOR-DEPLOYMENT-APPROVAL-01",
    "MVP-ALPHA-REMEDIATION-01",
}
REQUIRED_CONTRACTS = [
    "control/schemas/audits/audits/local_mvp_iteration_plan.v0.json",
    "contracts/audits/local_mvp_next_wave_option.v0.json",
    "contracts/audits/local_mvp_next_task_decision.v0.json",
    "control/schemas/audits/audits/local_mvp_deployment_deferral.v0.json",
    "control/schemas/audits/audits/local_mvp_expansion_gate.v0.json",
]
REQUIRED_POLICIES = [
    "control/inventory/audits/local_mvp_iteration_policy.json",
    "control/inventory/audits/local_mvp_next_wave_option_policy.json",
    "control/inventory/audits/local_mvp_next_task_decision_policy.json",
    "control/inventory/audits/local_mvp_deployment_deferral_policy.json",
    "control/inventory/audits/local_mvp_expansion_gate_policy.json",
    "control/inventory/audits/local_mvp_truth_policy.json",
    "control/inventory/audits/local_mvp_no_deploy_policy.json",
]
REQUIRED_EXAMPLES = [
    "examples/audits/local_mvp/local_mvp_iteration_plan_v0.json",
    "examples/audits/local_mvp/local_mvp_next_wave_option_h2_v0.json",
    "examples/audits/local_mvp/local_mvp_next_wave_option_h3_v0.json",
    "examples/audits/local_mvp/local_mvp_next_wave_option_j1_deferred_v0.json",
    "examples/audits/local_mvp/local_mvp_next_wave_option_k_deferred_v0.json",
    "examples/audits/local_mvp/local_mvp_next_wave_option_l_deferred_v0.json",
    "examples/audits/local_mvp/local_mvp_deployment_deferral_v0.json",
    "examples/audits/local_mvp/local_mvp_next_task_decision_h2_v0.json",
    "examples/audits/local_mvp/local_mvp_next_task_decision_remediation_v0.json",
    "examples/audits/local_mvp/local_mvp_policy_blocked_iteration_v0.json",
]
REQUIRED_DOCS = [
    "docs/reference/LOCAL_MVP_ITERATION_PLAN_CONTRACT.md",
    "docs/reference/LOCAL_MVP_NEXT_TASK_DECISION_CONTRACT.md",
    "docs/reference/LOCAL_MVP_EXPANSION_GATE_CONTRACT.md",
    "docs/architecture/LOCAL_MVP_ITERATION_MODEL.md",
    "docs/operations/LOCAL_MVP_NEXT_WAVE_SELECTION.md",
    "docs/operations/LOCAL_MVP_DEPLOYMENT_DEFERRAL_POLICY.md",
    "docs/operations/LOCAL_MVP_TO_H2_HANDOFF.md",
    "docs/operations/LOCAL_MVP_RISKY_ACTION_DEFERRAL.md",
    "docs/operations/LOCAL_MVP_AI_SEMANTIC_DEFERRAL.md",
]
REQUIRED_SCRIPTS = [
    "scripts/plan_local_mvp_iteration.py",
    "scripts/select_local_mvp_next_task.py",
    "scripts/check_local_mvp_deployment_deferral.py",
    "scripts/validate_local_mvp_iteration.py",
    "scripts/summarize_local_mvp_iteration.py",
]
AUDIT_ROOT = "control/audits/local-mvp-iteration-01-v0"
AUDIT_FILES = [
    "README.md",
    "local_mvp_iteration_01_report.json",
    "local_mvp_iteration_plan.md",
    "next_wave_option_matrix.md",
    "h2_readiness_review.md",
    "h3_deferral_review.md",
    "j1_risky_action_deferral_review.md",
    "k_semantic_ai_deferral_review.md",
    "l_wider_client_deferral_review.md",
    "deployment_deferral_review.md",
    "recommended_next_task.md",
    "no_deployment_report.md",
    "validation.md",
    "generated/sample_local_mvp_iteration_plan.json",
    "generated/sample_next_wave_option_matrix.json",
    "generated/sample_next_task_decision.json",
    "generated/sample_deployment_deferral.json",
    "generated/sample_local_mvp_summary.md",
]
FORBIDDEN_TRUE_KEYS = {
    "local_iteration_is_launch",
    "selected_next_task_is_approval",
    "public_alpha_live_claimed",
    "production_claimed",
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
    "operator_signoff_inferred",
    "deployment_approval_present",
    "operator_signoff_present",
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
    report = validate_local_mvp_iteration(REPO_ROOT)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(format_validation(report))
    return 0 if report["status"] == "pass" else 1


def validate_local_mvp_iteration(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    _validate_json_files(repo_root, REQUIRED_CONTRACTS + REQUIRED_POLICIES + REQUIRED_EXAMPLES, errors)
    _validate_required_files(repo_root, REQUIRED_DOCS + REQUIRED_SCRIPTS, errors)
    _validate_audit_pack(repo_root, errors)
    _validate_plan(load_json(repo_root / "examples/audits/local_mvp/local_mvp_iteration_plan_v0.json"), errors)
    _validate_decision(load_json(repo_root / "examples/audits/local_mvp/local_mvp_next_task_decision_h2_v0.json"), errors)
    _validate_deferral(load_json(repo_root / "examples/audits/local_mvp/local_mvp_deployment_deferral_v0.json"), errors)
    for relative in REQUIRED_EXAMPLES[1:6]:
        _validate_option(load_json(repo_root / relative), errors)
    _validate_no_private_roots(repo_root, errors)
    return {
        "schema_version": "local_mvp_iteration_validation.v0",
        "status": "fail" if errors else "pass",
        "contract_count": len(REQUIRED_CONTRACTS),
        "policy_count": len(REQUIRED_POLICIES),
        "example_count": len(REQUIRED_EXAMPLES),
        "script_count": len(REQUIRED_SCRIPTS),
        "doc_count": len(REQUIRED_DOCS),
        "errors": errors,
    }


def detect_forbidden_local_mvp_claims(payload: Any, path: str = "$") -> list[str]:
    errors: list[str] = []
    if isinstance(payload, dict):
        for key, value in payload.items():
            child = f"{path}.{key}"
            if key in FORBIDDEN_TRUE_KEYS and value is True:
                errors.append(f"{child}: forbidden local MVP claim is true.")
            errors.extend(detect_forbidden_local_mvp_claims(value, child))
    elif isinstance(payload, list):
        for index, value in enumerate(payload):
            errors.extend(detect_forbidden_local_mvp_claims(value, f"{path}[{index}]"))
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
            raise SystemExit(f"Refusing output outside allowed local MVP audit roots: {relative}")
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
        "Local MVP iteration validation",
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
        if relative.startswith("examples/audits/local_mvp") or relative.startswith(AUDIT_ROOT):
            errors.extend(detect_forbidden_local_mvp_claims(payload, relative))


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
                errors.extend(detect_forbidden_local_mvp_claims(load_json(path), f"{AUDIT_ROOT}/{filename}"))
            except Exception as exc:
                errors.append(f"{AUDIT_ROOT}/{filename}: invalid JSON: {exc}")
    report_path = audit / "local_mvp_iteration_01_report.json"
    if report_path.is_file():
        report = load_json(report_path)
        if report.get("recommended_next_task") != "H2-BUNDLE-01":
            errors.append("audit report must recommend H2-BUNDLE-01 unless remediation is justified.")
        deployment = report.get("deployment_deferral", {})
        if deployment.get("deployment_deferred") is not True:
            errors.append("audit report deployment_deferred must be true.")
        if deployment.get("operator_deployment_approval_present") is not False:
            errors.append("audit report operator deployment approval must be false.")


def _validate_plan(payload: dict[str, Any], errors: list[str]) -> None:
    if payload.get("plan_status") not in {"planning_only", "ready_for_next_local_bundle", "needs_remediation", "blocked", "not_evaluable"}:
        errors.append("plan_status is invalid.")
    options = set(payload.get("available_next_wave_options", []))
    missing = sorted(REQUIRED_OPTIONS - options)
    if missing:
        errors.append(f"iteration plan missing options: {missing}")
    if payload.get("recommended_next_task") != "H2-BUNDLE-01":
        errors.append("iteration plan should recommend H2-BUNDLE-01 for current evidence.")
    if payload.get("blocker_summary"):
        errors.append("current H2 recommendation example should not contain blockers.")
    _validate_deferral(payload.get("deployment_deferral", {}), errors)
    _require_false_boundaries(payload, errors, "iteration plan")


def _validate_option(payload: dict[str, Any], errors: list[str]) -> None:
    if payload.get("option_task_id") == "H2-BUNDLE-01" and payload.get("option_status") != "recommended":
        errors.append("H2 option must be recommended.")
    if payload.get("option_task_id") in {"H3-BUNDLE-01", "J1-POLICY-01", "K0-BUNDLE-01", "L0-BUNDLE-01"} and payload.get("option_status") != "deferred":
        errors.append(f"{payload.get('option_task_id')}: option must be deferred.")
    for key in ("value_assessment", "risk_assessment", "forbidden_actions", "required_gates"):
        if not payload.get(key):
            errors.append(f"{payload.get('option_task_id')}: {key} is required.")
    _require_false_boundaries(payload, errors, f"option {payload.get('option_task_id')}")


def _validate_decision(payload: dict[str, Any], errors: list[str]) -> None:
    if payload.get("selected_next_task") == "PUBLIC-ALPHA-OPERATOR-DEPLOYMENT-APPROVAL-01":
        errors.append("local MVP decision must not route to deployment approval without explicit approval evidence.")
    if payload.get("selected_next_task") != "H2-BUNDLE-01" and payload.get("decision_status") == "selected":
        errors.append("current selected local next task should be H2-BUNDLE-01.")
    for key in ("deployment_allowed_current", "launch_allowed_current"):
        if payload.get(key) is not False:
            errors.append(f"next task decision {key} must be false.")
    _require_false_boundaries(payload, errors, "next task decision")


def _validate_deferral(payload: dict[str, Any], errors: list[str]) -> None:
    if payload.get("deployment_deferred") is not True:
        errors.append("deployment must remain deferred.")
    if payload.get("operator_signoff_present") is not False:
        errors.append("operator_signoff_present must be false for current examples.")
    if payload.get("deployment_approval_present") is not False:
        errors.append("deployment_approval_present must be false for current examples.")
    _require_false_boundaries(payload, errors, "deployment deferral")


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
