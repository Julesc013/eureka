#!/usr/bin/env python3
"""Validate Software Heritage Connector Approval v0 governance artifacts."""
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
from validate_software_heritage_connector_approval import validate_all_examples  # noqa: E402

APPROVAL_CONTRACT = REPO_ROOT / "contracts/connectors/software_heritage_connector_approval.v0.json"
MANIFEST_CONTRACT = REPO_ROOT / "contracts/connectors/software_heritage_connector_manifest.v0.json"
CONNECTOR_INVENTORY = REPO_ROOT / "control/inventory/connectors/software_heritage_connector.json"
SOURCE_INVENTORY = REPO_ROOT / "control/inventory/sources/software-heritage-placeholder.source.json"
AUDIT_DIR = REPO_ROOT / "control/audits/software-heritage-connector-approval-v0"
REPORT_PATH = AUDIT_DIR / "software_heritage_connector_approval_report.json"

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
    "swhid_origin_repository_policy",
    "source_code_content_risk_policy",
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
    "x-software_heritage_api_calls_allowed_now",
    "x-swhid_resolution_allowed_now",
    "x-origin_lookup_allowed_now",
    "x-visit_lookup_allowed_now",
    "x-snapshot_lookup_allowed_now",
    "x-release_lookup_allowed_now",
    "x-revision_lookup_allowed_now",
    "x-directory_lookup_allowed_now",
    "x-content_blob_lookup_allowed_now",
    "x-repository_clone_allowed",
    "x-source_code_download_allowed",
    "x-source_archive_download_allowed",
    "x-source_file_retrieval_allowed",
    "x-public_search_live_fanout_allowed",
    "x-arbitrary_origin_fetch_allowed",
    "x-arbitrary_swhid_fetch_allowed",
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
    "x-software_heritage_token_used",
    "x-rights_clearance_claimed",
    "x-malware_safety_claimed",
    "x-source_code_safety_claimed",
    "x-source_completeness_claimed",
    "x-telemetry_implemented",
    "x-credentials_configured",
}
MANIFEST_FALSE = {
    "x-runtime_implemented",
    "x-live_enabled_by_default",
    "x-public_query_fanout_allowed",
    "x-downloads_allowed",
    "x-arbitrary_url_fetch_allowed",
    "x-repository_clone_allowed",
    "x-source_code_download_allowed",
    "x-source_archive_download_allowed",
    "x-content_blob_fetch_allowed",
    "x-origin_crawl_allowed",
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
    "arbitrary_origin_fetch_allowed",
    "arbitrary_swhid_fetch_allowed",
    "repository_clone_allowed",
    "source_code_download_allowed",
    "source_archive_download_allowed",
    "content_blob_fetch_allowed",
    "origin_crawl_allowed",
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
    "software_identity_metadata_only",
    "swhid_policy_review_required",
    "origin_url_policy_review_required",
    "repository_identity_review_required",
    "source_code_content_risk_policy_review_required",
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
SOURCE_APPROVAL_FALSE = {
    "connector_runtime_implemented",
    "live_enabled_by_default",
    "software_heritage_api_calls_enabled",
    "swhid_resolution_enabled",
    "origin_lookup_enabled",
    "content_blob_lookup_enabled",
    "repository_clone_enabled",
    "source_code_download_enabled",
    "source_archive_download_enabled",
    "source_cache_populated_from_live_calls",
    "evidence_ledger_populated_from_live_calls",
}
REPORT_FALSE = {
    "connector_runtime_implemented",
    "connector_approved_now",
    "live_enabled_by_default",
    "live_source_called",
    "external_calls_performed",
    "software_heritage_api_called",
    "swhid_resolved_live",
    "origin_lookup_performed",
    "visit_lookup_performed",
    "snapshot_lookup_performed",
    "release_lookup_performed",
    "revision_lookup_performed",
    "directory_lookup_performed",
    "content_blob_lookup_performed",
    "repository_cloned",
    "source_code_downloaded",
    "source_archive_downloaded",
    "source_file_retrieved",
    "public_query_fanout_allowed",
    "public_search_live_fanout_enabled",
    "arbitrary_origin_fetch_allowed",
    "arbitrary_swhid_fetch_allowed",
    "repository_clone_allowed",
    "source_code_download_allowed",
    "source_archive_download_allowed",
    "content_blob_fetch_allowed",
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
    "source_code_safety_claimed",
    "source_completeness_claimed",
    "telemetry_implemented",
    "credentials_configured",
    "token_required_now",
    "software_heritage_token_used",
}
AUDIT_FILES = {
    "README.md",
    "APPROVAL_SUMMARY.md",
    "CONNECTOR_SCOPE.md",
    "ALLOWED_METADATA_CAPABILITIES.md",
    "FORBIDDEN_CAPABILITIES.md",
    "SWHID_ORIGIN_AND_REPOSITORY_IDENTITY_POLICY.md",
    "SOURCE_CODE_CONTENT_RISK_POLICY.md",
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
    "software_heritage_connector_approval_report.json",
}
DOCS = {
    "docs/reference/SOFTWARE_HERITAGE_CONNECTOR_APPROVAL.md": (
        "live connector is not implemented",
        "no external calls",
        "no software heritage api calls",
        "public search must not call software heritage",
        "software identity/archive metadata-only",
        "arbitrary origin fetch",
        "arbitrary swhid fetch",
        "source code content fetch",
        "content blob fetch",
        "repository clone",
        "source archive download",
        "cache-first",
    ),
    "docs/architecture/SOURCE_INGESTION_PLANE.md": (
        "p76 software heritage connector approval",
        "no software heritage api calls",
        "public-query fanout",
    ),
    "docs/reference/SOURCE_SYNC_WORKER_CONTRACT.md": (
        "p76 software heritage connector approval",
        "cache-first",
    ),
    "docs/reference/SOURCE_CACHE_CONTRACT.md": (
        "p76 software heritage connector approval",
        "source cache",
    ),
    "docs/reference/EVIDENCE_LEDGER_CONTRACT.md": (
        "p76 software heritage connector approval",
        "evidence ledger",
    ),
}
FORBIDDEN = (
    "software heritage live search enabled true",
    "software heritage api was called",
    "swhid was resolved live",
    "origin lookup was performed",
    "visit lookup was performed",
    "snapshot lookup was performed",
    "release lookup was performed",
    "revision lookup was performed",
    "directory lookup was performed",
    "content blob lookup was performed",
    "repository was cloned",
    "source code was downloaded",
    "source archive was downloaded",
    "source file was retrieved",
    "source cache was mutated",
    "evidence ledger was mutated",
    "master index was mutated",
    "rights clearance is complete",
    "malware safety is confirmed",
    "source-code safety is confirmed",
    "source completeness is confirmed",
    "production ready",
)


def validate_contract() -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    c = load_json_object(APPROVAL_CONTRACT, errors, "contracts/connectors/software_heritage_connector_approval.v0.json")
    if c:
        validate_schema(c, REQ, CONTRACT_FALSE, "approval contract", errors)
    m = load_json_object(MANIFEST_CONTRACT, errors, "contracts/connectors/software_heritage_connector_manifest.v0.json")
    if m:
        validate_schema(m, MANIFEST_REQ, MANIFEST_FALSE, "manifest contract", errors)
    inv = load_json_object(CONNECTOR_INVENTORY, errors, "control/inventory/connectors/software_heritage_connector.json")
    if inv:
        validate_inventory(inv, errors)
    source_inv = load_json_object(SOURCE_INVENTORY, errors, "software-heritage source inventory")
    if source_inv:
        validate_source_inventory(source_inv, errors)
    examples = validate_all_examples(strict=True)
    if examples.get("status") != "valid":
        errors.append("Software Heritage connector approval examples failed validation.")
        errors.extend(examples.get("errors", []))
    validate_docs(errors)
    validate_audit(errors)
    report = load_json_object(REPORT_PATH, errors, "software_heritage_connector_approval_report.json")
    if report:
        if report.get("report_id") != "software_heritage_connector_approval_v0":
            errors.append("report_id must be software_heritage_connector_approval_v0.")
        for key in REPORT_FALSE:
            if report.get(key) is not False:
                errors.append(f"report {key} must be false.")
    scan_forbidden(errors)
    return {
        "status": "valid" if not errors else "invalid",
        "created_by": "software_heritage_connector_contract_validator_v0",
        "contract_file": "contracts/connectors/software_heritage_connector_approval.v0.json",
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
    if inv.get("connector_id") != "software_heritage_connector":
        errors.append("connector inventory connector_id must be software_heritage_connector.")
    if inv.get("source_family") != "software_heritage":
        errors.append("connector inventory source_family must be software_heritage.")
    for key in INVENTORY_FALSE:
        if inv.get(key) is not False:
            errors.append(f"connector inventory {key} must be false.")
    for key in INVENTORY_TRUE:
        if inv.get(key) is not True:
            errors.append(f"connector inventory {key} must be true.")


def validate_source_inventory(inv: Mapping[str, Any], errors: list[str]) -> None:
    record = inv.get("connector_approval")
    if not isinstance(record, Mapping):
        errors.append("source inventory connector_approval must reference P76.")
        return
    if record.get("connector_inventory_ref") != "control/inventory/connectors/software_heritage_connector.json":
        errors.append("source inventory connector_approval connector_inventory_ref must point to Software Heritage connector inventory.")
    if record.get("status") != "approval_required":
        errors.append("source inventory connector_approval status must be approval_required.")
    for key in SOURCE_APPROVAL_FALSE:
        if record.get(key) is not False:
            errors.append(f"source inventory connector_approval {key} must be false.")


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
        errors.append("control/audits/software-heritage-connector-approval-v0 missing.")
        return
    present = {p.name for p in AUDIT_DIR.iterdir() if p.is_file()}
    missing = AUDIT_FILES - present
    if missing:
        errors.append("audit pack missing files: " + ", ".join(sorted(missing)))


def scan_forbidden(errors: list[str]) -> None:
    paths = [
        APPROVAL_CONTRACT,
        MANIFEST_CONTRACT,
        CONNECTOR_INVENTORY,
        REPO_ROOT / "docs/reference/SOFTWARE_HERITAGE_CONNECTOR_APPROVAL.md",
        REPO_ROOT / "examples/connectors/software_heritage_approval_v0",
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
            errors.append(f"forbidden Software Heritage connector claim present: {phrase}")
    if re.search(r"\b[A-Za-z]:\\+(?:users|documents|temp|windows|projects|private|local)\\+", text, re.I):
        errors.append("Software Heritage governed artifacts contain prohibited private path.")
    if re.search(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", text, re.I):
        errors.append("Software Heritage governed artifacts contain an email/contact value.")
    if re.search(r"\b(?:api[_-]?key|auth[_-]?token|software[_-]?heritage[_-]?token|swh[_-]?token|password|secret)\s*[:=]", text, re.I):
        errors.append("Software Heritage governed artifacts contain a secret/API-key/token marker.")
    if re.search(r"https?://[^\s/]*@|\b(?:file|data|javascript):|archive\.softwareheritage\.org|softwareheritage\.org", text, re.I):
        errors.append("Software Heritage governed artifacts contain prohibited credentialed, file/data/javascript, or source-host reference.")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    report = validate_contract()
    print_report(report, args.json)
    return 0 if report["status"] == "valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
