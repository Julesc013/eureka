#!/usr/bin/env python3
"""Validate H11 storefront live-probe framework without live calls."""

from __future__ import annotations

import argparse
import importlib
import json
from pathlib import Path
import re
import subprocess
import sys
from collections.abc import Mapping, Sequence
from typing import Any, TextIO

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from control.prototypes.legacy_runtime.connectors.h11_storefront.live_probe_common import (  # noqa: E402
    H11_SOURCE_IDS,
    detect_h11_storefront_live_probe_product_boundary_violations,
    detect_h11_storefront_live_probe_truth_boundary_violations,
    load_h11_storefront_live_probe_policy_bundle,
    validate_h11_source_approval,
)

EXPECTED_SOURCES = tuple(['microsoft_store_metadata', 'mac_app_store_metadata', 'apple_app_store_metadata', 'google_play_metadata', 'fdroid_metadata', 'steam_store_metadata', 'gog_store_metadata', 'itchio_storefront_metadata', 'epic_games_store_policy_limited', 'humble_store_policy_limited', 'chrome_web_store_metadata', 'mozilla_addons_metadata', 'flathub_metadata', 'snapcraft_metadata', 'generic_vendor_product_page', 'generic_commercial_software_marketplace'])
REQUIRED_REQUEST_EXAMPLES = tuple(['fdroid_metadata', 'flathub_metadata', 'snapcraft_metadata', 'steam_store_metadata', 'gog_store_metadata', 'itchio_storefront_metadata', 'mozilla_addons_metadata', 'chrome_web_store_metadata', 'generic_vendor_product_page'])
CONTRACTS = tuple("control/schemas/previews/h11/connectors/" + name for name in ['storefront_live_probe_request.v0.json', 'storefront_live_probe_result.v0.json', 'storefront_live_probe_output_bundle.v0.json', 'storefront_connector_health_summary.v0.json'])
POLICIES = tuple("control/inventory/connectors/" + name for name in ['h11_storefront_live_probe_policy.json', 'h11_storefront_live_probe_allowed_requests.json', 'h11_storefront_live_probe_endpoint_policy.json', 'h11_storefront_live_probe_rate_limit_policy.json', 'h11_storefront_live_probe_cache_policy.json', 'h11_storefront_live_probe_kill_switch_policy.json', 'h11_storefront_live_probe_output_policy.json', 'h11_storefront_live_probe_path_policy.json', 'h11_storefront_live_probe_review_policy.json', 'h11_storefront_live_probe_truth_policy.json', 'h11_storefront_live_probe_no_purchase_download_account_policy.json', 'h11_storefront_live_probe_restricted_source_policy.json'])
DOCS = tuple(['docs/reference/H11_STOREFRONT_LIVE_PROBE.md', 'docs/reference/H11_STOREFRONT_LIVE_PROBE_RESULT.md', 'docs/reference/H11_STOREFRONT_CONNECTOR_HEALTH_SUMMARY.md', 'docs/architecture/H11_STOREFRONT_LIVE_PROBE_MODEL.md', 'docs/operations/H11_STOREFRONT_LIVE_PROBE_APPROVAL_GATES.md', 'docs/operations/H11_STOREFRONT_LIVE_PROBE_REVIEW.md', 'docs/operations/H11_STOREFRONT_LIVE_PROBE_BLOCKED_MODE.md', 'docs/operations/H11_STOREFRONT_LIVE_PROBE_NO_PURCHASE_DOWNLOAD_ACCOUNT_POLICY.md', 'docs/operations/H11_STOREFRONT_LIVE_PROBE_RESTRICTED_SOURCE_POLICY.md'])
AUDIT_DIR = Path("control/audits/h11-bundle-03-storefront-live-probes-v0")
AUDIT_FILES = tuple(['README.md', 'h11_bundle_03_report.json', 'live_probe_policy_review.md', 'live_probe_execution_report.md', 'storefront_listing_identity_candidate_preview.md', 'app_product_identity_candidate_preview.md', 'version_release_channel_candidate_preview.md', 'price_availability_region_candidate_preview.md', 'acquisition_path_candidate_preview.md', 'review_rating_metadata_candidate_preview.md', 'account_entitlement_boundary_candidate_preview.md', 'storefront_rights_safety_candidate_preview.md', 'source_cache_candidate_preview.md', 'evidence_candidate_preview.md', 'review_queue_seed_preview.md', 'connector_health_summary.md', 'no_purchase_download_account_report.md', 'restricted_source_policy_report.md', 'h11_live_probe_blocked_or_completed_summary.md', 'validation.md', 'generated/sample_h11_live_probe_result.json', 'generated/sample_h11_storefront_listing_identity_candidate_from_probe.json', 'generated/sample_h11_app_product_identity_candidate_from_probe.json', 'generated/sample_h11_version_release_channel_candidate_from_probe.json', 'generated/sample_h11_price_availability_region_candidate_from_probe.json', 'generated/sample_h11_acquisition_path_candidate_from_probe.json', 'generated/sample_h11_review_rating_metadata_candidate_from_probe.json', 'generated/sample_h11_account_entitlement_boundary_candidate_from_probe.json', 'generated/sample_h11_storefront_rights_safety_candidate_from_probe.json', 'generated/sample_h11_source_cache_candidate_from_probe.json', 'generated/sample_h11_evidence_candidate_preview_from_probe.json', 'generated/sample_h11_review_queue_seed_from_probe.json', 'generated/sample_h11_connector_health_summary.json', 'generated/sample_h11_live_probe_summary.md'])
PYTHON_FILES = tuple(
    ["control/prototypes/legacy_runtime/connectors/h11_storefront/live_probe_common.py"]
    + [f"control/prototypes/legacy_runtime/connectors/h11_storefront/live_probe_{source_id}.py" for source_id in EXPECTED_SOURCES]
    + [
        "scripts/run_h11_storefront_live_probe.py",
        "scripts/validate_h11_storefront_live_probe.py",
        "scripts/summarize_h11_storefront_live_probe_outputs.py",
    ]
)
BANNED_IMPORT_RE = re.compile(
    r"^\s*(?:from|import)\s+"
    r"(requests|httpx|aiohttp|socket|ftplib|smtplib|webbrowser|selenium|playwright|openai|anthropic)\b",
    re.MULTILINE,
)
CLIENT_CALL_RE = re.compile(r"(?<![\"'])\b(requests|httpx|aiohttp|openai|anthropic)\.")
SECRET_KEY_RE = re.compile(r'"[^"]*(api[_-]?key|api[_-]?token|access[_-]?token|auth[_-]?token|client_secret|password|private_key|cookie)[^"]*"\s*:', re.IGNORECASE)
PAYLOAD_BODY_RE = re.compile(r'"[^"]*(account_payload|credential_or_token_payload|receipt_payload|payment_payload|license_key_payload|entitlement_payload|app_payload|game_payload|package_payload|installer_payload|download_payload|install_log|launch_log|purchase_output|checkout_output|cart_wishlist_output|review_rating_write_output|scraping_output|crawling_output|browser_automation_output|restricted_source_access_output)[^"]*"\s*:', re.IGNORECASE)
FORBIDDEN_TRUE_KEYS = set(['accepted_candidate_truth', 'accepted_evidence_truth', 'accepted_public_record', 'accepted_source_truth', 'account_access_enabled', 'account_access_used', 'account_entitlement_boundary_candidate_is_license_truth', 'account_entitlement_candidate_is_license_truth', 'acquisition_path_candidate_is_action_permission', 'api_calls_made', 'api_query_enabled', 'app_download_enabled', 'app_product_identity_candidate_is_truth', 'browser_automation_enabled', 'bypass_or_automation_enabled', 'bypass_or_automation_used', 'cart_wishlist_automation_enabled', 'catalog_fetch_enabled', 'catalog_fetch_used', 'changed_public_search_behavior', 'checkout_automation_enabled', 'content_safety_claimed', 'crawling_enabled', 'crawling_used', 'credential_or_token_handling_enabled', 'current_availability_claimed', 'current_price_claimed', 'download_used', 'enabled_accounts', 'enabled_crawling', 'enabled_downloads', 'enabled_entitlement_checks', 'enabled_hosting', 'enabled_install_launch', 'enabled_purchase_actions', 'enabled_source_sync', 'enabled_telemetry', 'enabled_uploads', 'entitlement_check_used', 'evidence_candidate_preview_is_accepted_evidence', 'game_download_enabled', 'install_execute_enabled', 'install_launch_used', 'installability_claimed', 'installer_download_enabled', 'launch_execute_enabled', 'legal_acquisition_claimed', 'license_entitlement_claimed', 'listing_identity_candidate_is_truth', 'live_probe_default_enabled', 'live_probe_result_is_public_truth', 'malware_safety_claimed', 'master_index_mutated', 'media_fetch_enabled', 'mutated_master_index', 'mutated_public_index', 'network_calls_made', 'package_download_enabled', 'price_availability_candidate_is_truth', 'price_availability_region_candidate_is_truth', 'privacy_safety_claimed', 'product_page_fetch_enabled', 'product_page_fetch_used', 'production_readiness_claimed', 'public_index_mutated', 'public_query_fanout_enabled', 'purchase_action_used', 'purchase_automation_enabled', 'receipt_license_entitlement_handling_enabled', 'redemption_subscription_enabled', 'restricted_source_access_used', 'restricted_source_enabled', 'review_rating_candidate_is_quality_truth', 'review_rating_metadata_candidate_is_quality_truth', 'review_rating_write_enabled', 'review_rating_write_used', 'review_seed_is_review_decision', 'rights_clearance_claimed', 'rights_safety_candidate_is_rights_or_safety_truth', 'scraping_enabled', 'scraping_used', 'screenshot_fetch_enabled', 'screenshot_media_fetch_used', 'source_cache_candidate_is_accepted_source', 'source_sync_enabled', 'storefront_listing_identity_candidate_is_truth', 'storefront_metadata_grants_acquisition_permission', 'storefront_rights_safety_candidate_is_rights_or_safety_truth', 'storefront_search_enabled', 'storefront_search_used', 'user_data_upload_enabled', 'verified_authenticity_claimed', 'version_release_candidate_is_truth', 'version_release_channel_candidate_is_truth'])


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    result = validate_repo(REPO_ROOT)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    else:
        print("H11 storefront live probe validation", file=stdout)
        print(f"status: {result['status']}", file=stdout)
        print(f"errors: {len(result['errors'])}", file=stdout)
        for error in result["errors"]:
            print(f"- {error}", file=stdout)
    return 0 if result["status"] == "valid" else 1


def validate_repo(root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    payloads: dict[str, dict[str, Any]] = {}
    for rel in CONTRACTS + POLICIES:
        payload = load_json_object(root / rel, errors)
        if payload is not None:
            payloads[rel] = payload
    for rel in DOCS + PYTHON_FILES:
        if not (root / rel).is_file():
            errors.append(f"missing required file: {rel}")
    for name in AUDIT_FILES:
        if not (root / AUDIT_DIR / name).is_file():
            errors.append(f"missing audit file: {(AUDIT_DIR / name).as_posix()}")
    validate_policies(payloads, errors)
    validate_examples(root, errors)
    validate_runtime_imports(errors)
    validate_python_safety(root, errors)
    validate_cli_offline(root, errors)
    validate_generated_outputs(root, errors)
    validate_no_private_roots(root, errors)
    if tuple(H11_SOURCE_IDS) != EXPECTED_SOURCES:
        errors.append("runtime H11 source IDs do not match expected live-probe sources")
    return {
        "schema_version": "h11_storefront_live_probe_validation.v0",
        "status": "valid" if not errors else "invalid",
        "task": "H11-BUNDLE-03",
        "offline_default": True,
        "network_calls_made": False,
        "query_fetch_download_upload_execute_acquire_used": False,
        "restricted_source_access_used": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
        "errors": errors,
    }


def validate_policies(payloads: Mapping[str, Mapping[str, Any]], errors: list[str]) -> None:
    live = payloads.get(POLICIES[0], {})
    for key in (
        "live_probe_default_enabled",
        "source_sync_enabled",
        "public_query_fanout_enabled",
        "api_query_enabled",
        "catalog_fetch_enabled",
        "storefront_search_enabled",
        "product_page_fetch_enabled",
        "screenshot_fetch_enabled",
        "media_fetch_enabled",
        "app_download_enabled",
        "game_download_enabled",
        "package_download_enabled",
        "installer_download_enabled",
        "account_access_enabled",
        "credential_or_token_handling_enabled",
        "receipt_license_entitlement_handling_enabled",
        "purchase_automation_enabled",
        "checkout_automation_enabled",
        "cart_wishlist_automation_enabled",
        "redemption_subscription_enabled",
        "install_execute_enabled",
        "launch_execute_enabled",
        "review_rating_write_enabled",
        "user_data_upload_enabled",
        "scraping_enabled",
        "crawling_enabled",
        "browser_automation_enabled",
        "restricted_source_enabled",
        "bypass_or_automation_enabled",
    ):
        if live.get(key) is not False:
            errors.append(f"global policy {key} must be false")
    allowed = payloads.get(POLICIES[1], {})
    sources = allowed.get("sources", [])
    if sorted(item.get("source_id") for item in sources if isinstance(item, Mapping)) != sorted(EXPECTED_SOURCES):
        errors.append("allowed requests policy must list all H11 sources")
    bundle = load_h11_storefront_live_probe_policy_bundle(REPO_ROOT)
    for item in sources:
        if not isinstance(item, Mapping):
            errors.append("allowed request source entry must be object")
            continue
        source_id = str(item.get("source_id"))
        if item.get("approval_status") != "not_approved_for_live_access":
            errors.append(f"{source_id}: approval_status must remain not_approved_for_live_access")
        if item.get("allowed_request_keys") not in ([], None):
            errors.append(f"{source_id}: allowed_request_keys must stay empty without approval")
        for key in ("live_access_approved", "metadata_probe_approved"):
            if item.get(key) is not False:
                errors.append(f"{source_id}: {key} must be false")
        for key in (
            "source_sync_approved",
            "api_query_approved",
            "catalog_fetch_approved",
            "storefront_search_approved",
            "product_page_fetch_approved",
            "screenshot_fetch_approved",
            "media_fetch_approved",
            "app_download_approved",
            "game_download_approved",
            "package_download_approved",
            "installer_download_approved",
            "account_access_approved",
            "credential_or_token_handling_approved",
            "receipt_license_entitlement_handling_approved",
            "purchase_automation_approved",
            "checkout_automation_approved",
            "cart_wishlist_automation_approved",
            "redemption_subscription_approved",
            "install_execute_approved",
            "launch_execute_approved",
            "review_rating_write_approved",
            "user_data_upload_approved",
            "scraping_approved",
            "crawling_approved",
            "browser_automation_approved",
            "restricted_rights_sensitive_source_approved",
            "grey_market_or_piracy_adjacent_source_approved",
            "drm_or_access_control_bypass_approved",
            "public_query_fanout_approved",
        ):
            if item.get(key) is not False:
                errors.append(f"{source_id}: {key} must be false")
        request_key = str((item.get("planned_request_keys") or [""])[0])
        if validate_h11_source_approval(source_id, request_key, bundle)["approved"]:
            errors.append(f"{source_id}: live approval unexpectedly passes")
    output = payloads.get(POLICIES[6], {})
    for key in [
        "source_cache_write_current",
        "evidence_ledger_write_current",
        "review_queue_write_current",
        "live_sync_state",
        "api_query_sync_result",
        "catalog_fetch_result",
        "storefront_search_result",
        "product_page_payload",
        "screenshot_payload",
        "media_payload",
        "app_payload",
        "game_payload",
        "package_payload",
        "installer_payload",
        "account_payload",
        "credential_or_token_payload",
        "receipt_payload",
        "license_key_payload",
        "entitlement_payload",
        "payment_payload",
        "user_library_payload",
        "purchase_checkout_output",
        "cart_wishlist_output",
        "redemption_subscription_output",
        "install_execute_output",
        "launch_execute_output",
        "review_rating_write_output",
        "scraping_output",
        "crawling_output",
        "restricted_source_access_output",
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
        "public_index_mutation",
        "master_index_mutation",
        "rights_clearance",
        "current_price_truth",
        "current_availability_truth",
        "license_entitlement_truth",
        "legal_acquisition_truth",
        "installability_truth",
        "malware_safety",
        "content_safety_truth",
        "privacy_safety",
        "verified_authenticity",
        "production_readiness_claim",
    ]:
        if key not in output.get("forbidden_outputs", []):
            errors.append(f"output policy must forbid {key}")


def validate_examples(root: Path, errors: list[str]) -> None:
    request_dir = root / "examples/connectors/h11_storefront/live_probe"
    result_dir = root / "examples/connectors/h11_storefront/live_probe_results"
    for source_id in REQUIRED_REQUEST_EXAMPLES:
        path = request_dir / f"approved_{source_id}_probe_request_v0.json"
        if not path.is_file():
            errors.append(f"missing request example: {path.relative_to(root).as_posix()}")
        else:
            _scan_json_boundaries(load_json_object(path, errors) or {}, path, errors)
    if not (request_dir / "blocked_live_probe_request_v0.json").is_file():
        errors.append("missing blocked live-probe request example")
    for source_id in EXPECTED_SOURCES:
        path = result_dir / f"{source_id}_live_probe_result_example_v0.json"
        if not path.is_file():
            errors.append(f"missing live probe result example for {source_id}")
            continue
        payload = load_json_object(path, errors) or {}
        _scan_json_boundaries(payload, path, errors)
        if payload.get("network_used") is not False:
            errors.append(f"{path} must not use network")
        if payload.get("result_status") != "blocked_by_missing_approval":
            errors.append(f"{path} must be blocked by missing approval")
        if detect_h11_storefront_live_probe_truth_boundary_violations(payload, {}):
            errors.append(f"{path} has truth boundary violations")
        if detect_h11_storefront_live_probe_product_boundary_violations(payload, {}):
            errors.append(f"{path} has product boundary violations")
    for rel in [
        "source_cache_candidate_from_h11_probe_v0.json",
        "evidence_candidate_preview_from_h11_probe_v0.json",
        "review_queue_seed_from_h11_probe_v0.json",
        "connector_health_from_h11_probe_v0.json",
        "storefront_listing_identity_candidate_from_h11_probe_v0.json",
        "app_product_identity_candidate_from_h11_probe_v0.json",
        "version_release_channel_candidate_from_h11_probe_v0.json",
        "price_availability_region_candidate_from_h11_probe_v0.json",
        "acquisition_path_candidate_from_h11_probe_v0.json",
        "review_rating_metadata_candidate_from_h11_probe_v0.json",
        "account_entitlement_boundary_candidate_from_h11_probe_v0.json",
        "storefront_rights_safety_candidate_from_h11_probe_v0.json",
    ]:
        path = root / "examples/connectors/h11_storefront/live_probe_outputs" / rel
        if not path.is_file():
            errors.append(f"missing live probe output example: {rel}")
        else:
            _scan_json_boundaries(load_json_object(path, errors) or {}, path, errors)


def validate_runtime_imports(errors: list[str]) -> None:
    try:
        importlib.import_module("control.prototypes.legacy_runtime.connectors.h11_storefront.live_probe_common")
        for source_id in EXPECTED_SOURCES:
            module = importlib.import_module(f"control.prototypes.legacy_runtime.connectors.h11_storefront.live_probe_{source_id}")
            for name in ("build_request_url_or_metadata_request", "parse_response_payload", "normalize_response_payload"):
                if not hasattr(module, name):
                    errors.append(f"missing {name} in live_probe_{source_id}")
    except Exception as exc:  # noqa: BLE001
        errors.append(f"runtime import failed: {exc}")


def validate_python_safety(root: Path, errors: list[str]) -> None:
    for rel in PYTHON_FILES:
        path = root / rel
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        if BANNED_IMPORT_RE.search(text):
            errors.append(f"forbidden network/provider/browser import: {rel}")
        if CLIENT_CALL_RE.search(text):
            errors.append(f"forbidden client call in default live-probe framework: {rel}")
        if re.search(r"\b(playwright|selenium|browser_automation)\s*\(", text):
            errors.append(f"browser automation call pattern found: {rel}")


def validate_cli_offline(root: Path, errors: list[str]) -> None:
    _run_check([sys.executable, "scripts/run_h11_storefront_live_probe.py", "--source-id", "fdroid_metadata", "--request-key", "example_app_metadata", "--check"], root, errors)
    _run_check([sys.executable, "scripts/summarize_h11_storefront_live_probe_outputs.py", "--input", "examples/connectors/h11_storefront/live_probe_results", "--check"], root, errors)
    forbidden_checks = [
        [sys.executable, "scripts/run_h11_storefront_live_probe.py", "--source-id", "fdroid_metadata", "--request-key", "example_app_metadata", "--output", "site/dist/h11.json"],
        [sys.executable, "scripts/run_h11_storefront_live_probe.py", "--source-id", "fdroid_metadata", "--request-key", "example_app_metadata", "--output", "data/public_index/h11.json"],
        [sys.executable, "scripts/run_h11_storefront_live_probe.py", "--source-id", "fdroid_metadata", "--request-key", "example_app_metadata", "--output", "accounts/h11.json"],
        [sys.executable, "scripts/run_h11_storefront_live_probe.py", "--source-id", "fdroid_metadata", "--request-key", "example_app_metadata", "--output", "app_downloads/h11.json"],
    ]
    for cmd in forbidden_checks:
        proc = subprocess.run(cmd, cwd=root, text=True, capture_output=True, check=False)
        if proc.returncode == 0:
            errors.append(f"forbidden output root was not rejected: {cmd[-1]}")


def validate_generated_outputs(root: Path, errors: list[str]) -> None:
    for rel in [
        "control/audits/h11-bundle-03-storefront-live-probes-v0/generated/sample_h11_live_probe_result.json",
        "control/audits/h11-bundle-03-storefront-live-probes-v0/generated/sample_h11_connector_health_summary.json",
    ]:
        payload = load_json_object(root / rel, errors)
        if payload is not None:
            _scan_json_boundaries(payload, root / rel, errors)


def validate_no_private_roots(root: Path, errors: list[str]) -> None:
    for rel in (".aide.local", ".local/eureka", ".cache/eureka", "storefront_accounts", "accounts", "receipts", "entitlements", "store_libraries", "app_downloads", "package_downloads", "checkout_sessions", "install_actions", "launch_actions", "restricted_sources"):
        if (root / rel).exists():
            errors.append(f"forbidden local private root exists: {rel}")


def _scan_json_boundaries(value: Any, label: Path, errors: list[str]) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            key_text = str(key)
            if key_text in FORBIDDEN_TRUE_KEYS and item is True:
                errors.append(f"{label} forbidden true value: {key_text}")
            if SECRET_KEY_RE.search(json.dumps(key_text)) and item not in (False, None, "", "blocked_fixture_boundary"):
                errors.append(f"{label} forbidden secret-like key value: {key_text}")
            if PAYLOAD_BODY_RE.search(json.dumps(key_text)) and item not in (False, None, "", [], {}):
                errors.append(f"{label} forbidden payload key: {key_text}")
            _scan_json_boundaries(item, label, errors)
    elif isinstance(value, list):
        for item in value:
            _scan_json_boundaries(item, label, errors)


def _run_check(cmd: list[str], root: Path, errors: list[str]) -> None:
    proc = subprocess.run(cmd, cwd=root, text=True, capture_output=True, check=False)
    if proc.returncode != 0:
        errors.append(f"command failed: {' '.join(cmd)} :: {proc.stdout} {proc.stderr}")


def load_json_object(path: Path, errors: list[str]) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        errors.append(f"invalid JSON {path}: {exc}")
        return None
    if not isinstance(payload, dict):
        errors.append(f"JSON object expected: {path}")
        return None
    return payload


if __name__ == "__main__":
    raise SystemExit(main())
