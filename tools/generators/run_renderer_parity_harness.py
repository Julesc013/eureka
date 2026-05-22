"""Run semantic parity checks for rendered or projected view-model outputs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from typing import Any, Mapping, Sequence, TextIO

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.validate_renderer_parity_harness import (  # noqa: E402
    MATRIX_PATH,
    REQUIRED_BOUNDARY_FIELDS,
    SCHEMA_VERSION,
)


REPORT_SCHEMA_VERSION = "track_a_16_renderer_parity_report.v0"
TASK_ID = "TRACK-A-16"
DEFAULT_REPORT_PATH = "control/audits/track-a-16-renderer-parity-harness-v0/renderer_parity_report.json"
FUTURE_CASE_STATUSES = {"deferred", "future", "no_active_outputs_required", "skipped"}
TEXTUAL_OUTPUT_KINDS = {
    "file_tree_static",
    "html32_future",
    "lite_static_html",
    "standard_static_html",
    "terminal_future",
    "text_static",
}
JSON_OUTPUT_KINDS = {
    "native_card_future",
    "relay_future",
    "snapshot_future",
    "static_json_handoff",
}
FORBIDDEN_TEXT_PATTERNS: dict[str, tuple[re.Pattern[str], ...]] = {
    "enabled_hosting": (
        re.compile(r"\bhosted backend (?:is )?(?:active|live|enabled|configured|deployed)\b", re.IGNORECASE),
    ),
    "enabled_live_probes": (
        re.compile(r"\blive probes? (?:are )?enabled\b", re.IGNORECASE),
    ),
    "enabled_source_sync": (
        re.compile(r"\bsource sync (?:is )?enabled\b", re.IGNORECASE),
    ),
    "enabled_source_connectors": (
        re.compile(r"\bsource connectors? (?:are )?active\b", re.IGNORECASE),
    ),
    "enabled_downloads": (
        re.compile(r"\b(?:direct )?downloads? (?:are )?enabled\b", re.IGNORECASE),
    ),
    "enabled_installers": (
        re.compile(r"\binstallers? (?:are )?enabled\b", re.IGNORECASE),
    ),
    "enabled_execution": (
        re.compile(r"\bexecution (?:is )?enabled\b", re.IGNORECASE),
    ),
    "enabled_uploads": (
        re.compile(r"\buploads? (?:are )?enabled\b", re.IGNORECASE),
    ),
    "enabled_accounts": (
        re.compile(r"\baccounts? (?:are )?enabled\b", re.IGNORECASE),
    ),
    "enabled_telemetry": (
        re.compile(r"\btelemetry (?:is )?enabled\b", re.IGNORECASE),
    ),
    "claimed_rights_clearance": (
        re.compile(r"\brights clearance (?:is )?(?:granted|verified|claimed|cleared)\b", re.IGNORECASE),
    ),
    "claimed_malware_safety": (
        re.compile(r"\bmalware safety (?:is )?(?:verified|claimed|cleared)\b", re.IGNORECASE),
    ),
    "claimed_verified_installability": (
        re.compile(r"\bverified installability\b", re.IGNORECASE),
    ),
    "claimed_exhaustive_global_search": (
        re.compile(r"\bexhaustive global search\b", re.IGNORECASE),
    ),
    "claimed_automatic_merge_or_promotion": (
        re.compile(r"\bautomatic (?:merge|dedup|promotion) (?:is )?(?:enabled|allowed)\b", re.IGNORECASE),
    ),
    "claimed_google_affiliation": (
        re.compile(r"\baffiliated with google\b", re.IGNORECASE),
        re.compile(r"\bpowered by google\b", re.IGNORECASE),
        re.compile(r"\bgoogle affiliation\b", re.IGNORECASE),
    ),
    "mutated_master_index": (
        re.compile(r"\bmaster[- ]index mutation (?:is )?(?:enabled|allowed|performed)\b", re.IGNORECASE),
    ),
}
JSON_TRUE_BOUNDARY_FIELDS = {
    "accepted_public_status": "claimed_public_truth",
    "accounts_enabled": "enabled_accounts",
    "automatic_merge_enabled": "claimed_automatic_merge_or_promotion",
    "automatic_promotion_enabled": "claimed_automatic_merge_or_promotion",
    "direct_download_enabled": "enabled_downloads",
    "downloads_enabled": "enabled_downloads",
    "execution_enabled": "enabled_execution",
    "hosted_backend_active": "enabled_hosting",
    "hosted_backend_claimed": "enabled_hosting",
    "installers_enabled": "enabled_installers",
    "live_probes_enabled": "enabled_live_probes",
    "malware_safety_claimed": "claimed_malware_safety",
    "master_index_mutation_allowed": "mutated_master_index",
    "rights_clearance_claimed": "claimed_rights_clearance",
    "source_connectors_active": "enabled_source_connectors",
    "source_sync_enabled": "enabled_source_sync",
    "telemetry_enabled": "enabled_telemetry",
    "uploads_enabled": "enabled_uploads",
    "verified_installability_claimed": "claimed_verified_installability",
}


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Eureka renderer parity checks.")
    parser.add_argument("--repo-root", default=str(REPO_ROOT), help="Repository root to inspect.")
    parser.add_argument("--matrix", default=MATRIX_PATH, help="Renderer parity check matrix path.")
    parser.add_argument("--json-output", help="Write deterministic JSON report to an explicit path.")
    parser.add_argument("--check", action="store_true", help="Return nonzero on parity failure.")
    parser.add_argument("--case", dest="case_id", help="Run a single parity case ID.")
    parser.add_argument("--list", action="store_true", help="List parity cases and exit.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    root = Path(args.repo_root).resolve()
    matrix_path = _resolve_repo_path(Path(args.matrix), root)
    matrix = _load_json(matrix_path)
    output = stdout or sys.stdout

    if args.list:
        for record in _matrix_records(matrix):
            output.write(
                f"{record.get('parity_case_id')}: {record.get('case_status')} "
                f"{record.get('view_family')} {record.get('route_family')}\n"
            )
        return 0

    report = run_renderer_parity_harness(root, matrix_path=matrix_path, case_id=args.case_id)
    if args.json_output:
        report_path = _resolve_repo_path(Path(args.json_output), root)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    output.write(_format_plain(report))
    if args.check and report["status"] == "fail":
        return 1
    return 0 if report["status"] != "fail" else 1


def run_renderer_parity_harness(
    repo_root: Path = REPO_ROOT,
    *,
    matrix_path: Path | None = None,
    case_id: str | None = None,
) -> dict[str, Any]:
    root = repo_root.resolve()
    matrix_file = _resolve_repo_path(matrix_path or Path(MATRIX_PATH), root)
    errors: list[str] = []
    warnings: list[str] = []
    critical_boundary_violations: list[str] = []
    active_cases: list[str] = []
    skipped_future_cases: list[str] = []
    case_results: list[dict[str, Any]] = []
    semantic_category_results: dict[str, str] = {}

    try:
        matrix = _load_json(matrix_file)
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        errors.append(f"{_rel(matrix_file, root)}: {exc}")
        matrix = {}

    for record in _matrix_records(matrix):
        record_id = str(record.get("parity_case_id", ""))
        if case_id and record_id != case_id:
            continue
        case_payload, case_source = _load_case_payload(record, root, errors)
        if case_payload is None:
            continue
        status_values = {str(record.get("case_status", "")), str(case_payload.get("case_status", "")), str(case_payload.get("expected_status", ""))}
        if status_values & FUTURE_CASE_STATUSES:
            skipped_future_cases.append(record_id)
            case_results.append(
                {
                    "case_id": record_id,
                    "case_source": case_source,
                    "status": "skipped",
                    "reason": "future_or_no_active_outputs_required",
                    "output_results": [],
                    "errors": [],
                    "warnings": [],
                }
            )
            continue
        active_cases.append(record_id)
        result = run_parity_case(case_payload, root, case_source=case_source)
        case_results.append(result)
        if result["status"] == "fail":
            errors.extend(f"{record_id}: {error}" for error in result["errors"])
            critical_boundary_violations.extend(result["critical_boundary_violations"])
        warnings.extend(f"{record_id}: {warning}" for warning in result["warnings"])
        for category in case_payload.get("required_semantic_categories", []):
            if isinstance(category, str):
                previous = semantic_category_results.get(category)
                semantic_category_results[category] = "pass" if previous in {None, "pass"} and result["status"] == "pass" else "warn"

    if case_id and not active_cases and not skipped_future_cases and not errors:
        errors.append(f"case {case_id!r} was not found")

    status = "pass" if not errors and not warnings else "warn" if not errors else "fail"
    return {
        "schema_version": REPORT_SCHEMA_VERSION,
        "status": status,
        "track": "A",
        "task": TASK_ID,
        "active_cases": sorted(active_cases),
        "skipped_future_cases": sorted(skipped_future_cases),
        "case_results": sorted(case_results, key=lambda item: str(item.get("case_id", ""))),
        "semantic_category_results": dict(sorted(semantic_category_results.items())),
        "warnings": sorted(set(warnings)),
        "critical_boundary_violations": sorted(set(critical_boundary_violations)),
        "errors": sorted(set(errors)),
        "product_boundary": _false_product_boundary(),
        "next_task": "TRACK-A-17 - Track A integration audit",
    }


def run_parity_case(case: Mapping[str, Any], repo_root: Path, *, case_source: str) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    critical_boundary_violations: list[str] = []
    output_results: list[dict[str, Any]] = []
    for binding in case.get("output_bindings", []):
        if not isinstance(binding, Mapping):
            errors.append("output binding must be an object")
            continue
        output_result = check_output_binding(binding, repo_root)
        output_results.append(output_result)
        errors.extend(output_result["errors"])
        warnings.extend(output_result["warnings"])
        critical_boundary_violations.extend(output_result["critical_boundary_violations"])
    status = "pass" if not errors and not warnings else "warn" if not errors else "fail"
    return {
        "case_id": case.get("parity_case_id"),
        "case_source": case_source,
        "status": status,
        "output_results": sorted(output_results, key=lambda item: str(item.get("output_id", ""))),
        "errors": sorted(set(errors)),
        "warnings": sorted(set(warnings)),
        "critical_boundary_violations": sorted(set(critical_boundary_violations)),
    }


def check_output_binding(binding: Mapping[str, Any], repo_root: Path) -> dict[str, Any]:
    output_id = str(binding.get("output_id", "unknown_output"))
    path_value = str(binding.get("output_path", ""))
    output_path = _resolve_repo_path(Path(path_value), repo_root)
    errors: list[str] = []
    warnings: list[str] = []
    critical_boundary_violations: list[str] = []
    markers_checked: list[str] = []
    json_paths_checked: list[str] = []

    if binding.get("exists_required") is True and not output_path.is_file():
        errors.append(f"{path_value}: required output missing")
        return _output_report(output_id, path_value, "fail", errors, warnings, critical_boundary_violations, markers_checked, json_paths_checked)
    if not output_path.is_file():
        warnings.append(f"{path_value}: optional output missing")
        return _output_report(output_id, path_value, "warn", errors, warnings, critical_boundary_violations, markers_checked, json_paths_checked)

    if _is_relative_to(output_path, repo_root / "site" / "dist"):
        errors.append(f"{path_value}: output is under site/dist")

    kind = binding.get("output_kind")
    if kind in JSON_OUTPUT_KINDS or output_path.suffix.lower() == ".json":
        try:
            payload = json.loads(output_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"{path_value}: invalid JSON at line {exc.lineno}: {exc.msg}")
            payload = None
        if payload is not None:
            path_errors, checked = check_json_paths(payload, binding.get("json_paths_required", []), path_value)
            errors.extend(path_errors)
            json_paths_checked.extend(checked)
            claim_errors = check_json_claims_forbidden(payload, binding.get("json_claims_forbidden", []), path_value)
            errors.extend(claim_errors)
            boundary_errors = detect_json_boundary_claims(payload, path_value)
            errors.extend(boundary_errors)
            critical_boundary_violations.extend(boundary_errors)
    else:
        text = output_path.read_text(encoding="utf-8")
        marker_errors, checked = check_text_markers(text, binding.get("text_markers_required", []), path_value)
        errors.extend(marker_errors)
        markers_checked.extend(checked)
        boundary_errors = detect_forbidden_text_claims(text, path_value)
        case_marker_errors = detect_case_forbidden_markers(text, binding.get("text_markers_forbidden", []), path_value)
        errors.extend(boundary_errors)
        errors.extend(case_marker_errors)
        critical_boundary_violations.extend(boundary_errors)
        critical_boundary_violations.extend(case_marker_errors)

    status = "pass" if not errors and not warnings else "warn" if not errors else "fail"
    return _output_report(output_id, path_value, status, errors, warnings, critical_boundary_violations, markers_checked, json_paths_checked)


def check_text_markers(text: str, markers: Any, label: str) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    checked: list[str] = []
    for marker in _string_items(markers):
        checked.append(marker)
        if marker not in text:
            errors.append(f"{label}: missing required marker {marker!r}")
    return errors, checked


def detect_forbidden_text_claims(text: str, label: str) -> list[str]:
    violations: list[str] = []
    for boundary, patterns in FORBIDDEN_TEXT_PATTERNS.items():
        for pattern in patterns:
            if _has_unsafe_match(text, pattern):
                violations.append(f"{label}: {boundary} claim matched {pattern.pattern}")
                break
    return sorted(set(violations))


def detect_case_forbidden_markers(text: str, markers: Any, label: str) -> list[str]:
    violations: list[str] = []
    lowered = text.lower()
    for marker in _string_items(markers):
        marker_lower = marker.lower()
        start = lowered.find(marker_lower)
        if start == -1:
            continue
        prefix = lowered[max(0, start - 40):start]
        if not _prefix_is_negated(prefix):
            violations.append(f"{label}: forbidden marker present {marker!r}")
    return violations


def check_json_paths(payload: Any, paths: Any, label: str) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    checked: list[str] = []
    for path in _string_items(paths):
        checked.append(path)
        found, _value = _get_json_path(payload, path)
        if not found:
            errors.append(f"{label}: missing JSON path {path}")
    return errors, checked


def check_json_claims_forbidden(payload: Any, paths: Any, label: str) -> list[str]:
    errors: list[str] = []
    for path in _string_items(paths):
        found, value = _get_json_path(payload, path)
        if found and value is not False:
            errors.append(f"{label}: forbidden JSON claim {path} must be false")
    return errors


def detect_json_boundary_claims(value: Any, label: str, path: str = "$") -> list[str]:
    violations: list[str] = []
    if isinstance(value, Mapping):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            boundary = JSON_TRUE_BOUNDARY_FIELDS.get(str(key))
            if boundary and child is True:
                violations.append(f"{label}: {child_path} implies {boundary}")
            violations.extend(detect_json_boundary_claims(child, label, child_path))
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        for index, child in enumerate(value):
            violations.extend(detect_json_boundary_claims(child, label, f"{path}[{index}]"))
    return violations


def _load_case_payload(record: Mapping[str, Any], repo_root: Path, errors: list[str]) -> tuple[Mapping[str, Any] | None, str]:
    case_ref = record.get("case_ref")
    if isinstance(case_ref, str) and case_ref:
        try:
            payload = _load_json(repo_root / case_ref)
        except (FileNotFoundError, json.JSONDecodeError) as exc:
            errors.append(f"{case_ref}: {exc}")
            return None, case_ref
        return payload if isinstance(payload, Mapping) else None, case_ref
    inline = record.get("case_inline")
    if isinstance(inline, Mapping):
        return inline, f"{record.get('parity_case_id')}.case_inline"
    errors.append(f"{record.get('parity_case_id')}: missing case_ref or case_inline")
    return None, str(record.get("parity_case_id"))


def _matrix_records(matrix: Any) -> list[Mapping[str, Any]]:
    records = _mapping(matrix).get("parity_cases", [])
    if not isinstance(records, Sequence) or isinstance(records, (str, bytes)):
        return []
    return [record for record in records if isinstance(record, Mapping)]


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _get_json_path(payload: Any, path: str) -> tuple[bool, Any]:
    current = payload
    for part in path.split("."):
        if isinstance(current, Mapping) and part in current:
            current = current[part]
        elif isinstance(current, Sequence) and not isinstance(current, (str, bytes)) and part.isdigit():
            index = int(part)
            if index >= len(current):
                return False, None
            current = current[index]
        else:
            return False, None
    return True, current


def _has_unsafe_match(text: str, pattern: re.Pattern[str]) -> bool:
    for match in pattern.finditer(text):
        prefix = text[max(0, match.start() - 48):match.start()].lower()
        matched = text[match.start():match.end()].lower()
        if not _prefix_is_negated(prefix) and "not " not in matched and "unavailable" not in matched:
            return True
    return False


def _prefix_is_negated(prefix: str) -> bool:
    return (
        " no " in f" {prefix}"
        or " not " in f" {prefix}"
        or "without " in prefix
        or "unavailable" in prefix[-24:]
        or "disabled" in prefix[-24:]
        or "forbidden" in prefix[-32:]
    )


def _false_product_boundary() -> dict[str, bool]:
    return {field: False for field in sorted(REQUIRED_BOUNDARY_FIELDS)}


def _output_report(
    output_id: str,
    path_value: str,
    status: str,
    errors: list[str],
    warnings: list[str],
    critical_boundary_violations: list[str],
    markers_checked: list[str],
    json_paths_checked: list[str],
) -> dict[str, Any]:
    return {
        "output_id": output_id,
        "output_path": path_value,
        "status": status,
        "markers_checked": sorted(markers_checked),
        "json_paths_checked": sorted(json_paths_checked),
        "errors": sorted(set(errors)),
        "warnings": sorted(set(warnings)),
        "critical_boundary_violations": sorted(set(critical_boundary_violations)),
    }


def _resolve_repo_path(path: Path, repo_root: Path) -> Path:
    return path.resolve() if path.is_absolute() else (repo_root / path).resolve()


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def _rel(path: Path, repo_root: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return str(path.resolve())


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _string_items(value: Any) -> list[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return []
    return [item for item in value if isinstance(item, str)]


def _format_plain(report: Mapping[str, Any]) -> str:
    lines = [
        f"run_renderer_parity_harness: {report['status']}",
        f"schema_version: {report['schema_version']}",
        f"active_cases: {len(report.get('active_cases', []))}",
        f"skipped_future_cases: {len(report.get('skipped_future_cases', []))}",
    ]
    for case in report.get("case_results", []):
        if isinstance(case, Mapping):
            lines.append(f"- {case.get('case_id')}: {case.get('status')}")
    if report.get("errors"):
        lines.append("errors:")
        lines.extend(f"- {error}" for error in report["errors"])
    if report.get("warnings"):
        lines.append("warnings:")
        lines.extend(f"- {warning}" for warning in report["warnings"])
    if report.get("critical_boundary_violations"):
        lines.append("critical_boundary_violations:")
        lines.extend(f"- {violation}" for violation in report["critical_boundary_violations"])
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
