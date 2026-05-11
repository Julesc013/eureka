#!/usr/bin/env python3
"""Validate H12-BUNDLE-01 retro/community policy packs offline."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_FAMILY = "retro_community_archive"
SOURCE_IDS = ["winworld_metadata", "macintosh_garden_metadata", "macintosh_repository_metadata", "vetusware_metadata", "oldversion_metadata", "my_abandonware_metadata", "dos_games_archive_metadata", "hobbes_os2_archive_metadata", "aminet_metadata", "atarimania_metadata", "tucows_ia_legacy_metadata", "betaarchive_public_metadata_policy_limited", "generic_retro_community_archive"]
BLOCKED_SOURCE_ID = "retro_community_policy_blocked"
SOURCE_FILES = {source_id: f"{source_id}_source_v2.json" for source_id in SOURCE_IDS + [BLOCKED_SOURCE_ID]}
POLICY_FILES_BY_SOURCE = {
    "winworld_metadata": "winworld_metadata_policy_pack_v0.json",
    "macintosh_garden_metadata": "macintosh_garden_metadata_policy_pack_v0.json",
    "macintosh_repository_metadata": "macintosh_repository_metadata_policy_pack_v0.json",
    "vetusware_metadata": "vetusware_metadata_policy_pack_v0.json",
    "oldversion_metadata": "oldversion_metadata_policy_pack_v0.json",
    "my_abandonware_metadata": "my_abandonware_metadata_policy_pack_v0.json",
    "dos_games_archive_metadata": "dos_games_archive_metadata_policy_pack_v0.json",
    "hobbes_os2_archive_metadata": "hobbes_os2_archive_metadata_policy_pack_v0.json",
    "aminet_metadata": "aminet_metadata_policy_pack_v0.json",
    "atarimania_metadata": "atarimania_metadata_policy_pack_v0.json",
    "tucows_ia_legacy_metadata": "tucows_ia_legacy_metadata_policy_pack_v0.json",
    "betaarchive_public_metadata_policy_limited": "betaarchive_public_metadata_policy_limited_pack_v0.json",
    "generic_retro_community_archive": "generic_retro_community_archive_policy_pack_v0.json",
    "retro_community_policy_blocked": "retro_community_policy_blocked_pack_v0.json",
}
INVENTORY_FILES = (
    "control/inventory/source_packs/h12_retro_community_source_pack_policy.json",
    "control/inventory/source_packs/h12_retro_community_sources.json",
    "control/inventory/source_packs/h12_retro_community_connector_families.json",
    "control/inventory/source_packs/h12_retro_software_identity_policy.json",
    "control/inventory/source_packs/h12_platform_version_edition_policy.json",
    "control/inventory/source_packs/h12_archive_item_member_policy.json",
    "control/inventory/source_packs/h12_compatibility_install_note_policy.json",
    "control/inventory/source_packs/h12_community_review_comment_policy.json",
    "control/inventory/source_packs/h12_hash_checksum_policy.json",
    "control/inventory/source_packs/h12_ia_wayback_corroboration_policy.json",
    "control/inventory/source_packs/h12_gated_source_boundary_policy.json",
    "control/inventory/source_packs/h12_retro_rights_safety_policy.json",
    "control/inventory/source_packs/h12_retro_community_approval_gates.json",
    "control/inventory/source_packs/h12_retro_community_output_policy.json",
    "control/inventory/source_packs/h12_retro_community_truth_policy.json",
    "control/inventory/source_packs/h12_retro_community_no_live_call_policy.json",
    "control/inventory/source_packs/h12_retro_community_no_download_execute_policy.json",
)
SOURCE_PACK_EXAMPLES = (
    "examples/source_packs/h12_retro_community_source_pack_manifest_v0.json",
    "examples/source_packs/h12_retro_community_policy_pack_v0.json",
)
EXTRA_EXAMPLES = (
    "examples/connectors/h12_retro_community/coverage/h12_retro_community_coverage_preview_v0.json",
    "examples/connectors/h12_retro_community/scorecards/h12_retro_community_scorecard_preview_v0.json",
)
DOCS = (
    "docs/reference/H12_RETRO_COMMUNITY_SOURCE_PACKS.md",
    "docs/reference/H12_RETRO_SOFTWARE_IDENTITY_POLICY.md",
    "docs/reference/H12_PLATFORM_VERSION_EDITION_POLICY.md",
    "docs/reference/H12_ARCHIVE_ITEM_MEMBER_POLICY.md",
    "docs/reference/H12_COMPATIBILITY_INSTALL_NOTE_POLICY.md",
    "docs/reference/H12_COMMUNITY_REVIEW_COMMENT_POLICY.md",
    "docs/reference/H12_HASH_CHECKSUM_POLICY.md",
    "docs/reference/H12_IA_WAYBACK_CORROBORATION_POLICY.md",
    "docs/reference/H12_GATED_SOURCE_BOUNDARY_POLICY.md",
    "docs/reference/H12_RETRO_RIGHTS_SAFETY_POLICY.md",
    "docs/architecture/H12_RETRO_COMMUNITY_MODEL.md",
    "docs/architecture/RETRO_COMMUNITY_SOURCE_FAMILY_MODEL.md",
    "docs/operations/H12_RETRO_COMMUNITY_POLICY_GATES.md",
    "docs/operations/H12_RETRO_COMMUNITY_NO_LIVE_CALL_POLICY.md",
    "docs/operations/H12_RETRO_COMMUNITY_NO_DOWNLOAD_EXECUTE_POLICY.md",
    "docs/operations/H12_RETRO_COMMUNITY_FIXTURE_PLAN.md",
)
AUDIT_FILES = tuple(
    f"control/audits/h12-bundle-01-retro-community-policy-packs-v0/{name}"
    for name in (
        "README.md",
        "h12_bundle_01_report.json",
        "h12_source_pack_summary.md",
        "h12_source_policy_gate_summary.md",
        "h12_connector_family_summary.md",
        "h12_retro_software_identity_policy_summary.md",
        "h12_platform_version_edition_policy_summary.md",
        "h12_archive_item_member_policy_summary.md",
        "h12_compatibility_install_note_policy_summary.md",
        "h12_community_review_comment_policy_summary.md",
        "h12_hash_checksum_policy_summary.md",
        "h12_ia_wayback_corroboration_policy_summary.md",
        "h12_gated_source_boundary_policy_summary.md",
        "h12_retro_rights_safety_policy_summary.md",
        "h12_fixture_plan.md",
        "h12_no_live_call_report.md",
        "h12_no_download_execute_report.md",
        "h12_readiness_for_fixture_runtime.md",
        "validation.md",
        "generated/sample_h12_source_summary.json",
        "generated/sample_h12_source_summary.md",
        "generated/sample_h12_option_matrix.json",
    )
)
H12_PYTHON_FILES = (
    "scripts/validate_h12_retro_community_policy_packs.py",
    "scripts/summarize_h12_retro_community_sources.py",
)
ALLOWED_CURRENT_OPERATIONS = {"inspect_fixture", "normalize_fixture_future", "record_source_policy", "record_source_metadata_preview", "record_identity_policy", "record_relation_policy", "record_community_claim_policy", "record_rights_safety_policy", "create_coverage_preview", "create_scorecard_preview"}
FALSE_REQUIRED_KEYS = {
    "live_access_enabled",
    "source_sync_enabled",
    "connector_runtime_enabled",
    "approved_live_probe_enabled",
    "api_query_enabled",
    "catalog_fetch_enabled",
    "html_catalog_fetch_enabled",
    "forum_or_comment_fetch_enabled",
    "gated_source_access_enabled",
    "account_access_enabled",
    "download_enabled",
    "downloads_enabled",
    "rom_download_enabled",
    "iso_download_enabled",
    "disc_image_download_enabled",
    "bios_firmware_download_enabled",
    "software_binary_download_enabled",
    "driver_download_enabled",
    "installer_download_enabled",
    "patch_download_enabled",
    "crack_key_serial_handling_enabled",
    "archive_download_enabled",
    "extraction_enabled",
    "emulator_execution_enabled",
    "execution_enabled",
    "install_execute_enabled",
    "acquisition_action_enabled",
    "file_upload_enabled",
    "uploads_enabled",
    "hash_submission_enabled",
    "scraping_enabled",
    "crawling_enabled",
    "bypass_or_automation_enabled",
    "restricted_rights_sensitive_source_enabled",
    "source_pack_import_enabled",
}
FORBIDDEN_TRUE_KEYS = FALSE_REQUIRED_KEYS | {
    "source_pack_is_truth",
    "source_pack_is_accepted_evidence",
    "source_pack_is_imported_state",
    "policy_pack_grants_live_access",
    "capability_grants_permission",
    "coverage_preview_is_exhaustive",
    "coverage_preview_claims_exhaustive_coverage",
    "coverage_manifest_is_exhaustive_global_coverage",
    "scorecard_preview_is_production_ready",
    "scorecard_claims_production_readiness",
    "scorecard_auto_approves_future_connectors",
    "production_ready",
    "auto_approves_future_connectors",
    "retro_software_metadata_is_software_truth",
    "retro_software_identity_candidate_is_truth",
    "platform_version_metadata_is_version_truth",
    "platform_version_edition_candidate_is_truth",
    "archive_item_member_metadata_is_file_truth",
    "archive_item_member_candidate_is_truth",
    "compatibility_install_note_is_compatibility_truth",
    "compatibility_install_note_candidate_is_truth",
    "community_review_comment_is_truth",
    "community_review_comment_candidate_is_truth",
    "hash_checksum_metadata_is_identity_truth",
    "hash_checksum_candidate_is_truth",
    "ia_wayback_corroboration_is_truth",
    "ia_wayback_corroboration_candidate_is_truth",
    "gated_source_metadata_grants_access_permission",
    "rights_safety_metadata_is_rights_or_safety_truth",
    "rights_safety_candidate_is_rights_or_safety_truth",
    "abandonware_label_is_legal_permission",
    "community_download_metadata_grants_acquisition_permission",
    "accepted_retro_software_identity_truth",
    "accepted_platform_version_truth",
    "accepted_archive_item_member_truth",
    "accepted_compatibility_install_truth",
    "accepted_community_review_truth",
    "accepted_hash_checksum_truth",
    "accepted_ia_wayback_corroboration_truth",
    "accepted_gated_source_access_truth",
    "accepted_rights_safety_truth",
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
    "legal_acquisition_claimed",
    "file_authenticity_claimed",
    "checksum_correctness_claimed",
    "compatibility_correctness_claimed",
    "installability_claimed",
    "playability_claimed",
    "malware_safety_claimed",
    "content_safety_claimed",
    "privacy_safety_claimed",
    "community_reputation_claimed",
    "verified_authenticity_claimed",
    "production_readiness_claimed",
}
BANNED_IMPORT_RE = re.compile(
    r"^\s*(?:from|import)\s+"
    r"(requests|httpx|aiohttp|socket|ftplib|smtplib|webbrowser|selenium|playwright|openai|anthropic)\b",
    re.MULTILINE,
)
SECRET_KEY_NAMES = {"api_key", "api_token", "access_token", "auth_token", "client_secret", "password", "private_key", "cookie", "session_cookie"}
PAYLOAD_KEY_RE = re.compile(
    r"(software_binary_payload|rom_payload|iso_payload|disc_image_payload|chd_payload|bios_payload|firmware_payload|driver_payload|installer_payload|patch_payload|crack_payload|keygen_payload|serial_payload|archive_payload|download_payload|extraction_log|execution_log|emulator_output|install_log|acquisition_output|gated_private_content|restricted_payload|scraping_output|crawling_output|browser_automation_output)",
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
        print("H12 retro/community policy pack validation", file=stdout)
        print(f"status: {result['status']}", file=stdout)
        print(f"error_count: {len(result['errors'])}", file=stdout)
        for error in result["errors"][:40]:
            print(f"ERROR: {error}", file=stdout)
    return 0 if result["status"] == "valid" else 1


def validate_repo(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    required = list(INVENTORY_FILES) + list(SOURCE_PACK_EXAMPLES) + list(EXTRA_EXAMPLES) + list(DOCS) + list(AUDIT_FILES) + list(H12_PYTHON_FILES)
    required.extend(f"examples/sources/source_records/{SOURCE_FILES[source_id]}" for source_id in SOURCE_IDS + [BLOCKED_SOURCE_ID])
    required.extend(f"examples/connectors/h12_retro_community/policies/{POLICY_FILES_BY_SOURCE[source_id]}" for source_id in SOURCE_IDS + [BLOCKED_SOURCE_ID])
    for rel in required:
        if not (repo_root / rel).exists():
            errors.append(f"missing required file: {rel}")
    known = _load_known_values(repo_root, errors)
    for rel in required:
        path = repo_root / rel
        if rel.endswith(".json") and path.exists():
            try:
                payload = _load_json(path)
            except Exception as exc:  # noqa: BLE001
                errors.append(f"invalid JSON in {rel}: {exc}")
                continue
            _scan_json_payload(rel, payload, errors)
    inventory_path = repo_root / "control/inventory/source_packs/h12_retro_community_sources.json"
    if inventory_path.exists():
        inventory = _load_json(inventory_path)
        sources = inventory.get("sources", [])
        if inventory.get("source_count") != 13:
            errors.append("H12 source inventory source_count must be 13")
        ids = [item.get("source_id") for item in sources if isinstance(item, Mapping)]
        if sorted(ids) != sorted(SOURCE_IDS):
            errors.append("H12 source inventory must contain exactly the 13 in-scope source IDs")
        if len(ids) != len(set(ids)):
            errors.append("H12 source inventory contains duplicate source IDs")
        for source in sources:
            if isinstance(source, Mapping):
                errors.extend(validate_source_record(str(source.get("source_id", "")), source, known))
    for source_id in SOURCE_IDS + [BLOCKED_SOURCE_ID]:
        source_path = repo_root / "examples/sources/source_records" / SOURCE_FILES[source_id]
        if source_path.exists():
            errors.extend(validate_source_record(source_id, _load_json(source_path), known))
        pack_path = repo_root / "examples/connectors/h12_retro_community/policies" / POLICY_FILES_BY_SOURCE[source_id]
        if pack_path.exists():
            errors.extend(validate_policy_pack(source_id, _load_json(pack_path)))
    coverage_path = repo_root / "examples/connectors/h12_retro_community/coverage/h12_retro_community_coverage_preview_v0.json"
    if coverage_path.exists():
        errors.extend(validate_coverage_preview(_load_json(coverage_path)))
    scorecard_path = repo_root / "examples/connectors/h12_retro_community/scorecards/h12_retro_community_scorecard_preview_v0.json"
    if scorecard_path.exists():
        errors.extend(validate_scorecard_preview(_load_json(scorecard_path)))
    for rel in H12_PYTHON_FILES:
        path = repo_root / rel
        if path.exists():
            text = path.read_text(encoding="utf-8")
            if BANNED_IMPORT_RE.search(text):
                errors.append(f"{rel} imports a network/model/browser/provider library")
    return {"status": "valid" if not errors else "invalid", "errors": errors}


def validate_source_record(source_id: str, record: Mapping[str, Any], known: Mapping[str, set[str]] | None = None) -> list[str]:
    errors: list[str] = []
    if record.get("source_id") != source_id:
        errors.append(f"{source_id}: source_id mismatch")
    if record.get("source_family") != SOURCE_FAMILY:
        errors.append(f"{source_id}: source_family must be {SOURCE_FAMILY}")
    if record.get("trust_lane") not in {"community", "preservation"}:
        errors.append(f"{source_id}: trust_lane must be community or preservation")
    known = known or {}
    if record.get("connector_family") not in known.get("connector_families", set()):
        errors.append(f"{source_id}: connector_family is not known to H12 connector mapping")
    if record.get("current_access_mode") not in {"no_autonomous_access", "committed_fixture_only"}:
        errors.append(f"{source_id}: current_access_mode must block autonomous access")
    if record.get("current_index_depth") not in {"D0_source_known", "D1_catalog_indexed"}:
        errors.append(f"{source_id}: current_index_depth must be D0_source_known or D1_catalog_indexed preview only")
    for key in FALSE_REQUIRED_KEYS:
        if record.get(key) is True:
            errors.append(f"{source_id}: {key} must be false")
    for support_key in (
        "retro_software_identity_support",
        "platform_version_edition_support",
        "archive_item_member_support",
        "compatibility_install_note_support",
        "community_review_comment_support",
        "hash_checksum_support",
        "ia_wayback_corroboration_support",
        "gated_source_boundary_support",
        "rights_safety_support",
    ):
        support = record.get(support_key)
        if not isinstance(support, Mapping):
            errors.append(f"{source_id}: missing {support_key}")
        elif support.get("accepted_truth") is not False or support.get("review_required") is not True:
            errors.append(f"{source_id}: {support_key} must remain candidate/review only")
    _scan_boundaries(f"{source_id}:source_record", record, errors)
    return errors


def validate_policy_pack(source_id: str, pack: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    if pack.get("source_id") != source_id:
        errors.append(f"{source_id}: policy pack source_id mismatch")
    if pack.get("source_family") != SOURCE_FAMILY:
        errors.append(f"{source_id}: policy pack source_family mismatch")
    if pack.get("policy_pack_grants_live_access") is not False:
        errors.append(f"{source_id}: policy pack must not grant live access")
    allowed = set(pack.get("allowed_current_operations", []))
    if not allowed or not allowed.issubset(ALLOWED_CURRENT_OPERATIONS):
        errors.append(f"{source_id}: allowed_current_operations contains non-policy-pack operations")
    forbidden = set(pack.get("forbidden_current_operations", []))
    for required in ("network_call", "api_call", "catalog_fetch", "forum_comment_fetch", "gated_source_access", "software_download", "archive_extraction", "emulator_execution", "acquisition_action", "file_upload", "hash_submission", "scraping_output", "crawling_output", "public_index_mutation", "master_index_mutation"):
        if required not in forbidden:
            errors.append(f"{source_id}: forbidden_current_operations missing {required}")
    for key in FALSE_REQUIRED_KEYS:
        if pack.get(key) is True:
            errors.append(f"{source_id}: {key} must be false in policy pack")
    _scan_boundaries(f"{source_id}:policy_pack", pack, errors)
    return errors


def validate_coverage_preview(preview: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    if preview.get("source_count") != 13:
        errors.append("coverage preview source_count must be 13")
    if preview.get("coverage_manifest_is_exhaustive_global_coverage") is not False:
        errors.append("coverage preview must not claim exhaustive global coverage")
    for key in ("live_access_enabled",):
        if preview.get(key) is True:
            errors.append(f"coverage preview {key} must be false")
    for key in ("records_seen", "api_queries_performed", "catalog_fetches_performed", "forum_comment_fetches_performed", "gated_accesses_performed", "downloads_performed", "extractions_performed", "executions_performed", "acquisition_actions_performed", "uploads_performed", "scraping_crawling_performed"):
        if preview.get(key) != 0:
            errors.append(f"coverage preview {key} must be 0")
    _scan_boundaries("coverage_preview", preview, errors)
    return errors


def validate_scorecard_preview(preview: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    if preview.get("source_count") != 13:
        errors.append("scorecard preview source_count must be 13")
    if preview.get("production_ready") is not False:
        errors.append("scorecard preview must not claim production readiness")
    if preview.get("auto_approves_future_connectors") is not False:
        errors.append("scorecard preview must not auto-approve future connectors")
    for key in ("download_status", "extraction_status", "execution_status", "acquisition_action_status", "gated_source_status", "scraping_crawling_status"):
        if preview.get(key) != "forbidden_current":
            errors.append(f"scorecard preview {key} must be forbidden_current")
    _scan_boundaries("scorecard_preview", preview, errors)
    return errors


def _scan_boundaries(label: str, payload: Mapping[str, Any], errors: list[str]) -> None:
    _scan_json_payload(label, payload, errors)


def _scan_json_payload(label: str, payload: Any, errors: list[str]) -> None:
    if isinstance(payload, Mapping):
        for key, value in payload.items():
            key_text = str(key)
            if key_text in SECRET_KEY_NAMES or PAYLOAD_KEY_RE.search(key_text):
                errors.append(f"{label}: forbidden sensitive/payload key {key_text}")
            if key_text in FORBIDDEN_TRUE_KEYS and value is True:
                errors.append(f"{label}: forbidden true claim {key_text}")
            _scan_json_payload(label, value, errors)
    elif isinstance(payload, list):
        for item in payload:
            _scan_json_payload(label, item, errors)


def _load_known_values(repo_root: Path, errors: list[str]) -> dict[str, set[str]]:
    connector_families = {
        "retro_software_catalog",
        "community_archive_catalog",
        "old_version_catalog",
        "abandonware_metadata_policy_limited",
        "platform_archive_metadata",
        "html_catalog_policy_limited",
        "forum_or_comment_metadata_policy_limited",
        "ia_mirror_bridge",
        "wayback_trace_bridge",
        "gated_community_boundary",
        "restricted_manifest_only",
    }
    mapping_path = repo_root / "control/inventory/source_packs/h12_retro_community_connector_families.json"
    if mapping_path.exists():
        try:
            mapping = _load_json(mapping_path)
            connector_families.update(str(item.get("connector_family")) for item in mapping.get("connector_families", []) if isinstance(item, Mapping))
        except Exception as exc:  # noqa: BLE001
            errors.append(f"cannot load H12 connector families: {exc}")
    return {"connector_families": connector_families}


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    raise SystemExit(main())
