#!/usr/bin/env python3
"""Replay committed Internet Archive metadata fixtures with no live calls."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence, TextIO

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.source.observation.internet_archive_fixture_replay import (
    assert_no_forbidden_side_effects,
    assert_no_network_imports,
    build_fixture_replay_report,
    replay_fixture,
    replay_fixture_directory,
)


DEFAULT_FIXTURE_DIR = Path("examples/internet_archive_metadata")


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--fixture", help="Replay one committed IA metadata fixture.")
    source.add_argument("--fixture-dir", default=str(DEFAULT_FIXTURE_DIR), help="Replay a committed IA metadata fixture directory.")
    parser.add_argument("--json", action="store_true", help="Emit JSON.")
    parser.add_argument("--output", help="Optional path for the full replay report.")
    parser.add_argument("--boundary-output", help="Optional path for boundary reports only.")
    args = parser.parse_args(argv)

    assert_no_network_imports()
    if args.fixture:
        fixture_results = [replay_fixture(args.fixture)]
    else:
        fixture_results = replay_fixture_directory(args.fixture_dir)
    report = build_fixture_replay_report(fixture_results)
    assert_no_forbidden_side_effects(report)

    if args.output:
        Path(args.output).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.boundary_output:
        Path(args.boundary_output).write_text(
            json.dumps(report["boundary_reports"], indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True), file=stdout)
    else:
        print("IA fixture replay", file=stdout)
        print(f"status: {'PASS' if report['all_fixtures_replay'] else 'FAIL'}", file=stdout)
        print(f"fixture_count: {report['fixture_count']}", file=stdout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
