#!/usr/bin/env python3
"""Validate Result Merge and Deduplication Contract v0 governance artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.validate_deduplication_assessment import validate_all_examples as validate_all_assessments  # noqa: E402
from scripts.validate_result_merge_group import validate_all_examples as validate_all_groups  # noqa: E402


GROUP_CONTRACT_PATH = REPO_ROOT / "contracts" / "search" / "result_merge_group.v0.json"
ASSESSMENT_CONTRACT_PATH = REPO_ROOT / "contracts" / "search" / "deduplication_assessment.v0.json"
RELATION_CONTRACT_PATH = REPO_ROOT / "contracts" / "search" / "result_merge_relation.v0.json"
POLICY_PATH = REPO_ROOT / "control" / "inventory" / "search" / "result_merge_deduplication_policy.json"
AUDIT_DIR = REPO_ROOT / "control" / "audits" / "result-merge-deduplication-contract-v0"
REPORT_PATH = AUDIT_DIR / "result_merge_deduplication_report.json"
DOC_PATH = REPO_ROOT / "docs" / "reference" / "RESULT_MERGE_DEDUPLICATION_CONTRACT.md"
README_PATH = REPO_ROOT / "contracts" / "search" / "README.md"

REQUIRED_AUDIT_FILES = {
    "README.md",
    "CONTRACT_SUMMARY.md",
    "RESULT_MERGE_GROUP_SCHEMA.md",
    "DEDUPLICATION_ASSESSMENT_SCHEMA.md",
    "MERGE_RELATION_TAXONOMY.md",
    "DUPLICATE_NEAR_DUPLICATE_VARIANT_CONFLICT_MODEL.md",
    "GROUPING_CRITERIA_MODEL.md",
    "CANONICAL_DISPLAY_RECORD_POLICY.md",
    "COLLAPSED_RESULT_TRANSPARENCY_POLICY.md",
    "EXPAND_COLLAPSE_USER_FACING_MODEL.md",
    "SOURCE_EVIDENCE_PROVENANCE_PRESERVATION_MODEL.md",
    "IDENTITY_RESOLUTION_RELATIONSHIP.md",
    "OBJECT_SOURCE_COMPARISON_PAGE_RELATIONSHIP.md",
    "PUBLIC_SEARCH_RESULT_CARD_PROJECTION.md",
    "API_PROJECTION.md",
    "STATIC_DEMO_PROJECTION.md",
    "PRIVACY_AND_REDACTION_POLICY.md",
    "NO_DESTRUCTIVE_MERGE_POLICY.md",
    "NO_RANKING_PROMOTION_OR_MUTATION_POLICY.md",
    "INTEGRATION_BOUNDARIES.md",
    "EXAMPLE_RESULT_MERGE_REVIEW.md",
    "FUTURE_RUNTIME_PATH.md",
    "COMMAND_RESULTS.md",
    "REMAINING_BLOCKERS.md",
    "NEXT_STEPS.md",
    "result_merge_deduplication_report.json",
}
GROUP_REQUIRED_FIELDS = {
    "schema_version",
    "result_merge_group_id",
    "result_merge_group_kind",
    "status",
    "created_by_tool",
    "merge_group_identity",
    "group_relation",
    "grouped_results",
    "canonical_display_record",
    "collapsed_results",
    "transparency",
    "grouping_criteria",
    "identity_resolution_refs",
    "source_evidence_provenance",
    "conflicts",
    "user_facing_behavior",
    "result_card_projection",
    "api_projection",
    "privacy",
    "limitations",
    "no_destructive_merge_guarantees",
    "no_ranking_promotion_mutation_guarantees",
    "no_runtime_guarantees",
    "notes",
}
ASSESSMENT_REQUIRED_FIELDS = {
    "schema_version",
    "deduplication_assessment_id",
    "deduplication_assessment_kind",
    "status",
    "created_by_tool",
    "assessment_scope",
    "assessed_results",
    "asserted_relation",
    "relation_evidence",
    "grouping_decision",
    "display_decision",
    "conflict_review",
    "confidence",
    "review",
    "privacy",
    "limitations",
    "no_destructive_merge_guarantees",
    "no_runtime_guarantees",
    "no_mutation_guarantees",
    "notes",
}
GROUP_FALSE_FIELDS = {
    "runtime_result_merge_implemented",
    "persistent_merge_group_store_implemented",
    "public_search_runtime_grouping_enabled",
    "public_search_ranking_changed",
    "records_merged",
    "duplicates_deleted",
    "results_hidden_without_explanation",
    "destructive_merge_performed",
    "canonical_record_claimed_as_truth",
    "candidate_promotion_performed",
    "master_index_mutated",
    "public_index_mutated",
    "local_index_mutated",
    "source_cache_mutated",
    "evidence_ledger_mutated",
    "candidate_index_mutated",
    "live_source_called",
    "external_calls_performed",
    "downloads_enabled",
    "installs_enabled",
    "execution_enabled",
    "telemetry_exported",
}
ASSESSMENT_FALSE_FIELDS = {
    "runtime_deduplication_implemented",
    "deduplication_applied_to_live_search",
    "records_merged",
    "results_suppressed",
    "results_hidden_without_explanation",
    "destructive_merge_performed",
    "ranking_changed",
    "candidate_promotion_performed",
    "master_index_mutated",
    "public_index_mutated",
    "local_index_mutated",
    "source_cache_mutated",
    "evidence_ledger_mutated",
    "candidate_index_mutated",
    "live_source_called",
    "external_calls_performed",
    "telemetry_exported",
}
POLICY_FALSE_FIELDS = {
    "runtime_result_merge_implemented",
    "runtime_deduplication_implemented",
    "persistent_merge_group_store_implemented",
    "public_search_runtime_grouping_enabled",
    "public_search_ranking_changed",
    "records_merged",
    "duplicates_deleted",
    "destructive_merge_allowed",
    "conflict_hiding_allowed",
    "hidden_without_explanation_allowed",
    "canonical_display_is_truth",
    "candidate_promotion_allowed",
    "master_index_mutation_allowed",
    "public_index_mutation_allowed",
    "local_index_mutation_allowed",
    "source_cache_mutation_allowed",
    "evidence_ledger_mutation_allowed",
    "candidate_index_mutation_allowed",
}
REPORT_FALSE_FIELDS = {
    "runtime_result_merge_implemented",
    "runtime_deduplication_implemented",
    "persistent_merge_group_store_implemented",
    "public_search_runtime_grouping_enabled",
    "public_search_ranking_changed",
    "deduplication_applied_to_live_search",
    "records_merged",
    "duplicates_deleted",
    "results_suppressed",
    "results_hidden_without_explanation",
    "destructive_merge_performed",
    "destructive_merge_allowed",
    "canonical_record_claimed_as_truth",
    "candidate_promotion_allowed",
    "candidate_promotion_performed",
    "master_index_mutation_allowed",
    "public_index_mutation_allowed",
    "local_index_mutation_allowed",
    "source_cache_mutation_allowed",
    "evidence_ledger_mutation_allowed",
    "candidate_index_mutation_allowed",
    "live_source_called",
    "external_calls_performed",
    "telemetry_implemented",
}
REQUIRED_DOC_PHRASES = {
    "contract-only",
    "result merge is not identity truth",
    "result merge is not destructive record merge",
    "result merge is not ranking",
    "not candidate promotion",
    "canonical display record is not truth",
    "collapsed results must be transparent and expandable",
    "conflicts must not be hidden",
    "no result may be suppressed without user-visible explanation",
    "public search",
    "public index",
    "source cache",
    "evidence ledger",
    "candidate index",
    "future ranking contracts",
}


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def validate_schema(path: Path, required_fields: set[str], false_fields: set[str], errors: list[str]) -> None:
    if not path.exists():
        errors.append(f"missing schema: {path.relative_to(REPO_ROOT)}")
        return
    try:
        schema = load_json(path)
    except Exception as exc:
        errors.append(f"{path.relative_to(REPO_ROOT)} failed to parse: {exc}")
        return
    required = set(schema.get("required", []))
    missing = sorted(required_fields - required)
    if missing:
        errors.append(f"{path.relative_to(REPO_ROOT)} required list missing: {', '.join(missing)}")
    properties = schema.get("properties", {})
    if not isinstance(properties, Mapping):
        errors.append(f"{path.relative_to(REPO_ROOT)} properties must be an object")
        return
    for key in sorted(false_fields):
        prop = properties.get(key)
        if not isinstance(prop, Mapping):
            errors.append(f"{path.relative_to(REPO_ROOT)} missing false property {key}")
        elif prop.get("const") is not False:
            errors.append(f"{path.relative_to(REPO_ROOT)} property {key} must const false")


def validate_policy(errors: list[str]) -> None:
    if not POLICY_PATH.exists():
        errors.append(f"missing policy: {POLICY_PATH.relative_to(REPO_ROOT)}")
        return
    try:
        policy = load_json(POLICY_PATH)
    except Exception as exc:
        errors.append(f"{POLICY_PATH.relative_to(REPO_ROOT)} failed to parse: {exc}")
        return
    if policy.get("status") != "contract_only":
        errors.append("search policy status must be contract_only")
    for key in POLICY_FALSE_FIELDS:
        if policy.get(key) is not False:
            errors.append(f"search policy {key} must be false")
    for key in ("exact_duplicate_requires_strong_identifier_or_review", "weak_name_match_not_sufficient_for_exact_duplicate", "conflict_preservation_required"):
        if policy.get(key) is not True:
            errors.append(f"search policy {key} must be true")


def validate_report(errors: list[str]) -> None:
    if not REPORT_PATH.exists():
        errors.append(f"missing report: {REPORT_PATH.relative_to(REPO_ROOT)}")
        return
    try:
        report = load_json(REPORT_PATH)
    except Exception as exc:
        errors.append(f"{REPORT_PATH.relative_to(REPO_ROOT)} failed to parse: {exc}")
        return
    if report.get("report_id") != "result_merge_deduplication_contract_v0":
        errors.append("report_id must be result_merge_deduplication_contract_v0")
    guarantees = report.get("no_runtime_no_mutation_guarantees", {})
    if not isinstance(guarantees, Mapping):
        errors.append("report no_runtime_no_mutation_guarantees must be an object")
        return
    for key in REPORT_FALSE_FIELDS:
        if guarantees.get(key) is not False:
            errors.append(f"report guarantee {key} must be false")
    if not report.get("remaining_blockers"):
        errors.append("report must list remaining blockers")


def validate_audit_dir(errors: list[str]) -> None:
    if not AUDIT_DIR.exists():
        errors.append(f"missing audit dir: {AUDIT_DIR.relative_to(REPO_ROOT)}")
        return
    present = {path.name for path in AUDIT_DIR.iterdir() if path.is_file()}
    missing = sorted(REQUIRED_AUDIT_FILES - present)
    if missing:
        errors.append(f"audit dir missing files: {', '.join(missing)}")


def validate_docs(errors: list[str]) -> None:
    for path in (DOC_PATH, README_PATH):
        if not path.exists():
            errors.append(f"missing doc: {path.relative_to(REPO_ROOT)}")
    if not DOC_PATH.exists():
        return
    text = DOC_PATH.read_text(encoding="utf-8").lower()
    for phrase in REQUIRED_DOC_PHRASES:
        if phrase.lower() not in text:
            errors.append(f"doc missing phrase: {phrase}")


def validate_relation_contract(errors: list[str]) -> None:
    if not RELATION_CONTRACT_PATH.exists():
        errors.append(f"missing relation contract: {RELATION_CONTRACT_PATH.relative_to(REPO_ROOT)}")
        return
    relation = load_json(RELATION_CONTRACT_PATH)
    relation_types = relation.get("properties", {}).get("relation_type", {}).get("enum", [])
    if "exact_duplicate_result" not in relation_types or "conflicting_duplicate_claim" not in relation_types:
        errors.append("result merge relation contract must include exact_duplicate_result and conflicting_duplicate_claim")
    if relation.get("x-relation_claim_not_truth_required") is not True:
        errors.append("result merge relation contract must require relation_claim_not_truth")
    if relation.get("x-destructive_merge_allowed") is not False:
        errors.append("result merge relation contract must keep destructive merge false")
    if relation.get("x-ranking_changed_allowed") is not False:
        errors.append("result merge relation contract must keep ranking changes false")


def build_report() -> Mapping[str, Any]:
    errors: list[str] = []
    validate_schema(GROUP_CONTRACT_PATH, GROUP_REQUIRED_FIELDS, GROUP_FALSE_FIELDS, errors)
    validate_schema(ASSESSMENT_CONTRACT_PATH, ASSESSMENT_REQUIRED_FIELDS, ASSESSMENT_FALSE_FIELDS, errors)
    validate_relation_contract(errors)
    validate_policy(errors)
    validate_audit_dir(errors)
    validate_docs(errors)
    validate_report(errors)
    group_report = validate_all_groups()
    assessment_report = validate_all_assessments()
    errors.extend(group_report.get("errors", []))
    errors.extend(assessment_report.get("errors", []))
    return {
        "status": "valid" if not errors else "invalid",
        "report_id": "result_merge_deduplication_contract_v0",
        "group_example_count": group_report.get("example_count", 0),
        "assessment_example_count": assessment_report.get("example_count", 0),
        "contract_files": [
            str(GROUP_CONTRACT_PATH.relative_to(REPO_ROOT)),
            str(ASSESSMENT_CONTRACT_PATH.relative_to(REPO_ROOT)),
            str(RELATION_CONTRACT_PATH.relative_to(REPO_ROOT)),
        ],
        "audit_dir": str(AUDIT_DIR.relative_to(REPO_ROOT)),
        "errors": errors,
    }


def emit_report(report: Mapping[str, Any], *, json_output: bool, stream: TextIO) -> None:
    if json_output:
        stream.write(json.dumps(report, indent=2) + "\n")
        return
    stream.write(f"status: {report['status']}\n")
    stream.write(f"group_example_count: {report['group_example_count']}\n")
    stream.write(f"assessment_example_count: {report['assessment_example_count']}\n")
    for error in report.get("errors", []):
        stream.write(f"error: {error}\n")


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Emit JSON report.")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    report = build_report()
    emit_report(report, json_output=args.json, stream=sys.stdout)
    return 0 if report["status"] == "valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
