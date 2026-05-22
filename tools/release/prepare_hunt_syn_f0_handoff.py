#!/usr/bin/env python3
"""Prepare HUNT/SYN/F0 handoff records after LOCAL closeout."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_ROOT = Path(__file__).resolve().parent
if str(SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_ROOT))

from audit_local_appliance_closeout import build_closeout_records, write_json


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--output")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    root = Path(args.repo_root).resolve()
    records = build_closeout_records(root)
    payload = build_handoff_plan(records)
    if args.output:
        write_json(Path(args.output), payload)
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True), file=stdout)
    else:
        print("LOCAL handoff plan", file=stdout)
        print(f"recommended_next_task: {payload['recommended_next_task']}", file=stdout)
    return 0 if payload["status"] in {"pass", "pass_with_warnings"} else 1


def build_handoff_plan(records: Mapping[str, Any]) -> dict[str, Any]:
    closeout = records["closeout_result"]
    warnings = records["warning_disposition"]
    blockers = int(closeout.get("hard_blockers_remaining") or 0)
    if blockers:
        recommended = "LOCAL-REMEDIATION \u2014 Complete Local Appliance blockers"
        status = "blocked"
    elif warnings.get("summary", {}).get("warnings_remaining") and not (
        warnings.get("summary", {}).get("blocks_hunt")
        or warnings.get("summary", {}).get("blocks_syn")
        or warnings.get("summary", {}).get("blocks_f0")
    ):
        recommended = "HUNT-00 \u2014 Search Hunt track planning over Local Appliance"
        status = "pass_with_warnings"
    else:
        recommended = "HUNT-00 \u2014 Search Hunt track planning over Local Appliance"
        status = "pass"
    return {
        "schema_version": "local_appliance_handoff_plan.v0",
        "task": "LOCAL-14",
        "status": status,
        "recommended_next_task": recommended,
        "hunt": records["handoff_to_hunt"],
        "syn": records["handoff_to_syn"],
        "f0": records["handoff_to_f0"],
        "leakage_disposition": warnings.get("warnings", []),
        "no_implementation_started": True,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }


if __name__ == "__main__":
    raise SystemExit(main())
