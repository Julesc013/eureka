#!/usr/bin/env python3
"""Validate the R0 legacy runtime leakage remediation evidence."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]
TASK = "R0-REMEDIATION-LEGACY-LEAKAGE-01"
AUDIT_SCRIPT = Path("scripts/audit_runtime_architecture_leakage.py")
RESULT = Path("control/inventory/legacy_runtime_leakage_remediation_result.json")
INVENTORY = Path("control/inventory/legacy_runtime_leakage_inventory.json")
PLAN = Path("control/inventory/legacy_runtime_leakage_remediation_plan.json")
REMAINING = Path("control/inventory/legacy_runtime_leakage_remaining_allowlist.json")
DECISION = Path("control/inventory/r0_legacy_leakage_next_task_decision.json")
REPORT = Path("control/audits/r0-remediation-legacy-leakage-01-v0/remediation_report.json")
AUDIT_DIR = Path("control/audits/r0-remediation-legacy-leakage-01-v0")
R0_SEAMS = (
    "runtime/source_observation/",
    "runtime/source_cache/",
    "runtime/evidence_ledger/",
    "runtime/review_queue/",
    "runtime/public_index/",
)
REQUIRED_JSON = {
    INVENTORY: "legacy_runtime_leakage_inventory.v0",
    PLAN: "legacy_runtime_leakage_remediation_plan.v0",
    RESULT: "legacy_runtime_leakage_remediation_result.v0",
    REMAINING: "legacy_runtime_leakage_remaining_allowlist.v0",
    DECISION: "r0_legacy_leakage_next_task_decision.v0",
    REPORT: "r0_legacy_leakage_remediation_report.v0",
}
REQUIRED_MARKDOWN = (
    "docs/operations/R0_LEGACY_RUNTIME_LEAKAGE_REMEDIATION.md",
    f"{AUDIT_DIR.as_posix()}/README.md",
    f"{AUDIT_DIR.as_posix()}/leakage_inventory.md",
    f"{AUDIT_DIR.as_posix()}/remediation_plan.md",
    f"{AUDIT_DIR.as_posix()}/remediation_result.md",
    f"{AUDIT_DIR.as_posix()}/remaining_allowlist.md",
    f"{AUDIT_DIR.as_posix()}/validation.md",
    f"{AUDIT_DIR.as_posix()}/generated/sample_summary.md",
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    result = validate_repo(Path(args.repo_root).resolve())
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    else:
        print("R0 legacy runtime leakage remediation validation", file=stdout)
        print(f"status: {result['status']}", file=stdout)
        print(f"error_count: {len(result['errors'])}", file=stdout)
        for error in result["errors"]:
            print(f"ERROR: {error}", file=stdout)
    return 0 if result["status"] == "valid" else 1


def validate_repo(root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    payloads = {path.as_posix(): load_json(root / path, schema, errors) for path, schema in REQUIRED_JSON.items()}
    validate_markdown(root, errors)
    validate_result(payloads.get(RESULT.as_posix(), {}), errors)
    validate_plan(payloads.get(PLAN.as_posix(), {}), errors)
    validate_remaining_allowlist(payloads.get(REMAINING.as_posix(), {}), errors)
    validate_decision(payloads.get(DECISION.as_posix(), {}), errors)
    validate_report(payloads.get(REPORT.as_posix(), {}), payloads.get(RESULT.as_posix(), {}), errors)
    validate_fresh_audit(root, payloads.get(RESULT.as_posix(), {}), errors)
    validate_quarantine(root, payloads.get(PLAN.as_posix(), {}), errors)
    validate_no_generated_drift_result(root, errors)
    return {
        "schema_version": "legacy_runtime_leakage_remediation_validation.v0",
        "task": TASK,
        "status": "valid" if not errors else "invalid",
        "network_calls_made": False,
        "model_provider_calls_made": False,
        "errors": errors,
    }


def load_json(path: Path, schema: str, errors: list[str]) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"missing JSON output: {path.as_posix()}")
        return {}
    except json.JSONDecodeError as exc:
        errors.append(f"malformed JSON output {path.as_posix()}: {exc}")
        return {}
    if payload.get("schema_version") != schema:
        errors.append(f"{path.as_posix()} schema_version must be {schema}")
    return payload


def validate_markdown(root: Path, errors: list[str]) -> None:
    for rel in REQUIRED_MARKDOWN:
        path = root / rel
        if not path.is_file():
            errors.append(f"missing markdown output: {rel}")
        elif path.stat().st_size == 0:
            errors.append(f"empty markdown output: {rel}")


def validate_result(result: Mapping[str, Any], errors: list[str]) -> None:
    if result.get("status") not in {"pass", "pass_with_warnings"}:
        errors.append("remediation result must be pass or pass_with_warnings")
    if result.get("leak_count_after", 0) >= result.get("leak_count_before", 0):
        errors.append("legacy leakage count did not decrease")
    if result.get("allowlist_count_after", 0) >= result.get("allowlist_count_before", 0):
        errors.append("allowlist count did not decrease")
    if result.get("new_unallowlisted_leaks") != 0:
        errors.append("new unallowlisted production leaks must be zero")
    if result.get("clean_r0_seams_still_clean") is not True:
        errors.append("clean R0 seams must remain clean")
    if result.get("generated_artifact_cleanliness_pass") is not True:
        errors.append("generated artifact cleanliness pass flag must be true")
    if result.get("full_unittest_discovery_pass") is not True:
        errors.append("full unittest discovery pass flag must be true")
    if result.get("production_readiness_claimed") is not False:
        errors.append("production readiness must not be claimed")
    if result.get("public_launch_readiness_claimed") is not False:
        errors.append("public launch readiness must not be claimed")
    if result.get("f0_decision") not in {"resume_f0", "remain_blocked", "remediation_required"}:
        errors.append("F0 decision must be explicit")
    if result.get("dev_to_main_decision") not in {"promote_ready", "promotion_plan_only", "remain_blocked", "already_on_main"}:
        errors.append("dev-to-main decision must be explicit")


def validate_plan(plan: Mapping[str, Any], errors: list[str]) -> None:
    if plan.get("strategy") != "quarantine_task_shaped_connector_runtime":
        errors.append("remediation plan must quarantine task-shaped connector runtime")
    names = plan.get("legacy_connector_names")
    if not isinstance(names, list) or not names:
        errors.append("remediation plan must record legacy connector names")


def validate_remaining_allowlist(payload: Mapping[str, Any], errors: list[str]) -> None:
    entries = payload.get("entries")
    if not isinstance(entries, list):
        errors.append("remaining allowlist entries must be a list")
        return
    for index, entry in enumerate(entries):
        if not isinstance(entry, Mapping):
            errors.append(f"remaining allowlist entry {index} must be an object")
            continue
        for key in ("path", "term", "reason", "replacement", "owner", "expires_after_task", "severity_after_expiry"):
            if not entry.get(key):
                errors.append(f"remaining allowlist entry {index} missing {key}")
        if str(entry.get("expires_after_task")).lower() == "never":
            errors.append(f"remaining allowlist entry {index} has permanent expiry")
        if str(entry.get("path", "")).startswith("runtime/connectors/h"):
            errors.append(f"remaining allowlist entry {index} still points at quarantined runtime connector path")


def validate_decision(payload: Mapping[str, Any], errors: list[str]) -> None:
    if not isinstance(payload.get("f0_can_resume"), bool):
        errors.append("next task decision must make F0 resume state explicit")
    if payload.get("production_readiness_claimed") is not False:
        errors.append("next task decision must not claim production readiness")
    if payload.get("public_launch_readiness_claimed") is not False:
        errors.append("next task decision must not claim public launch readiness")


def validate_report(report: Mapping[str, Any], result: Mapping[str, Any], errors: list[str]) -> None:
    for key in (
        "leak_count_before",
        "leak_count_after",
        "allowlist_count_before",
        "allowlist_count_after",
        "remaining_allowlist_count",
        "new_unallowlisted_leaks",
        "f0_decision",
        "dev_to_main_decision",
    ):
        if report.get(key) != result.get(key):
            errors.append(f"remediation report {key} must match remediation result")


def validate_fresh_audit(root: Path, result: Mapping[str, Any], errors: list[str]) -> None:
    audit = load_audit_module(root).build_leakage_audit(root)
    summary = audit.get("summary", {})
    if summary.get("new_violation_count") != 0:
        errors.append("fresh leakage audit reports new unallowlisted leaks")
    if summary.get("known_allowlisted_violation_count") != result.get("leak_count_after"):
        errors.append("fresh leakage audit count does not match remediation result")
    for finding in audit.get("findings", []):
        path = str(finding.get("path", ""))
        if path.startswith(R0_SEAMS):
            errors.append(f"R0 seam leakage found: {path}")


def validate_quarantine(root: Path, plan: Mapping[str, Any], errors: list[str]) -> None:
    names = [str(item) for item in plan.get("legacy_connector_names", [])]
    for name in names:
        if (root / "runtime/connectors" / name).exists():
            errors.append(f"legacy connector still under runtime: {name}")
        if not (root / "archive/prototypes/legacy_runtime/connectors" / name).is_dir():
            errors.append(f"legacy connector missing from quarantine: {name}")


def validate_no_generated_drift_result(root: Path, errors: list[str]) -> None:
    path = root / "control/inventory/r0_generated_artifact_remediation_result.json"
    if not path.is_file():
        return
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"generated artifact remediation result is malformed: {exc}")
        return
    if payload.get("generated_artifact_drift_resolved") is not True:
        errors.append("generated artifact drift must remain resolved")


def load_audit_module(root: Path):
    spec = importlib.util.spec_from_file_location("audit_runtime_architecture_leakage", root / AUDIT_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load runtime architecture leakage audit script")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


if __name__ == "__main__":
    raise SystemExit(main())
