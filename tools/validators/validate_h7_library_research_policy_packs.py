#!/usr/bin/env python3
"""Validate H7-BUNDLE-01 library/cultural/research policy packs offline."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]
SOURCE_FAMILY = "library_cultural_research"
SOURCE_IDS = [
    "worldcat_library_catalog",
    "oaister_oai_pmh",
    "google_books",
    "hathitrust",
    "open_library",
    "trove_library_cultural",
    "europeana",
    "dpla",
    "gallica_bnf",
    "library_of_congress",
    "nara_catalog",
    "national_archives_australia",
    "uk_national_archives_discovery",
    "govinfo",
    "openalex",
    "crossref",
    "datacite",
    "arxiv",
    "pubmed",
    "pubmed_central",
    "doaj",
    "zenodo",
    "repec",
    "ssrn",
    "semantic_scholar",
    "kaggle_datasets",
    "deep_blue_repository",
    "google_patents",
    "wipo_patentscope",
    "uspto_patents",
]
EXPECTED_SOURCES = {
    source_id: {
        "source_record": f"examples/sources/source_records/{source_id}_source_v2.json",
        "policy_pack": f"examples/connectors/h7_library_research/policies/{source_id}_policy_pack_v0.json",
    }
    for source_id in SOURCE_IDS
}
INVENTORY_FILES = (
    "control/inventory/source_packs/h7_library_research_source_pack_policy.json",
    "control/inventory/source_packs/h7_library_research_sources.json",
    "control/inventory/source_packs/h7_library_research_connector_families.json",
    "control/inventory/source_packs/h7_bibliographic_identity_policy.json",
    "control/inventory/source_packs/h7_research_work_identity_policy.json",
    "control/inventory/source_packs/h7_dataset_repository_identity_policy.json",
    "control/inventory/source_packs/h7_cultural_object_identity_policy.json",
    "control/inventory/source_packs/h7_patent_identity_policy.json",
    "control/inventory/source_packs/h7_citation_relation_policy.json",
    "control/inventory/source_packs/h7_access_rights_availability_policy.json",
    "control/inventory/source_packs/h7_library_research_approval_gates.json",
    "control/inventory/source_packs/h7_library_research_output_policy.json",
    "control/inventory/source_packs/h7_library_research_truth_policy.json",
    "control/inventory/source_packs/h7_library_research_no_live_call_policy.json",
    "control/inventory/source_packs/h7_library_research_no_harvest_download_policy.json",
)
SOURCE_PACK_EXAMPLES = (
    "examples/packs/source/h7_library_research_source_pack_manifest_v0.json",
    "examples/packs/source/h7_library_research_policy_pack_v0.json",
)
EXTRA_EXAMPLES = (
    "examples/sources/source_records/library_research_policy_blocked_source_v2.json",
    "examples/connectors/h7_library_research/policies/library_research_policy_blocked_pack_v0.json",
    "examples/connectors/h7_library_research/coverage/h7_library_research_coverage_preview_v0.json",
    "examples/connectors/h7_library_research/scorecards/h7_library_research_scorecard_preview_v0.json",
)
DOCS = (
    "docs/reference/H7_LIBRARY_RESEARCH_SOURCE_PACKS.md",
    "docs/reference/H7_BIBLIOGRAPHIC_IDENTITY_POLICY.md",
    "docs/reference/H7_RESEARCH_WORK_IDENTITY_POLICY.md",
    "docs/reference/H7_DATASET_REPOSITORY_IDENTITY_POLICY.md",
    "docs/reference/H7_CULTURAL_OBJECT_IDENTITY_POLICY.md",
    "docs/reference/H7_PATENT_IDENTITY_POLICY.md",
    "docs/reference/H7_CITATION_RELATION_POLICY.md",
    "docs/reference/H7_ACCESS_RIGHTS_AVAILABILITY_POLICY.md",
    "docs/architecture/H7_LIBRARY_RESEARCH_MODEL.md",
    "docs/architecture/LIBRARY_RESEARCH_SOURCE_FAMILY_MODEL.md",
    "docs/operations/H7_LIBRARY_RESEARCH_POLICY_GATES.md",
    "docs/operations/H7_LIBRARY_RESEARCH_NO_LIVE_CALL_POLICY.md",
    "docs/operations/H7_LIBRARY_RESEARCH_NO_HARVEST_DOWNLOAD_POLICY.md",
    "docs/operations/H7_LIBRARY_RESEARCH_FIXTURE_PLAN.md",
)
AUDIT_FILES = tuple(
    f"control/audits/h7-bundle-01-library-research-policy-packs-v0/{name}"
    for name in (
        "README.md",
        "h7_bundle_01_report.json",
        "h7_source_pack_summary.md",
        "h7_source_policy_gate_summary.md",
        "h7_connector_family_summary.md",
        "h7_bibliographic_identity_policy_summary.md",
        "h7_research_work_identity_policy_summary.md",
        "h7_dataset_repository_identity_policy_summary.md",
        "h7_cultural_object_identity_policy_summary.md",
        "h7_patent_identity_policy_summary.md",
        "h7_citation_relation_policy_summary.md",
        "h7_access_rights_availability_policy_summary.md",
        "h7_fixture_plan.md",
        "h7_no_live_call_report.md",
        "h7_no_harvest_download_report.md",
        "h7_readiness_for_fixture_runtime.md",
        "validation.md",
        "generated/sample_h7_source_summary.json",
        "generated/sample_h7_source_summary.md",
        "generated/sample_h7_option_matrix.json",
    )
)
H7_PYTHON_FILES = (
    "scripts/validate_h7_library_research_policy_packs.py",
    "scripts/summarize_h7_library_research_sources.py",
)
ALLOWED_CURRENT_OPERATIONS = {
    "inspect_fixture",
    "normalize_fixture_future",
    "record_source_policy",
    "record_source_metadata_preview",
    "record_identity_policy",
    "record_access_rights_availability_policy",
    "create_coverage_preview",
    "create_scorecard_preview",
}
FALSE_REQUIRED_KEYS = {
    "live_access_enabled",
    "source_sync_enabled",
    "connector_runtime_enabled",
    "approved_live_probe_enabled",
    "oai_pmh_harvest_enabled",
    "api_query_enabled",
    "full_text_fetch_enabled",
    "pdf_download_enabled",
    "book_scan_download_enabled",
    "article_download_enabled",
    "dataset_download_enabled",
    "iiif_manifest_fetch_enabled",
    "media_download_enabled",
    "patent_document_download_enabled",
    "scraping_enabled",
    "crawling_enabled",
    "bypass_or_automation_enabled",
    "restricted_rights_sensitive_source_enabled",
}
FORBIDDEN_TRUE_KEYS = FALSE_REQUIRED_KEYS | {
    "source_pack_is_truth",
    "source_pack_is_accepted_evidence",
    "source_pack_is_imported_state",
    "policy_pack_grants_live_access",
    "capability_grants_permission",
    "coverage_preview_is_exhaustive",
    "coverage_manifest_is_exhaustive_global_coverage",
    "scorecard_preview_is_production_ready",
    "scorecard_claims_production_readiness",
    "scorecard_auto_approves_future_connectors",
    "production_ready",
    "auto_approves_future_connectors",
    "bibliographic_metadata_is_identity_truth",
    "research_work_metadata_is_work_truth",
    "dataset_metadata_is_dataset_truth",
    "cultural_object_metadata_is_object_truth",
    "patent_metadata_is_patent_truth",
    "citation_relation_is_citation_truth",
    "access_metadata_is_rights_truth",
    "open_access_metadata_is_rights_clearance",
    "landing_page_grants_download_permission",
    "catalog_presence_proves_current_availability",
    "rights_clearance_claimed",
    "open_access_truth_claimed",
    "privacy_safety_claimed",
    "malware_safety_claimed",
    "verified_availability_claimed",
    "bibliographic_completeness_claimed",
    "citation_correctness_verified",
    "article_truth_accepted",
    "dataset_validity_verified",
    "patent_validity_verified",
    "accepted_source_truth",
    "accepted_evidence_truth",
    "accepted_candidate_truth",
    "accepted_bibliographic_truth",
    "accepted_research_work_truth",
    "accepted_dataset_truth",
    "accepted_cultural_object_truth",
    "accepted_patent_truth",
    "accepted_citation_truth",
    "accepted_access_rights_truth",
    "accepted_public_record",
    "public_index_mutation_allowed",
    "master_index_mutation_allowed",
    "public_index_mutated",
    "master_index_mutated",
    "mutated_public_index",
    "mutated_master_index",
}
BANNED_IMPORT_RE = re.compile(
    r"^\s*(?:from|import)\s+"
    r"(requests|urllib|httpx|aiohttp|socket|ftplib|smtplib|webbrowser|selenium|playwright|openai|anthropic)\b",
    re.MULTILINE,
)
SECRET_KEY_RE = re.compile(
    r'"[^"]*(api[_-]?key|api[_-]?token|access[_-]?token|auth[_-]?token|client_secret|password|private_key|cookie)[^"]*"\s*:',
    re.IGNORECASE,
)
PAYLOAD_RE = re.compile(
    r'"[^"]*(full_text_payload|pdf_payload|book_scan_payload|article_payload|dataset_payload|patent_document_payload|iiif_payload|media_payload|ocr_payload|restricted_payload|scraping_output|crawling_output|browser_automation_output)[^"]*"\s*:',
    re.IGNORECASE,
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Print JSON validation result.")
    args = parser.parse_args(argv)
    result = validate_repo(REPO_ROOT)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    else:
        print("H7 library/cultural/research policy pack validation", file=stdout)
        print(f"status: {result['status']}", file=stdout)
        print(f"errors: {len(result['errors'])}", file=stdout)
        for error in result["errors"]:
            print(f"- {error}", file=stdout)
    return 0 if result["status"] == "valid" else 1


def validate_repo(root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    payloads: dict[str, dict[str, Any]] = {}
    required_paths = list(INVENTORY_FILES + SOURCE_PACK_EXAMPLES + EXTRA_EXAMPLES + DOCS + AUDIT_FILES + H7_PYTHON_FILES)
    for source_paths in EXPECTED_SOURCES.values():
        required_paths.extend(source_paths.values())
    for rel in required_paths:
        path = root / rel
        if not path.exists():
            errors.append(f"missing required path: {rel}")
            continue
        if path.suffix == ".json":
            try:
                payload = _load_json(path)
            except (OSError, json.JSONDecodeError, ValueError) as exc:
                errors.append(f"{rel}: invalid JSON: {exc}")
                continue
            payloads[rel] = payload
            _scan_json_payload(rel, payload, errors)
    known = _load_known_values(root, errors)
    inventory = payloads.get("control/inventory/source_packs/h7_library_research_sources.json", {})
    sources = inventory.get("sources", [])
    if not isinstance(sources, list):
        errors.append("h7 source inventory must contain sources list")
        sources = []
    source_ids = [item.get("source_id") for item in sources if isinstance(item, Mapping)]
    if len(sources) != 30:
        errors.append(f"h7 source inventory expected 30 sources, got {len(sources)}")
    if sorted(source_ids) != sorted(EXPECTED_SOURCES):
        errors.append("h7 source inventory source IDs do not match expected set")
    if len(source_ids) != len(set(source_ids)):
        errors.append("h7 source inventory source IDs must be unique")
    for source_id, paths in EXPECTED_SOURCES.items():
        errors.extend(validate_source_record(source_id, payloads.get(paths["source_record"], {}), known))
        errors.extend(validate_policy_pack(source_id, payloads.get(paths["policy_pack"], {})))
    blocked_record = payloads.get("examples/sources/source_records/library_research_policy_blocked_source_v2.json", {})
    if blocked_record:
        errors.extend(validate_source_record("library_research_policy_blocked", blocked_record, known, allow_blocked=True))
    blocked_pack = payloads.get("examples/connectors/h7_library_research/policies/library_research_policy_blocked_pack_v0.json", {})
    if blocked_pack:
        errors.extend(validate_policy_pack("library_research_policy_blocked", blocked_pack, allow_blocked=True))
    errors.extend(validate_coverage_preview(payloads.get("examples/connectors/h7_library_research/coverage/h7_library_research_coverage_preview_v0.json", {})))
    errors.extend(validate_scorecard_preview(payloads.get("examples/connectors/h7_library_research/scorecards/h7_library_research_scorecard_preview_v0.json", {})))
    errors.extend(validate_policies(payloads))
    errors.extend(validate_registry_entries(root))
    errors.extend(scan_python_files(root))
    errors.extend(scan_for_private_roots(root))
    return {
        "schema_version": "h7_library_research_policy_pack_validation.v0",
        "status": "valid" if not errors else "invalid",
        "source_count": len(EXPECTED_SOURCES),
        "errors": errors,
    }


def validate_source_record(source_id: str, record: Mapping[str, Any], known: Mapping[str, set[str]], allow_blocked: bool = False) -> list[str]:
    errors: list[str] = []
    prefix = f"source_record {source_id}"
    if record.get("schema_version") != "source_record.v2":
        errors.append(f"{prefix}: schema_version must be source_record.v2")
    if record.get("source_id") != source_id:
        errors.append(f"{prefix}: source_id mismatch")
    if record.get("source_family") != SOURCE_FAMILY:
        errors.append(f"{prefix}: source_family must be {SOURCE_FAMILY}")
    if SOURCE_FAMILY not in known.get("source_families", set()):
        errors.append(f"{prefix}: source family {SOURCE_FAMILY} is not registered")
    if record.get("connector_family") not in known.get("connector_families", set()):
        errors.append(f"{prefix}: connector_family is not registered")
    if record.get("trust_lane") not in known.get("trust_lanes", set()):
        errors.append(f"{prefix}: unknown trust_lane {record.get('trust_lane')}")
    if record.get("current_access_mode") not in known.get("access_modes", set()):
        errors.append(f"{prefix}: unknown current_access_mode {record.get('current_access_mode')}")
    if record.get("current_index_depth") not in known.get("index_depths", set()):
        errors.append(f"{prefix}: unknown current_index_depth {record.get('current_index_depth')}")
    if record.get("target_index_depth_future") not in known.get("index_depths", set()):
        errors.append(f"{prefix}: unknown target_index_depth_future {record.get('target_index_depth_future')}")
    if record.get("current_status") not in {"policy_pack_only", "policy_blocked"}:
        errors.append(f"{prefix}: current_status must be policy_pack_only or policy_blocked")
    if allow_blocked and record.get("current_status") != "policy_blocked":
        errors.append(f"{prefix}: blocked record must be policy_blocked")
    for key in (
        "bibliographic_identity_support",
        "research_work_identity_support",
        "dataset_identity_support",
        "cultural_object_identity_support",
        "patent_identity_support",
        "citation_relation_support",
        "access_rights_availability_support",
    ):
        if not isinstance(record.get(key), Mapping):
            errors.append(f"{prefix}: missing {key}")
    for key in ("fixture_required", "live_probe_required_future", "scorecard_required", "coverage_required"):
        if record.get(key) is not True:
            errors.append(f"{prefix}: {key} must be true")
    for key in FALSE_REQUIRED_KEYS:
        if record.get(key) is not False:
            errors.append(f"{prefix}: {key} must be false")
    errors.extend(_detect_forbidden_true_values(record, prefix))
    return errors


def validate_policy_pack(source_id: str, pack: Mapping[str, Any], allow_blocked: bool = False) -> list[str]:
    errors: list[str] = []
    prefix = f"policy_pack {source_id}"
    if pack.get("schema_version") != "h7_library_research_policy_pack.v0":
        errors.append(f"{prefix}: schema_version mismatch")
    if pack.get("source_id") != source_id:
        errors.append(f"{prefix}: source_id mismatch")
    if pack.get("source_family") != SOURCE_FAMILY:
        errors.append(f"{prefix}: source_family must be {SOURCE_FAMILY}")
    if pack.get("current_status") not in {"policy_pack_only", "policy_blocked"}:
        errors.append(f"{prefix}: current_status must be policy_pack_only or policy_blocked")
    if allow_blocked and pack.get("current_status") != "policy_blocked":
        errors.append(f"{prefix}: blocked pack must be policy_blocked")
    allowed_ops = pack.get("allowed_current_operations")
    if not isinstance(allowed_ops, list):
        errors.append(f"{prefix}: allowed_current_operations must be a list")
    elif not set(allowed_ops).issubset(ALLOWED_CURRENT_OPERATIONS):
        errors.append(f"{prefix}: allowed_current_operations contains unapproved operation")
    for key in (
        "endpoint_or_metadata_classes_planned",
        "endpoint_or_metadata_classes_forbidden_current",
        "fixture_requirements",
        "live_probe_requirements_future",
        "bibliographic_identity_mapping_future",
        "research_work_identity_mapping_future",
        "dataset_identity_mapping_future",
        "cultural_object_identity_mapping_future",
        "patent_identity_mapping_future",
        "citation_relation_mapping_future",
        "access_rights_availability_mapping_future",
        "source_cache_mapping_future",
        "evidence_mapping_future",
        "review_requirements",
        "scorecard_requirements",
        "coverage_requirements",
        "no_goals",
    ):
        if key not in pack:
            errors.append(f"{prefix}: missing {key}")
    errors.extend(_detect_forbidden_true_values(pack, prefix))
    return errors


def validate_coverage_preview(coverage: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    prefix = "coverage h7_library_research"
    if coverage.get("schema_version") != "h7_library_research_coverage_preview.v0":
        errors.append(f"{prefix}: schema_version mismatch")
    if coverage.get("source_count") != 30:
        errors.append(f"{prefix}: source_count must be 30")
    if coverage.get("coverage_basis") not in {"policy_pack_only", "example_only"}:
        errors.append(f"{prefix}: coverage_basis must be policy_pack_only or example_only")
    if coverage.get("coverage_depth_current") not in {"D0_source_known", "D1_catalog_indexed"}:
        errors.append(f"{prefix}: coverage_depth_current must be D0 or D1 preview")
    for key in ("records_seen", "api_queries_performed", "oai_pmh_harvests_performed", "downloads_performed", "full_text_fetches_performed", "scraping_crawling_performed"):
        if coverage.get(key) != 0:
            errors.append(f"{prefix}: {key} must be 0")
    errors.extend(_detect_forbidden_true_values(coverage, prefix))
    return errors


def validate_scorecard_preview(scorecard: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    prefix = "scorecard h7_library_research"
    if scorecard.get("schema_version") != "h7_library_research_scorecard_preview.v0":
        errors.append(f"{prefix}: schema_version mismatch")
    if scorecard.get("source_count") != 30:
        errors.append(f"{prefix}: source_count must be 30")
    expected_statuses = {
        "fixture_replay_status": "not_started",
        "policy_evaluation_status": "planned",
        "live_probe_envelope_status": "not_approved",
        "source_cache_mapping_status": "planned",
        "evidence_mapping_status": "planned",
        "bibliographic_identity_mapping_status": "planned",
        "research_work_identity_mapping_status": "planned",
        "dataset_identity_mapping_status": "planned",
        "cultural_object_identity_mapping_status": "planned",
        "patent_identity_mapping_status": "planned",
        "citation_relation_mapping_status": "planned",
        "access_rights_availability_mapping_status": "planned",
        "quality_delta_status": "not_started",
        "harvesting_status": "forbidden_current",
        "download_status": "forbidden_current",
        "scraping_crawling_status": "forbidden_current",
    }
    for key, expected in expected_statuses.items():
        if scorecard.get(key) != expected:
            errors.append(f"{prefix}: {key} must be {expected}")
    errors.extend(_detect_forbidden_true_values(scorecard, prefix))
    return errors


def validate_policies(payloads: Mapping[str, Mapping[str, Any]]) -> list[str]:
    errors: list[str] = []
    source_policy = payloads.get("control/inventory/source_packs/h7_library_research_source_pack_policy.json", {})
    for key in FALSE_REQUIRED_KEYS | {"source_pack_import_enabled"}:
        if source_policy.get(key) is not False:
            errors.append(f"source policy: {key} must be false")
    for key in ("source_pack_export_only", "review_required_before_live_access", "review_required_before_source_cache_write", "review_required_before_evidence_acceptance", "review_required_before_public_index_use", "review_required_before_master_index"):
        if source_policy.get(key) is not True:
            errors.append(f"source policy: {key} must be true")
    checks = [
        ("control/inventory/source_packs/h7_bibliographic_identity_policy.json", "identity_boundary", (
            "bibliographic_identity_candidate_is_not_accepted_bibliographic_truth",
            "isbn_issn_oclc_lccn_candidates_require_review",
            "catalog_presence_does_not_prove_current_availability",
            "holdings_metadata_does_not_prove_access_rights",
            "edition_work_manifestation_clustering_requires_review",
            "rights_license_access_metadata_is_not_rights_clearance",
        )),
        ("control/inventory/source_packs/h7_research_work_identity_policy.json", "work_boundary", (
            "research_work_candidate_is_not_accepted_work_truth",
            "doi_pmid_pmcid_arxiv_openalex_crossref_datacite_ids_require_review",
            "citation_counts_are_source_observations_not_truth",
            "abstract_metadata_is_not_full_text_truth",
            "open_access_status_is_not_rights_clearance",
            "preprint_reviewed_publication_state_requires_review",
        )),
        ("control/inventory/source_packs/h7_dataset_repository_identity_policy.json", "dataset_boundary", (
            "dataset_identity_candidate_is_not_accepted_dataset_truth",
            "dataset_metadata_does_not_prove_data_validity",
            "file_metadata_does_not_grant_download_permission",
            "license_metadata_is_not_rights_clearance",
            "checksum_size_metadata_is_not_malware_safety",
            "related_publication_links_require_review",
        )),
        ("control/inventory/source_packs/h7_cultural_object_identity_policy.json", "object_boundary", (
            "cultural_object_candidate_is_not_accepted_object_truth",
            "institution_metadata_does_not_prove_completeness",
            "rights_metadata_is_not_rights_clearance",
            "iiif_image_media_refs_do_not_grant_fetch_download_permission",
            "cultural_object_relationships_require_review",
        )),
        ("control/inventory/source_packs/h7_patent_identity_policy.json", "patent_boundary", (
            "patent_identity_candidate_is_not_accepted_patent_truth",
            "patent_metadata_does_not_prove_legal_status",
            "grant_expiry_enforceability_requires_legal_review",
            "citation_family_relationships_require_review",
            "patent_document_locator_does_not_grant_download_permission",
        )),
        ("control/inventory/source_packs/h7_citation_relation_policy.json", "relation_boundary", (
            "citation_relation_candidate_is_not_accepted_citation_truth",
            "citation_counts_do_not_prove_impact",
            "related_work_links_can_be_duplicated_stale_or_wrong",
            "same_work_duplicate_clustering_requires_review",
        )),
        ("control/inventory/source_packs/h7_access_rights_availability_policy.json", "access_boundary", (
            "access_metadata_is_not_rights_clearance",
            "open_access_metadata_can_be_stale_or_wrong",
            "landing_page_exists_does_not_grant_download_permission",
            "repository_copy_does_not_prove_lawful_redistribution",
            "restricted_paywalled_sources_are_policy_blocked_by_default",
            "download_permission_current_remains_false_in_h7_bundle_01",
        )),
    ]
    for rel, section, keys in checks:
        errors.extend(_require_true(payloads.get(rel, {}).get(section, {}), keys, rel))
    approvals = payloads.get("control/inventory/source_packs/h7_library_research_approval_gates.json", {})
    for item in approvals.get("source_gates", []):
        if isinstance(item, Mapping) and item.get("approval_state_current") != "not_approved_for_live_access":
            errors.append(f"approval gates {item.get('source_id')}: current approval must be not_approved_for_live_access")
    return errors


def validate_registry_entries(root: Path) -> list[str]:
    errors: list[str] = []
    source_registry = _load_json(root / "control/inventory/sources/source_family_registry.json")
    if SOURCE_FAMILY not in {item.get("family_id") for item in source_registry.get("families", []) if isinstance(item, Mapping)}:
        errors.append(f"source family registry missing {SOURCE_FAMILY}")
    connector_registry = _load_json(root / "control/inventory/connectors/connector_family_registry.json")
    registered = {item.get("family_id") for item in connector_registry.get("families", []) if isinstance(item, Mapping)}
    for family in ("library_catalog", "oai_pmh", "api_json", "iiif_future", "research_graph", "research_repository", "dataset_repository", "patent_metadata", "cultural_repository", "restricted_manifest_only"):
        if family not in registered:
            errors.append(f"connector family registry missing {family}")
    return errors


def scan_python_files(root: Path) -> list[str]:
    errors: list[str] = []
    for rel in H7_PYTHON_FILES:
        text = (root / rel).read_text(encoding="utf-8")
        if BANNED_IMPORT_RE.search(text):
            errors.append(f"{rel}: imports network/provider/browser library")
    return errors


def scan_for_private_roots(root: Path) -> list[str]:
    errors: list[str] = []
    for rel in (".aide.local", ".local/eureka", ".cache/eureka", "harvest_cache", "pdf_downloads", "book_downloads", "article_downloads", "dataset_downloads", "ocr_cache", "media_downloads"):
        if (root / rel).exists():
            errors.append(f"forbidden private/fetch root exists: {rel}")
    return errors


def _load_known_values(root: Path, errors: list[str]) -> dict[str, set[str]]:
    try:
        source_families = _load_json(root / "control/inventory/sources/source_family_registry.json")
        connector_families = _load_json(root / "control/inventory/connectors/connector_family_registry.json")
        trust_lanes = _load_json(root / "control/inventory/sources/source_trust_lane_policy.json")
        index_depths = _load_json(root / "control/inventory/sources/source_index_depth_registry.json")
        access_modes = _load_json(root / "control/inventory/sources/source_access_mode_policy.json")
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        errors.append(f"unable to load registry values: {exc}")
        return {"source_families": set(), "connector_families": set(), "trust_lanes": set(), "index_depths": set(), "access_modes": set()}
    return {
        "source_families": {str(item.get("family_id")) for item in source_families.get("families", []) if isinstance(item, Mapping)},
        "connector_families": {str(item.get("family_id")) for item in connector_families.get("families", []) if isinstance(item, Mapping)},
        "trust_lanes": {str(item.get("trust_lane")) for item in trust_lanes.get("trust_lanes", []) if isinstance(item, Mapping)},
        "index_depths": {str(item.get("depth_id")) for item in index_depths.get("depths", []) if isinstance(item, Mapping)},
        "access_modes": set(str(item) for item in access_modes.get("access_modes", [])),
    }


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def _require_true(section: Any, keys: Sequence[str], label: str) -> list[str]:
    errors: list[str] = []
    if not isinstance(section, Mapping):
        return [f"{label}: expected policy boundary object"]
    for key in keys:
        if section.get(key) is not True:
            errors.append(f"{label}: {key} must be true")
    return errors


def _detect_forbidden_true_values(value: Any, prefix: str, path: str = "") -> list[str]:
    errors: list[str] = []
    if isinstance(value, Mapping):
        for key, item in value.items():
            current = f"{path}.{key}" if path else str(key)
            if key in FORBIDDEN_TRUE_KEYS and item is True:
                errors.append(f"{prefix}: forbidden true value {current}")
            errors.extend(_detect_forbidden_true_values(item, prefix, current))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            errors.extend(_detect_forbidden_true_values(item, prefix, f"{path}[{index}]"))
    return errors


def _scan_json_payload(rel: str, payload: Mapping[str, Any], errors: list[str]) -> None:
    text = json.dumps(payload, sort_keys=True)
    if SECRET_KEY_RE.search(text):
        errors.append(f"{rel}: contains credential/cookie/token-like key")
    if PAYLOAD_RE.search(text):
        errors.append(f"{rel}: contains forbidden payload/scraping-output-like key")


if __name__ == "__main__":
    raise SystemExit(main())
