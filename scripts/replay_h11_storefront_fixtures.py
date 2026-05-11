#!/usr/bin/env python3
"""Replay committed H11 storefront fixtures offline."""

from __future__ import annotations

import argparse
import importlib
import json
from pathlib import Path
import sys
from typing import Sequence, TextIO

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.connectors.h11_storefront.fixture_loader import load_h11_storefront_fixture  # noqa: E402
from runtime.connectors.h11_storefront.normalizer_common import H11_SOURCE_IDS, build_h11_fixture_replay_result  # noqa: E402
from scripts.normalize_h11_storefront_fixture import safe_output_path  # noqa: E402

FIXTURE_FILES = {'minimal': 'minimal_record.json', 'listing_identity': 'listing_identity_record.json', 'app_product_identity': 'app_product_identity_record.json', 'version_release_channel': 'version_release_channel_record.json', 'price_availability_region': 'price_availability_region_record.json', 'acquisition_path_blocked': 'acquisition_path_blocked_record.json', 'review_rating_metadata': 'review_rating_metadata_record.json', 'account_entitlement_boundary': 'account_entitlement_boundary_record.json', 'rights_safety': 'rights_safety_record.json', 'policy_blocked': 'policy_blocked_record.json'}


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-id", choices=H11_SOURCE_IDS)
    parser.add_argument("--fixture-root", default="examples/connectors/h11_storefront/fixtures")
    parser.add_argument("--output-dir")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        source_ids = [args.source_id] if args.source_id else list(H11_SOURCE_IDS)
        results = []
        normalized_count = 0
        for source_id in source_ids:
            module = importlib.import_module(f"runtime.connectors.h11_storefront.{source_id}")
            source_dir = REPO_ROOT / args.fixture_root / source_id
            for kind, filename in FIXTURE_FILES.items():
                fixture = load_h11_storefront_fixture(source_dir / filename)
                normalized = module.normalize(fixture)
                replay = build_h11_fixture_replay_result(fixture, normalized)
                normalized_count += 1
                results.append(replay)
            if args.output_dir and not args.check:
                out_dir = safe_output_path(Path(args.output_dir) / source_id)
                out_dir.mkdir(parents=True, exist_ok=True)
                representative = module.normalize(load_h11_storefront_fixture(source_dir / "minimal_record.json"))
                replay = build_h11_fixture_replay_result(load_h11_storefront_fixture(source_dir / "minimal_record.json"), representative)
                (out_dir / "normalized_record.json").write_text(json.dumps(representative, indent=2, sort_keys=True) + "\n", encoding="utf-8")
                (out_dir / "replay_result.json").write_text(json.dumps(replay, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        summary = {
            "schema_version": "h11_storefront_fixture_replay_summary.v0",
            "status": "pass",
            "source_count": len(source_ids),
            "fixture_count": normalized_count,
            "result_count": len(results),
            "network_used": False,
            "download_account_purchase_install_launch_used": False,
            "public_index_mutated": False,
            "master_index_mutated": False,
            "wrote_files": bool(args.output_dir and not args.check),
        }
        if args.json:
            print(json.dumps(summary, indent=2, sort_keys=True), file=stdout)
        else:
            print("H11 storefront fixture replay", file=stdout)
            print(f"status: {summary['status']}", file=stdout)
            print(f"source_count: {summary['source_count']}", file=stdout)
            print(f"fixture_count: {summary['fixture_count']}", file=stdout)
            print("network_used: false", file=stdout)
        return 0
    except Exception as exc:  # noqa: BLE001
        if args.json:
            print(json.dumps({"status": "invalid", "error": str(exc)}, indent=2, sort_keys=True), file=stdout)
        else:
            print("H11 storefront fixture replay", file=stdout)
            print("status: invalid", file=stdout)
            print(f"ERROR: {exc}", file=stdout)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
