#!/usr/bin/env python3
"""Validate Object/Source/Comparison Page Runtime Planning v0 artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
AUDIT_DIR = REPO_ROOT / "control" / "audits" / "object-source-comparison-page-runtime-planning-v0"
REPORT_PATH = AUDIT_DIR / "object_source_comparison_page_runtime_planning_report.json"
INVENTORY_PATH = REPO_ROOT / "control" / "inventory" / "pages" / "page_runtime_plan.json"
DOC_PATH = REPO_ROOT / "docs" / "operations" / "OBJECT_SOURCE_COMPARISON_PAGE_RUNTIME_PLAN.md"

REQUIRED_FILES = {
    "README.md",
    "PLANNING_SUMMARY.md",
    "READINESS_DECISION.md",
    "PAGE_CONTRACT_GATE_REVIEW.md",
    "PUBLIC_SEARCH_AND_INDEX_GATE_REVIEW.md",
    "HOSTED_DEPLOYMENT_GATE_REVIEW.md",
    "ROUTING_AND_IDENTIFIER_POLICY.md",
    "RUNTIME_BOUNDARY.md",
    "PAGE_RUNTIME_ARCHITECTURE_PLAN.md",
    "OBJECT_PAGE_RUNTIME_PLAN.md",
    "SOURCE_PAGE_RUNTIME_PLAN.md",
    "COMPARISON_PAGE_RUNTIME_PLAN.md",
    "DATA_INPUT_MODEL.md",
    "RESPONSE_AND_RENDERING_MODEL.md",
    "STATIC_AND_LITE_FALLBACK_MODEL.md",
    "PUBLIC_SEARCH_INTEGRATION_PLAN.md",
    "SOURCE_EVIDENCE_CANDIDATE_BOUNDARY.md",
    "PRIVACY_RIGHTS_RISK_REVIEW.md",
    "SECURITY_AND_ABUSE_REVIEW.md",
    "IMPLEMENTATION_PHASES.md",
    "ACCEPTANCE_CRITERIA.md",
    "DO_NOT_IMPLEMENT_YET.md",
    "COMMAND_RESULTS.md",
    "REMAINING_BLOCKERS.md",
    "NEXT_STEPS.md",
    "object_source_comparison_page_runtime_planning_report.json",
}

VALID_READINESS = {
    "ready_for_local_dry_run_runtime_after_operator_approval",
    "ready_for_hosted_runtime_after_operator_approval",
    "ready_for_static_demo_only",
    "blocked_object_page_contract_missing",
    "blocked_source_page_contract_missing",
    "blocked_comparison_page_contract_missing",
    "blocked_public_search_contract_missing",
    "blocked_public_index_contract_missing",
    "blocked_public_search_safety_failed",
    "blocked_hosted_deployment_unverified",
    "blocked_page_identifier_policy_missing",
    "blocked_privacy_policy_incomplete",
    "blocked_source_evidence_boundary_incomplete",
    "blocked_other",
}

REPORT_FALSE_FIELDS = {
    "runtime_page_implementation_enabled",
    "object_page_runtime_implemented",
    "source_page_runtime_implemented",
    "comparison_page_runtime_implemented",
    "persistent_page_store_implemented",
    "public_search_runtime_mutated",
    "public_search_page_links_enabled_now",
    "hosted_page_runtime_verified",
    "live_source_calls_enabled",
    "external_calls_performed",
    "arbitrary_url_fetch_enabled",
    "local_path_access_enabled",
    "downloads_enabled",
    "uploads_enabled",
    "installs_enabled",
    "execution_enabled",
    "telemetry_enabled",
    "accounts_enabled",
    "source_cache_mutated",
    "evidence_ledger_mutated",
    "candidate_index_mutated",
    "candidate_promotion_performed",
    "public_index_mutated",
    "local_index_mutated",
    "master_index_mutated",
}

INVENTORY_FALSE_FIELDS = {
    "runtime_page_implementation_enabled",
    "object_page_runtime_implemented",
    "source_page_runtime_implemented",
    "comparison_page_runtime_implemented",
    "persistent_page_store_implemented",
    "public_search_page_links_enabled_now",
    "hosted_page_runtime_verified",
    "live_source_calls_enabled",
    "arbitrary_url_fetch_enabled",
    "local_path_access_enabled",
    "downloads_enabled",
    "uploads_enabled",
    "installs_enabled",
    "execution_enabled",
    "telemetry_enabled",
    "accounts_enabled",
    "source_cache_mutation_allowed",
    "evidence_ledger_mutation_allowed",
    "candidate_index_mutation_allowed",
    "candidate_promotion_allowed",
    "public_index_mutation_allowed",
    "master_index_mutation_allowed",
}

INVENTORY_TRUE_FIELDS = {
    "safe_page_identifier_policy_required",
    "public_search_safety_required",
    "hosted_deployment_required_for_hosted_runtime",
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
            gate = loaded.get("page_contract_gate_review", {})
            if not isinstance(gate, Mapping):
                errors.append("report.page_contract_gate_review must be an object")
            else:
                for field in ("object_page_contract_valid", "source_page_contract_valid", "comparison_page_contract_valid"):
                    if gate.get(field) is not True:
                        errors.append(f"report.page_contract_gate_review.{field} must be true")
            search = loaded.get("public_search_index_gate_review", {})
            if not isinstance(search, Mapping):
                errors.append("report.public_search_index_gate_review must be an object")
            else:
                for field in ("public_search_contract_valid", "public_result_card_contract_valid", "public_index_format_valid", "public_index_artifacts_valid", "local_public_search_runtime_valid", "blocked_request_safety_valid"):
                    if search.get(field) is not True:
                        errors.append(f"report.public_search_index_gate_review.{field} must be true")
                if search.get("page_links_enabled_now") is not False:
                    errors.append("report.public_search_index_gate_review.page_links_enabled_now must be false")
            hosted = loaded.get("hosted_deployment_gate_review", {})
            if not isinstance(hosted, Mapping):
                errors.append("report.hosted_deployment_gate_review must be an object")
            else:
                if hosted.get("hosted_backend_verified") is not False:
                    errors.append("report.hosted_deployment_gate_review.hosted_backend_verified must be false")
            acceptance_text = " ".join(str(item).casefold() for item in loaded.get("acceptance_criteria", []))
            for phrase in (
                "object page contract",
                "source page contract",
                "comparison page contract",
                "public search safety",
                "public index",
                "safe page id",
                "source/evidence/candidate",
                "hosted deployment",
                "blocked",
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
            AUDIT_DIR / "ROUTING_AND_IDENTIFIER_POLICY.md",
            (
                "/object/{object_id}",
                "/source/{source_id}",
                "/comparison/{comparison_id}",
                "public-index object ids",
                "local paths",
                "arbitrary urls",
                "not interpreted as filesystem paths",
                "must never trigger live source calls",
            ),
            errors,
        )
        require_phrases(
            AUDIT_DIR / "RUNTIME_BOUNDARY.md",
            (
                "does not implement page runtime",
                "no /object, /source, or /comparison routes are added",
                "no runtime page renderer",
                "no public search behavior changes",
                "no live source calls",
                "no source-cache/evidence-ledger/candidate/public/master mutation",
                "no downloads/installers/execution",
                "no telemetry/accounts",
            ),
            errors,
        )
        require_phrases(
            AUDIT_DIR / "DATA_INPUT_MODEL.md",
            (
                "public index documents",
                "reviewed source inventory records",
                "candidate records only if labelled candidate/review-required",
                "arbitrary local paths",
                "arbitrary urls",
                "raw unreviewed connector responses",
            ),
            errors,
        )
        require_phrases(
            AUDIT_DIR / "STATIC_AND_LITE_FALLBACK_MODEL.md",
            ("static demo pages remain available", "lite/text pages work without js", "backend unavailable"),
            errors,
        )
        require_phrases(
            AUDIT_DIR / "SOURCE_EVIDENCE_CANDIDATE_BOUNDARY.md",
            ("observations, not truth", "candidate records are provisional", "must not promote candidates", "must not mutate source/evidence/candidate records"),
            errors,
        )
        require_phrases(
            AUDIT_DIR / "ACCEPTANCE_CRITERIA.md",
            (
                "object page contract valid",
                "source page contract valid",
                "comparison page contract valid",
                "public search safety valid",
                "public index contract valid",
                "safe page id policy accepted",
                "source/evidence/candidate boundary accepted",
                "hosted deployment evidence for hosted runtime",
                "route tests for path traversal/arbitrary url/source selector blocked",
                "operator approval",
            ),
            errors,
        )
        require_phrases(
            AUDIT_DIR / "DO_NOT_IMPLEMENT_YET.md",
            (
                "no runtime page routes",
                "no object/source/comparison runtime renderer",
                "no database tables",
                "no persistent page store",
                "no public search mutation",
                "no live source calls",
                "no source cache writes",
                "no evidence ledger writes",
                "no candidate promotion",
                "no public/master index mutation",
                "no downloads/installers/execution",
                "no telemetry/accounts",
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
                "no runtime routes",
                "no live source",
                "no mutation",
                "safe page identifier policy",
                "static/lite fallback",
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
            "report_id": "object_source_comparison_page_runtime_planning_v0",
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
