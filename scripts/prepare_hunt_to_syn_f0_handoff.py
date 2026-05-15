#!/usr/bin/env python3
"""Prepare Search Hunt handoff records for SYN, F0, and later tracks."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping, Sequence, TextIO
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--capability-matrix", default="control/inventory/search_hunt_capability_matrix.json")
    parser.add_argument("--closeout-result", default="control/inventory/search_hunt_closeout_result.json")
    parser.add_argument("--output")
    parser.add_argument("--syn-output")
    parser.add_argument("--f0-output")
    parser.add_argument("--ghk-output")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    root = Path(args.repo_root).resolve()
    result = build_handoff(root, args.capability_matrix, args.closeout_result)
    if args.output:
        write_json(Path(args.output), result)
    if args.syn_output:
        write_json(Path(args.syn_output), result["syn_handoff"])
    if args.f0_output:
        write_json(Path(args.f0_output), result["f0_handoff"])
    if args.ghk_output:
        write_json(Path(args.ghk_output), result["g_h_k_handoff"])

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    else:
        print(f"recommended_next_task: {result['recommended_next_task']}", file=stdout)
    return 0 if result["status"] in {"pass", "pass_with_warnings"} else 1


def build_handoff(root: Path = REPO_ROOT, capability_matrix_rel: str = "control/inventory/search_hunt_capability_matrix.json", closeout_rel: str = "control/inventory/search_hunt_closeout_result.json") -> dict[str, Any]:
    capability_matrix = load_json(root / capability_matrix_rel)
    closeout = load_json(root / closeout_rel)
    capabilities = capability_matrix.get("capabilities", [])
    complete = bool(capabilities) and all(row.get("implemented") is True and row.get("tested") is True for row in capabilities)
    hard_blockers = int(closeout.get("hard_blockers_remaining", 0) or 0)
    if not complete or hard_blockers:
        recommended = "HUNT-REMEDIATION \u2014 Complete Search Hunt blockers"
        status = "blocked"
    else:
        recommended = "SYN-00 \u2014 Synthetic Query Foundry planning over Local Appliance"
        status = "pass_with_warnings" if closeout.get("warnings_remaining", 0) else "pass"

    syn = {
        "schema_version": "search_hunt_handoff_to_syn.v0",
        "task": "HUNT-12",
        "status": "pass",
        "next_task": "SYN-00 \u2014 Synthetic Query Foundry planning over Local Appliance",
        "syn_should_generate_query_pressure": True,
        "syn_should_generate_search_need_seeds": True,
        "syn_should_generate_workunit_seeds": True,
        "syn_must_not_generate_fake_evidence": True,
        "syn_must_not_generate_verified_records": True,
        "syn_must_use_hunt_absence_exhaustion_structures": True,
        "implementation_started": False,
    }
    f0 = {
        "schema_version": "search_hunt_handoff_to_f0.v0",
        "task": "HUNT-12",
        "status": "pass",
        "next_task": "F0-00 \u2014 Refresh F0 after Local Appliance and HUNT",
        "f0_can_resume": complete and hard_blockers == 0,
        "f0_recommended_now": False,
        "f0_should_use_workunits_for_extraction_tasks": True,
        "f0_outputs_must_flow_through_source_observation_evidence_review_index": True,
        "f0_must_be_visible_testable_through_workbench": True,
        "implementation_started": False,
    }
    ghk = {
        "schema_version": "search_hunt_handoff_to_g_h_k.v0",
        "task": "HUNT-12",
        "status": "pass",
        "g_consumes_hunt_explanations_exhaustion_absence": True,
        "h_source_expansion_consumes_source_probe_workunits_and_policy_gates": True,
        "k_consumes_ai_escalation_gate_and_agent_research_task_contract": True,
        "outputs_candidate_only_until_reviewed": True,
        "implementation_started": False,
    }
    return {
        "schema_version": "search_hunt_handoff_bundle.v0",
        "task": "HUNT-12",
        "status": status,
        "recommended_next_task": recommended,
        "alternative_next_task": "F0-00 \u2014 Refresh F0 after Local Appliance and HUNT",
        "f0_recommended_now": False,
        "syn_handoff": syn,
        "f0_handoff": f0,
        "g_h_k_handoff": ghk,
    }


def load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
