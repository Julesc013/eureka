#!/usr/bin/env python3
"""Summarize H12 retro/community fixture outputs offline."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import tempfile
from typing import Any, Mapping, Sequence, TextIO

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.connectors.h12_retro_community.normalizer_common import H12_SOURCE_IDS  # noqa: E402

FORBIDDEN_OUTPUT_ROOTS = (
    "site/dist",
    "data/public_index",
    "runtime",
    "contracts",
    "roms",
    "isos",
    "disc_images",
    "emulators",
    "bios",
    "firmware",
    "vintage_software_downloads",
    "installers",
    "patches",
    "cracks",
    "keys",
    "serials",
    "gated_source_accounts",
    "forum_sessions",
    "archive_extractions",
    "download_actions",
    "install_actions",
    "execution_actions",
    "acquisition_actions",
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
        summary = build_summary(args.input or ["examples/connectors/h12_retro_community"])
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
            print("H12 retro/community fixture output summary", file=stdout)
            print(f"status: {summary['status']}", file=stdout)
            print(f"source_count: {summary['source_count']}", file=stdout)
            print(f"normalized_record_count: {summary['normalized_record_count']}", file=stdout)
            print(f"retro_software_identity_candidate_count: {summary['retro_software_identity_candidate_count']}", file=stdout)
            print(f"rights_safety_candidate_count: {summary['retro_rights_safety_candidate_count']}", file=stdout)
        return 0
    except Exception as exc:  # noqa: BLE001
        if args.json:
            print(json.dumps({"status": "invalid", "error": str(exc)}, indent=2, sort_keys=True), file=stdout)
        else:
            print("H12 retro/community fixture output summary", file=stdout)
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

    source_ids = {str(item.get("source_id")) for item in records if item.get("source_id") in H12_SOURCE_IDS}
    return {
        "schema_version": "h12_retro_community_fixture_output_summary.v0",
        "status": "pass",
        "source_count": len(source_ids),
        "normalized_record_count": count_schema("h12_retro_community_normalized_record"),
        "retro_software_identity_candidate_count": count_schema("h12_retro_software_identity_candidate"),
        "platform_version_edition_candidate_count": count_schema("h12_platform_version_edition_candidate"),
        "archive_item_member_candidate_count": count_schema("h12_archive_item_member_candidate"),
        "compatibility_install_note_candidate_count": count_schema("h12_compatibility_install_note_candidate"),
        "community_review_comment_candidate_count": count_schema("h12_community_review_comment_candidate"),
        "hash_checksum_candidate_count": count_schema("h12_hash_checksum_candidate"),
        "ia_wayback_corroboration_candidate_count": count_schema("h12_ia_wayback_corroboration_candidate"),
        "gated_source_boundary_candidate_count": count_schema("h12_gated_source_boundary_candidate"),
        "retro_rights_safety_candidate_count": count_schema("h12_retro_rights_safety_candidate"),
        "fixture_replay_result_count": count_schema("h12_retro_community_fixture_replay_result"),
        "blockers": ["live access not approved", "downloads, extraction, execution, acquisition, uploads, hash submissions, gated access, scraping, crawling, bypass, and truth acceptance forbidden"],
        "warnings": [],
        "wrote_files": False,
    }


def render_summary_markdown(summary: Mapping[str, Any]) -> str:
    return "\n".join([
        "# H12 Retro/Community Fixture Output Summary",
        "",
        f"- status: `{summary['status']}`",
        f"- source_count: `{summary['source_count']}`",
        f"- normalized_record_count: `{summary['normalized_record_count']}`",
        f"- retro_software_identity_candidate_count: `{summary['retro_software_identity_candidate_count']}`",
        f"- gated_source_boundary_candidate_count: `{summary['gated_source_boundary_candidate_count']}`",
        "",
        "Outputs are fixture-only candidates and previews, not accepted retro/community archive truth.",
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
    allowed_prefix = "control/audits/h12-bundle-02-retro-community-fixture-runtime-v0/generated/"
    if rel_lower.startswith(allowed_prefix):
        return resolved
    for prefix in FORBIDDEN_OUTPUT_ROOTS:
        if rel_lower == prefix or rel_lower.startswith(prefix + "/"):
            raise ValueError(f"refusing forbidden output root: {prefix}")
    raise ValueError("repo output path must be under the H12 fixture audit generated root")


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
