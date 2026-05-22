#!/usr/bin/env python3
"""Validate H9-BUNDLE-01 media metadata policy packs offline."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]
SOURCE_FAMILY = "media_metadata"
SOURCE_IDS = [
    "wikimedia_commons",
    "openverse",
    "flickr_commons",
    "david_rumsey_maps",
    "nasa_image_video",
    "met_museum_collection",
    "art_institute_chicago",
    "musicbrainz",
    "discogs",
    "rate_your_music_policy_limited",
    "acoustid_policy_limited",
    "imslp",
    "librivox",
    "freesound",
    "great_78_project",
    "live_music_archive",
    "smithsonian_folkways",
    "prelinger_archives",
    "ubuweb_policy_limited",
    "vimeo_creative_commons_policy_limited",
]
SOURCE_FILES = {
    "wikimedia_commons": "wikimedia_commons_source_v2.json",
    "openverse": "openverse_source_v2.json",
    "flickr_commons": "flickr_commons_source_v2.json",
    "david_rumsey_maps": "david_rumsey_maps_source_v2.json",
    "nasa_image_video": "nasa_image_video_source_v2.json",
    "met_museum_collection": "met_museum_collection_source_v2.json",
    "art_institute_chicago": "art_institute_chicago_source_v2.json",
    "musicbrainz": "musicbrainz_source_v2.json",
    "discogs": "discogs_source_v2.json",
    "rate_your_music_policy_limited": "rate_your_music_policy_limited_source_v2.json",
    "acoustid_policy_limited": "acoustid_policy_limited_source_v2.json",
    "imslp": "imslp_source_v2.json",
    "librivox": "librivox_source_v2.json",
    "freesound": "freesound_source_v2.json",
    "great_78_project": "great_78_project_source_v2.json",
    "live_music_archive": "live_music_archive_source_v2.json",
    "smithsonian_folkways": "smithsonian_folkways_source_v2.json",
    "prelinger_archives": "prelinger_archives_source_v2.json",
    "ubuweb_policy_limited": "ubuweb_policy_limited_source_v2.json",
    "vimeo_creative_commons_policy_limited": "vimeo_creative_commons_policy_limited_source_v2.json",
}
POLICY_FILES_BY_SOURCE = {
    "wikimedia_commons": "wikimedia_commons_policy_pack_v0.json",
    "openverse": "openverse_policy_pack_v0.json",
    "flickr_commons": "flickr_commons_policy_pack_v0.json",
    "david_rumsey_maps": "david_rumsey_maps_policy_pack_v0.json",
    "nasa_image_video": "nasa_image_video_policy_pack_v0.json",
    "met_museum_collection": "met_museum_collection_policy_pack_v0.json",
    "art_institute_chicago": "art_institute_chicago_policy_pack_v0.json",
    "musicbrainz": "musicbrainz_policy_pack_v0.json",
    "discogs": "discogs_policy_pack_v0.json",
    "rate_your_music_policy_limited": "rate_your_music_policy_limited_pack_v0.json",
    "acoustid_policy_limited": "acoustid_policy_limited_pack_v0.json",
    "imslp": "imslp_policy_pack_v0.json",
    "librivox": "librivox_policy_pack_v0.json",
    "freesound": "freesound_policy_pack_v0.json",
    "great_78_project": "great_78_project_policy_pack_v0.json",
    "live_music_archive": "live_music_archive_policy_pack_v0.json",
    "smithsonian_folkways": "smithsonian_folkways_policy_pack_v0.json",
    "prelinger_archives": "prelinger_archives_policy_pack_v0.json",
    "ubuweb_policy_limited": "ubuweb_policy_limited_pack_v0.json",
    "vimeo_creative_commons_policy_limited": "vimeo_creative_commons_policy_limited_pack_v0.json",
}
INVENTORY_FILES = (
    "control/inventory/source_packs/h9_media_metadata_source_pack_policy.json",
    "control/inventory/source_packs/h9_media_metadata_sources.json",
    "control/inventory/source_packs/h9_media_metadata_connector_families.json",
    "control/inventory/source_packs/h9_media_object_identity_policy.json",
    "control/inventory/source_packs/h9_music_work_recording_release_policy.json",
    "control/inventory/source_packs/h9_image_video_map_identity_policy.json",
    "control/inventory/source_packs/h9_media_creator_collection_relation_policy.json",
    "control/inventory/source_packs/h9_media_fingerprint_policy.json",
    "control/inventory/source_packs/h9_media_rights_license_policy.json",
    "control/inventory/source_packs/h9_media_safety_privacy_policy.json",
    "control/inventory/source_packs/h9_media_metadata_approval_gates.json",
    "control/inventory/source_packs/h9_media_metadata_output_policy.json",
    "control/inventory/source_packs/h9_media_metadata_truth_policy.json",
    "control/inventory/source_packs/h9_media_metadata_no_live_call_policy.json",
    "control/inventory/source_packs/h9_media_metadata_no_download_upload_policy.json",
)
SOURCE_PACK_EXAMPLES = (
    "examples/source_packs/h9_media_metadata_source_pack_manifest_v0.json",
    "examples/source_packs/h9_media_metadata_policy_pack_v0.json",
)
EXTRA_EXAMPLES = (
    "examples/sources/source_records/media_metadata_policy_blocked_source_v2.json",
    "examples/connectors/h9_media_metadata/policies/media_metadata_policy_blocked_pack_v0.json",
    "examples/connectors/h9_media_metadata/coverage/h9_media_metadata_coverage_preview_v0.json",
    "examples/connectors/h9_media_metadata/scorecards/h9_media_metadata_scorecard_preview_v0.json",
)
DOCS = (
    "docs/reference/H9_MEDIA_METADATA_SOURCE_PACKS.md",
    "docs/reference/H9_MEDIA_OBJECT_IDENTITY_POLICY.md",
    "docs/reference/H9_MUSIC_WORK_RECORDING_RELEASE_POLICY.md",
    "docs/reference/H9_IMAGE_VIDEO_MAP_IDENTITY_POLICY.md",
    "docs/reference/H9_MEDIA_CREATOR_COLLECTION_RELATION_POLICY.md",
    "docs/reference/H9_MEDIA_FINGERPRINT_POLICY.md",
    "docs/reference/H9_MEDIA_RIGHTS_LICENSE_POLICY.md",
    "docs/reference/H9_MEDIA_SAFETY_PRIVACY_POLICY.md",
    "docs/architecture/H9_MEDIA_METADATA_MODEL.md",
    "docs/architecture/MEDIA_METADATA_SOURCE_FAMILY_MODEL.md",
    "docs/operations/H9_MEDIA_METADATA_POLICY_GATES.md",
    "docs/operations/H9_MEDIA_METADATA_NO_LIVE_CALL_POLICY.md",
    "docs/operations/H9_MEDIA_METADATA_NO_DOWNLOAD_UPLOAD_POLICY.md",
    "docs/operations/H9_MEDIA_METADATA_FIXTURE_PLAN.md",
)
AUDIT_FILES = tuple(
    f"control/audits/h9-bundle-01-media-metadata-policy-packs-v0/{name}"
    for name in (
        "README.md",
        "h9_bundle_01_report.json",
        "h9_source_pack_summary.md",
        "h9_source_policy_gate_summary.md",
        "h9_connector_family_summary.md",
        "h9_media_object_identity_policy_summary.md",
        "h9_music_work_recording_release_policy_summary.md",
        "h9_image_video_map_identity_policy_summary.md",
        "h9_media_creator_collection_relation_policy_summary.md",
        "h9_media_fingerprint_policy_summary.md",
        "h9_media_rights_license_policy_summary.md",
        "h9_media_safety_privacy_policy_summary.md",
        "h9_fixture_plan.md",
        "h9_no_live_call_report.md",
        "h9_no_download_upload_report.md",
        "h9_readiness_for_fixture_runtime.md",
        "validation.md",
        "generated/sample_h9_source_summary.json",
        "generated/sample_h9_source_summary.md",
        "generated/sample_h9_option_matrix.json",
    )
)
H9_PYTHON_FILES = (
    "scripts/validate_h9_media_metadata_policy_packs.py",
    "scripts/summarize_h9_media_metadata_sources.py",
)
ALLOWED_CURRENT_OPERATIONS = {
    "inspect_fixture",
    "normalize_fixture_future",
    "record_source_policy",
    "record_source_metadata_preview",
    "record_identity_policy",
    "record_relation_policy",
    "record_rights_license_policy",
    "record_safety_privacy_policy",
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
    "media_download_enabled",
    "image_download_enabled",
    "video_download_enabled",
    "audio_download_enabled",
    "map_download_enabled",
    "score_download_enabled",
    "thumbnail_fetch_enabled",
    "fingerprint_lookup_enabled",
    "fingerprint_submission_enabled",
    "fingerprint_generation_enabled",
    "media_upload_enabled",
    "user_media_upload_enabled",
    "metadata_scraping_enabled",
    "scraping_enabled",
    "crawling_enabled",
    "bypass_or_automation_enabled",
    "restricted_rights_sensitive_source_enabled",
    "download_permission_current",
    "redistribution_permission_current",
    "upload_allowed_current",
    "fingerprint_calculation_allowed_current",
    "lookup_allowed_current",
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
    "media_object_metadata_is_media_truth",
    "music_metadata_is_music_truth",
    "image_video_map_metadata_is_object_truth",
    "media_relation_is_relation_truth",
    "fingerprint_match_is_identity_truth",
    "rights_metadata_is_rights_truth",
    "license_metadata_is_rights_clearance",
    "public_domain_metadata_is_public_domain_truth",
    "creative_commons_metadata_is_license_truth",
    "safety_metadata_is_safety_truth",
    "media_metadata_grants_download_permission",
    "accepted_media_identity_truth",
    "accepted_music_identity_truth",
    "accepted_image_video_map_truth",
    "accepted_creator_collection_relation_truth",
    "accepted_fingerprint_identity_truth",
    "accepted_rights_license_truth",
    "accepted_safety_privacy_truth",
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
    "public_domain_truth_claimed",
    "creative_commons_truth_claimed",
    "content_safety_claimed",
    "privacy_safety_claimed",
    "malware_safety_claimed",
    "verified_authenticity_claimed",
    "production_readiness_claimed",
}
BANNED_IMPORT_RE = re.compile(
    r"^\s*(?:from|import)\s+"
    r"(requests|urllib|httpx|aiohttp|socket|ftplib|smtplib|webbrowser|selenium|playwright|openai|anthropic)\b",
    re.MULTILINE,
)
SECRET_KEY_RE = re.compile(
    r"[^a-z0-9](api[_-]?key|api[_-]?token|access[_-]?token|auth[_-]?token|client_secret|password|private_key|cookie)[^a-z0-9]",
    re.IGNORECASE,
)
PAYLOAD_KEY_RE = re.compile(
    r"(media_payload|image_payload|video_payload|audio_payload|map_payload|score_payload|thumbnail_payload|preview_payload|fingerprint_submission_payload|user_media_payload|restricted_payload|scraping_output|crawling_output|browser_automation_output)",
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
        print("H9 media metadata policy pack validation", file=stdout)
        print(f"status: {result['status']}", file=stdout)
        print(f"error_count: {len(result['errors'])}", file=stdout)
        for error in result["errors"][:25]:
            print(f"ERROR: {error}", file=stdout)
    return 0 if result["status"] == "valid" else 1


def validate_repo(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    required = list(INVENTORY_FILES) + list(SOURCE_PACK_EXAMPLES) + list(EXTRA_EXAMPLES) + list(DOCS) + list(AUDIT_FILES) + list(H9_PYTHON_FILES)
    required.extend(f"examples/sources/source_records/{SOURCE_FILES[source_id]}" for source_id in SOURCE_IDS)
    required.extend(f"examples/connectors/h9_media_metadata/policies/{POLICY_FILES_BY_SOURCE[source_id]}" for source_id in SOURCE_IDS)
    for rel in required:
        path = repo_root / rel
        if not path.exists():
            errors.append(f"missing required file: {rel}")
    known = _load_known_values(repo_root, errors)
    for rel in required:
        if rel.endswith(".json") and (repo_root / rel).exists():
            try:
                payload = _load_json(repo_root / rel)
            except Exception as exc:  # noqa: BLE001
                errors.append(f"{rel} invalid JSON: {exc}")
                continue
            _scan_json_payload(rel, payload, errors)

    inventory_path = repo_root / "control/inventory/source_packs/h9_media_metadata_sources.json"
    if inventory_path.exists():
        inventory = _load_json(inventory_path)
        sources = inventory.get("sources", [])
        if len(sources) != 20:
            errors.append("H9 source inventory must contain 20 sources")
        seen = [str(item.get("source_id")) for item in sources if isinstance(item, Mapping)]
        if sorted(seen) != sorted(SOURCE_IDS):
            errors.append("H9 source inventory source IDs do not match required H9 source IDs")
        if len(seen) != len(set(seen)):
            errors.append("H9 source inventory contains duplicate source IDs")
        for source in sources:
            if isinstance(source, Mapping):
                errors.extend(validate_source_record(str(source.get("source_id", "")), source, known))

    for source_id in SOURCE_IDS:
        source_path = repo_root / "examples/sources/source_records" / SOURCE_FILES[source_id]
        if source_path.exists():
            errors.extend(validate_source_record(source_id, _load_json(source_path), known))
        pack_path = repo_root / "examples/connectors/h9_media_metadata/policies" / POLICY_FILES_BY_SOURCE[source_id]
        if pack_path.exists():
            errors.extend(validate_policy_pack(source_id, _load_json(pack_path)))

    coverage_path = repo_root / "examples/connectors/h9_media_metadata/coverage/h9_media_metadata_coverage_preview_v0.json"
    if coverage_path.exists():
        errors.extend(validate_coverage_preview(_load_json(coverage_path)))
    scorecard_path = repo_root / "examples/connectors/h9_media_metadata/scorecards/h9_media_metadata_scorecard_preview_v0.json"
    if scorecard_path.exists():
        errors.extend(validate_scorecard_preview(_load_json(scorecard_path)))

    for rel in H9_PYTHON_FILES:
        path = repo_root / rel
        if path.exists() and BANNED_IMPORT_RE.search(path.read_text(encoding="utf-8")):
            errors.append(f"{rel} imports network/API/model/browser library")

    return {
        "schema_version": "h9_media_metadata_policy_pack_validation.v0",
        "status": "valid" if not errors else "invalid",
        "source_count": 20,
        "errors": errors,
        "network_calls_made": False,
        "model_provider_calls_made": False,
    }


def validate_source_record(source_id: str, payload: Mapping[str, Any], known: Mapping[str, set[str]]) -> list[str]:
    errors: list[str] = []
    if payload.get("source_id") != source_id:
        errors.append(f"{source_id} source_id mismatch")
    if payload.get("source_family") != SOURCE_FAMILY:
        errors.append(f"{source_id} source_family must be {SOURCE_FAMILY}")
    if SOURCE_FAMILY not in known["source_families"]:
        errors.append("media_metadata source family missing from source family registry")
    if payload.get("connector_family") not in known["connector_families"]:
        errors.append(f"{source_id} unknown connector_family: {payload.get('connector_family')}")
    if payload.get("trust_lane") not in known["trust_lanes"]:
        errors.append(f"{source_id} unknown trust_lane: {payload.get('trust_lane')}")
    if payload.get("current_index_depth") not in known["index_depths"]:
        errors.append(f"{source_id} unknown current_index_depth: {payload.get('current_index_depth')}")
    if payload.get("current_access_mode") not in {"no_autonomous_access", "committed_fixture_only"}:
        errors.append(f"{source_id} current_access_mode must remain no_autonomous_access or committed_fixture_only")
    for key in FALSE_REQUIRED_KEYS:
        if key in payload and payload.get(key) is not False:
            errors.append(f"{source_id} {key} must be false")
    for key in (
        "media_object_identity_support",
        "music_identity_support",
        "image_video_map_identity_support",
        "creator_collection_relation_support",
        "fingerprint_metadata_support",
        "rights_license_support",
        "safety_privacy_support",
    ):
        if not isinstance(payload.get(key), Mapping):
            errors.append(f"{source_id} missing support mapping: {key}")
    _scan_json_payload(source_id, payload, errors)
    return errors


def validate_policy_pack(source_id: str, payload: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("source_id") != source_id:
        errors.append(f"{source_id} policy pack source_id mismatch")
    if payload.get("source_family") != SOURCE_FAMILY:
        errors.append(f"{source_id} policy pack source_family must be {SOURCE_FAMILY}")
    allowed = set(payload.get("allowed_current_operations", []))
    if not allowed.issubset(ALLOWED_CURRENT_OPERATIONS):
        errors.append(f"{source_id} policy pack has unexpected allowed operation")
    if not ALLOWED_CURRENT_OPERATIONS.issubset(allowed):
        errors.append(f"{source_id} policy pack missing required allowed operations")
    _scan_json_payload(f"{source_id} policy pack", payload, errors)
    return errors


def validate_coverage_preview(payload: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("coverage_manifest_is_exhaustive_global_coverage") is not False:
        errors.append("coverage preview must not claim exhaustive global coverage")
    for key in ("live_access_enabled",):
        if payload.get(key) is not False:
            errors.append(f"coverage preview {key} must be false")
    for key in ("records_seen", "api_queries_performed", "catalog_fetches_performed", "media_downloads_performed", "media_uploads_performed", "fingerprint_submissions_performed", "scraping_crawling_performed"):
        if payload.get(key) != 0:
            errors.append(f"coverage preview {key} must be 0")
    _scan_json_payload("coverage preview", payload, errors)
    return errors


def validate_scorecard_preview(payload: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("production_ready") is not False:
        errors.append("scorecard preview production_ready must be false")
    if payload.get("auto_approves_future_connectors") is not False:
        errors.append("scorecard preview auto_approves_future_connectors must be false")
    for key in ("media_download_status", "media_upload_status", "fingerprint_submission_status", "scraping_crawling_status"):
        if payload.get(key) != "forbidden_current":
            errors.append(f"scorecard preview {key} must be forbidden_current")
    _scan_json_payload("scorecard preview", payload, errors)
    return errors


def _load_known_values(repo_root: Path, errors: list[str]) -> dict[str, set[str]]:
    source_families = set()
    connector_families = set()
    trust_lanes = {"official", "community", "preservation", "restricted_manifest_only", "web_archive_trace", "package_registry", "research_library", "unknown"}
    index_depths = {"D0_source_known", "D1_catalog_indexed", "D1_catalog_indexed_preview_only", "D2_metadata_indexed"}
    try:
        registry = _load_json(repo_root / "control/inventory/sources/source_family_registry.json")
        source_families = {str(item.get("family_id")) for item in registry.get("families", []) if isinstance(item, Mapping)}
    except Exception as exc:  # noqa: BLE001
        errors.append(f"could not load source family registry: {exc}")
    try:
        mapping = _load_json(repo_root / "control/inventory/source_packs/h9_media_metadata_connector_families.json")
        connector_families.update(str(item.get("connector_family")) for item in mapping.get("connector_families", []) if isinstance(item, Mapping))
    except Exception as exc:  # noqa: BLE001
        errors.append(f"could not load H9 connector family mapping: {exc}")
    try:
        registry = _load_json(repo_root / "control/inventory/connectors/connector_family_registry.json")
        connector_families.update(str(item.get("family_id")) for item in registry.get("families", []) if isinstance(item, Mapping))
    except Exception:
        pass
    return {
        "source_families": source_families,
        "connector_families": connector_families,
        "trust_lanes": trust_lanes,
        "index_depths": index_depths,
    }


def _scan_json_payload(label: str, value: Any, errors: list[str]) -> None:
    if isinstance(value, Mapping):
        for key, item in value.items():
            key_text = str(key)
            padded = f" {key_text} "
            if SECRET_KEY_RE.search(padded):
                errors.append(f"{label} contains credential-like key: {key_text}")
            if PAYLOAD_KEY_RE.search(key_text):
                errors.append(f"{label} contains forbidden media/restricted/scraping payload key: {key_text}")
            if key_text in FORBIDDEN_TRUE_KEYS and item is True:
                errors.append(f"{label} forbidden true claim: {key_text}")
            _scan_json_payload(label, item, errors)
    elif isinstance(value, list):
        for item in value:
            _scan_json_payload(label, item, errors)


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    raise SystemExit(main())
