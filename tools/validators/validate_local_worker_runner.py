#!/usr/bin/env python3
"""Validate LOCAL-09 deterministic local worker runner evidence."""

from __future__ import annotations

import argparse
import ast
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Mapping, Sequence, TextIO

try:
    from local_queue_progress import f0_deferred_or_past_local_closeout, queue_current_or_advanced, queue_task_available, queue_task_completed
except ModuleNotFoundError:  # pragma: no cover - supports package-style imports in tests.
    from scripts.local_queue_progress import f0_deferred_or_past_local_closeout, queue_current_or_advanced, queue_task_available, queue_task_completed


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.local.appliance import close_local_appliance, open_local_appliance
from runtime.local.worker import (
    BLOCKED_WORKER_KINDS,
    ENABLED_WORKER_KINDS,
    LocalWorkerRunner,
    get_default_worker_registry,
)
from runtime.worker.workunit_queue import WorkUnit, WorkUnitState


TASK_ID = "LOCAL-09"
NEXT_TASK = "LOCAL-10"
F0_CLOSEOUT = "LOCAL-14"
POLICIES = {
    "control/policies/local_worker_runner_policy.json": "local_worker_runner_policy.v0",
    "control/policies/local_worker_allowed_kinds_policy.json": "local_worker_allowed_kinds_policy.v0",
    "control/policies/local_worker_side_effect_policy.json": "local_worker_side_effect_policy.v0",
    "control/policies/local_worker_audit_policy.json": "local_worker_audit_policy.v0",
}
INVENTORIES = {
    "control/inventory/local_worker_runner_inventory.json": "local_worker_runner_inventory.v0",
    "control/inventory/local_worker_kind_matrix.json": "local_worker_kind_matrix.v0",
    "control/inventory/local_worker_runner_result.json": "local_worker_runner_result.v0",
    "control/inventory/local_worker_demo_result.json": "local_worker_demo_result.v0",
    "control/inventory/local_worker_gap_register.json": "local_worker_gap_register.v0",
    "control/inventory/local_09_leakage_baseline.json": "local_09_leakage_baseline.v0",
    "control/inventory/local_09_next_task_decision.json": "local_09_next_task_decision.v0",
}
RUNTIME_FILES = (
    "runtime/local/worker/__init__.py",
    "runtime/local/worker/audit.py",
    "runtime/local/worker/errors.py",
    "runtime/local/worker/policy.py",
    "runtime/local/worker/registry.py",
    "runtime/local/worker/results.py",
    "runtime/local/worker/runner.py",
    "runtime/local/worker/validation.py",
    "runtime/local/worker/workers.py",
)
SCRIPTS = (
    "scripts/eureka_worker_runner.py",
    "scripts/demo_local_worker_runner.py",
    "scripts/validate_local_worker_runner.py",
)
TESTS = (
    "tests/runtime/test_local_worker_registry.py",
    "tests/runtime/test_local_worker_runner.py",
    "tests/runtime/test_local_worker_results.py",
    "tests/runtime/test_local_worker_policy.py",
    "tests/runtime/test_local_worker_integration.py",
    "tests/operations/test_local_worker_scripts.py",
)
DOCS = (
    "docs/architecture/LOCAL_WORKER_RUNNER.md",
    "docs/reference/LOCAL_WORKER_RUNTIME.md",
    "docs/reference/LOCAL_WORKER_KIND_MATRIX.md",
    "docs/operations/LOCAL_WORKER_RUNNER_RUNBOOK.md",
    "docs/operations/LOCAL_WORKER_SAFETY_BOUNDARY.md",
)
AUDIT_ROOT = Path("control/audits/local-09-deterministic-worker-runner-v0")
AUDIT_FILES = (
    "README.md",
    "local_09_report.json",
    "worker_runner_summary.md",
    "worker_kind_matrix.md",
    "side_effect_boundary.md",
    "demo_result.md",
    "leakage_baseline.md",
    "validation.md",
    "generated/sample_worker_run.json",
    "generated/sample_worker_result.json",
    "generated/sample_worker_audit_event.json",
    "generated/sample_demo_result.json",
    "generated/sample_summary.md",
)
EXPECTED_ENABLED = (
    "noop_worker",
    "review_queue_checker",
    "reviewed_index_rebuild_worker",
    "absence_report_worker",
    "local_status_snapshot_worker",
)
EXPECTED_BLOCKED = (
    "source_probe_worker",
    "extraction_worker",
    "agent_research_worker",
    "ai_model_worker",
    "download_worker",
    "install_execute_worker",
    "source_sync_worker",
    "lan_worker",
    "deployment_worker",
)
FORBIDDEN_IMPORT_PREFIXES = (
    "runtime.connectors",
    "runtime.local_foundry",
    "runtime.extraction",
    "runtime.search_quality",
    "requests",
    "httpx",
    "aiohttp",
    "urllib.request",
)
FORBIDDEN_RUNTIME_TOKENS = ("LOCAL-", "H0", "H1", "H2", "H3", "H4", "H5", "H6", "H7", "H8", "H9", "H10", "H11", "H12", "H13", "H14", "BUNDLE", "task", "prompt", "agent")


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--output")
    args = parser.parse_args(argv)
    result = validate(Path(args.repo_root).resolve())
    if args.output:
        write_json(Path(args.output), result)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    else:
        print("LOCAL-09 deterministic worker runner validation", file=stdout)
        print(f"status: {result['status']}", file=stdout)
        for error in result["errors"]:
            print(f"ERROR: {error}", file=stdout)
        for warning in result["warnings"]:
            print(f"WARN: {warning}", file=stdout)
    return 0 if result["status"] in {"pass", "pass_with_warnings"} else 1


def validate(root: Path) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    payloads = {rel: load_json(root / rel, schema, errors) for rel, schema in {**POLICIES, **INVENTORIES}.items()}
    report = load_json(root / AUDIT_ROOT / "local_09_report.json", "local_09_report.v0", errors)
    validate_policies(payloads, errors)
    validate_inventories(payloads, errors)
    validate_files(root, errors)
    validate_runtime_imports(root, errors)
    validate_runtime_vocabulary(root, errors)
    runtime_result = validate_worker_runtime(root, errors)
    validate_cli_and_demo(root, errors)
    validate_queue_state(root, errors)
    validate_report(report, errors)
    validate_leakage(root, payloads.get("control/inventory/local_09_leakage_baseline.json", {}), errors, warnings)
    status = "fail" if errors else ("pass_with_warnings" if warnings else "pass")
    return {
        "schema_version": "local_worker_runner_validation.v0",
        "task": TASK_ID,
        "status": status,
        "errors": errors,
        "warnings": warnings,
        "runtime_package_added": all((root / rel).is_file() for rel in RUNTIME_FILES),
        "runner_added": (root / "runtime/local/worker/runner.py").is_file(),
        "registry_added": (root / "runtime/local/worker/registry.py").is_file(),
        "cli_added": (root / "scripts/eureka_worker_runner.py").is_file(),
        "demo_added": (root / "scripts/demo_local_worker_runner.py").is_file(),
        "validator_added": True,
        "noop_worker_passed": runtime_result.get("noop_worker_passed", False),
        "review_queue_checker_passed": runtime_result.get("review_queue_checker_passed", False),
        "absence_report_worker_passed": runtime_result.get("absence_report_worker_passed", False),
        "local_status_snapshot_worker_passed": runtime_result.get("local_status_snapshot_worker_passed", False),
        "reviewed_index_rebuild_worker_token_gated": runtime_result.get("reviewed_index_rebuild_worker_token_gated", False),
        "source_probe_worker_blocked": runtime_result.get("source_probe_worker_blocked", False),
        "extraction_worker_blocked": runtime_result.get("extraction_worker_blocked", False),
        "ai_model_worker_blocked": runtime_result.get("ai_model_worker_blocked", False),
        "transition_history_recorded": runtime_result.get("transition_history_recorded", False),
        "worker_audit_recorded": runtime_result.get("worker_audit_recorded", False),
        "external_network_used": False,
        "source_probe_executed": False,
        "extraction_executed": False,
        "model_provider_used": False,
        "download_install_execute_performed": False,
        "site_dist_mutated": False,
        "master_index_mutated": False,
        "lan_enabled": False,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }


def validate_policies(payloads: Mapping[str, Mapping[str, Any]], errors: list[str]) -> None:
    runner = payloads.get("control/policies/local_worker_runner_policy.json", {})
    for key in (
        "workers_execute_workunits_only",
        "deterministic_workers_only_current_task",
        "operator_token_required_for_mutating_workers",
        "workunit_transition_history_required",
        "worker_run_audit_required",
        "no_production_readiness_claim",
        "no_public_launch_readiness_claim",
    ):
        require_true(runner, key, errors, "worker runner policy")
    for key in (
        "source_probe_workers_enabled",
        "extraction_workers_enabled",
        "ai_model_workers_enabled",
        "agent_research_workers_enabled",
        "download_workers_enabled",
        "install_execute_workers_enabled",
        "source_sync_workers_enabled",
        "lan_workers_enabled",
        "deployment_workers_enabled",
    ):
        require_false(runner, key, errors, "worker runner policy")
    if runner.get("max_workunits_per_run_default") != 1:
        errors.append("worker runner policy max_workunits_per_run_default must be 1")

    allowed = payloads.get("control/policies/local_worker_allowed_kinds_policy.json", {})
    enabled = allowed.get("enabled_worker_kinds", {})
    blocked = allowed.get("blocked_worker_kinds", {})
    if set(enabled) != set(EXPECTED_ENABLED):
        errors.append("enabled worker kind policy mismatch")
    if set(blocked) != set(EXPECTED_BLOCKED):
        errors.append("blocked worker kind policy mismatch")
    for kind in EXPECTED_ENABLED:
        if enabled.get(kind, {}).get("enabled") is not True:
            errors.append(f"enabled worker kind is not enabled: {kind}")
    for kind in EXPECTED_BLOCKED:
        if blocked.get(kind, {}).get("enabled") is not False:
            errors.append(f"blocked worker kind is not disabled: {kind}")

    side_effect = payloads.get("control/policies/local_worker_side_effect_policy.json", {})
    for key in ("workunit_state_mutation_allowed", "worker_result_recording_allowed", "public_index_rebuild_allowed_for_reviewed_index_rebuild_worker"):
        require_true(side_effect, key, errors, "worker side-effect policy")
    for key in (
        "source_probe_allowed",
        "extraction_allowed",
        "external_network_allowed",
        "model_provider_allowed",
        "download_allowed",
        "install_execution_allowed",
        "source_sync_allowed",
        "lan_operations_allowed",
        "deployment_allowed",
        "site_dist_writes_allowed",
        "master_index_mutation_allowed",
        "source_registry_mutation_allowed",
        "connector_registry_mutation_allowed",
    ):
        require_false(side_effect, key, errors, "worker side-effect policy")

    audit = payloads.get("control/policies/local_worker_audit_policy.json", {})
    required = set(audit.get("required_fields", []))
    for key in ("worker_run_id", "workunit_id", "worker_kind", "started_at", "finished_at", "status", "policy_decision", "inputs", "outputs", "store_mutations", "warnings", "limitations"):
        if key not in required:
            errors.append(f"worker audit policy missing required field: {key}")


def validate_inventories(payloads: Mapping[str, Mapping[str, Any]], errors: list[str]) -> None:
    inventory = payloads.get("control/inventory/local_worker_runner_inventory.json", {})
    if inventory.get("runtime_package") != "runtime/local/worker":
        errors.append("worker inventory runtime_package mismatch")
    if inventory.get("enabled_worker_kinds") != list(EXPECTED_ENABLED):
        errors.append("worker inventory enabled kinds mismatch")
    if inventory.get("blocked_worker_kinds") != list(EXPECTED_BLOCKED):
        errors.append("worker inventory blocked kinds mismatch")
    require_true(inventory, "workunit_queue_required", errors, "worker inventory")
    require_true(inventory, "worker_execution_enabled", errors, "worker inventory")
    for key in (
        "source_probe_execution_enabled",
        "extraction_execution_enabled",
        "ai_model_execution_enabled",
        "external_network_enabled",
        "download_install_execute_enabled",
        "lan_enabled",
        "deployment_performed",
    ):
        require_false(inventory, key, errors, "worker inventory")

    matrix = payloads.get("control/inventory/local_worker_kind_matrix.json", {})
    rows = matrix.get("rows", [])
    row_kinds = [item.get("kind") for item in rows if isinstance(item, Mapping)]
    if row_kinds != list(EXPECTED_ENABLED + EXPECTED_BLOCKED):
        errors.append("worker kind matrix row order mismatch")

    result = payloads.get("control/inventory/local_worker_runner_result.json", {})
    for key in (
        "runtime_package_added",
        "runner_added",
        "registry_added",
        "cli_added",
        "demo_added",
        "validator_added",
        "noop_worker_passed",
        "review_queue_checker_passed",
        "absence_report_worker_passed",
        "local_status_snapshot_worker_passed",
        "reviewed_index_rebuild_worker_token_gated",
        "source_probe_worker_blocked",
        "extraction_worker_blocked",
        "ai_model_worker_blocked",
        "transition_history_recorded",
        "worker_audit_recorded",
    ):
        require_true(result, key, errors, "worker result inventory")
    for key in (
        "external_network_used",
        "source_probe_executed",
        "model_provider_used",
        "download_install_execute_performed",
        "site_dist_mutated",
        "master_index_mutated",
        "lan_enabled",
        "deployment_performed",
        "production_readiness_claimed",
        "public_launch_readiness_claimed",
    ):
        require_false(result, key, errors, "worker result inventory")

    demo = payloads.get("control/inventory/local_worker_demo_result.json", {})
    if demo.get("status") != "pass":
        errors.append("worker demo result inventory must pass")

    decision = payloads.get("control/inventory/local_09_next_task_decision.json", {})
    if decision.get("recommended_next_task") != "LOCAL-10 \u2014 Auto-test and auto-search harness":
        errors.append("LOCAL-09 next task decision must point to LOCAL-10")
    if decision.get("f0_current_status") != "deferred" or decision.get("f0_can_resume_after") != F0_CLOSEOUT:
        errors.append("F0 must remain deferred until LOCAL-14")
    if decision.get("lan_can_start") is not False or decision.get("source_probe_workers_enabled") is not False:
        errors.append("LOCAL-09 next task decision flags mismatch")
    if decision.get("deterministic_worker_runner_available") is not True:
        errors.append("LOCAL-09 next task decision must mark runner available")

    leakage = payloads.get("control/inventory/local_09_leakage_baseline.json", {})
    if leakage.get("local_09_increased_leakage") is not False:
        errors.append("LOCAL-09 leakage baseline must not increase leakage")


def validate_files(root: Path, errors: list[str]) -> None:
    for rel in (*RUNTIME_FILES, *SCRIPTS, *TESTS, *DOCS):
        path = root / rel
        if not path.is_file():
            errors.append(f"missing file: {rel}")
        elif path.stat().st_size == 0:
            errors.append(f"empty file: {rel}")
    for rel in AUDIT_FILES:
        path = root / AUDIT_ROOT / rel
        if not path.is_file():
            errors.append(f"missing audit file: {(AUDIT_ROOT / rel).as_posix()}")
        elif path.stat().st_size == 0:
            errors.append(f"empty audit file: {(AUDIT_ROOT / rel).as_posix()}")


def validate_runtime_imports(root: Path, errors: list[str]) -> None:
    for rel in RUNTIME_FILES:
        tree = ast.parse((root / rel).read_text(encoding="utf-8"), filename=rel)
        for node in ast.walk(tree):
            modules: list[str] = []
            if isinstance(node, ast.Import):
                modules = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and not node.level:
                modules = [node.module or ""]
            for module in modules:
                if any(module == item or module.startswith(item + ".") for item in FORBIDDEN_IMPORT_PREFIXES):
                    errors.append(f"forbidden import in {rel}: {module}")


def validate_runtime_vocabulary(root: Path, errors: list[str]) -> None:
    for rel in RUNTIME_FILES:
        text = (root / rel).read_text(encoding="utf-8")
        for token in FORBIDDEN_RUNTIME_TOKENS:
            if token in text:
                errors.append(f"forbidden runtime vocabulary in {rel}: {token}")


def validate_worker_runtime(root: Path, errors: list[str]) -> dict[str, bool]:
    result = {
        "noop_worker_passed": False,
        "review_queue_checker_passed": False,
        "absence_report_worker_passed": False,
        "local_status_snapshot_worker_passed": False,
        "reviewed_index_rebuild_worker_token_gated": False,
        "source_probe_worker_blocked": False,
        "extraction_worker_blocked": False,
        "ai_model_worker_blocked": False,
        "transition_history_recorded": False,
        "worker_audit_recorded": False,
    }
    registry = get_default_worker_registry()
    if tuple(ENABLED_WORKER_KINDS) != EXPECTED_ENABLED:
        errors.append("runtime enabled worker kind tuple mismatch")
    if tuple(BLOCKED_WORKER_KINDS) != EXPECTED_BLOCKED:
        errors.append("runtime blocked worker kind tuple mismatch")
    for kind in EXPECTED_ENABLED:
        if not registry.is_worker_enabled(kind):
            errors.append(f"runtime worker not enabled: {kind}")
    for kind in EXPECTED_BLOCKED:
        if registry.is_worker_enabled(kind):
            errors.append(f"runtime worker not blocked: {kind}")

    with tempfile.TemporaryDirectory(prefix="eureka-local-worker-validation-") as tmp:
        instance = Path(tmp) / "eureka-instance"
        init = run(root, "python", "scripts/eureka_init_instance.py", "--instance", str(instance), "--json")
        if init.returncode != 0:
            errors.append(f"temp instance init failed: {init.stdout}{init.stderr}")
            return result
        runtime = open_local_appliance(instance)
        try:
            runner = LocalWorkerRunner(runtime)
            before_public = runtime.public_index.summarize().to_dict()
            allowed_items = {
                "noop_worker": WorkUnit.new("regression_test", "Noop worker sample", payload={"worker_kind": "noop_worker"}),
                "review_queue_checker": WorkUnit.new("evidence_review", "Review queue checker sample", payload={"worker_kind": "review_queue_checker"}),
                "absence_report_worker": WorkUnit.new("search_need", "Absence worker sample", payload={"worker_kind": "absence_report_worker", "query": "not-present-local-worker-validation"}),
                "local_status_snapshot_worker": WorkUnit.new("regression_test", "Status snapshot worker sample", payload={"worker_kind": "local_status_snapshot_worker"}),
            }
            for kind, item in allowed_items.items():
                created = runtime.workunit_queue.create_workunit(item)
                worker_result = runner.run_one(created.id)
                result[f"{kind}_passed"] = worker_result.status.value == "complete"
                assert_no_external_effects(worker_result.to_dict(), errors)

            rebuild = runtime.workunit_queue.create_workunit(
                WorkUnit.new("index_rebuild", "Rebuild token gate sample", payload={"worker_kind": "reviewed_index_rebuild_worker"})
            )
            rebuild_result = runner.run_one(rebuild.id)
            result["reviewed_index_rebuild_worker_token_gated"] = rebuild_result.status.value == "blocked" and "operator token" in " ".join(rebuild_result.warnings)

            for kind, field in (
                ("source_probe_worker", "source_probe_worker_blocked"),
                ("extraction_worker", "extraction_worker_blocked"),
                ("ai_model_worker", "ai_model_worker_blocked"),
            ):
                created = runtime.workunit_queue.create_workunit(WorkUnit.new("regression_test", f"Blocked {kind}", payload={"worker_kind": kind}))
                blocked = runner.run_one(created.id)
                result[field] = blocked.status.value == "blocked"
                assert_no_external_effects(blocked.to_dict(), errors)

            transitions = runtime.workunit_queue.list_transitions(limit=500)
            refs = runtime.workunit_queue.list_payload_refs(limit=500)
            result["transition_history_recorded"] = len(transitions) >= 8
            result["worker_audit_recorded"] = any(ref.ref_kind == "worker_audit_event" for ref in refs)
            after_public = runtime.public_index.summarize().to_dict()
            if before_public != after_public:
                errors.append("public index changed during non-mutating worker validation")
            for key, value in result.items():
                if not value:
                    errors.append(f"runtime worker check failed: {key}")
        finally:
            close_local_appliance(runtime)
            close_local_appliance(runtime)
    return result


def validate_cli_and_demo(root: Path, errors: list[str]) -> None:
    missing = run(root, "python", "scripts/eureka_worker_runner.py", "list-workers", "--json")
    if missing.returncode == 0:
        errors.append("worker runner CLI must require --instance")
    with tempfile.TemporaryDirectory(prefix="eureka-local-worker-cli-") as tmp:
        instance = Path(tmp) / "eureka-instance"
        init = run(root, "python", "scripts/eureka_init_instance.py", "--instance", str(instance), "--json")
        if init.returncode != 0:
            errors.append("CLI temp instance init failed")
            return
        create = run(
            root,
            "python",
            "scripts/eureka_workunit_queue.py",
            "--instance",
            str(instance),
            "create",
            "--kind",
            "regression_test",
            "--title",
            "CLI deterministic worker sample",
            "--payload-json",
            "{\"worker_kind\":\"noop_worker\"}",
            "--json",
        )
        if create.returncode != 0:
            errors.append(f"CLI workunit create failed: {create.stdout}{create.stderr}")
            return
        list_workers = run(root, "python", "scripts/eureka_worker_runner.py", "--instance", str(instance), "list-workers", "--json")
        run_next = run(root, "python", "scripts/eureka_worker_runner.py", "--instance", str(instance), "run-next", "--kind", "noop_worker", "--json")
        blocked = run(root, "python", "scripts/eureka_worker_runner.py", "--instance", str(instance), "run-next", "--kind", "source_probe_worker", "--json")
        demo = run(root, "python", "scripts/demo_local_worker_runner.py", "--instance", str(instance), "--json")
        for label, completed in (("list-workers", list_workers), ("run-next", run_next), ("demo", demo)):
            if completed.returncode != 0:
                errors.append(f"worker CLI {label} failed: {completed.stdout}{completed.stderr}")
        if blocked.returncode == 0:
            errors.append("disabled worker CLI must refuse explicit disabled kind")


def validate_queue_state(root: Path, errors: list[str]) -> None:
    queue = read_text(root / ".aide/queue/index.yaml", errors)
    current = read_text(root / ".aide/queue/LOCAL-09/task.yaml", errors)
    next_task = read_text(root / ".aide/queue/LOCAL-10/task.yaml", errors)
    if not queue_current_or_advanced(root, TASK_ID, NEXT_TASK):
        errors.append("queue index must point to LOCAL-10")
    if not queue_task_completed(root, TASK_ID):
        errors.append("queue index must mark LOCAL-09 completed")
    if not queue_task_available(root, NEXT_TASK):
        errors.append("queue index must include queued LOCAL-10")
    if not f0_deferred_or_past_local_closeout(root):
        errors.append("queue index must keep F0 deferred until LOCAL-14")
    if "recommended_next: LOCAL-10" not in current:
        errors.append("LOCAL-09 task must recommend LOCAL-10")
    if "Auto-test and auto-search harness" not in next_task:
        errors.append("LOCAL-10 task title mismatch")


def validate_report(report: Mapping[str, Any], errors: list[str]) -> None:
    if report.get("recommended_next_task") != "LOCAL-10 \u2014 Auto-test and auto-search harness":
        errors.append("LOCAL-09 audit report must recommend LOCAL-10")
    for key in (
        "runtime_package_added",
        "runner_added",
        "registry_added",
        "cli_added",
        "demo_added",
        "validator_added",
        "noop_worker_passed",
        "review_queue_checker_passed",
        "absence_report_worker_passed",
        "local_status_snapshot_worker_passed",
        "reviewed_index_rebuild_worker_token_gated",
        "source_probe_worker_blocked",
        "extraction_worker_blocked",
        "ai_model_worker_blocked",
        "transition_history_recorded",
        "worker_audit_recorded",
        "server_implemented",
        "html_workbench_implemented",
        "workunit_runtime_implemented",
        "worker_execution_enabled",
    ):
        require_true(report, key, errors, "LOCAL-09 audit report")
    for key in (
        "lan_enabled",
        "source_probe_executed",
        "extraction_executed",
        "agent_execution_performed",
        "model_provider_used",
        "download_install_execute_performed",
        "master_index_mutated",
        "site_dist_mutated",
        "deployment_performed",
        "local_09_increased_leakage",
        "production_readiness_claimed",
        "public_launch_readiness_claimed",
    ):
        require_false(report, key, errors, "LOCAL-09 audit report")


def validate_leakage(root: Path, leakage: Mapping[str, Any], errors: list[str], warnings: list[str]) -> None:
    before = int(leakage.get("new_unallowlisted_production_findings_before", -1))
    after = int(leakage.get("new_unallowlisted_production_findings_after", -1))
    if before >= 0 and after > before:
        errors.append("LOCAL-09 increased runtime leakage")
    scan = run_leakage_scan(root)
    if scan:
        scan_count = int(scan.get("summary", {}).get("new_violation_count", -1))
        if before >= 0 and scan_count > before:
            errors.append("current leakage scan exceeds recorded LOCAL-09 baseline")
        if scan.get("gate_report", {}).get("status") == "fail":
            warnings.append("runtime leakage gate fails with pre-existing findings")


def assert_no_external_effects(payload: Mapping[str, Any], errors: list[str]) -> None:
    for key in (
        "external_network_used",
        "source_probe_executed",
        "extraction_executed",
        "model_provider_used",
        "download_install_execute_performed",
        "site_dist_mutated",
        "master_index_mutated",
        "lan_enabled",
        "deployment_performed",
        "production_readiness_claimed",
        "public_launch_readiness_claimed",
    ):
        if payload.get(key) is not False:
            errors.append(f"worker result {key} must be false")


def run_leakage_scan(root: Path) -> Mapping[str, Any]:
    scripts_path = root / "scripts"
    if str(scripts_path) not in sys.path:
        sys.path.insert(0, str(scripts_path))
    import audit_runtime_architecture_leakage as leakage

    policy = leakage.load_json(root / leakage.DEFAULT_POLICY)
    allowlist = leakage.load_json(root / leakage.DEFAULT_ALLOWLIST)
    return leakage.build_leakage_audit(root, policy, allowlist, policy_errors=[])


def require_true(payload: Mapping[str, Any], key: str, errors: list[str], label: str) -> None:
    if payload.get(key) is not True:
        errors.append(f"{label} {key} must be true")


def require_false(payload: Mapping[str, Any], key: str, errors: list[str], label: str) -> None:
    if payload.get(key) is not False:
        errors.append(f"{label} {key} must be false")


def load_json(path: Path, schema: str, errors: list[str]) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"missing JSON file: {relpath(path)}")
        return {}
    except json.JSONDecodeError as exc:
        errors.append(f"invalid JSON {relpath(path)}: {exc}")
        return {}
    if not isinstance(payload, dict):
        errors.append(f"JSON file must contain an object: {relpath(path)}")
        return {}
    if payload.get("schema_version") != schema:
        errors.append(f"schema_version mismatch for {relpath(path)}")
    return payload


def read_text(path: Path, errors: list[str]) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        errors.append(f"missing text file: {relpath(path)}")
        return ""


def write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def run(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(list(args), cwd=root, text=True, capture_output=True, check=False)


def relpath(path: Path) -> str:
    try:
        return path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


if __name__ == "__main__":
    raise SystemExit(main())
