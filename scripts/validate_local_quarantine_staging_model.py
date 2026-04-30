from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
INVENTORY_ROOT = REPO_ROOT / "control" / "inventory" / "local_state"
MODEL_PATH = INVENTORY_ROOT / "local_quarantine_staging_model.json"
PATH_POLICY_PATH = INVENTORY_ROOT / "local_state_path_policy.json"
AUDIT_ROOT = REPO_ROOT / "control" / "audits" / "local-quarantine-staging-model-v0"
REPORT_PATH = AUDIT_ROOT / "local_quarantine_staging_model_report.json"
GITIGNORE_PATH = REPO_ROOT / ".gitignore"

REQUIRED_INVENTORY_FILES = {
    "README.md",
    "local_quarantine_staging_model.json",
    "local_state_path_policy.json",
}
REQUIRED_AUDIT_FILES = {
    "README.md",
    "MODEL_SUMMARY.md",
    "PATH_POLICY.md",
    "STAGED_ENTITY_MODEL.md",
    "PROVENANCE_AND_REPORT_LINKING.md",
    "PRIVACY_RIGHTS_RISK_POLICY.md",
    "RESET_DELETE_EXPORT_MODEL.md",
    "LOCAL_SEARCH_AND_INDEX_IMPACT.md",
    "NATIVE_RELAY_SNAPSHOT_IMPACT.md",
    "MASTER_INDEX_IMPACT.md",
    "IMPLEMENTATION_BOUNDARIES.md",
    "FUTURE_IMPLEMENTATION_SEQUENCE.md",
    "RISKS_AND_LIMITATIONS.md",
    "NEXT_STEPS.md",
    "local_quarantine_staging_model_report.json",
}
REQUIRED_STAGED_ENTITIES = {
    "staged_pack_reference",
    "staged_validation_report",
    "staged_source_candidate",
    "staged_evidence_candidate",
    "staged_index_summary",
    "staged_contribution_candidate",
    "staged_ai_output_candidate",
    "staged_issue",
    "staged_decision_note",
}
REQUIRED_FUTURE_OPERATIONS = {
    "list_staged_packs",
    "inspect_staged_pack_metadata",
    "delete_staged_pack",
    "clear_all_staged_state",
    "export_staging_report_only",
    "export_public_safe_contribution_candidate_future",
}
REQUIRED_PROHIBITED_ROOTS = {
    "site/dist",
    "external",
    "runtime",
    "control/inventory canonical source files",
    "snapshots/examples committed examples",
    "docs",
}
REQUIRED_GITIGNORE_ENTRIES = {
    ".eureka-local/",
    ".eureka-cache/",
    ".eureka-staging/",
}
LOCAL_STATE_ROOTS = {
    ".eureka-local",
    ".eureka-cache",
    ".eureka-staging",
}
REQUIRED_DOCS = {
    REPO_ROOT / "docs" / "architecture" / "LOCAL_QUARANTINE_STAGING_MODEL.md",
    REPO_ROOT / "docs" / "reference" / "LOCAL_STAGING_PATH_POLICY.md",
    REPO_ROOT / "docs" / "reference" / "LOCAL_CACHE_PRIVACY_POLICY.md",
    REPO_ROOT / "docs" / "architecture" / "PACK_IMPORT_PIPELINE.md",
    REPO_ROOT / "docs" / "operations" / "VALIDATE_ONLY_PACK_IMPORT.md",
}
REQUIRED_DOC_PHRASES = {
    "no staging runtime exists",
    "does not create",
    "does not import",
    "does not stage",
    "does not index",
    "does not upload",
    "does not mutate",
    "public search",
    "master index",
}


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate Local Quarantine/Staging Model v0.")
    parser.add_argument("--json", action="store_true", help="Emit JSON report.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    report = validate_local_quarantine_staging_model()
    output = stdout or sys.stdout
    if args.json:
        output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        output.write(_format_plain(report))
    return 0 if report["status"] == "valid" else 1


def validate_local_quarantine_staging_model() -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    for filename in sorted(REQUIRED_INVENTORY_FILES):
        path = INVENTORY_ROOT / filename
        if not path.exists():
            errors.append(f"{_rel(path)}: required inventory file is missing.")

    model = _load_json(MODEL_PATH, errors)
    path_policy = _load_json(PATH_POLICY_PATH, errors)
    audit_report = _load_json(REPORT_PATH, errors)

    for filename in sorted(REQUIRED_AUDIT_FILES):
        path = AUDIT_ROOT / filename
        if not path.exists():
            errors.append(f"{_rel(path)}: required audit file is missing.")

    if isinstance(model, Mapping):
        _validate_model(model, errors)
    if isinstance(path_policy, Mapping):
        _validate_path_policy(path_policy, errors)
    if isinstance(audit_report, Mapping):
        _validate_audit_report(audit_report, errors)

    _validate_docs(errors)
    _validate_gitignore(errors)
    _validate_no_local_state_dirs(errors)

    return {
        "schema_version": "local_quarantine_staging_model_validation.v0",
        "validator_id": "local_quarantine_staging_model_validator_v0",
        "status": "valid" if not errors else "invalid",
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
        "inventory_root": _rel(INVENTORY_ROOT),
        "audit_root": _rel(AUDIT_ROOT),
        "staging_runtime_implemented": False,
        "default_visibility": model.get("default_visibility") if isinstance(model, Mapping) else None,
        "default_search_impact": model.get("default_search_impact") if isinstance(model, Mapping) else None,
        "default_master_index_impact": model.get("default_master_index_impact") if isinstance(model, Mapping) else None,
        "suggested_dev_root": path_policy.get("suggested_dev_root") if isinstance(path_policy, Mapping) else None,
        "local_state_roots_present": [
            root for root in sorted(LOCAL_STATE_ROOTS) if (REPO_ROOT / root).exists()
        ],
        "network_performed": False,
        "mutation_performed": False,
        "staging_performed": False,
        "import_performed": False,
        "indexing_performed": False,
        "master_index_mutation_performed": False,
    }


def _validate_model(model: Mapping[str, Any], errors: list[str]) -> None:
    expected = {
        "status": "planning_only",
        "staging_runtime_implemented": False,
        "default_enabled": False,
        "default_visibility": "local_private",
        "default_search_impact": "none",
        "default_master_index_impact": "none",
        "default_network_required": False,
        "default_telemetry_enabled": False,
    }
    for key, value in expected.items():
        if model.get(key) != value:
            errors.append(f"{_rel(MODEL_PATH)}: {key} must be {value!r}.")

    entities = {
        item.get("entity_type")
        for item in model.get("staged_entities", [])
        if isinstance(item, Mapping)
    }
    missing_entities = REQUIRED_STAGED_ENTITIES - entities
    if missing_entities:
        errors.append(f"{_rel(MODEL_PATH)}: staged_entities missing {sorted(missing_entities)}.")

    reset_policy = model.get("reset_delete_policy")
    if not isinstance(reset_policy, Mapping):
        errors.append(f"{_rel(MODEL_PATH)}: reset_delete_policy must be an object.")
    else:
        operations = set(_strings(reset_policy.get("future_operations")))
        missing_ops = REQUIRED_FUTURE_OPERATIONS - operations
        if missing_ops:
            errors.append(f"{_rel(MODEL_PATH)}: reset_delete_policy missing {sorted(missing_ops)}.")
        if reset_policy.get("private_content_export_default") != "forbidden":
            errors.append(f"{_rel(MODEL_PATH)}: private_content_export_default must be forbidden.")

    public_search = model.get("public_search_policy")
    if not isinstance(public_search, Mapping) or public_search.get("staged_packs_visible_by_default") is not False:
        errors.append(f"{_rel(MODEL_PATH)}: public_search_policy must keep staged packs hidden by default.")

    master_index = model.get("master_index_policy")
    if not isinstance(master_index, Mapping):
        errors.append(f"{_rel(MODEL_PATH)}: master_index_policy must be an object.")
    else:
        if master_index.get("submission_performed_by_staging") is not False:
            errors.append(f"{_rel(MODEL_PATH)}: staging must not submit to the master index.")
        if master_index.get("auto_acceptance") is not False:
            errors.append(f"{_rel(MODEL_PATH)}: auto_acceptance must be false.")


def _validate_path_policy(policy: Mapping[str, Any], errors: list[str]) -> None:
    if policy.get("status") != "planning_only":
        errors.append(f"{_rel(PATH_POLICY_PATH)}: status must be planning_only.")
    if policy.get("suggested_dev_root") != ".eureka-local/":
        errors.append(f"{_rel(PATH_POLICY_PATH)}: suggested_dev_root must be .eureka-local/.")

    prohibited = set(_strings(policy.get("prohibited_roots")))
    missing_roots = REQUIRED_PROHIBITED_ROOTS - prohibited
    if missing_roots:
        errors.append(f"{_rel(PATH_POLICY_PATH)}: prohibited_roots missing {sorted(missing_roots)}.")

    git_policy = policy.get("git_policy")
    if not isinstance(git_policy, Mapping):
        errors.append(f"{_rel(PATH_POLICY_PATH)}: git_policy must be an object.")
        return
    if git_policy.get("must_be_ignored") is not True:
        errors.append(f"{_rel(PATH_POLICY_PATH)}: git_policy.must_be_ignored must be true.")
    if git_policy.get("committed_state_forbidden") is not True:
        errors.append(f"{_rel(PATH_POLICY_PATH)}: committed_state_forbidden must be true.")
    required_entries = set(_strings(git_policy.get("gitignore_entries_required")))
    missing_entries = REQUIRED_GITIGNORE_ENTRIES - required_entries
    if missing_entries:
        errors.append(f"{_rel(PATH_POLICY_PATH)}: gitignore_entries_required missing {sorted(missing_entries)}.")


def _validate_audit_report(report: Mapping[str, Any], errors: list[str]) -> None:
    expected = {
        "status": "planning_only",
        "staging_runtime_implemented": False,
        "default_visibility": "local_private",
        "default_search_impact": "none",
        "default_master_index_impact": "none",
        "default_telemetry_enabled": False,
    }
    for key, value in expected.items():
        if report.get(key) != value:
            errors.append(f"{_rel(REPORT_PATH)}: {key} must be {value!r}.")

    prohibited = set(_strings(report.get("prohibited_roots")))
    missing_roots = REQUIRED_PROHIBITED_ROOTS - prohibited
    if missing_roots:
        errors.append(f"{_rel(REPORT_PATH)}: prohibited_roots missing {sorted(missing_roots)}.")

    entities = set(_strings(report.get("staged_entities")))
    missing_entities = REQUIRED_STAGED_ENTITIES - entities
    if missing_entities:
        errors.append(f"{_rel(REPORT_PATH)}: staged_entities missing {sorted(missing_entities)}.")

    operations = set(_strings(report.get("required_future_operations")))
    missing_ops = REQUIRED_FUTURE_OPERATIONS - operations
    if missing_ops:
        errors.append(f"{_rel(REPORT_PATH)}: required_future_operations missing {sorted(missing_ops)}.")


def _validate_docs(errors: list[str]) -> None:
    for path in sorted(REQUIRED_DOCS):
        text = _read_text(path, errors).lower()
        for phrase in REQUIRED_DOC_PHRASES:
            if phrase not in text:
                errors.append(f"{_rel(path)}: missing required phrase: {phrase}.")

    reset_text = _read_text(AUDIT_ROOT / "RESET_DELETE_EXPORT_MODEL.md", errors).lower()
    for phrase in ["list staged packs", "delete one staged pack", "clear all staged state", "export staging report only"]:
        if phrase not in reset_text:
            errors.append(f"RESET_DELETE_EXPORT_MODEL.md: missing reset/delete/export phrase: {phrase}.")

    impact_text = _read_text(AUDIT_ROOT / "NATIVE_RELAY_SNAPSHOT_IMPACT.md", errors).lower()
    for phrase in ["native", "relay", "snapshots", "private by default"]:
        if phrase not in impact_text:
            errors.append(f"NATIVE_RELAY_SNAPSHOT_IMPACT.md: missing impact phrase: {phrase}.")


def _validate_gitignore(errors: list[str]) -> None:
    text = _read_text(GITIGNORE_PATH, errors)
    entries = {line.strip() for line in text.splitlines() if line.strip() and not line.strip().startswith("#")}
    missing = REQUIRED_GITIGNORE_ENTRIES - entries
    if missing:
        errors.append(f"{_rel(GITIGNORE_PATH)}: missing local-state ignore entries {sorted(missing)}.")


def _validate_no_local_state_dirs(errors: list[str]) -> None:
    for root in sorted(LOCAL_STATE_ROOTS):
        path = REPO_ROOT / root
        if path.exists():
            errors.append(f"{root}/: local staging/cache directory must not exist in this milestone.")


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
        "Local Quarantine/Staging Model validation",
        f"status: {report['status']}",
        f"inventory_root: {report['inventory_root']}",
        f"audit_root: {report['audit_root']}",
        f"default_visibility: {report.get('default_visibility')}",
        f"default_search_impact: {report.get('default_search_impact')}",
        f"default_master_index_impact: {report.get('default_master_index_impact')}",
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
