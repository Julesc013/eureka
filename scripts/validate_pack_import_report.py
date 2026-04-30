from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = REPO_ROOT / "contracts" / "packs" / "pack_import_report.v0.json"
EXAMPLES_ROOT = REPO_ROOT / "examples" / "import_reports"
DEFAULT_EXAMPLES = [
    EXAMPLES_ROOT / "validate_only_all_examples.passed.json",
    EXAMPLES_ROOT / "validate_only_private_path.failed.json",
    EXAMPLES_ROOT / "validate_only_unknown_pack_type.failed.json",
]

SCHEMA_VERSION = "pack_import_report_validation.v0"
VALIDATOR_ID = "pack_import_report_validator_v0"

REPORT_STATUSES = {
    "validate_only_passed",
    "validate_only_failed",
    "partial_validation",
    "unsupported_pack_type",
    "blocked_by_policy",
    "unavailable_validator",
    "future_import_not_performed",
}
MODES = {
    "validate_only",
    "stage_local_quarantine_future",
    "inspect_staged_future",
    "local_index_candidate_future",
    "contribution_queue_candidate_future",
}
PACK_TYPES = {
    "source_pack",
    "evidence_pack",
    "index_pack",
    "contribution_pack",
    "master_index_review_queue",
    "ai_output_bundle",
    "unknown",
}
VALIDATION_STATUSES = {"passed", "failed", "unavailable", "unknown_type", "skipped"}
CHECKSUM_STATUSES = {"passed", "failed", "unavailable", "not_applicable"}
SCHEMA_STATUSES = {"passed", "failed", "unavailable"}
PRIVACY_STATUSES = {"public_safe", "local_private", "review_required", "restricted", "unknown", "failed"}
RIGHTS_STATUSES = {"public_metadata_only", "source_terms_apply", "review_required", "restricted", "unknown", "failed"}
RISK_STATUSES = {
    "metadata_only",
    "executable_reference",
    "raw_database_detected",
    "private_data_risk",
    "credential_risk",
    "malware_review_required",
    "unknown",
    "failed",
}
ISSUE_SEVERITIES = {"info", "warning", "error", "blocked"}
ISSUE_TYPES = {
    "schema_error",
    "checksum_error",
    "privacy_error",
    "rights_review_required",
    "risk_review_required",
    "executable_payload_detected",
    "raw_database_detected",
    "private_path_detected",
    "credential_detected",
    "unknown_pack_type",
    "validator_unavailable",
    "unsupported_feature",
    "policy_blocked",
}
NEXT_ACTIONS = {
    "no_action",
    "fix_pack_and_revalidate",
    "keep_local_private",
    "quarantine_future",
    "stage_local_quarantine_future",
    "inspect_future",
    "create_contribution_candidate_future",
    "submit_for_review_future",
    "reject",
    "unsupported",
}
HARD_FALSE_FIELDS = (
    "import_performed",
    "staging_performed",
    "indexing_performed",
    "upload_performed",
    "master_index_mutation_performed",
    "runtime_mutation_performed",
    "network_performed",
)
SECRET_KEY_RE = re.compile(r"(api[_-]?key|auth[_-]?token|password|private[_-]?key|secret)", re.IGNORECASE)
SECRET_VALUE_RE = re.compile(r"(sk-[A-Za-z0-9_-]{8,}|-----BEGIN [A-Z ]*PRIVATE KEY-----)", re.IGNORECASE)
PRIVATE_PATH_RE = re.compile(
    r"([A-Za-z]:[\\/](Users|Documents and Settings|Projects)[\\/]|"
    r"\\\\[^\\/\s]+[\\/][^\\/\s]+[\\/]|"
    r"/(Users|home|var/folders|private/tmp|tmp)/)",
    re.IGNORECASE,
)
POSITIVE_AUTHORITY_PATTERNS = (
    "rights clearance approved",
    "rights clearance complete",
    "rights cleared",
    "malware safety approved",
    "malware safety guaranteed",
    "is malware safe",
    "canonical truth established",
    "accepted as canonical truth",
    "truth authority granted",
)


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate Pack Import Report Format v0 examples or one report.")
    parser.add_argument("--report", help="Validate one pack import report JSON file.")
    parser.add_argument("--all-examples", action="store_true", help="Validate all repo example reports.")
    parser.add_argument("--json", action="store_true", help="Emit structured JSON.")
    parser.add_argument("--strict", action="store_true", help="Require the contract schema and all examples to exist.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    report = validate_reports(
        report_path=Path(args.report) if args.report else None,
        all_examples=args.all_examples or not args.report,
        strict=args.strict,
    )
    stream = stdout or sys.stdout
    if args.json:
        stream.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        stream.write(_format_plain(report))
    return 0 if report["ok"] else 1


def validate_reports(
    *,
    report_path: Path | None = None,
    all_examples: bool = True,
    strict: bool = False,
) -> dict[str, Any]:
    errors: list[str] = []
    checked_reports: list[dict[str, Any]] = []

    if strict and not CONTRACT_PATH.exists():
        errors.append(f"{_rel(CONTRACT_PATH)}: contract schema is missing.")
    elif CONTRACT_PATH.exists():
        _load_json(CONTRACT_PATH, errors)

    targets: list[Path]
    mode = "all_examples" if all_examples else "single_report"
    if all_examples:
        targets = list(DEFAULT_EXAMPLES)
        if strict and not EXAMPLES_ROOT.exists():
            errors.append(f"{_rel(EXAMPLES_ROOT)}: example import reports directory is missing.")
    elif report_path is not None:
        targets = [_resolve(report_path)]
    else:
        targets = []
        errors.append("no report target supplied.")

    for target in targets:
        result = validate_report_file(target)
        checked_reports.append(result)
        errors.extend(f"{result['path']}: {error}" for error in result["errors"])

    summary = _summarize(checked_reports)
    return {
        "schema_version": SCHEMA_VERSION,
        "validator_id": VALIDATOR_ID,
        "ok": not errors,
        "mode": mode,
        "strict": strict,
        "checked_reports": checked_reports,
        "summary": summary,
        "errors": errors,
        "network_performed": False,
        "mutation_performed": False,
        "import_performed": False,
        "staging_performed": False,
        "indexing_performed": False,
        "upload_performed": False,
        "master_index_mutation_performed": False,
        "runtime_mutation_performed": False,
    }


def validate_report_file(path: Path) -> dict[str, Any]:
    errors: list[str] = []
    resolved = _resolve(path)
    payload = _load_json(resolved, errors)
    if not isinstance(payload, Mapping):
        if not errors:
            errors.append("report must be a JSON object.")
        return _result(resolved, None, errors)

    _validate_report(payload, errors)
    return _result(resolved, payload, errors)


def _validate_report(payload: Mapping[str, Any], errors: list[str]) -> None:
    required = {
        "schema_version",
        "report_id",
        "report_version",
        "report_kind",
        "report_status",
        "mode",
        "created_by_tool",
        "input_roots",
        "pack_results",
        "validation_summary",
        "privacy_rights_risk_summary",
        "provenance_summary",
        "mutation_summary",
        "next_actions",
        "limitations",
        "notes",
    }
    for field in sorted(required):
        if field not in payload:
            errors.append(f"{field}: required field is missing.")

    if payload.get("schema_version") != "pack_import_report.v0":
        errors.append("schema_version must be pack_import_report.v0.")
    if payload.get("report_kind") != "pack_import_report":
        errors.append("report_kind must be pack_import_report.")
    _validate_enum(payload.get("report_status"), REPORT_STATUSES, "report_status", errors)
    _validate_enum(payload.get("mode"), MODES, "mode", errors)

    for field in HARD_FALSE_FIELDS:
        if payload.get(field) is not False:
            errors.append(f"{field} must be false.")

    input_roots = payload.get("input_roots")
    if not isinstance(input_roots, list) or not input_roots:
        errors.append("input_roots must be a non-empty array.")
    elif not all(isinstance(item, Mapping) and isinstance(item.get("root"), str) for item in input_roots):
        errors.append("input_roots entries must be objects with a root string.")

    pack_results = payload.get("pack_results")
    if not isinstance(pack_results, list) or not pack_results:
        errors.append("pack_results must be a non-empty array.")
        pack_results = []
    else:
        for index, result in enumerate(pack_results):
            if not isinstance(result, Mapping):
                errors.append(f"pack_results[{index}] must be an object.")
                continue
            _validate_pack_result(result, index, errors)

    _validate_summary(payload.get("validation_summary"), pack_results, errors)
    _validate_privacy_summary(payload.get("privacy_rights_risk_summary"), errors)
    _validate_provenance_summary(payload.get("provenance_summary"), errors)
    _validate_mutation_summary(payload.get("mutation_summary"), errors)
    _validate_next_actions(payload.get("next_actions"), errors)
    _validate_limitations(payload.get("limitations"), "limitations", errors)
    _validate_report_status_consistency(payload, pack_results, errors)
    _validate_no_private_paths_or_secrets(payload, errors)
    _validate_no_authority_claims(payload, errors)


def _validate_pack_result(result: Mapping[str, Any], index: int, errors: list[str]) -> None:
    prefix = f"pack_results[{index}]"
    for field in [
        "pack_root",
        "pack_type",
        "validator_id",
        "validation_status",
        "checksum_status",
        "schema_status",
        "privacy_status",
        "rights_status",
        "risk_status",
        "issue_count",
        "issues",
        "record_counts",
        "limitations",
        "recommended_next_action",
    ]:
        if field not in result:
            errors.append(f"{prefix}.{field}: required field is missing.")

    _validate_enum(result.get("pack_type"), PACK_TYPES, f"{prefix}.pack_type", errors)
    _validate_enum(result.get("validation_status"), VALIDATION_STATUSES, f"{prefix}.validation_status", errors)
    _validate_enum(result.get("checksum_status"), CHECKSUM_STATUSES, f"{prefix}.checksum_status", errors)
    _validate_enum(result.get("schema_status"), SCHEMA_STATUSES, f"{prefix}.schema_status", errors)
    _validate_enum(result.get("privacy_status"), PRIVACY_STATUSES, f"{prefix}.privacy_status", errors)
    _validate_enum(result.get("rights_status"), RIGHTS_STATUSES, f"{prefix}.rights_status", errors)
    _validate_enum(result.get("risk_status"), RISK_STATUSES, f"{prefix}.risk_status", errors)
    _validate_enum(result.get("recommended_next_action"), NEXT_ACTIONS, f"{prefix}.recommended_next_action", errors)

    issues = result.get("issues")
    if not isinstance(issues, list):
        errors.append(f"{prefix}.issues must be an array.")
        issues = []
    for issue_index, issue in enumerate(issues):
        if not isinstance(issue, Mapping):
            errors.append(f"{prefix}.issues[{issue_index}] must be an object.")
            continue
        _validate_issue(issue, f"{prefix}.issues[{issue_index}]", errors)

    if result.get("issue_count") != len(issues):
        errors.append(f"{prefix}.issue_count must match issues length.")
    if not isinstance(result.get("record_counts"), Mapping):
        errors.append(f"{prefix}.record_counts must be an object.")
    elif any(not isinstance(value, int) or value < 0 for value in result["record_counts"].values()):
        errors.append(f"{prefix}.record_counts values must be non-negative integers.")
    _validate_limitations(result.get("limitations"), f"{prefix}.limitations", errors)


def _validate_issue(issue: Mapping[str, Any], field: str, errors: list[str]) -> None:
    for required in ["issue_id", "severity", "issue_type", "message"]:
        if required not in issue:
            errors.append(f"{field}.{required}: required field is missing.")
    _validate_enum(issue.get("severity"), ISSUE_SEVERITIES, f"{field}.severity", errors)
    _validate_enum(issue.get("issue_type"), ISSUE_TYPES, f"{field}.issue_type", errors)
    if issue.get("severity") in {"error", "blocked"} and not issue.get("remediation"):
        errors.append(f"{field}.remediation is required for error or blocked issues.")


def _validate_summary(value: Any, pack_results: Sequence[Mapping[str, Any]], errors: list[str]) -> None:
    if not isinstance(value, Mapping):
        errors.append("validation_summary must be an object.")
        return
    expected = {
        "total": len(pack_results),
        "passed": 0,
        "failed": 0,
        "unavailable": 0,
        "unknown_type": 0,
        "skipped": 0,
    }
    for result in pack_results:
        status = result.get("validation_status")
        if status in expected and status != "total":
            expected[status] += 1
    for key, expected_value in expected.items():
        if value.get(key) != expected_value:
            errors.append(f"validation_summary.{key} must be {expected_value}.")


def _validate_privacy_summary(value: Any, errors: list[str]) -> None:
    if not isinstance(value, Mapping):
        errors.append("privacy_rights_risk_summary must be an object.")
        return
    for field in [
        "privacy_issues",
        "rights_issues",
        "risk_issues",
        "private_path_issues",
        "credential_issues",
        "executable_payload_issues",
        "raw_database_issues",
    ]:
        if not isinstance(value.get(field), int) or value.get(field) < 0:
            errors.append(f"privacy_rights_risk_summary.{field} must be a non-negative integer.")


def _validate_provenance_summary(value: Any, errors: list[str]) -> None:
    if not isinstance(value, Mapping):
        errors.append("provenance_summary must be an object.")
        return
    for field in ["input_roots_recorded", "pack_checksums_recorded", "validator_commands_recorded"]:
        if not isinstance(value.get(field), bool):
            errors.append(f"provenance_summary.{field} must be boolean.")
    if not isinstance(value.get("source_reports"), list):
        errors.append("provenance_summary.source_reports must be an array.")


def _validate_mutation_summary(value: Any, errors: list[str]) -> None:
    if not isinstance(value, Mapping):
        errors.append("mutation_summary must be an object.")
        return
    for field in HARD_FALSE_FIELDS:
        if value.get(field) is not False:
            errors.append(f"mutation_summary.{field} must be false.")
    files_written = value.get("files_written")
    if not isinstance(files_written, list):
        errors.append("mutation_summary.files_written must be an array.")
    elif any(not isinstance(item, str) for item in files_written):
        errors.append("mutation_summary.files_written entries must be strings.")
    if not isinstance(value.get("notes"), list):
        errors.append("mutation_summary.notes must be an array.")


def _validate_next_actions(value: Any, errors: list[str]) -> None:
    if not isinstance(value, list) or not value:
        errors.append("next_actions must be a non-empty array.")
        return
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            errors.append(f"next_actions[{index}] must be an object.")
            continue
        _validate_enum(item.get("action"), NEXT_ACTIONS, f"next_actions[{index}].action", errors)
        if not isinstance(item.get("reason"), str) or not item.get("reason"):
            errors.append(f"next_actions[{index}].reason must be a non-empty string.")


def _validate_limitations(value: Any, field: str, errors: list[str]) -> None:
    if not isinstance(value, list) or not value:
        errors.append(f"{field} must be a non-empty array.")
    elif any(not isinstance(item, str) or not item for item in value):
        errors.append(f"{field} entries must be non-empty strings.")


def _validate_report_status_consistency(
    payload: Mapping[str, Any], pack_results: Sequence[Mapping[str, Any]], errors: list[str]
) -> None:
    status = payload.get("report_status")
    validation_statuses = [result.get("validation_status") for result in pack_results]
    issue_severities = [
        issue.get("severity")
        for result in pack_results
        for issue in result.get("issues", [])
        if isinstance(issue, Mapping)
    ]
    issue_types = [
        issue.get("issue_type")
        for result in pack_results
        for issue in result.get("issues", [])
        if isinstance(issue, Mapping)
    ]
    if status == "validate_only_passed":
        if any(item != "passed" for item in validation_statuses):
            errors.append("report_status validate_only_passed requires every pack_result validation_status to be passed.")
        if any(severity in {"error", "blocked"} for severity in issue_severities):
            errors.append("report_status validate_only_passed cannot include error or blocked issues.")
    if status == "validate_only_failed" and "failed" not in validation_statuses:
        errors.append("report_status validate_only_failed requires at least one failed pack_result.")
    if status == "unsupported_pack_type":
        if "unknown_type" not in validation_statuses and "unknown_pack_type" not in issue_types:
            errors.append("report_status unsupported_pack_type requires unknown_type status or unknown_pack_type issue.")
    if status == "unavailable_validator":
        if "unavailable" not in validation_statuses and "validator_unavailable" not in issue_types:
            errors.append("report_status unavailable_validator requires unavailable status or validator_unavailable issue.")


def _validate_no_private_paths_or_secrets(payload: Mapping[str, Any], errors: list[str]) -> None:
    for path, value in _walk(payload):
        key = str(path[-1]) if path else ""
        if SECRET_KEY_RE.search(key):
            errors.append(f"{_join(path)}: secret-like field names are not allowed in import reports.")
        if isinstance(value, str):
            if SECRET_VALUE_RE.search(value):
                errors.append(f"{_join(path)}: secret-like value is not allowed in import reports.")
            if PRIVATE_PATH_RE.search(value):
                errors.append(f"{_join(path)}: private absolute paths must be redacted before report validation.")


def _validate_no_authority_claims(payload: Mapping[str, Any], errors: list[str]) -> None:
    for path, value in _walk(payload):
        key = str(path[-1]).lower() if path else ""
        if isinstance(value, bool) and value and key in {"rights_clearance", "malware_safety", "canonical_truth"}:
            errors.append(f"{_join(path)}: import reports cannot claim rights, malware, or truth authority.")
        if isinstance(value, str):
            lowered = value.lower()
            for phrase in POSITIVE_AUTHORITY_PATTERNS:
                if phrase in lowered:
                    errors.append(f"{_join(path)}: import reports cannot claim {phrase}.")


def _validate_enum(value: Any, allowed: set[str], field: str, errors: list[str]) -> None:
    if value not in allowed:
        errors.append(f"{field} must be one of {', '.join(sorted(allowed))}.")


def _load_json(path: Path, errors: list[str]) -> Any:
    if not path.exists():
        errors.append(f"{_rel(path)}: file is missing.")
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"{_rel(path)}: invalid JSON: {exc}.")
        return None


def _result(path: Path, payload: Mapping[str, Any] | None, errors: list[str]) -> dict[str, Any]:
    return {
        "path": _rel(path),
        "ok": not errors,
        "report_id": payload.get("report_id") if isinstance(payload, Mapping) else None,
        "report_status": payload.get("report_status") if isinstance(payload, Mapping) else None,
        "mode": payload.get("mode") if isinstance(payload, Mapping) else None,
        "pack_result_count": len(payload.get("pack_results", [])) if isinstance(payload, Mapping) else 0,
        "errors": errors,
    }


def _summarize(results: Sequence[Mapping[str, Any]]) -> dict[str, int]:
    return {
        "total": len(results),
        "passed": sum(1 for result in results if result.get("ok")),
        "failed": sum(1 for result in results if not result.get("ok")),
    }


def _walk(value: Any, path: tuple[Any, ...] = ()) -> list[tuple[tuple[Any, ...], Any]]:
    values = [(path, value)]
    if isinstance(value, Mapping):
        for key, child in value.items():
            values.extend(_walk(child, path + (key,)))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            values.extend(_walk(child, path + (index,)))
    return values


def _join(path: Sequence[Any]) -> str:
    return ".".join(str(item) for item in path) if path else "<root>"


def _resolve(path: Path) -> Path:
    return path if path.is_absolute() else (REPO_ROOT / path).resolve()


def _rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except (OSError, ValueError):
        return path.resolve().as_posix()


def _format_plain(report: Mapping[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "Pack Import Report validation",
        f"status: {'valid' if report['ok'] else 'invalid'}",
        f"mode: {report['mode']}",
        f"strict: {report['strict']}",
        f"summary: total={summary['total']} passed={summary['passed']} failed={summary['failed']}",
        f"network_performed: {report['network_performed']}",
        f"mutation_performed: {report['mutation_performed']}",
        f"import_performed: {report['import_performed']}",
        f"staging_performed: {report['staging_performed']}",
        f"indexing_performed: {report['indexing_performed']}",
        f"upload_performed: {report['upload_performed']}",
        f"master_index_mutation_performed: {report['master_index_mutation_performed']}",
        f"runtime_mutation_performed: {report['runtime_mutation_performed']}",
    ]
    for result in report.get("checked_reports", []):
        lines.append(f"- {result['path']}: {'passed' if result['ok'] else 'failed'} ({result['report_status']})")
    if report["errors"]:
        lines.append("")
        lines.append("Errors")
        lines.extend(f"- {error}" for error in report["errors"])
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
