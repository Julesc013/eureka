#!/usr/bin/env python3
"""Validate Public Hosted Deployment Evidence v0 audit files."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
AUDIT_DIR = REPO_ROOT / "control" / "audits" / "public-hosted-deployment-evidence-v0"
REPORT_PATH = AUDIT_DIR / "public_hosted_deployment_evidence_report.json"
VERIFIER = REPO_ROOT / "scripts" / "verify_public_hosted_deployment.py"
DOC_PATH = REPO_ROOT / "docs" / "operations" / "PUBLIC_HOSTED_DEPLOYMENT_EVIDENCE.md"
STATUS_VALUES = {
    "not_configured",
    "configured_unverified",
    "verified_passed",
    "verified_failed",
    "unreachable",
    "unsafe_failed",
    "operator_gated",
    "auth_unavailable",
    "evidence_unavailable",
    "blocked",
}
REQUIRED_AUDIT_FILES = {
    "README.md",
    "DEPLOYMENT_SUMMARY.md",
    "STATIC_SITE_EVIDENCE.md",
    "HOSTED_BACKEND_EVIDENCE.md",
    "ROUTE_VERIFICATION_RESULTS.md",
    "SAFE_QUERY_VERIFICATION.md",
    "BLOCKED_REQUEST_VERIFICATION.md",
    "STATUS_AND_HEALTH_VERIFICATION.md",
    "STATIC_TO_DYNAMIC_HANDOFF_VERIFICATION.md",
    "PUBLIC_INDEX_VERIFICATION.md",
    "TLS_CORS_CACHE_HEADER_REVIEW.md",
    "RATE_LIMIT_AND_EDGE_EVIDENCE.md",
    "PRIVACY_LOGGING_AND_TELEMETRY_REVIEW.md",
    "PUBLIC_CLAIM_REVIEW.md",
    "OPERATOR_ACTIONS_REQUIRED.md",
    "FAILURE_OR_UNVERIFIED_STATUS.md",
    "REMAINING_BLOCKERS.md",
    "NEXT_STEPS.md",
    "COMMAND_RESULTS.md",
    "public_hosted_deployment_evidence_report.json",
}
STATUS_FIELDS = (
    "static_site_status",
    "hosted_backend_status",
    "search_handoff_status",
    "route_verification_status",
    "safety_verification_status",
    "tls_status",
    "cors_status",
    "cache_header_status",
    "rate_limit_status",
    "logging_telemetry_status",
)
REQUIRED_FALSE_BOOLEANS = (
    "production_ready_claimed",
    "live_probes_enabled",
    "source_connectors_enabled",
    "external_source_calls_enabled",
    "downloads_enabled",
    "uploads_enabled",
    "installs_enabled",
    "local_paths_enabled",
    "arbitrary_url_fetch_enabled",
    "telemetry_enabled",
    "accounts_enabled",
    "master_index_mutation_enabled",
    "source_cache_runtime_enabled",
    "evidence_ledger_runtime_enabled",
    "candidate_index_runtime_enabled",
)


def validate_public_hosted_deployment_evidence() -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    if not VERIFIER.is_file():
        errors.append("scripts/verify_public_hosted_deployment.py is missing.")

    if not AUDIT_DIR.is_dir():
        errors.append("control/audits/public-hosted-deployment-evidence-v0 is missing.")
    else:
        existing = {path.name for path in AUDIT_DIR.iterdir() if path.is_file()}
        missing = sorted(REQUIRED_AUDIT_FILES - existing)
        if missing:
            errors.append(f"missing audit files: {', '.join(missing)}")

    report = _load_report(errors)
    if report:
        _validate_report(report, errors, warnings)

    if not DOC_PATH.is_file():
        errors.append("docs/operations/PUBLIC_HOSTED_DEPLOYMENT_EVIDENCE.md is missing.")
    else:
        doc = DOC_PATH.read_text(encoding="utf-8").casefold()
        for phrase in (
            "no deployment",
            "no production claim",
            "static-only",
            "hosted backend",
            "operator-gated",
            "live connectors remain disabled",
        ):
            if phrase not in doc:
                errors.append(f"PUBLIC_HOSTED_DEPLOYMENT_EVIDENCE.md missing phrase: {phrase}")

    return {
        "status": "valid" if not errors else "invalid",
        "created_by": "public_hosted_deployment_evidence_validator_v0",
        "report_id": report.get("report_id") if report else None,
        "static_site_status": report.get("static_site_status") if report else None,
        "hosted_backend_status": report.get("hosted_backend_status") if report else None,
        "deployment_verified": report.get("deployment_verified") if report else None,
        "production_ready_claimed": report.get("production_ready_claimed") if report else None,
        "errors": errors,
        "warnings": warnings,
    }


def _load_report(errors: list[str]) -> dict[str, Any]:
    if not REPORT_PATH.is_file():
        errors.append("public_hosted_deployment_evidence_report.json is missing.")
        return {}
    try:
        payload = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"public_hosted_deployment_evidence_report.json invalid JSON: {exc}")
        return {}
    if not isinstance(payload, dict):
        errors.append("public_hosted_deployment_evidence_report.json must be an object.")
        return {}
    return payload


def _validate_report(report: Mapping[str, Any], errors: list[str], warnings: list[str]) -> None:
    if report.get("report_id") != "public_hosted_deployment_evidence_v0":
        errors.append("report_id must be public_hosted_deployment_evidence_v0.")
    for field in STATUS_FIELDS:
        if report.get(field) not in STATUS_VALUES:
            errors.append(f"{field} has invalid status: {report.get(field)!r}.")

    for key in REQUIRED_FALSE_BOOLEANS:
        if report.get(key) is not False:
            errors.append(f"{key} must be false.")

    if report.get("deployment_verified") is True:
        if report.get("static_deployment_verified") is not True or report.get("backend_deployment_verified") is not True:
            errors.append("deployment_verified cannot be true unless both static and backend are verified.")
    if report.get("production_ready_claimed") is not False:
        errors.append("production_ready_claimed must be false.")

    static_verified = report.get("static_deployment_verified") is True
    static_url = report.get("static_url")
    static_routes = report.get("verifier_results", {}).get("static_route_results") if isinstance(report.get("verifier_results"), Mapping) else []
    if static_verified:
        if not static_url:
            errors.append("static_deployment_verified true requires static_url.")
        if not isinstance(static_routes, list) or not static_routes:
            errors.append("static_deployment_verified true requires static route evidence.")
        elif any(item.get("status") != "verified_passed" for item in static_routes if isinstance(item, Mapping)):
            errors.append("static_deployment_verified true requires all static route checks to pass.")
    elif report.get("static_site_status") == "verified_passed":
        errors.append("static_site_status verified_passed requires static_deployment_verified true.")

    backend_verified = report.get("backend_deployment_verified") is True
    backend_url = report.get("backend_url")
    route_results = report.get("verifier_results", {}).get("route_results") if isinstance(report.get("verifier_results"), Mapping) else []
    if backend_verified:
        if not backend_url:
            errors.append("backend_deployment_verified true requires backend_url.")
        if not isinstance(route_results, list) or not route_results:
            errors.append("backend_deployment_verified true requires route evidence.")
        elif any(item.get("passed") is not True for item in route_results if isinstance(item, Mapping)):
            errors.append("backend_deployment_verified true requires all route checks to pass.")
        if report.get("public_search_mode_local_index_only") is not True:
            errors.append("backend verified requires public_search_mode_local_index_only true.")
    elif report.get("hosted_public_search_live") is True:
        errors.append("hosted_public_search_live cannot be true without backend verification.")

    if report.get("rate_limit_status") == "verified_passed":
        rate = report.get("verifier_results", {}).get("rate_limit_results") if isinstance(report.get("verifier_results"), Mapping) else {}
        entries = rate.get("entries") if isinstance(rate, Mapping) else []
        if not entries and not report.get("rate_limit_operator_evidence_ref"):
            errors.append("rate_limit_status verified_passed requires header or operator evidence.")

    public_claim = report.get("public_claim_review")
    if not isinstance(public_claim, Mapping):
        errors.append("public_claim_review must be present.")
    else:
        for key in (
            "production_readiness_claimed",
            "hosted_public_search_live_claimed",
            "live_connector_claimed",
            "download_upload_account_claimed",
            "master_index_mutation_claimed",
        ):
            if public_claim.get(key) is not False:
                errors.append(f"public_claim_review.{key} must be false.")

    operator_actions = report.get("operator_actions_required")
    if not isinstance(operator_actions, list) or not operator_actions:
        errors.append("operator_actions_required must be a non-empty list.")
    if _has_unverified_status(report) and not operator_actions:
        errors.append("operator actions are required when deployment evidence is unverified/gated.")

    remaining = report.get("remaining_blockers")
    if not isinstance(remaining, list) or not remaining:
        errors.append("remaining_blockers must be a non-empty list.")

    if report.get("hosted_backend_status") in {"not_configured", "operator_gated"}:
        warnings.append("Hosted backend remains unverified/operator-gated.")
    if report.get("static_site_status") in {"verified_failed", "unreachable"}:
        warnings.append("Configured static URL exists but did not pass verification.")


def _has_unverified_status(report: Mapping[str, Any]) -> bool:
    return any(
        report.get(field) in {"not_configured", "configured_unverified", "verified_failed", "unreachable", "operator_gated", "evidence_unavailable"}
        for field in STATUS_FIELDS
    )


def _format_plain(result: Mapping[str, Any]) -> str:
    lines = [
        "Public Hosted Deployment Evidence validation",
        f"status: {result['status']}",
        f"report_id: {result.get('report_id')}",
        f"static_site_status: {result.get('static_site_status')}",
        f"hosted_backend_status: {result.get('hosted_backend_status')}",
        f"deployment_verified: {result.get('deployment_verified')}",
    ]
    if result.get("errors"):
        lines.append("errors:")
        lines.extend(f"- {error}" for error in result["errors"])
    if result.get("warnings"):
        lines.append("warnings:")
        lines.extend(f"- {warning}" for warning in result["warnings"])
    return "\n".join(lines) + "\n"


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Emit JSON validation output.")
    args = parser.parse_args(list(argv) if argv is not None else None)
    result = validate_public_hosted_deployment_evidence()
    output = stdout or sys.stdout
    if args.json:
        output.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    else:
        output.write(_format_plain(result))
    return 0 if result["status"] == "valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
