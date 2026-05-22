#!/usr/bin/env python3
"""Replay committed H10 games/emulation fixtures offline."""

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

from archive.prototypes.legacy_runtime.connectors.h10_games_emulation.fixture_loader import load_h10_games_emulation_fixture  # noqa: E402
from archive.prototypes.legacy_runtime.connectors.h10_games_emulation.normalizer_common import H10_SOURCE_IDS, build_h10_fixture_replay_result  # noqa: E402
from scripts.normalize_h10_games_emulation_fixture import safe_output_path  # noqa: E402

ALLOWED_PREFIXES = ("examples/connectors/h10_games_emulation/replay_results", "control/audits/h10-bundle-02-games-emulation-fixture-runtime-v0/generated")


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-id", choices=H10_SOURCE_IDS)
    parser.add_argument("--fixture-root", default="examples/connectors/h10_games_emulation/fixtures")
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
                kind = result.get("fixture_kind", "fixture")
                (output_dir / f"{result['source_id']}_{kind}_replay_result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        summary = {
            "schema_version": "h10_games_emulation_fixture_replay_summary.v0",
            "status": "pass",
            "source_count": len(sorted({item["source_id"] for item in results})),
            "fixture_replay_count": len(results),
            "network_calls_made": False,
            "download_upload_execute_acquire_used": False,
            "restricted_source_access_used": False,
            "results": results,
        }
        if args.json:
            print(json.dumps(summary, indent=2, sort_keys=True), file=stdout)
        else:
            print("H10 games/emulation fixture replay", file=stdout)
            print("status: pass", file=stdout)
            print(f"source_count: {summary['source_count']}", file=stdout)
            print(f"fixture_replay_count: {summary['fixture_replay_count']}", file=stdout)
            print("network_used: false", file=stdout)
            print("download_upload_execute_acquire_used: false", file=stdout)
        return 0
    except Exception as exc:  # noqa: BLE001
        if args.json:
            print(json.dumps({"status": "invalid", "error": str(exc)}, indent=2, sort_keys=True), file=stdout)
        else:
            print("H10 games/emulation fixture replay", file=stdout)
            print("status: invalid", file=stdout)
            print(f"ERROR: {exc}", file=stdout)
        return 1


def replay_fixtures(fixture_root: str | Path, source_id: str | None = None) -> list[dict[str, Any]]:
    root = Path(fixture_root)
    if not root.is_absolute():
        root = REPO_ROOT / root
    results: list[dict[str, Any]] = []
    for item in ([source_id] if source_id else list(H10_SOURCE_IDS)):
        assert item is not None
        source_dir = root / item
        if not source_dir.is_dir():
            raise ValueError(f"missing fixture directory: {source_dir}")
        module = importlib.import_module(f"archive.prototypes.legacy_runtime.connectors.h10_games_emulation.{item}")
        for fixture_path in sorted(source_dir.glob("*.json")):
            fixture = load_h10_games_emulation_fixture(fixture_path)
            normalized = module.normalize(fixture)
            results.append(build_h10_fixture_replay_result(fixture, normalized))
    return results


if __name__ == "__main__":
    raise SystemExit(main())
