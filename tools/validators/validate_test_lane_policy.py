#!/usr/bin/env python3
"""Validate TEST-LANE-ROUTER-01 policy, selector, ledger, and tests."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]

REQUIRED_JSON = {
    "control/policies/test_lane_policy.json": "test_lane_policy.v0",
    "control/inventory/test_lane_matrix.json": "test_lane_matrix.v0",
    "control/inventory/test_impact_map.json": "test_impact_map.v0",
    "control/inventory/test_failure_ledger.json": "test_failure_ledger.v0",
    "control/inventory/test_selection_result_schema.json": "test_selection_result_schema.v0",
    "control/inventory/test_lane_router_result.json": "test_lane_router_result.v0",
    "control/inventory/test_lane_router_next_task_decision.json": "test_lane_router_next_task_decision.v0",
    "control/audits/test-lane-router-01-v0/test_lane_router_report.json": "test_lane_router_report.v0",
}

REQUIRED_DOCS = [
    "docs/operations/TEST_LANE_POLICY.md",
    "docs/operations/TEST_SELECTION_RUNBOOK.md",
    "docs/operations/PROMOTION_TEST_POLICY.md",
    "docs/architecture/TEST_AND_VALIDATION_ARCHITECTURE.md",
]

REQUIRED_TESTS = [
    "tests/operations/test_test_lane_policy.py",
    "tests/operations/test_test_impact_map.py",
    "tests/operations/test_test_failure_ledger.py",
    "tests/scripts/test_eureka_test_select.py",
    "tests/scripts/test_validate_test_lane_policy.py",
]

REQUIRED_PATTERNS = {
    "contracts/**",
    "contracts/search/interaction/**",
    "contracts/workbench/**",
    "runtime/source/observation/**",
    "runtime/source/cache/**",
    "runtime/evidence/ledger/**",
    "runtime/index/candidate/**",
    "runtime/review/queue/**",
    "runtime/index/public/**",
    "surfaces/web/workbench/local_html/**",
    "runtime/local/service/**",
    "surfaces/**",
    "scripts/validate_*.py",
    "scripts/eureka_*.py",
    "control/policies/**",
    "control/inventory/**",
    "examples/**",
    "tests/**"
}

REQUIRED_LANES = {
    "L0_static_preflight",
    "L1_focused_unit",
    "L2_impact_integration",
    "L3_full_discovery",
    "L4_promotion_release",
}


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    report = validate_repo(Path(args.repo_root).resolve())
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True), file=stdout)
    else:
        print("Test lane policy validation", file=stdout)
        print(f"status: {report['status']}", file=stdout)
        print(f"error_count: {len(report['errors'])}", file=stdout)
        for error in report["errors"]:
            print(f"ERROR: {error}", file=stdout)
    return 0 if report["status"] == "valid" else 1


def validate_repo(root: Path) -> dict[str, Any]:
    errors: list[str] = []
    payloads = {rel: load_json(root / rel, schema, errors) for rel, schema in REQUIRED_JSON.items()}

    for rel in REQUIRED_DOCS:
        if not (root / rel).is_file():
            errors.append(f"missing doc: {rel}")
    for rel in REQUIRED_TESTS:
        if not (root / rel).is_file():
            errors.append(f"missing test: {rel}")
    for rel in (
        "contracts/testing/README.md",
        "contracts/testing/test_selection_result.v0.json",
        "scripts/eureka_test_select.py",
    ):
        if not (root / rel).is_file():
            errors.append(f"missing file: {rel}")

    policy = payloads.get("control/policies/test_lane_policy.json", {})
    if policy.get("full_discovery_per_commit_required") is not False:
        errors.append("policy must not require full discovery per commit")
    if policy.get("full_discovery_for_promotion_required") is not True:
        errors.append("policy must require full discovery for promotion")
    if policy.get("skip_reasons_required") is not True:
        errors.append("policy must require skip reasons")
    if policy.get("test_requirements_weakened") is not False:
        errors.append("policy must not weaken test requirements")

    lanes = {row.get("lane_id"): row for row in payloads.get("control/inventory/test_lane_matrix.json", {}).get("lanes", [])}
    missing_lanes = REQUIRED_LANES - set(lanes)
    if missing_lanes:
        errors.append(f"lane matrix missing lanes: {sorted(missing_lanes)}")
    if lanes.get("L3_full_discovery", {}).get("required_for_commit") is not False:
        errors.append("L3 full discovery must not be required for every commit")
    if lanes.get("L3_full_discovery", {}).get("required_for_promotion") is not True:
        errors.append("L3 full discovery must be required for promotion")

    impact_patterns = {row.get("path_pattern") for row in payloads.get("control/inventory/test_impact_map.json", {}).get("mappings", [])}
    missing_patterns = REQUIRED_PATTERNS - impact_patterns
    if missing_patterns:
        errors.append(f"impact map missing patterns: {sorted(missing_patterns)}")

    ledger = payloads.get("control/inventory/test_failure_ledger.json", {})
    failures = ledger.get("failures", [])
    for failure in failures:
        for key in (
            "failure_id",
            "test_module",
            "test_name",
            "failure_type",
            "first_seen_commit",
            "last_seen_commit",
            "owning_subsystem",
            "suspected_root_cause",
            "blocking_level",
            "rerun_command",
            "status",
            "linked_repair_task",
        ):
            if key not in failure:
                errors.append(f"failure ledger entry missing {key}")
    active_failures = [
        failure
        for failure in failures
        if failure.get("status") in {"new", "reproduced", "fixed_pending_full"}
    ]

    changed = run_selector(root, "--changed", "--json")
    failed_first = run_selector(root, "--failed-first", "--json")
    promotion = run_selector(root, "--promotion", "--json")
    task = run_selector(root, "--task", "WORKBENCH-RESULT-LANES-01", "--changed", "--json")
    for label, payload in (("changed", changed), ("failed_first", failed_first), ("promotion", promotion), ("task", task)):
        if payload.get("schema_version") != "test_selection_result.v0":
            errors.append(f"{label} selector returned wrong schema")
        if not payload.get("skip_reasons"):
            errors.append(f"{label} selector omitted skip reasons")
    if active_failures and not failed_first.get("failed_first_commands"):
        errors.append("failed-first selector must prioritize known failures")
    if "L3_full_discovery" not in set(promotion.get("selected_lanes", [])):
        errors.append("promotion selector must include L3 full discovery")
    if not any(item.get("command") == "python -m unittest discover -s tests -t ." for item in promotion.get("selected_commands", [])):
        errors.append("promotion selector must include full discovery command")
    if promotion.get("full_discovery_required") is not True:
        errors.append("promotion selector must mark full discovery required")
    active_blockers = [
        failure for failure in failures
        if failure in active_failures
        and failure.get("blocking_level") in {"promotion_blocker", "release_blocker", "commit_blocker"}
    ]
    if active_blockers and promotion.get("promotion_allowed") is not False:
        errors.append("promotion selector must refuse known blocking failures")
    if not task.get("selected_commands"):
        errors.append("task selector must select commands for WORKBENCH-RESULT-LANES-01")

    result = payloads.get("control/inventory/test_lane_router_result.json", {})
    if result.get("runtime_behavior_changed") is not False:
        errors.append("result must record runtime_behavior_changed=false")
    if result.get("tests_deleted") is not False:
        errors.append("result must record tests_deleted=false")
    if result.get("test_requirements_weakened") is not False:
        errors.append("result must record test_requirements_weakened=false")

    return {
        "schema_version": "test_lane_policy_validation.v0",
        "task": "TEST-LANE-ROUTER-01",
        "status": "valid" if not errors else "invalid",
        "errors": errors,
        "selector_changed_mode_passed": not errors_in_selector(changed),
        "selector_failed_first_mode_passed": not active_failures or bool(failed_first.get("failed_first_commands")),
        "selector_promotion_mode_passed": "L3_full_discovery" in set(promotion.get("selected_lanes", [])),
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }


def run_selector(root: Path, *args: str) -> dict[str, Any]:
    completed = subprocess.run(
        [sys.executable, str(root / "scripts/eureka_test_select.py"), *args],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        return {"schema_version": "selector_error", "error": completed.stderr + completed.stdout}
    return json.loads(completed.stdout)


def errors_in_selector(payload: Mapping[str, Any]) -> bool:
    return payload.get("schema_version") != "test_selection_result.v0"


def load_json(path: Path, schema_version: str, errors: list[str]) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"missing json: {rel(path)}")
        return {}
    except json.JSONDecodeError as exc:
        errors.append(f"invalid json: {rel(path)}: {exc}")
        return {}
    if payload.get("schema_version") != schema_version:
        errors.append(f"{rel(path)} schema_version must be {schema_version}")
    return payload


def rel(path: Path) -> str:
    try:
        return path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


if __name__ == "__main__":
    raise SystemExit(main())
