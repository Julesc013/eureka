#!/usr/bin/env python3
"""Summarize H6 web archive/news/event fixture outputs offline."""

from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence, TextIO

REPO_ROOT = Path(__file__).resolve().parents[2]
EXPECTED_SOURCE_IDS = {
    "wayback_cdx_memento",
    "common_crawl_cdxj",
    "public_warc_wacz_collection",
    "gdelt_news_event",
    "chronicling_america",
    "trove_newspapers",
    "cspan_video_library",
    "aapb_broadcast_archive",
    "archive_today_snapshot",
    "generic_newspaper_archive",
    "generic_web_archive",
    "generic_public_event_trace",
    "restricted_public_document_manifest",
}

from pathlib import Path
import tempfile

REPO_ROOT = Path(__file__).resolve().parents[2]
FORBIDDEN_OUTPUT_ROOTS = (
    "site/dist",
    "site/dist/data/public_index",
    "runtime",
    "contracts",
    "data/master_index",
    "master_index",
    "control/inventory/publication",
    "control/inventory/sources",
    "crawl",
    "crawl_cache",
    "warc_wacz_cache",
    "media_downloads",
    "transcript_cache",
    "document_dumps",
    ".aide.local",
    ".local/eureka",
    ".cache/eureka",
)


def safe_output_path(path_text: str | Path, allowed_prefixes: tuple[str, ...]) -> Path:
    path = Path(path_text)
    resolved = (REPO_ROOT / path).resolve() if not path.is_absolute() else path.resolve()
    repo_root = REPO_ROOT.resolve()
    try:
        rel = resolved.relative_to(repo_root).as_posix()
        rel_lower = rel.casefold()
        for forbidden in FORBIDDEN_OUTPUT_ROOTS:
            forbidden_lower = forbidden.casefold().rstrip("/")
            if rel_lower == forbidden_lower or rel_lower.startswith(forbidden_lower + "/"):
                raise ValueError(f"refusing forbidden output root: {forbidden}")
        for prefix in allowed_prefixes:
            prefix_lower = prefix.casefold().rstrip("/")
            if rel_lower == prefix_lower or rel_lower.startswith(prefix_lower + "/"):
                return resolved
        if rel_lower.startswith("control/audits/") and "/generated/" in rel_lower:
            return resolved
        raise ValueError(f"refusing output outside approved H6 fixture roots: {rel}")
    except ValueError as exc:
        if str(exc).startswith("refusing"):
            raise
        temp_root = Path(tempfile.gettempdir()).resolve()
        try:
            resolved.relative_to(temp_root)
            return resolved
        except ValueError as temp_exc:
            raise ValueError(f"refusing output outside approved roots or temp directory: {resolved}") from temp_exc


ALLOWED_PREFIXES = ("control/audits/h6-bundle-02-web-archive-fixture-runtime-v0/generated",)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", action="append", default=[])
    parser.add_argument("--output")
    parser.add_argument("--summary-output")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        roots = args.input or ["examples/connectors/h6_web_archive_news_event"]
        summary = build_summary([Path(item) for item in roots])
        if not args.check:
            if args.output:
                path = safe_output_path(args.output, ALLOWED_PREFIXES)
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            if args.summary_output:
                path = safe_output_path(args.summary_output, ALLOWED_PREFIXES)
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(render_markdown(summary), encoding="utf-8")
        if args.json:
            print(json.dumps(summary, indent=2, sort_keys=True), file=stdout)
        else:
            print("H6 web archive/news/event fixture output summary", file=stdout)
            print(f"status: {summary['status']}", file=stdout)
            print(f"source_count: {summary['source_count']}", file=stdout)
            print(f"normalized_records: {summary['normalized_record_count']}", file=stdout)
            print(f"event_candidates: {summary['news_event_candidate_count']}", file=stdout)
        return 0
    except Exception as exc:  # noqa: BLE001
        if args.json:
            print(json.dumps({"status": "invalid", "error": str(exc)}, indent=2, sort_keys=True), file=stdout)
        else:
            print("H6 web archive/news/event fixture output summary", file=stdout)
            print("status: invalid", file=stdout)
            print(f"ERROR: {exc}", file=stdout)
        return 1


def build_summary(inputs: Sequence[Path]) -> dict[str, Any]:
    files: list[Path] = []
    for item in inputs:
        path = item if item.is_absolute() else REPO_ROOT / item
        if path.is_dir():
            files.extend(sorted(path.rglob("*.json")))
        elif path.is_file():
            files.append(path)
    counts: Counter[str] = Counter()
    sources: set[str] = set()
    blockers: list[str] = []
    warnings: list[str] = []
    for path in files:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, Mapping):
            continue
        schema = str(payload.get("schema_version", "unknown"))
        source_id = payload.get("source_id")
        if schema == "h6_web_archive_normalized_record.v0":
            if isinstance(source_id, str) and source_id in EXPECTED_SOURCE_IDS:
                sources.add(source_id)
            counts["normalized_record"] += 1
            counts["web_capture"] += 1 if payload.get("web_capture_identity_candidate") else 0
            counts["time_state"] += 1 if payload.get("archived_url_time_state_candidate") else 0
            counts["news_event"] += len(payload.get("news_event_mention_candidate_preview", []) or [])
            counts["dead_link"] += len(payload.get("dead_link_trace_candidate_preview", []) or [])
            counts["public_document"] += len(payload.get("public_document_trace_candidate_preview", []) or [])
            counts["media_transcript"] += len(payload.get("media_transcript_metadata_candidate_preview", []) or [])
        elif schema == "h6_web_archive_fixture_replay_result.v0":
            if isinstance(source_id, str) and source_id in EXPECTED_SOURCE_IDS:
                sources.add(source_id)
            counts["replay_result"] += 1
            if payload.get("replay_status") == "blocked_by_policy_fixture":
                blockers.append(str(payload.get("fixture_id")))
        elif schema == "h6_web_archive_fixture.v0":
            if isinstance(source_id, str) and source_id in EXPECTED_SOURCE_IDS:
                sources.add(source_id)
            counts["fixture"] += 1
        elif schema.endswith("_candidate.v0"):
            counts["candidate_examples"] += 1
        if payload.get("warnings"):
            warnings.extend(str(item) for item in payload.get("warnings", []))
    return {
        "schema_version": "h6_web_archive_fixture_output_summary.v0",
        "status": "pass",
        "source_count": len(sources),
        "source_ids": sorted(sources),
        "fixture_count": counts["fixture"],
        "normalized_record_count": counts["normalized_record"],
        "fixture_replay_result_count": counts["replay_result"],
        "web_capture_candidate_count": counts["web_capture"],
        "time_state_candidate_count": counts["time_state"],
        "news_event_candidate_count": counts["news_event"],
        "dead_link_candidate_count": counts["dead_link"],
        "public_document_trace_candidate_count": counts["public_document"],
        "media_transcript_candidate_count": counts["media_transcript"],
        "candidate_example_count": counts["candidate_examples"],
        "blockers": blockers,
        "warnings": warnings,
        "network_calls_made": False,
        "fetch_crawl_used": False,
        "restricted_source_access_used": False,
    }


def render_markdown(summary: Mapping[str, Any]) -> str:
    lines = ["# H6 Web Archive Fixture Output Summary", "", f"- status: `{summary.get('status')}`", f"- source_count: `{summary.get('source_count')}`", f"- normalized_record_count: `{summary.get('normalized_record_count')}`", f"- news_event_candidate_count: `{summary.get('news_event_candidate_count')}`", "", "## Sources"]
    lines.extend(f"- {item}" for item in summary.get("source_ids", []))
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
