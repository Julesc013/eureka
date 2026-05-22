#!/usr/bin/env python3
"""Summarize H11 storefront/app-store source policy packs offline."""

from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import sys
import tempfile
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]
SOURCE_INVENTORY = REPO_ROOT / "control/inventory/source_packs/h11_storefront_sources.json"
CONNECTOR_FAMILIES = REPO_ROOT / "control/inventory/source_packs/h11_storefront_connector_families.json"
FORBIDDEN_OUTPUT_ROOTS = (
    "site/dist",
    "site/dist/data/public_index",
    "runtime",
    "contracts",
    "data/master_index",
    "master_index",
    ".aide.local",
    ".local/eureka",
    ".cache/eureka",
    "storefront_accounts",
    "receipts",
    "entitlements",
    "store_libraries",
    "app_downloads",
    "game_installs",
    "package_downloads",
    "checkout_sessions",
    "restricted_sources",
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", help="Optional JSON summary output path.")
    parser.add_argument("--summary-output", help="Optional Markdown summary output path.")
    parser.add_argument("--check", action="store_true", help="Summarize without writing files.")
    parser.add_argument("--json", action="store_true", help="Print JSON summary.")
    args = parser.parse_args(argv)
    try:
        summary = build_summary()
        if not args.check:
            if args.output:
                _write_json(args.output, summary)
                summary["wrote_files"] = True
            if args.summary_output:
                _write_text(args.summary_output, render_summary_markdown(summary))
                summary["wrote_files"] = True
        if args.json:
            print(json.dumps(summary, indent=2, sort_keys=True), file=stdout)
        else:
            print("H11 storefront source summary", file=stdout)
            print(f"status: {summary['status']}", file=stdout)
            print(f"source_count: {summary['source_count']}", file=stdout)
            print(f"live_access_enabled_count: {summary['live_access_enabled_count']}", file=stdout)
            print(f"storefront_product_fetch_enabled_count: {summary['storefront_product_fetch_enabled_count']}", file=stdout)
            print(f"downloads_enabled_count: {summary['downloads_enabled_count']}", file=stdout)
            print(f"account_access_enabled_count: {summary['account_access_enabled_count']}", file=stdout)
            print(f"purchase_automation_enabled_count: {summary['purchase_automation_enabled_count']}", file=stdout)
            print(f"entitlement_checks_enabled_count: {summary['entitlement_checks_enabled_count']}", file=stdout)
            print(f"install_launch_enabled_count: {summary['install_launch_enabled_count']}", file=stdout)
        return 0
    except Exception as exc:  # noqa: BLE001
        if args.json:
            print(json.dumps({"status": "invalid", "error": str(exc)}, indent=2, sort_keys=True), file=stdout)
        else:
            print("H11 storefront source summary", file=stdout)
            print("status: invalid", file=stdout)
            print(f"ERROR: {exc}", file=stdout)
        return 1


def build_summary() -> dict[str, Any]:
    inventory = _load_json(SOURCE_INVENTORY)
    connector_mapping = _load_json(CONNECTOR_FAMILIES)
    sources = inventory.get("sources", [])
    if not isinstance(sources, list):
        raise ValueError("H11 source inventory must contain a sources list")
    source_family_counts = Counter(str(item.get("source_family", "unknown")) for item in sources if isinstance(item, Mapping))
    connector_family_counts = Counter(str(item.get("connector_family", "unknown")) for item in sources if isinstance(item, Mapping))
    trust_lane_counts = Counter(str(item.get("trust_lane", "unknown")) for item in sources if isinstance(item, Mapping))
    access_mode_counts = Counter(str(item.get("current_access_mode", "unknown")) for item in sources if isinstance(item, Mapping))
    index_depth_counts = Counter(str(item.get("current_index_depth", "unknown")) for item in sources if isinstance(item, Mapping))

    def count_true(key: str) -> int:
        return sum(1 for item in sources if isinstance(item, Mapping) and item.get(key) is True)

    def support_count(key: str) -> int:
        return sum(
            1
            for item in sources
            if isinstance(item, Mapping)
            and isinstance(item.get(key), Mapping)
            and item[key].get("metadata_future") is True
            and item[key].get("accepted_truth") is False
        )

    download_keys = ("app_download_enabled", "game_download_enabled", "package_download_enabled", "installer_download_enabled", "downloads_enabled", "screenshot_fetch_enabled", "media_fetch_enabled", "screenshots_media_fetch_enabled")
    account_keys = ("account_access_enabled", "license_key_handling_enabled", "subscription_status_check_enabled")
    purchase_keys = ("purchase_automation_enabled", "checkout_automation_enabled", "cart_or_wishlist_automation_enabled")
    install_keys = ("install_execute_enabled", "launch_execute_enabled", "install_launch_enabled")
    return {
        "schema_version": "h11_storefront_source_summary.v0",
        "status": "pass",
        "wave_id": inventory.get("wave_id", "H11"),
        "current_status": inventory.get("current_status", "policy_pack_only"),
        "source_count": len(sources),
        "source_ids": sorted(str(item.get("source_id", "")) for item in sources if isinstance(item, Mapping)),
        "source_family_counts": dict(sorted(source_family_counts.items())),
        "connector_family_counts": dict(sorted(connector_family_counts.items())),
        "trust_lane_counts": dict(sorted(trust_lane_counts.items())),
        "access_mode_counts": dict(sorted(access_mode_counts.items())),
        "index_depth_counts": dict(sorted(index_depth_counts.items())),
        "fixture_required_count": count_true("fixture_required"),
        "future_live_probe_required_count": count_true("live_probe_required_future"),
        "scorecard_required_count": count_true("scorecard_required"),
        "coverage_required_count": count_true("coverage_required"),
        "storefront_listing_identity_support_count": support_count("storefront_listing_identity_support"),
        "app_product_identity_support_count": support_count("app_product_identity_support"),
        "version_release_channel_support_count": support_count("version_release_channel_support"),
        "price_availability_region_support_count": support_count("price_availability_region_support"),
        "acquisition_path_candidate_support_count": support_count("acquisition_path_candidate_support"),
        "review_rating_metadata_support_count": support_count("review_rating_metadata_support"),
        "account_entitlement_boundary_support_count": support_count("account_entitlement_boundary_support"),
        "rights_safety_support_count": support_count("rights_safety_support"),
        "connector_mapping_count": len(connector_mapping.get("source_connector_family_mappings", [])),
        "live_access_enabled_count": count_true("live_access_enabled"),
        "source_sync_enabled_count": count_true("source_sync_enabled"),
        "connector_runtime_enabled_count": count_true("connector_runtime_enabled"),
        "api_catalog_query_enabled_count": count_true("api_query_enabled") + count_true("catalog_fetch_enabled"),
        "storefront_product_fetch_enabled_count": count_true("storefront_search_enabled") + count_true("product_page_fetch_enabled"),
        "downloads_enabled_count": sum(1 for item in sources if isinstance(item, Mapping) and any(item.get(key) is True for key in download_keys)),
        "account_access_enabled_count": sum(1 for item in sources if isinstance(item, Mapping) and any(item.get(key) is True for key in account_keys)),
        "purchase_automation_enabled_count": sum(1 for item in sources if isinstance(item, Mapping) and any(item.get(key) is True for key in purchase_keys)),
        "entitlement_checks_enabled_count": count_true("entitlement_verification_enabled"),
        "install_launch_enabled_count": sum(1 for item in sources if isinstance(item, Mapping) and any(item.get(key) is True for key in install_keys)),
        "review_rating_write_enabled_count": count_true("review_rating_write_enabled"),
        "scraping_crawling_enabled_count": count_true("scraping_enabled") + count_true("crawling_enabled") + count_true("bypass_or_automation_enabled"),
        "restricted_source_enabled_count": count_true("restricted_rights_sensitive_source_enabled") + count_true("restricted_source_access_enabled"),
        "blockers": [
            "fixture runtime not implemented",
            "live access not approved",
            "API/catalog/storefront/product-page fetches forbidden",
            "app/game/package/installer/screenshot/media downloads forbidden",
            "account, credential, receipt, license, entitlement, payment, purchase, checkout, cart, wishlist, redemption, subscription, install, and launch behavior forbidden",
            "review/rating writes forbidden",
            "scraping, crawling, browser automation, and bypass forbidden",
            "listing, app/product, version, price, availability, acquisition, review, account, entitlement, rights, safety, source, evidence, candidate, public, and master truth acceptance forbidden",
        ],
        "readiness": "READY_FOR_H11_FIXTURE_RUNTIME",
        "wrote_files": False,
    }


def render_summary_markdown(summary: Mapping[str, Any]) -> str:
    lines = [
        "# H11 Storefront Source Summary",
        "",
        f"- status: `{summary['status']}`",
        f"- source_count: `{summary['source_count']}`",
        f"- live_access_enabled_count: `{summary['live_access_enabled_count']}`",
        f"- storefront_product_fetch_enabled_count: `{summary['storefront_product_fetch_enabled_count']}`",
        f"- downloads_enabled_count: `{summary['downloads_enabled_count']}`",
        f"- account_access_enabled_count: `{summary['account_access_enabled_count']}`",
        f"- purchase_automation_enabled_count: `{summary['purchase_automation_enabled_count']}`",
        f"- entitlement_checks_enabled_count: `{summary['entitlement_checks_enabled_count']}`",
        f"- install_launch_enabled_count: `{summary['install_launch_enabled_count']}`",
        f"- readiness: `{summary['readiness']}`",
        "",
        "H11-BUNDLE-01 is policy-pack-only and does not accept listing, app/product, version, price, availability, acquisition, review, account, entitlement, rights, safety, source, evidence, candidate, public, or master truth.",
    ]
    return "\n".join(lines) + "\n"


def safe_output_path(raw: str) -> Path:
    path = Path(raw)
    resolved = path if path.is_absolute() else REPO_ROOT / path
    resolved = resolved.resolve()
    repo = REPO_ROOT.resolve()
    try:
        rel = resolved.relative_to(repo).as_posix()
    except ValueError:
        temp_root = Path(tempfile.gettempdir()).resolve()
        try:
            resolved.relative_to(temp_root)
        except ValueError as exc:
            raise ValueError("output path must be in repo allowed audit generated root or an explicit temp directory") from exc
        return resolved
    rel_lower = rel.lower()
    allowed_prefix = "control/audits/h11-bundle-01-storefront-policy-packs-v0/generated/"
    if rel_lower.startswith(allowed_prefix):
        return resolved
    for prefix in FORBIDDEN_OUTPUT_ROOTS:
        if rel_lower == prefix or rel_lower.startswith(prefix + "/"):
            raise ValueError(f"refusing forbidden output root: {prefix}")
    raise ValueError("repo output path must be under the H11 audit generated root")


def _write_json(raw: str, payload: Mapping[str, Any]) -> None:
    path = safe_output_path(raw)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_text(raw: str, payload: str) -> None:
    path = safe_output_path(raw)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(payload, encoding="utf-8")


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    raise SystemExit(main())
