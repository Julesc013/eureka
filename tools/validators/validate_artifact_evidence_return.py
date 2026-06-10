from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RETURN_FILE = (
    REPO_ROOT.parent
    / "eureka-evidence-runs"
    / "artifact_evidence_collection_00"
    / "artifact_evidence_collection_summary.json"
)
SCHEMA_VERSION = "artifact_evidence_return_validation.v0"
VALIDATOR_ID = "artifact_evidence_return_validator_v0"

REQUIRED_TOP_LEVEL_FIELDS = {
    "schema_version",
    "run_id",
    "collected_at",
    "collector",
    "target_results",
    "raw_artifacts_retained_outside_repo",
    "downloads_performed",
    "executables_fetched",
    "install_or_execution_performed",
    "rights_clearance_claimed",
    "malware_safety_claimed",
    "resume_recommended_task",
}
REQUIRED_TARGET_FIELDS = {
    "target_id",
    "status",
    "source_refs",
    "observed_fields",
    "remaining_gaps",
    "recommended_review_action",
}
ALLOWED_STATUSES = {
    "evidence_collected",
    "partially_collected",
    "blocked",
    "not_found",
    "deferred",
}
ALLOWED_REVIEW_ACTIONS = {
    "promote_to_review_candidate",
    "request_more_evidence",
    "mark_near_miss",
    "mark_need",
    "mark_blocked_for_user_details",
    "reject",
    "defer",
}
ALLOWED_ARTIFACT_LEVELS = {
    "level0_mention_only",
    "level1_metadata_or_source_lead",
    "level2_source_observed_artifact_listing",
    "level3_artifact_identity_evidence",
    "level4_artifact_integrity_evidence",
    "level5_verified_acquisition_or_reproducibility_path",
}
FORBIDDEN_TRUE_FIELDS = {
    "downloads_performed",
    "executables_fetched",
    "install_or_execution_performed",
    "rights_clearance_claimed",
    "malware_safety_claimed",
    "reviewed_artifact_record_created",
    "verified_artifact_created",
    "driver_recommended",
}
FORBIDDEN_CLAIM_PHRASES = (
    "reviewed artifact record created",
    "verified artifact",
    "rights cleared",
    "rights clearance approved",
    "malware safe",
    "malware clean",
    "safe to download",
    "safe to install",
    "driver recommended",
    "public alpha ready",
    "production ready",
)
PRIVATE_PATH_RE = re.compile(
    r"([A-Za-z]:[\\/](Users|Documents and Settings|Projects)[\\/]|"
    r"\\\\[^\\/\s]+[\\/][^\\/\s]+[\\/]|"
    r"/(Users|home|var/folders|private/tmp|tmp)/)",
    re.IGNORECASE,
)
SECRET_KEY_RE = re.compile(r"(api[_-]?key|auth[_-]?token|password|private[_-]?key|secret)", re.IGNORECASE)
SECRET_VALUE_RE = re.compile(r"(sk-[A-Za-z0-9_-]{8,}|-----BEGIN [A-Z ]*PRIVATE KEY-----)", re.IGNORECASE)


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate an external artifact evidence return summary.")
    parser.add_argument("--return-file", help="Artifact evidence collection summary JSON to validate.")
    parser.add_argument("--json", action="store_true", help="Emit JSON report.")
    parser.add_argument("--strict", action="store_true", help="Require at least one target result.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    report = validate_return_file(
        Path(args.return_file) if args.return_file else DEFAULT_RETURN_FILE,
        strict=args.strict,
    )
    stream = stdout or sys.stdout
    if args.json:
        stream.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        stream.write(_format_plain(report))
    return 0 if report["status"] == "valid" else 1


def validate_return_file(path: Path, *, strict: bool = False) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    resolved = path if path.is_absolute() else (REPO_ROOT / path).resolve()
    payload = _load_json(resolved, errors)
    if isinstance(payload, Mapping):
        _validate_payload(payload, strict=strict, errors=errors, warnings=warnings)
    elif not errors:
        errors.append("return summary must be a JSON object.")

    target_results = payload.get("target_results") if isinstance(payload, Mapping) else []
    return {
        "schema_version": SCHEMA_VERSION,
        "validator_id": VALIDATOR_ID,
        "status": "valid" if not errors else "invalid",
        "return_file": _display_path(resolved),
        "run_id": payload.get("run_id") if isinstance(payload, Mapping) else None,
        "target_result_count": len(target_results) if isinstance(target_results, list) else 0,
        "resume_recommended_task": payload.get("resume_recommended_task") if isinstance(payload, Mapping) else None,
        "network_performed": False,
        "mutation_performed": False,
        "truth_created": False,
        "errors": errors,
        "warnings": warnings,
    }


def _validate_payload(
    payload: Mapping[str, Any],
    *,
    strict: bool,
    errors: list[str],
    warnings: list[str],
) -> None:
    for field in sorted(REQUIRED_TOP_LEVEL_FIELDS - set(payload)):
        errors.append(f"{field}: required field is missing.")

    if payload.get("resume_recommended_task") != "MANUAL-ARTIFACT-OBSERVATION-BATCH-03":
        errors.append("resume_recommended_task must be MANUAL-ARTIFACT-OBSERVATION-BATCH-03.")

    for field in [
        "raw_artifacts_retained_outside_repo",
        "downloads_performed",
        "executables_fetched",
        "install_or_execution_performed",
        "rights_clearance_claimed",
        "malware_safety_claimed",
    ]:
        if field in payload and not isinstance(payload.get(field), bool):
            errors.append(f"{field} must be boolean.")
    for field in FORBIDDEN_TRUE_FIELDS & set(payload):
        if payload.get(field) is True:
            errors.append(f"{field} must be false for this no-download external return.")

    target_results = payload.get("target_results")
    if not isinstance(target_results, list):
        errors.append("target_results must be an array.")
        target_results = []
    elif strict and not target_results:
        errors.append("target_results must include at least one result in strict mode.")

    target_ids: set[str] = set()
    source_ref_ids: set[str] = set()
    for index, result in enumerate(target_results):
        if not isinstance(result, Mapping):
            errors.append(f"target_results[{index}] must be an object.")
            continue
        _validate_target_result(result, index, errors, warnings)
        target_id = result.get("target_id")
        if isinstance(target_id, str):
            if target_id in target_ids:
                errors.append(f"target_results[{index}].target_id duplicates {target_id}.")
            target_ids.add(target_id)
        for source_ref in result.get("source_refs", []):
            if isinstance(source_ref, str):
                source_ref_ids.add(source_ref)

    if not source_ref_ids and any(
        isinstance(result, Mapping) and result.get("status") in {"evidence_collected", "partially_collected"}
        for result in target_results
    ):
        warnings.append("evidence_collected or partially_collected results should include source_refs.")

    _validate_no_private_paths_or_secrets(payload, errors)
    _validate_no_forbidden_claim_text(payload, errors)


def _validate_target_result(
    result: Mapping[str, Any],
    index: int,
    errors: list[str],
    warnings: list[str],
) -> None:
    prefix = f"target_results[{index}]"
    for field in sorted(REQUIRED_TARGET_FIELDS - set(result)):
        errors.append(f"{prefix}.{field}: required field is missing.")

    target_id = result.get("target_id")
    if not isinstance(target_id, str) or not target_id:
        errors.append(f"{prefix}.target_id must be a non-empty string.")
        target_id_text = ""
    else:
        target_id_text = target_id.lower()

    status = result.get("status")
    if status not in ALLOWED_STATUSES:
        errors.append(f"{prefix}.status must be one of {', '.join(sorted(ALLOWED_STATUSES))}.")

    source_refs = result.get("source_refs")
    if not isinstance(source_refs, list) or any(not isinstance(item, str) or not item for item in source_refs):
        errors.append(f"{prefix}.source_refs must be an array of non-empty strings.")

    observed_fields = result.get("observed_fields")
    if not isinstance(observed_fields, Mapping):
        errors.append(f"{prefix}.observed_fields must be an object.")
        observed_fields = {}

    remaining_gaps = result.get("remaining_gaps")
    if not isinstance(remaining_gaps, list) or any(not isinstance(item, str) or not item for item in remaining_gaps):
        errors.append(f"{prefix}.remaining_gaps must be an array of non-empty strings.")

    action = result.get("recommended_review_action")
    if action not in ALLOWED_REVIEW_ACTIONS:
        errors.append(f"{prefix}.recommended_review_action must be one of {', '.join(sorted(ALLOWED_REVIEW_ACTIONS))}.")

    level = result.get("artifact_evidence_level") or observed_fields.get("artifact_evidence_level")
    if level is not None and level not in ALLOWED_ARTIFACT_LEVELS:
        errors.append(f"{prefix}.artifact_evidence_level must use the governed level vocabulary.")

    for field in FORBIDDEN_TRUE_FIELDS & set(result):
        if result.get(field) is True:
            errors.append(f"{prefix}.{field} must be false in an external return.")
    truth_boundary = result.get("truth_boundary")
    if isinstance(truth_boundary, Mapping):
        for field in FORBIDDEN_TRUE_FIELDS & set(truth_boundary):
            if truth_boundary.get(field) is True:
                errors.append(f"{prefix}.truth_boundary.{field} must be false in an external return.")

    if "win98" in target_id_text or "driver" in target_id_text:
        _validate_driver_target(prefix, result, observed_fields, errors, warnings)


def _validate_driver_target(
    prefix: str,
    result: Mapping[str, Any],
    observed_fields: Mapping[str, Any],
    errors: list[str],
    warnings: list[str],
) -> None:
    action = result.get("recommended_review_action")
    status = result.get("status")
    if action != "mark_blocked_for_user_details":
        warnings.append(f"{prefix}: Windows 98 or driver targets should normally remain blocked for user details.")
    if status not in {"blocked", "deferred"}:
        required_identity = ("hardware_vendor", "hardware_model", "chipset", "bus_or_interface", "windows_version")
        missing = [field for field in required_identity if not observed_fields.get(field)]
        if missing:
            errors.append(f"{prefix}: driver target is not blocked/deferred but lacks hardware identity fields {', '.join(missing)}.")


def _load_json(path: Path, errors: list[str]) -> Any:
    if not path.exists():
        errors.append(f"{_display_path(path)}: file is missing.")
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"{_display_path(path)}: invalid JSON: {exc.msg}.")
        return None


def _validate_no_private_paths_or_secrets(payload: Mapping[str, Any], errors: list[str]) -> None:
    for path, value in _walk(payload):
        key = str(path[-1]) if path else ""
        if SECRET_KEY_RE.search(key):
            errors.append(f"{_join(path)}: secret-like field names are not allowed.")
        if isinstance(value, str):
            if SECRET_VALUE_RE.search(value):
                errors.append(f"{_join(path)}: secret-like values are not allowed.")
            if PRIVATE_PATH_RE.search(value):
                errors.append(f"{_join(path)}: private or absolute local evidence paths are not allowed.")


def _validate_no_forbidden_claim_text(payload: Mapping[str, Any], errors: list[str]) -> None:
    for path, value in _walk(payload):
        if not isinstance(value, str):
            continue
        lowered = value.lower()
        for phrase in FORBIDDEN_CLAIM_PHRASES:
            if phrase in lowered:
                errors.append(f"{_join(path)}: external returns cannot claim {phrase}.")


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


def _display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except (OSError, ValueError):
        return path.resolve().as_posix()


def _format_plain(report: Mapping[str, Any]) -> str:
    lines = [
        "Artifact Evidence Return validation",
        f"status: {report['status']}",
        f"return_file: {report['return_file']}",
        f"target_result_count: {report['target_result_count']}",
        f"resume_recommended_task: {report['resume_recommended_task']}",
        f"network_performed: {report['network_performed']}",
        f"mutation_performed: {report['mutation_performed']}",
        f"truth_created: {report['truth_created']}",
    ]
    for warning in report.get("warnings", []):
        lines.append(f"WARN: {warning}")
    for error in report.get("errors", []):
        lines.append(f"ERROR: {error}")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
