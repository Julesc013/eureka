from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
AUDIT_DIR = REPO_ROOT / "control" / "audits" / "public-data-contract-stability-review-v0"
PUBLIC_DATA_DIR = REPO_ROOT / "site/dist" / "data"
PUBLICATION_DIR = REPO_ROOT / "control" / "inventory" / "publication"

REPORT_NAME = "public_data_stability_report.json"
REQUIRED_PACK_FILES = {
    "README.md",
    "CURRENT_PUBLIC_DATA.md",
    "FIELD_STABILITY_MATRIX.md",
    "FILE_STABILITY_DECISIONS.md",
    "VERSIONING_POLICY.md",
    "BREAKING_CHANGE_POLICY.md",
    "CLIENT_CONSUMPTION_GUIDANCE.md",
    "SNAPSHOT_NATIVE_RELAY_IMPACT.md",
    "RISKS.md",
    "NEXT_GUARDS.md",
    REPORT_NAME,
}
REQUIRED_STABILITY_CLASSES = {
    "stable_draft",
    "experimental",
    "volatile",
    "internal",
    "deprecated",
    "future",
}
PRODUCTION_STABLE_MARKERS = {
    "stable",
    "production_stable",
    "production",
    "production_ready",
}
DOCS_REQUIRING_POLICY_REFERENCE = {
    "docs/reference/PUBLIC_DATA_CONTRACT.md",
    "docs/reference/SNAPSHOT_CONSUMER_CONTRACT.md",
    "docs/reference/NATIVE_CLIENT_CONTRACT.md",
    "docs/reference/RELAY_SURFACE_CONTRACT.md",
}


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate Public Data Contract Stability Review v0."
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON report.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    report = validate_public_data_stability()
    output = stdout or sys.stdout
    if args.json:
        output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        output.write(_format_plain(report))
    return 0 if report["status"] == "valid" else 1


def validate_public_data_stability() -> dict[str, Any]:
    errors: list[str] = []

    existing_pack_files = []
    for name in sorted(REQUIRED_PACK_FILES):
        path = AUDIT_DIR / name
        if path.exists():
            existing_pack_files.append(name)
        else:
            errors.append(f"{_rel(path)}: required audit file is missing.")

    report = _load_json(AUDIT_DIR / REPORT_NAME, errors)
    current_public_files = sorted(path.name for path in PUBLIC_DATA_DIR.glob("*.json"))

    covered_files: set[str] = set()
    stable_draft_fields: list[tuple[str, str]] = []
    stability_classes_seen: set[str] = set()

    if isinstance(report, Mapping):
        _validate_report_shape(report, errors)
        covered_files = _covered_public_files(report)
        stability_classes_seen = _stability_classes_seen(report)
        stable_draft_fields = _stable_draft_fields(report)
        _validate_file_decisions(report, errors)
        _validate_field_stability(report, current_public_files, errors)
    else:
        errors.append(f"{_rel(AUDIT_DIR / REPORT_NAME)}: report must be a JSON object.")

    missing_coverage = sorted(set(current_public_files) - covered_files)
    extra_coverage = sorted(covered_files - set(current_public_files))
    if missing_coverage:
        errors.append(f"{REPORT_NAME}: missing public data file coverage {missing_coverage}.")
    if extra_coverage:
        errors.append(f"{REPORT_NAME}: covers non-current public data files {extra_coverage}.")

    missing_classes = sorted(REQUIRED_STABILITY_CLASSES - stability_classes_seen)
    if missing_classes:
        errors.append(f"{REPORT_NAME}: missing stability classes {missing_classes}.")

    _validate_stable_draft_fields_present(stable_draft_fields, errors)
    _validate_public_data_contract(errors)
    _validate_docs(errors)

    return {
        "status": "valid" if not errors else "invalid",
        "created_by": "public_data_contract_stability_review_v0",
        "audit_dir": _rel(AUDIT_DIR),
        "checked_public_data_files": current_public_files,
        "covered_public_data_files": sorted(covered_files),
        "stability_classes": sorted(stability_classes_seen),
        "stable_draft_field_count": len(stable_draft_fields),
        "existing_pack_files": sorted(existing_pack_files),
        "errors": errors,
    }


def _validate_report_shape(report: Mapping[str, Any], errors: list[str]) -> None:
    expected = {
        "report_id": "public-data-contract-stability-review-v0",
        "schema_version": "0.1.0",
        "created_by_slice": "public_data_contract_stability_review_v0",
        "next_recommended_guard": "Generated Artifact Drift Guard v0",
    }
    for key, value in expected.items():
        if report.get(key) != value:
            errors.append(f"{REPORT_NAME}: {key} must be {value!r}.")
    for required in (
        "public_data_files",
        "field_stability",
        "stable_draft_fields",
        "experimental_fields",
        "volatile_fields",
        "internal_fields",
        "consumer_guidance",
        "breaking_change_rules",
        "notes",
    ):
        if required not in report:
            errors.append(f"{REPORT_NAME}: missing {required}.")


def _covered_public_files(report: Mapping[str, Any]) -> set[str]:
    covered: set[str] = set()
    files = report.get("public_data_files")
    if not isinstance(files, list):
        return covered
    for item in files:
        if isinstance(item, Mapping):
            name = item.get("file_name")
            path = item.get("path")
            if isinstance(name, str):
                covered.add(name)
            elif isinstance(path, str):
                covered.add(Path(path).name)
        elif isinstance(item, str):
            covered.add(Path(item).name)
    return covered


def _stability_classes_seen(report: Mapping[str, Any]) -> set[str]:
    seen: set[str] = set()
    classes = report.get("stability_classes")
    if isinstance(classes, Mapping):
        seen.update(str(key) for key in classes)
    field_stability = report.get("field_stability")
    if isinstance(field_stability, Mapping):
        for entries in field_stability.values():
            if isinstance(entries, list):
                for entry in entries:
                    if isinstance(entry, Mapping) and isinstance(entry.get("stability"), str):
                        seen.add(entry["stability"])
    for key in (
        "stable_draft_fields",
        "experimental_fields",
        "volatile_fields",
        "internal_fields",
        "deprecated_fields",
        "future_fields",
    ):
        if key in report:
            seen.add(key.removesuffix("_fields"))
    return seen


def _stable_draft_fields(report: Mapping[str, Any]) -> list[tuple[str, str]]:
    fields: list[tuple[str, str]] = []
    entries = report.get("stable_draft_fields")
    if isinstance(entries, list):
        for entry in entries:
            if isinstance(entry, Mapping):
                file_name = entry.get("file_name")
                field_path = entry.get("field_path")
                if isinstance(file_name, str) and isinstance(field_path, str):
                    fields.append((file_name, field_path))
    field_stability = report.get("field_stability")
    if isinstance(field_stability, Mapping):
        for file_name, entries_for_file in field_stability.items():
            if not isinstance(file_name, str) or not isinstance(entries_for_file, list):
                continue
            for entry in entries_for_file:
                if (
                    isinstance(entry, Mapping)
                    and entry.get("stability") == "stable_draft"
                    and isinstance(entry.get("field_path"), str)
                ):
                    candidate = (file_name, entry["field_path"])
                    if candidate not in fields:
                        fields.append(candidate)
    return fields


def _validate_file_decisions(report: Mapping[str, Any], errors: list[str]) -> None:
    files = report.get("public_data_files")
    if not isinstance(files, list):
        errors.append(f"{REPORT_NAME}: public_data_files must be a list.")
        return
    for item in files:
        if not isinstance(item, Mapping):
            errors.append(f"{REPORT_NAME}: public_data_files entries must be objects.")
            continue
        file_name = item.get("file_name", item.get("path", "<unknown>"))
        stability = str(item.get("stability_class", "")).lower()
        if not stability:
            errors.append(f"{REPORT_NAME}: {file_name} missing stability_class.")
        if stability in PRODUCTION_STABLE_MARKERS:
            errors.append(f"{REPORT_NAME}: {file_name} must not be marked production stable.")
        if item.get("allowed_client_use") in (None, ""):
            errors.append(f"{REPORT_NAME}: {file_name} missing allowed_client_use.")
        if item.get("prohibited_client_use") in (None, ""):
            errors.append(f"{REPORT_NAME}: {file_name} missing prohibited_client_use.")


def _validate_field_stability(
    report: Mapping[str, Any], current_public_files: list[str], errors: list[str]
) -> None:
    field_stability = report.get("field_stability")
    if not isinstance(field_stability, Mapping):
        errors.append(f"{REPORT_NAME}: field_stability must be an object.")
        return
    for file_name in current_public_files:
        entries = field_stability.get(file_name)
        if not isinstance(entries, list) or not entries:
            errors.append(f"{REPORT_NAME}: field_stability missing entries for {file_name}.")
            continue
        for entry in entries:
            if not isinstance(entry, Mapping):
                errors.append(f"{REPORT_NAME}: field_stability.{file_name} entries must be objects.")
                continue
            if not isinstance(entry.get("field_path"), str):
                errors.append(f"{REPORT_NAME}: field_stability.{file_name} entry missing field_path.")
            stability = entry.get("stability")
            if stability not in REQUIRED_STABILITY_CLASSES:
                errors.append(
                    f"{REPORT_NAME}: field_stability.{file_name} has invalid stability {stability!r}."
                )


def _validate_stable_draft_fields_present(
    stable_draft_fields: list[tuple[str, str]], errors: list[str]
) -> None:
    for file_name, field_path in sorted(stable_draft_fields):
        public_data_file = PUBLIC_DATA_DIR / file_name
        payload = _load_json(public_data_file, errors)
        if not isinstance(payload, Mapping):
            continue
        if not _path_exists(payload, field_path):
            errors.append(f"{_rel(public_data_file)}: stable_draft field {field_path} missing.")


def _validate_public_data_contract(errors: list[str]) -> None:
    contract_path = PUBLICATION_DIR / "public_data_contract.json"
    contract = _load_json(contract_path, errors)
    if not isinstance(contract, Mapping):
        return
    if contract.get("stability_policy") != "docs/reference/PUBLIC_DATA_STABILITY_POLICY.md":
        errors.append("public_data_contract.json: stability_policy must reference PUBLIC_DATA_STABILITY_POLICY.md.")
    if contract.get("client_consumption_status") != "field_level_stable_draft_only":
        errors.append("public_data_contract.json: client_consumption_status must be field_level_stable_draft_only.")
    if not isinstance(contract.get("field_stability_summary"), Mapping):
        errors.append("public_data_contract.json: field_stability_summary must be present.")
    entries = contract.get("entries")
    if isinstance(entries, list):
        for entry in entries:
            if not isinstance(entry, Mapping):
                continue
            if str(entry.get("path", "")).startswith("/data/"):
                if str(entry.get("stability", "")).lower() in PRODUCTION_STABLE_MARKERS:
                    errors.append(
                        f"public_data_contract.json: {entry.get('path')} must not be production stable."
                    )


def _validate_docs(errors: list[str]) -> None:
    policy_path = REPO_ROOT / "docs" / "reference" / "PUBLIC_DATA_STABILITY_POLICY.md"
    policy_text = _read_text(policy_path, errors).lower()
    for phrase in (
        "does not make public json a production api",
        "no current public json file is production-stable",
        "stable_draft",
        "experimental",
        "volatile",
        "internal",
    ):
        if phrase not in policy_text:
            errors.append(f"{_rel(policy_path)}: missing phrase {phrase!r}.")

    for relative in sorted(DOCS_REQUIRING_POLICY_REFERENCE):
        path = REPO_ROOT / relative
        text = _read_text(path, errors)
        if "PUBLIC_DATA_STABILITY_POLICY.md" not in text:
            errors.append(f"{relative}: must reference PUBLIC_DATA_STABILITY_POLICY.md.")


def _path_exists(value: Any, field_path: str) -> bool:
    parts = [part for part in field_path.split(".") if part]
    return _path_parts_exist(value, parts)


def _path_parts_exist(value: Any, parts: list[str]) -> bool:
    if not parts:
        return True
    head, *tail = parts
    if head.endswith("[]"):
        key = head[:-2]
        if key:
            if not isinstance(value, Mapping) or key not in value:
                return False
            value = value[key]
        if not isinstance(value, list):
            return False
        if not tail:
            return True
        return any(_path_parts_exist(item, tail) for item in value)
    if not isinstance(value, Mapping) or head not in value:
        return False
    return _path_parts_exist(value[head], tail)


def _load_json(path: Path, errors: list[str]) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"{_rel(path)}: file is missing.")
    except json.JSONDecodeError as exc:
        errors.append(f"{_rel(path)}: invalid JSON: {exc}.")
    return None


def _read_text(path: Path, errors: list[str]) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        errors.append(f"{_rel(path)}: file is missing.")
        return ""


def _format_plain(report: Mapping[str, Any]) -> str:
    lines = [
        "Public data stability validation",
        f"status: {report['status']}",
        f"checked_public_data_files: {len(report['checked_public_data_files'])}",
        f"covered_public_data_files: {len(report['covered_public_data_files'])}",
        f"stable_draft_field_count: {report['stable_draft_field_count']}",
    ]
    if report["errors"]:
        lines.append("")
        lines.append("Errors")
        lines.extend(f"- {error}" for error in report["errors"])
    return "\n".join(lines) + "\n"


def _rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT.resolve())).replace("\\", "/")
    except ValueError:
        return str(path)


if __name__ == "__main__":
    raise SystemExit(main())
