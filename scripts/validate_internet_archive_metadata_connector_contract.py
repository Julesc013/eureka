#!/usr/bin/env python3
"""Validate Internet Archive Metadata Connector Approval v0 governance artifacts."""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys
from typing import Any, Mapping, Sequence


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "scripts"))

from _p70_contract_common import load_json_object, print_report  # noqa: E402
from validate_internet_archive_metadata_connector_approval import validate_all_examples  # noqa: E402


APPROVAL_CONTRACT = REPO_ROOT / "contracts/connectors/internet_archive_metadata_connector_approval.v0.json"
MANIFEST_CONTRACT = REPO_ROOT / "contracts/connectors/internet_archive_metadata_connector_manifest.v0.json"
CONNECTOR_INVENTORY = REPO_ROOT / "control/inventory/connectors/internet_archive_metadata_connector.json"
AUDIT_DIR = REPO_ROOT / "control/audits/internet-archive-metadata-connector-approval-v0"
REPORT_PATH = AUDIT_DIR / "internet_archive_metadata_connector_approval_report.json"
REQUIRED_CONTRACT_FIELDS = {
    "schema_version",
    "approval_record_id",
    "approval_record_kind",
    "status",
    "created_by_tool",
    "connector_ref",
    "connector_scope",
    "allowed_capabilities",
    "forbidden_capabilities",
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
REQUIRED_MANIFEST_FIELDS = {
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
    "x-public_search_live_fanout_allowed",
    "x-source_cache_mutation_allowed_now",
    "x-evidence_ledger_mutation_allowed_now",
    "x-candidate_index_mutation_allowed_now",
    "x-public_index_mutation_allowed_now",
    "x-local_index_mutation_allowed_now",
    "x-master_index_mutation_allowed",
    "x-downloads_allowed",
    "x-file_retrieval_allowed",
    "x-mirroring_allowed",
    "x-arbitrary_url_fetch_allowed",
    "x-telemetry_implemented",
    "x-credentials_configured",
}
MANIFEST_FALSE = {
    "x-runtime_implemented",
    "x-live_enabled_by_default",
    "x-public_query_fanout_allowed",
    "x-downloads_allowed",
    "x-arbitrary_url_fetch_allowed",
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
    "downloads_allowed",
    "file_retrieval_allowed",
    "mirroring_allowed",
    "arbitrary_url_fetch_allowed",
    "source_cache_mutation_allowed_now",
    "evidence_ledger_mutation_allowed_now",
    "candidate_index_mutation_allowed_now",
    "master_index_mutation_allowed",
}
INVENTORY_TRUE = {
    "metadata_only_scope",
    "source_policy_review_required",
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
    "public_query_fanout_allowed",
    "public_search_live_fanout_enabled",
    "source_cache_mutation_allowed_now",
    "evidence_ledger_mutation_allowed_now",
    "candidate_index_mutation_allowed_now",
    "public_index_mutation_allowed_now",
    "local_index_mutation_allowed_now",
    "master_index_mutation_allowed",
    "downloads_allowed",
    "file_retrieval_allowed",
    "mirroring_allowed",
    "arbitrary_url_fetch_allowed",
    "rights_clearance_claimed",
    "malware_safety_claimed",
    "telemetry_implemented",
    "credentials_configured",
}
REQUIRED_AUDIT_FILES = {
    "README.md",
    "APPROVAL_SUMMARY.md",
    "CONNECTOR_SCOPE.md",
    "ALLOWED_METADATA_CAPABILITIES.md",
    "FORBIDDEN_CAPABILITIES.md",
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
    "internet_archive_metadata_connector_approval_report.json",
}
REQUIRED_DOCS = {
    "docs/reference/INTERNET_ARCHIVE_METADATA_CONNECTOR_APPROVAL.md": (
        "connector is not implemented",
        "no external calls",
        "metadata-only",
        "downloads",
        "arbitrary url fetch",
        "source policy",
        "user-agent",
        "cache-first",
        "evidence ledger",
        "public search must not call",
    ),
    "docs/architecture/SOURCE_INGESTION_PLANE.md": (
        "p71 internet archive metadata connector approval",
        "connector is not implemented",
        "no external calls",
        "public queries do not fan out",
    ),
    "docs/reference/SOURCE_SYNC_WORKER_CONTRACT.md": ("p71 internet archive metadata connector approval", "cache-first"),
    "docs/reference/SOURCE_CACHE_CONTRACT.md": ("p71 internet archive metadata connector approval", "source cache"),
    "docs/reference/EVIDENCE_LEDGER_CONTRACT.md": ("p71 internet archive metadata connector approval", "evidence ledger"),
}
FORBIDDEN_CLAIMS = (
    "internet archive connector is implemented",
    "ia connector is implemented",
    "connector_approved_now true",
    "live ia search is enabled",
    "archive.org was called",
    "source cache was mutated",
    "evidence ledger was mutated",
    "master index was mutated",
    "rights clearance is complete",
    "malware safety is confirmed",
    "production ready",
)


def validate_contract() -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    approval_contract = load_json_object(APPROVAL_CONTRACT, errors, "contracts/connectors/internet_archive_metadata_connector_approval.v0.json")
    if approval_contract:
        _validate_approval_contract(approval_contract, errors)
    manifest_contract = load_json_object(MANIFEST_CONTRACT, errors, "contracts/connectors/internet_archive_metadata_connector_manifest.v0.json")
    if manifest_contract:
        _validate_manifest_contract(manifest_contract, errors)
    inventory = load_json_object(CONNECTOR_INVENTORY, errors, "control/inventory/connectors/internet_archive_metadata_connector.json")
    if inventory:
        _validate_inventory(inventory, errors)
    examples = validate_all_examples(strict=True)
    if examples.get("status") != "valid":
        errors.append("Internet Archive metadata connector approval examples failed validation.")
        errors.extend(examples.get("errors", []))
    _validate_docs(errors)
    _validate_audit_pack(errors)
    report = load_json_object(REPORT_PATH, errors, "internet_archive_metadata_connector_approval_report.json")
    if report:
        for key in REPORT_FALSE:
            if report.get(key) is not False:
                errors.append(f"report {key} must be false.")
        if report.get("report_id") != "internet_archive_metadata_connector_approval_v0":
            errors.append("report_id must be internet_archive_metadata_connector_approval_v0.")
    _scan_forbidden_claims(errors)
    return {
        "status": "valid" if not errors else "invalid",
        "created_by": "internet_archive_metadata_connector_contract_validator_v0",
        "contract_file": "contracts/connectors/internet_archive_metadata_connector_approval.v0.json",
        "example_count": examples.get("example_count", 0),
        "errors": errors,
        "warnings": warnings,
    }


def _validate_approval_contract(contract: Mapping[str, Any], errors: list[str]) -> None:
    if contract.get("x-status") != "contract_only":
        errors.append("approval contract x-status must be contract_only.")
    for key in CONTRACT_FALSE:
        if contract.get(key) is not False:
            errors.append(f"approval contract {key} must be false.")
    missing = REQUIRED_CONTRACT_FIELDS - set(contract.get("required", []))
    if missing:
        errors.append(f"approval contract missing required fields: {', '.join(sorted(missing))}")


def _validate_manifest_contract(contract: Mapping[str, Any], errors: list[str]) -> None:
    if contract.get("x-status") != "contract_only":
        errors.append("manifest contract x-status must be contract_only.")
    for key in MANIFEST_FALSE:
        if contract.get(key) is not False:
            errors.append(f"manifest contract {key} must be false.")
    missing = REQUIRED_MANIFEST_FIELDS - set(contract.get("required", []))
    if missing:
        errors.append(f"manifest contract missing required fields: {', '.join(sorted(missing))}")


def _validate_inventory(inventory: Mapping[str, Any], errors: list[str]) -> None:
    if inventory.get("status") != "approval_required":
        errors.append("connector inventory status must be approval_required.")
    if inventory.get("connector_id") != "internet_archive_metadata_connector":
        errors.append("connector inventory connector_id must be internet_archive_metadata_connector.")
    if inventory.get("source_family") != "internet_archive":
        errors.append("connector inventory source_family must be internet_archive.")
    for key in INVENTORY_FALSE:
        if inventory.get(key) is not False:
            errors.append(f"connector inventory {key} must be false.")
    for key in INVENTORY_TRUE:
        if inventory.get(key) is not True:
            errors.append(f"connector inventory {key} must be true.")


def _validate_docs(errors: list[str]) -> None:
    for rel, phrases in REQUIRED_DOCS.items():
        path = REPO_ROOT / rel
        if not path.is_file():
            errors.append(f"{rel} missing.")
            continue
        text = path.read_text(encoding="utf-8").casefold()
        for phrase in phrases:
            if phrase not in text:
                errors.append(f"{rel} missing required phrase: {phrase}")


def _validate_audit_pack(errors: list[str]) -> None:
    if not AUDIT_DIR.is_dir():
        errors.append("control/audits/internet-archive-metadata-connector-approval-v0 missing.")
        return
    present = {path.name for path in AUDIT_DIR.iterdir() if path.is_file()}
    missing = REQUIRED_AUDIT_FILES - present
    if missing:
        errors.append(f"audit pack missing files: {', '.join(sorted(missing))}")


def _scan_forbidden_claims(errors: list[str]) -> None:
    paths = [
        REPO_ROOT / "contracts/connectors",
        REPO_ROOT / "control/inventory/connectors",
        REPO_ROOT / "docs/reference/INTERNET_ARCHIVE_METADATA_CONNECTOR_APPROVAL.md",
        REPO_ROOT / "examples/connectors/internet_archive_metadata_approval_v0",
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
    for phrase in FORBIDDEN_CLAIMS:
        if phrase in text:
            errors.append(f"forbidden IA connector claim present: {phrase}")
    if re.search(r"\b[A-Za-z]:\\+(?:users|documents|temp|windows|projects|private|local)\\+", text, re.I):
        errors.append("IA connector governed artifacts contain prohibited private path.")
    if re.search(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", text, re.I):
        errors.append("IA connector governed artifacts contain an email/contact value.")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    report = validate_contract()
    print_report(report, args.json)
    return 0 if report["status"] == "valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
