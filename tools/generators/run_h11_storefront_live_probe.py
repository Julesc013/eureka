#!/usr/bin/env python3
"""Run or preflight H11 storefront metadata-only live probes with fail-closed gates."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from collections.abc import Mapping, Sequence
from typing import Any, TextIO

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from archive.prototypes.legacy_runtime.connectors.h11_storefront.live_probe_common import (  # noqa: E402
    SOURCE_CONFIGS,
    build_h11_storefront_live_probe_blocked_result,
    build_h11_storefront_live_probe_output_bundle,
    build_h11_storefront_live_probe_request,
    load_h11_storefront_live_probe_policy_bundle,
    summarize_h11_storefront_live_probe_result,
    validate_h11_storefront_live_probe_request,
)

FORBIDDEN_OUTPUT_ROOTS = (
    "site/dist",
    "site/dist/data/public_index",
    "runtime",
    "contracts",
    "control/inventory/publication",
    "control/inventory/sources",
    "data/master_index",
    "master_index",
    "accounts",
    "storefront_accounts",
    "receipts",
    "entitlements",
    "store_libraries",
    "app_downloads",
    "game_installs",
    "package_downloads",
    "checkout_sessions",
    "install_actions",
    "launch_actions",
    "review_actions",
    "restricted_sources",
    "uploads",
    "actions",
    ".aide.local",
    ".local/eureka",
    ".cache/eureka",
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-id", choices=sorted(SOURCE_CONFIGS))
    parser.add_argument("--request-key")
    parser.add_argument("--input")
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
    parser.add_argument("--review-seed-output")
    parser.add_argument("--health-output")
    parser.add_argument("--summary-output")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        bundle = load_h11_storefront_live_probe_policy_bundle(REPO_ROOT)
        request = _load_request(args, bundle)
        artifacts = run_probe(request, bundle, live=args.live and not args.check)
        result = artifacts["live_probe_result"]
        if not args.check:
            outputs = {
                args.output: result,
                args.listing_output: result["storefront_listing_identity_candidate"],
                args.app_product_output: result["app_product_identity_candidate"],
                args.version_output: result["version_release_channel_candidate"],
                args.price_availability_output: result["price_availability_region_candidate"],
                args.acquisition_output: result["acquisition_path_candidate"],
                args.review_rating_output: result["review_rating_metadata_candidate"],
                args.account_boundary_output: result["account_entitlement_boundary_candidate"],
                args.rights_safety_output: result["storefront_rights_safety_candidate"],
                args.source_cache_output: result["source_cache_candidate_preview"],
                args.evidence_preview_output: result["evidence_candidate_preview"],
                args.review_seed_output: result["review_queue_seed_preview"],
                args.health_output: result["connector_health_summary"],
            }
            for path, payload in outputs.items():
                if path:
                    _write_json(path, payload)
            if args.summary_output:
                _write_text(args.summary_output, render_summary(result))
        summary = {
            "status": "valid",
            "mode": "live" if args.live and not args.check else "check",
            "wrote_files": (not args.check) and any([
                args.output,
                args.listing_output,
                args.app_product_output,
                args.version_output,
                args.price_availability_output,
                args.acquisition_output,
                args.review_rating_output,
                args.account_boundary_output,
                args.rights_safety_output,
                args.source_cache_output,
                args.evidence_preview_output,
                args.review_seed_output,
                args.health_output,
                args.summary_output,
            ]),
            "live_probe": summarize_h11_storefront_live_probe_result(result),
        }
        if args.json:
            print(json.dumps(summary, indent=2, sort_keys=True), file=stdout)
        else:
            live = summary["live_probe"]
            print("H11 storefront live probe", file=stdout)
            print(f"status: {summary['status']}", file=stdout)
            print(f"mode: {summary['mode']}", file=stdout)
            print(f"source_id: {live['source_id']}", file=stdout)
            print(f"result: {live['result_status']}", file=stdout)
            print(f"request_count: {live['request_count']}", file=stdout)
            print(f"network_used: {str(live['network_used']).lower()}", file=stdout)
            if live["blocked_reasons"]:
                print("blocked_reasons:", file=stdout)
                for reason in live["blocked_reasons"]:
                    print(f"- {reason}", file=stdout)
        return 0
    except Exception as exc:  # noqa: BLE001
        if args.json:
            print(json.dumps({"status": "invalid", "error": str(exc)}, indent=2, sort_keys=True), file=stdout)
        else:
            print("H11 storefront live probe", file=stdout)
            print("status: invalid", file=stdout)
            print(f"ERROR: {exc}", file=stdout)
        return 1


def run_probe(request: Mapping[str, Any], policy_bundle: Mapping[str, Any], live: bool) -> dict[str, Any]:
    validation = validate_h11_storefront_live_probe_request(request, policy_bundle)
    if not validation["approved"]:
        result = build_h11_storefront_live_probe_blocked_result(request, validation["blocked_reasons"], policy_bundle)
        return {"live_probe_result": result, "output_bundle": build_h11_storefront_live_probe_output_bundle(result)}
    if not live:
        result = build_h11_storefront_live_probe_blocked_result(request, ["dry preflight only; --live not provided"], policy_bundle)
        result["result_status"] = "dry_run_preflight_pass"
        result["blocked_reason"] = None
        result["blocked_reasons"] = []
        result["connector_health_summary"]["live_probe_status"] = "dry_run_preflight_pass"
        result["connector_health_summary"]["response_status_summary"] = "preflight_pass"
        result["connector_health_summary"]["policy_blockers"] = []
        result["limitations"] = ["Committed policy approves this request, but no network call was requested."]
        return {"live_probe_result": result, "output_bundle": build_h11_storefront_live_probe_output_bundle(result)}
    result = build_h11_storefront_live_probe_blocked_result(
        request,
        ["live network execution remains fail-closed in H11-BUNDLE-03; source-specific transport requires future reviewed approval"],
        policy_bundle,
    )
    result["result_status"] = "live_probe_failed"
    result["connector_health_summary"]["live_probe_status"] = "live_probe_failed"
    return {"live_probe_result": result, "output_bundle": build_h11_storefront_live_probe_output_bundle(result)}


def render_summary(result: Mapping[str, Any]) -> str:
    summary = summarize_h11_storefront_live_probe_result(result)
    lines = [
        "# H11 Storefront Live Probe Summary",
        "",
        f"- source_id: `{summary['source_id']}`",
        f"- result: `{summary['result_status']}`",
        f"- request_count: `{summary['request_count']}`",
        f"- network_used: `{str(summary['network_used']).lower()}`",
        "- metadata_only: `true`",
        "- api_catalog_query: `false unless approved bounded metadata-only`",
        "- product_page_fetch: `false unless approved bounded metadata-only`",
        "- downloads: `false`",
        "- account_access: `false`",
        "- purchase_automation: `false`",
        "- entitlement_checks: `false`",
        "- install_launch: `false`",
        "- review_rating_write: `false`",
        "- scraping_crawling: `false`",
        "- restricted_source_access: `false`",
        "- public_index_mutated: `false`",
        "- master_index_mutated: `false`",
    ]
    if summary["blocked_reasons"]:
        lines.extend(["", "## Blocked Reasons"])
        lines.extend(f"- {reason}" for reason in summary["blocked_reasons"])
    return "\n".join(lines) + "\n"


def _load_request(args: argparse.Namespace, bundle: Mapping[str, Any]) -> dict[str, Any]:
    if args.input:
        payload = json.loads(_repo_path(args.input).read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("request input must be a JSON object")
        return payload
    if not args.source_id or not args.request_key:
        raise ValueError("--source-id and --request-key are required when --input is not provided")
    return build_h11_storefront_live_probe_request(args.source_id, args.request_key, bundle, live_requested=args.live and not args.check)


def _repo_path(path_text: str | Path) -> Path:
    path = Path(path_text)
    return path if path.is_absolute() else REPO_ROOT / path


def _write_json(path_text: str, payload: object) -> None:
    path = _safe_output_path(Path(path_text))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_text(path_text: str, text: str) -> None:
    path = _safe_output_path(Path(path_text))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _safe_output_path(path: Path) -> Path:
    resolved = (REPO_ROOT / path).resolve() if not path.is_absolute() else path.resolve()
    try:
        rel = resolved.relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return resolved
    rel_lower = rel.casefold()
    for forbidden in FORBIDDEN_OUTPUT_ROOTS:
        forbidden_lower = forbidden.casefold().rstrip("/")
        if rel_lower == forbidden_lower or rel_lower.startswith(forbidden_lower + "/"):
            raise ValueError(f"refusing forbidden output root: {forbidden}")
    return resolved


if __name__ == "__main__":
    raise SystemExit(main())
