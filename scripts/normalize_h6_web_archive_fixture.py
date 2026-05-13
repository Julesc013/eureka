#!/usr/bin/env python3
"""Normalize one committed H6 web archive/news/event fixture offline."""

from __future__ import annotations

import argparse
import importlib
import json
from pathlib import Path
import sys
from typing import Any, Sequence, TextIO

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from control.prototypes.legacy_runtime.connectors.h6_web_archive_news_event.fixture_loader import load_h6_web_archive_fixture  # noqa: E402
from control.prototypes.legacy_runtime.connectors.h6_web_archive_news_event.normalizer_common import H6_SOURCE_IDS  # noqa: E402

from pathlib import Path
import tempfile

REPO_ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN_OUTPUT_ROOTS = (
    "site/dist",
    "data/public_index",
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


ALLOWED_PREFIXES = (
    "examples/connectors/h6_web_archive_news_event/normalized",
    "examples/connectors/h6_web_archive_news_event/identity",
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-id", required=True, choices=H6_SOURCE_IDS)
    parser.add_argument("--input", required=True)
    parser.add_argument("--output")
    parser.add_argument("--capture-output")
    parser.add_argument("--time-state-output")
    parser.add_argument("--event-output")
    parser.add_argument("--dead-link-output")
    parser.add_argument("--public-document-output")
    parser.add_argument("--media-transcript-output")
    parser.add_argument("--source-cache-output")
    parser.add_argument("--evidence-preview-output")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        fixture = load_h6_web_archive_fixture(args.input)
        module = importlib.import_module(f"control.prototypes.legacy_runtime.connectors.h6_web_archive_news_event.{args.source_id}")
        normalized = module.normalize(fixture)
        outputs: list[tuple[str | None, Any]] = [
            (args.output, normalized),
            (args.capture_output, normalized.get("web_capture_identity_candidate", {})),
            (args.time_state_output, normalized.get("archived_url_time_state_candidate", {})),
            (args.event_output, normalized.get("news_event_mention_candidate_preview", [])),
            (args.dead_link_output, normalized.get("dead_link_trace_candidate_preview", [])),
            (args.public_document_output, normalized.get("public_document_trace_candidate_preview", [])),
            (args.media_transcript_output, normalized.get("media_transcript_metadata_candidate_preview", [])),
            (args.source_cache_output, normalized.get("source_cache_candidate_preview", {})),
            (args.evidence_preview_output, normalized.get("evidence_candidate_preview", {})),
        ]
        if not args.check:
            for output_path, payload in outputs:
                if output_path:
                    path = safe_output_path(output_path, ALLOWED_PREFIXES)
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        summary = {
            "schema_version": "h6_web_archive_normalize_summary.v0",
            "status": "pass",
            "source_id": args.source_id,
            "normalized_record_id": normalized.get("normalized_record_id"),
            "web_capture_candidates": 1 if normalized.get("web_capture_identity_candidate") else 0,
            "time_state_candidates": 1 if normalized.get("archived_url_time_state_candidate") else 0,
            "news_event_candidates": len(normalized.get("news_event_mention_candidate_preview", [])),
            "dead_link_candidates": len(normalized.get("dead_link_trace_candidate_preview", [])),
            "public_document_trace_candidates": len(normalized.get("public_document_trace_candidate_preview", [])),
            "media_transcript_candidates": len(normalized.get("media_transcript_metadata_candidate_preview", [])),
            "network_calls_made": False,
            "fetch_crawl_used": False,
            "restricted_source_access_used": False,
        }
        if args.json:
            print(json.dumps(summary, indent=2, sort_keys=True), file=stdout)
        else:
            print("H6 web archive/news/event fixture normalization", file=stdout)
            print("status: pass", file=stdout)
            print(f"source_id: {args.source_id}", file=stdout)
            print(f"normalized_record_id: {summary['normalized_record_id']}", file=stdout)
            print("network_used: false", file=stdout)
            print("fetch_crawl_used: false", file=stdout)
        return 0
    except Exception as exc:  # noqa: BLE001
        if args.json:
            print(json.dumps({"status": "invalid", "error": str(exc)}, indent=2, sort_keys=True), file=stdout)
        else:
            print("H6 web archive/news/event fixture normalization", file=stdout)
            print("status: invalid", file=stdout)
            print(f"ERROR: {exc}", file=stdout)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
