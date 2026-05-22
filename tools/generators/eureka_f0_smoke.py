#!/usr/bin/env python3
"""Run the F0 fixture-only manifest smoke path."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Sequence, TextIO

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.extraction_safe_fixtures import (  # noqa: E402
    PROJECTION_PROFILES,
    build_container_descriptor_from_fixture,
    build_extraction_console_view,
    build_member_manifest,
    load_f0_fixture_manifest,
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture-manifest", default="examples/f0/f0_fixture_manifest.json")
    parser.add_argument("--projection", choices=PROJECTION_PROFILES, default="operator_workbench")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--repo-root", default=str(REPO_ROOT), help=argparse.SUPPRESS)
    args = parser.parse_args(argv)

    root = Path(args.repo_root).resolve()
    manifest = load_f0_fixture_manifest(root / args.fixture_manifest)
    fixture = next(item for item in manifest["fixtures"] if item["fixture_id"] == "safe_zip_basic")
    descriptor = build_container_descriptor_from_fixture(fixture["container_descriptor"])
    member_manifest = build_member_manifest(descriptor)
    view = build_extraction_console_view(member_manifest, args.projection)
    result = {
        "schema_version": "f0_smoke_result.v0",
        "status": "pass",
        "projection_profile": args.projection,
        "manifest_id": member_manifest["manifest_id"],
        "member_count": member_manifest["member_count"],
        "blocked_member_count": member_manifest["risk_report"]["blocked_member_count"],
        "read_only": view["read_only"],
        "manifest_only": True,
        "filesystem_extraction_performed": False,
        "execution_performed": False,
        "view": view,
    }
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    else:
        print("F0 smoke", file=stdout)
        print(f"status: {result['status']}", file=stdout)
        print(f"projection_profile: {args.projection}", file=stdout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
