#!/usr/bin/env python3
"""Validate LOCAL-07 durable WorkUnit queue evidence."""

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
from runtime.worker.workunit_queue import (
    ALLOWED_TRANSITIONS,
    ALLOWED_WORKUNIT_STATES,
    ALLOWED_WORKUNIT_TYPES,
    WorkUnit,
    WorkUnitQueueError,
    WorkUnitState,
)


TASK_ID = "LOCAL-07"
NEXT_TASK = "LOCAL-08"
F0_CLOSEOUT = "LOCAL-14"
POLICIES = {
    "control/policies/local_workunit_queue_policy.json": "local_workunit_queue_policy.v0",
    "control/policies/local_workunit_state_policy.json": "local_workunit_state_policy.v0",
    "control/policies/local_workunit_side_effect_policy.json": "local_workunit_side_effect_policy.v0",
}
INVENTORIES = {
    "control/inventory/local_workunit_queue_inventory.json": "local_workunit_queue_inventory.v0",
    "control/inventory/local_workunit_state_machine.json": "local_workunit_state_machine.v0",
    "control/inventory/local_workunit_queue_result.json": "local_workunit_queue_result.v0",
    "control/inventory/local_workunit_queue_demo_result.json": "local_workunit_queue_demo_result.v0",
    "control/inventory/local_workunit_gap_register.json": "local_workunit_gap_register.v0",
    "control/inventory/local_07_leakage_baseline.json": "local_07_leakage_baseline.v0",
    "control/inventory/local_07_next_task_decision.json": "local_07_next_task_decision.v0",
}
RUNTIME_FILES = (
    "runtime/worker/workunit_queue/__init__.py",
    "runtime/worker/workunit_queue/schema.py",
    "runtime/worker/workunit_queue/records.py",
    "runtime/worker/workunit_queue/store.py",
    "runtime/worker/workunit_queue/transitions.py",
    "runtime/worker/workunit_queue/queries.py",
    "runtime/worker/workunit_queue/validation.py",
    "runtime/worker/workunit_queue/errors.py",
)
SCRIPTS = (
    "scripts/eureka_workunit_queue.py",
    "scripts/demo_workunit_queue.py",
    "scripts/validate_workunit_queue.py",
)
TESTS = (
    "tests/runtime/test_workunit_queue_store.py",
    "tests/runtime/test_workunit_queue_transitions.py",
    "tests/runtime/test_workunit_queue_validation.py",
    "tests/runtime/test_workunit_queue_integration.py",
    "tests/operations/test_workunit_queue_scripts.py",
)
DOCS = (
    "docs/architecture/LOCAL_WORKUNIT_QUEUE.md",
    "docs/reference/LOCAL_WORKUNIT_QUEUE_RUNTIME.md",
    "docs/reference/LOCAL_WORKUNIT_STATE_MACHINE.md",
    "docs/operations/LOCAL_WORKUNIT_QUEUE_RUNBOOK.md",
)
AUDIT_ROOT = Path("control/audits/local-07-workunit-queue-v0")
AUDIT_FILES = (
    "README.md",
    "local_07_report.json",
    "workunit_queue_summary.md",
    "state_machine.md",
    "side_effect_boundary.md",
    "demo_result.md",
    "leakage_baseline.md",
    "validation.md",
    "generated/sample_workunit.json",
    "generated/sample_workunit_list.json",
    "generated/sample_transition_history.json",
    "generated/sample_demo_result.json",
    "generated/sample_summary.md",
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
FORBIDDEN_VOCABULARY = ("LOCAL-", "AIDE", "H0", "H1", "H2", "H3", "H4", "H5", "H6", "H7", "H8", "H9", "H10", "H11", "H12", "H13", "H14", "BUNDLE")
EXPECTED_TYPES = (
    "search_need",
    "source_probe",
    "evidence_review",
    "index_rebuild",
    "regression_test",
    "extraction_task",
    "agent_task",
)
EXPECTED_STATES = ("queued", "running", "paused", "blocked", "complete", "failed", "cancelled")
EXPECTED_TRANSITIONS = (
    ("queued", "running"),
    ("queued", "paused"),
    ("queued", "blocked"),
    ("queued", "cancelled"),
    ("running", "paused"),
    ("running", "complete"),
    ("running", "failed"),
    ("running", "blocked"),
    ("running", "cancelled"),
    ("paused", "queued"),
    ("paused", "cancelled"),
    ("blocked", "queued"),
    ("blocked", "cancelled"),
    ("failed", "queued"),
    ("complete", "complete"),
    ("cancelled", "cancelled"),
)


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
        print("LOCAL-07 workunit queue validation", file=stdout)
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
    report = load_json(root / AUDIT_ROOT / "local_07_report.json", "local_07_report.v0", errors)
    validate_policies(payloads, errors)
    validate_inventories(payloads, errors, warnings)
    validate_files(root, errors)
    validate_runtime_imports(root, errors)
    validate_runtime_vocabulary(root, errors)
    service = validate_queue_runtime(root, errors)
    validate_cli_and_demo(root, errors)
    validate_queue_state(root, errors)
    validate_report(report, errors)
    validate_leakage(root, payloads.get("control/inventory/local_07_leakage_baseline.json", {}), errors, warnings)
    status = "fail" if errors else ("pass_with_warnings" if warnings else "pass")
    return {
        "schema_version": "local_workunit_queue_validation.v0",
        "task": TASK_ID,
        "status": status,
        "errors": errors,
        "warnings": warnings,
        "runtime_package_added": all((root / rel).is_file() for rel in RUNTIME_FILES),
        "sqlite_store_added": service.get("sqlite_store_added", False),
        "cli_added": (root / "scripts/eureka_workunit_queue.py").is_file(),
        "demo_added": (root / "scripts/demo_workunit_queue.py").is_file(),
        "validator_added": True,
        "all_required_types_supported": set(EXPECTED_TYPES).issubset(set(ALLOWED_WORKUNIT_TYPES)),
        "all_required_states_supported": set(EXPECTED_STATES).issubset(set(ALLOWED_WORKUNIT_STATES)),
        "valid_transitions_passed": service.get("valid_transitions_passed", False),
        "invalid_transitions_rejected": service.get("invalid_transitions_rejected", False),
        "transition_history_recorded": service.get("transition_history_recorded", False),
        "idempotency_checked": service.get("idempotency_checked", False),
        "source_probe_executed": False,
        "worker_execution_performed": False,
        "review_mutation_performed": False,
        "index_rebuild_performed": False,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }


def validate_policies(payloads: Mapping[str, Mapping[str, Any]], errors: list[str]) -> None:
    queue_policy = payloads.get("control/policies/local_workunit_queue_policy.json", {})
    expected_false = (
        "workunit_execution_enabled",
        "worker_runner_enabled",
        "source_probe_execution_enabled",
        "agent_execution_enabled",
        "review_decision_mutation_enabled",
        "index_rebuild_enabled",
        "public_index_direct_mutation_enabled",
        "master_index_mutation_enabled",
        "lan_enabled",
        "deployment_enabled",
        "production_readiness_claimed",
        "public_launch_readiness_claimed",
    )
    for key in ("durable_queue_required", "sqlite_store_required", "explicit_instance_path_required", "hidden_state_roots_forbidden", "committed_queue_state_forbidden"):
        if queue_policy.get(key) is not True:
            errors.append(f"queue policy {key} must be true")
    for key in expected_false:
        if queue_policy.get(key) is not False:
            errors.append(f"queue policy {key} must be false")

    state_policy = payloads.get("control/policies/local_workunit_state_policy.json", {})
    if state_policy.get("allowed_states") != list(EXPECTED_STATES):
        errors.append("state policy allowed_states mismatch")
    if state_policy.get("allowed_types") != list(EXPECTED_TYPES):
        errors.append("state policy allowed_types mismatch")
    transitions = [(item.get("from"), item.get("to")) for item in state_policy.get("allowed_transitions", []) if isinstance(item, Mapping)]
    if transitions != list(EXPECTED_TRANSITIONS):
        errors.append("state policy allowed_transitions mismatch")
    for key in ("invalid_transitions_fail_closed", "transition_history_required", "idempotent_terminal_transitions"):
        if state_policy.get(key) is not True:
            errors.append(f"state policy {key} must be true")

    side_effect = payloads.get("control/policies/local_workunit_side_effect_policy.json", {})
    if side_effect.get("queue_mutation_allowed") is not True:
        errors.append("side-effect policy must allow queue mutation")
    for key in (
        "work_execution_allowed",
        "source_probe_allowed",
        "download_allowed",
        "install_execution_allowed",
        "model_provider_allowed",
        "review_decision_allowed",
        "index_rebuild_allowed",
        "direct_public_index_mutation_allowed",
        "master_index_mutation_allowed",
        "site_dist_writes_allowed",
        "lan_operations_allowed",
    ):
        if side_effect.get(key) is not False:
            errors.append(f"side-effect policy {key} must be false")


def validate_inventories(payloads: Mapping[str, Mapping[str, Any]], errors: list[str], warnings: list[str]) -> None:
    inventory = payloads.get("control/inventory/local_workunit_queue_inventory.json", {})
    if inventory.get("runtime_package") != "runtime/worker/workunit_queue":
        errors.append("workunit inventory runtime_package mismatch")
    if inventory.get("store_id") != "workunit_queue" or inventory.get("db_path") != "db/workunit_queue.sqlite":
        errors.append("workunit inventory store path mismatch")
    if inventory.get("workunit_types") != list(EXPECTED_TYPES):
        errors.append("workunit inventory types mismatch")
    if inventory.get("workunit_states") != list(EXPECTED_STATES):
        errors.append("workunit inventory states mismatch")
    for key in (
        "execution_enabled",
        "worker_runner_enabled",
        "source_probe_execution_enabled",
        "review_decision_mutation_enabled",
        "index_rebuild_enabled",
        "lan_enabled",
        "deployment_performed",
    ):
        if inventory.get(key) is not False:
            errors.append(f"workunit inventory {key} must be false")

    state_machine = payloads.get("control/inventory/local_workunit_state_machine.json", {})
    if state_machine.get("allowed_states") != list(EXPECTED_STATES):
        errors.append("state machine inventory states mismatch")
    transitions = [(item.get("from"), item.get("to")) for item in state_machine.get("allowed_transitions", []) if isinstance(item, Mapping)]
    if transitions != list(EXPECTED_TRANSITIONS):
        errors.append("state machine inventory transitions mismatch")

    result = payloads.get("control/inventory/local_workunit_queue_result.json", {})
    for key in (
        "runtime_package_added",
        "sqlite_store_added",
        "cli_added",
        "demo_added",
        "validator_added",
        "all_required_types_supported",
        "all_required_states_supported",
        "valid_transitions_passed",
        "invalid_transitions_rejected",
        "transition_history_recorded",
        "idempotency_checked",
    ):
        if result.get(key) is not True:
            errors.append(f"workunit result {key} must be true")
    for key in (
        "source_probe_executed",
        "worker_execution_performed",
        "review_mutation_performed",
        "index_rebuild_performed",
        "deployment_performed",
        "production_readiness_claimed",
        "public_launch_readiness_claimed",
    ):
        if result.get(key) is not False:
            errors.append(f"workunit result {key} must be false")

    demo = payloads.get("control/inventory/local_workunit_queue_demo_result.json", {})
    if demo.get("status") != "pass":
        errors.append("workunit demo inventory must pass")

    decision = payloads.get("control/inventory/local_07_next_task_decision.json", {})
    if decision.get("recommended_next_task") != "LOCAL-08 \u2014 Review and index rebuild from UI":
        errors.append("LOCAL-07 next task decision must point to LOCAL-08")
    if decision.get("f0_current_status") != "deferred" or decision.get("f0_can_resume_after") != F0_CLOSEOUT:
        errors.append("F0 must remain deferred until LOCAL-14")
    if decision.get("lan_can_start") is not False or decision.get("worker_execution_enabled") is not False:
        errors.append("LOCAL-07 next task decision flags mismatch")

    leakage = payloads.get("control/inventory/local_07_leakage_baseline.json", {})
    if leakage.get("local_07_increased_leakage") is not False:
        errors.append("LOCAL-07 leakage baseline must not increase leakage")
    if leakage.get("runtime_leakage_gate_status_after") == "fail":
        warnings.append("pre-existing runtime leakage gate still fails")


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
        for token in FORBIDDEN_VOCABULARY:
            if token in text:
                errors.append(f"forbidden runtime vocabulary in {rel}: {token}")


def validate_queue_runtime(root: Path, errors: list[str]) -> dict[str, bool]:
    result = {
        "sqlite_store_added": False,
        "valid_transitions_passed": False,
        "invalid_transitions_rejected": False,
        "transition_history_recorded": False,
        "idempotency_checked": False,
    }
    if set(EXPECTED_TYPES) - set(ALLOWED_WORKUNIT_TYPES):
        errors.append("runtime missing required workunit types")
    if set(EXPECTED_STATES) - set(ALLOWED_WORKUNIT_STATES):
        errors.append("runtime missing required workunit states")
    runtime_transitions = sorted((from_state.value, to_state.value) for from_state, targets in ALLOWED_TRANSITIONS.items() for to_state in targets)
    if sorted(EXPECTED_TRANSITIONS) != runtime_transitions:
        errors.append("runtime transition table mismatch")

    with tempfile.TemporaryDirectory(prefix="eureka-workunit-validation-") as tmp:
        instance = Path(tmp) / "eureka-instance"
        init = run(root, "python", "scripts/eureka_init_instance.py", "--instance", str(instance), "--json")
        if init.returncode != 0:
            errors.append(f"temp instance init failed: {init.stdout}{init.stderr}")
            return result
        runtime = open_local_appliance(instance)
        try:
            queue = runtime.workunit_queue
            result["sqlite_store_added"] = (instance / "db" / "workunit_queue.sqlite").is_file()
            before_public = runtime.public_index.summarize().to_dict()
            for kind in EXPECTED_TYPES:
                queue.create_workunit(WorkUnit.new(kind, f"Sample {kind}"))
            result["valid_transitions_passed"] = exercise_valid_transitions(queue, errors)
            result["invalid_transitions_rejected"] = exercise_invalid_transition(queue)
            transitions = queue.list_transitions(limit=500)
            result["transition_history_recorded"] = len(transitions) >= len(EXPECTED_TYPES)
            terminal = queue.create_workunit(WorkUnit.new("search_need", "Terminal idempotency sample"))
            queue.transition_workunit(terminal.id, "running", "start")
            queue.complete_workunit(terminal.id, "finish")
            before_repeat = len(queue.list_transitions(terminal.id))
            queue.complete_workunit(terminal.id, "repeat")
            after_repeat = len(queue.list_transitions(terminal.id))
            result["idempotency_checked"] = before_repeat == after_repeat
            integrity = queue.check_integrity()
            if integrity.get("status") != "pass":
                errors.append("workunit queue integrity failed")
            status = runtime.status().to_dict()
            if "workunit_queue" not in status.get("stores", {}) or status.get("workunit_queue", {}).get("execution_enabled") is not False:
                errors.append("runtime status missing workunit_queue or execution flag")
            for key in ("server_enabled", "lan_enabled", "deployment_performed", "production_readiness_claimed", "public_launch_readiness_claimed"):
                if status.get(key) is not False:
                    errors.append(f"runtime status {key} must be false")
            after_public = runtime.public_index.summarize().to_dict()
            if before_public != after_public:
                errors.append("public index summary changed during queue validation")
        finally:
            close_local_appliance(runtime)
            close_local_appliance(runtime)
    return result


def exercise_valid_transitions(queue: Any, errors: list[str]) -> bool:
    try:
        for from_state, to_state in EXPECTED_TRANSITIONS:
            item = queue.create_workunit(WorkUnit.new("search_need", f"{from_state} to {to_state}"))
            move_to_state(queue, item.id, from_state)
            queue.transition_workunit(item.id, to_state, "validator transition")
        return True
    except WorkUnitQueueError as exc:
        errors.append(f"valid transition failed: {exc}")
        return False


def move_to_state(queue: Any, workunit_id: str, state: str) -> None:
    if state == "queued":
        return
    if state == "running":
        queue.transition_workunit(workunit_id, "running", "prepare")
    elif state == "paused":
        queue.pause_workunit(workunit_id, "prepare")
    elif state == "blocked":
        queue.block_workunit(workunit_id, "prepare")
    elif state == "failed":
        queue.transition_workunit(workunit_id, "running", "prepare")
        queue.fail_workunit(workunit_id, "prepare")
    elif state == "complete":
        queue.transition_workunit(workunit_id, "running", "prepare")
        queue.complete_workunit(workunit_id, "prepare")
    elif state == "cancelled":
        queue.cancel_workunit(workunit_id, "prepare")


def exercise_invalid_transition(queue: Any) -> bool:
    item = queue.create_workunit(WorkUnit.new("search_need", "Invalid transition sample"))
    try:
        queue.complete_workunit(item.id, "invalid")
    except WorkUnitQueueError:
        return True
    return False


def validate_cli_and_demo(root: Path, errors: list[str]) -> None:
    with tempfile.TemporaryDirectory(prefix="eureka-workunit-cli-") as tmp:
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
            "search_need",
            "--title",
            "Validator sample",
            "--json",
        )
        if create.returncode != 0:
            errors.append(f"CLI create failed: {create.stdout}{create.stderr}")
            return
        payload = json.loads(create.stdout)
        workunit_id = payload.get("workunit", {}).get("id")
        listing = run(root, "python", "scripts/eureka_workunit_queue.py", "--instance", str(instance), "list", "--json")
        show = run(root, "python", "scripts/eureka_workunit_queue.py", "--instance", str(instance), "show", "--id", str(workunit_id), "--json")
        summary = run(root, "python", "scripts/eureka_workunit_queue.py", "--instance", str(instance), "summary", "--json")
        demo = run(root, "python", "scripts/demo_workunit_queue.py", "--instance", str(instance), "--json")
        for label, completed in (("CLI list", listing), ("CLI show", show), ("CLI summary", summary), ("demo", demo)):
            if completed.returncode != 0:
                errors.append(f"{label} failed: {completed.stdout}{completed.stderr}")


def validate_queue_state(root: Path, errors: list[str]) -> None:
    queue = read_text(root / ".aide/queue/index.yaml", errors)
    task = read_text(root / ".aide/queue/LOCAL-07/task.yaml", errors)
    next_task = read_text(root / ".aide/queue/LOCAL-08/task.yaml", errors)
    if not queue_current_or_advanced(root, TASK_ID, NEXT_TASK):
        errors.append("queue index must point to LOCAL-08")
    if not queue_task_completed(root, TASK_ID):
        errors.append("queue index must mark LOCAL-07 completed")
    if not queue_task_available(root, NEXT_TASK):
        errors.append("queue index must include queued LOCAL-08")
    if not f0_deferred_or_past_local_closeout(root):
        errors.append("queue index must keep F0 deferred until LOCAL-14")
    if "recommended_next: LOCAL-08" not in task:
        errors.append("LOCAL-07 task must recommend LOCAL-08")
    if "Review and index rebuild from UI" not in next_task:
        errors.append("LOCAL-08 task title mismatch")


def validate_report(report: Mapping[str, Any], errors: list[str]) -> None:
    if report.get("recommended_next_task") != "LOCAL-08 \u2014 Review and index rebuild from UI":
        errors.append("LOCAL-07 audit report must recommend LOCAL-08")
    for key in (
        "runtime_package_added",
        "sqlite_store_added",
        "cli_added",
        "demo_added",
        "validator_added",
        "all_required_types_supported",
        "all_required_states_supported",
        "valid_transitions_passed",
        "invalid_transitions_rejected",
        "transition_history_recorded",
        "idempotency_checked",
        "server_implemented",
        "html_workbench_implemented",
        "workunit_runtime_implemented",
    ):
        if report.get(key) is not True:
            errors.append(f"LOCAL-07 report {key} must be true")
    for key in (
        "worker_execution_enabled",
        "lan_enabled",
        "source_probe_executed",
        "review_mutation_performed",
        "index_rebuild_performed",
        "deployment_performed",
        "local_07_increased_leakage",
        "production_readiness_claimed",
        "public_launch_readiness_claimed",
    ):
        if report.get(key) is not False:
            errors.append(f"LOCAL-07 report {key} must be false")


def validate_leakage(root: Path, leakage: Mapping[str, Any], errors: list[str], warnings: list[str]) -> None:
    before = int(leakage.get("new_unallowlisted_production_findings_before", -1))
    after = int(leakage.get("new_unallowlisted_production_findings_after", -1))
    if before >= 0 and after > before:
        errors.append("LOCAL-07 increased runtime leakage")
    scan = run_leakage_scan(root)
    if scan:
        scan_count = int(scan.get("summary", {}).get("new_violation_count", -1))
        if scan_count > before and before >= 0:
            errors.append("current leakage scan exceeds recorded LOCAL-07 baseline")
        if scan.get("gate_report", {}).get("status") == "fail":
            warnings.append("runtime leakage gate fails with pre-existing findings")


def run_leakage_scan(root: Path) -> Mapping[str, Any]:
    import audit_runtime_architecture_leakage as leakage

    policy = leakage.load_json(root / leakage.DEFAULT_POLICY)
    allowlist = leakage.load_json(root / leakage.DEFAULT_ALLOWLIST)
    return leakage.build_leakage_audit(root, policy, allowlist, policy_errors=[])


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
