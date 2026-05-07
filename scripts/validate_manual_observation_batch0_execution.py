"""Validate the Batch 0 manual observation execution packet.

The checks are intentionally local and read-only: they prove that the packet is
ready for a human operator without opening browsers or producing observations.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence, TextIO

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.prepare_manual_observation_batch0_execution import (
    ALLOWED_MANUAL_ACTIONS,
    BATCH_PENDING,
    BATCH_ROOT,
    COMPLETION_STATES,
    FORBIDDEN_AUTOMATION,
    PRODUCT_BOUNDARY,
    build_slot_manifest,
)


EXECUTION_INVENTORY_PATH = "control/inventory/observations/manual_observation_batch_0_execution.json"
SLOT_MANIFEST_PATH = "control/inventory/observations/manual_observation_batch_0_slot_manifest.json"
AUDIT_REPORT_PATH = "control/audits/obs0-02-manual-observation-batch-0-execution-packet-v0/obs0_02_report.json"
AUDIT_SLOT_MANIFEST_PATH = "control/audits/obs0-02-manual-observation-batch-0-execution-packet-v0/slot_execution_manifest.json"
OBS0_01_AUDIT_PATH = "control/audits/obs0-01-manual-observation-protocol-v0/obs0_01_report.json"
DOC_PATHS = (
    "docs/operations/MANUAL_OBSERVATION_BATCH_0_EXECUTION.md",
    "docs/operations/MANUAL_OBSERVATION_SLOT_COMPLETION_GUIDE.md",
    "docs/operations/MANUAL_OBSERVATION_PROTOCOL.md",
    "docs/operations/MANUAL_OBSERVATION_ANTI_FABRICATION_CHECKLIST.md",
    "docs/operations/MANUAL_OBSERVATION_FAILURE_TAXONOMY.md",
)
BATCH_DOC_PATHS = (
    f"{BATCH_ROOT}/EXECUTION_PACKET.md",
    f"{BATCH_ROOT}/SLOT_COMPLETION_GUIDE.md",
    f"{BATCH_ROOT}/EXECUTION_STATUS.md",
    f"{BATCH_ROOT}/OBSERVATION_PROTOCOL.md",
    f"{BATCH_ROOT}/ANTI_FABRICATION_CHECKLIST.md",
    f"{BATCH_ROOT}/FAILURE_TAXONOMY.md",
)
PROTOCOL_REFS = {
    "docs/operations/MANUAL_OBSERVATION_PROTOCOL.md",
    "docs/operations/MANUAL_OBSERVATION_ANTI_FABRICATION_CHECKLIST.md",
    "docs/operations/MANUAL_OBSERVATION_FAILURE_TAXONOMY.md",
    "control/inventory/observations/manual_observation_policy.json",
    "control/inventory/observations/manual_observation_failure_taxonomy.json",
}
PRODUCT_BOUNDARY_FIELDS = set(PRODUCT_BOUNDARY) | {
    "changed_public_routes",
    "changed_generated_site_artifacts",
    "enabled_hosting",
    "enabled_source_sync",
}


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate Manual Observation Batch 0 execution packet.")
    parser.add_argument("--repo-root", default=str(REPO_ROOT), help="Repository root to validate.")
    parser.add_argument("--json", action="store_true", help="Emit deterministic JSON.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    report = validate_manual_observation_batch0_execution(Path(args.repo_root))
    output = stdout or sys.stdout
    if args.json:
        output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        output.write(_format_plain(report))
    return 0 if report["status"] == "valid" else 1


def validate_manual_observation_batch0_execution(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    root = repo_root.resolve()
    errors: list[str] = []
    warnings: list[str] = []

    execution_inventory = _load_json(root / EXECUTION_INVENTORY_PATH, errors)
    slot_manifest = _load_json(root / SLOT_MANIFEST_PATH, errors)
    audit_slot_manifest = _load_json(root / AUDIT_SLOT_MANIFEST_PATH, errors)
    audit_report = _load_json(root / AUDIT_REPORT_PATH, errors)

    errors.extend(validate_required_docs(root, DOC_PATHS, "docs"))
    errors.extend(validate_required_docs(root, BATCH_DOC_PATHS, "batch docs"))
    errors.extend(validate_execution_inventory(execution_inventory, EXECUTION_INVENTORY_PATH, root))
    errors.extend(validate_slot_manifest(slot_manifest, SLOT_MANIFEST_PATH, expected_manifest=build_slot_manifest(repo_root=root)))
    errors.extend(validate_slot_manifest(audit_slot_manifest, AUDIT_SLOT_MANIFEST_PATH, expected_manifest=build_slot_manifest(repo_root=root)))
    errors.extend(validate_audit_report(audit_report, AUDIT_REPORT_PATH))
    errors.extend(validate_pending_batch(root / BATCH_PENDING, root))
    errors.extend(validate_no_observed_files(root / BATCH_ROOT, root))

    if audit_slot_manifest != slot_manifest:
        errors.append(f"{AUDIT_SLOT_MANIFEST_PATH}: must match {SLOT_MANIFEST_PATH}")

    return {
        "schema_version": "manual_observation_batch0_execution_validation.v0",
        "status": "valid" if not errors else "invalid",
        "execution_inventory": EXECUTION_INVENTORY_PATH,
        "slot_manifest": SLOT_MANIFEST_PATH,
        "audit_report": AUDIT_REPORT_PATH,
        "errors": sorted(set(errors)),
        "warnings": sorted(set(warnings)),
    }


def validate_required_docs(repo_root: Path, paths: Sequence[str], label: str) -> list[str]:
    errors: list[str] = []
    for path in paths:
        full_path = repo_root / path
        if not full_path.is_file():
            errors.append(f"{label}: missing {path}")
            continue
        text = full_path.read_text(encoding="utf-8").lower()
        for phrase in ("manual", "pending"):
            if phrase not in text:
                errors.append(f"{path}: missing phrase {phrase!r}")
    return errors


def validate_execution_inventory(payload: Any, source: str, repo_root: Path = REPO_ROOT) -> list[str]:
    data = _mapping(payload)
    errors: list[str] = []
    if data.get("schema_version") != "manual_observation_batch_0_execution.v0":
        errors.append(f"{source}: schema_version must be manual_observation_batch_0_execution.v0")
    if data.get("batch_id") != "batch_0":
        errors.append(f"{source}: batch_id must be batch_0")
    if data.get("batch_root") != BATCH_ROOT:
        errors.append(f"{source}: batch_root must be {BATCH_ROOT}")
    for ref in sorted(PROTOCOL_REFS):
        if ref not in _string_items(data.get("protocol_refs") or []) and ref not in _string_items(data.get("anti_fabrication_refs") or []) and ref not in _string_items(data.get("failure_taxonomy_refs") or []):
            errors.append(f"{source}: missing protocol/taxonomy ref {ref}")
        if not (repo_root / ref).is_file():
            errors.append(f"{source}: referenced file missing {ref}")
    for action in ALLOWED_MANUAL_ACTIONS:
        if action not in _string_items(data.get("allowed_manual_actions")):
            errors.append(f"{source}: allowed_manual_actions missing {action}")
    for item in FORBIDDEN_AUTOMATION:
        if item not in _string_items(data.get("forbidden_automation")):
            errors.append(f"{source}: forbidden_automation missing {item}")
    for state in COMPLETION_STATES:
        if state not in _string_items(data.get("completion_states")):
            errors.append(f"{source}: completion_states missing {state}")
    required_commands = _string_items(data.get("required_validation_commands"))
    for command in (
        "python scripts/prepare_manual_observation_batch0_execution.py --check",
        "python scripts/validate_manual_observation_batch0_execution.py",
        "python scripts/validate_manual_observation_protocol.py",
    ):
        if command not in required_commands:
            errors.append(f"{source}: required_validation_commands missing {command}")
    errors.extend(_boundary_false_errors(_mapping(data.get("product_boundary")), PRODUCT_BOUNDARY_FIELDS, source))
    return errors


def validate_slot_manifest(payload: Any, source: str, *, expected_manifest: Mapping[str, Any] | None = None) -> list[str]:
    data = _mapping(payload)
    errors: list[str] = []
    if data.get("schema_version") != "manual_observation_batch_0_slot_manifest.v0":
        errors.append(f"{source}: schema_version must be manual_observation_batch_0_slot_manifest.v0")
    if data.get("batch_id") != "batch_0":
        errors.append(f"{source}: batch_id must be batch_0")
    if data.get("source_batch_root") != BATCH_ROOT:
        errors.append(f"{source}: source_batch_root must be {BATCH_ROOT}")
    slots = data.get("slots")
    if not isinstance(slots, list):
        return errors + [f"{source}: slots must be a list"]
    slot_count = data.get("slot_count")
    if slot_count != len(slots):
        errors.append(f"{source}: slot_count must match slots length")
    status_counts = _count_slot_statuses(slots)
    if data.get("status_counts") != status_counts:
        errors.append(f"{source}: status_counts must match slots")
    if status_counts.get("observed", 0):
        for index, slot in enumerate(slots):
            item = _mapping(slot)
            if item.get("slot_status") == "observed":
                if not item.get("observed_file_path_if_any"):
                    errors.append(f"{source}: slots[{index}] observed status requires observed_file_path_if_any")
                if item.get("required_fields_status") != "observed_fields_review_ready":
                    errors.append(f"{source}: slots[{index}] observed status requires reviewed required_fields_status")
    for index, slot in enumerate(slots):
        item = _mapping(slot)
        prefix = f"{source}: slots[{index}]"
        for field in ("slot_id", "query_id", "system_id", "slot_status", "pending_file_path", "required_fields_status", "priority"):
            if field not in item:
                errors.append(f"{prefix} missing {field}")
        if item.get("pending_file_path") != BATCH_PENDING:
            errors.append(f"{prefix}: pending_file_path must be {BATCH_PENDING}")
        if item.get("slot_status") == "pending_manual_observation" and item.get("observed_file_path_if_any") is not None:
            errors.append(f"{prefix}: pending slot must not reference observed_file_path_if_any")
    errors.extend(_boundary_false_errors(_mapping(data.get("product_boundary")), set(PRODUCT_BOUNDARY), source))
    if expected_manifest is not None:
        if data.get("slot_count") != expected_manifest.get("slot_count"):
            errors.append(f"{source}: slot_count does not match discovered Batch 0 state")
        if data.get("status_counts") != expected_manifest.get("status_counts"):
            errors.append(f"{source}: status_counts does not match discovered Batch 0 state")
        if data.get("slots") != expected_manifest.get("slots"):
            errors.append(f"{source}: slots do not match discovered Batch 0 state")
    return errors


def validate_audit_report(payload: Any, source: str) -> list[str]:
    data = _mapping(payload)
    errors: list[str] = []
    if data.get("schema_version") != "obs0_02_report.v0":
        errors.append(f"{source}: schema_version must be obs0_02_report.v0")
    if data.get("task") != "OBS0-02":
        errors.append(f"{source}: task must be OBS0-02")
    if data.get("slot_count") != 39:
        errors.append(f"{source}: slot_count must be 39")
    if data.get("pending_slots") != 39:
        errors.append(f"{source}: pending_slots must be 39")
    if data.get("observed_slots_created_by_this_task") != 0:
        errors.append(f"{source}: observed_slots_created_by_this_task must be 0")
    if data.get("execution_ready") is not True:
        errors.append(f"{source}: execution_ready must be true")
    errors.extend(_boundary_false_errors(_mapping(data.get("product_boundary")), PRODUCT_BOUNDARY_FIELDS, source))
    return errors


def validate_pending_batch(path: Path, repo_root: Path) -> list[str]:
    errors: list[str] = []
    payload = _load_json(path, errors)
    data = _mapping(payload)
    if data.get("observation_status") != "pending_manual_observation":
        errors.append(f"{_rel(path, repo_root)}: batch file must remain pending")
    records = data.get("observations")
    if not isinstance(records, list):
        return errors + [f"{_rel(path, repo_root)}: observations must be a list"]
    for index, record in enumerate(records):
        item = _mapping(record)
        prefix = f"{_rel(path, repo_root)}#{index}"
        if item.get("observation_status") != "pending_manual_observation":
            errors.append(f"{prefix}: pending slot was marked observed")
        if item.get("top_results") != []:
            errors.append(f"{prefix}: pending slot must not contain top_results")
        if item.get("observed_at") is not None:
            errors.append(f"{prefix}: pending slot observed_at must remain null")
    return errors


def validate_no_observed_files(batch_root: Path, repo_root: Path) -> list[str]:
    observations_dir = batch_root / "observations"
    if not observations_dir.is_dir():
        return [f"{_rel(observations_dir, repo_root)}: observations directory missing"]
    errors: list[str] = []
    for path in sorted(observations_dir.glob("*.json")):
        if path.name.startswith("pending_"):
            continue
        errors.append(f"{_rel(path, repo_root)}: observed result files must not be created by OBS0-02")
    return errors


def _count_slot_statuses(slots: Sequence[Any]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for slot in slots:
        status = _mapping(slot).get("slot_status")
        if isinstance(status, str):
            counts[status] = counts.get(status, 0) + 1
    return dict(sorted(counts.items()))


def _boundary_false_errors(boundary: Mapping[str, Any], fields: set[str], source: str) -> list[str]:
    errors: list[str] = []
    for field in sorted(fields):
        if field not in boundary:
            errors.append(f"{source}: product_boundary missing {field}")
        elif boundary[field] is not False:
            errors.append(f"{source}: product_boundary.{field} must be false")
    return errors


def _load_json(path: Path, errors: list[str]) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"{_rel(path, REPO_ROOT)}: missing JSON file")
    except json.JSONDecodeError as exc:
        errors.append(f"{_rel(path, REPO_ROOT)}: invalid JSON at line {exc.lineno}: {exc.msg}")
    return None


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _string_items(value: Any) -> list[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return []
    return [item for item in value if isinstance(item, str)]


def _rel(path: Path, repo_root: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _format_plain(report: Mapping[str, Any]) -> str:
    lines = [
        f"validate_manual_observation_batch0_execution: {report['status']}",
        f"schema_version: {report['schema_version']}",
        f"execution_inventory: {report['execution_inventory']}",
        f"slot_manifest: {report['slot_manifest']}",
    ]
    if report.get("errors"):
        lines.append("errors:")
        lines.extend(f"- {error}" for error in report["errors"])
    if report.get("warnings"):
        lines.append("warnings:")
        lines.extend(f"- {warning}" for warning in report["warnings"])
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
