from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
AUDIT_DIR = REPO_ROOT / "control" / "audits" / "search-usefulness-delta-v2"
REPORT_PATH = AUDIT_DIR / "delta_report.json"
SOURCE_EXPANSION_REPORT = (
    REPO_ROOT / "control" / "audits" / "search-usefulness-source-expansion-v2" / "source_expansion_v2_report.json"
)

REQUIRED_AUDIT_FILES = {
    "README.md",
    "BASELINE.md",
    "CURRENT_COUNTS.md",
    "STATUS_DELTA.md",
    "QUERY_MOVEMENT.md",
    "FAILURE_MODE_DELTA.md",
    "SOURCE_FAMILY_IMPACT.md",
    "PUBLIC_SEARCH_IMPACT.md",
    "HARD_EVAL_AND_REGRESSION_STATUS.md",
    "EXTERNAL_BASELINE_STATUS.md",
    "REMAINING_GAPS.md",
    "RECOMMENDATIONS.md",
    "DELTA_LIMITATIONS.md",
    "delta_report.json",
}
EXPECTED_BASELINE_COUNTS = {
    "covered": 5,
    "partial": 22,
    "source_gap": 26,
    "capability_gap": 9,
    "unknown": 2,
}
EXPECTED_CURRENT_COUNTS = {
    "covered": 5,
    "partial": 40,
    "source_gap": 10,
    "capability_gap": 7,
    "unknown": 2,
}
EXPECTED_DELTAS = {
    "covered": 0,
    "partial": 18,
    "source_gap": -16,
    "capability_gap": -2,
    "unknown": 0,
}
REQUIRED_SOURCE_FAMILIES = {
    "manual_document_recorded",
    "package_registry_recorded",
    "review_description_recorded",
    "software_heritage_recorded",
    "sourceforge_recorded",
    "wayback_memento_recorded",
}
FORBIDDEN_PHRASES = (
    "beats google",
    "beats internet archive",
    "production search relevance",
    "production-ready",
    "hosted public search is live",
)


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate Search Usefulness Delta v2 evidence.")
    parser.add_argument("--json", action="store_true", help="Emit JSON report.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    report = validate_search_usefulness_delta_v2()
    output = stdout or sys.stdout
    if args.json:
        output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        output.write(_format_plain(report))
    return 0 if report["status"] == "valid" else 1


def validate_search_usefulness_delta_v2() -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    existing_audit_files = []
    for filename in sorted(REQUIRED_AUDIT_FILES):
        path = AUDIT_DIR / filename
        if path.exists():
            existing_audit_files.append(filename)
        else:
            errors.append(f"{_rel(path)}: required audit file is missing.")

    report = _load_json(REPORT_PATH, errors)
    source_report = _load_json(SOURCE_EXPANSION_REPORT, errors)
    current_audit = _run_json_command(["scripts/run_search_usefulness_audit.py", "--json"], errors)
    external_status = _run_json_command(["scripts/report_external_baseline_status.py", "--json"], errors)

    if isinstance(report, Mapping):
        _validate_report(report, errors)
        _validate_against_source_expansion_report(report, source_report, errors)
        _validate_current_audit(report, current_audit, errors)
        _validate_external_status(report, external_status, errors)
    _validate_no_forbidden_claims(errors)

    return {
        "status": "valid" if not errors else "invalid",
        "created_by": "validate_search_usefulness_delta_v2",
        "audit_dir": _rel(AUDIT_DIR),
        "required_audit_files": sorted(REQUIRED_AUDIT_FILES),
        "existing_audit_files": sorted(existing_audit_files),
        "baseline_counts": _mapping(report.get("baseline_counts") if isinstance(report, Mapping) else None),
        "current_counts": _mapping(report.get("current_counts") if isinstance(report, Mapping) else None),
        "query_movement_count": len(_list(report.get("query_movements") if isinstance(report, Mapping) else None)),
        "errors": errors,
        "warnings": warnings,
    }


def _validate_report(report: Mapping[str, Any], errors: list[str]) -> None:
    expected = {
        "report_id": "search-usefulness-delta-v2",
        "created_by_slice": "search_usefulness_delta_v2",
        "status": "implemented_audit_only",
        "next_recommended_milestone": "Source Pack Contract v0",
    }
    for key, value in expected.items():
        if report.get(key) != value:
            errors.append(f"delta_report.json: {key} must be {value!r}.")

    if _mapping(report.get("baseline_counts")) != EXPECTED_BASELINE_COUNTS:
        errors.append("delta_report.json: baseline_counts do not match the P32 baseline.")

    current_counts = _mapping(report.get("current_counts"))
    for key, value in EXPECTED_CURRENT_COUNTS.items():
        if current_counts.get(key) != value:
            errors.append(f"delta_report.json: current_counts.{key} must be {value}.")
    if current_counts.get("total_query_count") != 64:
        errors.append("delta_report.json: current_counts.total_query_count must be 64.")

    if _mapping(report.get("status_deltas")) != EXPECTED_DELTAS:
        errors.append("delta_report.json: status_deltas do not match the P32 delta.")

    movements = _list(report.get("query_movements"))
    if len(movements) < 15:
        errors.append("delta_report.json: query_movements must include the 15 selected P32 targets.")
    for movement in movements:
        if not isinstance(movement, Mapping):
            errors.append("delta_report.json: query_movements entries must be objects.")
            continue
        if movement.get("baseline_status") != "source_gap":
            errors.append(f"delta_report.json: {movement.get('query_id')} baseline_status must be source_gap.")
        if movement.get("current_status") != "partial":
            errors.append(f"delta_report.json: {movement.get('query_id')} current_status must be partial.")
        if movement.get("movement") != "source_gap_to_partial":
            errors.append(f"delta_report.json: {movement.get('query_id')} movement must be source_gap_to_partial.")
        if movement.get("source_family") not in REQUIRED_SOURCE_FAMILIES:
            errors.append(f"delta_report.json: {movement.get('query_id')} source_family is not a required v2 family.")

    impact_families = {
        item.get("source_family") for item in _list(report.get("source_family_impacts")) if isinstance(item, Mapping)
    }
    if impact_families != REQUIRED_SOURCE_FAMILIES:
        errors.append("delta_report.json: source_family_impacts must include all six Source Expansion v2 families.")

    external = _mapping(report.get("external_baseline_status"))
    if external.get("automated_external_calls_performed") is not False:
        errors.append("delta_report.json: automated_external_calls_performed must be false.")
    if external.get("external_observations_added") is not False:
        errors.append("delta_report.json: external_observations_added must be false.")
    if _mapping(external.get("global_slot_counts")).get("observed") != 0:
        errors.append("delta_report.json: observed external baseline count must remain 0.")

    hard = _mapping(report.get("hard_eval_status"))
    if _mapping(hard.get("archive_resolution_eval_status_counts")).get("satisfied") != 6:
        errors.append("delta_report.json: archive_resolution_eval_status_counts.satisfied must be 6.")
    if hard.get("regressions_found") is not False:
        errors.append("delta_report.json: hard_eval_status.regressions_found must be false.")

    public = _mapping(report.get("public_search_status"))
    if public.get("smoke_status") != "passed":
        errors.append("delta_report.json: public_search_status.smoke_status must be passed.")
    for flag in (
        "hosted_public_deployment",
        "live_probes_enabled",
        "downloads_enabled",
        "installs_enabled",
        "uploads_enabled",
        "local_paths_enabled",
        "telemetry_enabled",
    ):
        if public.get(flag) is not False:
            errors.append(f"delta_report.json: public_search_status.{flag} must be false.")

    remaining = _mapping(report.get("remaining_gaps"))
    if len(_string_list(remaining.get("source_gap"))) != 10:
        errors.append("delta_report.json: remaining_gaps.source_gap must list 10 current source gaps.")
    if len(_string_list(remaining.get("capability_gap"))) != 7:
        errors.append("delta_report.json: remaining_gaps.capability_gap must list 7 current capability gaps.")


def _validate_against_source_expansion_report(report: Mapping[str, Any], source_report: Any, errors: list[str]) -> None:
    if not isinstance(source_report, Mapping):
        return
    if _mapping(source_report.get("baseline_counts")) != _mapping(report.get("baseline_counts")):
        errors.append("delta_report.json: baseline_counts must match Source Expansion v2 report.")
    source_final = _mapping(source_report.get("final_counts"))
    report_current = dict(_mapping(report.get("current_counts")))
    report_current.pop("total_query_count", None)
    if source_final != report_current:
        errors.append("delta_report.json: current_counts must match Source Expansion v2 final_counts.")
    if _mapping(source_report.get("delta")) != _mapping(report.get("status_deltas")):
        errors.append("delta_report.json: status_deltas must match Source Expansion v2 delta.")


def _validate_current_audit(report: Mapping[str, Any], current_audit: Any, errors: list[str]) -> None:
    if not isinstance(current_audit, Mapping):
        return
    audit_counts = _mapping(current_audit.get("eureka_status_counts"))
    current_counts = _mapping(report.get("current_counts"))
    for key, value in EXPECTED_CURRENT_COUNTS.items():
        if audit_counts.get(key) != value or current_counts.get(key) != value:
            errors.append(f"current audit: {key} must be {value}.")
    if current_audit.get("total_query_count") != current_counts.get("total_query_count"):
        errors.append("delta_report.json: total_query_count must match current audit output.")
    report_failure_modes = _mapping(_mapping(report.get("failure_mode_deltas")).get("current_counts"))
    audit_failure_modes = _mapping(current_audit.get("failure_mode_counts"))
    for key in ("external_baseline_pending", "source_coverage_gap", "compatibility_evidence_gap"):
        if report_failure_modes.get(key) != audit_failure_modes.get(key):
            errors.append(f"delta_report.json: failure_mode_deltas.current_counts.{key} must match current audit.")


def _validate_external_status(report: Mapping[str, Any], external_status: Any, errors: list[str]) -> None:
    if not isinstance(external_status, Mapping):
        return
    report_external = _mapping(report.get("external_baseline_status"))
    global_counts = _mapping(external_status.get("global_slot_counts"))
    if global_counts.get("observed") != 0:
        errors.append("external baseline status: observed count must remain 0 unless committed observations exist.")
    if global_counts != _mapping(report_external.get("global_slot_counts")):
        errors.append("delta_report.json: external global_slot_counts must match external baseline status report.")
    if external_status.get("validation_status") != "valid":
        errors.append("external baseline status report must be valid.")


def _validate_no_forbidden_claims(errors: list[str]) -> None:
    for path in sorted(AUDIT_DIR.glob("*")):
        if not path.is_file() or path.suffix.lower() not in {".md", ".json"}:
            continue
        text = path.read_text(encoding="utf-8").casefold()
        for phrase in FORBIDDEN_PHRASES:
            if phrase in text:
                errors.append(f"{_rel(path)}: forbidden unsupported claim phrase {phrase!r}.")


def _run_json_command(args: Sequence[str], errors: list[str]) -> Any:
    command = [sys.executable, *args]
    completed = subprocess.run(
        command,
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        errors.append(f"{' '.join(args)} failed with exit code {completed.returncode}: {completed.stderr.strip()}")
        return None
    try:
        return json.loads(completed.stdout)
    except json.JSONDecodeError as error:
        errors.append(f"{' '.join(args)} did not emit valid JSON: {error}.")
        return None


def _load_json(path: Path, errors: list[str]) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"{_rel(path)}: file is missing.")
    except json.JSONDecodeError as error:
        errors.append(f"{_rel(path)}: invalid JSON: {error}.")
    return None


def _format_plain(report: Mapping[str, Any]) -> str:
    lines = [
        "Search Usefulness Delta v2 validation",
        f"status: {report['status']}",
        f"query_movement_count: {report['query_movement_count']}",
    ]
    if report["errors"]:
        lines.append("")
        lines.append("Errors")
        lines.extend(f"- {error}" for error in report["errors"])
    if report["warnings"]:
        lines.append("")
        lines.append("Warnings")
        lines.extend(f"- {warning}" for warning in report["warnings"])
    return "\n".join(lines) + "\n"


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _string_list(value: Any) -> list[str]:
    return [item for item in value if isinstance(item, str)] if isinstance(value, list) else []


def _rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return str(path)


if __name__ == "__main__":
    raise SystemExit(main())
