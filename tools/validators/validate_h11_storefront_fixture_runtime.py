#!/usr/bin/env python3
"""Validate H11 storefront fixture runtime artifacts offline."""

from __future__ import annotations

import importlib
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from archive.prototypes.legacy_runtime.connectors.h11_storefront.fixture_loader import load_h11_storefront_fixture  # noqa: E402
from archive.prototypes.legacy_runtime.connectors.h11_storefront.normalizer_common import H11_FIXTURE_KINDS, H11_SOURCE_IDS, detect_h11_product_boundary_violations, detect_h11_truth_boundary_violations  # noqa: E402

CONTRACTS = ['contracts/schema/control/fixtures/h11/connectors/storefront_fixture.v0.json', 'contracts/schema/control/previews/h11/connectors/storefront_normalized_record.v0.json', 'contracts/schema/control/previews/h11/connectors/storefront_listing_identity_candidate.v0.json', 'contracts/schema/control/previews/h11/connectors/app_product_identity_candidate.v0.json', 'contracts/schema/control/previews/h11/connectors/version_release_channel_candidate.v0.json', 'contracts/schema/control/previews/h11/connectors/price_availability_region_candidate.v0.json', 'contracts/schema/control/previews/h11/connectors/acquisition_path_candidate.v0.json', 'contracts/schema/control/previews/h11/connectors/review_rating_metadata_candidate.v0.json', 'contracts/schema/control/previews/h11/connectors/account_entitlement_boundary_candidate.v0.json', 'contracts/schema/control/previews/h11/connectors/storefront_rights_safety_candidate.v0.json', 'contracts/schema/control/fixtures/h11/connectors/storefront_fixture_replay_result.v0.json']
POLICIES = ['control/inventory/connectors/h11_storefront_fixture_runtime_policy.json', 'control/inventory/connectors/h11_storefront_normalization_policy.json', 'control/inventory/connectors/h11_storefront_listing_identity_mapping_policy.json', 'control/inventory/connectors/h11_app_product_identity_mapping_policy.json', 'control/inventory/connectors/h11_version_release_channel_mapping_policy.json', 'control/inventory/connectors/h11_price_availability_region_mapping_policy.json', 'control/inventory/connectors/h11_acquisition_path_candidate_mapping_policy.json', 'control/inventory/connectors/h11_review_rating_metadata_mapping_policy.json', 'control/inventory/connectors/h11_account_entitlement_boundary_mapping_policy.json', 'control/inventory/connectors/h11_storefront_rights_safety_mapping_policy.json', 'control/inventory/connectors/h11_storefront_fixture_output_policy.json', 'control/inventory/connectors/h11_storefront_fixture_path_policy.json', 'control/inventory/connectors/h11_storefront_fixture_truth_policy.json', 'control/inventory/connectors/h11_storefront_source_cache_mapping_policy.json', 'control/inventory/connectors/h11_storefront_evidence_mapping_policy.json', 'control/inventory/connectors/h11_storefront_no_purchase_download_account_policy.json']
FIXTURE_FILES = {'minimal': 'minimal_record.json', 'listing_identity': 'listing_identity_record.json', 'app_product_identity': 'app_product_identity_record.json', 'version_release_channel': 'version_release_channel_record.json', 'price_availability_region': 'price_availability_region_record.json', 'acquisition_path_blocked': 'acquisition_path_blocked_record.json', 'review_rating_metadata': 'review_rating_metadata_record.json', 'account_entitlement_boundary': 'account_entitlement_boundary_record.json', 'rights_safety': 'rights_safety_record.json', 'policy_blocked': 'policy_blocked_record.json'}
EXAMPLES = ['examples/connectors/h11_storefront/identity/storefront_listing_identity_candidate_v0.json', 'examples/connectors/h11_storefront/identity/app_product_identity_candidate_v0.json', 'examples/connectors/h11_storefront/identity/version_release_channel_candidate_v0.json', 'examples/connectors/h11_storefront/identity/price_availability_region_candidate_v0.json', 'examples/connectors/h11_storefront/identity/acquisition_path_candidate_v0.json', 'examples/connectors/h11_storefront/identity/review_rating_metadata_candidate_v0.json', 'examples/connectors/h11_storefront/identity/account_entitlement_boundary_candidate_v0.json', 'examples/connectors/h11_storefront/identity/storefront_rights_safety_candidate_v0.json', 'examples/connectors/h11_storefront/identity/policy_blocked_identity_candidate_v0.json']
DOCS = ['docs/reference/H11_STOREFRONT_FIXTURE_RUNTIME.md', 'docs/reference/H11_STOREFRONT_NORMALIZED_RECORD.md', 'docs/reference/H11_STOREFRONT_LISTING_IDENTITY_CANDIDATE.md', 'docs/reference/H11_APP_PRODUCT_IDENTITY_CANDIDATE.md', 'docs/reference/H11_VERSION_RELEASE_CHANNEL_CANDIDATE.md', 'docs/reference/H11_PRICE_AVAILABILITY_REGION_CANDIDATE.md', 'docs/reference/H11_ACQUISITION_PATH_CANDIDATE.md', 'docs/reference/H11_REVIEW_RATING_METADATA_CANDIDATE.md', 'docs/reference/H11_ACCOUNT_ENTITLEMENT_BOUNDARY_CANDIDATE.md', 'docs/reference/H11_STOREFRONT_RIGHTS_SAFETY_CANDIDATE.md', 'docs/architecture/H11_STOREFRONT_NORMALIZER_MODEL.md', 'docs/architecture/H11_STOREFRONT_LISTING_IDENTITY_MODEL.md', 'docs/architecture/H11_APP_PRODUCT_IDENTITY_MODEL.md', 'docs/architecture/H11_VERSION_RELEASE_CHANNEL_MODEL.md', 'docs/architecture/H11_PRICE_AVAILABILITY_REGION_MODEL.md', 'docs/architecture/H11_ACQUISITION_PATH_MODEL.md', 'docs/architecture/H11_REVIEW_RATING_METADATA_MODEL.md', 'docs/architecture/H11_ACCOUNT_ENTITLEMENT_BOUNDARY_MODEL.md', 'docs/architecture/H11_STOREFRONT_RIGHTS_SAFETY_MODEL.md', 'docs/operations/H11_STOREFRONT_FIXTURE_REPLAY.md', 'docs/operations/H11_STOREFRONT_FIXTURE_NO_LIVE_CALL_POLICY.md', 'docs/operations/H11_STOREFRONT_FIXTURE_NO_PURCHASE_DOWNLOAD_ACCOUNT_POLICY.md']
SCRIPTS = ['scripts/normalize_h11_storefront_fixture.py', 'scripts/replay_h11_storefront_fixtures.py', 'scripts/summarize_h11_storefront_fixture_outputs.py']
RUNTIME_DIR = "archive/prototypes/legacy_runtime/connectors/h11_storefront"
BANNED_IMPORT_RE = re.compile(r"\b(requests|httpx|aiohttp|urllib|socket|ftplib|smtplib|webbrowser|selenium|playwright|openai|anthropic)\b")
FORBIDDEN_PAYLOAD_KEY_RE = re.compile(r"(account_data|credential_value|token_value|receipt_payload|payment_payload|license_key_payload|entitlement_payload|app_package_payload|installer_payload|download_payload|install_log|launch_log|purchase_output|checkout_output|scraping_output|crawling_output|browser_automation_output)", re.IGNORECASE)
SECRET_KEY_RE = re.compile(r"(^|_)(api_key|api_token|access_token|auth_token|client_secret|password|private_key|cookie)($|_)", re.IGNORECASE)
FORBIDDEN_TRUE_KEYS = {'entitlement_payload_included', 'redemption_subscription_action_performed', 'app_package_payload_included', 'catalog_payload_included', 'credential_or_token_payload_included', 'product_page_payload_included', 'screenshot_payload_included', 'network_used', 'user_library_payload_included', 'scraping_output_included', 'payment_payload_included', 'game_package_payload_included', 'live_call_used', 'cart_wishlist_action_performed', 'install_execute_performed', 'restricted_source_accessed', 'media_payload_included', 'installer_payload_included', 'checkout_action_performed', 'review_rating_write_performed', 'account_payload_included', 'license_key_payload_included', 'bypass_or_automation_used', 'purchase_action_performed', 'external_api_used', 'crawling_output_included', 'receipt_payload_included', 'storefront_search_payload_included', 'launch_execute_performed'}
CLAIM_KEYS = {'privacy_safety_claimed', 'accepted_evidence_truth', 'version_release_channel_candidate_is_truth', 'app_product_identity_candidate_is_truth', 'accepted_price_availability_truth', 'review_rating_metadata_candidate_is_quality_truth', 'acquisition_path_candidate_is_action_permission', 'storefront_metadata_grants_acquisition_permission', 'source_cache_preview_is_accepted_source', 'price_availability_region_candidate_is_truth', 'availability_metadata_is_current_availability_truth', 'production_readiness_claimed', 'accepted_app_product_truth', 'accepted_source_truth', 'purchase_permission_granted', 'accepted_account_entitlement_truth', 'public_index_mutated', 'storefront_rights_safety_candidate_is_rights_or_safety_truth', 'account_entitlement_boundary_candidate_is_license_truth', 'current_price_claimed', 'accepted_public_record', 'accepted_acquisition_permission', 'malware_safety_claimed', 'verified_authenticity_claimed', 'evidence_preview_is_accepted_evidence', 'accepted_candidate_truth', 'storefront_listing_identity_candidate_is_truth', 'master_index_mutated', 'accepted_rights_safety_truth', 'accepted_listing_identity_truth', 'install_launch_permission_granted', 'account_access_permission_granted', 'accepted_review_rating_truth', 'download_permission_granted', 'rights_clearance_claimed', 'license_entitlement_claimed', 'accepted_version_release_truth', 'current_availability_claimed', 'installability_claimed', 'price_metadata_is_current_price_truth', 'legal_acquisition_claimed', 'normalized_record_is_public_truth', 'content_safety_claimed'}


def validate_repo(root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    for rel in CONTRACTS + POLICIES + EXAMPLES + DOCS + SCRIPTS:
        path = root / rel
        if not path.exists():
            errors.append(f"missing required artifact: {rel}")
        elif path.suffix == ".json":
            _load_json(path, errors)
    for source_id in H11_SOURCE_IDS:
        source_dir = root / "examples/connectors/h11_storefront/fixtures" / source_id
        if not source_dir.is_dir():
            errors.append(f"missing fixture directory: {source_id}")
            continue
        module = importlib.import_module(f"archive.prototypes.legacy_runtime.connectors.h11_storefront.{source_id}")
        for kind, filename in FIXTURE_FILES.items():
            fixture_path = source_dir / filename
            if not fixture_path.exists():
                errors.append(f"missing fixture: {fixture_path.relative_to(root).as_posix()}")
                continue
            fixture = _load_json(fixture_path, errors)
            if isinstance(fixture, dict):
                if fixture.get("fixture_kind") != kind:
                    errors.append(f"fixture kind mismatch: {fixture_path}")
                _scan_json_boundaries(fixture, fixture_path, errors)
                try:
                    loaded = load_h11_storefront_fixture(fixture_path)
                    normalized = module.normalize(loaded)
                    errors.extend(detect_h11_truth_boundary_violations(normalized))
                    errors.extend(detect_h11_product_boundary_violations(normalized))
                except Exception as exc:  # noqa: BLE001
                    errors.append(f"normalizer failed for {source_id}/{filename}: {exc}")
        normalized_path = root / "examples/connectors/h11_storefront/normalized" / f"{source_id}_normalized_record_v0.json"
        replay_path = root / "examples/connectors/h11_storefront/replay_results" / f"{source_id}_replay_result_v0.json"
        if not normalized_path.exists():
            errors.append(f"missing normalized example for {source_id}")
        if not replay_path.exists():
            errors.append(f"missing replay example for {source_id}")
    _scan_runtime(root, errors)
    _run_check([sys.executable, "scripts/normalize_h11_storefront_fixture.py", "--source-id", "fdroid_metadata", "--input", "examples/connectors/h11_storefront/fixtures/fdroid_metadata/app_product_identity_record.json", "--check"], root, errors)
    _run_check([sys.executable, "scripts/replay_h11_storefront_fixtures.py", "--check"], root, errors)
    _run_check([sys.executable, "scripts/summarize_h11_storefront_fixture_outputs.py", "--input", "examples/connectors/h11_storefront", "--check"], root, errors)
    _check_forbidden_output_roots(root, errors)
    for rel in (".aide.local", ".local/eureka", ".cache/eureka", "storefront_accounts", "accounts", "receipts", "entitlements", "store_libraries", "app_downloads", "game_installs", "package_downloads", "checkout_sessions"):
        if (root / rel).exists():
            errors.append(f"forbidden local private root exists: {rel}")
    return {
        "schema_version": "h11_storefront_fixture_runtime_validation.v0",
        "status": "valid" if not errors else "invalid",
        "source_count": len(H11_SOURCE_IDS),
        "fixture_kind_count": len(H11_FIXTURE_KINDS),
        "network_calls_made": False,
        "download_account_purchase_install_launch_used": False,
        "restricted_source_access_used": False,
        "errors": errors,
        "warnings": warnings,
    }


def main() -> int:
    result = validate_repo()
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "valid" else 1


def _scan_runtime(root: Path, errors: list[str]) -> None:
    runtime_root = root / RUNTIME_DIR
    expected_modules = ['__init__.py', 'fixture_loader.py', 'normalizer_common.py', 'storefront_listing_identity.py', 'app_product_identity.py', 'version_release_channel.py', 'price_availability_region.py', 'acquisition_path_candidate.py', 'review_rating_metadata.py', 'account_entitlement_boundary.py', 'storefront_rights_safety.py', 'microsoft_store_metadata.py', 'mac_app_store_metadata.py', 'apple_app_store_metadata.py', 'google_play_metadata.py', 'fdroid_metadata.py', 'steam_store_metadata.py', 'gog_store_metadata.py', 'itchio_storefront_metadata.py', 'epic_games_store_policy_limited.py', 'humble_store_policy_limited.py', 'chrome_web_store_metadata.py', 'mozilla_addons_metadata.py', 'flathub_metadata.py', 'snapcraft_metadata.py', 'generic_vendor_product_page.py', 'generic_commercial_software_marketplace.py']
    for module in expected_modules:
        if not (runtime_root / module).exists():
            errors.append(f"missing runtime module: {module}")
    for path in runtime_root.glob("*.py"):
        text = path.read_text(encoding="utf-8")
        if BANNED_IMPORT_RE.search(text):
            errors.append(f"runtime module imports forbidden network/provider/browser library: {path}")
        if re.search(r"\b(fetch|download|upload|purchase|checkout|install|launch|scrape|crawl)\s*\(", text):
            errors.append(f"runtime module appears to define forbidden active behavior: {path}")


def _scan_json_boundaries(value: Any, label: Path, errors: list[str]) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            key_text = str(key)
            if key_text in FORBIDDEN_TRUE_KEYS and item is True:
                errors.append(f"{label} forbidden fixture true value: {key_text}")
            if key_text in CLAIM_KEYS and item is True:
                errors.append(f"{label} forbidden truth claim: {key_text}")
            if SECRET_KEY_RE.search(key_text) and item not in (False, None, "", "blocked_fixture_boundary"):
                errors.append(f"{label} forbidden secret-like key value: {key_text}")
            if FORBIDDEN_PAYLOAD_KEY_RE.search(key_text) and item not in (False, None, "", [], {}):
                errors.append(f"{label} forbidden payload key: {key_text}")
            _scan_json_boundaries(item, label, errors)
    elif isinstance(value, list):
        for item in value:
            _scan_json_boundaries(item, label, errors)


def _check_forbidden_output_roots(root: Path, errors: list[str]) -> None:
    checks = [
        [sys.executable, "scripts/normalize_h11_storefront_fixture.py", "--source-id", "fdroid_metadata", "--input", "examples/connectors/h11_storefront/fixtures/fdroid_metadata/minimal_record.json", "--output", "site/dist/h11.json"],
        [sys.executable, "scripts/normalize_h11_storefront_fixture.py", "--source-id", "fdroid_metadata", "--input", "examples/connectors/h11_storefront/fixtures/fdroid_metadata/minimal_record.json", "--output", "site/dist/data/public_index/h11.json"],
        [sys.executable, "scripts/normalize_h11_storefront_fixture.py", "--source-id", "fdroid_metadata", "--input", "examples/connectors/h11_storefront/fixtures/fdroid_metadata/minimal_record.json", "--output", "storefront_accounts/h11.json"],
        [sys.executable, "scripts/normalize_h11_storefront_fixture.py", "--source-id", "fdroid_metadata", "--input", "examples/connectors/h11_storefront/fixtures/fdroid_metadata/minimal_record.json", "--output", "app_downloads/h11.json"],
    ]
    for cmd in checks:
        proc = subprocess.run(cmd, cwd=root, text=True, capture_output=True, check=False)
        if proc.returncode == 0:
            errors.append(f"forbidden output root was not rejected: {cmd[-1]}")


def _run_check(cmd: list[str], root: Path, errors: list[str]) -> None:
    proc = subprocess.run(cmd, cwd=root, text=True, capture_output=True, check=False)
    if proc.returncode != 0:
        errors.append(f"command failed: {' '.join(cmd)} :: {proc.stdout} {proc.stderr}")


def _load_json(path: Path, errors: list[str]) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        errors.append(f"invalid JSON {path}: {exc}")
        return {}


if __name__ == "__main__":
    raise SystemExit(main())
