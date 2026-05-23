#!/usr/bin/env python3
"""Validate H11-BUNDLE-01 storefront/app-store policy packs offline."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]
SOURCE_FAMILY = "storefront_app_store_metadata"
SOURCE_IDS = ["microsoft_store_metadata", "mac_app_store_metadata", "apple_app_store_metadata", "google_play_metadata", "fdroid_metadata", "steam_store_metadata", "gog_store_metadata", "itchio_storefront_metadata", "epic_games_store_policy_limited", "humble_store_policy_limited", "chrome_web_store_metadata", "mozilla_addons_metadata", "flathub_metadata", "snapcraft_metadata", "generic_vendor_product_page", "generic_commercial_software_marketplace"]
BLOCKED_SOURCE_ID = "storefront_policy_blocked"
SOURCE_FILES = {"microsoft_store_metadata": "microsoft_store_metadata_source_v2.json", "mac_app_store_metadata": "mac_app_store_metadata_source_v2.json", "apple_app_store_metadata": "apple_app_store_metadata_source_v2.json", "google_play_metadata": "google_play_metadata_source_v2.json", "fdroid_metadata": "fdroid_metadata_source_v2.json", "steam_store_metadata": "steam_store_metadata_source_v2.json", "gog_store_metadata": "gog_store_metadata_source_v2.json", "itchio_storefront_metadata": "itchio_storefront_metadata_source_v2.json", "epic_games_store_policy_limited": "epic_games_store_policy_limited_source_v2.json", "humble_store_policy_limited": "humble_store_policy_limited_source_v2.json", "chrome_web_store_metadata": "chrome_web_store_metadata_source_v2.json", "mozilla_addons_metadata": "mozilla_addons_metadata_source_v2.json", "flathub_metadata": "flathub_metadata_source_v2.json", "snapcraft_metadata": "snapcraft_metadata_source_v2.json", "generic_vendor_product_page": "generic_vendor_product_page_source_v2.json", "generic_commercial_software_marketplace": "generic_commercial_software_marketplace_source_v2.json", "storefront_policy_blocked": "storefront_policy_blocked_source_v2.json"}
POLICY_FILES_BY_SOURCE = {"microsoft_store_metadata": "microsoft_store_metadata_policy_pack_v0.json", "mac_app_store_metadata": "mac_app_store_metadata_policy_pack_v0.json", "apple_app_store_metadata": "apple_app_store_metadata_policy_pack_v0.json", "google_play_metadata": "google_play_metadata_policy_pack_v0.json", "fdroid_metadata": "fdroid_metadata_policy_pack_v0.json", "steam_store_metadata": "steam_store_metadata_policy_pack_v0.json", "gog_store_metadata": "gog_store_metadata_policy_pack_v0.json", "itchio_storefront_metadata": "itchio_storefront_metadata_policy_pack_v0.json", "epic_games_store_policy_limited": "epic_games_store_policy_limited_pack_v0.json", "humble_store_policy_limited": "humble_store_policy_limited_pack_v0.json", "chrome_web_store_metadata": "chrome_web_store_metadata_policy_pack_v0.json", "mozilla_addons_metadata": "mozilla_addons_metadata_policy_pack_v0.json", "flathub_metadata": "flathub_metadata_policy_pack_v0.json", "snapcraft_metadata": "snapcraft_metadata_policy_pack_v0.json", "generic_vendor_product_page": "generic_vendor_product_page_policy_pack_v0.json", "generic_commercial_software_marketplace": "generic_commercial_software_marketplace_policy_pack_v0.json", "storefront_policy_blocked": "storefront_policy_blocked_pack_v0.json"}
INVENTORY_FILES = (
    "control/inventory/source_packs/h11_storefront_source_pack_policy.json",
    "control/inventory/source_packs/h11_storefront_sources.json",
    "control/inventory/source_packs/h11_storefront_connector_families.json",
    "control/inventory/source_packs/h11_storefront_listing_identity_policy.json",
    "control/inventory/source_packs/h11_app_product_identity_policy.json",
    "control/inventory/source_packs/h11_version_release_channel_policy.json",
    "control/inventory/source_packs/h11_price_availability_region_policy.json",
    "control/inventory/source_packs/h11_acquisition_path_candidate_policy.json",
    "control/inventory/source_packs/h11_review_rating_metadata_policy.json",
    "control/inventory/source_packs/h11_account_entitlement_boundary_policy.json",
    "control/inventory/source_packs/h11_storefront_rights_safety_policy.json",
    "control/inventory/source_packs/h11_storefront_approval_gates.json",
    "control/inventory/source_packs/h11_storefront_output_policy.json",
    "control/inventory/source_packs/h11_storefront_truth_policy.json",
    "control/inventory/source_packs/h11_storefront_no_live_call_policy.json",
    "control/inventory/source_packs/h11_storefront_no_purchase_download_account_policy.json",
)
SOURCE_PACK_EXAMPLES = (
    "examples/packs/source/h11_storefront_source_pack_manifest_v0.json",
    "examples/packs/source/h11_storefront_policy_pack_v0.json",
)
EXTRA_EXAMPLES = (
    "examples/connectors/h11_storefront/coverage/h11_storefront_coverage_preview_v0.json",
    "examples/connectors/h11_storefront/scorecards/h11_storefront_scorecard_preview_v0.json",
)
DOCS = (
    "docs/reference/H11_STOREFRONT_SOURCE_PACKS.md",
    "docs/reference/H11_STOREFRONT_LISTING_IDENTITY_POLICY.md",
    "docs/reference/H11_APP_PRODUCT_IDENTITY_POLICY.md",
    "docs/reference/H11_VERSION_RELEASE_CHANNEL_POLICY.md",
    "docs/reference/H11_PRICE_AVAILABILITY_REGION_POLICY.md",
    "docs/reference/H11_ACQUISITION_PATH_CANDIDATE_POLICY.md",
    "docs/reference/H11_REVIEW_RATING_METADATA_POLICY.md",
    "docs/reference/H11_ACCOUNT_ENTITLEMENT_BOUNDARY_POLICY.md",
    "docs/reference/H11_STOREFRONT_RIGHTS_SAFETY_POLICY.md",
    "docs/architecture/H11_STOREFRONT_MODEL.md",
    "docs/architecture/STOREFRONT_SOURCE_FAMILY_MODEL.md",
    "docs/operations/H11_STOREFRONT_POLICY_GATES.md",
    "docs/operations/H11_STOREFRONT_NO_LIVE_CALL_POLICY.md",
    "docs/operations/H11_STOREFRONT_NO_PURCHASE_DOWNLOAD_ACCOUNT_POLICY.md",
    "docs/operations/H11_STOREFRONT_FIXTURE_PLAN.md",
)
AUDIT_FILES = tuple(
    f"control/audits/h11-bundle-01-storefront-policy-packs-v0/{name}"
    for name in (
        "README.md",
        "h11_bundle_01_report.json",
        "h11_source_pack_summary.md",
        "h11_source_policy_gate_summary.md",
        "h11_connector_family_summary.md",
        "h11_storefront_listing_identity_policy_summary.md",
        "h11_app_product_identity_policy_summary.md",
        "h11_version_release_channel_policy_summary.md",
        "h11_price_availability_region_policy_summary.md",
        "h11_acquisition_path_candidate_policy_summary.md",
        "h11_review_rating_metadata_policy_summary.md",
        "h11_account_entitlement_boundary_policy_summary.md",
        "h11_storefront_rights_safety_policy_summary.md",
        "h11_fixture_plan.md",
        "h11_no_live_call_report.md",
        "h11_no_purchase_download_account_report.md",
        "h11_readiness_for_fixture_runtime.md",
        "validation.md",
        "generated/sample_h11_source_summary.json",
        "generated/sample_h11_source_summary.md",
        "generated/sample_h11_option_matrix.json",
    )
)
H11_PYTHON_FILES = (
    "scripts/validate_h11_storefront_policy_packs.py",
    "scripts/summarize_h11_storefront_sources.py",
)
ALLOWED_CURRENT_OPERATIONS = {"inspect_fixture", "normalize_fixture_future", "record_source_policy", "record_source_metadata_preview", "record_identity_policy", "record_availability_policy", "record_acquisition_boundary_policy", "record_rights_safety_policy", "create_coverage_preview", "create_scorecard_preview"}
FALSE_REQUIRED_KEYS = {
    "live_access_enabled",
    "source_sync_enabled",
    "connector_runtime_enabled",
    "approved_live_probe_enabled",
    "api_query_enabled",
    "catalog_fetch_enabled",
    "storefront_search_enabled",
    "product_page_fetch_enabled",
    "screenshot_fetch_enabled",
    "media_fetch_enabled",
    "screenshots_media_fetch_enabled",
    "app_download_enabled",
    "game_download_enabled",
    "package_download_enabled",
    "installer_download_enabled",
    "downloads_enabled",
    "account_access_enabled",
    "purchase_automation_enabled",
    "checkout_automation_enabled",
    "cart_or_wishlist_automation_enabled",
    "entitlement_verification_enabled",
    "license_key_handling_enabled",
    "subscription_status_check_enabled",
    "install_execute_enabled",
    "launch_execute_enabled",
    "install_launch_enabled",
    "review_rating_write_enabled",
    "user_data_upload_enabled",
    "scraping_enabled",
    "crawling_enabled",
    "bypass_or_automation_enabled",
    "restricted_rights_sensitive_source_enabled",
    "restricted_source_access_enabled",
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
    "storefront_listing_metadata_is_listing_truth",
    "listing_identity_candidate_is_truth",
    "app_product_metadata_is_product_truth",
    "app_product_identity_candidate_is_truth",
    "version_release_metadata_is_version_truth",
    "version_release_candidate_is_truth",
    "price_availability_metadata_is_price_or_availability_truth",
    "price_availability_candidate_is_truth",
    "acquisition_path_candidate_is_action_permission",
    "review_rating_metadata_is_quality_truth",
    "review_rating_candidate_is_quality_truth",
    "account_entitlement_metadata_is_license_truth",
    "account_entitlement_candidate_is_license_truth",
    "storefront_rights_safety_metadata_is_rights_or_safety_truth",
    "rights_safety_candidate_is_rights_or_safety_truth",
    "storefront_metadata_grants_acquisition_permission",
    "accepted_listing_identity_truth",
    "accepted_app_product_truth",
    "accepted_version_release_truth",
    "accepted_price_availability_truth",
    "accepted_acquisition_permission",
    "accepted_review_rating_truth",
    "accepted_account_entitlement_truth",
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
    "current_price_claimed",
    "current_availability_claimed",
    "license_entitlement_claimed",
    "legal_acquisition_claimed",
    "installability_claimed",
    "malware_safety_claimed",
    "content_safety_claimed",
    "privacy_safety_claimed",
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
    r"(account_payload|receipt_payload|payment_payload|license_key_payload|entitlement_payload|app_package_payload|apk_payload|ipa_payload|msix_payload|appx_payload|dmg_payload|pkg_payload|exe_payload|msi_payload|installer_payload|download_payload|screenshot_payload|media_payload|install_log|launch_log|purchase_output|checkout_output|redemption_output|subscription_output|restricted_payload|scraping_output|crawling_output|browser_automation_output)",
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
        print("H11 storefront policy pack validation", file=stdout)
        print(f"status: {result['status']}", file=stdout)
        print(f"error_count: {len(result['errors'])}", file=stdout)
        for error in result["errors"][:25]:
            print(f"ERROR: {error}", file=stdout)
    return 0 if result["status"] == "valid" else 1


def validate_repo(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    required = list(INVENTORY_FILES) + list(SOURCE_PACK_EXAMPLES) + list(EXTRA_EXAMPLES) + list(DOCS) + list(AUDIT_FILES) + list(H11_PYTHON_FILES)
    required.extend(f"examples/sources/source_records/{SOURCE_FILES[source_id]}" for source_id in SOURCE_IDS + [BLOCKED_SOURCE_ID])
    required.extend(f"examples/connectors/h11_storefront/policies/{POLICY_FILES_BY_SOURCE[source_id]}" for source_id in SOURCE_IDS + [BLOCKED_SOURCE_ID])
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
                errors.append(f"invalid JSON in {rel}: {exc}")
                continue
            _scan_json_payload(rel, payload, errors)
    inventory_path = repo_root / "control/inventory/source_packs/h11_storefront_sources.json"
    if inventory_path.exists():
        inventory = _load_json(inventory_path)
        sources = inventory.get("sources", [])
        if inventory.get("source_count") != 16:
            errors.append("H11 source inventory source_count must be 16")
        ids = [item.get("source_id") for item in sources if isinstance(item, Mapping)]
        if sorted(ids) != sorted(SOURCE_IDS):
            errors.append("H11 source inventory must contain exactly the 16 in-scope source IDs")
        if len(ids) != len(set(ids)):
            errors.append("H11 source inventory contains duplicate source IDs")
        for source in sources:
            if isinstance(source, Mapping):
                errors.extend(validate_source_record(str(source.get("source_id", "")), source, known))
    for source_id in SOURCE_IDS + [BLOCKED_SOURCE_ID]:
        source_path = repo_root / "examples/sources/source_records" / SOURCE_FILES[source_id]
        if source_path.exists():
            errors.extend(validate_source_record(source_id, _load_json(source_path), known))
        pack_path = repo_root / "examples/connectors/h11_storefront/policies" / POLICY_FILES_BY_SOURCE[source_id]
        if pack_path.exists():
            errors.extend(validate_policy_pack(source_id, _load_json(pack_path)))
    coverage_path = repo_root / "examples/connectors/h11_storefront/coverage/h11_storefront_coverage_preview_v0.json"
    if coverage_path.exists():
        errors.extend(validate_coverage_preview(_load_json(coverage_path)))
    scorecard_path = repo_root / "examples/connectors/h11_storefront/scorecards/h11_storefront_scorecard_preview_v0.json"
    if scorecard_path.exists():
        errors.extend(validate_scorecard_preview(_load_json(scorecard_path)))
    for rel in H11_PYTHON_FILES:
        path = repo_root / rel
        if path.exists() and BANNED_IMPORT_RE.search(path.read_text(encoding="utf-8")):
            errors.append(f"{rel} imports a network/provider/browser library")
    forbidden_roots = [".aide.local", ".local/eureka", ".cache/eureka", "storefront_accounts", "receipts", "entitlements", "store_libraries", "app_downloads", "game_installs", "package_downloads", "checkout_sessions"]
    for rel in forbidden_roots:
        if (repo_root / rel).exists():
            errors.append(f"forbidden local private root exists: {rel}")
    return {"schema_version": "h11_storefront_policy_pack_validation.v0", "status": "valid" if not errors else "invalid", "errors": errors}


def validate_source_record(source_id: str, payload: Mapping[str, Any], known: Mapping[str, set[str]]) -> list[str]:
    errors: list[str] = []
    if payload.get("source_id") != source_id:
        errors.append(f"{source_id} source_id mismatch")
    if payload.get("source_family") != SOURCE_FAMILY:
        errors.append(f"{source_id} source_family must be {SOURCE_FAMILY}")
    if payload.get("connector_family") not in known["connector_families"]:
        errors.append(f"{source_id} unknown connector_family: {payload.get('connector_family')}")
    if payload.get("trust_lane") not in known["trust_lanes"]:
        errors.append(f"{source_id} unknown trust_lane: {payload.get('trust_lane')}")
    if payload.get("current_index_depth") not in known["index_depths"]:
        errors.append(f"{source_id} unknown current_index_depth: {payload.get('current_index_depth')}")
    if payload.get("current_access_mode") not in {"no_autonomous_access", "committed_fixture_only"}:
        errors.append(f"{source_id} current_access_mode must remain no_autonomous_access or committed_fixture_only")
    for key in FALSE_REQUIRED_KEYS - {"source_pack_import_enabled"}:
        if payload.get(key) is not False:
            errors.append(f"{source_id} {key} must be false")
    for key in (
        "storefront_listing_identity_support",
        "app_product_identity_support",
        "version_release_channel_support",
        "price_availability_region_support",
        "acquisition_path_candidate_support",
        "review_rating_metadata_support",
        "account_entitlement_boundary_support",
        "rights_safety_support",
    ):
        value = payload.get(key)
        if not isinstance(value, Mapping):
            errors.append(f"{source_id} missing {key}")
        elif value.get("accepted_truth") is not False or value.get("candidate_only") is not True or value.get("review_required") is not True:
            errors.append(f"{source_id} {key} must remain candidate-only with review")
    nested_errors: list[str] = []
    _scan_json_payload(source_id, payload, nested_errors)
    errors.extend(nested_errors)
    return errors


def validate_policy_pack(source_id: str, payload: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("source_id") != source_id:
        errors.append(f"{source_id} policy pack source_id mismatch")
    if payload.get("source_family") != SOURCE_FAMILY:
        errors.append(f"{source_id} policy pack source_family mismatch")
    if payload.get("policy_pack_grants_live_access") is not False:
        errors.append(f"{source_id} policy pack must not grant live access")
    for key in FALSE_REQUIRED_KEYS - {"source_pack_import_enabled"}:
        if payload.get(key) not in (False, None):
            errors.append(f"{source_id} policy pack {key} must be false when present")
    allowed = set(payload.get("allowed_current_operations", []))
    if not allowed.issubset(ALLOWED_CURRENT_OPERATIONS):
        errors.append(f"{source_id} policy pack allows unexpected current operations: {sorted(allowed - ALLOWED_CURRENT_OPERATIONS)}")
    _scan_json_payload(f"{source_id} policy pack", payload, errors)
    return errors


def validate_coverage_preview(payload: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("coverage_manifest_is_exhaustive_global_coverage") is not False:
        errors.append("coverage preview must not claim exhaustive coverage")
    for key in ("live_access_enabled",):
        if payload.get(key) is not False:
            errors.append(f"coverage preview {key} must be false")
    for key in ("api_queries_performed", "storefront_searches_performed", "product_page_fetches_performed", "downloads_performed", "account_actions_performed", "purchase_actions_performed", "entitlement_checks_performed", "installs_or_launches_performed", "scraping_crawling_performed"):
        if payload.get(key) != 0:
            errors.append(f"coverage preview {key} must be 0")
    _scan_json_payload("coverage preview", payload, errors)
    return errors


def validate_scorecard_preview(payload: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("production_ready") is not False:
        errors.append("scorecard preview must not claim production readiness")
    if payload.get("auto_approves_future_connectors") is not False:
        errors.append("scorecard preview must not auto-approve future connectors")
    _scan_json_payload("scorecard preview", payload, errors)
    return errors


def _load_known_values(repo_root: Path, errors: list[str]) -> dict[str, set[str]]:
    connector_families = {SOURCE_FAMILY}
    trust_lanes = {"official", "community", "preservation", "restricted_manifest_only", "web_archive_trace", "package_registry", "research_library", "unknown"}
    index_depths = {"D0_source_known", "D1_catalog_indexed", "D1_catalog_indexed_preview_only", "D2_metadata_indexed"}
    try:
        mapping = _load_json(repo_root / "control/inventory/source_packs/h11_storefront_connector_families.json")
        connector_families.update(str(item.get("connector_family")) for item in mapping.get("connector_families", []) if isinstance(item, Mapping))
    except Exception as exc:  # noqa: BLE001
        errors.append(f"could not load H11 connector family mapping: {exc}")
    try:
        registry = _load_json(repo_root / "control/inventory/connectors/connector_family_registry.json")
        connector_families.update(str(item.get("family_id")) for item in registry.get("families", []) if isinstance(item, Mapping))
    except Exception:
        pass
    return {"connector_families": connector_families, "trust_lanes": trust_lanes, "index_depths": index_depths}


def _scan_json_payload(label: str, value: Any, errors: list[str]) -> None:
    if isinstance(value, Mapping):
        for key, item in value.items():
            key_text = str(key)
            lower = key_text.lower()
            if PAYLOAD_KEY_RE.search(key_text):
                errors.append(f"{label} contains forbidden storefront/account/download/action payload key: {key_text}")
            if lower in SECRET_KEY_NAMES and item not in (None, "", False):
                errors.append(f"{label} contains forbidden credential/token key: {key_text}")
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
