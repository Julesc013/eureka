#!/usr/bin/env python3
"""Validate Internet Archive Metadata Connector Runtime Planning v0 artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
AUDIT_DIR = REPO_ROOT / "control" / "audits" / "internet-archive-metadata-connector-runtime-planning-v0"
REPORT_PATH = AUDIT_DIR / "internet_archive_metadata_connector_runtime_planning_report.json"
INVENTORY_PATH = REPO_ROOT / "control" / "inventory" / "connectors" / "internet_archive_metadata_connector_runtime_plan.json"
DOC_PATH = REPO_ROOT / "docs" / "operations" / "INTERNET_ARCHIVE_METADATA_CONNECTOR_RUNTIME_PLAN.md"

REQUIRED_FILES = {
    "README.md",
    "PLANNING_SUMMARY.md",
    "READINESS_DECISION.md",
    "APPROVAL_GATE_REVIEW.md",
    "SOURCE_POLICY_AND_OPERATOR_GATE_REVIEW.md",
    "USER_AGENT_CONTACT_AND_RATE_LIMIT_REVIEW.md",
    "RUNTIME_BOUNDARY.md",
    "CONNECTOR_RUNTIME_ARCHITECTURE_PLAN.md",
    "SOURCE_SYNC_JOB_FLOW.md",
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
    "internet_archive_metadata_connector_runtime_planning_report.json",
}

VALID_READINESS = {
    "ready_for_local_dry_run_runtime_after_operator_approval",
    "ready_for_source_sync_worker_runtime_after_operator_approval",
    "blocked_connector_approval_missing",
    "blocked_connector_approval_pending",
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
    "archive_org_called",
    "internet_archive_api_called",
    "source_sync_worker_execution_enabled",
    "source_cache_runtime_enabled",
    "evidence_ledger_runtime_enabled",
    "public_search_live_fanout_enabled",
    "downloads_enabled",
    "mirroring_enabled",
    "file_retrieval_enabled",
    "installs_enabled",
    "execution_enabled",
    "telemetry_enabled",
    "credentials_configured",
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
    "source_sync_worker_execution_enabled",
    "source_cache_runtime_enabled",
    "evidence_ledger_runtime_enabled",
    "public_search_live_fanout_enabled",
    "downloads_enabled",
    "mirroring_enabled",
    "file_retrieval_enabled",
    "installs_enabled",
    "execution_enabled",
    "telemetry_enabled",
    "credentials_configured",
    "master_index_mutation_allowed",
    "public_index_mutation_allowed",
    "candidate_index_mutation_allowed",
}

INVENTORY_TRUE_FIELDS = {
    "approval_required",
    "operator_approval_required",
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

    report: Mapping[str, Any] = {}
    inventory: Mapping[str, Any] = {}
    if REPORT_PATH.exists():
        loaded = load_json(REPORT_PATH)
        if not isinstance(loaded, Mapping):
            errors.append("report JSON must be an object")
        else:
            report = loaded
            if report.get("readiness_decision") not in VALID_READINESS:
                errors.append("report.readiness_decision is invalid")
            check_false(report, REPORT_FALSE_FIELDS, "report", errors)
            approval = report.get("approval_gate_review", {})
            if not isinstance(approval, Mapping):
                errors.append("report.approval_gate_review must be an object")
            else:
                if approval.get("connector_approved_now") is not False:
                    errors.append("report.approval_gate_review.connector_approved_now must be false")
                if approval.get("decision") != "runtime_blocked":
                    errors.append("report.approval_gate_review.decision must be runtime_blocked")
            if not report.get("source_cache_output_plan"):
                errors.append("report.source_cache_output_plan must be present")
            if not report.get("evidence_ledger_output_plan"):
                errors.append("report.evidence_ledger_output_plan must be present")
            acceptance_text = " ".join(str(item).casefold() for item in report.get("acceptance_criteria", []))
            for phrase in ("approval", "source policy", "user-agent/contact", "rate limits", "cache", "evidence attribution", "kill switch", "operator approval"):
                if phrase not in acceptance_text:
                    errors.append(f"report.acceptance_criteria missing {phrase}")
    if INVENTORY_PATH.exists():
        loaded = load_json(INVENTORY_PATH)
        if not isinstance(loaded, Mapping):
            errors.append("inventory JSON must be an object")
        else:
            inventory = loaded
            if inventory.get("status") != "planning_only":
                errors.append("inventory.status must be planning_only")
            if inventory.get("connector_id") != "internet_archive_metadata_connector":
                errors.append("inventory.connector_id must be internet_archive_metadata_connector")
            check_false(inventory, INVENTORY_FALSE_FIELDS, "inventory", errors)
            check_true(inventory, INVENTORY_TRUE_FIELDS, "inventory", errors)

    if AUDIT_DIR.exists():
        require_phrases(
            AUDIT_DIR / "RUNTIME_BOUNDARY.md",
            ("does not implement", "no live ia calls", "no source-cache records", "no evidence-ledger records", "no indexes are mutated"),
            errors,
        )
        require_phrases(
            AUDIT_DIR / "SOURCE_POLICY_AND_OPERATOR_GATE_REVIEW.md",
            ("source policy", "operator approval", "pending", "no fabricate"),
            errors,
        )
        require_phrases(
            AUDIT_DIR / "USER_AGENT_CONTACT_AND_RATE_LIMIT_REVIEW.md",
            ("user-agent", "contact", "rate-limit", "timeout", "circuit breaker"),
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
            ("p71 approval complete", "source policy reviewed", "user-agent/contact configured", "rate limits approved", "cache destination", "evidence attribution", "kill switch", "operator approval"),
            errors,
        )
        require_phrases(
            AUDIT_DIR / "DO_NOT_IMPLEMENT_YET.md",
            ("no ia api calls", "no connector runtime", "no source cache writes", "no evidence ledger writes", "no public search live fanout", "no index/master mutation"),
            errors,
        )
        combined = "\n".join(path.read_text(encoding="utf-8") for path in AUDIT_DIR.iterdir() if path.is_file())
        scan_sensitive_text(combined, "audit pack", errors)

    if DOC_PATH.exists():
        text = require_phrases(
            DOC_PATH,
            ("planning-only", "no runtime", "no external calls", "no mutation", "metadata-only", "public search must not call internet archive live"),
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
            "report_id": "internet_archive_metadata_connector_runtime_planning_v0",
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
