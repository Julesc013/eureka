#!/usr/bin/env python3
"""Summarize H11 storefront fixture outputs offline."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import tempfile
from typing import Any, Mapping, Sequence, TextIO

REPO_ROOT = Path(__file__).resolve().parents[1]
KNOWN_SOURCE_IDS = {
    "apple_app_store_metadata",
    "chrome_web_store_metadata",
    "epic_games_store_policy_limited",
    "fdroid_metadata",
    "flathub_metadata",
    "generic_commercial_software_marketplace",
    "generic_vendor_product_page",
    "gog_store_metadata",
    "google_play_metadata",
    "humble_store_policy_limited",
    "itchio_storefront_metadata",
    "mac_app_store_metadata",
    "microsoft_store_metadata",
    "mozilla_addons_metadata",
    "snapcraft_metadata",
    "steam_store_metadata",
}
FORBIDDEN_OUTPUT_ROOTS = (
    "site/dist",
    "data/public_index",
    "runtime",
    "contracts",
    "storefront_accounts",
    "accounts",
    "receipts",
    "entitlements",
    "store_libraries",
    "app_downloads",
    "package_downloads",
    "game_installs",
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
    parser.add_argument("--input", action="append", default=[])
    parser.add_argument("--output")
    parser.add_argument("--summary-output")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        summary = build_summary(args.input or ["examples/connectors/h11_storefront"])
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
            print("H11 storefront fixture output summary", file=stdout)
            print(f"status: {summary['status']}", file=stdout)
            print(f"source_count: {summary['source_count']}", file=stdout)
            print(f"normalized_record_count: {summary['normalized_record_count']}", file=stdout)
            print(f"listing_identity_candidate_count: {summary['listing_identity_candidate_count']}", file=stdout)
            print(f"acquisition_path_candidate_count: {summary['acquisition_path_candidate_count']}", file=stdout)
        return 0
    except Exception as exc:  # noqa: BLE001
        if args.json:
            print(json.dumps({"status": "invalid", "error": str(exc)}, indent=2, sort_keys=True), file=stdout)
        else:
            print("H11 storefront fixture output summary", file=stdout)
            print("status: invalid", file=stdout)
            print(f"ERROR: {exc}", file=stdout)
        return 1


def build_summary(inputs: Sequence[str]) -> dict[str, Any]:
    files: list[Path] = []
    for raw in inputs:
        path = Path(raw)
        if not path.is_absolute():
            path = REPO_ROOT / path
        if path.is_dir():
            files.extend(path.rglob("*.json"))
        elif path.exists():
            files.append(path)
    records: list[Mapping[str, Any]] = []
    for path in files:
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if isinstance(value, Mapping):
            records.append(value)
    def count_schema(schema: str) -> int:
        return sum(1 for item in records if str(item.get("schema_version", "")).startswith(schema))
    source_ids = {str(item.get("source_id")) for item in records if item.get("source_id") in KNOWN_SOURCE_IDS}
    return {
        "schema_version": "h11_storefront_fixture_output_summary.v0",
        "status": "pass",
        "source_count": len(source_ids),
        "normalized_record_count": count_schema("h11_storefront_normalized_record"),
        "listing_identity_candidate_count": count_schema("h11_storefront_listing_identity_candidate"),
        "app_product_candidate_count": count_schema("h11_app_product_identity_candidate"),
        "version_candidate_count": count_schema("h11_version_release_channel_candidate"),
        "price_availability_candidate_count": count_schema("h11_price_availability_region_candidate"),
        "acquisition_path_candidate_count": count_schema("h11_acquisition_path_candidate"),
        "review_rating_candidate_count": count_schema("h11_review_rating_metadata_candidate"),
        "account_boundary_candidate_count": count_schema("h11_account_entitlement_boundary_candidate"),
        "rights_safety_candidate_count": count_schema("h11_storefront_rights_safety_candidate"),
        "replay_result_count": count_schema("h11_storefront_fixture_replay_result"),
        "blockers": ["live access not approved", "account/download/purchase/install/launch behavior forbidden"],
        "warnings": [],
        "wrote_files": False,
    }


def render_summary_markdown(summary: Mapping[str, Any]) -> str:
    return "\n".join([
        "# H11 Storefront Fixture Output Summary",
        "",
        f"- status: `{summary['status']}`",
        f"- source_count: `{summary['source_count']}`",
        f"- normalized_record_count: `{summary['normalized_record_count']}`",
        f"- acquisition_path_candidate_count: `{summary['acquisition_path_candidate_count']}`",
        "",
        "Outputs are fixture-only candidates and previews, not accepted storefront truth.",
    ]) + "\n"


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
    if rel_lower.startswith("control/audits/h11-bundle-02-storefront-fixture-runtime-v0/generated/"):
        return resolved
    for prefix in FORBIDDEN_OUTPUT_ROOTS:
        if rel_lower == prefix or rel_lower.startswith(prefix + "/"):
            raise ValueError(f"refusing forbidden output root: {prefix}")
    raise ValueError("repo output path must be under the H11 fixture audit generated root")


def _write_json(raw: str, payload: Mapping[str, Any]) -> None:
    path = safe_output_path(raw)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_text(raw: str, payload: str) -> None:
    path = safe_output_path(raw)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(payload, encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
