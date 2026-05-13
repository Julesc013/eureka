#!/usr/bin/env python3
"""Replay committed H7 library/cultural/research fixtures offline."""

from __future__ import annotations

import argparse
import importlib
import json
from pathlib import Path
import sys
import tempfile
from typing import Any, Sequence, TextIO

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from control.prototypes.legacy_runtime.connectors.h7_library_research.fixture_loader import load_h7_library_research_fixture  # noqa: E402
from control.prototypes.legacy_runtime.connectors.h7_library_research.normalizer_common import H7_SOURCE_IDS, build_h7_fixture_replay_result  # noqa: E402
from scripts.normalize_h7_library_research_fixture import safe_output_path  # noqa: E402

ALLOWED_PREFIXES = ("examples/connectors/h7_library_research/replay_results",)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-id", choices=H7_SOURCE_IDS)
    parser.add_argument("--fixture-root", default="examples/connectors/h7_library_research/fixtures")
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
                parts = str(result.get("fixture_ref", "fixture")).split(".")
                kind = parts[-2] if len(parts) > 2 else "fixture"
                (output_dir / f"{result['source_id']}_{kind}_replay_result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        summary = {
            "schema_version": "h7_library_research_fixture_replay_summary.v0",
            "status": "pass",
            "source_count": len(sorted({item["source_id"] for item in results})),
            "fixture_replay_count": len(results),
            "network_calls_made": False,
            "harvest_query_fetch_download_used": False,
            "restricted_source_access_used": False,
            "results": results,
        }
        if args.json:
            print(json.dumps(summary, indent=2, sort_keys=True), file=stdout)
        else:
            print("H7 library/cultural/research fixture replay", file=stdout)
            print("status: pass", file=stdout)
            print(f"source_count: {summary['source_count']}", file=stdout)
            print(f"fixture_replay_count: {summary['fixture_replay_count']}", file=stdout)
            print("network_used: false", file=stdout)
            print("harvest_query_fetch_download_used: false", file=stdout)
        return 0
    except Exception as exc:  # noqa: BLE001
        if args.json:
            print(json.dumps({"status": "invalid", "error": str(exc)}, indent=2, sort_keys=True), file=stdout)
        else:
            print("H7 library/cultural/research fixture replay", file=stdout)
            print("status: invalid", file=stdout)
            print(f"ERROR: {exc}", file=stdout)
        return 1


def replay_fixtures(fixture_root: str | Path, source_id: str | None = None) -> list[dict[str, Any]]:
    root = Path(fixture_root)
    if not root.is_absolute():
        root = REPO_ROOT / root
    results: list[dict[str, Any]] = []
    for item in ([source_id] if source_id else list(H7_SOURCE_IDS)):
        assert item is not None
        source_dir = root / item
        if not source_dir.is_dir():
            raise ValueError(f"missing fixture directory: {source_dir}")
        module = importlib.import_module(f"control.prototypes.legacy_runtime.connectors.h7_library_research.{item}")
        for fixture_path in sorted(source_dir.glob("*.json")):
            fixture = load_h7_library_research_fixture(fixture_path)
            normalized = module.normalize(fixture)
            results.append(build_h7_fixture_replay_result(fixture, normalized))
    return results


if __name__ == "__main__":
    raise SystemExit(main())
