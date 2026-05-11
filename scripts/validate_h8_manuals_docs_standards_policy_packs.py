#!/usr/bin/env python3
"""Validate H8-BUNDLE-01 manuals/docs/standards policy packs offline."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_FAMILY = "manuals_docs_standards"
SOURCE_IDS = [
    "bitsavers_docs",
    "ia_manuals_library",
    "manualslib_metadata",
    "vendor_documentation_portal",
    "microsoft_technical_docs",
    "apple_support_developer_docs",
    "ibm_documentation",
    "sun_oracle_documentation",
    "hp_hpe_documentation",
    "dec_vax_pdp_documentation",
    "sgi_documentation",
    "rfc_editor_ietf",
    "w3c_technical_reports",
    "iso_iec_public_standards",
    "ieee_acm_standards_metadata",
    "semiconductor_datasheets",
    "service_manual_schematic_archive",
    "generic_technical_document_collection",
]
EXPECTED_SOURCES = {
    source_id: {
        "source_record": f"examples/sources/source_records/{source_id}_source_v2.json",
        "policy_pack": f"examples/connectors/h8_manuals_docs_standards/policies/{source_id}_policy_pack_v0.json",
    }
    for source_id in SOURCE_IDS
}
INVENTORY_FILES = (
    "control/inventory/source_packs/h8_manuals_docs_standards_source_pack_policy.json",
    "control/inventory/source_packs/h8_manuals_docs_standards_sources.json",
    "control/inventory/source_packs/h8_manuals_docs_standards_connector_families.json",
    "control/inventory/source_packs/h8_technical_document_identity_policy.json",
    "control/inventory/source_packs/h8_manual_artifact_relation_policy.json",
    "control/inventory/source_packs/h8_datasheet_device_identity_policy.json",
    "control/inventory/source_packs/h8_standards_specification_identity_policy.json",
    "control/inventory/source_packs/h8_install_requirement_claim_policy.json",
    "control/inventory/source_packs/h8_repair_service_safety_policy.json",
    "control/inventory/source_packs/h8_access_rights_policy.json",
    "control/inventory/source_packs/h8_manuals_docs_standards_approval_gates.json",
    "control/inventory/source_packs/h8_manuals_docs_standards_output_policy.json",
    "control/inventory/source_packs/h8_manuals_docs_standards_truth_policy.json",
    "control/inventory/source_packs/h8_manuals_docs_standards_no_live_call_policy.json",
    "control/inventory/source_packs/h8_manuals_docs_standards_no_download_extract_policy.json",
)
SOURCE_PACK_EXAMPLES = (
    "examples/source_packs/h8_manuals_docs_standards_source_pack_manifest_v0.json",
    "examples/source_packs/h8_manuals_docs_standards_policy_pack_v0.json",
)
EXTRA_EXAMPLES = (
    "examples/sources/source_records/manuals_docs_standards_policy_blocked_source_v2.json",
    "examples/connectors/h8_manuals_docs_standards/policies/manuals_docs_standards_policy_blocked_pack_v0.json",
    "examples/connectors/h8_manuals_docs_standards/coverage/h8_manuals_docs_standards_coverage_preview_v0.json",
    "examples/connectors/h8_manuals_docs_standards/scorecards/h8_manuals_docs_standards_scorecard_preview_v0.json",
)
DOCS = (
    "docs/reference/H8_MANUALS_DOCS_STANDARDS_SOURCE_PACKS.md",
    "docs/reference/H8_TECHNICAL_DOCUMENT_IDENTITY_POLICY.md",
    "docs/reference/H8_MANUAL_ARTIFACT_RELATION_POLICY.md",
    "docs/reference/H8_DATASHEET_DEVICE_IDENTITY_POLICY.md",
    "docs/reference/H8_STANDARDS_SPECIFICATION_IDENTITY_POLICY.md",
    "docs/reference/H8_INSTALL_REQUIREMENT_CLAIM_POLICY.md",
    "docs/reference/H8_REPAIR_SERVICE_SAFETY_POLICY.md",
    "docs/reference/H8_ACCESS_RIGHTS_POLICY.md",
    "docs/architecture/H8_MANUALS_DOCS_STANDARDS_MODEL.md",
    "docs/architecture/MANUALS_DOCS_STANDARDS_SOURCE_FAMILY_MODEL.md",
    "docs/operations/H8_MANUALS_DOCS_STANDARDS_POLICY_GATES.md",
    "docs/operations/H8_MANUALS_DOCS_STANDARDS_NO_LIVE_CALL_POLICY.md",
    "docs/operations/H8_MANUALS_DOCS_STANDARDS_NO_DOWNLOAD_EXTRACT_POLICY.md",
    "docs/operations/H8_MANUALS_DOCS_STANDARDS_FIXTURE_PLAN.md",
)
AUDIT_FILES = tuple(
    f"control/audits/h8-bundle-01-manuals-docs-standards-policy-packs-v0/{name}"
    for name in (
        "README.md",
        "h8_bundle_01_report.json",
        "h8_source_pack_summary.md",
        "h8_source_policy_gate_summary.md",
        "h8_connector_family_summary.md",
        "h8_technical_document_identity_policy_summary.md",
        "h8_manual_artifact_relation_policy_summary.md",
        "h8_datasheet_device_identity_policy_summary.md",
        "h8_standards_specification_identity_policy_summary.md",
        "h8_install_requirement_claim_policy_summary.md",
        "h8_repair_service_safety_policy_summary.md",
        "h8_access_rights_policy_summary.md",
        "h8_fixture_plan.md",
        "h8_no_live_call_report.md",
        "h8_no_download_extract_report.md",
        "h8_readiness_for_fixture_runtime.md",
        "validation.md",
        "generated/sample_h8_source_summary.json",
        "generated/sample_h8_source_summary.md",
        "generated/sample_h8_option_matrix.json",
    )
)
H8_PYTHON_FILES = (
    "scripts/validate_h8_manuals_docs_standards_policy_packs.py",
    "scripts/summarize_h8_manuals_docs_standards_sources.py",
)
ALLOWED_CURRENT_OPERATIONS = {
    "inspect_fixture",
    "normalize_fixture_future",
    "record_source_policy",
    "record_source_metadata_preview",
    "record_identity_policy",
    "record_relation_policy",
    "record_access_rights_policy",
    "create_coverage_preview",
    "create_scorecard_preview",
}
FALSE_REQUIRED_KEYS = {
    "live_access_enabled",
    "source_sync_enabled",
    "connector_runtime_enabled",
    "approved_live_probe_enabled",
    "api_query_enabled",
    "catalog_fetch_enabled",
    "document_download_enabled",
    "pdf_download_enabled",
    "scan_download_enabled",
    "full_text_fetch_enabled",
    "ocr_extraction_enabled",
    "iiif_manifest_fetch_enabled",
    "standards_document_fetch_enabled",
    "datasheet_download_enabled",
    "schematic_download_enabled",
    "service_manual_download_enabled",
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
    "technical_document_metadata_is_document_truth",
    "manual_artifact_relation_is_relation_truth",
    "datasheet_metadata_is_device_truth",
    "standards_metadata_is_standards_truth",
    "install_requirement_claim_is_installability_truth",
    "repair_service_claim_is_safety_truth",
    "access_metadata_is_rights_truth",
    "open_access_metadata_is_rights_clearance",
    "document_metadata_grants_download_permission",
    "accepted_document_truth",
    "accepted_manual_artifact_relation_truth",
    "accepted_datasheet_device_truth",
    "accepted_standard_truth",
    "accepted_install_requirement_truth",
    "accepted_repair_safety_truth",
    "accepted_access_rights_truth",
    "accepted_source_truth",
    "accepted_evidence_truth",
    "accepted_candidate_truth",
    "accepted_public_record",
    "public_index_mutation_allowed",
    "master_index_mutation_allowed",
    "public_index_mutated",
    "master_index_mutated",
    "mutated_public_index",
    "mutated_master_index",
    "rights_clearance_claimed",
    "open_access_truth_claimed",
    "compatibility_correctness_claimed",
    "installability_claimed",
    "repair_safety_claimed",
    "electrical_safety_claimed",
    "malware_safety_claimed",
    "verified_authenticity_claimed",
    "verified_availability_claimed",
    "production_readiness_claimed",
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
    r'"[^"]*(pdf_payload|manual_payload|datasheet_payload|standards_document_payload|scan_payload|ocr_payload|schematic_payload|full_text_payload|media_payload|restricted_payload|scraping_output|crawling_output|browser_automation_output)[^"]*"\s*:',
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
        print("H8 manuals/docs/standards policy pack validation", file=stdout)
        print(f"status: {result['status']}", file=stdout)
        print(f"errors: {len(result['errors'])}", file=stdout)
        for error in result["errors"]:
            print(f"- {error}", file=stdout)
    return 0 if result["status"] == "valid" else 1


def validate_repo(root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    payloads: dict[str, dict[str, Any]] = {}
    required_paths = list(INVENTORY_FILES + SOURCE_PACK_EXAMPLES + EXTRA_EXAMPLES + DOCS + AUDIT_FILES + H8_PYTHON_FILES)
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
    inventory = payloads.get("control/inventory/source_packs/h8_manuals_docs_standards_sources.json", {})
    sources = inventory.get("sources", [])
    if not isinstance(sources, list):
        errors.append("h8 source inventory must contain sources list")
        sources = []
    source_ids = [item.get("source_id") for item in sources if isinstance(item, Mapping)]
    if len(sources) != 18:
        errors.append(f"h8 source inventory expected 18 sources, got {len(sources)}")
    if sorted(source_ids) != sorted(EXPECTED_SOURCES):
        errors.append("h8 source inventory source IDs do not match expected set")
    if len(source_ids) != len(set(source_ids)):
        errors.append("h8 source inventory source IDs must be unique")
    for source_id, paths in EXPECTED_SOURCES.items():
        errors.extend(validate_source_record(source_id, payloads.get(paths["source_record"], {}), known))
        errors.extend(validate_policy_pack(source_id, payloads.get(paths["policy_pack"], {})))
    blocked_record = payloads.get("examples/sources/source_records/manuals_docs_standards_policy_blocked_source_v2.json", {})
    if blocked_record:
        errors.extend(validate_source_record("manuals_docs_standards_policy_blocked", blocked_record, known, allow_blocked=True))
    blocked_pack = payloads.get("examples/connectors/h8_manuals_docs_standards/policies/manuals_docs_standards_policy_blocked_pack_v0.json", {})
    if blocked_pack:
        errors.extend(validate_policy_pack("manuals_docs_standards_policy_blocked", blocked_pack, allow_blocked=True))
    errors.extend(validate_coverage_preview(payloads.get("examples/connectors/h8_manuals_docs_standards/coverage/h8_manuals_docs_standards_coverage_preview_v0.json", {})))
    errors.extend(validate_scorecard_preview(payloads.get("examples/connectors/h8_manuals_docs_standards/scorecards/h8_manuals_docs_standards_scorecard_preview_v0.json", {})))
    errors.extend(validate_policies(payloads))
    errors.extend(validate_registry_entries(root))
    errors.extend(scan_python_files(root))
    errors.extend(scan_for_private_roots(root))
    return {
        "schema_version": "h8_manuals_docs_standards_policy_pack_validation.v0",
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
        "technical_document_identity_support",
        "manual_artifact_relation_support",
        "datasheet_device_identity_support",
        "standards_specification_identity_support",
        "install_requirement_claim_support",
        "repair_service_safety_support",
        "access_rights_support",
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
    if pack.get("schema_version") != "h8_manuals_docs_standards_policy_pack.v0":
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
        "technical_document_identity_mapping_future",
        "manual_artifact_relation_mapping_future",
        "datasheet_device_identity_mapping_future",
        "standards_specification_identity_mapping_future",
        "install_requirement_claim_mapping_future",
        "repair_service_safety_mapping_future",
        "access_rights_mapping_future",
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
    prefix = "coverage h8_manuals_docs_standards"
    if coverage.get("schema_version") != "h8_manuals_docs_standards_coverage_preview.v0":
        errors.append(f"{prefix}: schema_version mismatch")
    if coverage.get("source_count") != 18:
        errors.append(f"{prefix}: source_count must be 18")
    if coverage.get("coverage_basis") not in {"policy_pack_only", "example_only"}:
        errors.append(f"{prefix}: coverage_basis must be policy_pack_only or example_only")
    if coverage.get("coverage_depth_current") not in {"D0_source_known", "D1_catalog_indexed"}:
        errors.append(f"{prefix}: coverage_depth_current must be D0 or D1 preview")
    for key in ("records_seen", "api_queries_performed", "catalog_fetches_performed", "downloads_performed", "full_text_fetches_performed", "ocr_extractions_performed", "scraping_crawling_performed"):
        if coverage.get(key) != 0:
            errors.append(f"{prefix}: {key} must be 0")
    errors.extend(_detect_forbidden_true_values(coverage, prefix))
    return errors


def validate_scorecard_preview(scorecard: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    prefix = "scorecard h8_manuals_docs_standards"
    if scorecard.get("schema_version") != "h8_manuals_docs_standards_scorecard_preview.v0":
        errors.append(f"{prefix}: schema_version mismatch")
    if scorecard.get("source_count") != 18:
        errors.append(f"{prefix}: source_count must be 18")
    expected_statuses = {
        "fixture_replay_status": "not_started",
        "policy_evaluation_status": "planned",
        "live_probe_envelope_status": "not_approved",
        "source_cache_mapping_status": "planned",
        "evidence_mapping_status": "planned",
        "technical_document_identity_mapping_status": "planned",
        "manual_artifact_relation_mapping_status": "planned",
        "datasheet_device_identity_mapping_status": "planned",
        "standards_specification_identity_mapping_status": "planned",
        "install_requirement_claim_mapping_status": "planned",
        "repair_service_safety_mapping_status": "planned",
        "access_rights_mapping_status": "planned",
        "quality_delta_status": "not_started",
        "document_download_status": "forbidden_current",
        "full_text_ocr_status": "forbidden_current",
        "scraping_crawling_status": "forbidden_current",
    }
    for key, expected in expected_statuses.items():
        if scorecard.get(key) != expected:
            errors.append(f"{prefix}: {key} must be {expected}")
    errors.extend(_detect_forbidden_true_values(scorecard, prefix))
    return errors


def validate_policies(payloads: Mapping[str, Mapping[str, Any]]) -> list[str]:
    errors: list[str] = []
    source_policy = payloads.get("control/inventory/source_packs/h8_manuals_docs_standards_source_pack_policy.json", {})
    for key in FALSE_REQUIRED_KEYS | {"source_pack_import_enabled"}:
        if source_policy.get(key) is not False:
            errors.append(f"source policy: {key} must be false")
    for key in ("source_pack_export_only", "review_required_before_live_access", "review_required_before_source_cache_write", "review_required_before_evidence_acceptance", "review_required_before_public_index_use", "review_required_before_master_index"):
        if source_policy.get(key) is not True:
            errors.append(f"source policy: {key} must be true")
    checks = [
        ("control/inventory/source_packs/h8_technical_document_identity_policy.json", "document_boundary", (
            "technical_document_identity_candidate_is_not_accepted_document_truth",
            "document_metadata_does_not_prove_document_completeness",
            "ocr_full_text_availability_metadata_is_not_extraction_permission",
            "checksum_metadata_does_not_prove_authenticity_unless_reviewed",
            "catalog_presence_does_not_prove_lawful_access_or_current_availability",
        )),
        ("control/inventory/source_packs/h8_manual_artifact_relation_policy.json", "relation_boundary", (
            "manual_artifact_relation_candidate_is_not_accepted_relation_truth",
            "title_model_string_match_does_not_prove_applicability",
            "manual_presence_does_not_prove_compatibility_installability_repair_safety_or_rights",
        )),
        ("control/inventory/source_packs/h8_datasheet_device_identity_policy.json", "device_boundary", (
            "datasheet_device_identity_candidate_is_not_accepted_device_truth",
            "electrical_metadata_is_not_engineering_safety_proof",
            "pinout_package_metadata_requires_review_before_action",
            "lifecycle_status_is_source_observation_not_availability_truth",
            "cross_reference_candidates_require_review",
        )),
        ("control/inventory/source_packs/h8_standards_specification_identity_policy.json", "standards_boundary", (
            "standard_specification_identity_candidate_is_not_accepted_standards_truth",
            "public_metadata_does_not_grant_document_access",
            "standard_status_metadata_may_be_stale",
            "conformance_compliance_is_not_verified",
            "paywalled_restricted_standards_remain_policy_blocked_by_default",
        )),
        ("control/inventory/source_packs/h8_install_requirement_claim_policy.json", "install_boundary", (
            "install_requirement_candidate_is_not_verified_installability",
            "manual_instructions_do_not_prove_safe_execution",
            "compatibility_notes_require_review",
            "installation_actions_remain_blocked_until_track_j_policy_opens_them",
        )),
        ("control/inventory/source_packs/h8_repair_service_safety_policy.json", "repair_boundary", (
            "repair_service_candidate_is_not_repair_safety_truth",
            "service_instructions_do_not_authorize_action",
            "electrical_mechanical_safety_requires_human_review",
            "firmware_flashing_calibration_mains_voltage_repair_and_hazardous_procedures_remain_blocked",
            "eureka_may_index_metadata_and_evidence_candidates_only",
        )),
        ("control/inventory/source_packs/h8_access_rights_policy.json", "access_boundary", (
            "access_metadata_is_not_rights_clearance",
            "public_manual_availability_does_not_prove_redistribution_rights",
            "landing_page_exists_does_not_grant_download_permission",
            "paywalled_restricted_sources_are_policy_blocked_by_default",
            "download_permission_current_remains_false_in_h8_bundle_01",
        )),
    ]
    for rel, section, keys in checks:
        errors.extend(_require_true(payloads.get(rel, {}).get(section, {}), keys, rel))
    approvals = payloads.get("control/inventory/source_packs/h8_manuals_docs_standards_approval_gates.json", {})
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
    for family in ("technical_document_catalog", "manual_library_metadata", "vendor_documentation_catalog", "standards_metadata", "datasheet_catalog", "service_manual_catalog", "html_catalog", "api_json", "restricted_manifest_only"):
        if family not in registered:
            errors.append(f"connector family registry missing {family}")
    return errors


def scan_python_files(root: Path) -> list[str]:
    errors: list[str] = []
    for rel in H8_PYTHON_FILES:
        text = (root / rel).read_text(encoding="utf-8")
        if BANNED_IMPORT_RE.search(text):
            errors.append(f"{rel}: imports network/provider/browser library")
    return errors


def scan_for_private_roots(root: Path) -> list[str]:
    errors: list[str] = []
    for rel in (".aide.local", ".local/eureka", ".cache/eureka", "document_downloads", "standards_downloads", "manual_downloads", "datasheet_downloads", "repair_manual_dumps", "ocr_cache", "media_downloads"):
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
