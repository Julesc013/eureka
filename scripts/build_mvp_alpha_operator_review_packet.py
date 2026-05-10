#!/usr/bin/env python3
"""Build an MVP alpha operator review packet without approving launch."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.validate_mvp_alpha_audit import detect_forbidden_mvp_claims, validate_output_path, write_json_output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit", default="examples/audits/mvp_alpha/mvp_alpha_readiness_audit_v0.json")
    parser.add_argument("--gate", default="examples/audits/mvp_alpha/mvp_alpha_gate_decision_ready_for_operator_review_v0.json")
    parser.add_argument("--remediation", default="examples/audits/mvp_alpha/mvp_alpha_remediation_plan_v0.json")
    parser.add_argument("--output")
    parser.add_argument("--summary-output")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    packet = build_operator_review_packet(args.audit, args.gate, args.remediation)
    errors = validate_packet(packet)
    result = {"schema_version": "mvp_alpha_operator_review_packet_result.v0", "status": "fail" if errors else "pass", "packet": packet, "errors": errors}
    if args.output:
        write_json_output(validate_output_path(args.output), packet)
    if args.summary_output:
        validate_output_path(args.summary_output).write_text(format_packet(packet) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    elif args.check:
        print(f"MVP alpha operator review packet status: {result['status']}")
    else:
        print(format_packet(packet))
    return 0 if result["status"] == "pass" else 1


def build_operator_review_packet(audit_path: str, gate_path: str, remediation_path: str) -> dict[str, Any]:
    audit = _load(audit_path)
    gate = _load(gate_path)
    remediation = _load(remediation_path)
    return {
        "schema_version": "mvp_alpha_operator_review_packet.v0",
        "operator_review_packet_id": "mvp-alpha-operator-review-packet-generated-v0",
        "review_status": "operator_review_required",
        "summary": "Generated operator review packet from MVP local readiness evidence; no launch approval is inferred.",
        "launch_non_claims": [
            "Eureka is not live.",
            "Eureka is not production.",
            "Deployment is not approved by this packet.",
            "Operator signoff is required and absent.",
        ],
        "local_mvp_capabilities": list(audit.get("local_mvp_path_results", {}).keys()),
        "disabled_features": [
            "deployment",
            "provider_api_calls",
            "dns_changes",
            "public_bind",
            "live_source_fanout",
            "downloads",
            "uploads",
            "accounts",
            "telemetry",
            "install",
            "execute",
        ],
        "operator_gated_decisions": audit.get("operator_gated_items", []),
        "required_signoffs": [
            "Operator launch decision",
            "No-claims review",
            "Deployment boundary review",
        ],
        "evidence_refs": [audit_path, gate_path, remediation_path],
        "blockers": gate.get("blockers", []),
        "warnings": sorted(set(audit.get("warnings", []) + gate.get("warnings", []) + remediation.get("warnings", []))),
        "recommended_decision": "READY_WITH_WARNINGS" if gate.get("decision") == "READY_FOR_OPERATOR_REVIEW" else gate.get("decision", "NEEDS_REMEDIATION"),
        "truth_boundary": audit.get("truth_boundary", {}),
        "product_boundary": audit.get("product_boundary", {}),
        "notes": ["This packet does not infer signoff and does not allow deployment."],
    }


def validate_packet(packet: dict[str, Any]) -> list[str]:
    errors = detect_forbidden_mvp_claims(packet, "packet")
    if packet.get("review_status") != "operator_review_required":
        errors.append("packet review_status must be operator_review_required.")
    if not packet.get("required_signoffs"):
        errors.append("packet must list required signoffs.")
    return errors


def format_packet(packet: dict[str, Any]) -> str:
    return "\n".join([
        "# MVP Alpha Operator Review Packet",
        "",
        f"- review_status: {packet['review_status']}",
        f"- recommended_decision: {packet['recommended_decision']}",
        "- launch_allowed_current: false",
        "- deployment_allowed_current: false",
    ])


def _load(value: str) -> dict[str, Any]:
    path = Path(value)
    if not path.is_absolute():
        path = REPO_ROOT / path
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    raise SystemExit(main())
