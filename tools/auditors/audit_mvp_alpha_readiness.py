#!/usr/bin/env python3
"""Build a local MVP alpha readiness audit without deployment."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.validate_mvp_alpha_audit import (
    REQUIRED_TRACKS,
    detect_forbidden_mvp_claims,
    validate_output_path,
    write_json_output,
)

EXAMPLE_ROOT = REPO_ROOT / "examples/audits/mvp_alpha"
KNOWN_REPORTS = {
    "A": "control/audits/track-a-16-renderer-parity-harness-v0/renderer_parity_report.json",
    "B": "control/audits/track-b-23-integration-audit-v0/track_b_23_report.json",
    "IA": "control/audits/ia-bundle-03-review-integration-quality-delta-v0/ia_bundle_03_report.json",
    "H0": "control/audits/h0-bundle-03-coverage-scorecards-source-packs-v0/h0_bundle_03_report.json",
    "H1": "control/audits/h1-bundle-04-review-quality-audit-v0/h1_bundle_04_report.json",
    "F": "control/audits/f-bundle-02-extraction-candidate-search-integration-v0/f_bundle_02_report.json",
    "G": "control/audits/g-bundle-02-ranking-shadow-quality-harness-v0/g_bundle_02_report.json",
    "I": "control/audits/i-bundle-01-pack-quarantine-contribution-review-v0/i_bundle_01_report.json",
    "J0": "control/audits/j0-bundle-01-safe-actions-manifests-v0/j0_bundle_01_report.json",
    "D": "control/audits/d-bundle-02-localhost-readonly-relay-v0/d_bundle_02_report.json",
    "C": "control/audits/c-bundle-03-native-smoke-packaging-v0/c_bundle_03_report.json",
    "E": "control/audits/e-bundle-02-hosted-wrapper-rehearsal-v0/e_bundle_02_report.json",
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json-output")
    parser.add_argument("--matrix-output")
    parser.add_argument("--summary-output")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = build_mvp_alpha_readiness_result()
    if args.json_output:
        write_json_output(validate_output_path(args.json_output), report["audit"])
    if args.matrix_output:
        write_json_output(validate_output_path(args.matrix_output), report["matrix"])
    if args.summary_output:
        validate_output_path(args.summary_output).write_text(format_mvp_alpha_summary(report) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    elif args.check:
        print(f"MVP alpha readiness audit status: {report['status']}")
        print(f"MVP gate: {report['gate_decision']}")
    else:
        print(format_mvp_alpha_summary(report))
    return 0 if report["status"] in {"pass", "pass_with_warnings"} else 1


def build_mvp_alpha_readiness_result() -> dict[str, Any]:
    matrix = _read_example("mvp_alpha_integration_matrix_v0.json")
    audit = _read_example("mvp_alpha_readiness_audit_v0.json")
    gate = _read_example("mvp_alpha_gate_decision_ready_for_operator_review_v0.json")
    remediation = _read_example("mvp_alpha_remediation_plan_v0.json")
    operator_packet = _read_example("mvp_alpha_operator_review_packet_v0.json")
    report_statuses = inspect_known_reports()
    errors: list[str] = []
    warnings = list(audit.get("warnings", []))
    missing_tracks = sorted(set(REQUIRED_TRACKS) - set(audit.get("audited_tracks", [])))
    if missing_tracks:
        errors.append(f"Missing audited tracks: {missing_tracks}")
    for payload, label in ((matrix, "matrix"), (audit, "audit"), (gate, "gate"), (remediation, "remediation"), (operator_packet, "operator_packet")):
        errors.extend(f"{label}: {error}" for error in detect_forbidden_mvp_claims(payload, label))
    for track, status in report_statuses.items():
        if status == "missing":
            if track == "A":
                warnings.append("Track A exact final audit report is not present; latest Track A parity evidence is used.")
            else:
                errors.append(f"{track}: expected audit report missing.")
    status = "fail" if errors else audit.get("audit_status", "pass_with_warnings")
    gate_decision = "NEEDS_REMEDIATION" if errors else "READY_WITH_WARNINGS"
    return {
        "schema_version": "mvp_alpha_readiness_audit_result.v0",
        "status": status,
        "gate_decision": gate_decision,
        "next_task": "MVP-ALPHA-OPERATOR-REVIEW-01 - Operator review and launch decision packet" if not errors else "MVP-ALPHA-REMEDIATION-01 - Resolve local MVP readiness blockers",
        "audit": audit,
        "matrix": matrix,
        "gate": gate,
        "remediation": remediation,
        "operator_packet": operator_packet,
        "known_report_statuses": report_statuses,
        "warnings": sorted(set(warnings)),
        "errors": errors,
        "deployment_scope": {
            "deployment_performed": False,
            "provider_api_called": False,
            "dns_changed": False,
            "site_dist_mutated": False,
            "public_alpha_live_claimed": False,
            "production_claimed": False,
        },
    }


def inspect_known_reports() -> dict[str, str]:
    statuses: dict[str, str] = {}
    for track, relative in KNOWN_REPORTS.items():
        path = REPO_ROOT / relative
        if not path.is_file():
            statuses[track] = "missing"
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            statuses[track] = "invalid_json"
            continue
        statuses[track] = str(payload.get("status") or payload.get("track_c_exit_gate") or "present").casefold()
    return statuses


def format_mvp_alpha_summary(report: dict[str, Any]) -> str:
    lines = [
        "# MVP Alpha Readiness Summary",
        "",
        f"- status: {report['status']}",
        f"- gate_decision: {report['gate_decision']}",
        f"- next_task: {report['next_task']}",
        f"- deployment_performed: {report['deployment_scope']['deployment_performed']}",
        f"- public_alpha_live_claimed: {report['deployment_scope']['public_alpha_live_claimed']}",
        f"- production_claimed: {report['deployment_scope']['production_claimed']}",
        "",
        "## Warnings",
    ]
    lines.extend(f"- {warning}" for warning in report.get("warnings", []))
    if report.get("errors"):
        lines.append("")
        lines.append("## Errors")
        lines.extend(f"- {error}" for error in report["errors"])
    return "\n".join(lines)


def _read_example(name: str) -> dict[str, Any]:
    return json.loads((EXAMPLE_ROOT / name).read_text(encoding="utf-8"))


if __name__ == "__main__":
    raise SystemExit(main())
