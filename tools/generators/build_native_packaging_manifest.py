#!/usr/bin/env python3
"""Build native packaging manifest previews without creating binaries."""

from __future__ import annotations

import argparse
import json

try:
    from validate_native_packaging_manifests import build_native_packaging_manifest, validate_output_path, write_json_output
except ModuleNotFoundError:  # pragma: no cover - package import path for tests.
    from scripts.validate_native_packaging_manifests import build_native_packaging_manifest, validate_output_path, write_json_output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lane", default="win.winforms")
    parser.add_argument("--output")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    manifest = build_native_packaging_manifest(args.lane)
    if args.output:
        write_json_output(validate_output_path(args.output), manifest)
    if args.json:
        print(json.dumps(manifest, indent=2, sort_keys=True))
    else:
        print(f"Native packaging manifest\nstatus: {manifest['packaging_status']}\nlane_id: {manifest['lane_id']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
