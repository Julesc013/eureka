#!/usr/bin/env python3
"""Validate combined Source Cache and Evidence Ledger v0 artifacts."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "scripts"))

from _p70_contract_common import load_json_object, print_report  # noqa: E402
from validate_source_cache_contract import validate_source_cache_contract  # noqa: E402
from validate_evidence_ledger_contract import validate_evidence_ledger_contract  # noqa: E402


AUDIT_DIR = REPO_ROOT / "control/audits/source-cache-evidence-ledger-v0"
REPORT_PATH = AUDIT_DIR / "source_cache_evidence_ledger_report.json"
REQUIRED_AUDIT_FILES = {
    "README.md",
    "CONTRACT_SUMMARY.md",
    "SOURCE_CACHE_RECORD_SCHEMA.md",
    "SOURCE_CACHE_MANIFEST_SCHEMA.md",
    "EVIDENCE_LEDGER_RECORD_SCHEMA.md",
    "EVIDENCE_LEDGER_MANIFEST_SCHEMA.md",
    "CACHE_LIFECYCLE_MODEL.md",
    "EVIDENCE_LIFECYCLE_MODEL.md",
    "SOURCE_POLICY_AND_APPROVAL_GATES.md",
    "FRESHNESS_AND_INVALIDATION_MODEL.md",
    "PROVENANCE_FIXITY_CHECKSUM_MODEL.md",
    "NORMALIZED_EVIDENCE_OBSERVATION_MODEL.md",
    "PRIVACY_AND_REDACTION_POLICY.md",
    "RIGHTS_AND_RISK_POLICY.md",
    "CANDIDATE_AND_PUBLIC_INDEX_RELATIONSHIP.md",
    "MASTER_INDEX_RELATIONSHIP.md",
    "SOURCE_SYNC_WORKER_RELATIONSHIP.md",
    "QUERY_INTELLIGENCE_RELATIONSHIP.md",
    "NO_RUNTIME_AND_NO_MUTATION_POLICY.md",
    "EXAMPLE_SOURCE_CACHE_REVIEW.md",
    "EXAMPLE_EVIDENCE_LEDGER_REVIEW.md",
    "FUTURE_RUNTIME_PATH.md",
    "COMMAND_RESULTS.md",
    "REMAINING_BLOCKERS.md",
    "NEXT_STEPS.md",
    "source_cache_evidence_ledger_report.json",
}
REPORT_FALSE = {
    "runtime_source_cache_implemented",
    "persistent_source_cache_implemented",
    "runtime_evidence_ledger_implemented",
    "persistent_evidence_ledger_implemented",
    "source_cache_runtime_implemented",
    "evidence_ledger_runtime_implemented",
    "cache_write_performed",
    "ledger_write_performed",
    "live_sources_enabled_by_default",
    "public_query_fanout_allowed",
    "arbitrary_url_cache_allowed",
    "raw_payload_storage_allowed_now",
    "private_data_storage_allowed_now",
    "executable_payload_storage_allowed_now",
    "accepted_as_truth_by_default",
    "automatic_promotion_allowed",
    "live_source_called",
    "external_calls_performed",
    "source_cache_mutation_allowed_now",
    "evidence_ledger_mutation_allowed_now",
    "candidate_index_mutation_allowed_now",
    "public_index_mutation_allowed_now",
    "local_index_mutation_allowed_now",
    "master_index_mutation_allowed",
    "telemetry_implemented",
    "credentials_configured",
}
REL_DOCS = {
    "control/audits/source-cache-evidence-ledger-v0/SOURCE_SYNC_WORKER_RELATIONSHIP.md": ("approved source sync workers", "writes no cache/ledger state"),
    "control/audits/source-cache-evidence-ledger-v0/QUERY_INTELLIGENCE_RELATIONSHIP.md": ("probe queue", "demand dashboard"),
    "control/audits/source-cache-evidence-ledger-v0/CANDIDATE_AND_PUBLIC_INDEX_RELATIONSHIP.md": ("candidate", "public index"),
    "control/audits/source-cache-evidence-ledger-v0/MASTER_INDEX_RELATIONSHIP.md": ("not master-index truth", "promotion policy"),
}


def validate_combined_contract() -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    source_report = validate_source_cache_contract()
    evidence_report = validate_evidence_ledger_contract()
    if source_report.get("status") != "valid":
        errors.append("source cache contract validator failed.")
        errors.extend(source_report.get("errors", []))
    if evidence_report.get("status") != "valid":
        errors.append("evidence ledger contract validator failed.")
        errors.extend(evidence_report.get("errors", []))
    _validate_audit_pack(errors)
    report = load_json_object(REPORT_PATH, errors, "source_cache_evidence_ledger_report.json")
    if report:
        for key in REPORT_FALSE:
            if report.get(key) is not False:
                errors.append(f"report {key} must be false.")
        if report.get("report_id") != "source_cache_evidence_ledger_v0":
            errors.append("report_id must be source_cache_evidence_ledger_v0.")
    return {
        "status": "valid" if not errors else "invalid",
        "created_by": "source_cache_evidence_ledger_contract_validator_v0",
        "report_id": report.get("report_id") if report else None,
        "errors": errors,
        "warnings": warnings,
    }


def _validate_audit_pack(errors: list[str]) -> None:
    if not AUDIT_DIR.is_dir():
        errors.append("control/audits/source-cache-evidence-ledger-v0 missing.")
        return
    present = {path.name for path in AUDIT_DIR.iterdir() if path.is_file()}
    missing = REQUIRED_AUDIT_FILES - present
    if missing:
        errors.append(f"audit pack missing files: {', '.join(sorted(missing))}")
    for rel, phrases in REL_DOCS.items():
        path = REPO_ROOT / rel
        if not path.is_file():
            errors.append(f"{rel} missing.")
            continue
        text = path.read_text(encoding="utf-8").casefold()
        for phrase in phrases:
            if phrase not in text:
                errors.append(f"{rel} missing required phrase: {phrase}")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    report = validate_combined_contract()
    print_report(report, args.json)
    return 0 if report["status"] == "valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
