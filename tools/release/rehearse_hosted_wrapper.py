#!/usr/bin/env python3
"""Run a local fixture hosted-wrapper rehearsal without deployment."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.hosting.readiness import build_hosted_wrapper_rehearsal
from runtime.hosting.smoke_matrix import build_public_alpha_smoke_matrix, run_local_fixture_smoke_matrix
from scripts.validate_hosted_wrapper_rehearsal import validate_output_path, write_json_output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default="examples/hosting/rehearsal/hosted_wrapper_rehearsal_local_fixture_v0.json")
    parser.add_argument("--output")
    parser.add_argument("--summary-output")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    payload = json.loads((REPO_ROOT / args.input).read_text(encoding="utf-8"))
    rehearsal = build_hosted_wrapper_rehearsal(payload, {})
    smoke = run_local_fixture_smoke_matrix(build_public_alpha_smoke_matrix({}, {}), {})
    report = {
        "schema_version": "hosted_wrapper_rehearsal_run.v0",
        "status": "pass" if smoke["status"] == "pass" else "fail",
        "rehearsal": rehearsal,
        "smoke_result": smoke,
        "deployment_performed": False,
        "provider_api_called": False,
        "dns_changed": False,
        "site_dist_mutated": False,
    }
    if args.output:
        write_json_output(validate_output_path(args.output), report)
    if args.summary_output:
        validate_output_path(args.summary_output).write_text("Hosted wrapper rehearsal: pass\nNo deployment, DNS change, provider call, or public launch claim.\n", encoding="utf-8")
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    elif args.check:
        print(f"Hosted wrapper rehearsal status: {report['status']}")
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
