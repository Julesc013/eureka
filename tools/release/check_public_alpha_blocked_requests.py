#!/usr/bin/env python3
"""Validate public alpha blocked request reports."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.hosting.blocked_requests import validate_blocked_request_report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default="examples/hosting/blocked_requests")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    root = REPO_ROOT / args.input
    files = sorted(root.rglob("*.json")) if root.is_dir() else [root]
    errors: list[str] = []
    for path in files:
        payload = json.loads(path.read_text(encoding="utf-8"))
        report = validate_blocked_request_report(payload, {})
        errors.extend(f"{path.relative_to(REPO_ROOT).as_posix()}: {error}" for error in report["errors"])
    result = {"schema_version": "public_alpha_blocked_request_check.v0", "status": "fail" if errors else "pass", "checked": len(files), "errors": errors}
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"Public alpha blocked requests status: {result['status']}")
        for error in errors:
            print(f"ERROR: {error}")
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
