#!/usr/bin/env python3
"""Check that local MVP iteration keeps deployment deferred."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.validate_local_mvp_iteration import detect_forbidden_local_mvp_claims, load_json


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default="examples/audits/local_mvp/local_mvp_deployment_deferral_v0.json")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    report = check_deferral(load_json(_resolve(args.input)), args.input)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    elif args.check:
        print(f"Local MVP deployment deferral status: {report['status']}")
    else:
        print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "pass" else 1


def check_deferral(payload: dict, source: str = "inline") -> dict:
    errors = detect_forbidden_local_mvp_claims(payload, source)
    if payload.get("deployment_deferred") is not True:
        errors.append("deployment_deferred must be true.")
    if payload.get("operator_signoff_present") is not False:
        errors.append("operator_signoff_present must be false.")
    if payload.get("deployment_approval_present") is not False:
        errors.append("deployment_approval_present must be false.")
    return {
        "schema_version": "local_mvp_deployment_deferral_check.v0",
        "status": "fail" if errors else "pass",
        "source": source,
        "deployment_deferred": payload.get("deployment_deferred"),
        "operator_deployment_approval_present": payload.get("deployment_approval_present"),
        "deployment_allowed_current": False,
        "launch_allowed_current": False,
        "errors": errors,
    }


def _resolve(raw: str) -> Path:
    path = Path(raw)
    if not path.is_absolute():
        path = REPO_ROOT / path
    return path


if __name__ == "__main__":
    raise SystemExit(main())
