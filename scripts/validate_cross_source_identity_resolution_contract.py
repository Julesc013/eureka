#!/usr/bin/env python3
"""Validate Cross-Source Identity Resolution Contract v0 governance artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.validate_identity_cluster import validate_all_examples as validate_all_clusters  # noqa: E402
from scripts.validate_identity_resolution_assessment import validate_all_examples as validate_all_assessments  # noqa: E402


ASSESSMENT_CONTRACT_PATH = REPO_ROOT / "contracts" / "identity" / "identity_resolution_assessment.v0.json"
CLUSTER_CONTRACT_PATH = REPO_ROOT / "contracts" / "identity" / "identity_cluster.v0.json"
RELATION_CONTRACT_PATH = REPO_ROOT / "contracts" / "identity" / "identity_relation.v0.json"
POLICY_PATH = REPO_ROOT / "control" / "inventory" / "identity" / "cross_source_identity_resolution_policy.json"
AUDIT_DIR = REPO_ROOT / "control" / "audits" / "cross-source-identity-resolution-contract-v0"
REPORT_PATH = AUDIT_DIR / "cross_source_identity_resolution_report.json"
DOC_PATH = REPO_ROOT / "docs" / "reference" / "CROSS_SOURCE_IDENTITY_RESOLUTION_CONTRACT.md"
README_PATH = REPO_ROOT / "contracts" / "identity" / "README.md"

REQUIRED_AUDIT_FILES = {
    "README.md",
    "CONTRACT_SUMMARY.md",
    "IDENTITY_RESOLUTION_ASSESSMENT_SCHEMA.md",
    "IDENTITY_CLUSTER_SCHEMA.md",
    "IDENTITY_RELATION_TAXONOMY.md",
    "IDENTIFIER_MODEL.md",
    "ALIAS_AND_NAME_NORMALIZATION_MODEL.md",
    "VERSION_PLATFORM_ARCHITECTURE_MATCHING_MODEL.md",
    "SOURCE_AND_PROVENANCE_EVIDENCE_MODEL.md",
    "HASH_CHECKSUM_INTRINSIC_ID_MODEL.md",
    "PACKAGE_REPOSITORY_ARCHIVE_CAPTURE_IDENTITY_MODEL.md",
    "REPRESENTATION_AND_MEMBER_IDENTITY_MODEL.md",
    "CONFLICT_AND_DUPLICATE_PRESERVATION_MODEL.md",
    "CONFIDENCE_AND_REVIEW_MODEL.md",
    "PROMOTION_AND_MERGE_BOUNDARY_MODEL.md",
    "PUBLIC_SEARCH_OBJECT_SOURCE_COMPARISON_PROJECTION.md",
    "PRIVACY_AND_REDACTION_POLICY.md",
    "NO_DESTRUCTIVE_MERGE_POLICY.md",
    "NO_RUNTIME_AND_NO_MUTATION_POLICY.md",
    "INTEGRATION_BOUNDARIES.md",
    "EXAMPLE_IDENTITY_RESOLUTION_REVIEW.md",
    "FUTURE_RUNTIME_PATH.md",
    "COMMAND_RESULTS.md",
    "REMAINING_BLOCKERS.md",
    "NEXT_STEPS.md",
    "cross_source_identity_resolution_report.json",
}
ASSESSMENT_REQUIRED_FIELDS = {
    "schema_version",
    "assessment_id",
    "assessment_kind",
    "status",
    "created_by_tool",
    "assessment_scope",
    "subjects",
    "asserted_relation",
    "relation_evidence",
    "identifier_evidence",
    "alias_name_evidence",
    "version_platform_architecture_evidence",
    "source_provenance_evidence",
    "hash_checksum_intrinsic_id_model",
    "package_repository_archive_capture_identity",
    "representation_member_evidence",
    "conflicts",
    "confidence",
    "review",
    "promotion_and_merge_boundary",
    "public_projection",
    "privacy",
    "limitations",
    "no_runtime_guarantees",
    "no_mutation_guarantees",
    "notes",
}
CLUSTER_REQUIRED_FIELDS = {
    "schema_version",
    "identity_cluster_id",
    "identity_cluster_kind",
    "status",
    "created_by_tool",
    "cluster_identity",
    "cluster_members",
    "cluster_relations",
    "canonicalization_policy",
    "conflicts",
    "confidence",
    "review",
    "privacy",
    "limitations",
    "no_runtime_guarantees",
    "no_mutation_guarantees",
    "notes",
}
ASSESSMENT_FALSE_FIELDS = {
    "runtime_identity_resolution_implemented",
    "persistent_identity_store_implemented",
    "identity_cluster_created",
    "records_merged",
    "destructive_merge_performed",
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
CLUSTER_FALSE_FIELDS = {
    "runtime_identity_cluster_implemented",
    "persistent_cluster_store_implemented",
    "cluster_accepted_as_truth",
    "records_merged",
    "destructive_merge_performed",
    "master_index_mutated",
    "public_index_mutated",
    "local_index_mutated",
    "source_cache_mutated",
    "evidence_ledger_mutated",
    "candidate_index_mutated",
    "telemetry_exported",
}
POLICY_FALSE_FIELDS = {
    "runtime_identity_resolution_implemented",
    "persistent_identity_store_implemented",
    "identity_cluster_runtime_implemented",
    "merge_runtime_implemented",
    "destructive_merge_allowed",
    "candidate_promotion_allowed",
    "master_index_mutation_allowed",
    "public_index_mutation_allowed",
    "local_index_mutation_allowed",
    "source_cache_mutation_allowed",
    "evidence_ledger_mutation_allowed",
    "candidate_index_mutation_allowed",
    "public_search_identity_resolution_enabled_now",
}
REPORT_FALSE_FIELDS = {
    "runtime_identity_resolution_implemented",
    "persistent_identity_store_implemented",
    "identity_cluster_runtime_implemented",
    "merge_runtime_implemented",
    "identity_cluster_created",
    "records_merged",
    "destructive_merge_performed",
    "destructive_merge_allowed",
    "candidate_promotion_allowed",
    "candidate_promotion_performed",
    "master_index_mutation_allowed",
    "public_index_mutation_allowed",
    "local_index_mutation_allowed",
    "source_cache_mutation_allowed",
    "evidence_ledger_mutation_allowed",
    "candidate_index_mutation_allowed",
    "public_search_identity_resolution_enabled_now",
    "live_source_called",
    "external_calls_performed",
    "telemetry_implemented",
}
REQUIRED_DOC_PHRASES = {
    "contract-only",
    "identity resolution is not runtime",
    "identity resolution is not destructive deduplication",
    "not candidate promotion",
    "no destructive merge",
    "no records merged",
    "no master index mutation",
    "source cache mutation",
    "evidence ledger mutation",
    "confidence_not_truth",
    "name_match_not_sufficient_alone",
    "object pages",
    "source pages",
    "comparison pages",
    "public search",
    "public index",
    "candidate promotion policy",
    "no source trust",
    "not rights clearance",
    "not malware safety",
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
    if schema.get("type") != "object":
        errors.append(f"{path.relative_to(REPO_ROOT)} must define an object schema")
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
        errors.append("identity policy status must be contract_only")
    for key in POLICY_FALSE_FIELDS:
        if policy.get(key) is not False:
            errors.append(f"identity policy {key} must be false")
    for key in (
        "confidence_not_truth_required",
        "exact_identity_requires_strong_identifier_or_review",
        "name_match_not_sufficient_alone",
        "conflict_preservation_required",
    ):
        if policy.get(key) is not True:
            errors.append(f"identity policy {key} must be true")


def validate_report(errors: list[str]) -> None:
    if not REPORT_PATH.exists():
        errors.append(f"missing report: {REPORT_PATH.relative_to(REPO_ROOT)}")
        return
    try:
        report = load_json(REPORT_PATH)
    except Exception as exc:
        errors.append(f"{REPORT_PATH.relative_to(REPO_ROOT)} failed to parse: {exc}")
        return
    if report.get("report_id") != "cross_source_identity_resolution_contract_v0":
        errors.append("report_id must be cross_source_identity_resolution_contract_v0")
    guarantees = report.get("no_runtime_no_mutation_guarantees", {})
    if not isinstance(guarantees, Mapping):
        errors.append("report no_runtime_no_mutation_guarantees must be an object")
        return
    for key in REPORT_FALSE_FIELDS:
        if guarantees.get(key) is not False:
            errors.append(f"report guarantee {key} must be false")
    blockers = report.get("remaining_blockers", [])
    if not blockers:
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
    try:
        relation = load_json(RELATION_CONTRACT_PATH)
    except Exception as exc:
        errors.append(f"{RELATION_CONTRACT_PATH.relative_to(REPO_ROOT)} failed to parse: {exc}")
        return
    relation_types = relation.get("properties", {}).get("relation_type", {}).get("enum", [])
    if "exact_same_object" not in relation_types or "conflicting_identity" not in relation_types:
        errors.append("identity relation contract must include exact_same_object and conflicting_identity")
    if relation.get("x-relation_claim_not_truth_required") is not True:
        errors.append("identity relation contract must require relation_claim_not_truth")
    if relation.get("x-global_merge_allowed") is not False:
        errors.append("identity relation contract must keep global_merge_allowed false")


def build_report() -> Mapping[str, Any]:
    errors: list[str] = []
    validate_schema(ASSESSMENT_CONTRACT_PATH, ASSESSMENT_REQUIRED_FIELDS, ASSESSMENT_FALSE_FIELDS, errors)
    validate_schema(CLUSTER_CONTRACT_PATH, CLUSTER_REQUIRED_FIELDS, CLUSTER_FALSE_FIELDS, errors)
    validate_relation_contract(errors)
    validate_policy(errors)
    validate_audit_dir(errors)
    validate_docs(errors)
    validate_report(errors)

    assessment_report = validate_all_assessments()
    cluster_report = validate_all_clusters()
    errors.extend(assessment_report.get("errors", []))
    errors.extend(cluster_report.get("errors", []))

    return {
        "status": "valid" if not errors else "invalid",
        "report_id": "cross_source_identity_resolution_contract_v0",
        "assessment_example_count": assessment_report.get("example_count", 0),
        "cluster_example_count": cluster_report.get("example_count", 0),
        "contract_files": [
            str(ASSESSMENT_CONTRACT_PATH.relative_to(REPO_ROOT)),
            str(CLUSTER_CONTRACT_PATH.relative_to(REPO_ROOT)),
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
    stream.write(f"assessment_example_count: {report['assessment_example_count']}\n")
    stream.write(f"cluster_example_count: {report['cluster_example_count']}\n")
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
