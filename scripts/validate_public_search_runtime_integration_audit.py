#!/usr/bin/env python3
"""Validate Public Search Runtime Integration Audit v0 artifacts."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
AUDIT_DIR = REPO_ROOT / "control" / "audits" / "public-search-runtime-integration-audit-v0"
REPORT_PATH = AUDIT_DIR / "public_search_runtime_integration_audit_report.json"
INVENTORY_PATH = REPO_ROOT / "control" / "inventory" / "publication" / "public_search_runtime_integration_status.json"
DOC_PATH = REPO_ROOT / "docs" / "operations" / "PUBLIC_SEARCH_RUNTIME_INTEGRATION_AUDIT.md"

REQUIRED_FILES = {
    "README.md",
    "EXECUTIVE_SUMMARY.md",
    "INTEGRATION_STATUS_MATRIX.md",
    "PUBLIC_SEARCH_RUNTIME_STATUS.md",
    "PUBLIC_SEARCH_ROUTE_STATUS.md",
    "PUBLIC_INDEX_STATUS.md",
    "STATIC_SITE_SEARCH_HANDOFF_STATUS.md",
    "HOSTED_DEPLOYMENT_STATUS.md",
    "SOURCE_CACHE_DRY_RUN_INTEGRATION_STATUS.md",
    "EVIDENCE_LEDGER_DRY_RUN_INTEGRATION_STATUS.md",
    "QUERY_OBSERVATION_INTEGRATION_STATUS.md",
    "PAGE_RUNTIME_INTEGRATION_STATUS.md",
    "CONNECTOR_RUNTIME_INTEGRATION_STATUS.md",
    "PACK_IMPORT_INTEGRATION_STATUS.md",
    "DEEP_EXTRACTION_INTEGRATION_STATUS.md",
    "SEARCH_RESULT_EXPLANATION_INTEGRATION_STATUS.md",
    "RANKING_RUNTIME_INTEGRATION_STATUS.md",
    "SAFETY_AND_BLOCKED_REQUEST_STATUS.md",
    "MUTATION_BOUNDARY_STATUS.md",
    "TELEMETRY_ACCOUNT_UPLOAD_DOWNLOAD_STATUS.md",
    "ARCHITECTURE_BOUNDARY_REVIEW.md",
    "COMMAND_RESULTS.md",
    "REMAINING_BLOCKERS.md",
    "NEXT_STEPS.md",
    "public_search_runtime_integration_audit_report.json",
}

CLASSIFICATIONS = {
    "implemented_public_runtime",
    "implemented_local_runtime",
    "implemented_local_dry_run",
    "implemented_static_artifact",
    "contract_only",
    "planning_only",
    "approval_gated",
    "operator_gated",
    "disabled",
    "absent",
    "blocked",
    "unexpected_integration",
}

REPORT_TRUE_FIELDS = {"audit_only"}
REPORT_FALSE_FIELDS = {
    "runtime_integration_implemented",
    "public_search_runtime_mutated",
    "public_search_routes_changed",
    "public_search_response_changed",
    "public_search_order_changed",
    "public_search_live_source_fanout_enabled",
    "source_cache_dry_run_integrated_with_public_search",
    "evidence_ledger_dry_run_integrated_with_public_search",
    "query_observation_runtime_integrated_with_public_search",
    "page_runtime_integrated_with_public_search",
    "connector_runtime_integrated_with_public_search",
    "pack_import_runtime_integrated_with_public_search",
    "deep_extraction_runtime_integrated_with_public_search",
    "explanation_runtime_integrated_with_public_search",
    "ranking_runtime_integrated_with_public_search",
    "source_cache_mutated",
    "evidence_ledger_mutated",
    "candidate_index_mutated",
    "public_index_mutated",
    "local_index_mutated",
    "master_index_mutated",
    "external_calls_performed",
    "live_source_called",
    "telemetry_enabled",
    "accounts_enabled",
    "uploads_enabled",
    "downloads_enabled",
    "installs_enabled",
    "execution_enabled",
    "deployment_performed",
}

INVENTORY_FALSE_FIELDS = {
    "public_search_live_source_fanout_enabled",
    "public_search_runtime_mutates_source_cache",
    "public_search_runtime_mutates_evidence_ledger",
    "public_search_runtime_mutates_candidate_index",
    "public_search_runtime_mutates_public_index",
    "public_search_runtime_mutates_master_index",
    "public_search_order_changed_by_ranking_runtime",
    "public_search_response_changed_by_explanation_runtime",
    "public_search_uses_telemetry",
    "public_search_uses_accounts",
    "public_search_uploads_enabled",
    "public_search_downloads_enabled",
    "public_search_installs_enabled",
    "public_search_execution_enabled",
}

INVENTORY_CLASSIFICATION_FIELDS = {
    "public_search_runtime_classification",
    "hosted_runtime_classification",
    "public_index_classification",
    "static_search_classification",
    "source_cache_dry_run_classification",
    "evidence_ledger_dry_run_classification",
    "query_observation_classification",
    "page_runtime_classification",
    "connector_runtime_classification",
    "pack_import_classification",
    "deep_extraction_classification",
    "explanation_runtime_classification",
    "ranking_runtime_classification",
    "telemetry_accounts_uploads_downloads_classification",
}

REQUIRED_REPORT_OBJECTS = {
    "integration_status_matrix",
    "public_search_runtime_status",
    "public_search_route_status",
    "public_index_status",
    "static_site_search_handoff_status",
    "hosted_deployment_status",
    "source_cache_dry_run_integration_status",
    "evidence_ledger_dry_run_integration_status",
    "query_observation_integration_status",
    "page_runtime_integration_status",
    "connector_runtime_integration_status",
    "pack_import_integration_status",
    "deep_extraction_integration_status",
    "search_result_explanation_integration_status",
    "ranking_runtime_integration_status",
    "safety_blocked_request_status",
    "mutation_boundary_status",
    "telemetry_account_upload_download_status",
    "architecture_boundary_review",
}


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


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


def validate_report(report: Mapping[str, Any], errors: list[str]) -> None:
    values = report.get("classification_values")
    if set(values or []) != CLASSIFICATIONS:
        errors.append("report.classification_values must exactly match allowed classifications")
    matrix = report.get("integration_status_matrix")
    if not isinstance(matrix, Mapping):
        errors.append("report.integration_status_matrix must be an object")
    else:
        for key, value in matrix.items():
            if value not in CLASSIFICATIONS:
                errors.append(f"report.integration_status_matrix.{key} has invalid classification {value!r}")
        expected = {
            "public_search_api": "implemented_local_runtime",
            "local_public_search_runtime": "implemented_local_runtime",
            "hosted_public_search_runtime": "operator_gated",
            "public_index": "implemented_static_artifact",
            "static_search_handoff": "implemented_static_artifact",
            "source_cache_dry_run": "implemented_local_dry_run",
            "evidence_ledger_dry_run": "implemented_local_dry_run",
            "query_observation": "planning_only",
            "connector_runtimes": "approval_gated",
            "deep_extraction": "contract_only",
            "search_result_explanation": "contract_only",
            "ranking_runtime": "planning_only",
            "telemetry_accounts_uploads_downloads": "disabled",
        }
        for key, value in expected.items():
            if matrix.get(key) != value:
                errors.append(f"report.integration_status_matrix.{key} must be {value}")
    check_true(report, REPORT_TRUE_FIELDS, "report", errors)
    check_false(report, REPORT_FALSE_FIELDS, "report", errors)
    for key in sorted(REQUIRED_REPORT_OBJECTS):
        if not isinstance(report.get(key), Mapping):
            errors.append(f"report.{key} must be an object")
    if report.get("source_cache_dry_run_integration_status", {}).get("public_search_integrated") is not False:
        errors.append("source cache dry-run must not be public-search integrated")
    if report.get("evidence_ledger_dry_run_integration_status", {}).get("public_search_integrated") is not False:
        errors.append("evidence ledger dry-run must not be public-search integrated")
    if report.get("connector_runtime_integration_status", {}).get("public_search_integrated") is not False:
        errors.append("connector runtimes must not be public-search integrated")
    if report.get("ranking_runtime_integration_status", {}).get("public_search_order_changed") is not False:
        errors.append("ranking runtime must not change public search order")
    if report.get("search_result_explanation_integration_status", {}).get("public_search_response_integrated") is not False:
        errors.append("explanation runtime must not change public search response")


def validate_inventory(inventory: Mapping[str, Any], errors: list[str]) -> None:
    if inventory.get("status") != "audited":
        errors.append("inventory.status must be audited")
    for field in sorted(INVENTORY_CLASSIFICATION_FIELDS):
        value = inventory.get(field)
        if value not in CLASSIFICATIONS:
            errors.append(f"inventory.{field} has invalid classification {value!r}")
    check_false(inventory, INVENTORY_FALSE_FIELDS, "inventory", errors)
    expected = {
        "public_search_runtime_classification": "implemented_local_runtime",
        "hosted_runtime_classification": "operator_gated",
        "source_cache_dry_run_classification": "implemented_local_dry_run",
        "evidence_ledger_dry_run_classification": "implemented_local_dry_run",
        "connector_runtime_classification": "approval_gated",
        "ranking_runtime_classification": "planning_only",
    }
    for key, value in expected.items():
        if inventory.get(key) != value:
            errors.append(f"inventory.{key} must be {value}")


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
        loaded = load_json(report_path)
        if not isinstance(loaded, Mapping):
            errors.append("report JSON must be an object")
        else:
            validate_report(loaded, errors)

    if inventory_path.exists():
        loaded = load_json(inventory_path)
        if not isinstance(loaded, Mapping):
            errors.append("inventory JSON must be an object")
        else:
            validate_inventory(loaded, errors)

    if audit_dir.exists():
        checks = {
            "PUBLIC_SEARCH_RUNTIME_STATUS.md": (
                "local_index_only",
                "implemented_local_runtime",
                "unexpected integrations: none",
            ),
            "PUBLIC_SEARCH_ROUTE_STATUS.md": (
                "/api/v1/search",
                "/api/v1/status",
                "/api/v1/result/{result_id}/explanation",
                "no route changes",
            ),
            "PUBLIC_INDEX_STATUS.md": (
                "584",
                "source cache integration: not integrated",
                "evidence ledger integration: not integrated",
            ),
            "HOSTED_DEPLOYMENT_STATUS.md": (
                "verified_failed",
                "not_configured",
                "no provider deployment",
            ),
            "SOURCE_CACHE_DRY_RUN_INTEGRATION_STATUS.md": (
                "implemented_local_dry_run",
                "public search integration status: not integrated",
                "authoritative source-cache status: disabled",
            ),
            "EVIDENCE_LEDGER_DRY_RUN_INTEGRATION_STATUS.md": (
                "implemented_local_dry_run",
                "public search integration status: not integrated",
                "truth acceptance: disabled",
            ),
            "CONNECTOR_RUNTIME_INTEGRATION_STATUS.md": (
                "approval_gated",
                "public search integration",
                "live calls enabled",
            ),
            "MUTATION_BOUNDARY_STATUS.md": (
                "source cache",
                "evidence ledger",
                "candidate index",
                "master index",
                "unexpected_integration",
            ),
            "TELEMETRY_ACCOUNT_UPLOAD_DOWNLOAD_STATUS.md": (
                "telemetry: disabled",
                "accounts: disabled",
                "upload endpoint: disabled",
                "download/install/execute: disabled",
            ),
            "ARCHITECTURE_BOUNDARY_REVIEW.md": (
                "public search should read controlled public/local index",
                "dry-run runtimes should remain cli/local",
                "no unexpected integration",
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
                "audit-only",
                "classification values",
                "source-cache dry-run runtime",
                "evidence-ledger dry-run runtime",
                "mutation",
                "safety",
                "validate_public_search_runtime_integration_audit.py",
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
            "report_id": "public_search_runtime_integration_audit_v0",
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
