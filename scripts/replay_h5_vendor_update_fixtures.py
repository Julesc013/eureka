#!/usr/bin/env python3
"""Replay committed H5 vendor/update fixtures offline."""

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

from control.prototypes.legacy_runtime.connectors.h5_vendor_update_driver.fixture_loader import load_h5_vendor_update_fixture  # noqa: E402
from control.prototypes.legacy_runtime.connectors.h5_vendor_update_driver.normalizer_common import H5_SOURCE_IDS, build_h5_fixture_replay_result  # noqa: E402


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
    "vendor_downloads",
    "firmware_staging",
    "package_cache",
    "data/package_cache",
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
        raise ValueError(f"refusing output outside approved H5 fixture roots: {rel}")
    except ValueError as exc:
        if str(exc).startswith("refusing"):
            raise
        temp_root = Path(tempfile.gettempdir()).resolve()
        try:
            resolved.relative_to(temp_root)
            return resolved
        except ValueError as temp_exc:
            raise ValueError(f"refusing output outside approved roots or temp directory: {resolved}") from temp_exc


ALLOWED_PREFIXES = ("examples/connectors/h5_vendor_update_driver/replay_results",)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-id", choices=H5_SOURCE_IDS)
    parser.add_argument("--fixture-root", default="examples/connectors/h5_vendor_update_driver/fixtures")
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
            "schema_version": "h5_vendor_update_fixture_replay_summary.v0",
            "status": "pass",
            "source_count": len(sorted({item["source_id"] for item in results})),
            "fixture_replay_count": len(results),
            "network_calls_made": False,
            "vendor_catalog_fetches_made": False,
            "downloads_made": False,
            "vendor_tools_invoked": False,
            "firmware_flashes_made": False,
            "results": results,
        }
        if args.json:
            print(json.dumps(summary, indent=2, sort_keys=True), file=stdout)
        else:
            print("H5 vendor/update fixture replay", file=stdout)
            print("status: pass", file=stdout)
            print(f"source_count: {summary['source_count']}", file=stdout)
            print(f"fixture_replay_count: {summary['fixture_replay_count']}", file=stdout)
            print("network_used: false", file=stdout)
            print("downloads_used: false", file=stdout)
            print("firmware_flash_used: false", file=stdout)
        return 0
    except Exception as exc:  # noqa: BLE001
        if args.json:
            print(json.dumps({"status": "invalid", "error": str(exc)}, indent=2, sort_keys=True), file=stdout)
        else:
            print("H5 vendor/update fixture replay", file=stdout)
            print("status: invalid", file=stdout)
            print(f"ERROR: {exc}", file=stdout)
        return 1


def replay_fixtures(fixture_root: str | Path, source_id: str | None = None) -> list[dict[str, Any]]:
    root = Path(fixture_root)
    if not root.is_absolute():
        root = REPO_ROOT / root
    results: list[dict[str, Any]] = []
    for item in ([source_id] if source_id else list(H5_SOURCE_IDS)):
        assert item is not None
        source_dir = root / item
        if not source_dir.is_dir():
            raise ValueError(f"missing fixture directory: {source_dir}")
        module = importlib.import_module(f"control.prototypes.legacy_runtime.connectors.h5_vendor_update_driver.{item}")
        for fixture_path in sorted(source_dir.glob("*.json")):
            fixture = load_h5_vendor_update_fixture(fixture_path)
            normalized = module.normalize(fixture)
            results.append(build_h5_fixture_replay_result(fixture, normalized))
    return results


if __name__ == "__main__":
    raise SystemExit(main())
