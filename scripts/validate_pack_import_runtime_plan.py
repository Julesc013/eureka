#!/usr/bin/env python3
"""Validate Pack Import Runtime Planning v0 artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
AUDIT_DIR = REPO_ROOT / "control" / "audits" / "pack-import-runtime-planning-v0"
REPORT_PATH = AUDIT_DIR / "pack_import_runtime_planning_report.json"
INVENTORY_PATH = REPO_ROOT / "control" / "inventory" / "packs" / "pack_import_runtime_plan.json"
DOC_PATH = REPO_ROOT / "docs" / "operations" / "PACK_IMPORT_RUNTIME_PLAN.md"

REQUIRED_FILES = {
    "README.md",
    "PLANNING_SUMMARY.md",
    "READINESS_DECISION.md",
    "PACK_CONTRACT_GATE_REVIEW.md",
    "VALIDATE_ONLY_IMPORT_GATE_REVIEW.md",
    "QUARANTINE_AND_STAGING_GATE_REVIEW.md",
    "REVIEW_QUEUE_AND_PROMOTION_GATE_REVIEW.md",
    "RUNTIME_BOUNDARY.md",
    "PACK_IMPORT_RUNTIME_ARCHITECTURE_PLAN.md",
    "PACK_INPUT_AND_TRUST_MODEL.md",
    "VALIDATION_PIPELINE_PLAN.md",
    "QUARANTINE_STAGING_AND_INSPECTION_FLOW.md",
    "IMPORT_REPORT_AND_DIFF_MODEL.md",
    "SOURCE_PACK_IMPORT_PLAN.md",
    "EVIDENCE_PACK_IMPORT_PLAN.md",
    "INDEX_PACK_IMPORT_PLAN.md",
    "CONTRIBUTION_PACK_IMPORT_PLAN.md",
    "PACK_SET_IMPORT_PLAN.md",
    "PRIVACY_PATH_TRAVERSAL_AND_SECRET_POLICY.md",
    "EXECUTABLE_PAYLOAD_AND_CONTENT_SAFETY_POLICY.md",
    "RIGHTS_RISK_AND_PROVENANCE_REVIEW.md",
    "MUTATION_AND_PROMOTION_BOUNDARY.md",
    "FAILURE_ROLLBACK_AND_AUDIT_MODEL.md",
    "PUBLIC_CONTRIBUTION_BOUNDARY.md",
    "IMPLEMENTATION_PHASES.md",
    "ACCEPTANCE_CRITERIA.md",
    "DO_NOT_IMPLEMENT_YET.md",
    "COMMAND_RESULTS.md",
    "REMAINING_BLOCKERS.md",
    "NEXT_STEPS.md",
    "pack_import_runtime_planning_report.json",
}

VALID_READINESS = {
    "ready_for_local_dry_run_runtime_after_operator_approval",
    "ready_for_local_quarantine_runtime_after_operator_approval",
    "blocked_source_pack_contract_missing",
    "blocked_evidence_pack_contract_missing",
    "blocked_index_pack_contract_missing",
    "blocked_contribution_pack_contract_missing",
    "blocked_pack_set_validator_missing",
    "blocked_validate_only_import_missing",
    "blocked_import_report_contract_missing",
    "blocked_quarantine_staging_model_missing",
    "blocked_staged_pack_inspector_missing",
    "blocked_review_queue_contract_missing",
    "blocked_privacy_path_secret_policy_missing",
    "blocked_executable_payload_policy_missing",
    "blocked_mutation_boundary_incomplete",
    "blocked_other",
}

REPORT_FALSE_FIELDS = {
    "pack_import_runtime_implemented",
    "validate_only_runtime_implemented",
    "quarantine_runtime_implemented",
    "staging_runtime_implemented",
    "promotion_runtime_implemented",
    "public_contribution_intake_enabled",
    "upload_endpoint_enabled",
    "admin_endpoint_enabled",
    "pack_content_execution_enabled",
    "pack_url_fetching_enabled",
    "arbitrary_local_path_enabled",
    "source_cache_mutated",
    "evidence_ledger_mutated",
    "candidate_index_mutated",
    "public_index_mutated",
    "local_index_mutated",
    "master_index_mutated",
    "promotion_decision_created",
    "accepted_record_created",
    "external_calls_performed",
    "live_source_called",
    "telemetry_enabled",
    "accounts_enabled",
}

INVENTORY_FALSE_FIELDS = {
    "pack_import_runtime_implemented",
    "validate_only_runtime_implemented",
    "quarantine_runtime_implemented",
    "staging_runtime_implemented",
    "promotion_runtime_implemented",
    "public_contribution_intake_enabled",
    "upload_endpoint_enabled",
    "admin_endpoint_enabled",
    "pack_content_execution_enabled",
    "pack_url_fetching_enabled",
    "arbitrary_local_path_enabled",
    "source_cache_mutation_allowed",
    "evidence_ledger_mutation_allowed",
    "candidate_index_mutation_allowed",
    "public_index_mutation_allowed",
    "local_index_mutation_allowed",
    "master_index_mutation_allowed",
    "telemetry_enabled",
    "accounts_enabled",
}

INVENTORY_TRUE_FIELDS = {
    "source_pack_contract_required",
    "evidence_pack_contract_required",
    "index_pack_contract_required",
    "contribution_pack_contract_required",
    "pack_set_validator_required",
    "validate_only_import_required",
    "quarantine_staging_required",
    "staged_pack_inspector_required",
    "review_queue_required",
    "operator_approval_required",
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
            gate = loaded.get("pack_contract_gate_review", {})
            if not isinstance(gate, Mapping):
                errors.append("report.pack_contract_gate_review must be an object")
            else:
                for field in (
                    "source_pack_contract_valid",
                    "evidence_pack_contract_valid",
                    "index_pack_contract_valid",
                    "contribution_pack_contract_valid",
                    "pack_set_validator_valid",
                    "examples_valid",
                    "validators_present",
                ):
                    if gate.get(field) is not True:
                        errors.append(f"report.pack_contract_gate_review.{field} must be true")
            validate_only = loaded.get("validate_only_import_gate_review", {})
            if not isinstance(validate_only, Mapping):
                errors.append("report.validate_only_import_gate_review must be an object")
            else:
                for field in (
                    "validate_only_import_tool_valid",
                    "known_examples_valid",
                    "import_report_contract_valid",
                    "no_mutation_guarantee_present",
                    "report_output_valid",
                ):
                    if validate_only.get(field) is not True:
                        errors.append(f"report.validate_only_import_gate_review.{field} must be true")
            staging = loaded.get("quarantine_staging_gate_review", {})
            if not isinstance(staging, Mapping):
                errors.append("report.quarantine_staging_gate_review must be an object")
            else:
                for field in (
                    "local_quarantine_staging_model_valid",
                    "staging_report_path_contract_valid",
                    "local_staging_manifest_valid",
                    "staged_pack_inspector_valid",
                    "path_policy_present",
                    "public_private_data_boundary_present",
                ):
                    if staging.get(field) is not True:
                        errors.append(f"report.quarantine_staging_gate_review.{field} must be true")
            review = loaded.get("review_queue_promotion_gate_review", {})
            if not isinstance(review, Mapping):
                errors.append("report.review_queue_promotion_gate_review must be an object")
            else:
                for field in ("master_index_review_queue_contract_valid", "promotion_policy_present", "candidate_review_policy_present"):
                    if review.get(field) is not True:
                        errors.append(f"report.review_queue_promotion_gate_review.{field} must be true")
                for field in ("accepted_record_mutation_enabled", "runtime_implementation_present"):
                    if review.get(field) is not False:
                        errors.append(f"report.review_queue_promotion_gate_review.{field} must be false")
            acceptance_text = " ".join(str(item).casefold() for item in loaded.get("acceptance_criteria", []))
            for phrase in (
                "source pack contract",
                "evidence pack contract",
                "index pack contract",
                "contribution pack contract",
                "pack set validator",
                "validate-only import",
                "import report contract",
                "local quarantine/staging",
                "staged-pack inspector",
                "master index review queue",
                "privacy/path/secret policy",
                "executable payload policy",
                "mutation/promotion boundary",
                "rollback/audit model",
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
            check_false(loaded, INVENTORY_FALSE_FIELDS, "inventory", errors)
            check_true(loaded, INVENTORY_TRUE_FIELDS, "inventory", errors)

    if AUDIT_DIR.exists():
        require_phrases(
            AUDIT_DIR / "RUNTIME_BOUNDARY.md",
            (
                "does not implement pack import runtime",
                "no packs are imported into runtime state",
                "no real packs are staged beyond existing examples",
                "no source cache records are written",
                "no evidence ledger records are written",
                "no candidate index records are written",
                "no public/local/runtime/master indexes are mutated",
                "no promotion decisions are created",
                "no pack contents are executed",
                "no pack urls are fetched",
            ),
            errors,
        )
        require_phrases(
            AUDIT_DIR / "PACK_CONTRACT_GATE_REVIEW.md",
            ("source pack contract status", "evidence pack contract status", "index pack contract status", "contribution pack contract status", "pack set status"),
            errors,
        )
        require_phrases(
            AUDIT_DIR / "VALIDATE_ONLY_IMPORT_GATE_REVIEW.md",
            ("validate-only import tool status", "import report contract status", "no-mutation guarantee status"),
            errors,
        )
        require_phrases(
            AUDIT_DIR / "QUARANTINE_AND_STAGING_GATE_REVIEW.md",
            ("local quarantine/staging model status", "staging report path contract status", "staged-pack inspector status", "path policy"),
            errors,
        )
        require_phrases(
            AUDIT_DIR / "REVIEW_QUEUE_AND_PROMOTION_GATE_REVIEW.md",
            ("master index review queue contract status", "promotion policy status", "candidate review policy status"),
            errors,
        )
        require_phrases(
            AUDIT_DIR / "PRIVACY_PATH_TRAVERSAL_AND_SECRET_POLICY.md",
            ("reject absolute paths", "reject path traversal", "reject credentials/secrets/api keys/tokens", "no local filesystem scanning beyond approved pack root"),
            errors,
        )
        require_phrases(
            AUDIT_DIR / "EXECUTABLE_PAYLOAD_AND_CONTENT_SAFETY_POLICY.md",
            ("no execution", "no installers", "no scripts", "no package manager invocation", "no malware safety claims"),
            errors,
        )
        require_phrases(
            AUDIT_DIR / "MUTATION_AND_PROMOTION_BOUNDARY.md",
            ("validate-only import may produce reports", "promotion is separate from import", "source cache mutation requires", "evidence ledger mutation requires", "master index mutation requires"),
            errors,
        )
        require_phrases(
            AUDIT_DIR / "ACCEPTANCE_CRITERIA.md",
            (
                "source pack contract valid",
                "evidence pack contract valid",
                "index pack contract valid",
                "contribution pack contract valid",
                "pack set validator valid",
                "validate-only import tool valid",
                "import report contract valid",
                "local quarantine/staging model valid",
                "staged-pack inspector valid",
                "master index review queue contract valid",
                "privacy/path/secret policy accepted",
                "executable payload policy accepted",
                "mutation/promotion boundary accepted",
                "operator approval",
            ),
            errors,
        )
        require_phrases(
            AUDIT_DIR / "DO_NOT_IMPLEMENT_YET.md",
            (
                "no pack import runtime",
                "no real pack staging",
                "no source cache writes",
                "no evidence ledger writes",
                "no candidate index writes",
                "no upload endpoint",
                "no pack content execution",
                "no url fetching from packs",
                "no public/local/master index mutation",
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
                "no pack import runtime",
                "no upload",
                "no execution",
                "no URL fetching",
                "no mutation",
                "validate-first",
                "quarantine-first",
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
            "report_id": "pack_import_runtime_planning_v0",
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
