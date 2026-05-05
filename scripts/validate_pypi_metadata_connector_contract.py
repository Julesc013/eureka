#!/usr/bin/env python3
"""Validate PyPI Metadata Connector Approval v0 governance artifacts."""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "scripts"))
from _p70_contract_common import load_json_object, print_report  # noqa: E402
from validate_pypi_metadata_connector_approval import validate_all_examples  # noqa: E402

APPROVAL_CONTRACT = REPO_ROOT / "contracts/connectors/pypi_metadata_connector_approval.v0.json"
MANIFEST_CONTRACT = REPO_ROOT / "contracts/connectors/pypi_metadata_connector_manifest.v0.json"
CONNECTOR_INVENTORY = REPO_ROOT / "control/inventory/connectors/pypi_metadata_connector.json"
AUDIT_DIR = REPO_ROOT / "control/audits/pypi-metadata-connector-approval-v0"
REPORT_PATH = AUDIT_DIR / "pypi_metadata_connector_approval_report.json"

REQ = {
    "schema_version",
    "approval_record_id",
    "approval_record_kind",
    "status",
    "created_by_tool",
    "connector_ref",
    "connector_scope",
    "allowed_capabilities",
    "forbidden_capabilities",
    "package_identity_policy",
    "dependency_metadata_caution_policy",
    "source_policy_review",
    "user_agent_and_contact_policy",
    "rate_limit_timeout_retry_circuit_breaker_policy",
    "cache_first_policy",
    "expected_source_cache_outputs",
    "expected_evidence_ledger_outputs",
    "query_intelligence_relationship",
    "public_search_boundary",
    "rights_access_and_risk_policy",
    "privacy_policy",
    "approval_checklist",
    "operator_checklist",
    "implementation_prerequisites",
    "limitations",
    "no_runtime_guarantees",
    "no_mutation_guarantees",
    "notes",
}
MANIFEST_REQ = {
    "schema_version",
    "connector_id",
    "connector_kind",
    "status",
    "source_family",
    "supported_capabilities",
    "disabled_capabilities",
    "default_policy",
    "source_sync_worker_relationship",
    "source_cache_relationship",
    "evidence_ledger_relationship",
    "safety_defaults",
    "no_runtime_guarantees",
    "notes",
}
CONTRACT_FALSE = {
    "x-connector_runtime_implemented",
    "x-connector_approved_now",
    "x-live_source_calls_allowed_now",
    "x-external_calls_allowed_now",
    "x-pypi_api_calls_allowed_now",
    "x-package_metadata_fetch_allowed_now",
    "x-releases_fetch_allowed_now",
    "x-files_metadata_fetch_allowed_now",
    "x-wheel_download_allowed",
    "x-sdist_download_allowed",
    "x-package_file_download_allowed",
    "x-package_install_allowed",
    "x-dependency_resolution_allowed_now",
    "x-package_archive_inspection_allowed_now",
    "x-public_search_live_fanout_allowed",
    "x-arbitrary_package_fetch_allowed",
    "x-source_cache_mutation_allowed_now",
    "x-evidence_ledger_mutation_allowed_now",
    "x-candidate_index_mutation_allowed_now",
    "x-public_index_mutation_allowed_now",
    "x-local_index_mutation_allowed_now",
    "x-master_index_mutation_allowed",
    "x-downloads_allowed",
    "x-file_retrieval_allowed",
    "x-mirroring_allowed",
    "x-token_required_now",
    "x-pypi_token_used",
    "x-dependency_safety_claimed",
    "x-installability_claimed",
    "x-telemetry_implemented",
    "x-credentials_configured",
}
MANIFEST_FALSE = {
    "x-runtime_implemented",
    "x-live_enabled_by_default",
    "x-public_query_fanout_allowed",
    "x-downloads_allowed",
    "x-arbitrary_url_fetch_allowed",
    "x-package_install_allowed",
    "x-wheel_download_allowed",
    "x-sdist_download_allowed",
    "x-package_file_download_allowed",
    "x-dependency_resolution_allowed_now",
    "x-token_required_now",
    "x-source_cache_mutation_allowed_now",
    "x-evidence_ledger_mutation_allowed_now",
    "x-candidate_index_mutation_allowed_now",
    "x-master_index_mutation_allowed_now",
}
INVENTORY_FALSE = {
    "connector_runtime_implemented",
    "connector_approved_now",
    "live_enabled_by_default",
    "public_query_fanout_allowed",
    "arbitrary_package_fetch_allowed",
    "package_install_allowed",
    "wheel_download_allowed",
    "sdist_download_allowed",
    "package_file_download_allowed",
    "dependency_resolution_allowed_now",
    "downloads_allowed",
    "file_retrieval_allowed",
    "mirroring_allowed",
    "token_required_now",
    "credentials_configured",
    "source_cache_mutation_allowed_now",
    "evidence_ledger_mutation_allowed_now",
    "candidate_index_mutation_allowed_now",
    "master_index_mutation_allowed",
}
INVENTORY_TRUE = {
    "metadata_only_scope",
    "package_metadata_only",
    "package_identity_review_required",
    "dependency_metadata_policy_review_required",
    "source_policy_review_required",
    "token_policy_review_required",
    "user_agent_contact_required_future",
    "rate_limit_required_future",
    "timeout_required_future",
    "retry_backoff_required_future",
    "circuit_breaker_required_future",
    "cache_required_before_public_use",
    "evidence_attribution_required",
}
REPORT_FALSE = {
    "connector_runtime_implemented",
    "connector_approved_now",
    "live_enabled_by_default",
    "live_source_called",
    "external_calls_performed",
    "pypi_api_called",
    "package_metadata_fetched",
    "releases_fetched",
    "files_metadata_fetched",
    "wheels_downloaded",
    "sdists_downloaded",
    "package_files_downloaded",
    "package_installed",
    "dependency_resolution_performed",
    "package_archive_inspected",
    "public_query_fanout_allowed",
    "public_search_live_fanout_enabled",
    "arbitrary_package_fetch_allowed",
    "package_install_allowed",
    "wheel_download_allowed",
    "sdist_download_allowed",
    "package_file_download_allowed",
    "downloads_allowed",
    "file_retrieval_allowed",
    "mirroring_allowed",
    "source_cache_mutation_allowed_now",
    "evidence_ledger_mutation_allowed_now",
    "candidate_index_mutation_allowed_now",
    "public_index_mutation_allowed_now",
    "local_index_mutation_allowed_now",
    "master_index_mutation_allowed",
    "rights_clearance_claimed",
    "malware_safety_claimed",
    "dependency_safety_claimed",
    "installability_claimed",
    "telemetry_implemented",
    "credentials_configured",
    "token_required_now",
    "pypi_token_used",
}
AUDIT_FILES = {
    "README.md",
    "APPROVAL_SUMMARY.md",
    "CONNECTOR_SCOPE.md",
    "ALLOWED_METADATA_CAPABILITIES.md",
    "FORBIDDEN_CAPABILITIES.md",
    "PACKAGE_IDENTITY_AND_PRIVACY_POLICY.md",
    "DEPENDENCY_METADATA_CAUTION_POLICY.md",
    "SOURCE_POLICY_REVIEW.md",
    "USER_AGENT_AND_CONTACT_POLICY.md",
    "RATE_LIMIT_TIMEOUT_RETRY_CIRCUIT_BREAKER_POLICY.md",
    "CACHE_FIRST_AND_EVIDENCE_OUTPUT_POLICY.md",
    "SOURCE_SYNC_WORKER_RELATIONSHIP.md",
    "SOURCE_CACHE_OUTPUT_MODEL.md",
    "EVIDENCE_LEDGER_OUTPUT_MODEL.md",
    "QUERY_INTELLIGENCE_RELATIONSHIP.md",
    "PUBLIC_SEARCH_BOUNDARY.md",
    "RIGHTS_ACCESS_AND_RISK_POLICY.md",
    "PRIVACY_AND_REDACTION_POLICY.md",
    "APPROVAL_CHECKLIST.md",
    "OPERATOR_CHECKLIST.md",
    "EXAMPLE_APPROVAL_RECORD_REVIEW.md",
    "NO_RUNTIME_AND_NO_MUTATION_POLICY.md",
    "FUTURE_IMPLEMENTATION_PATH.md",
    "COMMAND_RESULTS.md",
    "REMAINING_BLOCKERS.md",
    "NEXT_STEPS.md",
    "pypi_metadata_connector_approval_report.json",
}
DOCS = {
    "docs/reference/PYPI_METADATA_CONNECTOR_APPROVAL.md": (
        "live connector is not implemented",
        "no external calls",
        "no pypi api calls",
        "package metadata-only",
        "arbitrary package fetch",
        "package install",
        "wheel download",
        "sdist download",
        "dependency resolution",
        "dependency metadata caution",
        "token policy",
        "cache-first",
        "public search must not call pypi",
    ),
    "docs/architecture/SOURCE_INGESTION_PLANE.md": ("p74 pypi metadata connector approval", "no pypi api calls", "public-query fanout"),
    "docs/reference/SOURCE_SYNC_WORKER_CONTRACT.md": ("p74 pypi metadata connector approval", "cache-first"),
    "docs/reference/SOURCE_CACHE_CONTRACT.md": ("p74 pypi metadata connector approval", "source cache"),
    "docs/reference/EVIDENCE_LEDGER_CONTRACT.md": ("p74 pypi metadata connector approval", "evidence ledger"),
}
FORBIDDEN = (
    "pypi live search enabled true",
    "pypi api was called",
    "package metadata was fetched",
    "wheels were downloaded",
    "sdists were downloaded",
    "package files were downloaded",
    "package was installed",
    "dependency resolution was performed",
    "package archive was inspected",
    "source cache was mutated",
    "evidence ledger was mutated",
    "master index was mutated",
    "rights clearance is complete",
    "malware safety is confirmed",
    "dependency safety is confirmed",
    "installability is confirmed",
    "production ready",
)


def validate_contract() -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    c = load_json_object(APPROVAL_CONTRACT, errors, "contracts/connectors/pypi_metadata_connector_approval.v0.json")
    if c:
        validate_schema(c, REQ, CONTRACT_FALSE, "approval contract", errors)
    m = load_json_object(MANIFEST_CONTRACT, errors, "contracts/connectors/pypi_metadata_connector_manifest.v0.json")
    if m:
        validate_schema(m, MANIFEST_REQ, MANIFEST_FALSE, "manifest contract", errors)
    inv = load_json_object(CONNECTOR_INVENTORY, errors, "control/inventory/connectors/pypi_metadata_connector.json")
    if inv:
        validate_inventory(inv, errors)
    examples = validate_all_examples(strict=True)
    if examples.get("status") != "valid":
        errors.append("PyPI metadata connector approval examples failed validation.")
        errors.extend(examples.get("errors", []))
    validate_docs(errors)
    validate_audit(errors)
    report = load_json_object(REPORT_PATH, errors, "pypi_metadata_connector_approval_report.json")
    if report:
        if report.get("report_id") != "pypi_metadata_connector_approval_v0":
            errors.append("report_id must be pypi_metadata_connector_approval_v0.")
        for key in REPORT_FALSE:
            if report.get(key) is not False:
                errors.append(f"report {key} must be false.")
    scan_forbidden(errors)
    return {
        "status": "valid" if not errors else "invalid",
        "created_by": "pypi_metadata_connector_contract_validator_v0",
        "contract_file": "contracts/connectors/pypi_metadata_connector_approval.v0.json",
        "example_count": examples.get("example_count", 0),
        "errors": errors,
        "warnings": warnings,
    }


def validate_schema(c: Mapping[str, Any], req: set[str], false: set[str], label: str, errors: list[str]) -> None:
    if c.get("x-status") != "contract_only":
        errors.append(f"{label} x-status must be contract_only.")
    for key in false:
        if c.get(key) is not False:
            errors.append(f"{label} {key} must be false.")
    missing = req - set(c.get("required", []))
    if missing:
        errors.append(f"{label} missing required fields: " + ", ".join(sorted(missing)))


def validate_inventory(inv: Mapping[str, Any], errors: list[str]) -> None:
    if inv.get("status") != "approval_required":
        errors.append("connector inventory status must be approval_required.")
    if inv.get("connector_id") != "pypi_metadata_connector":
        errors.append("connector inventory connector_id must be pypi_metadata_connector.")
    if inv.get("source_family") != "pypi":
        errors.append("connector inventory source_family must be pypi.")
    for key in INVENTORY_FALSE:
        if inv.get(key) is not False:
            errors.append(f"connector inventory {key} must be false.")
    for key in INVENTORY_TRUE:
        if inv.get(key) is not True:
            errors.append(f"connector inventory {key} must be true.")


def validate_docs(errors: list[str]) -> None:
    for rel, phrases in DOCS.items():
        path = REPO_ROOT / rel
        if not path.is_file():
            errors.append(f"{rel} missing.")
            continue
        text = path.read_text(encoding="utf-8").casefold()
        for phrase in phrases:
            if phrase not in text:
                errors.append(f"{rel} missing required phrase: {phrase}")


def validate_audit(errors: list[str]) -> None:
    if not AUDIT_DIR.is_dir():
        errors.append("control/audits/pypi-metadata-connector-approval-v0 missing.")
        return
    present = {p.name for p in AUDIT_DIR.iterdir() if p.is_file()}
    missing = AUDIT_FILES - present
    if missing:
        errors.append("audit pack missing files: " + ", ".join(sorted(missing)))


def scan_forbidden(errors: list[str]) -> None:
    paths = [
        REPO_ROOT / "contracts/connectors/pypi_metadata_connector_approval.v0.json",
        REPO_ROOT / "contracts/connectors/pypi_metadata_connector_manifest.v0.json",
        REPO_ROOT / "control/inventory/connectors/pypi_metadata_connector.json",
        REPO_ROOT / "docs/reference/PYPI_METADATA_CONNECTOR_APPROVAL.md",
        REPO_ROOT / "examples/connectors/pypi_metadata_approval_v0",
        AUDIT_DIR,
    ]
    chunks: list[str] = []
    for base in paths:
        if not base.exists():
            continue
        for path in ([base] if base.is_file() else base.rglob("*")):
            if path.is_file():
                chunks.append(path.read_text(encoding="utf-8"))
    text = "\n".join(chunks).casefold()
    for phrase in FORBIDDEN:
        if phrase in text:
            errors.append(f"forbidden PyPI metadata connector claim present: {phrase}")
    if re.search(r"\b[A-Za-z]:\\+(?:users|documents|temp|windows|projects|private|local)\\+", text, re.I):
        errors.append("PyPI metadata governed artifacts contain prohibited private path.")
    if re.search(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", text, re.I):
        errors.append("PyPI metadata governed artifacts contain an email/contact value.")
    if re.search(r"\b(?:api[_-]?key|auth[_-]?token|pypi[_-]?token|password|secret)\s*[:=]", text, re.I):
        errors.append("PyPI metadata governed artifacts contain a secret/API-key/token marker.")
    if re.search(r"https?://[^\s/]*@|\b(?:file|data|javascript):|pypi\.org|pythonhosted", text, re.I):
        errors.append("PyPI metadata governed artifacts contain prohibited credentialed, file/data/javascript, or API-host reference.")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    report = validate_contract()
    print_report(report, args.json)
    return 0 if report["status"] == "valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
