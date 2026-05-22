#!/usr/bin/env python3
"""Normalize one committed H11 storefront fixture offline."""

from __future__ import annotations

import argparse
import importlib
import json
from pathlib import Path
import sys
from typing import Any, Sequence, TextIO

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from archive.prototypes.legacy_runtime.connectors.h11_storefront.fixture_loader import load_h11_storefront_fixture  # noqa: E402
from archive.prototypes.legacy_runtime.connectors.h11_storefront.normalizer_common import H11_SOURCE_IDS  # noqa: E402

ALLOWED_PREFIXES = (
    "examples/connectors/h11_storefront/normalized",
    "examples/connectors/h11_storefront/identity",
    "control/audits/h11-bundle-02-storefront-fixture-runtime-v0/generated",
)
FORBIDDEN_PREFIXES = (
    "site/dist",
    "site/dist/data/public_index",
    "runtime",
    "contracts",
    "control/inventory/publication",
    "control/inventory/sources",
    "storefront_accounts",
    "accounts",
    "receipts",
    "entitlements",
    "store_libraries",
    "app_downloads",
    "game_installs",
    "package_downloads",
    "checkout_sessions",
    "install_actions",
    "launch_actions",
    "restricted_sources",
    "master_index",
    ".aide.local",
    ".local/eureka",
    ".cache/eureka",
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-id", required=True, choices=H11_SOURCE_IDS)
    parser.add_argument("--input", required=True)
    parser.add_argument("--output")
    parser.add_argument("--listing-output")
    parser.add_argument("--app-product-output")
    parser.add_argument("--version-output")
    parser.add_argument("--price-availability-output")
    parser.add_argument("--acquisition-output")
    parser.add_argument("--review-rating-output")
    parser.add_argument("--account-boundary-output")
    parser.add_argument("--rights-safety-output")
    parser.add_argument("--source-cache-output")
    parser.add_argument("--evidence-preview-output")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        fixture = load_h11_storefront_fixture(args.input)
        module = importlib.import_module(f"archive.prototypes.legacy_runtime.connectors.h11_storefront.{args.source_id}")
        normalized = module.normalize(fixture)
        outputs: list[tuple[str | None, Any]] = [
            (args.output, normalized),
            (args.listing_output, normalized["storefront_listing_identity_candidate"]),
            (args.app_product_output, normalized["app_product_identity_candidate"]),
            (args.version_output, normalized["version_release_channel_candidate"]),
            (args.price_availability_output, normalized["price_availability_region_candidate"]),
            (args.acquisition_output, normalized["acquisition_path_candidate"]),
            (args.review_rating_output, normalized["review_rating_metadata_candidate"]),
            (args.account_boundary_output, normalized["account_entitlement_boundary_candidate"]),
            (args.rights_safety_output, normalized["storefront_rights_safety_candidate"]),
            (args.source_cache_output, normalized["source_cache_candidate_preview"]),
            (args.evidence_preview_output, normalized["evidence_candidate_preview"]),
        ]
        if not args.check:
            for output, payload in outputs:
                if output:
                    path = safe_output_path(output, ALLOWED_PREFIXES)
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        if args.json:
            print(json.dumps(normalized, indent=2, sort_keys=True), file=stdout)
        else:
            print("H11 storefront fixture normalization", file=stdout)
            print("status: pass", file=stdout)
            print(f"source_id: {normalized['source_id']}", file=stdout)
            print("fixture_only: true", file=stdout)
            print("network_used: false", file=stdout)
            print("download_account_purchase_install_launch: false", file=stdout)
        return 0
    except Exception as exc:  # noqa: BLE001
        if args.json:
            print(json.dumps({"status": "invalid", "error": str(exc)}, indent=2, sort_keys=True), file=stdout)
        else:
            print("H11 storefront fixture normalization", file=stdout)
            print("status: invalid", file=stdout)
            print(f"ERROR: {exc}", file=stdout)
        return 1


def safe_output_path(output: str | Path, allowed_prefixes: Sequence[str] = ALLOWED_PREFIXES) -> Path:
    path = Path(output)
    if not path.is_absolute():
        path = REPO_ROOT / path
    resolved = path.resolve()
    try:
        rel = resolved.relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return resolved
    for forbidden in FORBIDDEN_PREFIXES:
        if rel == forbidden or rel.startswith(forbidden.rstrip("/") + "/"):
            raise ValueError(f"refusing forbidden output root: {forbidden}")
    return resolved


if __name__ == "__main__":
    raise SystemExit(main())
