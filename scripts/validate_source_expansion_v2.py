from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
AUDIT_DIR = REPO_ROOT / "control" / "audits" / "search-usefulness-source-expansion-v2"
REPORT_PATH = AUDIT_DIR / "source_expansion_v2_report.json"
QUERY_ROOT = REPO_ROOT / "evals" / "search_usefulness"
SOURCE_DIR = REPO_ROOT / "control" / "inventory" / "sources"

REQUIRED_AUDIT_FILES = {
    "README.md",
    "BASELINE_AUDIT_COUNTS.md",
    "SELECTED_QUERY_TARGETS.md",
    "SOURCE_FAMILY_SELECTION.md",
    "FIXTURE_INVENTORY.md",
    "NORMALIZATION_AND_INDEXING_NOTES.md",
    "QUERY_IMPACT_MATRIX.md",
    "FINAL_AUDIT_COUNTS.md",
    "REMAINING_GAPS.md",
    "RISKS_AND_LIMITATIONS.md",
    "NEXT_SOURCE_WORK.md",
    "source_expansion_v2_report.json",
}
REQUIRED_SOURCE_IDS = {
    "manual-document-recorded-fixtures",
    "package-registry-recorded-fixtures",
    "review-description-recorded-fixtures",
    "software-heritage-recorded-fixtures",
    "sourceforge-recorded-fixtures",
    "wayback-memento-recorded-fixtures",
}
REQUIRED_SOURCE_FAMILIES = {
    "manual_document_recorded",
    "package_registry_recorded",
    "review_description_recorded",
    "software_heritage_recorded",
    "sourceforge_recorded",
    "wayback_memento_recorded",
}
FORBIDDEN_LIVE_FLAGS = (
    "live_supported",
    "network_required",
    "supports_live_probe",
    "supports_action_paths",
    "auth_required",
    "local_private",
)
FORBIDDEN_REPORT_FLAGS = (
    "live_probes_enabled",
    "downloads_enabled",
    "installs_enabled",
    "uploads_enabled",
    "local_path_search_enabled",
    "telemetry_enabled",
    "hosted_search_claimed",
    "external_baselines_fabricated",
)


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate Search Usefulness Source Expansion v2 fixture-only evidence."
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON report.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    report = validate_source_expansion_v2()
    output = stdout or sys.stdout
    if args.json:
        output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        output.write(_format_plain(report))
    return 0 if report["status"] == "valid" else 1


def validate_source_expansion_v2() -> dict[str, Any]:
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
    query_ids = _load_search_usefulness_query_ids(errors)
    selected_targets = _string_set(report.get("selected_query_targets") if isinstance(report, Mapping) else None)
    missing_targets = sorted(selected_targets - query_ids)
    if missing_targets:
        errors.append(f"source_expansion_v2_report.json: selected targets missing from query pack: {missing_targets}.")
    if len(selected_targets) < 8:
        errors.append("source_expansion_v2_report.json: selected_query_targets must include at least 8 queries.")

    if isinstance(report, Mapping):
        _validate_report(report, errors)
        fixture_paths = _string_list(report.get("fixture_files"))
    else:
        fixture_paths = []

    source_records = _load_source_records(errors)
    _validate_source_records(source_records, errors)
    _validate_fixture_files(fixture_paths, errors)

    return {
        "status": "valid" if not errors else "invalid",
        "created_by": "validate_source_expansion_v2",
        "audit_dir": _rel(AUDIT_DIR),
        "required_audit_files": sorted(REQUIRED_AUDIT_FILES),
        "existing_audit_files": sorted(existing_audit_files),
        "selected_query_count": len(selected_targets),
        "source_record_count": len(source_records),
        "required_source_ids": sorted(REQUIRED_SOURCE_IDS),
        "fixture_files": fixture_paths,
        "errors": errors,
        "warnings": warnings,
    }


def _validate_report(report: Mapping[str, Any], errors: list[str]) -> None:
    expected = {
        "report_id": "search-usefulness-source-expansion-v2",
        "created_by_slice": "search_usefulness_source_expansion_v2",
        "status": "implemented_fixture_only",
        "mode": "local_index_only",
        "next_recommended_milestone": "Search Usefulness Delta v2",
    }
    for key, value in expected.items():
        if report.get(key) != value:
            errors.append(f"source_expansion_v2_report.json: {key} must be {value!r}.")
    if set(_string_list(report.get("source_families_added"))) != REQUIRED_SOURCE_FAMILIES:
        errors.append("source_expansion_v2_report.json: source_families_added does not match required families.")
    if set(_string_list(report.get("source_inventory_records"))) != REQUIRED_SOURCE_IDS:
        errors.append("source_expansion_v2_report.json: source_inventory_records does not match required source IDs.")
    final_counts = _mapping(report.get("final_counts"))
    baseline_counts = _mapping(report.get("baseline_counts"))
    if final_counts.get("source_gap") != 10:
        errors.append("source_expansion_v2_report.json: final_counts.source_gap must be 10 for this recorded run.")
    if baseline_counts.get("source_gap") != 26:
        errors.append("source_expansion_v2_report.json: baseline_counts.source_gap must record 26.")
    external = _mapping(report.get("external_baseline_status"))
    if external.get("automated_external_calls_performed") is not False:
        errors.append("source_expansion_v2_report.json: automated_external_calls_performed must be false.")
    if external.get("external_observations_added") is not False:
        errors.append("source_expansion_v2_report.json: external_observations_added must be false.")
    forbidden = _mapping(report.get("forbidden_behaviors_preserved"))
    for flag in FORBIDDEN_REPORT_FLAGS:
        if forbidden.get(flag) is not False:
            errors.append(f"source_expansion_v2_report.json: {flag} must be false.")
    for item in _list(report.get("selected_query_results")):
        if not isinstance(item, Mapping):
            errors.append("source_expansion_v2_report.json: selected_query_results entries must be objects.")
            continue
        if item.get("final_status") != "partial":
            errors.append(f"source_expansion_v2_report.json: {item.get('query_id')} final_status must be partial.")
        if item.get("first_useful_result_rank") != 1:
            errors.append(f"source_expansion_v2_report.json: {item.get('query_id')} first_useful_result_rank must be 1.")


def _validate_source_records(source_records: Mapping[str, Mapping[str, Any]], errors: list[str]) -> None:
    missing = sorted(REQUIRED_SOURCE_IDS - set(source_records))
    if missing:
        errors.append(f"source inventory: missing source records {missing}.")
    for source_id in sorted(REQUIRED_SOURCE_IDS & set(source_records)):
        record = source_records[source_id]
        capabilities = _mapping(record.get("capabilities"))
        coverage = _mapping(record.get("coverage"))
        if record.get("status") != "active_recorded_fixture":
            errors.append(f"{source_id}: status must be active_recorded_fixture.")
        if record.get("source_family") not in REQUIRED_SOURCE_FAMILIES:
            errors.append(f"{source_id}: source_family is not one of the required v2 families.")
        if _mapping(record.get("connector")).get("status") != "fixture_backed":
            errors.append(f"{source_id}: connector.status must be fixture_backed.")
        if _mapping(record.get("live_access")).get("mode") != "recorded_fixture_only":
            errors.append(f"{source_id}: live_access.mode must be recorded_fixture_only.")
        if _mapping(record.get("extraction_policy")).get("mode") != "recorded_fixture_only":
            errors.append(f"{source_id}: extraction_policy.mode must be recorded_fixture_only.")
        if capabilities.get("fixture_backed") is not True:
            errors.append(f"{source_id}: capabilities.fixture_backed must be true.")
        if capabilities.get("recorded_fixture_backed") is not True:
            errors.append(f"{source_id}: capabilities.recorded_fixture_backed must be true.")
        for flag in FORBIDDEN_LIVE_FLAGS:
            if capabilities.get(flag) is not False:
                errors.append(f"{source_id}: capabilities.{flag} must be false.")
        if coverage.get("connector_mode") != "recorded_fixture_only":
            errors.append(f"{source_id}: coverage.connector_mode must be recorded_fixture_only.")


def _validate_fixture_files(fixture_paths: Sequence[str], errors: list[str]) -> None:
    if fixture_paths != ["runtime/connectors/source_expansion_recorded/fixtures/source_expansion_v2_fixture.json"]:
        errors.append("source_expansion_v2_report.json: fixture_files must point to the source expansion v2 fixture.")
    for fixture in fixture_paths:
        path = REPO_ROOT / fixture
        payload = _load_json(path, errors)
        if not isinstance(payload, Mapping):
            continue
        if payload.get("created_by_slice") != "search_usefulness_source_expansion_v2":
            errors.append(f"{fixture}: created_by_slice is incorrect.")
        records = payload.get("records")
        if not isinstance(records, list) or len(records) != 15:
            errors.append(f"{fixture}: records must contain 15 fixture records.")
            continue
        families = {item.get("source_family") for item in records if isinstance(item, Mapping)}
        if families != REQUIRED_SOURCE_FAMILIES:
            errors.append(f"{fixture}: fixture record families do not match required v2 families.")
        serialized = json.dumps(payload, sort_keys=True).casefold()
        for phrase in ("live api call", "url fetches", "scraping", "crawling"):
            if phrase not in serialized:
                errors.append(f"{fixture}: fixture notes must mention no {phrase}.")


def _load_search_usefulness_query_ids(errors: list[str]) -> set[str]:
    query_ids: set[str] = set()
    for path in sorted(QUERY_ROOT.rglob("*.json")):
        payload = _load_json(path, errors)
        if not isinstance(payload, Mapping):
            continue
        queries = payload.get("queries")
        if not isinstance(queries, list):
            continue
        for item in queries:
            if isinstance(item, Mapping) and isinstance(item.get("id"), str):
                query_ids.add(item["id"])
    return query_ids


def _load_source_records(errors: list[str]) -> dict[str, Mapping[str, Any]]:
    records: dict[str, Mapping[str, Any]] = {}
    for path in sorted(SOURCE_DIR.glob("*.source.json")):
        payload = _load_json(path, errors)
        if isinstance(payload, Mapping) and isinstance(payload.get("source_id"), str):
            records[payload["source_id"]] = payload
    return records


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
        "Search Usefulness Source Expansion v2 validation",
        f"status: {report['status']}",
        f"selected_query_count: {report['selected_query_count']}",
        f"source_record_count: {report['source_record_count']}",
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


def _string_list(value: Any) -> list[str]:
    return [item for item in value if isinstance(item, str)] if isinstance(value, list) else []


def _string_set(value: Any) -> set[str]:
    return set(_string_list(value))


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return str(path)


if __name__ == "__main__":
    raise SystemExit(main())
