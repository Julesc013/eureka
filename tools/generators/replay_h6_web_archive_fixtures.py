#!/usr/bin/env python3
"""Replay committed H6 web archive/news/event fixtures offline."""

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

from archive.prototypes.legacy_runtime.connectors.h6_web_archive_news_event.fixture_loader import load_h6_web_archive_fixture  # noqa: E402
from archive.prototypes.legacy_runtime.connectors.h6_web_archive_news_event.normalizer_common import H6_SOURCE_IDS, build_h6_fixture_replay_result  # noqa: E402

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


ALLOWED_PREFIXES = ("examples/connectors/h6_web_archive_news_event/replay_results",)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-id", choices=H6_SOURCE_IDS)
    parser.add_argument("--fixture-root", default="examples/connectors/h6_web_archive_news_event/fixtures")
    parser.add_argument("--output-dir")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        results = replay_fixtures(args.fixture_root, args.source_id)
        if args.output_dir and not args.check:
            output_dir = safe_output_path(args.output_dir, ALLOWED_PREFIXES)
            output_dir.mkdir(parents=True, exist_ok=True)
            for result in results:
                parts = str(result.get("fixture_id", "fixture")).split(".")
                kind = parts[-2] if len(parts) > 2 else "fixture"
                (output_dir / f"{result['source_id']}_{kind}_replay_result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        summary = {
            "schema_version": "h6_web_archive_fixture_replay_summary.v0",
            "status": "pass",
            "source_count": len(sorted({item["source_id"] for item in results})),
            "fixture_replay_count": len(results),
            "network_calls_made": False,
            "fetch_crawl_used": False,
            "restricted_source_access_used": False,
            "results": results,
        }
        if args.json:
            print(json.dumps(summary, indent=2, sort_keys=True), file=stdout)
        else:
            print("H6 web archive/news/event fixture replay", file=stdout)
            print("status: pass", file=stdout)
            print(f"source_count: {summary['source_count']}", file=stdout)
            print(f"fixture_replay_count: {summary['fixture_replay_count']}", file=stdout)
            print("network_used: false", file=stdout)
            print("fetch_crawl_used: false", file=stdout)
        return 0
    except Exception as exc:  # noqa: BLE001
        if args.json:
            print(json.dumps({"status": "invalid", "error": str(exc)}, indent=2, sort_keys=True), file=stdout)
        else:
            print("H6 web archive/news/event fixture replay", file=stdout)
            print("status: invalid", file=stdout)
            print(f"ERROR: {exc}", file=stdout)
        return 1


def replay_fixtures(fixture_root: str | Path, source_id: str | None = None) -> list[dict[str, Any]]:
    root = Path(fixture_root)
    if not root.is_absolute():
        root = REPO_ROOT / root
    results: list[dict[str, Any]] = []
    for item in ([source_id] if source_id else list(H6_SOURCE_IDS)):
        assert item is not None
        source_dir = root / item
        if not source_dir.is_dir():
            raise ValueError(f"missing fixture directory: {source_dir}")
        module = importlib.import_module(f"archive.prototypes.legacy_runtime.connectors.h6_web_archive_news_event.{item}")
        for fixture_path in sorted(source_dir.glob("*.json")):
            fixture = load_h6_web_archive_fixture(fixture_path)
            normalized = module.normalize(fixture)
            results.append(build_h6_fixture_replay_result(fixture, normalized))
    return results


if __name__ == "__main__":
    raise SystemExit(main())
