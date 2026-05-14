#!/usr/bin/env python3
"""Validate HUNT-01 Search Hunt Session runtime evidence."""

from __future__ import annotations

import argparse
import ast
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.local_appliance import close_local_appliance, open_local_appliance
from runtime.search_hunt import (
    ALLOWED_SEARCH_HUNT_CHECKED_LAYERS,
    ALLOWED_SEARCH_HUNT_STATES,
    ALLOWED_SEARCH_HUNT_UNCHECKED_LAYERS,
    ALLOWED_TRANSITIONS,
    SearchHuntError,
    SearchHuntSession,
    SearchHuntState,
    build_local_absence_summary,
    build_reviewed_index_search_summary,
)


TASK_ID = "HUNT-01"
NEXT_TASK = "HUNT-02"
POLICIES = {
    "control/policies/search_hunt_runtime_policy.json": "search_hunt_runtime_policy.v0",
    "control/policies/search_hunt_state_policy.json": "search_hunt_state_policy.v0",
    "control/policies/search_hunt_side_effect_policy.json": "search_hunt_side_effect_policy.v0",
    "control/policies/search_hunt_store_policy.json": "search_hunt_store_policy.v0",
}
INVENTORIES = {
    "control/inventory/search_hunt_runtime_inventory.json": "search_hunt_runtime_inventory.v0",
    "control/inventory/search_hunt_state_machine.json": "search_hunt_state_machine.v0",
    "control/inventory/search_hunt_store_result.json": "search_hunt_store_result.v0",
    "control/inventory/search_hunt_runtime_result.json": "search_hunt_runtime_result.v0",
    "control/inventory/search_hunt_demo_result.json": "search_hunt_demo_result.v0",
    "control/inventory/search_hunt_gap_register.json": "search_hunt_gap_register.v0",
    "control/inventory/hunt_01_next_task_decision.json": "hunt_01_next_task_decision.v0",
}
RUNTIME_FILES = (
    "runtime/search_hunt/__init__.py",
    "runtime/search_hunt/schema.py",
    "runtime/search_hunt/records.py",
    "runtime/search_hunt/store.py",
    "runtime/search_hunt/transitions.py",
    "runtime/search_hunt/search_summary.py",
    "runtime/search_hunt/absence_summary.py",
    "runtime/search_hunt/queries.py",
    "runtime/search_hunt/validation.py",
    "runtime/search_hunt/errors.py",
)
SCRIPTS = (
    "scripts/eureka_search_hunt.py",
    "scripts/demo_search_hunt_session.py",
    "scripts/validate_search_hunt_runtime.py",
)
TESTS = (
    "tests/runtime/test_search_hunt_store.py",
    "tests/runtime/test_search_hunt_records.py",
    "tests/runtime/test_search_hunt_transitions.py",
    "tests/runtime/test_search_hunt_search_summary.py",
    "tests/runtime/test_search_hunt_integration.py",
    "tests/operations/test_search_hunt_scripts.py",
)
DOCS = (
    "docs/architecture/SEARCH_HUNT_SESSION_RUNTIME.md",
    "docs/reference/SEARCH_HUNT_SESSION_RECORD.md",
    "docs/reference/SEARCH_HUNT_STATE_MACHINE.md",
    "docs/operations/SEARCH_HUNT_RUNTIME_RUNBOOK.md",
)
AUDIT_ROOT = Path("control/audits/hunt-01-search-hunt-session-runtime-v0")
AUDIT_FILES = (
    "README.md",
    "hunt_01_report.json",
    "session_runtime_summary.md",
    "state_machine.md",
    "store_summary.md",
    "local_appliance_integration.md",
    "side_effect_boundary.md",
    "demo_result.md",
    "validation.md",
    "generated/sample_search_hunt_session.json",
    "generated/sample_search_hunt_list.json",
    "generated/sample_transition_history.json",
    "generated/sample_search_summary.json",
    "generated/sample_absence_summary.json",
    "generated/sample_demo_result.json",
    "generated/sample_summary.md",
)
EXPECTED_STATES = (
    "created",
    "running",
    "paused",
    "waiting_for_user",
    "waiting_for_policy",
    "blocked",
    "complete",
    "failed",
    "cancelled",
)
EXPECTED_CHECKED = ("reviewed_public_index", "local_candidate_summary", "local_absence_report")
EXPECTED_UNCHECKED = (
    "source_probes",
    "WorkUnits",
    "extraction",
    "broader_connectors",
    "synthetic_query_foundry",
    "AI_research_escalation",
)
EXPECTED_TRANSITIONS = (
    ("created", "running"),
    ("created", "paused"),
    ("created", "blocked"),
    ("created", "cancelled"),
    ("running", "paused"),
    ("running", "waiting_for_user"),
    ("running", "waiting_for_policy"),
    ("running", "complete"),
    ("running", "failed"),
    ("running", "blocked"),
    ("running", "cancelled"),
    ("paused", "running"),
    ("paused", "cancelled"),
    ("waiting_for_user", "running"),
    ("waiting_for_user", "cancelled"),
    ("waiting_for_policy", "running"),
    ("waiting_for_policy", "blocked"),
    ("waiting_for_policy", "cancelled"),
    ("blocked", "running"),
    ("blocked", "cancelled"),
    ("failed", "running"),
    ("complete", "complete"),
    ("cancelled", "cancelled"),
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
        print("HUNT-01 Search Hunt runtime validation", file=stdout)
        print(f"status: {result['status']}", file=stdout)
        for error in result["errors"]:
            print(f"ERROR: {error}", file=stdout)
        for warning in result["warnings"]:
            print(f"WARN: {warning}", file=stdout)
    return 0 if result["status"] in {"pass", "pass_with_warnings"} else 1


def validate(root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    payloads = {rel: load_json(root / rel, schema, errors) for rel, schema in {**POLICIES, **INVENTORIES}.items()}
    report = load_json(root / AUDIT_ROOT / "hunt_01_report.json", "hunt_01_report.v0", errors)
    validate_required_files(root, errors)
    validate_policies(payloads, errors)
    validate_inventories(payloads, errors)
    validate_runtime_imports(root, errors)
    validate_runtime_vocabulary(root, errors)
    runtime_result = validate_runtime_behavior(root, errors)
    validate_cli_and_demo(root, errors)
    validate_queue(root, errors)
    validate_report(report, errors)
    status = "fail" if errors else ("pass_with_warnings" if warnings else "pass")
    return {
        "schema_version": "search_hunt_runtime_validation.v0",
        "task": TASK_ID,
        "status": status,
        "errors": errors,
        "warnings": warnings,
        "runtime_package_added": all((root / rel).is_file() for rel in RUNTIME_FILES),
        "sqlite_store_added": runtime_result.get("sqlite_store_added", False),
        "store_added_to_instance_manifest": runtime_result.get("store_added_to_instance_manifest", False),
        "cli_added": (root / "scripts/eureka_search_hunt.py").is_file(),
        "demo_added": (root / "scripts/demo_search_hunt_session.py").is_file(),
        "validator_added": True,
        "session_create_passed": runtime_result.get("session_create_passed", False),
        "session_list_show_passed": runtime_result.get("session_list_show_passed", False),
        "valid_transitions_passed": runtime_result.get("valid_transitions_passed", False),
        "invalid_transitions_rejected": runtime_result.get("invalid_transitions_rejected", False),
        "transition_history_recorded": runtime_result.get("transition_history_recorded", False),
        "reviewed_index_search_summary_passed": runtime_result.get("reviewed_index_search_summary_passed", False),
        "local_absence_summary_passed": runtime_result.get("local_absence_summary_passed", False),
        "workunit_creation_performed": False,
        "source_probe_executed": False,
        "external_network_used": False,
        "model_provider_used": False,
        "review_mutation_performed": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }


def validate_required_files(root: Path, errors: list[str]) -> None:
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


def validate_policies(payloads: Mapping[str, Mapping[str, Any]], errors: list[str]) -> None:
    runtime = payloads.get("control/policies/search_hunt_runtime_policy.json", {})
    for key in (
        "durable_store_required",
        "sqlite_store_required",
        "explicit_instance_path_required",
        "local_appliance_composition_required",
        "reviewed_index_first",
        "session_creation_enabled",
    ):
        if runtime.get(key) is not True:
            errors.append(f"runtime policy {key} must be true")
    for key in (
        "workunit_creation_enabled",
        "source_probe_execution_enabled",
        "extraction_execution_enabled",
        "model_provider_enabled",
        "sync_enabled",
        "direct_public_index_mutation_enabled",
        "master_index_mutation_enabled",
        "deployment_enabled",
        "production_readiness_claimed",
        "public_launch_readiness_claimed",
    ):
        if runtime.get(key) is not False:
            errors.append(f"runtime policy {key} must be false")

    state = payloads.get("control/policies/search_hunt_state_policy.json", {})
    if state.get("allowed_states") != list(EXPECTED_STATES):
        errors.append("state policy allowed_states mismatch")
    transitions = [(item.get("from"), item.get("to")) for item in state.get("allowed_transitions", []) if isinstance(item, Mapping)]
    if transitions != list(EXPECTED_TRANSITIONS):
        errors.append("state policy allowed_transitions mismatch")
    for key in ("invalid_transitions_fail_closed", "transition_history_required", "idempotent_terminal_transitions"):
        if state.get(key) is not True:
            errors.append(f"state policy {key} must be true")

    side_effect = payloads.get("control/policies/search_hunt_side_effect_policy.json", {})
    for key in ("hunt_store_mutation_allowed", "hunt_state_transition_allowed", "search_summary_recording_allowed", "absence_summary_recording_allowed"):
        if side_effect.get(key) is not True:
            errors.append(f"side-effect policy {key} must be true")
    for key in (
        "workunit_creation_allowed",
        "source_probe_allowed",
        "extraction_allowed",
        "external_network_allowed",
        "model_provider_allowed",
        "sync_allowed",
        "review_decision_allowed",
        "public_index_mutation_allowed",
        "master_index_mutation_allowed",
        "site_dist_writes_allowed",
        "deployment_allowed",
    ):
        if side_effect.get(key) is not False:
            errors.append(f"side-effect policy {key} must be false")

    store = payloads.get("control/policies/search_hunt_store_policy.json", {})
    if store.get("store_id") != "search_hunt" or store.get("db_path") != "db/search_hunt.sqlite":
        errors.append("store policy path mismatch")
    for key in ("instance_manifest_required", "store_paths_must_come_from_manifest", "ad_hoc_store_paths_forbidden", "hidden_store_paths_forbidden", "schema_version_required", "integrity_check_required"):
        if store.get(key) is not True:
            errors.append(f"store policy {key} must be true")


def validate_inventories(payloads: Mapping[str, Mapping[str, Any]], errors: list[str]) -> None:
    inventory = payloads.get("control/inventory/search_hunt_runtime_inventory.json", {})
    if inventory.get("runtime_package") != "runtime/search_hunt":
        errors.append("runtime inventory package mismatch")
    if inventory.get("store_id") != "search_hunt" or inventory.get("db_path") != "db/search_hunt.sqlite":
        errors.append("runtime inventory store path mismatch")
    if inventory.get("states") != list(EXPECTED_STATES):
        errors.append("runtime inventory states mismatch")
    if inventory.get("checked_layers") != list(EXPECTED_CHECKED):
        errors.append("runtime inventory checked_layers mismatch")
    if inventory.get("unchecked_layers") != list(EXPECTED_UNCHECKED):
        errors.append("runtime inventory unchecked_layers mismatch")
    for key in ("workunit_creation_enabled", "source_probe_execution_enabled", "model_provider_enabled", "sync_enabled", "deployment_performed"):
        if inventory.get(key) is not False:
            errors.append(f"runtime inventory {key} must be false")

    state_machine = payloads.get("control/inventory/search_hunt_state_machine.json", {})
    if state_machine.get("allowed_states") != list(EXPECTED_STATES):
        errors.append("state machine inventory states mismatch")
    transitions = [(item.get("from"), item.get("to")) for item in state_machine.get("allowed_transitions", []) if isinstance(item, Mapping)]
    if transitions != list(EXPECTED_TRANSITIONS):
        errors.append("state machine inventory transitions mismatch")

    store_result = payloads.get("control/inventory/search_hunt_store_result.json", {})
    for key in ("sqlite_store_added", "store_added_to_instance_manifest", "init_validation_integration_passed", "transition_history_recorded", "integrity_check_passed"):
        if store_result.get(key) is not True:
            errors.append(f"store result {key} must be true")

    runtime_result = payloads.get("control/inventory/search_hunt_runtime_result.json", {})
    for key in (
        "runtime_package_added",
        "cli_added",
        "demo_added",
        "validator_added",
        "session_create_passed",
        "session_list_show_passed",
        "valid_transitions_passed",
        "invalid_transitions_rejected",
        "reviewed_index_search_summary_passed",
        "local_absence_summary_passed",
    ):
        if runtime_result.get(key) is not True:
            errors.append(f"runtime result {key} must be true")
    for key in (
        "workunit_creation_performed",
        "source_probe_executed",
        "external_network_used",
        "model_provider_used",
        "review_mutation_performed",
        "public_index_mutated",
        "master_index_mutated",
        "deployment_performed",
        "production_readiness_claimed",
        "public_launch_readiness_claimed",
    ):
        if runtime_result.get(key) is not False:
            errors.append(f"runtime result {key} must be false")

    decision = payloads.get("control/inventory/hunt_01_next_task_decision.json", {})
    if decision.get("recommended_next_task") != "HUNT-02 \u2014 Search Hunt UI state in Local Workbench":
        errors.append("HUNT-01 next task decision must point to HUNT-02")
    for key in ("workunit_creation_enabled", "source_probe_execution_enabled", "model_provider_enabled"):
        if decision.get(key) is not False:
            errors.append(f"HUNT-01 decision {key} must be false")


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


def validate_runtime_behavior(root: Path, errors: list[str]) -> dict[str, bool]:
    result = {
        "sqlite_store_added": False,
        "store_added_to_instance_manifest": False,
        "session_create_passed": False,
        "session_list_show_passed": False,
        "valid_transitions_passed": False,
        "invalid_transitions_rejected": False,
        "transition_history_recorded": False,
        "reviewed_index_search_summary_passed": False,
        "local_absence_summary_passed": False,
    }
    if tuple(ALLOWED_SEARCH_HUNT_STATES) != EXPECTED_STATES:
        errors.append("runtime states mismatch")
    if tuple(ALLOWED_SEARCH_HUNT_CHECKED_LAYERS) != EXPECTED_CHECKED:
        errors.append("runtime checked layers mismatch")
    if tuple(ALLOWED_SEARCH_HUNT_UNCHECKED_LAYERS) != EXPECTED_UNCHECKED:
        errors.append("runtime unchecked layers mismatch")
    runtime_transitions = tuple((from_state.value, to_state.value) for from_state, targets in ALLOWED_TRANSITIONS.items() for to_state in targets)
    if runtime_transitions != EXPECTED_TRANSITIONS:
        errors.append("runtime transition table mismatch")

    with tempfile.TemporaryDirectory(prefix="eureka-search-hunt-runtime-") as tmp:
        instance = Path(tmp) / "eureka-instance"
        init = run(root, "python", "scripts/eureka_init_instance.py", "--instance", str(instance), "--json")
        if init.returncode != 0:
            errors.append(f"temp instance init failed: {init.stdout}{init.stderr}")
            return result
        validate = run(root, "python", "scripts/eureka_validate_instance.py", "--instance", str(instance), "--json")
        if validate.returncode != 0:
            errors.append(f"temp instance validation failed: {validate.stdout}{validate.stderr}")
            return result
        runtime = open_local_appliance(instance)
        try:
            result["sqlite_store_added"] = (instance / "db" / "search_hunt.sqlite").is_file()
            result["store_added_to_instance_manifest"] = "search_hunt" in runtime.store_manifest.stores
            before_work = runtime.workunit_queue.summarize().to_dict()
            before_public = runtime.public_index.summarize().to_dict()
            session = runtime.search_hunt.create_session_from_query("sampleproject", runtime=runtime, idempotency_key="runtime-validator-sample")
            result["session_create_passed"] = bool(session.id and session.state.value == "created")
            result["session_list_show_passed"] = runtime.search_hunt.get_session(session.id) is not None and bool(runtime.search_hunt.list_sessions())
            result["valid_transitions_passed"] = exercise_valid_transitions(runtime.search_hunt, errors)
            result["invalid_transitions_rejected"] = exercise_invalid_transition(runtime.search_hunt)
            result["transition_history_recorded"] = len(runtime.search_hunt.list_transitions(limit=500)) >= 2
            search = build_reviewed_index_search_summary(runtime, "sampleproject")
            absence = build_local_absence_summary(runtime, "definitely-not-present-search-hunt-runtime")
            result["reviewed_index_search_summary_passed"] = search.get("reviewed_index_only") is True and search.get("source_probe_executed") is False
            result["local_absence_summary_passed"] = absence.get("local_current_index_absence_only") is True and set(EXPECTED_UNCHECKED).issubset(set(absence.get("unchecked_layers", [])))
            if runtime.search_hunt.check_integrity().get("status") != "pass":
                errors.append("search_hunt integrity failed")
            after_work = runtime.workunit_queue.summarize().to_dict()
            after_public = runtime.public_index.summarize().to_dict()
            if before_work != after_work:
                errors.append("Search Hunt runtime created WorkUnit records")
            if before_public != after_public:
                errors.append("Search Hunt runtime mutated public index")
            status = runtime.status().to_dict()
            if "search_hunt" not in status.get("stores", {}) or status.get("search_hunt", {}).get("source_probe_execution_enabled") is not False:
                errors.append("runtime status missing search_hunt or disabled flags")
        finally:
            close_local_appliance(runtime)
    return result


def exercise_valid_transitions(store: Any, errors: list[str]) -> bool:
    try:
        for from_state, to_state in EXPECTED_TRANSITIONS:
            item = store.create_session(SearchHuntSession.new(f"{from_state} to {to_state}"))
            move_to_state(store, item.id, from_state)
            store.transition_session(item.id, to_state, "validator transition")
        return True
    except SearchHuntError as exc:
        errors.append(f"valid transition failed: {exc}")
        return False


def move_to_state(store: Any, session_id: str, state: str) -> None:
    if state == "created":
        return
    if state == "running":
        store.transition_session(session_id, "running", "prepare")
    elif state == "paused":
        store.transition_session(session_id, "paused", "prepare")
    elif state == "waiting_for_user":
        store.transition_session(session_id, "running", "prepare")
        store.transition_session(session_id, "waiting_for_user", "prepare")
    elif state == "waiting_for_policy":
        store.transition_session(session_id, "running", "prepare")
        store.transition_session(session_id, "waiting_for_policy", "prepare")
    elif state == "blocked":
        store.transition_session(session_id, "blocked", "prepare")
    elif state == "failed":
        store.transition_session(session_id, "running", "prepare")
        store.transition_session(session_id, "failed", "prepare")
    elif state == "complete":
        store.transition_session(session_id, "running", "prepare")
        store.transition_session(session_id, "complete", "prepare")
    elif state == "cancelled":
        store.transition_session(session_id, "cancelled", "prepare")


def exercise_invalid_transition(store: Any) -> bool:
    item = store.create_session(SearchHuntSession.new("invalid transition sample"))
    try:
        store.transition_session(item.id, "complete", "invalid")
    except SearchHuntError:
        return True
    return False


def validate_cli_and_demo(root: Path, errors: list[str]) -> None:
    with tempfile.TemporaryDirectory(prefix="eureka-search-hunt-cli-") as tmp:
        instance = Path(tmp) / "eureka-instance"
        init = run(root, "python", "scripts/eureka_init_instance.py", "--instance", str(instance), "--json")
        if init.returncode != 0:
            errors.append("CLI temp instance init failed")
            return
        create = run(root, "python", "scripts/eureka_search_hunt.py", "--instance", str(instance), "create", "--query", "sampleproject", "--json")
        if create.returncode != 0:
            errors.append(f"CLI create failed: {create.stdout}{create.stderr}")
            return
        payload = json.loads(create.stdout)
        session_id = payload.get("session", {}).get("id")
        listing = run(root, "python", "scripts/eureka_search_hunt.py", "--instance", str(instance), "list", "--json")
        show = run(root, "python", "scripts/eureka_search_hunt.py", "--instance", str(instance), "show", "--id", str(session_id), "--with-transitions", "--json")
        transition = run(root, "python", "scripts/eureka_search_hunt.py", "--instance", str(instance), "transition", "--id", str(session_id), "--state", "running", "--reason", "validator", "--json")
        demo = run(root, "python", "scripts/demo_search_hunt_session.py", "--instance", str(instance), "--json")
        for label, completed in (("CLI list", listing), ("CLI show", show), ("CLI transition", transition), ("demo", demo)):
            if completed.returncode != 0:
                errors.append(f"{label} failed: {completed.stdout}{completed.stderr}")


def validate_queue(root: Path, errors: list[str]) -> None:
    queue = read_text(root / ".aide/queue/index.yaml", errors)
    task = read_text(root / ".aide/queue/HUNT-01/task.yaml", errors)
    next_task = read_text(root / ".aide/queue/HUNT-02/task.yaml", errors)
    if "current_recommended_task: HUNT-02" not in queue:
        errors.append("queue must point to HUNT-02")
    if "id: HUNT-01" not in queue or "status: completed" not in queue:
        errors.append("queue must mark HUNT-01 completed")
    if "id: HUNT-02" not in queue or "status: queued" not in queue:
        errors.append("queue must include HUNT-02 queued")
    if "recommended_next: HUNT-02" not in task:
        errors.append("HUNT-01 task must recommend HUNT-02")
    if "Search Hunt UI state in Local Workbench" not in next_task:
        errors.append("HUNT-02 task title mismatch")
    if "current_recommended_task: F0-00" in queue:
        errors.append("F0 must not be current")


def validate_report(report: Mapping[str, Any], errors: list[str]) -> None:
    if report.get("recommended_next_task") != "HUNT-02 \u2014 Search Hunt UI state in Local Workbench":
        errors.append("HUNT-01 report must recommend HUNT-02")
    for key in (
        "runtime_package_added",
        "sqlite_store_added",
        "store_added_to_instance_manifest",
        "cli_added",
        "demo_added",
        "validator_added",
        "session_create_passed",
        "session_list_show_passed",
        "valid_transitions_passed",
        "invalid_transitions_rejected",
        "transition_history_recorded",
        "reviewed_index_search_summary_passed",
        "local_absence_summary_passed",
    ):
        if report.get(key) is not True:
            errors.append(f"HUNT-01 report {key} must be true")
    for key in (
        "workunit_creation_performed",
        "source_probe_executed",
        "external_network_used",
        "model_provider_used",
        "review_mutation_performed",
        "public_index_mutated",
        "master_index_mutated",
        "deployment_performed",
        "production_readiness_claimed",
        "public_launch_readiness_claimed",
    ):
        if report.get(key) is not False:
            errors.append(f"HUNT-01 report {key} must be false")


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
