#!/usr/bin/env python3
"""Validate Comparison Page Contract v0 governance artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.validate_comparison_page import validate_all_examples  # noqa: E402


CONTRACT_PATH = REPO_ROOT / "contracts" / "pages" / "comparison_page.v0.json"
SECTION_CONTRACT_PATH = REPO_ROOT / "contracts" / "pages" / "comparison_page_section.v0.json"
POLICY_PATH = REPO_ROOT / "control" / "inventory" / "pages" / "comparison_page_policy.json"
AUDIT_DIR = REPO_ROOT / "control" / "audits" / "comparison-page-contract-v0"
REPORT_PATH = AUDIT_DIR / "comparison_page_contract_report.json"
DOC_PATH = REPO_ROOT / "docs" / "reference" / "COMPARISON_PAGE_CONTRACT.md"

REQUIRED_AUDIT_FILES = {
    "README.md",
    "CONTRACT_SUMMARY.md",
    "COMPARISON_PAGE_SCHEMA.md",
    "COMPARISON_SUBJECT_MODEL.md",
    "COMPARISON_TYPE_TAXONOMY.md",
    "COMPARISON_CRITERIA_MODEL.md",
    "IDENTITY_SAME_AS_DIFFERENT_FROM_MODEL.md",
    "VERSION_STATE_RELEASE_COMPARISON_MODEL.md",
    "REPRESENTATION_AND_MEMBER_COMPARISON_MODEL.md",
    "SOURCE_EVIDENCE_PROVENANCE_COMPARISON_MODEL.md",
    "COMPATIBILITY_COMPARISON_MODEL.md",
    "RIGHTS_RISK_ACTION_COMPARISON_MODEL.md",
    "CONFLICT_DUPLICATE_AND_DISAGREEMENT_MODEL.md",
    "ABSENCE_NEAR_MISS_AND_GAP_COMPARISON_MODEL.md",
    "RESULT_CARD_OBJECT_SOURCE_PROJECTION.md",
    "API_PROJECTION.md",
    "STATIC_DEMO_PROJECTION.md",
    "PRIVACY_AND_REDACTION_POLICY.md",
    "NO_WINNER_WITHOUT_EVIDENCE_POLICY.md",
    "NO_DOWNLOAD_INSTALL_EXECUTION_POLICY.md",
    "NO_RUNTIME_AND_NO_MUTATION_POLICY.md",
    "INTEGRATION_BOUNDARIES.md",
    "EXAMPLE_COMPARISON_PAGE_REVIEW.md",
    "FUTURE_RUNTIME_PATH.md",
    "COMMAND_RESULTS.md",
    "REMAINING_BLOCKERS.md",
    "NEXT_STEPS.md",
    "comparison_page_contract_report.json",
}
REQUIRED_CONTRACT_FIELDS = {
    "schema_version",
    "comparison_page_id",
    "comparison_page_kind",
    "status",
    "created_by_tool",
    "comparison_identity",
    "comparison_type",
    "subjects",
    "criteria",
    "comparison_matrix",
    "identity_comparison",
    "version_state_release_comparison",
    "representation_member_comparison",
    "source_evidence_provenance_comparison",
    "compatibility_comparison",
    "rights_risk_action_comparison",
    "conflicts_and_disagreements",
    "absence_near_miss_gap_comparison",
    "result_card_object_source_projection",
    "api_projection",
    "static_projection",
    "privacy",
    "limitations",
    "no_winner_without_evidence_guarantees",
    "no_runtime_guarantees",
    "no_mutation_guarantees",
    "notes",
}
HARD_FALSE_FIELDS = {
    "runtime_comparison_page_implemented",
    "persistent_comparison_page_store_implemented",
    "comparison_page_generated_from_live_source",
    "comparison_winner_claimed",
    "live_source_called",
    "external_calls_performed",
    "source_sync_worker_executed",
    "source_cache_mutated",
    "evidence_ledger_mutated",
    "candidate_index_mutated",
    "candidate_promotion_performed",
    "public_index_mutated",
    "local_index_mutated",
    "master_index_mutated",
    "downloads_enabled",
    "uploads_enabled",
    "installs_enabled",
    "execution_enabled",
    "arbitrary_url_fetch_enabled",
    "rights_clearance_claimed",
    "malware_safety_claimed",
    "source_trust_claimed",
    "telemetry_exported",
}
POLICY_FALSE_FIELDS = {
    "runtime_comparison_pages_implemented",
    "persistent_comparison_page_store_implemented",
    "static_demo_available",
    "public_search_comparison_links_enabled_now",
    "live_source_calls_allowed",
    "connector_runtime_allowed",
    "source_sync_worker_execution_allowed",
    "source_cache_mutation_allowed",
    "evidence_ledger_mutation_allowed",
    "candidate_index_mutation_allowed",
    "candidate_promotion_allowed",
    "public_index_mutation_allowed",
    "local_index_mutation_allowed",
    "master_index_mutation_allowed",
    "downloads_enabled",
    "uploads_enabled",
    "installs_enabled",
    "execution_enabled",
    "arbitrary_url_fetch_enabled",
    "winner_claims_allowed_without_evidence",
    "rights_clearance_claimed",
    "malware_safety_claimed",
}
REPORT_FALSE_FIELDS = {
    "runtime_comparison_pages_implemented",
    "persistent_comparison_page_store_implemented",
    "comparison_page_generated_from_live_source",
    "comparison_winner_claimed",
    "live_source_called",
    "external_calls_performed",
    "source_sync_worker_executed",
    "source_cache_mutation_allowed",
    "evidence_ledger_mutation_allowed",
    "candidate_index_mutation_allowed",
    "candidate_promotion_allowed",
    "public_index_mutation_allowed",
    "local_index_mutation_allowed",
    "master_index_mutation_allowed",
    "downloads_enabled",
    "uploads_enabled",
    "installs_enabled",
    "execution_enabled",
    "arbitrary_url_fetch_enabled",
    "winner_claims_allowed_without_evidence",
    "rights_clearance_claimed",
    "malware_safety_claimed",
    "source_trust_claimed",
    "telemetry_implemented",
}
REQUIRED_DEFS = {
    "comparison_identity",
    "comparison_type",
    "subject",
    "criterion",
    "comparison_matrix",
    "comparison_cell",
    "identity_comparison",
    "version_state_release_comparison",
    "representation_member_comparison",
    "source_evidence_provenance_comparison",
    "compatibility_comparison",
    "rights_risk_action_comparison",
    "conflicts_and_disagreements",
    "absence_near_miss_gap_comparison",
    "result_card_object_source_projection",
    "api_projection",
    "static_projection",
    "privacy",
}
REQUIRED_DOC_PHRASES = (
    "contract-only",
    "comparison page is not ranking authority",
    "comparison page is not candidate promotion",
    "no runtime comparison pages",
    "no live source",
    "no source cache mutation",
    "no evidence ledger mutation",
    "no candidate promotion",
    "no master index mutation",
    "no winner without evidence",
    "no download",
    "no install",
    "no execution",
    "no rights clearance",
    "no malware safety",
    "object pages",
    "source pages",
)


def validate_comparison_page_contract() -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    contract = _read_json_object(CONTRACT_PATH, errors, "contracts/pages/comparison_page.v0.json")
    if contract:
        _validate_contract(contract, errors)
    section = _read_json_object(SECTION_CONTRACT_PATH, errors, "contracts/pages/comparison_page_section.v0.json")
    if section:
        for key in (
            "x-runtime_comparison_page_implemented",
            "x-winner_claims_allowed_without_evidence",
            "x-live_source_calls_allowed",
            "x-source_cache_mutation_allowed",
            "x-evidence_ledger_mutation_allowed",
            "x-candidate_promotion_allowed",
            "x-master_index_mutation_allowed",
        ):
            if section.get(key) is not False:
                errors.append(f"comparison_page_section.v0.json {key} must be false.")
    policy = _read_json_object(POLICY_PATH, errors, "control/inventory/pages/comparison_page_policy.json")
    if policy:
        _validate_policy(policy, errors)
    report = _read_json_object(REPORT_PATH, errors, "control/audits/comparison-page-contract-v0/comparison_page_contract_report.json")
    if report:
        _validate_report(report, errors)
    _validate_docs(errors)
    _validate_audit_pack(errors, warnings)
    examples = validate_all_examples(strict=True)
    if examples.get("status") != "valid":
        errors.append("comparison page examples failed validation.")
        errors.extend(examples.get("errors", []))
    return {
        "status": "valid" if not errors else "invalid",
        "created_by": "comparison_page_contract_validator_v0",
        "contract_file": "contracts/pages/comparison_page.v0.json",
        "section_contract_file": "contracts/pages/comparison_page_section.v0.json",
        "policy_file": "control/inventory/pages/comparison_page_policy.json",
        "report_id": _report_id(),
        "example_count": examples.get("example_count", 0),
        "errors": errors,
        "warnings": warnings,
    }


def _validate_contract(contract: Mapping[str, Any], errors: list[str]) -> None:
    if contract.get("x-status") != "contract_only":
        errors.append("comparison_page.v0.json x-status must be contract_only.")
    for key in (
        "x-runtime_comparison_page_implemented",
        "x-persistent_comparison_page_store_implemented",
        "x-live_source_calls_allowed",
        "x-downloads_enabled",
        "x-installs_enabled",
        "x-execution_enabled",
        "x-winner_claims_allowed_without_evidence",
        "x-source_sync_worker_execution_allowed",
        "x-source_cache_mutation_allowed",
        "x-evidence_ledger_mutation_allowed",
        "x-candidate_index_mutation_allowed",
        "x-candidate_promotion_allowed",
        "x-public_index_mutation_allowed",
        "x-local_index_mutation_allowed",
        "x-master_index_mutation_allowed",
        "x-telemetry_implemented",
    ):
        if contract.get(key) is not False:
            errors.append(f"comparison_page.v0.json {key} must be false.")
    required = set(contract.get("required", []))
    missing = sorted((REQUIRED_CONTRACT_FIELDS | HARD_FALSE_FIELDS) - required)
    if missing:
        errors.append(f"comparison_page.v0.json missing required fields: {', '.join(missing)}")
    props = contract.get("properties")
    if not isinstance(props, Mapping):
        errors.append("comparison_page.v0.json properties must be an object.")
    else:
        for key in sorted(REQUIRED_CONTRACT_FIELDS | HARD_FALSE_FIELDS):
            if key not in props:
                errors.append(f"comparison_page.v0.json properties missing {key}.")
    defs = contract.get("$defs")
    if not isinstance(defs, Mapping):
        errors.append("comparison_page.v0.json $defs must be present.")
        return
    for key in sorted(REQUIRED_DEFS):
        if key not in defs:
            errors.append(f"comparison_page.v0.json $defs missing {key}.")


def _validate_policy(policy: Mapping[str, Any], errors: list[str]) -> None:
    if policy.get("status") != "contract_only":
        errors.append("comparison_page_policy.status must be contract_only.")
    for key in sorted(POLICY_FALSE_FIELDS):
        if policy.get(key) is not False:
            errors.append(f"comparison_page_policy.{key} must be false.")
    next_contracts = policy.get("next_contracts")
    for key in ("cross_source_identity_resolution_contract", "result_merge_deduplication_contract", "evidence_weighted_ranking_contract"):
        if not isinstance(next_contracts, list) or key not in next_contracts:
            errors.append(f"comparison_page_policy.next_contracts missing {key}.")


def _validate_report(report: Mapping[str, Any], errors: list[str]) -> None:
    if report.get("report_id") != "comparison_page_contract_v0":
        errors.append("comparison_page_contract_report.report_id must be comparison_page_contract_v0.")
    if report.get("next_recommended_branch") != "P82 Cross-Source Identity Resolution Contract v0":
        errors.append("comparison_page_contract_report.next_recommended_branch must point to P82.")
    for key in sorted(REPORT_FALSE_FIELDS):
        if report.get(key) is not False:
            errors.append(f"comparison_page_contract_report.{key} must be false.")


def _validate_docs(errors: list[str]) -> None:
    if not DOC_PATH.is_file():
        errors.append("docs/reference/COMPARISON_PAGE_CONTRACT.md: missing.")
        return
    text = DOC_PATH.read_text(encoding="utf-8").casefold()
    for phrase in REQUIRED_DOC_PHRASES:
        if phrase.casefold() not in text:
            errors.append(f"docs/reference/COMPARISON_PAGE_CONTRACT.md missing phrase: {phrase}")


def _validate_audit_pack(errors: list[str], warnings: list[str]) -> None:
    if not AUDIT_DIR.is_dir():
        errors.append("control/audits/comparison-page-contract-v0: missing audit directory.")
        return
    present = {path.name for path in AUDIT_DIR.iterdir() if path.is_file()}
    missing = sorted(REQUIRED_AUDIT_FILES - present)
    if missing:
        errors.append(f"comparison-page-contract-v0 audit pack missing files: {', '.join(missing)}")
    extra = sorted(present - REQUIRED_AUDIT_FILES)
    if extra:
        warnings.append(f"comparison-page-contract-v0 audit pack has extra files: {', '.join(extra)}")


def _read_json_object(path: Path, errors: list[str], label: str) -> Mapping[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"{label}: missing.")
        return {}
    except json.JSONDecodeError as exc:
        errors.append(f"{label}: invalid JSON: {exc}")
        return {}
    if not isinstance(payload, Mapping):
        errors.append(f"{label}: JSON root must be an object.")
        return {}
    return payload


def _report_id() -> str:
    if REPORT_PATH.is_file():
        try:
            report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
            return str(report.get("report_id", "comparison_page_contract_v0"))
        except json.JSONDecodeError:
            return "invalid_report"
    return "missing_report"


def _emit(report: Mapping[str, Any], *, json_mode: bool, stream: TextIO) -> None:
    if json_mode:
        json.dump(report, stream, indent=2, sort_keys=True)
        stream.write("\n")
        return
    stream.write(f"status: {report['status']}\n")
    stream.write(f"example_count: {report['example_count']}\n")
    if report.get("errors"):
        stream.write("errors:\n")
        for error in report["errors"]:
            stream.write(f"- {error}\n")
    if report.get("warnings"):
        stream.write("warnings:\n")
        for warning in report["warnings"]:
            stream.write(f"- {warning}\n")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate Comparison Page Contract v0 governance artifacts.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    return parser


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    args = build_parser().parse_args(argv)
    report = validate_comparison_page_contract()
    _emit(report, json_mode=args.json, stream=stdout)
    return 0 if report["status"] == "valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
