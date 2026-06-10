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
    / "user_hardware_details_00"
    / "user_hardware_details_return.json"
)
SCHEMA_VERSION = "user_hardware_details_return_validation.v0"
VALIDATOR_ID = "user_hardware_details_return_validator_v0"

REQUIRED_TOP_LEVEL_FIELDS = {
    "schema_version",
    "task_id",
    "query_id",
    "submitted_at",
    "submitted_by",
    "device_identity",
    "device_ids",
    "machine_context",
    "windows_context",
    "source_or_media_context",
    "attachments_or_observations",
    "redactions_applied",
    "truth_boundary",
    "recommended_next_action",
}
REQUIRED_OBJECT_FIELDS = {
    "device_identity": {
        "hardware_vendor",
        "hardware_model",
        "chipset",
        "board_revision",
        "fcc_id_or_label",
        "product_label_text",
    },
    "device_ids": {
        "pci_vendor_device_id",
        "isa_pnp_id",
        "usb_vid_pid",
        "pcmcia_cardbus_id",
        "other_device_id",
        "observed_from",
    },
    "machine_context": {
        "machine_vendor",
        "machine_model",
        "motherboard_vendor",
        "motherboard_model",
        "bios",
        "bus_or_interface",
    },
    "windows_context": {
        "windows_version",
        "windows_98_edition",
        "language_or_region",
        "architecture",
        "service_pack_or_update_pack",
    },
    "source_or_media_context": {
        "existing_driver_media",
        "media_label",
        "candidate_source_url_or_citation",
        "previously_tried_driver",
        "observed_error_messages",
    },
}
ALLOWED_NEXT_ACTIONS = {
    "review_hardware_details",
    "request_more_details",
    "mark_blocked_for_user_details",
    "reject_candidate",
}
FORBIDDEN_TRUE_FIELDS = {
    "driver_recommended",
    "reviewed_artifact_record_created",
    "verified_artifact_created",
    "download_or_execution_performed",
    "rights_clearance_claimed",
    "malware_safety_claimed",
}
FORBIDDEN_CLAIM_PHRASES = (
    "driver recommended",
    "safe to install",
    "safe to download",
    "malware safe",
    "malware clean",
    "rights cleared",
    "rights clearance approved",
    "verified artifact",
    "public alpha ready",
)
PRIVATE_PATH_RE = re.compile(
    r"([A-Za-z]:[\\/](Users|Documents and Settings|Projects)[\\/]|"
    r"\\\\[^\\/\s]+[\\/][^\\/\s]+[\\/]|"
    r"/(Users|home|var/folders|private/tmp|tmp)/)",
    re.IGNORECASE,
)
SECRET_KEY_RE = re.compile(r"(api[_-]?key|auth[_-]?token|password|private[_-]?key|secret|license[_-]?key)", re.IGNORECASE)
SECRET_VALUE_RE = re.compile(r"(sk-[A-Za-z0-9_-]{8,}|-----BEGIN [A-Z ]*PRIVATE KEY-----)", re.IGNORECASE)


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate a user hardware details return packet.")
    parser.add_argument("--return-file", help="User hardware details return JSON to validate.")
    parser.add_argument("--json", action="store_true", help="Emit JSON report.")
    parser.add_argument("--strict", action="store_true", help="Require enough detail to leave blocked status.")
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
    completeness = _empty_completeness()
    if isinstance(payload, Mapping):
        completeness = _validate_payload(payload, strict=strict, errors=errors, warnings=warnings)
    elif not errors:
        errors.append("hardware details return must be a JSON object.")

    return {
        "schema_version": SCHEMA_VERSION,
        "validator_id": VALIDATOR_ID,
        "status": "valid" if not errors else "invalid",
        "return_file": _display_path(resolved),
        "task_id": payload.get("task_id") if isinstance(payload, Mapping) else None,
        "query_id": payload.get("query_id") if isinstance(payload, Mapping) else None,
        "recommended_next_action": payload.get("recommended_next_action") if isinstance(payload, Mapping) else None,
        "detail_completeness": completeness,
        "sufficient_for_hardware_review": all(completeness.values()),
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
) -> dict[str, bool]:
    for field in sorted(REQUIRED_TOP_LEVEL_FIELDS - set(payload)):
        errors.append(f"{field}: required field is missing.")

    if payload.get("schema_version") != "user_hardware_details_return.v0":
        errors.append("schema_version must be user_hardware_details_return.v0.")
    if payload.get("task_id") != "USER-HARDWARE-DETAILS-00":
        errors.append("task_id must be USER-HARDWARE-DETAILS-00.")
    if payload.get("query_id") != "hq_driver_win98":
        errors.append("query_id must be hq_driver_win98.")
    if payload.get("recommended_next_action") not in ALLOWED_NEXT_ACTIONS:
        errors.append(
            "recommended_next_action must be one of "
            + ", ".join(sorted(ALLOWED_NEXT_ACTIONS))
            + "."
        )

    sections: dict[str, Mapping[str, Any]] = {}
    for section, required_fields in REQUIRED_OBJECT_FIELDS.items():
        value = payload.get(section)
        if not isinstance(value, Mapping):
            errors.append(f"{section} must be an object.")
            sections[section] = {}
            continue
        sections[section] = value
        for field in sorted(required_fields - set(value)):
            errors.append(f"{section}.{field}: required field is missing.")

    for field in ["attachments_or_observations", "redactions_applied"]:
        if field in payload and not isinstance(payload.get(field), list):
            errors.append(f"{field} must be an array.")

    truth_boundary = payload.get("truth_boundary")
    if not isinstance(truth_boundary, Mapping):
        errors.append("truth_boundary must be an object.")
    else:
        for field in sorted(FORBIDDEN_TRUE_FIELDS - set(truth_boundary)):
            errors.append(f"truth_boundary.{field}: required field is missing.")
        for field in FORBIDDEN_TRUE_FIELDS & set(truth_boundary):
            if truth_boundary.get(field) is True:
                errors.append(f"truth_boundary.{field} must be false in a hardware details return.")

    completeness = _hardware_detail_completeness(sections, payload)
    missing = [field for field, complete in completeness.items() if not complete]
    if strict and missing:
        errors.append("strict hardware review requires: " + ", ".join(missing) + ".")
    elif missing:
        warnings.append("hardware details are incomplete: " + ", ".join(missing) + ".")

    if payload.get("recommended_next_action") == "review_hardware_details" and missing:
        warnings.append("review_hardware_details should not be used until hardware detail completeness is satisfied.")

    _validate_no_private_paths_or_secrets(payload, errors)
    _validate_no_forbidden_claim_text(payload, errors)
    return completeness


def _hardware_detail_completeness(sections: Mapping[str, Mapping[str, Any]], payload: Mapping[str, Any]) -> dict[str, bool]:
    device_identity = sections.get("device_identity", {})
    device_ids = sections.get("device_ids", {})
    machine_context = sections.get("machine_context", {})
    windows_context = sections.get("windows_context", {})
    source_or_media_context = sections.get("source_or_media_context", {})

    has_device_id = _any_non_empty(
        device_ids,
        [
            "pci_vendor_device_id",
            "isa_pnp_id",
            "usb_vid_pid",
            "pcmcia_cardbus_id",
            "other_device_id",
        ],
    )
    has_source_or_media_context = _any_non_empty(
        source_or_media_context,
        [
            "existing_driver_media",
            "media_label",
            "candidate_source_url_or_citation",
            "previously_tried_driver",
            "observed_error_messages",
        ],
    ) or bool(payload.get("attachments_or_observations"))

    return {
        "hardware_vendor": _non_empty(device_identity.get("hardware_vendor")),
        "hardware_identity": _any_non_empty(
            device_identity,
            ["hardware_model", "chipset", "fcc_id_or_label", "product_label_text"],
        ),
        "device_id": has_device_id,
        "device_id_observed_from": (not has_device_id) or _non_empty(device_ids.get("observed_from")),
        "bus_or_interface": _non_empty(machine_context.get("bus_or_interface")),
        "windows_version": _non_empty(windows_context.get("windows_version")),
        "windows_98_edition": _non_empty(windows_context.get("windows_98_edition")),
        "architecture": _non_empty(windows_context.get("architecture")),
        "source_or_media_context": has_source_or_media_context,
    }


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
                errors.append(f"{_join(path)}: hardware details returns cannot claim {phrase}.")


def _walk(value: Any, path: tuple[Any, ...] = ()) -> list[tuple[tuple[Any, ...], Any]]:
    values = [(path, value)]
    if isinstance(value, Mapping):
        for key, child in value.items():
            values.extend(_walk(child, path + (key,)))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            values.extend(_walk(child, path + (index,)))
    return values


def _non_empty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _any_non_empty(values: Mapping[str, Any], fields: Sequence[str]) -> bool:
    return any(_non_empty(values.get(field)) for field in fields)


def _empty_completeness() -> dict[str, bool]:
    return {
        "hardware_vendor": False,
        "hardware_identity": False,
        "device_id": False,
        "device_id_observed_from": False,
        "bus_or_interface": False,
        "windows_version": False,
        "windows_98_edition": False,
        "architecture": False,
        "source_or_media_context": False,
    }


def _join(path: Sequence[Any]) -> str:
    return ".".join(str(item) for item in path) if path else "<root>"


def _display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except (OSError, ValueError):
        return path.resolve().as_posix()


def _format_plain(report: Mapping[str, Any]) -> str:
    lines = [
        "User Hardware Details Return validation",
        f"status: {report['status']}",
        f"return_file: {report['return_file']}",
        f"task_id: {report['task_id']}",
        f"query_id: {report['query_id']}",
        f"recommended_next_action: {report['recommended_next_action']}",
        f"sufficient_for_hardware_review: {report['sufficient_for_hardware_review']}",
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

