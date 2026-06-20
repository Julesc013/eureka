#!/usr/bin/env python
"""Validate live discovery stack audit artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
AUDIT_ROOT = REPO_ROOT / "control" / "audits" / "e2e_reference_system" / "live_discovery_stack_audit_v1"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    payload = validate()
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(f"status: {payload['status']}")
    return 0 if payload["status"] in {"pass", "pass_with_warnings"} else 1


def validate() -> dict[str, object]:
    required = [
        "README.md",
        "AUDIT_REPORT.md",
        "findings.json",
        "performance_baseline.json",
        "security_matrix.json",
        "retention_matrix.json",
        "remaining_risks.md",
    ]
    missing = [name for name in required if not (AUDIT_ROOT / name).is_file()]
    errors: list[str] = []
    findings = _load_json("findings.json", errors)
    security = _load_json("security_matrix.json", errors)
    retention = _load_json("retention_matrix.json", errors)
    performance = _load_json("performance_baseline.json", errors)
    critical = int(findings.get("critical_count") or 0)
    high = int(findings.get("high_count") or 0)
    if critical or high:
        errors.append("critical_or_high_findings_present")
    if retention.get("provider_result_payload_persisted") is not False:
        errors.append("provider payload retention violation")
    if retention.get("api_key_persisted") is not False:
        errors.append("API key retention violation")
    if security.get("high_findings") not in {0, "0"}:
        errors.append("security high findings present")
    if performance.get("production_scale_claimed") is not False:
        errors.append("production scale claim present")
    return {
        "schema_version": "eureka.live_discovery_stack_audit_validation.v1",
        "status": "fail" if missing or errors else "pass_with_warnings",
        "audit_root": str(AUDIT_ROOT),
        "missing": missing,
        "errors": errors,
        "critical_findings": critical,
        "high_findings": high,
        "medium_findings": int(findings.get("medium_count") or 0),
        "provider_result_payload_persisted": retention.get("provider_result_payload_persisted"),
        "production_scale_claimed": performance.get("production_scale_claimed"),
    }


def _load_json(name: str, errors: list[str]) -> dict[str, object]:
    try:
        return json.loads((AUDIT_ROOT / name).read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"{name}: {type(exc).__name__}")
        return {}


if __name__ == "__main__":
    raise SystemExit(main())
