#!/usr/bin/env python3
"""Check public alpha DNS readiness without querying DNS."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.validate_public_alpha_deployment_plan import detect_forbidden_deployment_claims


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default="examples/hosting/deployment/public_alpha_dns_readiness_unknown_v0.json")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    payload = _load(args.input)
    errors = check_dns_readiness(payload)
    result = {"schema_version": "public_alpha_dns_readiness_check.v0", "status": "fail" if errors else "pass", "errors": errors}
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    elif args.check:
        print(f"Public alpha DNS readiness check status: {result['status']}")
    else:
        print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "pass" else 1


def check_dns_readiness(payload: dict) -> list[str]:
    errors = detect_forbidden_deployment_claims(payload, "dns")
    if payload.get("custom_domain_status") == "configured_future":
        errors.append("configured DNS cannot be claimed in this planning bundle.")
    if payload.get("current_records_known") is not False:
        errors.append("current_records_known must be false without committed evidence.")
    if payload.get("verification_evidence_refs"):
        errors.append("verification evidence must be absent for unknown DNS readiness.")
    return errors


def _load(value: str) -> dict:
    path = Path(value)
    if not path.is_absolute():
        path = REPO_ROOT / path
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    raise SystemExit(main())
