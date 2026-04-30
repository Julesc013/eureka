from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
AUDIT_ROOT = REPO_ROOT / "control" / "audits" / "pack-import-planning-v0"
REPORT_PATH = AUDIT_ROOT / "pack_import_planning_report.json"

REQUIRED_AUDIT_FILES = {
    "README.md",
    "IMPORT_SCOPE.md",
    "IMPORT_MODES.md",
    "STAGING_MODEL.md",
    "VALIDATION_PIPELINE.md",
    "PRIVACY_RIGHTS_RISK_REVIEW.md",
    "PROVENANCE_AND_CLAIM_MODEL.md",
    "LOCAL_SEARCH_AND_INDEX_INTERACTION.md",
    "NATIVE_SNAPSHOT_RELAY_IMPACT.md",
    "MASTER_INDEX_REVIEW_INTERACTION.md",
    "IMPLEMENTATION_BOUNDARIES.md",
    "FUTURE_IMPLEMENTATION_SEQUENCE.md",
    "RISKS_AND_LIMITATIONS.md",
    "NEXT_STEPS.md",
    "pack_import_planning_report.json",
}
REQUIRED_SUPPORTED_PACK_TYPES = {
    "source_pack",
    "evidence_pack",
    "index_pack",
    "contribution_pack",
}
REQUIRED_PROHIBITED_BEHAVIORS = {
    "arbitrary_directory_scan",
    "live_fetch",
    "canonical_registry_merge",
    "hosted_master_index_mutation",
    "raw_db_import",
    "executable_plugin_loading",
}
REQUIRED_PIPELINE_STEPS = {
    "identify_pack_type",
    "parse_manifest",
    "validate_schema",
    "validate_checksums",
    "parse_jsonl_files",
    "validate_privacy_status_consistency",
    "scan_for_forbidden_fields_private_paths",
    "scan_for_executable_payloads_raw_db_cache",
    "validate_rights_access_docs",
    "classify_risk",
    "produce_import_report",
    "stage_or_reject",
    "never_mutate_canonical_records_by_default",
}
REQUIRED_VALIDATOR_COMMANDS = {
    "python scripts/validate_source_pack.py",
    "python scripts/validate_evidence_pack.py",
    "python scripts/validate_index_pack.py",
    "python scripts/validate_contribution_pack.py",
}
OPTIONAL_VALIDATOR_COMMANDS = {
    "python scripts/validate_master_index_review_queue.py",
}
REQUIRED_STAGING_PHRASES = (
    ".eureka-local/staged_packs/",
    ".eureka-local/quarantine/",
    ".eureka-local/import_reports/",
    "private by default",
    "not committed",
    "must not leak",
    "site/dist",
    "external",
)
REQUIRED_SEARCH_PHRASES = (
    "no search impact by default",
    "no index impact by default",
    "local_index_only",
)
REQUIRED_MASTER_INDEX_PHRASES = (
    "no automatic acceptance",
    "never writes the hosted/master index",
    "accepted_public requires a review decision",
)
REQUIRED_DOC_FILES = [
    REPO_ROOT / "docs" / "architecture" / "PACK_IMPORT_PIPELINE.md",
    REPO_ROOT / "docs" / "reference" / "PACK_IMPORT_PLANNING.md",
]
FORBIDDEN_POSITIVE_RUNTIME_CLAIMS = (
    "pack import runtime is implemented",
    "pack import exists",
    "imported packs affect public search",
    "imported packs are accepted by the master index",
    "local imported packs affect public search",
)


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate Pack Import Planning v0 audit pack.")
    parser.add_argument("--json", action="store_true", help="Emit JSON report.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    report = validate_pack_import_planning()
    output = stdout or sys.stdout
    if args.json:
        output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        output.write(_format_plain(report))
    return 0 if report["status"] == "valid" else 1


def validate_pack_import_planning() -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    if not AUDIT_ROOT.exists():
        errors.append(f"{_rel(AUDIT_ROOT)}: audit pack is missing.")
        return _report(None, errors, warnings)

    for filename in sorted(REQUIRED_AUDIT_FILES):
        path = AUDIT_ROOT / filename
        if not path.exists():
            errors.append(f"{_rel(path)}: required audit file is missing.")

    payload = _load_json(REPORT_PATH, errors)
    if isinstance(payload, Mapping):
        _validate_report(payload, errors, warnings)
    else:
        payload = None

    _validate_staging_doc(errors)
    _validate_local_search_doc(errors)
    _validate_master_index_doc(errors)
    _validate_reference_docs(errors)

    return _report(payload, errors, warnings)


def _validate_report(payload: Mapping[str, Any], errors: list[str], warnings: list[str]) -> None:
    if payload.get("status") != "planning_only":
        errors.append("pack_import_planning_report.json: status must be planning_only.")
    if payload.get("import_runtime_implemented") is not False:
        errors.append("pack_import_planning_report.json: import_runtime_implemented must be false.")
    if payload.get("default_future_mode") != "validate_only":
        errors.append("pack_import_planning_report.json: default_future_mode must be validate_only.")
    if payload.get("next_future_mode") != "stage_local_quarantine":
        errors.append("pack_import_planning_report.json: next_future_mode must be stage_local_quarantine.")

    supported = set(_list_of_strings(payload.get("supported_pack_types")))
    missing_pack_types = REQUIRED_SUPPORTED_PACK_TYPES - supported
    if missing_pack_types:
        errors.append(
            "pack_import_planning_report.json: supported_pack_types is missing "
            + ", ".join(sorted(missing_pack_types))
            + "."
        )

    prohibited = set(_list_of_strings(payload.get("prohibited_import_behaviors")))
    missing_prohibited = REQUIRED_PROHIBITED_BEHAVIORS - prohibited
    if missing_prohibited:
        errors.append(
            "pack_import_planning_report.json: prohibited_import_behaviors is missing "
            + ", ".join(sorted(missing_prohibited))
            + "."
        )

    pipeline = payload.get("validation_pipeline")
    if not isinstance(pipeline, Mapping):
        errors.append("pack_import_planning_report.json: validation_pipeline must be an object.")
        return

    steps = set(_list_of_strings(pipeline.get("steps")))
    missing_steps = REQUIRED_PIPELINE_STEPS - steps
    if missing_steps:
        errors.append(
            "pack_import_planning_report.json: validation_pipeline.steps is missing "
            + ", ".join(sorted(missing_steps))
            + "."
        )

    commands = set(_list_of_strings(pipeline.get("validator_commands")))
    missing_commands = REQUIRED_VALIDATOR_COMMANDS - commands
    if missing_commands:
        errors.append(
            "pack_import_planning_report.json: validation_pipeline.validator_commands is missing "
            + ", ".join(sorted(missing_commands))
            + "."
        )
    if not commands.intersection(OPTIONAL_VALIDATOR_COMMANDS):
        warnings.append("validation_pipeline.validator_commands does not mention the review queue validator.")
    for command in sorted(commands):
        script = _script_path_from_command(command)
        if script is not None and not script.exists():
            errors.append(f"pack_import_planning_report.json: referenced validator is missing: {command}.")

    staging_policy = payload.get("staging_policy")
    if isinstance(staging_policy, Mapping):
        if staging_policy.get("create_directories_now") is not False:
            errors.append("pack_import_planning_report.json: staging_policy.create_directories_now must be false.")
        for key in ["private_by_default", "not_committed_to_git", "no_public_leakage"]:
            if staging_policy.get(key) is not True:
                errors.append(f"pack_import_planning_report.json: staging_policy.{key} must be true.")
    else:
        errors.append("pack_import_planning_report.json: staging_policy must be an object.")

    local_search = payload.get("local_search_impact")
    if isinstance(local_search, Mapping):
        if local_search.get("validate_only") != "no_impact":
            errors.append("pack_import_planning_report.json: validate_only must have no local search impact.")
        if local_search.get("stage_local_quarantine") != "no_impact_by_default":
            errors.append("pack_import_planning_report.json: staged quarantine must have no impact by default.")
        if local_search.get("public_search_runtime_impact") != "none":
            errors.append("pack_import_planning_report.json: public search runtime impact must be none.")
    else:
        errors.append("pack_import_planning_report.json: local_search_impact must be an object.")

    master_index = payload.get("master_index_review_impact")
    if isinstance(master_index, Mapping):
        if master_index.get("automatic_acceptance") is not False:
            errors.append("pack_import_planning_report.json: automatic_acceptance must be false.")
        if master_index.get("hosted_master_index_mutation") is not False:
            errors.append("pack_import_planning_report.json: hosted_master_index_mutation must be false.")
    else:
        errors.append("pack_import_planning_report.json: master_index_review_impact must be an object.")


def _validate_staging_doc(errors: list[str]) -> None:
    text = _read_text(AUDIT_ROOT / "STAGING_MODEL.md", errors).lower()
    for phrase in REQUIRED_STAGING_PHRASES:
        if phrase.lower() not in text:
            errors.append(f"STAGING_MODEL.md: missing required staging phrase: {phrase}.")


def _validate_local_search_doc(errors: list[str]) -> None:
    text = _read_text(AUDIT_ROOT / "LOCAL_SEARCH_AND_INDEX_INTERACTION.md", errors).lower()
    for phrase in REQUIRED_SEARCH_PHRASES:
        if phrase.lower() not in text:
            errors.append(f"LOCAL_SEARCH_AND_INDEX_INTERACTION.md: missing required phrase: {phrase}.")
    if "public static site: no impact" not in text:
        errors.append("LOCAL_SEARCH_AND_INDEX_INTERACTION.md: must say public static site has no impact.")


def _validate_master_index_doc(errors: list[str]) -> None:
    text = _read_text(AUDIT_ROOT / "MASTER_INDEX_REVIEW_INTERACTION.md", errors).lower()
    for phrase in REQUIRED_MASTER_INDEX_PHRASES:
        if phrase.lower() not in text:
            errors.append(f"MASTER_INDEX_REVIEW_INTERACTION.md: missing required phrase: {phrase}.")


def _validate_reference_docs(errors: list[str]) -> None:
    for doc in REQUIRED_DOC_FILES:
        text = _read_text(doc, errors).lower()
        if "planning only" not in text:
            errors.append(f"{_rel(doc)}: must state the work is planning only.")
        if "does not implement import" not in text:
            errors.append(f"{_rel(doc)}: must state import is not implemented.")
        if "validate_only" not in text:
            errors.append(f"{_rel(doc)}: must mention validate_only.")
        for phrase in FORBIDDEN_POSITIVE_RUNTIME_CLAIMS:
            if phrase in text and f"does not claim {phrase}" not in text:
                errors.append(f"{_rel(doc)}: unsupported positive runtime claim: {phrase}.")


def _load_json(path: Path, errors: list[str]) -> Any:
    if not path.exists():
        errors.append(f"{_rel(path)}: JSON file is missing.")
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"{_rel(path)}: invalid JSON: {exc}.")
        return None


def _read_text(path: Path, errors: list[str]) -> str:
    if not path.exists():
        errors.append(f"{_rel(path)}: required text file is missing.")
        return ""
    return path.read_text(encoding="utf-8")


def _list_of_strings(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str)]


def _script_path_from_command(command: str) -> Path | None:
    parts = command.split()
    if len(parts) < 2:
        return None
    script = parts[1]
    if not script.startswith("scripts/"):
        return None
    return REPO_ROOT / script


def _report(payload: Mapping[str, Any] | None, errors: list[str], warnings: list[str]) -> dict[str, Any]:
    return {
        "status": "valid" if not errors else "invalid",
        "audit_root": _rel(AUDIT_ROOT),
        "report_id": payload.get("report_id") if isinstance(payload, Mapping) else None,
        "import_runtime_implemented": payload.get("import_runtime_implemented") if isinstance(payload, Mapping) else None,
        "default_future_mode": payload.get("default_future_mode") if isinstance(payload, Mapping) else None,
        "next_future_mode": payload.get("next_future_mode") if isinstance(payload, Mapping) else None,
        "supported_pack_types": payload.get("supported_pack_types", []) if isinstance(payload, Mapping) else [],
        "next_recommended_milestone": payload.get("next_recommended_milestone") if isinstance(payload, Mapping) else None,
        "errors": errors,
        "warnings": warnings,
    }


def _format_plain(report: Mapping[str, Any]) -> str:
    lines = [
        f"status: {report['status']}",
        f"audit_root: {report['audit_root']}",
        f"report_id: {report['report_id']}",
        f"import_runtime_implemented: {report['import_runtime_implemented']}",
        f"default_future_mode: {report['default_future_mode']}",
        f"next_future_mode: {report['next_future_mode']}",
        "supported_pack_types: " + ", ".join(report["supported_pack_types"]),
        f"next_recommended_milestone: {report['next_recommended_milestone']}",
    ]
    for warning in report["warnings"]:
        lines.append(f"warning: {warning}")
    for error in report["errors"]:
        lines.append(f"error: {error}")
    return "\n".join(lines) + "\n"


def _rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


if __name__ == "__main__":
    raise SystemExit(main())
