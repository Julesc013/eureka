#!/usr/bin/env python3
"""Validate Hosted Public Search Rehearsal v0."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
AUDIT_DIR = REPO_ROOT / "control" / "audits" / "hosted-public-search-rehearsal-v0"
REPORT_PATH = AUDIT_DIR / "hosted_public_search_rehearsal_report.json"
RUNNER = REPO_ROOT / "scripts" / "run_hosted_public_search_rehearsal.py"
DOC_PATH = REPO_ROOT / "docs" / "operations" / "HOSTED_PUBLIC_SEARCH_REHEARSAL.md"
REQUIRED_AUDIT_FILES = {
    "README.md",
    "REHEARSAL_SUMMARY.md",
    "HOSTED_MODE_CONFIGURATION.md",
    "STARTUP_AND_HEALTH_EVIDENCE.md",
    "ROUTE_REHEARSAL_RESULTS.md",
    "SAFE_QUERY_REHEARSAL.md",
    "BLOCKED_REQUEST_REHEARSAL.md",
    "STATIC_HANDOFF_COMPATIBILITY.md",
    "PUBLIC_INDEX_COMPATIBILITY.md",
    "SAFETY_AND_PRIVACY_REVIEW.md",
    "DEPLOYMENT_TEMPLATE_REVIEW.md",
    "OPERATOR_DEPLOYMENT_READINESS.md",
    "RATE_LIMIT_AND_EDGE_GAPS.md",
    "PUBLIC_CLAIM_REVIEW.md",
    "REMAINING_BLOCKERS.md",
    "NEXT_STEPS.md",
    "COMMAND_RESULTS.md",
    "hosted_public_search_rehearsal_report.json",
}
REQUIRED_HARD_FALSE = {
    "hosted_deployment_performed",
    "hosted_deployment_verified",
    "live_probes_enabled",
    "downloads_enabled",
    "uploads_enabled",
    "installs_enabled",
    "local_paths_enabled",
    "arbitrary_url_fetch_enabled",
    "telemetry_enabled",
    "accounts_enabled",
    "external_calls_performed",
    "ai_runtime_enabled",
    "master_index_mutated",
}
PRIVATE_MARKERS = (
    "c:\\",
    "d:\\",
    "/users/",
    "/home/",
    "/tmp/",
    "/var/",
    "secret-value",
    "traceback",
)


def validate_hosted_public_search_rehearsal(*, run_rehearsal: bool = True) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    if not AUDIT_DIR.is_dir():
        errors.append("control/audits/hosted-public-search-rehearsal-v0: missing audit directory.")
    else:
        existing = {path.name for path in AUDIT_DIR.iterdir() if path.is_file()}
        missing = sorted(REQUIRED_AUDIT_FILES - existing)
        if missing:
            errors.append(f"missing audit files: {', '.join(missing)}")

    if not RUNNER.is_file():
        errors.append("scripts/run_hosted_public_search_rehearsal.py: missing runner.")

    report: dict[str, Any] = {}
    if not REPORT_PATH.is_file():
        errors.append("hosted_public_search_rehearsal_report.json: missing report.")
    else:
        try:
            payload = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
            if isinstance(payload, dict):
                report = payload
            else:
                errors.append("hosted_public_search_rehearsal_report.json: top-level JSON must be an object.")
        except json.JSONDecodeError as exc:
            errors.append(f"hosted_public_search_rehearsal_report.json: invalid JSON: {exc}")

    if report:
        _validate_report(report, errors, warnings)

    rehearsal_result: dict[str, Any] = {}
    if run_rehearsal and RUNNER.is_file():
        try:
            from scripts.run_hosted_public_search_rehearsal import run_hosted_public_search_rehearsal

            rehearsal_result = run_hosted_public_search_rehearsal()
            if rehearsal_result.get("ok") is not True:
                errors.append("live local rehearsal run did not pass.")
            _validate_rehearsal_result(rehearsal_result, errors)
        except Exception as exc:  # pragma: no cover - defensive validator guard
            errors.append(f"could not run rehearsal: {exc}")

    if not DOC_PATH.is_file():
        errors.append("docs/operations/HOSTED_PUBLIC_SEARCH_REHEARSAL.md: missing docs.")
    else:
        doc = DOC_PATH.read_text(encoding="utf-8").casefold()
        for phrase in (
            "local-only",
            "no deployment",
            "no live probes",
            "no downloads",
            "operator-gated",
            "p59 query observation contract",
        ):
            if phrase not in doc:
                errors.append(f"HOSTED_PUBLIC_SEARCH_REHEARSAL.md missing phrase: {phrase}")

    return {
        "status": "valid" if not errors else "invalid",
        "created_by": "hosted_public_search_rehearsal_validator_v0",
        "report_id": report.get("report_id"),
        "route_check_count": len(report.get("route_results", [])) if isinstance(report.get("route_results"), list) else 0,
        "safe_query_count": len(report.get("safe_query_results", [])) if isinstance(report.get("safe_query_results"), list) else 0,
        "blocked_request_count": len(report.get("blocked_request_results", [])) if isinstance(report.get("blocked_request_results"), list) else 0,
        "live_rehearsal_status": rehearsal_result.get("summary", {}).get("status") if rehearsal_result else "not_run",
        "errors": errors,
        "warnings": warnings,
    }


def _validate_report(report: Mapping[str, Any], errors: list[str], warnings: list[str]) -> None:
    if report.get("report_id") != "hosted_public_search_rehearsal_v0":
        errors.append("report_id must be hosted_public_search_rehearsal_v0.")
    if report.get("rehearsal_mode") != "hosted_local_rehearsal":
        errors.append("rehearsal_mode must be hosted_local_rehearsal.")
    if report.get("server_started") is not True:
        errors.append("server_started must be true for P58 local rehearsal evidence.")
    if not str(report.get("base_url", "")).startswith("http://127.0.0.1:"):
        errors.append("base_url must be a localhost rehearsal URL.")
    for key in (
        "route_results",
        "safe_query_results",
        "blocked_request_results",
        "startup_and_health",
        "status_endpoint_evidence",
        "static_handoff_compatibility",
        "public_index_compatibility",
        "deployment_template_review",
    ):
        value = report.get(key)
        if not isinstance(value, list) or not value:
            errors.append(f"{key} must be a non-empty list.")
        elif any(item.get("passed") is not True for item in value if isinstance(item, Mapping)):
            errors.append(f"{key} contains failed checks.")
    blocked = report.get("blocked_request_results")
    if isinstance(blocked, list) and len(blocked) < 34:
        errors.append("blocked_request_results must include the full P58 blocked matrix.")
    hard_booleans = report.get("hard_booleans")
    if not isinstance(hard_booleans, Mapping):
        errors.append("hard_booleans must be present.")
    else:
        for key in sorted(REQUIRED_HARD_FALSE):
            if hard_booleans.get(key) is not False:
                errors.append(f"hard_booleans.{key} must be false.")
    public_claim = report.get("public_claim_review")
    if not isinstance(public_claim, Mapping):
        errors.append("public_claim_review must be present.")
    else:
        for key in (
            "hosted_deployment_claimed",
            "production_readiness_claimed",
            "live_probe_claimed",
            "edge_rate_limit_claimed",
        ):
            if public_claim.get(key) is not False:
                errors.append(f"public_claim_review.{key} must be false.")
    rate_gaps = report.get("rate_limit_and_edge_gaps")
    if not isinstance(rate_gaps, Mapping):
        errors.append("rate_limit_and_edge_gaps must be present.")
    elif rate_gaps.get("edge_rate_limit_status") not in {"operator_gated", "not_configured"}:
        errors.append("edge rate-limit status must remain operator_gated/not_configured unless evidence exists.")
    if not isinstance(report.get("remaining_blockers"), list) or not report.get("remaining_blockers"):
        errors.append("remaining_blockers must be recorded.")
    if report.get("next_recommended_branch") != "P59 Query Observation Contract v0":
        errors.append("next_recommended_branch must be P59 Query Observation Contract v0.")
    if not _has_no_private_marker(json.dumps(report, sort_keys=True)):
        errors.append("report contains a private path, secret marker, or traceback marker.")
    if report.get("hosted_deployment_verified") is True:
        errors.append("report must not claim hosted deployment verification.")
    if report.get("hosted_deployment_performed") is True:
        errors.append("report must not claim a hosted deployment was performed.")
    if warnings is not None and report.get("hosted_deployment_verified") is False:
        warnings.append("hosted deployment remains operator-gated/unverified.")


def _validate_rehearsal_result(result: Mapping[str, Any], errors: list[str]) -> None:
    if result.get("mode") != "hosted_local_rehearsal":
        errors.append("runner mode must be hosted_local_rehearsal.")
    if result.get("server_started") is not True:
        errors.append("runner must start a local server.")
    hard = result.get("hard_booleans")
    if not isinstance(hard, Mapping):
        errors.append("runner hard_booleans missing.")
    else:
        for key in sorted(REQUIRED_HARD_FALSE):
            if hard.get(key) is not False:
                errors.append(f"runner hard_booleans.{key} must be false.")
    summary = result.get("summary") if isinstance(result.get("summary"), Mapping) else {}
    if summary.get("passed_blocked_request_count") != summary.get("blocked_request_count"):
        errors.append("runner blocked request count did not fully pass.")
    if not _has_no_private_marker(json.dumps(result, sort_keys=True)):
        errors.append("runner output contains a private path, secret marker, or traceback marker.")


def _has_no_private_marker(text: str) -> bool:
    folded = text.casefold().replace("\\\\", "\\")
    return not any(marker in folded for marker in PRIVATE_MARKERS)


def _format_plain(report: Mapping[str, Any]) -> str:
    lines = [
        "Hosted Public Search Rehearsal validation",
        f"status: {report['status']}",
        f"report_id: {report.get('report_id')}",
        f"routes: {report.get('route_check_count')}",
        f"safe_queries: {report.get('safe_query_count')}",
        f"blocked_requests: {report.get('blocked_request_count')}",
        f"live_rehearsal_status: {report.get('live_rehearsal_status')}",
    ]
    if report.get("errors"):
        lines.append("errors:")
        lines.extend(f"- {error}" for error in report["errors"])
    if report.get("warnings"):
        lines.append("warnings:")
        lines.extend(f"- {warning}" for warning in report["warnings"])
    return "\n".join(lines) + "\n"


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Emit JSON validation report.")
    parser.add_argument("--no-run", action="store_true", help="Validate files without running the local rehearsal.")
    args = parser.parse_args(list(argv) if argv is not None else None)
    report = validate_hosted_public_search_rehearsal(run_rehearsal=not args.no_run)
    output = stdout or sys.stdout
    if args.json:
        output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        output.write(_format_plain(report))
    return 0 if report["status"] == "valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
