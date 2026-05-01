#!/usr/bin/env python3
"""Validate Public Search Safety Evidence v0."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
AUDIT_DIR = REPO_ROOT / "control" / "audits" / "public-search-safety-evidence-v0"
REPORT_PATH = AUDIT_DIR / "public_search_safety_evidence_report.json"
RUNNER = REPO_ROOT / "scripts" / "run_public_search_safety_evidence.py"
DOC_PATH = REPO_ROOT / "docs" / "operations" / "PUBLIC_SEARCH_SAFETY_EVIDENCE.md"
REQUIRED_AUDIT_FILES = {
    "README.md",
    "SAFETY_SUMMARY.md",
    "SAFE_QUERY_EVIDENCE.md",
    "BLOCKED_REQUEST_EVIDENCE.md",
    "LIMIT_AND_TIMEOUT_EVIDENCE.md",
    "STATUS_ENDPOINT_EVIDENCE.md",
    "STATIC_HANDOFF_SAFETY_REVIEW.md",
    "PUBLIC_INDEX_SAFETY_REVIEW.md",
    "HOSTED_WRAPPER_SAFETY_REVIEW.md",
    "RATE_LIMIT_AND_EDGE_STATUS.md",
    "PRIVACY_AND_REDACTION_REVIEW.md",
    "PUBLIC_CLAIM_REVIEW.md",
    "REMAINING_BLOCKERS.md",
    "NEXT_STEPS.md",
    "COMMAND_RESULTS.md",
    "public_search_safety_evidence_report.json",
}
REQUIRED_FORBIDDEN_CATEGORIES = {
    "credential",
    "download",
    "install_execute",
    "live_mode",
    "live_probe",
    "local_path",
    "query_limit",
    "raw_payload",
    "required_query",
    "result_limit",
    "upload",
    "url_fetch",
}
REQUIRED_HARD_FALSE = {
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
    "hosted_deployment_claimed",
}
PRIVATE_MARKERS = (
    "c:\\",
    "d:\\",
    "/users/",
    "/home/",
    "/tmp/",
    "/var/",
    "secret-value",
)


def validate_public_search_safety_evidence(*, run_evidence: bool = True) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    if not AUDIT_DIR.is_dir():
        errors.append("control/audits/public-search-safety-evidence-v0: missing audit directory.")
    for name in sorted(REQUIRED_AUDIT_FILES):
        if not (AUDIT_DIR / name).is_file():
            errors.append(f"control/audits/public-search-safety-evidence-v0/{name}: missing.")
    if not RUNNER.is_file():
        errors.append("scripts/run_public_search_safety_evidence.py: missing.")
    if not DOC_PATH.is_file():
        errors.append("docs/operations/PUBLIC_SEARCH_SAFETY_EVIDENCE.md: missing.")

    report = _load_json(REPORT_PATH, errors)
    if isinstance(report, Mapping):
        _validate_report(report, errors)

    evidence_report: Mapping[str, Any] = {}
    if run_evidence and not errors:
        try:
            if str(REPO_ROOT) not in sys.path:
                sys.path.insert(0, str(REPO_ROOT))
            from scripts.run_public_search_safety_evidence import (  # noqa: WPS433
                run_public_search_safety_evidence,
            )

            evidence_report = run_public_search_safety_evidence()
        except Exception as exc:  # pragma: no cover - defensive validation
            errors.append(f"run_public_search_safety_evidence failed: {exc}")
        else:
            if evidence_report.get("ok") is not True:
                errors.append("run_public_search_safety_evidence did not return ok=true.")
            _validate_evidence_output(evidence_report, errors)

    _validate_docs(errors)

    return {
        "status": "valid" if not errors else "invalid",
        "created_by": "public_search_safety_evidence_validator_v0",
        "report_id": report.get("report_id") if isinstance(report, Mapping) else None,
        "safe_query_count": len(report.get("safe_query_evidence", [])) if isinstance(report, Mapping) else 0,
        "blocked_request_count": len(report.get("blocked_request_evidence", [])) if isinstance(report, Mapping) else 0,
        "forbidden_categories": sorted(
            set(
                _mapping(report.get("forbidden_parameter_coverage")).get("covered_categories", [])
                if isinstance(report, Mapping)
                else []
            )
        ),
        "errors": errors,
        "warnings": warnings,
    }


def _validate_report(report: Mapping[str, Any], errors: list[str]) -> None:
    expected_scalars = {
        "report_id": "public_search_safety_evidence_v0",
        "created_by_slice": "p57_public_search_safety_evidence_v0",
        "safety_evidence_script": "scripts/run_public_search_safety_evidence.py",
        "safety_validator_script": "scripts/validate_public_search_safety_evidence.py",
        "next_recommended_branch": "P58 Hosted Public Search Rehearsal v0",
    }
    for key, expected in expected_scalars.items():
        if report.get(key) != expected:
            errors.append(f"report: {key} must be {expected!r}.")
    if not report.get("repo_head"):
        errors.append("report: repo_head is required.")
    if report.get("branch") != "main":
        errors.append("report: branch must be main.")
    for key in (
        "route_evidence",
        "safe_query_evidence",
        "blocked_request_evidence",
        "limit_and_timeout_evidence",
        "status_endpoint_evidence",
        "command_results",
        "remaining_blockers",
    ):
        if not isinstance(report.get(key), list) or not report[key]:
            errors.append(f"report: {key} must be a non-empty list.")
    _validate_forbidden_coverage(_mapping(report.get("forbidden_parameter_coverage")), errors)
    _validate_hard_booleans(_mapping(report.get("hard_booleans")), errors)
    _validate_static_handoff(_mapping(report.get("static_handoff_review")), errors)
    _validate_public_index(_mapping(report.get("public_index_safety_review")), errors)
    _validate_rate_limit_status(_mapping(report.get("rate_limit_and_edge_status")), errors)
    _validate_public_claims(_mapping(report.get("public_claim_review")), errors)
    text = json.dumps(report, sort_keys=True).casefold()
    for marker in PRIVATE_MARKERS:
        if marker in text:
            errors.append(f"report: private or secret marker {marker!r} detected.")


def _validate_evidence_output(report: Mapping[str, Any], errors: list[str]) -> None:
    if report.get("mode") != "local_index_only":
        errors.append("evidence: mode must be local_index_only.")
    if _mapping(report.get("summary")).get("failed_checks") != 0:
        errors.append("evidence: failed_checks must be 0.")
    if len(report.get("safe_query_results", [])) < 4:
        errors.append("evidence: expected at least four safe query results.")
    if len(report.get("blocked_request_results", [])) < 32:
        errors.append("evidence: expected at least 32 blocked request results.")
    _validate_forbidden_coverage(_mapping(report.get("forbidden_parameter_coverage")), errors)
    _validate_hard_booleans(_mapping(report.get("hard_booleans")), errors, require_hosted_claim=False)


def _validate_forbidden_coverage(coverage: Mapping[str, Any], errors: list[str]) -> None:
    covered = set(_string_list(coverage.get("covered_categories")))
    missing = REQUIRED_FORBIDDEN_CATEGORIES - covered
    if missing:
        errors.append(f"forbidden_parameter_coverage: missing categories {sorted(missing)}.")
    if coverage.get("missing_categories") not in ([], None):
        errors.append("forbidden_parameter_coverage: missing_categories must be empty.")
    if coverage.get("passed_blocked_case_count") != coverage.get("blocked_case_count"):
        errors.append("forbidden_parameter_coverage: all blocked cases must pass.")


def _validate_hard_booleans(
    booleans: Mapping[str, Any],
    errors: list[str],
    *,
    require_hosted_claim: bool = True,
) -> None:
    required = set(REQUIRED_HARD_FALSE)
    if not require_hosted_claim:
        required.remove("hosted_deployment_claimed")
        required.remove("ai_runtime_enabled")
    missing = sorted(key for key in required if key not in booleans)
    if missing:
        errors.append(f"hard_booleans: missing {missing}.")
    for key in required:
        if booleans.get(key) is not False:
            errors.append(f"hard_booleans: {key} must be false.")


def _validate_static_handoff(payload: Mapping[str, Any], errors: list[str]) -> None:
    if payload.get("status") != "passed":
        errors.append("static_handoff_review: status must be passed.")
    if payload.get("hosted_backend_verified") is not False:
        errors.append("static_handoff_review: hosted_backend_verified must be false.")
    if payload.get("search_form_enabled") is not False:
        errors.append("static_handoff_review: search_form_enabled must be false.")
    if payload.get("fake_hosted_url_detected") is not False:
        errors.append("static_handoff_review: fake_hosted_url_detected must be false.")


def _validate_public_index(payload: Mapping[str, Any], errors: list[str]) -> None:
    if int(payload.get("document_count", 0) or 0) <= 0:
        errors.append("public_index_safety_review: document_count must be positive.")
    for key in ("contains_live_data", "contains_private_data", "contains_executables", "private_or_secret_marker_detected"):
        if payload.get(key) is not False:
            errors.append(f"public_index_safety_review: {key} must be false.")
    if payload.get("enabled_dangerous_action_count") != 0:
        errors.append("public_index_safety_review: dangerous actions must not be enabled.")


def _validate_rate_limit_status(payload: Mapping[str, Any], errors: list[str]) -> None:
    if payload.get("edge_rate_limit_status") != "operator_gated":
        errors.append("rate_limit_and_edge_status: edge_rate_limit_status must be operator_gated.")
    if payload.get("app_rate_limit_status") not in {"contract_only", "not_implemented"}:
        errors.append("rate_limit_and_edge_status: app_rate_limit_status must be contract_only or not_implemented.")
    if payload.get("hosted_rate_limit_evidence") != "unavailable":
        errors.append("rate_limit_and_edge_status: hosted_rate_limit_evidence must be unavailable.")
    if payload.get("cloudflare_or_edge_claimed") is not False:
        errors.append("rate_limit_and_edge_status: cloudflare_or_edge_claimed must be false.")


def _validate_public_claims(payload: Mapping[str, Any], errors: list[str]) -> None:
    for key, value in payload.items():
        if value is not False:
            errors.append(f"public_claim_review: {key} must be false.")


def _validate_docs(errors: list[str]) -> None:
    if not DOC_PATH.is_file():
        return
    text = DOC_PATH.read_text(encoding="utf-8").casefold()
    required = (
        "safe query",
        "blocked request",
        "static handoff",
        "public index",
        "hosted wrapper",
        "rate-limit",
        "operator-gated",
        "no live probes",
        "no downloads",
        "no production claim",
        "p58 hosted public search rehearsal",
    )
    for phrase in required:
        if phrase not in text:
            errors.append(f"docs/operations/PUBLIC_SEARCH_SAFETY_EVIDENCE.md: missing phrase {phrase!r}.")


def _load_json(path: Path, errors: list[str]) -> Any:
    if not path.is_file():
        errors.append(f"{_rel(path)}: missing.")
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"{_rel(path)}: invalid JSON line {exc.lineno}: {exc.msg}.")
        return {}


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _string_list(value: Any) -> list[str]:
    return [item for item in value if isinstance(item, str)] if isinstance(value, list) else []


def _rel(path: Path) -> str:
    try:
        return path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _format_plain(report: Mapping[str, Any]) -> str:
    lines = [
        "Public Search Safety Evidence validation",
        f"status: {report['status']}",
        f"report_id: {report.get('report_id')}",
        f"safe_query_count: {report.get('safe_query_count')}",
        f"blocked_request_count: {report.get('blocked_request_count')}",
    ]
    if report["errors"]:
        lines.append("errors:")
        lines.extend(f"- {error}" for error in report["errors"])
    if report["warnings"]:
        lines.append("warnings:")
        lines.extend(f"- {warning}" for warning in report["warnings"])
    return "\n".join(lines) + "\n"


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Emit JSON validation report.")
    parser.add_argument("--no-run", action="store_true", help="Validate files without rerunning local evidence.")
    args = parser.parse_args(list(argv) if argv is not None else None)
    report = validate_public_search_safety_evidence(run_evidence=not args.no_run)
    output = stdout or sys.stdout
    if args.json:
        output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        output.write(_format_plain(report))
    return 0 if report["status"] == "valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
