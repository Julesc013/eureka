#!/usr/bin/env python3
"""Check a public alpha deployment plan remains planning-only."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.validate_public_alpha_deployment_plan import detect_forbidden_deployment_claims


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default="examples/hosting/deployment/public_alpha_deployment_plan_v0.json")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    payload = _load(args.input)
    errors = check_plan(payload)
    result = {"schema_version": "public_alpha_deployment_plan_check.v0", "status": "fail" if errors else "pass", "errors": errors}
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    elif args.check:
        print(f"Public alpha deployment plan check status: {result['status']}")
    else:
        print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "pass" else 1


def check_plan(payload: dict[str, Any]) -> list[str]:
    errors = detect_forbidden_deployment_claims(payload, "plan")
    if payload.get("plan_status") not in {"planning_only", "operator_review_required", "blocked"}:
        errors.append("plan status must remain current planning-only/operator-gated.")
    for step in payload.get("deployment_steps", []):
        if step.get("external_provider_action") is not False:
            errors.append(f"{step.get('step_id')}: external provider action must be false current.")
        if step.get("secret_required") is not False:
            errors.append(f"{step.get('step_id')}: secret_required must be false current.")
    return errors


def _load(value: str) -> dict[str, Any]:
    path = Path(value)
    if not path.is_absolute():
        path = REPO_ROOT / path
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    raise SystemExit(main())
