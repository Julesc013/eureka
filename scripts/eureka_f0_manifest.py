#!/usr/bin/env python3
"""Build a fixture-only F0 member manifest without extracting files."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence, TextIO

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.extraction_safe_fixtures import (  # noqa: E402
    build_container_descriptor_from_fixture,
    build_extraction_boundary_report,
    build_member_manifest,
    load_f0_fixture_manifest,
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture-manifest", default="examples/f0/f0_fixture_manifest.json")
    parser.add_argument("--zip", dest="zip_path", help="Optional explicit safe ZIP fixture path.")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--output", help="Optional member manifest output path.")
    parser.add_argument("--boundary-output", help="Optional boundary report output path.")
    parser.add_argument("--repo-root", default=str(REPO_ROOT), help=argparse.SUPPRESS)
    args = parser.parse_args(argv)

    root = Path(args.repo_root).resolve()
    manifest_path = _resolve(root, args.fixture_manifest)
    fixture_manifest = load_f0_fixture_manifest(manifest_path)
    descriptor = _select_descriptor(root, fixture_manifest, args.zip_path)
    member_manifest = build_member_manifest(descriptor)
    boundary_report = build_extraction_boundary_report(member_manifest)

    if args.output:
        _write_json(root, args.output, member_manifest)
    if args.boundary_output:
        _write_json(root, args.boundary_output, boundary_report)

    if args.json:
        print(json.dumps(member_manifest, indent=2, sort_keys=True), file=stdout)
    else:
        print("F0 member manifest", file=stdout)
        print(f"manifest_id: {member_manifest['manifest_id']}", file=stdout)
        print(f"member_count: {member_manifest['member_count']}", file=stdout)
        print(f"blocked_member_count: {member_manifest['risk_report']['blocked_member_count']}", file=stdout)
    return 0


def _select_descriptor(root: Path, fixture_manifest: Mapping[str, Any], zip_path: str | None) -> dict[str, Any]:
    if zip_path:
        return build_container_descriptor_from_fixture(_resolve(root, zip_path))
    fixtures = [item for item in fixture_manifest.get("fixtures", []) if isinstance(item, Mapping)]
    for item in fixtures:
        if item.get("fixture_id") == "safe_zip_basic":
            descriptor = dict(item.get("container_descriptor", {}))
            if descriptor.get("locator"):
                descriptor["locator"] = str(_resolve(root, str(descriptor["locator"])).relative_to(root))
            return build_container_descriptor_from_fixture(descriptor)
    raise ValueError("safe_zip_basic fixture descriptor is missing")


def _write_json(root: Path, path_text: str, payload: Mapping[str, Any]) -> None:
    path = _resolve(root, path_text)
    forbidden = ("site/dist", "data/public_index", "runtime/extraction", "eureka-instance", "instances", "secrets", ".aide.local")
    rel = path.relative_to(root).as_posix() if path.is_relative_to(root) else path.as_posix()
    if any(rel == prefix or rel.startswith(prefix + "/") for prefix in forbidden):
        raise ValueError(f"refusing forbidden output root: {rel}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _resolve(root: Path, path_text: str | Path) -> Path:
    path = Path(path_text)
    if not path.is_absolute():
        path = root / path
    return path.resolve()


if __name__ == "__main__":
    raise SystemExit(main())
