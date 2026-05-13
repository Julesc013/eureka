#!/usr/bin/env python3
"""Validate generated artifact drift remediation evidence."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
TASK_ID = "R0-REMEDIATION-GENERATED-ARTIFACT-DRIFT-01"

REQUIRED_JSON = {
    "control/policies/generated_artifact_policy.json": "generated_artifact_policy.v0",
    "control/policies/site_dist_test_isolation_policy.json": "site_dist_test_isolation_policy.v0",
    "control/inventory/generated_artifact_drift_report.json": "generated_artifact_drift_report.v0",
    "control/inventory/generated_artifact_drift_repair_result.json": "generated_artifact_drift_repair_result.v0",
    "control/inventory/generated_artifact_canonical_state.json": "generated_artifact_canonical_state.v0",
    "control/inventory/generated_artifact_test_isolation_report.json": "generated_artifact_test_isolation_report.v0",
    "control/inventory/r0_generated_artifact_remediation_result.json": "r0_generated_artifact_remediation_result.v0",
    "control/inventory/r0_generated_artifact_next_task_decision.json": "r0_generated_artifact_next_task_decision.v0",
    "control/audits/r0-remediation-generated-artifact-drift-01-v0/remediation_report.json": "r0_generated_artifact_drift_remediation_report.v0",
}
REQUIRED_FILES = (
    "docs/operations/GENERATED_ARTIFACT_POLICY.md",
    "docs/operations/SITE_DIST_TEST_ISOLATION.md",
    "docs/operations/R0_GENERATED_ARTIFACT_DRIFT_REMEDIATION.md",
    "control/audits/r0-remediation-generated-artifact-drift-01-v0/README.md",
    "control/audits/r0-remediation-generated-artifact-drift-01-v0/drift_diagnosis.md",
    "control/audits/r0-remediation-generated-artifact-drift-01-v0/repair_result.md",
    "control/audits/r0-remediation-generated-artifact-drift-01-v0/canonical_artifact_state.md",
    "control/audits/r0-remediation-generated-artifact-drift-01-v0/test_isolation_report.md",
    "control/audits/r0-remediation-generated-artifact-drift-01-v0/full_unittest_result.md",
    "control/audits/r0-remediation-generated-artifact-drift-01-v0/r0_closeout_update.md",
    "control/audits/r0-remediation-generated-artifact-drift-01-v0/f0_resumption_decision.md",
    "control/audits/r0-remediation-generated-artifact-drift-01-v0/validation.md",
    "control/audits/r0-remediation-generated-artifact-drift-01-v0/generated/sample_generated_artifact_drift_report.json",
    "control/audits/r0-remediation-generated-artifact-drift-01-v0/generated/sample_repair_result.json",
    "control/audits/r0-remediation-generated-artifact-drift-01-v0/generated/sample_final_cleanliness_report.json",
    "control/audits/r0-remediation-generated-artifact-drift-01-v0/generated/sample_summary.md",
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    result = validate(Path(args.repo_root).resolve())
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    else:
        print("Generated artifact drift remediation validation", file=stdout)
        print(f"status: {result['status']}", file=stdout)
        for error in result["errors"]:
            print(f"ERROR: {error}", file=stdout)
        for warning in result["warnings"]:
            print(f"WARN: {warning}", file=stdout)
    return 0 if result["status"] == "pass" else 1


def validate(root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    payloads = validate_json_files(root, errors)
    validate_required_files(root, errors)
    validate_policy(payloads, errors)
    validate_remediation_result(payloads, errors)
    validate_closeout_update(root, errors)
    command_results = [run_cleanliness(root, errors)]
    return {
        "schema_version": "generated_artifact_drift_validation.v0",
        "task": TASK_ID,
        "status": "pass" if not errors else "fail",
        "errors": errors,
        "warnings": warnings,
        "command_results": command_results,
        "site_dist_mutated": False,
        "master_index_mutated": False,
        "network_used": False,
        "model_provider_used": False,
    }


def validate_json_files(root: Path, errors: list[str]) -> dict[str, Any]:
    payloads: dict[str, Any] = {}
    for rel, schema in REQUIRED_JSON.items():
        path = root / rel
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            errors.append(f"missing JSON file: {rel}")
            continue
        except json.JSONDecodeError as exc:
            errors.append(f"invalid JSON file {rel}: {exc}")
            continue
        payloads[rel] = payload
        if payload.get("schema_version") != schema:
            errors.append(f"unexpected schema_version for {rel}")
    return payloads


def validate_required_files(root: Path, errors: list[str]) -> None:
    for rel in REQUIRED_FILES:
        if not (root / rel).exists():
            errors.append(f"missing required file: {rel}")


def validate_policy(payloads: Mapping[str, Any], errors: list[str]) -> None:
    policy = payloads.get("control/policies/generated_artifact_policy.json", {})
    classes = {item.get("artifact_class") for item in policy.get("classifiers", []) if isinstance(item, dict)}
    required = {
        "canonical_generated",
        "deployment_generated",
        "audit_generated",
        "fixture_generated",
        "temp_test_generated",
        "historical_evidence",
        "source_input",
        "unknown",
    }
    missing = required - classes
    if missing:
        errors.append(f"generated artifact policy missing classes: {sorted(missing)}")
    isolation = payloads.get("control/policies/site_dist_test_isolation_policy.json", {})
    if isolation.get("ordinary_tests_must_use_tempdir") is not True:
        errors.append("site/dist isolation policy must require tempdir for ordinary tests")


def validate_remediation_result(payloads: Mapping[str, Any], errors: list[str]) -> None:
    result = payloads.get("control/inventory/r0_generated_artifact_remediation_result.json", {})
    repair = payloads.get("control/inventory/generated_artifact_drift_repair_result.json", {})
    if result.get("generated_artifact_drift_resolved") is not True:
        errors.append("generated artifact drift is not marked resolved")
    if result.get("full_unittest_discovery_pass") is not True:
        errors.append("full unittest discovery is not marked pass")
    if result.get("architecture_boundary_checks_pass") is not True:
        errors.append("architecture boundary checks are not marked pass")
    if result.get("production_readiness_claimed") is not False or result.get("public_launch_readiness_claimed") is not False:
        errors.append("remediation must not claim production or public launch readiness")
    if repair.get("remaining_drift_paths"):
        errors.append("repair result still has remaining drift paths")


def validate_closeout_update(root: Path, errors: list[str]) -> None:
    closeout = read_json(root / "control/inventory/r0_final_closeout_result.json") or {}
    blockers = (read_json(root / "control/inventory/r0_final_blocker_register.json") or {}).get("blockers", [])
    if closeout.get("full_unittest_discovery_pass") is not True:
        errors.append("R0 final closeout does not record full unittest pass")
    if any(item.get("area") == "generated_artifact_drift" and item.get("fixed_in_r0_11") is not True for item in blockers):
        errors.append("R0 final blocker register still has unresolved generated artifact drift blocker")


def run_cleanliness(root: Path, errors: list[str]) -> dict[str, Any]:
    completed = subprocess.run(
        [sys.executable, "scripts/check_generated_artifact_cleanliness.py", "--check", "--json"],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        errors.append("generated artifact cleanliness check failed")
    return {
        "command": "python scripts/check_generated_artifact_cleanliness.py --check --json",
        "status": "pass" if completed.returncode == 0 else "fail",
    }


def read_json(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


if __name__ == "__main__":
    raise SystemExit(main())
