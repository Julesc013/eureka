#!/usr/bin/env python3
"""Validate Connector Approval and Runtime Planning Audit v0 artifacts."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
AUDIT_DIR = REPO_ROOT / "control" / "audits" / "connector-approval-runtime-planning-audit-v0"
REPORT_PATH = AUDIT_DIR / "connector_approval_runtime_planning_audit_report.json"
INVENTORY_PATH = REPO_ROOT / "control" / "inventory" / "connectors" / "connector_approval_runtime_planning_status.json"
DOC_PATH = REPO_ROOT / "docs" / "operations" / "CONNECTOR_APPROVAL_RUNTIME_PLANNING_AUDIT.md"

CONNECTORS = {
    "internet_archive_metadata",
    "wayback_cdx_memento",
    "github_releases",
    "pypi_metadata",
    "npm_metadata",
    "software_heritage",
}

CLASSIFICATIONS = {
    "approval_pack_missing",
    "approval_pack_present",
    "approval_pending",
    "approval_complete_future",
    "contract_only",
    "planning_only",
    "runtime_plan_missing",
    "runtime_plan_present",
    "local_dry_run_ready_after_operator_approval",
    "source_sync_worker_ready_after_operator_approval",
    "operator_gated",
    "approval_gated",
    "policy_gated",
    "dependency_gated",
    "blocked",
    "disabled",
    "implemented_local_dry_run",
    "implemented_runtime",
    "unexpected_runtime_or_live_integration",
}

REQUIRED_FILES = {
    "README.md",
    "EXECUTIVE_SUMMARY.md",
    "CONNECTOR_STATUS_MATRIX.md",
    "APPROVAL_PACK_STATUS.md",
    "RUNTIME_PLANNING_STATUS.md",
    "SOURCE_POLICY_GATE_STATUS.md",
    "USER_AGENT_CONTACT_RATE_LIMIT_STATUS.md",
    "TOKEN_AUTH_GATE_STATUS.md",
    "IDENTITY_PRIVACY_GATE_STATUS.md",
    "SOURCE_CACHE_EVIDENCE_LEDGER_DEPENDENCY_STATUS.md",
    "PUBLIC_SEARCH_BOUNDARY_STATUS.md",
    "RUNTIME_IMPLEMENTATION_STATUS.md",
    "MUTATION_BOUNDARY_STATUS.md",
    "CONNECTOR_BY_CONNECTOR_REVIEW.md",
    "INTERNET_ARCHIVE_METADATA_REVIEW.md",
    "WAYBACK_CDX_MEMENTO_REVIEW.md",
    "GITHUB_RELEASES_REVIEW.md",
    "PYPI_METADATA_REVIEW.md",
    "NPM_METADATA_REVIEW.md",
    "SOFTWARE_HERITAGE_REVIEW.md",
    "OPERATOR_ACTIONS_REQUIRED.md",
    "APPROVAL_GATED_ACTIONS.md",
    "DO_NOT_IMPLEMENT_YET.md",
    "COMMAND_RESULTS.md",
    "REMAINING_BLOCKERS.md",
    "NEXT_STEPS.md",
    "connector_approval_runtime_planning_audit_report.json",
}

REPORT_TRUE_FIELDS = {"audit_only"}

REPORT_FALSE_FIELDS = {
    "connector_runtime_implemented_by_this_milestone",
    "live_connector_runtime_enabled",
    "public_search_connector_fanout_enabled",
    "external_calls_performed",
    "live_source_called",
    "credentials_configured",
    "tokens_enabled",
    "downloads_enabled",
    "installs_enabled",
    "execution_enabled",
    "source_cache_mutated",
    "evidence_ledger_mutated",
    "candidate_index_mutated",
    "public_index_mutated",
    "local_index_mutated",
    "master_index_mutated",
    "deployment_performed",
    "telemetry_enabled",
    "accounts_enabled",
}

INVENTORY_FALSE_FIELDS = {
    "live_connector_runtime_enabled",
    "public_search_connector_fanout_enabled",
    "external_calls_performed",
    "credentials_configured",
    "tokens_enabled",
    "downloads_enabled",
    "installs_enabled",
    "execution_enabled",
    "source_cache_authoritative_writes_enabled",
    "evidence_ledger_authoritative_writes_enabled",
    "candidate_index_mutation_enabled",
    "public_index_mutation_enabled",
    "master_index_mutation_enabled",
}

MATRIX_CLASSIFICATION_FIELDS = {
    "approval_pack_status",
    "connector_contract_status",
    "connector_inventory_status",
    "runtime_planning_status",
    "readiness_decision",
    "source_policy_gate",
    "user_agent_contact_gate",
    "rate_limit_timeout_circuit_breaker_gate",
    "token_auth_gate",
    "identity_privacy_gate",
    "source_cache_dependency",
    "evidence_ledger_dependency",
    "source_sync_dependency",
    "public_search_boundary",
    "runtime_implementation_status",
    "mutation_status",
}

MATRIX_FALSE_FIELDS = {
    "live_calls_enabled",
    "downloads_enabled",
    "install_execute_enabled",
}


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def check_false(data: Mapping[str, Any], fields: set[str], prefix: str, errors: list[str]) -> None:
    for field in sorted(fields):
        if data.get(field) is not False:
            errors.append(f"{prefix}.{field} must be false")


def check_true(data: Mapping[str, Any], fields: set[str], prefix: str, errors: list[str]) -> None:
    for field in sorted(fields):
        if data.get(field) is not True:
            errors.append(f"{prefix}.{field} must be true")


def require_phrases(path: Path, phrases: Sequence[str], errors: list[str], label: str | None = None) -> str:
    if not path.exists():
        errors.append(f"missing required artifact: {display_path(path)}")
        return ""
    text = path.read_text(encoding="utf-8")
    folded = text.casefold()
    for phrase in phrases:
        if phrase.casefold() not in folded:
            errors.append(f"{label or path.name} missing required phrase: {phrase}")
    return text


def scan_sensitive_text(text: str, label: str, errors: list[str]) -> None:
    if re.search(r"\b[A-Za-z]:\\+(?:users|documents|downloads|desktop|projects|private|temp|windows)\\+", text, re.I):
        errors.append(f"{label} contains a prohibited private absolute path")
    if re.search(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", text, re.I):
        errors.append(f"{label} contains an email/contact value")
    if re.search(r"https?://[^\s/]*@|\b(?:file|data|javascript):", text, re.I):
        errors.append(f"{label} contains a credentialed, file, data, or javascript URL")


def validate_matrix(matrix: Mapping[str, Any], errors: list[str], prefix: str = "report.connector_status_matrix") -> None:
    if set(matrix.keys()) != CONNECTORS:
        errors.append(f"{prefix} must contain exactly the six first-wave connectors")
        return
    for connector_id in sorted(CONNECTORS):
        row = matrix.get(connector_id)
        if not isinstance(row, Mapping):
            errors.append(f"{prefix}.{connector_id} must be an object")
            continue
        if row.get("connector_id") != connector_id:
            errors.append(f"{prefix}.{connector_id}.connector_id must be {connector_id}")
        for field in sorted(MATRIX_CLASSIFICATION_FIELDS):
            value = row.get(field)
            if value not in CLASSIFICATIONS:
                errors.append(f"{prefix}.{connector_id}.{field} has invalid classification {value!r}")
        check_false(row, MATRIX_FALSE_FIELDS, f"{prefix}.{connector_id}", errors)
        if row.get("approval_pack_status") != "approval_pack_present":
            errors.append(f"{prefix}.{connector_id}.approval_pack_status must be approval_pack_present")
        if row.get("runtime_planning_status") != "runtime_plan_present":
            errors.append(f"{prefix}.{connector_id}.runtime_planning_status must be runtime_plan_present")
        if row.get("readiness_decision") != "approval_gated":
            errors.append(f"{prefix}.{connector_id}.readiness_decision must be approval_gated")
        if row.get("public_search_boundary") != "disabled":
            errors.append(f"{prefix}.{connector_id}.public_search_boundary must be disabled")
        if row.get("mutation_status") != "disabled":
            errors.append(f"{prefix}.{connector_id}.mutation_status must be disabled")


def validate_report(report: Mapping[str, Any], errors: list[str]) -> None:
    values = report.get("classification_values")
    if set(values or []) != CLASSIFICATIONS:
        errors.append("report.classification_values must exactly match allowed classifications")
    matrix = report.get("connector_status_matrix")
    if not isinstance(matrix, Mapping):
        errors.append("report.connector_status_matrix must be an object")
    else:
        validate_matrix(matrix, errors)
    check_true(report, REPORT_TRUE_FIELDS, "report", errors)
    check_false(report, REPORT_FALSE_FIELDS, "report", errors)

    required_objects = (
        "approval_pack_status",
        "runtime_planning_status",
        "source_policy_gate_status",
        "user_agent_contact_rate_limit_status",
        "token_auth_gate_status",
        "identity_privacy_gate_status",
        "source_cache_evidence_ledger_dependency_status",
        "public_search_boundary_status",
        "runtime_implementation_status",
        "mutation_boundary_status",
        "connector_by_connector_review",
    )
    for key in required_objects:
        if not isinstance(report.get(key), Mapping):
            errors.append(f"report.{key} must be an object")

    if report.get("approval_pack_status", {}).get("connector_approved_now") is not False:
        errors.append("report.approval_pack_status.connector_approved_now must be false")
    if report.get("runtime_planning_status", {}).get("runtime_connector_implemented") is not False:
        errors.append("report.runtime_planning_status.runtime_connector_implemented must be false")
    if report.get("public_search_boundary_status", {}).get("public_search_connector_fanout_enabled") is not False:
        errors.append("report.public_search_boundary_status.public_search_connector_fanout_enabled must be false")
    if report.get("source_cache_evidence_ledger_dependency_status", {}).get("connector_runtime_may_write_now") is not False:
        errors.append("report.source_cache_evidence_ledger_dependency_status.connector_runtime_may_write_now must be false")
    if report.get("runtime_implementation_status", {}).get("unexpected_runtime_or_live_integration_found") is not False:
        errors.append("report.runtime_implementation_status.unexpected_runtime_or_live_integration_found must be false")


def validate_inventory(inventory: Mapping[str, Any], errors: list[str]) -> None:
    if inventory.get("status") != "audited":
        errors.append("inventory.status must be audited")
    connectors = inventory.get("connectors")
    if not isinstance(connectors, Mapping) or set(connectors.keys()) != CONNECTORS:
        errors.append("inventory.connectors must contain exactly the six first-wave connectors")
    else:
        for connector_id, status in connectors.items():
            if status not in CLASSIFICATIONS:
                errors.append(f"inventory.connectors.{connector_id} has invalid classification {status!r}")
            if status != "approval_gated":
                errors.append(f"inventory.connectors.{connector_id} must be approval_gated")
    if inventory.get("aggregate_status") != "approval_gated":
        errors.append("inventory.aggregate_status must be approval_gated")
    check_false(inventory, INVENTORY_FALSE_FIELDS, "inventory", errors)


def validate(
    *,
    audit_dir: Path = AUDIT_DIR,
    report_path: Path = REPORT_PATH,
    inventory_path: Path = INVENTORY_PATH,
    doc_path: Path = DOC_PATH,
) -> list[str]:
    errors: list[str] = []
    if not audit_dir.exists():
        errors.append(f"missing audit directory: {display_path(audit_dir)}")
    else:
        present = {path.name for path in audit_dir.iterdir() if path.is_file()}
        missing = sorted(REQUIRED_FILES - present)
        if missing:
            errors.append(f"audit pack missing files: {', '.join(missing)}")

    for path in (report_path, inventory_path, doc_path):
        if not path.exists():
            errors.append(f"missing required artifact: {display_path(path)}")

    if report_path.exists():
        report = load_json(report_path)
        if not isinstance(report, Mapping):
            errors.append("report JSON must be an object")
        else:
            validate_report(report, errors)

    if inventory_path.exists():
        inventory = load_json(inventory_path)
        if not isinstance(inventory, Mapping):
            errors.append("inventory JSON must be an object")
        else:
            validate_inventory(inventory, errors)

    if audit_dir.exists():
        checks = {
            "CONNECTOR_STATUS_MATRIX.md": (
                "internet_archive_metadata",
                "wayback_cdx_memento",
                "github_releases",
                "software_heritage",
                "public_search_boundary",
            ),
            "APPROVAL_PACK_STATUS.md": (
                "connector_approved_now: false",
                "live_source_called",
                "external_calls_performed",
            ),
            "RUNTIME_PLANNING_STATUS.md": (
                "runtime_connector_implemented",
                "public_search_live_fanout_enabled",
                "planning-only",
            ),
            "SOURCE_POLICY_GATE_STATUS.md": (
                "policy_gated",
                "Do not fabricate",
            ),
            "USER_AGENT_CONTACT_RATE_LIMIT_STATUS.md": (
                "fake contact",
                "rate-limit",
                "circuit breaker",
            ),
            "TOKEN_AUTH_GATE_STATUS.md": (
                "No credentials",
                "tokens are disabled",
            ),
            "SOURCE_CACHE_EVIDENCE_LEDGER_DEPENDENCY_STATUS.md": (
                "implemented_local_dry_run",
                "Authoritative",
                "must not write directly",
            ),
            "PUBLIC_SEARCH_BOUNDARY_STATUS.md": (
                "must not call connectors live",
                "public-query-triggered",
            ),
            "MUTATION_BOUNDARY_STATUS.md": (
                "source_cache_mutated",
                "evidence_ledger_mutated",
                "master_index_mutated",
            ),
            "OPERATOR_ACTIONS_REQUIRED.md": (
                "review official source/API policies",
                "Manual Observation Batch 0",
            ),
            "APPROVAL_GATED_ACTIONS.md": (
                "live metadata probes",
                "source cache authoritative writes",
            ),
            "DO_NOT_IMPLEMENT_YET.md": (
                "no connector runtimes",
                "no live external source calls",
                "no public-search fanout",
                "no credentials or tokens",
            ),
        }
        for filename, phrases in checks.items():
            require_phrases(audit_dir / filename, phrases, errors)
        combined = "\n".join(path.read_text(encoding="utf-8") for path in audit_dir.iterdir() if path.is_file())
        scan_sensitive_text(combined, "audit pack", errors)

    if doc_path.exists():
        text = require_phrases(
            doc_path,
            (
                "connector set",
                "classification values",
                "Approval packs are not runtime",
                "Public search must not call connectors live",
                "Mutation remains disabled",
                "validate_connector_approval_runtime_planning_audit.py",
            ),
            errors,
            "operations doc",
        )
        scan_sensitive_text(text, "operations doc", errors)
    return errors


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit-dir", default=str(AUDIT_DIR))
    parser.add_argument("--report", default=str(REPORT_PATH))
    parser.add_argument("--inventory", default=str(INVENTORY_PATH))
    parser.add_argument("--doc", default=str(DOC_PATH))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    errors = validate(
        audit_dir=Path(args.audit_dir),
        report_path=Path(args.report),
        inventory_path=Path(args.inventory),
        doc_path=Path(args.doc),
    )
    status = "valid" if not errors else "invalid"
    if args.json:
        payload = {
            "status": status,
            "report_id": "connector_approval_runtime_planning_audit_v0",
            "audit_dir": display_path(Path(args.audit_dir)),
            "errors": errors,
        }
        print(json.dumps(payload, indent=2, sort_keys=True), file=stdout)
    else:
        print(f"status: {status}", file=stdout)
        for error in errors:
            print(f"ERROR: {error}", file=stdout)
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
