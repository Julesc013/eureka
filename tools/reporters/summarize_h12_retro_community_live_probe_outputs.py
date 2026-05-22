#!/usr/bin/env python3
"""Summarize H12 retro/community live-probe outputs without network use."""

from __future__ import annotations

import argparse
import json
from collections.abc import Mapping, Sequence
from pathlib import Path
import sys
from typing import Any, TextIO

REPO_ROOT = Path(__file__).resolve().parents[2]
FORBIDDEN_OUTPUT_ROOTS = (
    "site/dist",
    "site/dist/data/public_index",
    "runtime",
    "contracts",
    "data/master_index",
    "master_index",
    "roms",
    "isos",
    "disc_images",
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
    "execution_actions",
    "restricted_sources",
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
        inputs = args.input or ["examples/connectors/h12_retro_community/live_probe_results"]
        results = load_results(inputs)
        summary = summarize(results)
        if not args.check:
            if args.output:
                _write_json(args.output, summary)
            if args.summary_output:
                _write_text(args.summary_output, render_markdown(summary))
        if args.json:
            print(json.dumps(summary, indent=2, sort_keys=True), file=stdout)
        else:
            print("H12 retro/community live probe output summary", file=stdout)
            print(f"status: {summary['status']}", file=stdout)
            print(f"sources_attempted: {len(summary['attempted_sources'])}", file=stdout)
            print(f"blocked_sources: {len(summary['blocked_sources'])}", file=stdout)
            print(f"completed_sources: {len(summary['completed_sources'])}", file=stdout)
            print(f"network_used: {str(summary['network_used']).lower()}", file=stdout)
        return 0
    except Exception as exc:  # noqa: BLE001
        if args.json:
            print(json.dumps({"status": "invalid", "error": str(exc)}, indent=2, sort_keys=True), file=stdout)
        else:
            print("H12 retro/community live probe output summary", file=stdout)
            print("status: invalid", file=stdout)
            print(f"ERROR: {exc}", file=stdout)
        return 1


def load_results(inputs: Sequence[str]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for item in inputs:
        path = _repo_path(item)
        files = sorted(path.rglob("*.json")) if path.is_dir() else [path]
        for file in files:
            payload = json.loads(file.read_text(encoding="utf-8"))
            if isinstance(payload, Mapping) and payload.get("schema_version") == "h12_retro_community_live_probe_result.v0":
                out.append(dict(payload))
    return out


def summarize(results: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    attempted = sorted({str(item.get("source_id")) for item in results if item.get("source_id")})
    blocked = sorted({str(item.get("source_id")) for item in results if str(item.get("result_status", "")).startswith("blocked_")})
    completed = sorted({str(item.get("source_id")) for item in results if item.get("result_status") == "live_probe_completed"})
    return {
        "schema_version": "h12_retro_community_live_probe_output_summary.v0",
        "status": "valid",
        "attempted_sources": attempted,
        "completed_sources": completed,
        "blocked_sources": blocked,
        "request_count_total": sum(int(item.get("request_count") or 0) for item in results),
        "network_used": any(bool(item.get("network_used")) for item in results),
        "blocked_reasons": sorted({reason for item in results for reason in (item.get("blocked_reasons") or [])}),
        "retro_software_identity_candidate_count": sum(1 for item in results if _candidate_present(item.get("retro_software_identity_candidate"))),
        "platform_version_edition_candidate_count": sum(1 for item in results if _candidate_present(item.get("platform_version_edition_candidate"))),
        "archive_item_member_candidate_count": sum(1 for item in results if _candidate_present(item.get("archive_item_member_candidate"))),
        "compatibility_install_note_candidate_count": sum(1 for item in results if _candidate_present(item.get("compatibility_install_note_candidate"))),
        "community_review_comment_candidate_count": sum(1 for item in results if _candidate_present(item.get("community_review_comment_candidate"))),
        "hash_checksum_candidate_count": sum(1 for item in results if _candidate_present(item.get("hash_checksum_candidate"))),
        "ia_wayback_corroboration_candidate_count": sum(1 for item in results if _candidate_present(item.get("ia_wayback_corroboration_candidate"))),
        "gated_source_boundary_candidate_count": sum(1 for item in results if _candidate_present(item.get("gated_source_boundary_candidate"))),
        "retro_rights_safety_candidate_count": sum(1 for item in results if _candidate_present(item.get("retro_rights_safety_candidate"))),
        "source_cache_candidate_count": sum(1 for item in results if _candidate_present(item.get("source_cache_candidate_preview"))),
        "evidence_candidate_preview_count": sum(1 for item in results if _candidate_present(item.get("evidence_candidate_preview"))),
        "review_seed_count": sum(1 for item in results if item.get("review_queue_seed_preview")),
        "health_summary_count": sum(1 for item in results if item.get("connector_health_summary")),
        "public_index_mutated": False,
        "master_index_mutated": False,
    }


def render_markdown(summary: Mapping[str, Any]) -> str:
    return "\n".join([
        "# H12 Retro/Community Live Probe Output Summary",
        "",
        f"- status: `{summary['status']}`",
        f"- attempted_sources: `{len(summary['attempted_sources'])}`",
        f"- completed_sources: `{len(summary['completed_sources'])}`",
        f"- blocked_sources: `{len(summary['blocked_sources'])}`",
        f"- request_count_total: `{summary['request_count_total']}`",
        f"- network_used: `{str(summary['network_used']).lower()}`",
        "- metadata_only: `true`",
        "- downloads: `false`",
        "- extraction: `false`",
        "- execution: `false`",
        "- acquisition_actions: `false`",
        "- uploads: `false`",
        "- scraping_crawling: `false`",
        "- restricted_source_access: `false`",
        "- public_index_mutated: `false`",
        "- master_index_mutated: `false`",
        "",
    ]) + "\n"


def _candidate_present(value: object) -> bool:
    return isinstance(value, Mapping) and value.get("status") != "not_created_blocked_by_policy"


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
