#!/usr/bin/env python3
"""Select the next local MVP task from an iteration plan."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.validate_local_mvp_iteration import load_json, validate_output_path, write_json_output

DEPLOYMENT_TASK = "PUBLIC-ALPHA-OPERATOR-DEPLOYMENT-APPROVAL-01"
ALLOWED_LOCAL_TASKS = {"H2-BUNDLE-01", "MVP-ALPHA-REMEDIATION-01", "LOCAL-MVP-BLOCKED-01"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", default="examples/audits/local_mvp/local_mvp_iteration_plan_v0.json")
    parser.add_argument("--output")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    plan = load_json(_resolve(args.plan))
    result = select_next_task(plan, args.plan)
    if args.output:
        write_json_output(validate_output_path(args.output), result)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    elif args.check:
        print(f"Local MVP next task selection status: {result['status']}")
        print(f"selected_next_task: {result['selected_next_task']}")
    else:
        print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "pass" else 1


def select_next_task(plan: dict[str, Any], plan_ref: str = "inline") -> dict[str, Any]:
    selected = plan.get("recommended_next_task", "not_evaluable")
    deferral = plan.get("deployment_deferral", {})
    errors: list[str] = []
    if selected == DEPLOYMENT_TASK and deferral.get("deployment_approval_present") is not True:
        errors.append("Cannot route to deployment approval without explicit approval artifact.")
    if selected not in ALLOWED_LOCAL_TASKS and selected != DEPLOYMENT_TASK:
        errors.append(f"Unknown or unsafe local MVP next task: {selected}")
    if deferral.get("deployment_deferred") is not True:
        errors.append("deployment_deferred must be true.")
    if deferral.get("deployment_approval_present") is not False:
        errors.append("deployment approval must not be inferred.")
    return {
        "schema_version": "local_mvp_next_task_selection.v0",
        "status": "fail" if errors else "pass",
        "decision_ref": plan_ref,
        "selected_next_task": selected,
        "selected_next_task_title": title_for_task(selected),
        "deployment_allowed_current": False,
        "launch_allowed_current": False,
        "operator_approval_required": selected == DEPLOYMENT_TASK,
        "errors": errors,
    }


def title_for_task(task_id: str) -> str:
    return {
        "H2-BUNDLE-01": "Package registry source-family policy packs",
        "MVP-ALPHA-REMEDIATION-01": "Resolve local MVP readiness blockers",
        "LOCAL-MVP-BLOCKED-01": "Resolve blocked local iteration gate",
        DEPLOYMENT_TASK: "Operator approval for deployment execution",
    }.get(task_id, "Unknown task")


def _resolve(raw: str) -> Path:
    path = Path(raw)
    if not path.is_absolute():
        path = REPO_ROOT / path
    return path


if __name__ == "__main__":
    raise SystemExit(main())
