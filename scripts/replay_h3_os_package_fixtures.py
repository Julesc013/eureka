#!/usr/bin/env python3
"""Replay committed H3 OS package archive fixtures offline."""

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

from runtime.connectors.h3_os_package_archives.fixture_loader import load_h3_os_package_fixture  # noqa: E402
from runtime.connectors.h3_os_package_archives.normalizer_common import H3_SOURCE_IDS, build_h3_fixture_replay_result  # noqa: E402


FORBIDDEN_OUTPUT_ROOTS = (
    "site/dist",
    "data/public_index",
    "runtime",
    "contracts",
    "data/master_index",
    "master_index",
    "control/inventory/publication",
    "control/inventory/sources",
    "package_cache",
    "data/package_cache",
    ".aide.local",
    ".local/eureka",
    ".cache/eureka",
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-id", choices=H3_SOURCE_IDS)
    parser.add_argument("--fixture-root", default="examples/connectors/h3_os_package_archives/fixtures")
    parser.add_argument("--output-dir", help="Optional output directory for replay results.")
    parser.add_argument("--check", action="store_true", help="Replay without writing files.")
    parser.add_argument("--json", action="store_true", help="Print JSON replay summary.")
    args = parser.parse_args(argv)
    try:
        results = replay_fixtures(args.fixture_root, args.source_id)
        summary = {
            "schema_version": "h3_os_package_fixture_replay_summary.v0",
            "status": "pass",
            "source_count": len(sorted({item["source_id"] for item in results})),
            "fixture_replay_count": len(results),
            "network_calls_made": False,
            "live_source_calls_made": False,
            "repository_index_fetches_made": False,
            "package_downloads_made": False,
            "package_manager_invocations_made": False,
            "results": results,
        }
        if args.output_dir and not args.check:
            output_dir = _safe_output_dir(Path(args.output_dir))
            output_dir.mkdir(parents=True, exist_ok=True)
            for result in results:
                source_id = str(result["source_id"])
                fixture_parts = str(result["fixture_id"]).split(".")
                fixture_kind = fixture_parts[-2] if len(fixture_parts) > 2 else "fixture"
                out = output_dir / f"{source_id}_{fixture_kind}_replay_result.json"
                out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        if args.json:
            print(json.dumps(summary, indent=2, sort_keys=True), file=stdout)
        else:
            print("H3 OS package fixture replay", file=stdout)
            print("status: pass", file=stdout)
            print(f"source_count: {summary['source_count']}", file=stdout)
            print(f"fixture_replay_count: {summary['fixture_replay_count']}", file=stdout)
            print("network_used: false", file=stdout)
            print("repository_index_fetch_used: false", file=stdout)
            print("package_download_used: false", file=stdout)
        return 0
    except Exception as exc:  # noqa: BLE001
        if args.json:
            print(json.dumps({"status": "invalid", "error": str(exc)}, indent=2, sort_keys=True), file=stdout)
        else:
            print("H3 OS package fixture replay", file=stdout)
            print("status: invalid", file=stdout)
            print(f"ERROR: {exc}", file=stdout)
        return 1


def replay_fixtures(fixture_root: str | Path, source_id: str | None = None) -> list[dict[str, Any]]:
    root = _repo_path(fixture_root)
    source_ids = [source_id] if source_id else list(H3_SOURCE_IDS)
    results: list[dict[str, Any]] = []
    for item in source_ids:
        normalizer = _normalizer(str(item))
        source_dir = root / str(item)
        if not source_dir.is_dir():
            raise ValueError(f"missing fixture directory: {source_dir}")
        for fixture_path in sorted(source_dir.glob("*.json")):
            fixture = load_h3_os_package_fixture(fixture_path)
            normalized = normalizer(fixture)
            results.append(build_h3_fixture_replay_result(fixture, normalized))
    return results


def _normalizer(source_id: str):
    module = importlib.import_module(f"runtime.connectors.h3_os_package_archives.{source_id}")
    return module.normalize


def _repo_path(path_text: str | Path) -> Path:
    path = Path(path_text)
    return path if path.is_absolute() else REPO_ROOT / path


def _safe_output_dir(path: Path) -> Path:
    resolved = (REPO_ROOT / path).resolve() if not path.is_absolute() else path.resolve()
    repo_resolved = REPO_ROOT.resolve()
    try:
        rel = resolved.relative_to(repo_resolved).as_posix()
        rel_lower = rel.casefold()
        for forbidden in FORBIDDEN_OUTPUT_ROOTS:
            forbidden_lower = forbidden.casefold().rstrip("/")
            if rel_lower == forbidden_lower or rel_lower.startswith(forbidden_lower + "/"):
                raise ValueError(f"refusing forbidden output root: {forbidden}")
        if rel_lower.startswith("control/audits/") and rel_lower.endswith("/generated"):
            return resolved
        if rel_lower.startswith("examples/connectors/h3_os_package_archives/replay_results"):
            return resolved
        raise ValueError(f"refusing output outside approved H3 replay roots: {rel}")
    except ValueError as exc:
        if str(exc).startswith("refusing"):
            raise
        temp_root = Path(tempfile.gettempdir()).resolve()
        try:
            resolved.relative_to(temp_root)
            return resolved
        except ValueError as temp_exc:
            raise ValueError(f"refusing output outside approved roots or temp directory: {resolved}") from temp_exc


if __name__ == "__main__":
    raise SystemExit(main())
