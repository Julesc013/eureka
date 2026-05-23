#!/usr/bin/env python3
"""Run a deterministic G0 smoke over fixture scoring and console projection."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Sequence, TextIO

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.local.eval.g0_quality import PROJECTION_PROFILES, build_quality_console_view, load_quality_fixture  # noqa: E402


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", default="examples/search/quality/sample_quality_fixture.json")
    parser.add_argument("--projection", choices=PROJECTION_PROFILES, default="operator_workbench")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    view = build_quality_console_view(load_quality_fixture(args.fixture), args.projection)
    payload = {
        "schema_version": "g0_smoke_result.v0",
        "status": "pass",
        "projection_profile": args.projection,
        "read_only": view["read_only"],
        "score_count": view["views"]["QualityOverviewView"]["score_count"],
        "explanation_count": view["views"]["QualityOverviewView"]["explanation_count"],
        "accepted_truth": False,
        "model_provider_used": False,
    }
    print(json.dumps(payload, indent=2, sort_keys=True) if args.json else f"G0 smoke {payload['status']}", file=stdout)
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
