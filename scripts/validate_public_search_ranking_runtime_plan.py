#!/usr/bin/env python3
"""Validate Public Search Ranking Runtime Planning v0 artifacts."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
AUDIT_DIR = REPO_ROOT / "control" / "audits" / "public-search-ranking-runtime-planning-v0"
REPORT_PATH = AUDIT_DIR / "public_search_ranking_runtime_planning_report.json"
INVENTORY_PATH = REPO_ROOT / "control" / "inventory" / "search" / "public_search_ranking_runtime_plan.json"
DOC_PATH = REPO_ROOT / "docs" / "operations" / "PUBLIC_SEARCH_RANKING_RUNTIME_PLAN.md"

REQUIRED_FILES = {
    "README.md",
    "PLANNING_SUMMARY.md",
    "READINESS_DECISION.md",
    "RANKING_CONTRACT_GATE_REVIEW.md",
    "PUBLIC_SEARCH_AND_INDEX_GATE_REVIEW.md",
    "EVAL_AND_BASELINE_GATE_REVIEW.md",
    "HOSTED_DEPLOYMENT_GATE_REVIEW.md",
    "RUNTIME_BOUNDARY.md",
    "RANKING_RUNTIME_ARCHITECTURE_PLAN.md",
    "RANKING_INPUT_AND_OUTPUT_MODEL.md",
    "RANKING_PIPELINE_PLAN.md",
    "EVIDENCE_WEIGHTED_RANKING_INTEGRATION_PLAN.md",
    "COMPATIBILITY_AWARE_RANKING_INTEGRATION_PLAN.md",
    "RESULT_MERGE_AND_IDENTITY_INTEGRATION_PLAN.md",
    "SEARCH_RESULT_EXPLANATION_INTEGRATION_PLAN.md",
    "EVAL_AND_REGRESSION_PLAN.md",
    "SAFE_FALLBACK_AND_ROLLBACK_MODEL.md",
    "PRIVACY_NO_TELEMETRY_AND_NO_HIDDEN_SCORE_POLICY.md",
    "SECURITY_AND_ABUSE_REVIEW.md",
    "IMPLEMENTATION_PHASES.md",
    "ACCEPTANCE_CRITERIA.md",
    "DO_NOT_IMPLEMENT_YET.md",
    "COMMAND_RESULTS.md",
    "REMAINING_BLOCKERS.md",
    "NEXT_STEPS.md",
    "public_search_ranking_runtime_planning_report.json",
}

VALID_READINESS = {
    "ready_for_local_dry_run_runtime_after_operator_approval",
    "ready_for_hosted_staging_after_operator_approval",
    "ready_for_planning_only",
    "blocked_evidence_weighted_ranking_contract_missing",
    "blocked_compatibility_aware_ranking_contract_missing",
    "blocked_result_merge_contract_missing",
    "blocked_identity_resolution_contract_missing",
    "blocked_search_result_explanation_contract_missing",
    "blocked_public_search_contract_missing",
    "blocked_public_index_contract_missing",
    "blocked_public_search_safety_failed",
    "blocked_eval_gate_incomplete",
    "blocked_external_baseline_unavailable",
    "blocked_hosted_deployment_unverified",
    "blocked_privacy_or_hidden_score_policy_incomplete",
    "blocked_other",
}

REPORT_FALSE_FIELDS = {
    "runtime_ranking_implemented",
    "public_search_ranking_enabled",
    "public_search_order_changed",
    "public_search_response_changed",
    "persistent_ranking_store_implemented",
    "ranking_applied_to_live_search",
    "hidden_scores_enabled",
    "result_suppression_enabled",
    "telemetry_signal_enabled",
    "popularity_signal_enabled",
    "user_profile_signal_enabled",
    "ad_signal_enabled",
    "model_call_enabled",
    "live_source_calls_enabled",
    "external_calls_performed",
    "source_cache_mutated",
    "evidence_ledger_mutated",
    "candidate_index_mutated",
    "public_index_mutated",
    "local_index_mutated",
    "master_index_mutated",
    "candidate_promotion_performed",
}

INVENTORY_FALSE_FIELDS = {
    "runtime_ranking_implemented",
    "public_search_ranking_enabled",
    "public_search_order_changed",
    "public_search_response_changed",
    "persistent_ranking_store_implemented",
    "ranking_applied_to_live_search",
    "hidden_scores_enabled",
    "result_suppression_enabled",
    "telemetry_signal_enabled",
    "popularity_signal_enabled",
    "user_profile_signal_enabled",
    "ad_signal_enabled",
    "model_call_enabled",
    "live_source_calls_enabled",
    "candidate_promotion_allowed",
    "source_cache_mutation_allowed",
    "evidence_ledger_mutation_allowed",
    "candidate_index_mutation_allowed",
    "public_index_mutation_allowed",
    "local_index_mutation_allowed",
    "master_index_mutation_allowed",
}

INVENTORY_TRUE_FIELDS = {
    "evidence_weighted_contract_required",
    "compatibility_aware_contract_required",
    "result_merge_contract_required",
    "identity_resolution_contract_required",
    "search_result_explanation_contract_required",
    "eval_gate_required",
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
            for key in (
                "ranking_contract_gate_review",
                "public_search_index_gate_review",
                "eval_baseline_gate_review",
                "hosted_deployment_gate_review",
            ):
                if not isinstance(loaded.get(key), Mapping):
                    errors.append(f"report.{key} must be an object")
            ranking_gate = loaded.get("ranking_contract_gate_review", {})
            for key in (
                "evidence_weighted_ranking_contract_status",
                "compatibility_aware_ranking_contract_status",
                "result_merge_deduplication_contract_status",
                "identity_resolution_contract_status",
                "search_result_explanation_contract_status",
                "public_result_card_contract_status",
            ):
                if ranking_gate.get(key) != "valid":
                    errors.append(f"report.ranking_contract_gate_review.{key} must be valid")
            public_gate = loaded.get("public_search_index_gate_review", {})
            for key in (
                "public_search_api_contract_status",
                "public_result_card_contract_status",
                "public_search_safety_status",
                "public_index_format_status",
            ):
                if public_gate.get(key) != "valid":
                    errors.append(f"report.public_search_index_gate_review.{key} must be valid")
            hosted = loaded.get("hosted_deployment_gate_review", {})
            if hosted.get("hosted_backend_verified") is not False:
                errors.append("report.hosted_deployment_gate_review.hosted_backend_verified must be false")
            acceptance_text = " ".join(str(item).casefold() for item in loaded.get("acceptance_criteria", []))
            for phrase in (
                "evidence-weighted ranking contract",
                "compatibility-aware ranking contract",
                "result merge/deduplication contract",
                "identity resolution contract",
                "search result explanation contract",
                "public search safety",
                "public index contract",
                "archive evals pass",
                "deterministic tie-break",
                "no telemetry/user-profile/ad/model signals",
                "no result suppression",
                "current-order fallback",
                "hosted deployment evidence required for hosted mode",
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
                "does not implement ranking runtime",
                "no public search order is changed",
                "no public search response is changed",
                "no result suppression occurs",
                "no hidden scores",
                "no telemetry",
                "no source-cache/evidence-ledger/candidate/public/master mutation",
                "no live source calls",
            ),
            errors,
        )
        require_phrases(
            AUDIT_DIR / "RANKING_RUNTIME_ARCHITECTURE_PLAN.md",
            (
                "future modules only",
                "factors.py",
                "evidence_weighted.py",
                "compatibility.py",
                "explain.py",
                "policy.py",
                "EUREKA_PUBLIC_SEARCH_RANKING_ENABLED=0",
            ),
            errors,
        )
        require_phrases(
            AUDIT_DIR / "RANKING_INPUT_AND_OUTPUT_MODEL.md",
            (
                "public index result candidates",
                "result card fields",
                "raw private query",
                "telemetry profile",
                "ad signals",
                "live connector responses",
                "same result set",
                "no suppressed results",
                "current order",
            ),
            errors,
        )
        require_phrases(
            AUDIT_DIR / "EVAL_AND_REGRESSION_PLAN.md",
            (
                "archive resolution evals must stay satisfied",
                "search usefulness audit must not regress",
                "manual external baseline comparison",
                "ranking regression corpus required",
                "result suppression must be impossible",
                "deterministic tie-break",
                "production ranking requires external baseline evidence and hosted deployment evidence",
            ),
            errors,
        )
        require_phrases(
            AUDIT_DIR / "PRIVACY_NO_TELEMETRY_AND_NO_HIDDEN_SCORE_POLICY.md",
            (
                "no raw query retention",
                "no telemetry signal",
                "no ad signal",
                "no hidden score",
                "no secret model scoring",
                "no result suppression without explanation",
                "no demographic or personalization ranking",
            ),
            errors,
        )
        require_phrases(
            AUDIT_DIR / "ACCEPTANCE_CRITERIA.md",
            (
                "evidence-weighted ranking contract valid",
                "compatibility-aware ranking contract valid",
                "result merge/deduplication contract valid",
                "identity resolution contract valid",
                "search result explanation contract valid",
                "public search safety valid",
                "public index contract valid",
                "archive evals pass",
                "deterministic tie-break policy accepted",
                "no telemetry/user-profile/ad/model signals accepted",
                "no result suppression accepted",
                "current-order fallback accepted",
                "hosted deployment evidence required for hosted mode",
                "operator approval",
            ),
            errors,
        )
        require_phrases(
            AUDIT_DIR / "DO_NOT_IMPLEMENT_YET.md",
            (
                "no runtime ranking",
                "no public search order change",
                "no public search response change",
                "no hidden scores",
                "no result suppression",
                "no ai/model calls",
                "no telemetry",
                "no public/local/master index mutation",
                "no live source calls",
                "no deployment",
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
                "no public search order",
                "no hidden scores",
                "no result suppression",
                "no telemetry",
                "no mutation",
                "ranking input and output model",
                "safe fallback",
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
            "report_id": "public_search_ranking_runtime_planning_v0",
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
