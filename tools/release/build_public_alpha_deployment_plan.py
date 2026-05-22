#!/usr/bin/env python3
"""Build a public alpha deployment plan packet without deploying."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.validate_public_alpha_deployment_plan import (
    detect_forbidden_deployment_claims,
    validate_output_path,
    write_json_output,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--operator-review", default="control/audits/mvp-alpha-operator-review-01-v0/mvp_alpha_operator_review_01_report.json")
    parser.add_argument("--readiness", default="control/audits/e-bundle-02-hosted-wrapper-rehearsal-v0/e_bundle_02_report.json")
    parser.add_argument("--output")
    parser.add_argument("--summary-output")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    plan = build_plan(args.operator_review, args.readiness)
    errors = detect_forbidden_deployment_claims(plan, "plan")
    result = {"schema_version": "public_alpha_deployment_plan_build_result.v0", "status": "fail" if errors else "pass", "plan": plan, "errors": errors}
    if args.output:
        write_json_output(validate_output_path(args.output), plan)
    if args.summary_output:
        validate_output_path(args.summary_output).write_text(format_plan(plan) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    elif args.check:
        print(f"Public alpha deployment plan build status: {result['status']}")
    else:
        print(format_plan(plan))
    return 0 if result["status"] == "pass" else 1


def build_plan(operator_review: str, readiness: str) -> dict[str, Any]:
    base = _load_json("examples/hosting/deployment/public_alpha_deployment_plan_v0.json")
    base["input_refs"] = [operator_review, readiness]
    base["operator_approval_present"] = False
    base["deployment_execution_approval_present"] = False
    base["notes"] = list(base.get("notes", [])) + ["Generated plan packet; no deployment execution approval is inferred."]
    return base


def format_plan(plan: dict[str, Any]) -> str:
    return "\n".join([
        "# Public Alpha Deployment Plan",
        "",
        f"- plan_status: {plan['plan_status']}",
        "- planning_only: true",
        "- deployed: false",
        "- provider_api_called: false",
        "- dns_changed: false",
        "- site_dist_mutated: false",
    ])


def _load_json(relative: str) -> dict[str, Any]:
    return json.loads((REPO_ROOT / relative).read_text(encoding="utf-8"))


if __name__ == "__main__":
    raise SystemExit(main())
