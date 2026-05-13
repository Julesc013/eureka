#!/usr/bin/env python3
"""Replay committed H14 Source OS rollup fixtures offline."""

from __future__ import annotations

import argparse
import importlib
import json
from pathlib import Path
import sys
from typing import Sequence, TextIO

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from control.prototypes.legacy_runtime.connectors.h14_source_discovery.fixture_loader import load_h14_source_discovery_fixture  # noqa: E402
from control.prototypes.legacy_runtime.connectors.h14_source_discovery.normalizer_common import H14_FIXTURE_FILES, H14_SOURCE_IDS, build_h14_fixture_replay_result  # noqa: E402
from scripts.normalize_h14_source_discovery_fixture import SOURCE_MODULES, safe_output_path  # noqa: E402

SAFE_FIXTURE_ROOT = (REPO_ROOT / "examples/connectors/h14_source_discovery/fixtures").resolve()


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-id", choices=H14_SOURCE_IDS)
    parser.add_argument("--fixture-root", default="examples/connectors/h14_source_discovery/fixtures")
    parser.add_argument("--output-dir")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        fixture_root = safe_fixture_root(args.fixture_root)
        source_ids = [args.source_id] if args.source_id else list(H14_SOURCE_IDS)
        results = []
        normalized_count = 0
        for source_id in source_ids:
            module = importlib.import_module(f"control.prototypes.legacy_runtime.connectors.h14_source_discovery.{SOURCE_MODULES[source_id]}")
            source_dir = fixture_root / source_id
            representative = None
            representative_replay = None
            for kind, filename in H14_FIXTURE_FILES.items():
                fixture = load_h14_source_discovery_fixture(source_dir / filename)
                normalized = module.normalize(fixture)
                replay = build_h14_fixture_replay_result(fixture, normalized)
                normalized_count += 1
                results.append(replay)
                if representative is None:
                    representative = normalized
                    representative_replay = replay
            if args.output_dir and not args.check:
                out_dir = safe_output_path(Path(args.output_dir) / source_id)
                out_dir.mkdir(parents=True, exist_ok=True)
                (out_dir / "normalized_record.json").write_text(json.dumps(representative, indent=2, sort_keys=True) + "\n", encoding="utf-8")
                (out_dir / "replay_result.json").write_text(json.dumps(representative_replay, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        summary = {
            "schema_version": "h14_source_discovery_fixture_replay_summary.v0",
            "status": "pass",
            "source_count": len(source_ids),
            "fixture_count": normalized_count,
            "result_count": len(results),
            "source_discovery_runtime_used": False,
            "network_used": False,
            "pack_export_import_used": False,
            "registry_mutation_used": False,
            "public_index_mutated": False,
            "master_index_mutated": False,
            "wrote_files": bool(args.output_dir and not args.check),
        }
        if args.json:
            print(json.dumps(summary, indent=2, sort_keys=True), file=stdout)
        else:
            print("H14 source discovery fixture replay", file=stdout)
            print(f"status: {summary['status']}", file=stdout)
            print(f"source_count: {summary['source_count']}", file=stdout)
            print(f"fixture_count: {summary['fixture_count']}", file=stdout)
            print("source_discovery_runtime_used: false", file=stdout)
            print("pack_export_import_used: false", file=stdout)
        return 0
    except Exception as exc:  # noqa: BLE001
        if args.json:
            print(json.dumps({"status": "invalid", "error": str(exc)}, indent=2, sort_keys=True), file=stdout)
        else:
            print("H14 source discovery fixture replay", file=stdout)
            print("status: invalid", file=stdout)
            print(f"ERROR: {exc}", file=stdout)
        return 1


def safe_fixture_root(raw: str | Path) -> Path:
    path = Path(raw)
    if not path.is_absolute():
        path = REPO_ROOT / path
    resolved = path.resolve()
    try:
        resolved.relative_to(SAFE_FIXTURE_ROOT)
    except ValueError as exc:
        raise ValueError("fixture root must be under committed H14 fixture root") from exc
    return resolved


if __name__ == "__main__":
    raise SystemExit(main())
