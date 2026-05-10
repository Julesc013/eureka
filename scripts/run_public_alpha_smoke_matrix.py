#!/usr/bin/env python3
"""Run public alpha smoke matrix against local fixtures only."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.hosting.smoke_matrix import run_local_fixture_smoke_matrix
from scripts.validate_hosted_wrapper_rehearsal import validate_output_path, write_json_output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--matrix", default="examples/hosting/smoke/public_alpha_smoke_matrix_v0.json")
    parser.add_argument("--output")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    matrix = json.loads((REPO_ROOT / args.matrix).read_text(encoding="utf-8"))
    report = run_local_fixture_smoke_matrix(matrix, {})
    if args.output:
        write_json_output(validate_output_path(args.output), report)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    elif args.check:
        print(f"Public alpha smoke matrix status: {report['status']}")
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
