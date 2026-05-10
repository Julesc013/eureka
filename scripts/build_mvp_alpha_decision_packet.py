#!/usr/bin/env python3
"""Build an MVP alpha operator decision packet without approving launch."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.validate_mvp_alpha_operator_review import (
    detect_forbidden_operator_review_claims,
    validate_output_path,
    write_json_output,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit", default="control/audits/mvp-alpha-audit-01-local-mvp-readiness-v0/mvp_alpha_audit_01_report.json")
    parser.add_argument("--gate", default="control/audits/mvp-alpha-audit-01-local-mvp-readiness-v0/mvp_alpha_gate_decision.md")
    parser.add_argument("--remediation", default="control/audits/mvp-alpha-audit-01-local-mvp-readiness-v0/remediation_plan.md")
    parser.add_argument("--output")
    parser.add_argument("--summary-output")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    packet = build_decision_packet(args.audit, args.gate, args.remediation)
    errors = validate_decision_packet(packet)
    result = {"schema_version": "mvp_alpha_operator_decision_packet_result.v0", "status": "fail" if errors else "pass", "packet": packet, "errors": errors}
    if args.output:
        write_json_output(validate_output_path(args.output), packet)
    if args.summary_output:
        validate_output_path(args.summary_output).write_text(format_decision_packet(packet) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    elif args.check:
        print(f"MVP alpha decision packet status: {result['status']}")
        print(f"recommended_next_task: {packet['recommended_next_task']}")
    else:
        print(format_decision_packet(packet))
    return 0 if result["status"] == "pass" else 1


def build_decision_packet(audit_path: str, gate_path: str, remediation_path: str) -> dict[str, Any]:
    audit = _load_json_if_possible(audit_path)
    status = audit.get("status", "pass_with_warnings")
    gate_decision = audit.get("gate_decision", "READY_WITH_WARNINGS")
    selected_decision = "not_evaluable"
    recommended_next = "LOCAL-MVP-ITERATION-01"
    if status in {"needs_remediation", "blocked", "fail"} or gate_decision in {"NEEDS_REMEDIATION", "BLOCKED", "FAIL"}:
        selected_decision = "request_remediation"
        recommended_next = "MVP-ALPHA-REMEDIATION-01"
    return {
        "schema_version": "mvp_alpha_operator_decision_packet.v0",
        "decision_packet_id": "mvp-alpha-operator-decision-packet-generated-v0",
        "decision_status": "decision_requested",
        "selected_decision": selected_decision,
        "decision_options": [
            "approve_local_only_continuation",
            "approve_public_alpha_deployment_planning_only",
            "approve_operator_supervised_launch_future",
            "request_remediation",
            "block_launch",
            "defer_launch",
        ],
        "explicit_operator_approval": False,
        "signoff_required": True,
        "operator_signoff_inferred": False,
        "launch_allowed_current": False,
        "deployment_allowed_current": False,
        "evidence_refs": [audit_path, gate_path, remediation_path],
        "recommended_next_task": recommended_next,
        "required_acknowledgements": [
            "PASS and PASS_WITH_WARNINGS do not approve launch.",
            "Unsigned operator packets are not launch approval.",
            "No deployment execution is allowed in this bundle.",
        ],
        "warnings": list(audit.get("known_warn_only_conditions", [])) or list(audit.get("warnings", [])),
        "truth_boundary": {
            "operator_review_is_launch": False,
            "operator_signoff_inferred": False,
            "public_alpha_live_claimed": False,
            "production_claimed": False,
            "public_index_mutated": False,
            "master_index_mutated": False,
            "source_truth_accepted": False,
            "evidence_truth_accepted": False,
            "candidate_truth_accepted": False,
            "rights_clearance_claimed": False,
            "malware_safety_claimed": False,
            "verified_installability_claimed": False,
        },
        "product_boundary": {
            "changed_public_search_behavior": False,
            "enabled_live_source_fanout": False,
            "enabled_source_sync": False,
            "enabled_downloads": False,
            "enabled_uploads": False,
            "enabled_accounts": False,
            "enabled_telemetry": False,
            "enabled_public_relay": False,
            "enabled_hosting": False,
            "mutated_site_dist": False,
            "mutated_public_index": False,
            "mutated_master_index": False,
        },
    }


def validate_decision_packet(packet: dict[str, Any]) -> list[str]:
    errors = detect_forbidden_operator_review_claims(packet, "packet")
    for key in ("explicit_operator_approval", "operator_signoff_inferred", "launch_allowed_current", "deployment_allowed_current"):
        if packet.get(key) is not False:
            errors.append(f"{key} must be false.")
    if packet.get("signoff_required") is not True:
        errors.append("signoff_required must be true.")
    return errors


def format_decision_packet(packet: dict[str, Any]) -> str:
    return "\n".join([
        "# MVP Alpha Operator Decision Packet",
        "",
        f"- decision_status: {packet['decision_status']}",
        f"- selected_decision: {packet['selected_decision']}",
        f"- recommended_next_task: {packet['recommended_next_task']}",
        "- signoff_required: true",
        "- signoff_inferred: false",
        "- deployment_allowed_current: false",
        "- launch_allowed_current: false",
    ])


def _load_json_if_possible(value: str) -> dict[str, Any]:
    path = Path(value)
    if not path.is_absolute():
        path = REPO_ROOT / path
    if path.suffix.lower() != ".json" or not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    raise SystemExit(main())
