from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = REPO_ROOT / "contracts" / "packs" / "local_staging_manifest.v0.json"
EXAMPLES_ROOT = REPO_ROOT / "examples" / "local_staging_manifests"
DEFAULT_EXAMPLE_ROOTS = [
    EXAMPLES_ROOT / "minimal_local_staging_manifest_v0",
]

SCHEMA_VERSION = "local_staging_manifest_validation.v0"
VALIDATOR_ID = "local_staging_manifest_validator_v0"
MANIFEST_NAME = "LOCAL_STAGING_MANIFEST.json"
CHECKSUMS_NAME = "CHECKSUMS.SHA256"

STATUSES = {
    "planned_example",
    "local_private",
    "staged_quarantine",
    "inspectable",
    "delete_requested",
    "reset_requested",
    "exported_report_only",
    "superseded",
}
STAGING_MODES = {
    "stage_local_quarantine",
    "inspect_staged",
    "local_index_candidate_future",
    "contribution_queue_candidate_future",
}
REPORT_PATH_POLICIES = {"stdout_only", "explicit_local_path", "redacted", "example_committed"}
REPORT_STATUSES = {
    "validate_only_passed",
    "validate_only_failed",
    "partial_validation",
    "unsupported_pack_type",
    "blocked_by_policy",
    "unavailable_validator",
    "future_import_not_performed",
}
PACK_TYPES = {
    "source_pack",
    "evidence_pack",
    "index_pack",
    "contribution_pack",
    "master_index_review_queue",
    "ai_output_bundle",
}
PACK_ROOT_POLICIES = {"explicit_user_selected", "example_committed", "redacted_local"}
VALIDATION_STATUSES = {"passed", "failed", "unavailable", "unknown_type", "skipped"}
PRIVACY_CLASSIFICATIONS = {"public_safe", "local_private", "review_required", "restricted", "unknown"}
RIGHTS_CLASSIFICATIONS = {"public_metadata_only", "source_terms_apply", "review_required", "restricted", "unknown"}
RISK_CLASSIFICATIONS = {
    "metadata_only",
    "private_data_risk",
    "credential_risk",
    "executable_reference",
    "malware_review_required",
    "unknown",
}
ENTITY_TYPES = {
    "staged_source_candidate",
    "staged_evidence_candidate",
    "staged_index_summary",
    "staged_contribution_candidate",
    "staged_ai_output_candidate",
    "staged_issue",
    "staged_decision_note",
}
REVIEW_STATUSES = {
    "unreviewed",
    "validated_structure",
    "quarantine_required",
    "inspectable_local",
    "local_index_candidate_future",
    "contribution_candidate_future",
    "rejected_local",
}
HARD_FALSE_FIELDS = (
    "public_search_mutated",
    "local_index_mutated",
    "canonical_source_registry_mutated",
    "runtime_state_mutated",
    "master_index_mutated",
    "upload_performed",
    "live_network_performed",
)
REQUIRED_TOP_LEVEL_FIELDS = {
    "schema_version",
    "manifest_id",
    "manifest_version",
    "manifest_kind",
    "status",
    "created_by_tool",
    "staging_mode",
    "source_validate_report_ref",
    "staged_pack_refs",
    "staged_entities",
    "counts",
    "privacy_rights_risk_summary",
    "provenance_summary",
    "no_mutation_guarantees",
    "reset_delete_export_policy",
    "limitations",
    "notes",
    *HARD_FALSE_FIELDS,
}
COUNT_FIELDS = {
    "staged_pack_count",
    "staged_entity_count",
    "staged_source_candidate_count",
    "staged_evidence_candidate_count",
    "staged_index_summary_count",
    "staged_contribution_candidate_count",
    "staged_ai_output_candidate_count",
    "issue_count",
    "blocked_issue_count",
    "private_record_count",
    "public_safe_record_count",
}
SECRET_KEY_RE = re.compile(r"(api[_-]?key|auth[_-]?token|password|private[_-]?key|secret)", re.IGNORECASE)
SECRET_VALUE_RE = re.compile(r"(sk-[A-Za-z0-9_-]{8,}|-----BEGIN [A-Z ]*PRIVATE KEY-----)", re.IGNORECASE)
PRIVATE_PATH_RE = re.compile(
    r"([A-Za-z]:[\\/](Users|Documents and Settings|Projects)[\\/]|"
    r"\\\\[^\\/\s]+[\\/][^\\/\s]+[\\/]|"
    r"/(Users|home|var/folders|private/tmp|tmp)/)",
    re.IGNORECASE,
)
FORBIDDEN_AUTHORITY_PATTERNS = (
    "rights clearance approved",
    "rights clearance complete",
    "rights cleared",
    "malware safety approved",
    "malware safety guaranteed",
    "canonical truth established",
    "accepted as canonical truth",
    "master index accepted",
    "public search updated",
    "local index updated",
)


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate Local Staging Manifest Format v0 examples or one manifest.")
    parser.add_argument("--manifest", help="Validate one LOCAL_STAGING_MANIFEST.json file.")
    parser.add_argument("--manifest-root", help="Validate one local staging manifest root.")
    parser.add_argument("--all-examples", action="store_true", help="Validate all repo example manifests.")
    parser.add_argument("--json", action="store_true", help="Emit structured JSON.")
    parser.add_argument("--strict", action="store_true", help="Require schema, examples, and checksum coverage.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    report = validate_local_staging_manifests(
        manifest_path=Path(args.manifest) if args.manifest else None,
        manifest_root=Path(args.manifest_root) if args.manifest_root else None,
        all_examples=args.all_examples or (not args.manifest and not args.manifest_root),
        strict=args.strict,
    )
    output = stdout or sys.stdout
    if args.json:
        output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        output.write(_format_plain(report))
    return 0 if report["ok"] else 1


def validate_local_staging_manifests(
    *,
    manifest_path: Path | None = None,
    manifest_root: Path | None = None,
    all_examples: bool = True,
    strict: bool = False,
) -> dict[str, Any]:
    errors: list[str] = []
    checked_manifests: list[dict[str, Any]] = []

    if strict and not CONTRACT_PATH.exists():
        errors.append(f"{_rel(CONTRACT_PATH)}: local staging manifest schema is missing.")
    elif CONTRACT_PATH.exists():
        _load_json(CONTRACT_PATH, errors)

    mode = "all_examples"
    targets: list[tuple[Path, Path | None]]
    if all_examples:
        if strict and not EXAMPLES_ROOT.exists():
            errors.append(f"{_rel(EXAMPLES_ROOT)}: local staging manifest examples directory is missing.")
        targets = [(root / MANIFEST_NAME, root) for root in DEFAULT_EXAMPLE_ROOTS]
    elif manifest_root is not None:
        root = _resolve(manifest_root)
        targets = [(root / MANIFEST_NAME, root)]
        mode = "single_manifest_root"
    elif manifest_path is not None:
        targets = [(_resolve(manifest_path), None)]
        mode = "single_manifest"
    else:
        targets = []
        errors.append("no manifest target supplied.")

    for target, root in targets:
        result = validate_local_staging_manifest_file(target, manifest_root=root, strict=strict)
        checked_manifests.append(result)
        errors.extend(f"{result['path']}: {error}" for error in result["errors"])

    return {
        "schema_version": SCHEMA_VERSION,
        "validator_id": VALIDATOR_ID,
        "ok": not errors,
        "status": "valid" if not errors else "invalid",
        "mode": mode,
        "strict": strict,
        "checked_manifests": checked_manifests,
        "summary": _summarize(checked_manifests),
        "errors": errors,
        "model_calls_performed": False,
        "network_performed": False,
        "mutation_performed": False,
        "staging_performed": False,
        "import_performed": False,
        "indexing_performed": False,
        "upload_performed": False,
        "master_index_mutation_performed": False,
        "public_search_mutated": False,
        "local_index_mutated": False,
    }


def validate_local_staging_manifest_file(
    manifest_path: Path,
    *,
    manifest_root: Path | None = None,
    strict: bool = False,
) -> dict[str, Any]:
    errors: list[str] = []
    path = _resolve(manifest_path)
    payload = _load_json(path, errors)
    if not isinstance(payload, Mapping):
        if not errors:
            errors.append("manifest must be a JSON object.")
        return _result(path, None, errors)

    _validate_manifest(payload, errors)
    if manifest_root is not None:
        _validate_example_root(_resolve(manifest_root), strict=strict, errors=errors)
    _validate_no_private_paths_or_secrets(payload, errors)
    _validate_no_authority_claims(payload, errors)
    return _result(path, payload, errors)


def _validate_manifest(payload: Mapping[str, Any], errors: list[str]) -> None:
    missing = sorted(REQUIRED_TOP_LEVEL_FIELDS - set(payload))
    for field in missing:
        errors.append(f"{field}: required field is missing.")

    if payload.get("schema_version") != "local_staging_manifest.v0":
        errors.append("schema_version must be local_staging_manifest.v0.")
    if payload.get("manifest_kind") != "local_staging_manifest":
        errors.append("manifest_kind must be local_staging_manifest.")
    _validate_enum(payload.get("status"), STATUSES, "status", errors)
    _validate_enum(payload.get("staging_mode"), STAGING_MODES, "staging_mode", errors)

    for field in HARD_FALSE_FIELDS:
        if payload.get(field) is not False:
            errors.append(f"{field} must be false.")

    _validate_created_by_tool(payload.get("created_by_tool"), errors)
    _validate_validate_report_ref(payload.get("source_validate_report_ref"), errors)

    pack_refs = payload.get("staged_pack_refs")
    if not isinstance(pack_refs, list) or not pack_refs:
        errors.append("staged_pack_refs must be a non-empty array.")
        pack_refs = []
    else:
        for index, pack_ref in enumerate(pack_refs):
            _validate_staged_pack_ref(pack_ref, index, errors)

    entities = payload.get("staged_entities")
    if not isinstance(entities, list):
        errors.append("staged_entities must be an array.")
        entities = []
    else:
        for index, entity in enumerate(entities):
            _validate_staged_entity(entity, index, errors)

    _validate_counts(payload.get("counts"), pack_refs, entities, errors)
    _validate_privacy_rights_risk_summary(payload.get("privacy_rights_risk_summary"), errors)
    _validate_provenance_summary(payload.get("provenance_summary"), errors)
    _validate_no_mutation_guarantees(payload.get("no_mutation_guarantees"), payload, errors)
    _validate_reset_delete_export_policy(payload.get("reset_delete_export_policy"), errors)

    if not isinstance(payload.get("limitations"), list) or not payload.get("limitations"):
        errors.append("limitations must be a non-empty array.")


def _validate_created_by_tool(value: Any, errors: list[str]) -> None:
    if not isinstance(value, Mapping):
        errors.append("created_by_tool must be an object.")
        return
    for field in ["tool_id", "tool_version", "tool_status"]:
        if not isinstance(value.get(field), str) or not value.get(field):
            errors.append(f"created_by_tool.{field} must be a non-empty string.")
    _validate_enum(value.get("tool_status"), {"contract_example", "future_local_tool"}, "created_by_tool.tool_status", errors)


def _validate_validate_report_ref(value: Any, errors: list[str]) -> None:
    if not isinstance(value, Mapping):
        errors.append("source_validate_report_ref must be an object.")
        return
    for field in ["report_id", "report_path_policy", "report_status", "report_created_by_tool", "limitations"]:
        if field not in value:
            errors.append(f"source_validate_report_ref.{field}: required field is missing.")
    _validate_enum(value.get("report_path_policy"), REPORT_PATH_POLICIES, "source_validate_report_ref.report_path_policy", errors)
    _validate_enum(value.get("report_status"), REPORT_STATUSES, "source_validate_report_ref.report_status", errors)
    if "report_checksum" in value and not _is_sha256_ref(value.get("report_checksum")):
        errors.append("source_validate_report_ref.report_checksum must be sha256:<64 lowercase hex>.")
    if not isinstance(value.get("limitations"), list) or not value.get("limitations"):
        errors.append("source_validate_report_ref.limitations must be a non-empty array.")


def _validate_staged_pack_ref(value: Any, index: int, errors: list[str]) -> None:
    prefix = f"staged_pack_refs[{index}]"
    if not isinstance(value, Mapping):
        errors.append(f"{prefix} must be an object.")
        return
    required = {
        "staged_pack_ref",
        "pack_id",
        "pack_version",
        "pack_type",
        "pack_checksum",
        "pack_root_policy",
        "validation_status",
        "privacy_classification",
        "rights_classification",
        "risk_classification",
        "limitations",
    }
    for field in sorted(required - set(value)):
        errors.append(f"{prefix}.{field}: required field is missing.")
    _validate_enum(value.get("pack_type"), PACK_TYPES, f"{prefix}.pack_type", errors)
    _validate_enum(value.get("pack_root_policy"), PACK_ROOT_POLICIES, f"{prefix}.pack_root_policy", errors)
    _validate_enum(value.get("validation_status"), VALIDATION_STATUSES, f"{prefix}.validation_status", errors)
    _validate_enum(value.get("privacy_classification"), PRIVACY_CLASSIFICATIONS, f"{prefix}.privacy_classification", errors)
    _validate_enum(value.get("rights_classification"), RIGHTS_CLASSIFICATIONS, f"{prefix}.rights_classification", errors)
    _validate_enum(value.get("risk_classification"), RISK_CLASSIFICATIONS, f"{prefix}.risk_classification", errors)
    if not _is_sha256_ref(value.get("pack_checksum")):
        errors.append(f"{prefix}.pack_checksum must be sha256:<64 lowercase hex>.")
    if not isinstance(value.get("limitations"), list) or not value.get("limitations"):
        errors.append(f"{prefix}.limitations must be a non-empty array.")


def _validate_staged_entity(value: Any, index: int, errors: list[str]) -> None:
    prefix = f"staged_entities[{index}]"
    if not isinstance(value, Mapping):
        errors.append(f"{prefix} must be an object.")
        return
    required = {
        "staged_entity_id",
        "entity_type",
        "public_safe",
        "privacy_classification",
        "rights_classification",
        "risk_classification",
        "review_status",
        "summary",
        "limitations",
        "provenance_refs",
    }
    for field in sorted(required - set(value)):
        errors.append(f"{prefix}.{field}: required field is missing.")
    _validate_enum(value.get("entity_type"), ENTITY_TYPES, f"{prefix}.entity_type", errors)
    _validate_enum(value.get("privacy_classification"), PRIVACY_CLASSIFICATIONS, f"{prefix}.privacy_classification", errors)
    _validate_enum(value.get("rights_classification"), RIGHTS_CLASSIFICATIONS, f"{prefix}.rights_classification", errors)
    _validate_enum(value.get("risk_classification"), RISK_CLASSIFICATIONS, f"{prefix}.risk_classification", errors)
    _validate_enum(value.get("review_status"), REVIEW_STATUSES, f"{prefix}.review_status", errors)
    if not isinstance(value.get("public_safe"), bool):
        errors.append(f"{prefix}.public_safe must be boolean.")
    if value.get("review_status") in {"local_index_candidate_future", "contribution_candidate_future"}:
        if not str(value.get("entity_type", "")).endswith("_candidate"):
            errors.append(f"{prefix}.future candidate review status requires a candidate entity type.")
    if not isinstance(value.get("limitations"), list) or not value.get("limitations"):
        errors.append(f"{prefix}.limitations must be a non-empty array.")
    if not isinstance(value.get("provenance_refs"), list) or not value.get("provenance_refs"):
        errors.append(f"{prefix}.provenance_refs must be a non-empty array.")
    for forbidden in ["canonical", "accepted_public", "master_index_accepted"]:
        if forbidden in str(value.get("review_status", "")).lower():
            errors.append(f"{prefix}.review_status must not claim canonical or public acceptance.")


def _validate_counts(pack_counts: Any, pack_refs: list[Any], entities: list[Any], errors: list[str]) -> None:
    if not isinstance(pack_counts, Mapping):
        errors.append("counts must be an object.")
        return
    for field in sorted(COUNT_FIELDS):
        if not isinstance(pack_counts.get(field), int) or pack_counts.get(field) < 0:
            errors.append(f"counts.{field} must be a non-negative integer.")

    entity_types = [entity.get("entity_type") for entity in entities if isinstance(entity, Mapping)]
    expected = {
        "staged_pack_count": len(pack_refs),
        "staged_entity_count": len(entities),
        "staged_source_candidate_count": entity_types.count("staged_source_candidate"),
        "staged_evidence_candidate_count": entity_types.count("staged_evidence_candidate"),
        "staged_index_summary_count": entity_types.count("staged_index_summary"),
        "staged_contribution_candidate_count": entity_types.count("staged_contribution_candidate"),
        "staged_ai_output_candidate_count": entity_types.count("staged_ai_output_candidate"),
        "issue_count": entity_types.count("staged_issue"),
        "blocked_issue_count": sum(
            1
            for entity in entities
            if isinstance(entity, Mapping)
            and entity.get("entity_type") == "staged_issue"
            and entity.get("review_status") == "quarantine_required"
        ),
        "private_record_count": sum(
            1
            for entity in entities
            if isinstance(entity, Mapping)
            and entity.get("privacy_classification") in {"local_private", "restricted"}
        ),
        "public_safe_record_count": sum(
            1
            for entity in entities
            if isinstance(entity, Mapping)
            and entity.get("public_safe") is True
        ),
    }
    for field, expected_value in expected.items():
        if pack_counts.get(field) != expected_value:
            errors.append(f"counts.{field} must be {expected_value} for staged_entities in this manifest.")


def _validate_privacy_rights_risk_summary(value: Any, errors: list[str]) -> None:
    if not isinstance(value, Mapping):
        errors.append("privacy_rights_risk_summary must be an object.")
        return
    if value.get("default_visibility") != "local_private":
        errors.append("privacy_rights_risk_summary.default_visibility must be local_private.")
    _validate_enum(value.get("privacy_classification"), PRIVACY_CLASSIFICATIONS, "privacy_rights_risk_summary.privacy_classification", errors)
    _validate_enum(value.get("rights_classification"), RIGHTS_CLASSIFICATIONS, "privacy_rights_risk_summary.rights_classification", errors)
    _validate_enum(value.get("risk_classification"), RISK_CLASSIFICATIONS, "privacy_rights_risk_summary.risk_classification", errors)
    for field in [
        "private_paths_present",
        "credentials_present",
        "executable_payloads_present",
        "raw_database_or_cache_present",
        "rights_clearance_claimed",
        "malware_safety_claimed",
        "canonical_truth_claimed",
    ]:
        if value.get(field) is not False:
            errors.append(f"privacy_rights_risk_summary.{field} must be false.")


def _validate_provenance_summary(value: Any, errors: list[str]) -> None:
    if not isinstance(value, Mapping):
        errors.append("provenance_summary must be an object.")
        return
    for field in [
        "validate_report_linked",
        "pack_checksums_recorded",
        "pack_versions_recorded",
        "validator_tool_ids_recorded",
        "staged_entities_link_to_pack_refs",
        "operator_action_required_future",
    ]:
        if value.get(field) is not True:
            errors.append(f"provenance_summary.{field} must be true.")


def _validate_no_mutation_guarantees(value: Any, payload: Mapping[str, Any], errors: list[str]) -> None:
    if not isinstance(value, Mapping):
        errors.append("no_mutation_guarantees must be an object.")
        return
    for field in HARD_FALSE_FIELDS:
        if value.get(field) is not False:
            errors.append(f"no_mutation_guarantees.{field} must be false.")
        if field in payload and value.get(field) != payload.get(field):
            errors.append(f"no_mutation_guarantees.{field} must match top-level {field}.")


def _validate_reset_delete_export_policy(value: Any, errors: list[str]) -> None:
    if not isinstance(value, Mapping):
        errors.append("reset_delete_export_policy must be an object.")
        return
    for field in [
        "delete_staged_pack_supported_future",
        "clear_all_staged_state_supported_future",
        "export_manifest_supported_future",
        "export_public_safe_report_supported_future",
        "irreversible_delete_requires_confirmation_future",
    ]:
        if value.get(field) is not True:
            errors.append(f"reset_delete_export_policy.{field} must be true.")
    if value.get("export_private_data_default") is not False:
        errors.append("reset_delete_export_policy.export_private_data_default must be false.")
    if not isinstance(value.get("notes"), list) or not value.get("notes"):
        errors.append("reset_delete_export_policy.notes must be a non-empty array.")


def _validate_example_root(root: Path, *, strict: bool, errors: list[str]) -> None:
    if not root.exists() or not root.is_dir():
        errors.append(f"{_display_path(root)}: manifest root is missing.")
        return
    for filename in [MANIFEST_NAME, "README.md", CHECKSUMS_NAME]:
        if not (root / filename).is_file():
            errors.append(f"{_display_path(root / filename)}: required example file is missing.")
    _validate_checksums(root, strict=strict, errors=errors)


def _validate_checksums(root: Path, *, strict: bool, errors: list[str]) -> None:
    checksum_path = root / CHECKSUMS_NAME
    if not checksum_path.exists():
        errors.append(f"{_display_path(checksum_path)}: checksum file is missing.")
        return

    covered: set[str] = set()
    for line_number, raw_line in enumerate(checksum_path.read_text(encoding="utf-8").splitlines(), start=1):
        if not raw_line.strip():
            continue
        parts = raw_line.split(None, 1)
        if len(parts) != 2:
            errors.append(f"{_display_path(checksum_path)}:{line_number}: checksum line must contain hash and relative path.")
            continue
        expected, relative_name = parts[0], parts[1].strip()
        if not re.fullmatch(r"[a-f0-9]{64}", expected):
            errors.append(f"{_display_path(checksum_path)}:{line_number}: checksum must be 64 lowercase hex chars.")
            continue
        if Path(relative_name).is_absolute() or ".." in Path(relative_name).parts:
            errors.append(f"{_display_path(checksum_path)}:{line_number}: checksum path must be pack-root relative.")
            continue
        target = root / relative_name
        if not target.is_file():
            errors.append(f"{_display_path(target)}: checksum target is missing.")
            continue
        actual = hashlib.sha256(target.read_bytes()).hexdigest()
        if actual != expected:
            errors.append(f"{_display_path(target)}: checksum mismatch.")
        covered.add(relative_name.replace("\\", "/"))

    required = {MANIFEST_NAME, "README.md"}
    missing = required - covered
    if missing:
        errors.append(f"{_display_path(checksum_path)}: missing required checksum entries {sorted(missing)}.")
    if strict:
        actual_files = {
            str(path.relative_to(root)).replace("\\", "/")
            for path in root.rglob("*")
            if path.is_file() and path.name != CHECKSUMS_NAME
        }
        missing_strict = actual_files - covered
        if missing_strict:
            errors.append(f"{_display_path(checksum_path)}: strict mode missing entries {sorted(missing_strict)}.")


def _validate_no_private_paths_or_secrets(payload: Mapping[str, Any], errors: list[str]) -> None:
    for path, value in _walk(payload):
        key = str(path[-1]) if path else ""
        if SECRET_KEY_RE.search(key) and value is not False:
            errors.append(f"{_join(path)}: secret-like field names are not allowed unless they are explicit false policy flags.")
        if isinstance(value, str):
            if SECRET_VALUE_RE.search(value):
                errors.append(f"{_join(path)}: secret-like value is not allowed in local staging manifests.")
            if PRIVATE_PATH_RE.search(value):
                errors.append(f"{_join(path)}: private absolute paths must be redacted before manifest validation.")


def _validate_no_authority_claims(payload: Mapping[str, Any], errors: list[str]) -> None:
    for path, value in _walk(payload):
        key = str(path[-1]).lower() if path else ""
        if isinstance(value, bool) and value and key in {
            "rights_clearance_claimed",
            "malware_safety_claimed",
            "canonical_truth_claimed",
            "master_index_mutated",
            "public_search_mutated",
            "local_index_mutated",
        }:
            errors.append(f"{_join(path)}: manifests cannot claim rights, malware, truth, search, index, or master-index authority.")
        if isinstance(value, str):
            text = value.lower()
            for phrase in FORBIDDEN_AUTHORITY_PATTERNS:
                if phrase in text:
                    errors.append(f"{_join(path)}: forbidden authority claim phrase: {phrase}.")


def _validate_enum(value: Any, allowed: set[str], field: str, errors: list[str]) -> None:
    if value not in allowed:
        errors.append(f"{field} must be one of {sorted(allowed)}.")


def _is_sha256_ref(value: Any) -> bool:
    return isinstance(value, str) and re.fullmatch(r"sha256:[a-f0-9]{64}", value) is not None


def _load_json(path: Path, errors: list[str]) -> Any:
    if not path.exists():
        errors.append(f"{_rel(path)}: file is missing.")
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"{_rel(path)}: invalid JSON: {exc}.")
        return None


def _walk(value: Any, path: tuple[str, ...] = ()) -> list[tuple[tuple[str, ...], Any]]:
    results: list[tuple[tuple[str, ...], Any]] = []
    if isinstance(value, Mapping):
        for key, nested in value.items():
            results.extend(_walk(nested, path + (str(key),)))
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            results.extend(_walk(nested, path + (str(index),)))
    else:
        results.append((path, value))
    return results


def _join(path: tuple[str, ...]) -> str:
    return ".".join(path) if path else "<root>"


def _result(path: Path, payload: Mapping[str, Any] | None, errors: list[str]) -> dict[str, Any]:
    return {
        "path": _display_path(path),
        "ok": not errors,
        "status": "passed" if not errors else "failed",
        "manifest_id": payload.get("manifest_id") if isinstance(payload, Mapping) else None,
        "manifest_status": payload.get("status") if isinstance(payload, Mapping) else None,
        "staging_mode": payload.get("staging_mode") if isinstance(payload, Mapping) else None,
        "staged_pack_count": (
            payload.get("counts", {}).get("staged_pack_count")
            if isinstance(payload, Mapping) and isinstance(payload.get("counts"), Mapping)
            else None
        ),
        "staged_entity_count": (
            payload.get("counts", {}).get("staged_entity_count")
            if isinstance(payload, Mapping) and isinstance(payload.get("counts"), Mapping)
            else None
        ),
        "errors": errors,
    }


def _summarize(results: list[dict[str, Any]]) -> dict[str, int]:
    passed = sum(1 for result in results if result["ok"])
    failed = len(results) - passed
    return {"total": len(results), "passed": passed, "failed": failed}


def _format_plain(report: Mapping[str, Any]) -> str:
    lines = [
        "Local Staging Manifest validation",
        f"status: {report['status']}",
        f"mode: {report['mode']}",
        f"checked_manifests: {report['summary']['total']}",
        f"passed: {report['summary']['passed']}",
        f"failed: {report['summary']['failed']}",
        f"staging_performed: {report['staging_performed']}",
        f"indexing_performed: {report['indexing_performed']}",
        f"public_search_mutated: {report['public_search_mutated']}",
        f"master_index_mutation_performed: {report['master_index_mutation_performed']}",
    ]
    for result in report.get("checked_manifests", []):
        lines.append(
            f"- {result['path']}: {'passed' if result['ok'] else 'failed'} "
            f"({result.get('manifest_status')}, {result.get('staging_mode')})"
        )
    if report["errors"]:
        lines.append("")
        lines.append("Errors")
        lines.extend(f"- {error}" for error in report["errors"])
    return "\n".join(lines) + "\n"


def _resolve(path: Path) -> Path:
    return path if path.is_absolute() else (REPO_ROOT / path).resolve()


def _rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return str(path)


def _display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.name


if __name__ == "__main__":
    raise SystemExit(main())
