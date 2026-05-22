#!/usr/bin/env python3
"""Check public-alpha non-claims and forbidden positive hosting claims."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from validate_hosting_readiness import REPO_ROOT, REQUIRED_NON_CLAIMS, detect_forbidden_hosting_claims
except ModuleNotFoundError:  # pragma: no cover
    from scripts.validate_hosting_readiness import REPO_ROOT, REQUIRED_NON_CLAIMS, detect_forbidden_hosting_claims


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default="examples/hosting/public_alpha_non_claims_v0.json")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    path = Path(args.input)
    if not path.is_absolute():
        path = REPO_ROOT / path
    errors: list[str] = []
    payload = json.loads(path.read_text(encoding="utf-8"))
    for key in REQUIRED_NON_CLAIMS:
        if payload.get(key) is not True:
            errors.append(f"{key} must be true.")
    errors.extend(detect_forbidden_hosting_claims(payload, args.input))
    for doc in ("docs/operations/PUBLIC_ALPHA_NON_CLAIMS.md", "docs/reference/PUBLIC_ALPHA_NON_CLAIMS_CONTRACT.md"):
        if not (REPO_ROOT / doc).is_file():
            errors.append(f"{doc}: missing non-claims doc.")
    report = {"schema_version": "public_alpha_non_claims_check.v0", "status": "fail" if errors else "pass", "errors": errors}
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(f"Public alpha non-claims check\nstatus: {report['status']}")
        for error in errors:
            print(f"ERROR: {error}")
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
