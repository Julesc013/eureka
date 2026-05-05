#!/usr/bin/env python3
"""Validate Software Heritage Connector Runtime Planning v0 artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
AUDIT_DIR = REPO_ROOT / "control" / "audits" / "software-heritage-connector-runtime-planning-v0"
REPORT_PATH = AUDIT_DIR / "software_heritage_connector_runtime_planning_report.json"
INVENTORY_PATH = REPO_ROOT / "control" / "inventory" / "connectors" / "software_heritage_connector_runtime_plan.json"
DOC_PATH = REPO_ROOT / "docs" / "operations" / "SOFTWARE_HERITAGE_CONNECTOR_RUNTIME_PLAN.md"

REQUIRED_FILES = {
    "README.md",
    "PLANNING_SUMMARY.md",
    "READINESS_DECISION.md",
    "APPROVAL_GATE_REVIEW.md",
    "SWHID_ORIGIN_REPOSITORY_AND_SOURCE_POLICY_GATE_REVIEW.md",
    "SOURCE_CODE_CONTENT_BOUNDARY_REVIEW.md",
    "TOKEN_AUTH_BOUNDARY_REVIEW.md",
    "USER_AGENT_CONTACT_AND_RATE_LIMIT_REVIEW.md",
    "RUNTIME_BOUNDARY.md",
    "CONNECTOR_RUNTIME_ARCHITECTURE_PLAN.md",
    "SOURCE_SYNC_JOB_FLOW.md",
    "SWHID_ORIGIN_REPOSITORY_REVIEW_AND_NORMALIZATION_PLAN.md",
    "SOURCE_CACHE_OUTPUT_PLAN.md",
    "EVIDENCE_LEDGER_OUTPUT_PLAN.md",
    "VALIDATION_AND_NORMALIZATION_PLAN.md",
    "FAILURE_RETRY_TIMEOUT_CIRCUIT_BREAKER_PLAN.md",
    "PUBLIC_SEARCH_BOUNDARY.md",
    "PRIVACY_RIGHTS_RISK_REVIEW.md",
    "SECURITY_AND_ABUSE_REVIEW.md",
    "IMPLEMENTATION_PHASES.md",
    "ACCEPTANCE_CRITERIA.md",
    "DO_NOT_IMPLEMENT_YET.md",
    "COMMAND_RESULTS.md",
    "REMAINING_BLOCKERS.md",
    "NEXT_STEPS.md",
    "software_heritage_connector_runtime_planning_report.json",
}

VALID_READINESS = {
    "ready_for_local_dry_run_runtime_after_operator_approval",
    "ready_for_source_sync_worker_runtime_after_operator_approval",
    "blocked_connector_approval_missing",
    "blocked_connector_approval_pending",
    "blocked_swhid_policy_missing",
    "blocked_origin_url_policy_missing",
    "blocked_repository_identity_policy_missing",
    "blocked_source_code_content_policy_missing",
    "blocked_token_auth_policy_missing",
    "blocked_source_code_download_content_repository_boundary_missing",
    "blocked_source_policy_review_missing",
    "blocked_user_agent_contact_missing",
    "blocked_rate_limit_timeout_circuit_breaker_policy_missing",
    "blocked_source_cache_contract_missing",
    "blocked_evidence_ledger_contract_missing",
    "blocked_source_sync_worker_contract_missing",
    "blocked_public_search_safety_failed",
    "blocked_hosted_deployment_unverified",
    "blocked_other",
}

REPORT_FALSE_FIELDS = {
    "runtime_connector_implemented",
    "live_calls_enabled",
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
    "source_sync_worker_execution_enabled",
    "source_cache_runtime_enabled",
    "evidence_ledger_runtime_enabled",
    "public_search_live_fanout_enabled",
    "arbitrary_swhid_fetch_enabled",
    "arbitrary_origin_fetch_enabled",
    "arbitrary_repository_fetch_enabled",
    "content_blob_fetch_enabled",
    "directory_content_traversal_enabled",
    "source_code_download_enabled",
    "source_archive_download_enabled",
    "repository_clone_enabled",
    "origin_crawl_enabled",
    "source_code_execution_enabled",
    "downloads_enabled",
    "mirroring_enabled",
    "file_retrieval_enabled",
    "installs_enabled",
    "execution_enabled",
    "telemetry_enabled",
    "credentials_configured",
    "software_heritage_token_enabled",
    "source_cache_mutated",
    "evidence_ledger_mutated",
    "candidate_index_mutated",
    "public_index_mutated",
    "local_index_mutated",
    "master_index_mutated",
}

INVENTORY_FALSE_FIELDS = {
    "runtime_connector_implemented",
    "live_calls_enabled",
    "software_heritage_api_calls_enabled",
    "source_sync_worker_execution_enabled",
    "source_cache_runtime_enabled",
    "evidence_ledger_runtime_enabled",
    "public_search_live_fanout_enabled",
    "arbitrary_swhid_fetch_enabled",
    "arbitrary_origin_fetch_enabled",
    "arbitrary_repository_fetch_enabled",
    "swhid_resolution_enabled",
    "origin_lookup_enabled",
    "visit_lookup_enabled",
    "snapshot_lookup_enabled",
    "release_lookup_enabled",
    "revision_lookup_enabled",
    "directory_lookup_enabled",
    "content_blob_fetch_enabled",
    "directory_content_traversal_enabled",
    "source_code_download_enabled",
    "source_archive_download_enabled",
    "repository_clone_enabled",
    "origin_crawl_enabled",
    "source_code_execution_enabled",
    "downloads_enabled",
    "mirroring_enabled",
    "file_retrieval_enabled",
    "installs_enabled",
    "execution_enabled",
    "telemetry_enabled",
    "credentials_configured",
    "software_heritage_token_enabled",
    "master_index_mutation_allowed",
    "public_index_mutation_allowed",
    "candidate_index_mutation_allowed",
}

INVENTORY_TRUE_FIELDS = {
    "approval_required",
    "operator_approval_required",
    "swhid_policy_review_required",
    "origin_url_policy_review_required",
    "repository_identity_review_required",
    "source_code_content_policy_review_required",
    "token_auth_review_required",
    "source_policy_review_required",
    "user_agent_contact_required",
    "rate_limit_required",
    "timeout_required",
    "circuit_breaker_required",
    "cache_required_before_public_use",
    "evidence_attribution_required",
}


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
        errors.append(f"missing required artifact: {path.relative_to(REPO_ROOT)}")
        return ""
    text = path.read_text(encoding="utf-8").casefold()
    for phrase in phrases:
        if phrase.casefold() not in text:
            errors.append(f"{label or path.name} missing required phrase: {phrase}")
    return text


def scan_sensitive_text(text: str, label: str, errors: list[str]) -> None:
    if re.search(r"\b[A-Za-z]:\\+(?:users|documents|downloads|desktop|projects|private|temp|windows)\\+", text):
        errors.append(f"{label} contains a prohibited private absolute path")
    if re.search(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", text, re.I):
        errors.append(f"{label} contains an email/contact value")
    if re.search(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", text):
        errors.append(f"{label} contains an IP address")
    if re.search(r"https?://[^\s/]*@|\b(?:file|data|javascript):", text, re.I):
        errors.append(f"{label} contains a credentialed, file, data, or javascript URL")


def validate() -> list[str]:
    errors: list[str] = []
    if not AUDIT_DIR.exists():
        errors.append(f"missing audit directory: {AUDIT_DIR.relative_to(REPO_ROOT)}")
    else:
        present = {path.name for path in AUDIT_DIR.iterdir() if path.is_file()}
        missing = sorted(REQUIRED_FILES - present)
        if missing:
            errors.append(f"audit pack missing files: {', '.join(missing)}")
    for path in (REPORT_PATH, INVENTORY_PATH, DOC_PATH):
        if not path.exists():
            errors.append(f"missing required artifact: {path.relative_to(REPO_ROOT)}")

    if REPORT_PATH.exists():
        loaded = load_json(REPORT_PATH)
        if not isinstance(loaded, Mapping):
            errors.append("report JSON must be an object")
        else:
            if loaded.get("readiness_decision") not in VALID_READINESS:
                errors.append("report.readiness_decision is invalid")
            check_false(loaded, REPORT_FALSE_FIELDS, "report", errors)
            approval = loaded.get("approval_gate_review", {})
            if not isinstance(approval, Mapping):
                errors.append("report.approval_gate_review must be an object")
            else:
                if approval.get("connector_approved_now") is not False:
                    errors.append("report.approval_gate_review.connector_approved_now must be false")
                if approval.get("decision") != "runtime_blocked":
                    errors.append("report.approval_gate_review.decision must be runtime_blocked")
            gates = loaded.get("swhid_origin_repository_source_policy_gate_review", {})
            if not isinstance(gates, Mapping):
                errors.append("report.swhid_origin_repository_source_policy_gate_review must be an object")
            else:
                for field in (
                    "swhid_policy_review_required",
                    "origin_url_policy_review_required",
                    "repository_identity_review_required",
                    "source_policy_review_required",
                    "operator_approval_required",
                ):
                    if gates.get(field) is not True:
                        errors.append(f"report.swhid_origin_repository_source_policy_gate_review.{field} must be true")
            content = loaded.get("source_code_content_boundary_review", {})
            if not isinstance(content, Mapping):
                errors.append("report.source_code_content_boundary_review must be an object")
            else:
                for field in (
                    "content_blob_fetch_enabled",
                    "raw_file_fetch_enabled",
                    "directory_content_traversal_enabled",
                    "repository_clone_enabled",
                    "source_archive_download_enabled",
                    "origin_crawl_enabled",
                    "source_code_execution_enabled",
                    "source_code_safety_claimed",
                    "source_completeness_claimed",
                    "license_right_clearance_claimed",
                ):
                    if content.get(field) is not False:
                        errors.append(f"report.source_code_content_boundary_review.{field} must be false")
            token = loaded.get("token_auth_boundary_review", {})
            if not isinstance(token, Mapping):
                errors.append("report.token_auth_boundary_review must be an object")
            else:
                if token.get("token_free_v0") is not True:
                    errors.append("report.token_auth_boundary_review.token_free_v0 must be true")
                if token.get("software_heritage_token_enabled") is not False:
                    errors.append("report.token_auth_boundary_review.software_heritage_token_enabled must be false")
            if not loaded.get("source_cache_output_plan"):
                errors.append("report.source_cache_output_plan must be present")
            if not loaded.get("evidence_ledger_output_plan"):
                errors.append("report.evidence_ledger_output_plan must be present")
            acceptance_text = " ".join(str(item).casefold() for item in loaded.get("acceptance_criteria", []))
            for phrase in (
                "approval",
                "swhid",
                "origin url",
                "repository identity",
                "source-code-content",
                "token/auth",
                "source policy",
                "user-agent/contact",
                "rate limits",
                "cache",
                "evidence attribution",
                "kill switch",
                "operator approval",
            ):
                if phrase not in acceptance_text:
                    errors.append(f"report.acceptance_criteria missing {phrase}")
    if INVENTORY_PATH.exists():
        loaded = load_json(INVENTORY_PATH)
        if not isinstance(loaded, Mapping):
            errors.append("inventory JSON must be an object")
        else:
            if loaded.get("status") != "planning_only":
                errors.append("inventory.status must be planning_only")
            if loaded.get("connector_id") != "software_heritage_connector":
                errors.append("inventory.connector_id must be software_heritage_connector")
            check_false(loaded, INVENTORY_FALSE_FIELDS, "inventory", errors)
            check_true(loaded, INVENTORY_TRUE_FIELDS, "inventory", errors)

    if AUDIT_DIR.exists():
        require_phrases(
            AUDIT_DIR / "RUNTIME_BOUNDARY.md",
            (
                "does not implement",
                "no live software heritage calls",
                "no software heritage api endpoints are called",
                "no swhids are resolved live",
                "no origins, visits, snapshots, releases, revisions, directories, or content blobs are fetched",
                "no source files or source archives are downloaded",
                "no repositories are cloned",
                "no source code is inspected or executed",
                "no source-cache records",
                "no evidence-ledger records",
                "no credentials or software heritage tokens",
                "no indexes are mutated",
            ),
            errors,
        )
        require_phrases(
            AUDIT_DIR / "SWHID_ORIGIN_REPOSITORY_AND_SOURCE_POLICY_GATE_REVIEW.md",
            ("swhid", "origin url", "repository identity", "source policy", "operator approval", "pending", "does not fabricate"),
            errors,
        )
        require_phrases(
            AUDIT_DIR / "SOURCE_CODE_CONTENT_BOUNDARY_REVIEW.md",
            (
                "source-code metadata",
                "content blob fetch remains disabled",
                "raw file fetch remains disabled",
                "directory content traversal remains disabled",
                "repository clone remains disabled",
                "source archive download remains disabled",
                "origin crawl remains disabled",
                "source code execution remains disabled",
                "source-code safety claims are forbidden",
                "source completeness claims are forbidden",
            ),
            errors,
        )
        require_phrases(
            AUDIT_DIR / "TOKEN_AUTH_BOUNDARY_REVIEW.md",
            ("token-free", "software heritage tokens", "not configured", "future explicit policy"),
            errors,
        )
        require_phrases(
            AUDIT_DIR / "USER_AGENT_CONTACT_AND_RATE_LIMIT_REVIEW.md",
            ("user-agent", "contact", "rate-limit", "timeout", "circuit breaker"),
            errors,
        )
        require_phrases(
            AUDIT_DIR / "SWHID_ORIGIN_REPOSITORY_REVIEW_AND_NORMALIZATION_PLAN.md",
            (
                "reviewed source record",
                "raw public query parameter",
                "private repository",
                "credentialed repository",
                "unreviewed origin url",
                "swhid syntax validation",
                "origin url normalization",
                "public-safe fingerprint",
                "no raw private origin/repository publication",
            ),
            errors,
        )
        require_phrases(
            AUDIT_DIR / "IMPLEMENTATION_PHASES.md",
            (
                "phase 0: keep disabled",
                "phase 1: local dry-run",
                "phase 2: local approved live metadata probe",
                "phase 3: source sync worker",
                "phase 4: public index rebuild",
                "phase 5: hosted connector worker",
            ),
            errors,
        )
        require_phrases(
            AUDIT_DIR / "ACCEPTANCE_CRITERIA.md",
            (
                "p76 approval complete",
                "swhid policy reviewed",
                "origin url policy reviewed",
                "repository identity policy reviewed",
                "source-code-content risk policy reviewed",
                "token/auth boundary reviewed",
                "source policy reviewed",
                "user-agent/contact configured",
                "rate limits approved",
                "cache destination",
                "evidence attribution",
                "kill switch",
                "operator approval",
            ),
            errors,
        )
        require_phrases(
            AUDIT_DIR / "DO_NOT_IMPLEMENT_YET.md",
            (
                "no software heritage api calls",
                "no connector runtime",
                "no source cache writes",
                "no evidence ledger writes",
                "no public search live fanout",
                "no arbitrary swhid/origin/repository fetch",
                "no swhid live resolution",
                "no origin lookup",
                "no visit/snapshot/release/revision/directory/content lookup",
                "no content blob fetch",
                "no directory traversal",
                "no source code download",
                "no source archive download",
                "no repository clone",
                "no origin crawl",
                "no source code execution",
                "no index/master mutation",
            ),
            errors,
        )
        combined = "\n".join(path.read_text(encoding="utf-8") for path in AUDIT_DIR.iterdir() if path.is_file())
        scan_sensitive_text(combined, "audit pack", errors)

    if DOC_PATH.exists():
        text = require_phrases(
            DOC_PATH,
            (
                "planning-only",
                "no runtime",
                "no external calls",
                "no arbitrary swhid/origin/repository",
                "no source code download",
                "no content blob fetch",
                "no directory traversal",
                "no repository clone",
                "no mutation",
                "public search must not call software heritage live",
            ),
            errors,
            "operations doc",
        )
        scan_sensitive_text(text, "operations doc", errors)
    return errors


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    errors = validate()
    status = "invalid" if errors else "valid"
    readiness = None
    if REPORT_PATH.exists():
        try:
            loaded = load_json(REPORT_PATH)
            if isinstance(loaded, Mapping):
                readiness = loaded.get("readiness_decision")
        except Exception:
            readiness = None
    if args.json:
        payload = {
            "status": status,
            "report_id": "software_heritage_connector_runtime_planning_v0",
            "readiness_decision": readiness,
            "audit_dir": str(AUDIT_DIR.relative_to(REPO_ROOT)),
            "errors": errors,
        }
        print(json.dumps(payload, indent=2), file=stdout)
    else:
        print(f"status: {status}", file=stdout)
        for error in errors:
            print(f"ERROR: {error}", file=stdout)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
