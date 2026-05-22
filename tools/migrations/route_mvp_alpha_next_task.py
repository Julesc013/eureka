#!/usr/bin/env python3
"""Route an MVP alpha operator decision to the next task without executing it."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.validate_mvp_alpha_operator_review import NEXT_TASK_MAPPING, validate_output_path, write_json_output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--decision", default="examples/audits/mvp_alpha_operator/operator_decision_request_v0.json")
    parser.add_argument("--output")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    decision = _load(args.decision)
    result = route_decision(decision, args.decision)
    if args.output:
        write_json_output(validate_output_path(args.output), result)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    elif args.check:
        print(f"MVP alpha next-task route status: {result['status']}")
        print(f"next_task_id: {result['next_task_id']}")
    else:
        print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "pass" else 1


def route_decision(decision: dict, decision_ref: str) -> dict:
    selected = decision.get("selected_decision", "not_evaluable")
    next_task = NEXT_TASK_MAPPING.get(selected, "LOCAL-MVP-ITERATION-01")
    errors: list[str] = []
    if decision.get("deployment_allowed_current") is not False:
        errors.append("deployment_allowed_current must be false.")
    if decision.get("launch_allowed_current") is not False:
        errors.append("launch_allowed_current must be false.")
    if decision.get("explicit_operator_approval") is not False:
        errors.append("explicit_operator_approval must be false in current examples.")
    return {
        "schema_version": "mvp_alpha_operator_next_task.v0",
        "status": "fail" if errors else "pass",
        "next_task_record_id": "mvp-alpha-next-task-route-generated-v0",
        "decision_ref": decision_ref,
        "selected_decision": selected,
        "next_task_id": next_task,
        "next_task_title": title_for_next_task(next_task),
        "next_task_allowed": not errors,
        "next_task_forbidden_actions": [
            "deployment",
            "hosting_provider_calls",
            "dns_changes",
            "site_dist_mutation",
            "public_alpha_live_claim",
            "production_claim",
            "operator_signoff_inference",
        ],
        "preconditions": ["Routing does not execute the next task."],
        "errors": errors,
    }


def title_for_next_task(task_id: str) -> str:
    return {
        "LOCAL-MVP-ITERATION-01": "Continue local MVP improvements pending operator decision",
        "PUBLIC-ALPHA-DEPLOYMENT-PLAN-01": "Public alpha deployment planning only",
        "PUBLIC-ALPHA-LAUNCH-PREP-01": "Operator supervised public alpha launch preparation",
        "MVP-ALPHA-REMEDIATION-01": "Resolve local MVP readiness blockers",
        "MVP-ALPHA-BLOCKED-01": "MVP alpha launch blocked",
    }.get(task_id, "Unknown next task")


def _load(value: str) -> dict:
    path = Path(value)
    if not path.is_absolute():
        path = REPO_ROOT / path
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    raise SystemExit(main())
