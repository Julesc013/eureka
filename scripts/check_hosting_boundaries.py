#!/usr/bin/env python3
"""Check hosting boundaries without calling providers or deploying."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from validate_hosting_readiness import REPO_ROOT, detect_forbidden_hosting_claims, validate_hosting_readiness
except ModuleNotFoundError:  # pragma: no cover
    from scripts.validate_hosting_readiness import REPO_ROOT, detect_forbidden_hosting_claims, validate_hosting_readiness


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    errors: list[str] = []
    validation = validate_hosting_readiness(REPO_ROOT)
    errors.extend(validation["errors"])
    for root in (REPO_ROOT / "examples" / "hosting", REPO_ROOT / "control" / "audits" / "e-bundle-01-hosting-ops-readiness-v0"):
        for path in sorted(root.rglob("*.json")) if root.exists() else []:
            payload = json.loads(path.read_text(encoding="utf-8"))
            errors.extend(detect_forbidden_hosting_claims(payload, path.relative_to(REPO_ROOT).as_posix()))
    for private_root in (".aide.local", ".local/eureka", ".cache/eureka"):
        if (REPO_ROOT / private_root).exists():
            errors.append(f"{private_root}: private root must not exist.")
    report = {
        "schema_version": "hosting_boundary_check.v0",
        "status": "fail" if errors else "pass",
        "provider_api_called": False,
        "deployment_performed": False,
        "dns_changed": False,
        "errors": errors,
    }
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(f"Hosting boundary check\nstatus: {report['status']}")
        for error in errors:
            print(f"ERROR: {error}")
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
