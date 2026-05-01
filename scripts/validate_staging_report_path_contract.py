from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
INVENTORY_ROOT = REPO_ROOT / "control" / "inventory" / "local_state"
CONTRACT_PATH = INVENTORY_ROOT / "staging_report_path_contract.json"
AUDIT_ROOT = REPO_ROOT / "control" / "audits" / "staging-report-path-contract-v0"
REPORT_PATH = AUDIT_ROOT / "staging_report_path_contract_report.json"
GITIGNORE_PATH = REPO_ROOT / ".gitignore"
VALIDATE_ONLY_TOOL = REPO_ROOT / "scripts" / "validate_only_pack_import.py"

REQUIRED_AUDIT_FILES = {
    "README.md",
    "CONTRACT_SUMMARY.md",
    "ALLOWED_AND_FORBIDDEN_ROOTS.md",
    "FILENAME_POLICY.md",
    "REDACTION_POLICY.md",
    "TOOL_BEHAVIOR_POLICY.md",
    "GITIGNORE_REVIEW.md",
    "NATIVE_RELAY_SNAPSHOT_IMPACT.md",
    "PUBLIC_SEARCH_AND_MASTER_INDEX_IMPACT.md",
    "RISKS_AND_LIMITATIONS.md",
    "NEXT_STEPS.md",
    "staging_report_path_contract_report.json",
}
REQUIRED_FORBIDDEN_ROOT_MARKERS = {
    "site/dist",
    "external",
    "runtime",
    "control/inventory",
    "contracts",
    "snapshots/examples",
    "docs",
}
REQUIRED_LOCAL_ROOTS = {
    ".eureka-local/",
    ".eureka-cache/",
    ".eureka-staging/",
    ".eureka-reports/",
}
LOCAL_STATE_DIRS = {
    ".eureka-local",
    ".eureka-cache",
    ".eureka-staging",
    ".eureka-reports",
}
REQUIRED_DOCS = {
    REPO_ROOT / "docs" / "reference" / "STAGING_REPORT_PATH_CONTRACT.md",
    REPO_ROOT / "docs" / "operations" / "LOCAL_REPORT_PATHS.md",
    REPO_ROOT / "docs" / "reference" / "LOCAL_STAGING_PATH_POLICY.md",
    REPO_ROOT / "docs" / "operations" / "VALIDATE_ONLY_PACK_IMPORT.md",
    REPO_ROOT / "docs" / "reference" / "PACK_IMPORT_REPORT_FORMAT.md",
    REPO_ROOT / "docs" / "architecture" / "PACK_IMPORT_PIPELINE.md",
    REPO_ROOT / "docs" / "reference" / "LOCAL_CACHE_PRIVACY_POLICY.md",
}
REQUIRED_DOC_PHRASES = {
    "stdout",
    "explicit output",
    "redaction",
    "redact",
    "forbidden",
    "public search",
    "master index",
    "no staging runtime exists",
}


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate Staging Report Path Contract v0.")
    parser.add_argument("--json", action="store_true", help="Emit JSON report.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    report = validate_staging_report_path_contract()
    output = stdout or sys.stdout
    if args.json:
        output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        output.write(_format_plain(report))
    return 0 if report["ok"] else 1


def validate_staging_report_path_contract() -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    contract = _load_json(CONTRACT_PATH, errors)
    audit_report = _load_json(REPORT_PATH, errors)

    for filename in sorted(REQUIRED_AUDIT_FILES):
        path = AUDIT_ROOT / filename
        if not path.exists():
            errors.append(f"{_rel(path)}: required audit file is missing.")

    if isinstance(contract, Mapping):
        _validate_contract(contract, errors)
    if isinstance(audit_report, Mapping):
        _validate_audit_report(audit_report, errors)

    _validate_gitignore(errors)
    _validate_no_local_state_dirs(errors)
    _validate_docs(errors)
    _validate_validate_only_tool(errors)

    return {
        "schema_version": "staging_report_path_contract_validation.v0",
        "validator_id": "staging_report_path_contract_validator_v0",
        "ok": not errors,
        "status": "valid" if not errors else "invalid",
        "errors": errors,
        "warnings": warnings,
        "contract_path": _rel(CONTRACT_PATH),
        "audit_root": _rel(AUDIT_ROOT),
        "report_path_runtime_implemented": False,
        "staging_runtime_implemented": False,
        "default_output_mode": contract.get("default_output_mode") if isinstance(contract, Mapping) else None,
        "explicit_output_required_for_file_write": (
            contract.get("explicit_output_required_for_file_write") if isinstance(contract, Mapping) else None
        ),
        "local_private_by_default": contract.get("local_private_by_default") if isinstance(contract, Mapping) else None,
        "local_state_roots_present": [
            root for root in sorted(LOCAL_STATE_DIRS) if (REPO_ROOT / root).exists()
        ],
        "network_performed": False,
        "mutation_performed": False,
        "staging_performed": False,
        "import_performed": False,
        "indexing_performed": False,
        "upload_performed": False,
        "master_index_mutation_performed": False,
    }


def _validate_contract(contract: Mapping[str, Any], errors: list[str]) -> None:
    expected = {
        "status": "planning_only",
        "report_path_runtime_implemented": False,
        "staging_runtime_implemented": False,
        "default_output_mode": "stdout",
        "explicit_output_required_for_file_write": True,
        "auto_create_parent_directories_default": False,
        "local_private_by_default": True,
    }
    for key, value in expected.items():
        if contract.get(key) != value:
            errors.append(f"{_rel(CONTRACT_PATH)}: {key} must be {value!r}.")

    _require_root_markers(CONTRACT_PATH, contract.get("committed_report_roots_forbidden"), errors)
    _require_root_markers(CONTRACT_PATH, contract.get("local_report_roots_forbidden"), errors)

    ignored_roots = set(_strings(contract.get("local_report_roots_ignored_by_git")))
    missing_ignored = REQUIRED_LOCAL_ROOTS - ignored_roots
    if missing_ignored:
        errors.append(f"{_rel(CONTRACT_PATH)}: local_report_roots_ignored_by_git missing {sorted(missing_ignored)}.")

    filename_policy = contract.get("filename_policy")
    if not isinstance(filename_policy, Mapping):
        errors.append(f"{_rel(CONTRACT_PATH)}: filename_policy must be an object.")
    else:
        if filename_policy.get("machine_report_extension") != ".json":
            errors.append(f"{_rel(CONTRACT_PATH)}: machine_report_extension must be .json.")
        forbidden = set(_strings(filename_policy.get("forbidden_components")))
        for component in ["raw_local_path", "raw_user_query_text", "full_source_url", "credential_or_secret"]:
            if component not in forbidden:
                errors.append(f"{_rel(CONTRACT_PATH)}: filename_policy missing forbidden component {component}.")

    redaction_policy = contract.get("redaction_policy")
    if not isinstance(redaction_policy, Mapping):
        errors.append(f"{_rel(CONTRACT_PATH)}: redaction_policy must be an object.")
    else:
        for key in [
            "absolute_local_paths_redacted_in_committed_reports",
            "home_directories_redacted",
            "drive_letters_redacted",
            "credentials_never_emitted",
            "api_keys_never_emitted",
        ]:
            if redaction_policy.get(key) is not True:
                errors.append(f"{_rel(CONTRACT_PATH)}: redaction_policy.{key} must be true.")

    tool_policy = contract.get("validate_only_tool_policy")
    if not isinstance(tool_policy, Mapping):
        errors.append(f"{_rel(CONTRACT_PATH)}: validate_only_tool_policy must be an object.")
    else:
        for key in [
            "file_write_requires_explicit_output_argument",
            "output_parent_must_exist",
            "report_must_validate_as_pack_import_report_v0",
            "forbidden_repo_roots_rejected",
        ]:
            if tool_policy.get(key) is not True:
                errors.append(f"{_rel(CONTRACT_PATH)}: validate_only_tool_policy.{key} must be true.")
        for key in ["hidden_state_allowed", "staging_allowed", "index_mutation_allowed"]:
            if tool_policy.get(key) is not False:
                errors.append(f"{_rel(CONTRACT_PATH)}: validate_only_tool_policy.{key} must be false.")


def _validate_audit_report(report: Mapping[str, Any], errors: list[str]) -> None:
    expected = {
        "status": "planning_only",
        "report_path_runtime_implemented": False,
        "staging_runtime_implemented": False,
        "default_output_mode": "stdout",
        "explicit_output_required_for_file_write": True,
        "local_private_by_default": True,
    }
    for key, value in expected.items():
        if report.get(key) != value:
            errors.append(f"{_rel(REPORT_PATH)}: {key} must be {value!r}.")
    _require_root_markers(REPORT_PATH, report.get("forbidden_committed_roots"), errors)
    required_patterns = set(_strings(report.get("gitignore_patterns_required")))
    missing = REQUIRED_LOCAL_ROOTS - required_patterns
    if missing:
        errors.append(f"{_rel(REPORT_PATH)}: gitignore_patterns_required missing {sorted(missing)}.")


def _require_root_markers(path: Path, roots_value: Any, errors: list[str]) -> None:
    roots_text = "\n".join(_strings(roots_value))
    missing = [marker for marker in sorted(REQUIRED_FORBIDDEN_ROOT_MARKERS) if marker not in roots_text]
    if missing:
        errors.append(f"{_rel(path)}: forbidden roots missing markers {missing}.")


def _validate_gitignore(errors: list[str]) -> None:
    text = _read_text(GITIGNORE_PATH, errors)
    entries = {line.strip() for line in text.splitlines() if line.strip() and not line.strip().startswith("#")}
    missing = REQUIRED_LOCAL_ROOTS - entries
    if missing:
        errors.append(f"{_rel(GITIGNORE_PATH)}: missing local report ignore entries {sorted(missing)}.")


def _validate_no_local_state_dirs(errors: list[str]) -> None:
    for root in sorted(LOCAL_STATE_DIRS):
        if (REPO_ROOT / root).exists():
            errors.append(f"{root}/: local report or staging directory must not exist in this milestone.")


def _validate_docs(errors: list[str]) -> None:
    for path in sorted(REQUIRED_DOCS):
        text = _read_text(path, errors).lower()
        for phrase in REQUIRED_DOC_PHRASES:
            if phrase not in text:
                errors.append(f"{_rel(path)}: missing required phrase: {phrase}.")


def _validate_validate_only_tool(errors: list[str]) -> None:
    text = _read_text(VALIDATE_ONLY_TOOL, errors)
    for phrase in ["--output", "parent must already exist", "FORBIDDEN_OUTPUT_REPO_ROOTS"]:
        if phrase not in text:
            errors.append(f"{_rel(VALIDATE_ONLY_TOOL)}: missing output path policy phrase: {phrase}.")
    for root in ["site/dist", "control/inventory", "contracts", "runtime", "external"]:
        if root not in text:
            errors.append(f"{_rel(VALIDATE_ONLY_TOOL)}: missing forbidden output root {root}.")


def _load_json(path: Path, errors: list[str]) -> Any:
    if not path.exists():
        errors.append(f"{_rel(path)}: missing JSON file.")
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"{_rel(path)}: invalid JSON: {exc}.")
        return None


def _read_text(path: Path, errors: list[str]) -> str:
    if not path.exists():
        errors.append(f"{_rel(path)}: missing text file.")
        return ""
    return path.read_text(encoding="utf-8")


def _strings(value: Any) -> list[str]:
    return [item for item in value if isinstance(item, str)] if isinstance(value, list) else []


def _rel(path: Path) -> str:
    try:
        return path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return str(path)


def _format_plain(report: Mapping[str, Any]) -> str:
    lines = [
        "Staging Report Path Contract validation",
        f"status: {report['status']}",
        f"contract_path: {report['contract_path']}",
        f"audit_root: {report['audit_root']}",
        f"default_output_mode: {report.get('default_output_mode')}",
        f"explicit_output_required_for_file_write: {report.get('explicit_output_required_for_file_write')}",
        f"local_private_by_default: {report.get('local_private_by_default')}",
        f"report_path_runtime_implemented: {report['report_path_runtime_implemented']}",
        f"staging_runtime_implemented: {report['staging_runtime_implemented']}",
        f"local_state_roots_present: {len(report['local_state_roots_present'])}",
        f"network_performed: {report['network_performed']}",
        f"mutation_performed: {report['mutation_performed']}",
    ]
    for error in report["errors"]:
        lines.append(f"error: {error}")
    for warning in report["warnings"]:
        lines.append(f"warning: {warning}")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
