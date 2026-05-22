#!/usr/bin/env python3
"""Plan the next local MVP iteration without executing it."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.validate_local_mvp_iteration import load_json, validate_output_path, write_json_output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output")
    parser.add_argument("--matrix-output")
    parser.add_argument("--summary-output")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    result = build_local_mvp_iteration()
    if args.output:
        write_json_output(validate_output_path(args.output), result["plan"])
    if args.matrix_output:
        write_json_output(validate_output_path(args.matrix_output), result["option_matrix"])
    if args.summary_output:
        validate_output_path(args.summary_output).write_text(result["summary"], encoding="utf-8")

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    elif args.check:
        print(f"Local MVP iteration planning status: {result['status']}")
        print(f"recommended_next_task: {result['recommended_next_task']}")
    else:
        print(result["summary"])
    return 0 if result["status"] == "pass" else 1


def build_local_mvp_iteration(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    plan = load_json(repo_root / "examples/audits/local_mvp/local_mvp_iteration_plan_v0.json")
    public_alpha = _load_optional(repo_root / "control/audits/public-alpha-deployment-plan-01-v0/public_alpha_deployment_plan_01_report.json")
    errors: list[str] = []
    if public_alpha:
        if public_alpha.get("status") not in {"pass", "pass_with_warnings"}:
            errors.append("PUBLIC-ALPHA-DEPLOYMENT-PLAN-01 is not pass/pass_with_warnings.")
        scope = public_alpha.get("planning_scope", {})
        for key in ("deployment_performed", "provider_api_called", "dns_changed", "site_dist_mutated", "public_alpha_live_claimed", "production_claimed"):
            if scope.get(key) is not False:
                errors.append(f"public alpha report {key} must be false.")
    deferral = plan.get("deployment_deferral", {})
    if deferral.get("deployment_approval_present") is not False:
        errors.append("deployment approval must not be inferred.")
    if plan.get("recommended_next_task") != "H2-BUNDLE-01":
        errors.append("current local MVP plan should recommend H2-BUNDLE-01.")
    option_matrix = {
        "schema_version": "local_mvp_option_matrix.v0",
        "options": plan.get("evaluated_options", []),
        "recommended_next_task": plan.get("recommended_next_task"),
        "deployment_deferred": deferral.get("deployment_deferred"),
        "errors": errors,
    }
    return {
        "schema_version": "local_mvp_iteration_planner_result.v0",
        "status": "fail" if errors else "pass",
        "recommended_next_task": plan.get("recommended_next_task"),
        "plan": plan,
        "option_matrix": option_matrix,
        "summary": _summary(plan, errors),
        "errors": errors,
    }


def _summary(plan: dict[str, Any], errors: list[str]) -> str:
    lines = [
        "# Local MVP Iteration Summary",
        "",
        f"- recommended_next_task: {plan.get('recommended_next_task')}",
        f"- recommendation_reason: {plan.get('recommendation_reason')}",
        f"- deployment_deferred: {plan.get('deployment_deferral', {}).get('deployment_deferred')}",
        f"- deployment_approval_present: {plan.get('deployment_deferral', {}).get('deployment_approval_present')}",
    ]
    lines.extend(f"- error: {error}" for error in errors)
    return "\n".join(lines) + "\n"


def _load_optional(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    return load_json(path)


if __name__ == "__main__":
    raise SystemExit(main())
