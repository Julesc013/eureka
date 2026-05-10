#!/usr/bin/env python3
"""Audit public alpha readiness evidence without deploying."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.hosting.readiness import validate_public_launch_readiness_audit
from scripts.validate_hosted_wrapper_rehearsal import validate_output_path, write_json_output


def build_audit() -> dict:
    audit = json.loads((REPO_ROOT / "examples/hosting/launch/public_launch_readiness_audit_v0.json").read_text(encoding="utf-8"))
    validation = validate_public_launch_readiness_audit(audit, {})
    return {
        "schema_version": "public_alpha_readiness_audit_result.v0",
        "status": validation["status"],
        "readiness_status": audit.get("readiness_status"),
        "next_phase": "READY_FOR_MVP_ALPHA_AUDIT" if validation["status"] == "pass" else "NEEDS_REMEDIATION",
        "operator_signoff_required": audit.get("operator_signoff_required"),
        "deployment_performed": False,
        "provider_api_called": False,
        "dns_changed": False,
        "site_dist_mutated": False,
        "errors": validation["errors"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json-output")
    parser.add_argument("--summary-output")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = build_audit()
    if args.json_output:
        write_json_output(validate_output_path(args.json_output), report)
    if args.summary_output:
        validate_output_path(args.summary_output).write_text(f"Public alpha readiness: {report['status']}\nNext phase: {report['next_phase']}\n", encoding="utf-8")
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(f"Public alpha readiness audit status: {report['status']}")
        print(f"Next phase: {report['next_phase']}")
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
