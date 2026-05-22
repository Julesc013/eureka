#!/usr/bin/env python3
"""Validate HUNT-03 Search Hunt command and steering controls."""

from __future__ import annotations

import argparse
import ast
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.hunt_queue_progress import (
    hunt_latest_packet_current_or_advanced,
    hunt_queue_current_or_advanced,
    post_hunt_current_allowed,
)
from runtime.local_appliance import close_local_appliance, open_local_appliance
from runtime.local_operator.auth import build_cli_operator_auth_state
from runtime.local_service import LocalServiceApp
from runtime.search_hunt import SearchHuntError


TASK_ID = "HUNT-03"
NEXT_TASK = "HUNT-04"
COMMAND_TYPES = (
    "pause",
    "resume",
    "cancel",
    "block",
    "wait_for_user",
    "wait_for_policy",
    "complete",
    "fail",
)
STEERING_TYPES = (
    "include_source_family",
    "exclude_source_family",
    "prefer_official_sources",
    "allow_community_sources",
    "metadata_only",
    "allow_extraction_future",
    "disallow_extraction",
    "allow_ai_escalation_future",
    "disallow_ai_escalation",
    "add_note",
    "set_priority",
)
POLICIES = {
    "control/policies/search_hunt_command_policy.json": "search_hunt_command_policy.v0",
    "control/policies/search_hunt_steering_policy.json": "search_hunt_steering_policy.v0",
    "control/policies/search_hunt_command_auth_policy.json": "search_hunt_command_auth_policy.v0",
    "control/policies/search_hunt_command_side_effect_policy.json": "search_hunt_command_side_effect_policy.v0",
    "control/policies/search_hunt_lan_command_policy.json": "search_hunt_lan_command_policy.v0",
}
INVENTORIES = {
    "control/inventory/search_hunt_command_inventory.json": "search_hunt_command_inventory.v0",
    "control/inventory/search_hunt_command_matrix.json": "search_hunt_command_matrix.v0",
    "control/inventory/search_hunt_steering_matrix.json": "search_hunt_steering_matrix.v0",
    "control/inventory/search_hunt_command_result.json": "search_hunt_command_result.v0",
    "control/inventory/search_hunt_command_demo_result.json": "search_hunt_command_demo_result.v0",
    "control/inventory/search_hunt_command_gap_register.json": "search_hunt_command_gap_register.v0",
    "control/inventory/hunt_03_next_task_decision.json": "hunt_03_next_task_decision.v0",
}
RUNTIME_FILES = (
    "runtime/search_hunt/commands.py",
    "runtime/search_hunt/steering.py",
    "runtime/search_hunt/store.py",
    "runtime/search_hunt/schema.py",
    "runtime/search_hunt/queries.py",
    "runtime/search_hunt/validation.py",
    "runtime/local_service/routes.py",
    "runtime/local_service/validation.py",
    "surfaces/web/workbench/local_html/pages.py",
    "surfaces/web/workbench/local_html/view_models.py",
    "runtime/local_operator/auth.py",
)
SCRIPTS = (
    "scripts/eureka_search_hunt_command.py",
    "scripts/demo_search_hunt_commands.py",
    "scripts/validate_search_hunt_commands.py",
)
DOCS = (
    "docs/architecture/SEARCH_HUNT_COMMANDS.md",
    "docs/reference/SEARCH_HUNT_COMMAND_API.md",
    "docs/reference/SEARCH_HUNT_STEERING_MODEL.md",
    "docs/operations/SEARCH_HUNT_COMMAND_RUNBOOK.md",
    "docs/operations/SEARCH_HUNT_COMMAND_BOUNDARIES.md",
)
TESTS = (
    "tests/runtime/test_search_hunt_commands.py",
    "tests/runtime/test_search_hunt_steering.py",
    "tests/runtime/test_search_hunt_command_routes.py",
    "tests/runtime/test_search_hunt_command_ui.py",
    "tests/runtime/test_search_hunt_command_auth.py",
    "tests/operations/test_search_hunt_command_scripts.py",
)
AUDIT_ROOT = Path("control/audits/hunt-03-search-hunt-commands-v0")
AUDIT_FILES = (
    "README.md",
    "hunt_03_report.json",
    "command_summary.md",
    "steering_summary.md",
    "auth_boundary.md",
    "side_effect_boundary.md",
    "route_matrix.md",
    "ui_summary.md",
    "demo_result.md",
    "validation.md",
    "generated/sample_hunt_command.json",
    "generated/sample_hunt_command_history.json",
    "generated/sample_steering_preferences.json",
    "generated/sample_hunt_detail_with_controls.html",
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
FORBIDDEN_RUNTIME_VOCABULARY = ("HUNT-03", "HUNT-04", "LOCAL-", "AIDE", "BUNDLE")


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
        print("HUNT-03 Search Hunt command validation", file=stdout)
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
    report = load_json(root / AUDIT_ROOT / "hunt_03_report.json", "hunt_03_report.v0", errors)
    validate_files(root, errors)
    validate_policies(payloads, errors)
    validate_inventories(payloads, errors)
    validate_report(report, errors)
    validate_runtime_imports(root, errors)
    validate_runtime_vocabulary(root, errors)
    behavior = validate_behavior(root, errors)
    validate_cli_and_demo(root, errors)
    validate_queue(root, errors)
    status = "fail" if errors else ("pass_with_warnings" if warnings else "pass")
    return {
        "schema_version": "search_hunt_command_validation.v0",
        "task": TASK_ID,
        "status": status,
        "errors": errors,
        "warnings": warnings,
        **behavior,
        "validator_added": True,
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


def validate_files(root: Path, errors: list[str]) -> None:
    for rel in (*RUNTIME_FILES, *SCRIPTS, *DOCS, *TESTS):
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
    command = payloads.get("control/policies/search_hunt_command_policy.json", {})
    for key in ("commands_enabled", "command_history_required", "operator_token_required_for_mutations", "localhost_only_mutations"):
        if command.get(key) is not True:
            errors.append(f"command policy {key} must be true")
    for key in (
        "lan_mutations_enabled",
        "workunit_creation_enabled",
        "source_probe_execution_enabled",
        "extraction_execution_enabled",
        "model_provider_enabled",
        "public_index_mutation_enabled",
        "master_index_mutation_enabled",
        "deployment_enabled",
        "production_readiness_claimed",
        "public_launch_readiness_claimed",
    ):
        if command.get(key) is not False:
            errors.append(f"command policy {key} must be false")

    steering = payloads.get("control/policies/search_hunt_steering_policy.json", {})
    if tuple(steering.get("allowed_steering_command_types", [])) != STEERING_TYPES:
        errors.append("steering policy command types mismatch")
    for key in (
        "steering_preferences_do_not_execute_work",
        "steering_preferences_do_not_approve_sources",
        "steering_preferences_do_not_accept_truth",
        "steering_preferences_do_not_mutate_index",
        "steering_preferences_feed_future_HUNT_06_WORKUNITS",
    ):
        if steering.get(key) is not True:
            errors.append(f"steering policy {key} must be true")

    auth = payloads.get("control/policies/search_hunt_command_auth_policy.json", {})
    for key in (
        "operator_token_required",
        "raw_token_storage_forbidden",
        "token_logging_forbidden",
        "localhost_only_current_task",
        "lan_command_mutations_forbidden",
        "missing_token_rejected",
        "invalid_token_rejected",
    ):
        if auth.get(key) is not True:
            errors.append(f"auth policy {key} must be true")

    side_effect = payloads.get("control/policies/search_hunt_command_side_effect_policy.json", {})
    for key in ("hunt_state_mutation_allowed", "hunt_command_history_mutation_allowed", "hunt_steering_mutation_allowed"):
        if side_effect.get(key) is not True:
            errors.append(f"side-effect policy {key} must be true")
    for key in (
        "workunit_creation_allowed",
        "source_probe_allowed",
        "extraction_allowed",
        "external_network_allowed",
        "model_provider_allowed",
        "review_decision_allowed",
        "public_index_mutation_allowed",
        "master_index_mutation_allowed",
        "site_dist_writes_allowed",
        "deployment_allowed",
    ):
        if side_effect.get(key) is not False:
            errors.append(f"side-effect policy {key} must be false")

    lan = payloads.get("control/policies/search_hunt_lan_command_policy.json", {})
    for key in ("lan_hunt_mutations_enabled", "lan_pause_resume_enabled", "lan_steering_enabled", "lan_cancel_enabled"):
        if lan.get(key) is not False:
            errors.append(f"LAN command policy {key} must be false")
    for key in ("lan_command_routes_return_403", "lan_read_only_hunt_routes_allowed"):
        if lan.get(key) is not True:
            errors.append(f"LAN command policy {key} must be true")


def validate_inventories(payloads: Mapping[str, Mapping[str, Any]], errors: list[str]) -> None:
    inventory = payloads.get("control/inventory/search_hunt_command_inventory.json", {})
    for key in ("commands_enabled", "steering_enabled", "operator_token_required", "localhost_only_mutations"):
        if inventory.get(key) is not True:
            errors.append(f"command inventory {key} must be true")
    for key in ("lan_mutations_enabled", "workunit_creation_enabled", "source_probe_execution_enabled", "model_provider_enabled", "deployment_performed"):
        if inventory.get(key) is not False:
            errors.append(f"command inventory {key} must be false")

    command_matrix = payloads.get("control/inventory/search_hunt_command_matrix.json", {}).get("commands", [])
    if [item.get("command_type") for item in command_matrix if isinstance(item, Mapping)] != list(COMMAND_TYPES):
        errors.append("command matrix command list mismatch")
    for item in command_matrix:
        if isinstance(item, Mapping):
            if item.get("operator_token_required") is not True or item.get("enabled") is not True:
                errors.append(f"command matrix auth/enabled mismatch for {item.get('command_type')}")
            for key in ("creates_workunit", "runs_source_probe", "calls_model_provider", "mutates_index"):
                if item.get(key) is not False:
                    errors.append(f"command matrix {key} must be false for {item.get('command_type')}")

    steering_matrix = payloads.get("control/inventory/search_hunt_steering_matrix.json", {}).get("steering", [])
    if [item.get("steering_type") for item in steering_matrix if isinstance(item, Mapping)] != list(STEERING_TYPES):
        errors.append("steering matrix type list mismatch")

    result = payloads.get("control/inventory/search_hunt_command_result.json", {})
    for key in (
        "command_runtime_added",
        "steering_runtime_added",
        "command_history_recorded",
        "operator_auth_required",
        "missing_token_rejected",
        "invalid_token_rejected",
        "lan_command_mutation_blocked",
        "pause_resume_passed",
        "cancel_passed",
        "block_wait_commands_passed",
        "steering_preferences_recorded",
        "invalid_commands_rejected",
        "ui_controls_added",
        "cli_added",
        "demo_added",
        "validator_added",
    ):
        if result.get(key) is not True:
            errors.append(f"command result {key} must be true")
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
        if result.get(key) is not False:
            errors.append(f"command result {key} must be false")

    decision = payloads.get("control/inventory/hunt_03_next_task_decision.json", {})
    if decision.get("recommended_next_task") != "HUNT-04 \u2014 Hunt exhaustion report":
        errors.append("HUNT-03 next task decision must point to HUNT-04")
    for key in ("workunit_creation_enabled", "source_probe_execution_enabled", "model_provider_enabled"):
        if decision.get(key) is not False:
            errors.append(f"HUNT-03 decision {key} must be false")


def validate_report(report: Mapping[str, Any], errors: list[str]) -> None:
    if report.get("recommended_next_task") != "HUNT-04 \u2014 Hunt exhaustion report":
        errors.append("HUNT-03 report must recommend HUNT-04")
    for key in (
        "command_runtime_added",
        "steering_runtime_added",
        "command_history_recorded",
        "operator_auth_required",
        "missing_token_rejected",
        "invalid_token_rejected",
        "lan_command_mutation_blocked",
        "pause_resume_passed",
        "cancel_passed",
        "block_wait_commands_passed",
        "steering_preferences_recorded",
        "invalid_commands_rejected",
        "ui_controls_added",
        "cli_added",
        "demo_added",
        "validator_added",
    ):
        if report.get(key) is not True:
            errors.append(f"HUNT-03 report {key} must be true")
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
            errors.append(f"HUNT-03 report {key} must be false")


def validate_behavior(root: Path, errors: list[str]) -> dict[str, bool]:
    result = {
        "command_runtime_added": False,
        "steering_runtime_added": False,
        "command_history_recorded": False,
        "operator_auth_required": False,
        "missing_token_rejected": False,
        "invalid_token_rejected": False,
        "lan_command_mutation_blocked": False,
        "pause_resume_passed": False,
        "cancel_passed": False,
        "block_wait_commands_passed": False,
        "steering_preferences_recorded": False,
        "invalid_commands_rejected": False,
        "ui_controls_added": False,
    }
    with tempfile.TemporaryDirectory(prefix="eureka-search-hunt-command-") as tmp:
        instance = Path(tmp) / "eureka-instance"
        init = run(root, "python", "scripts/eureka_init_instance.py", "--instance", str(instance), "--json")
        if init.returncode != 0:
            errors.append(f"temp instance init failed: {init.stdout}{init.stderr}")
            return result
        runtime = open_local_appliance(instance, read_only=False)
        try:
            before_work = runtime.workunit_queue.summarize().to_dict()
            before_public = runtime.public_index.summarize().to_dict()
            hunt = runtime.search_hunt.create_session_from_query("sampleproject", runtime=runtime)
            wait_user = runtime.search_hunt.create_session_from_query("wait-user", runtime=runtime)
            wait_policy = runtime.search_hunt.create_session_from_query("wait-policy", runtime=runtime)
            block_hunt = runtime.search_hunt.create_session_from_query("block", runtime=runtime)
            cancel_hunt = runtime.search_hunt.create_session_from_query("cancel", runtime=runtime)
            runtime.search_hunt.transition_session(wait_user.id, "running", "prepare")
            runtime.search_hunt.transition_session(wait_policy.id, "running", "prepare")

            pause = runtime.search_hunt.apply_command(hunt.id, "pause", reason="validator")
            resume = runtime.search_hunt.apply_command(hunt.id, "resume", reason="validator")
            cancel = runtime.search_hunt.apply_command(cancel_hunt.id, "cancel", reason="validator")
            block = runtime.search_hunt.apply_command(block_hunt.id, "block", reason="validator")
            wait1 = runtime.search_hunt.apply_command(wait_user.id, "wait_for_user", reason="validator")
            wait2 = runtime.search_hunt.apply_command(wait_policy.id, "wait_for_policy", reason="validator")
            preference = runtime.search_hunt.add_steering_preference(hunt.id, "metadata_only", reason="validator")
            deactivated = runtime.search_hunt.remove_steering_preference(hunt.id, preference.id, reason="validator")

            invalid_rejected = False
            try:
                runtime.search_hunt.apply_command(hunt.id, "not_valid")
            except (SearchHuntError, ValueError):
                invalid_rejected = True

            app = LocalServiceApp(runtime, operator_auth_state=build_cli_operator_auth_state("validator-token"))
            missing = app.handle("POST", f"/hunt/{hunt.id}/pause", body="reason=missing")
            invalid = app.handle("POST", f"/hunt/{hunt.id}/pause", body="operator_token=wrong&reason=invalid")
            lan = app.handle("POST", f"/hunt/{hunt.id}/pause", client_host="192.168.1.30", body="operator_token=validator-token&reason=lan")
            command_route = app.handle("GET", f"/api/v1/hunt/{hunt.id}/commands")
            detail = app.handle("GET", f"/hunt/{hunt.id}")

            after_work = runtime.workunit_queue.summarize().to_dict()
            after_public = runtime.public_index.summarize().to_dict()
            result.update(
                {
                    "command_runtime_added": hasattr(runtime.search_hunt, "apply_command"),
                    "steering_runtime_added": hasattr(runtime.search_hunt, "add_steering_preference"),
                    "command_history_recorded": command_route.status_code == 200 and command_route.payload.get("command_count", 0) >= 4,
                    "operator_auth_required": missing.status_code == 401,
                    "missing_token_rejected": missing.status_code == 401,
                    "invalid_token_rejected": invalid.status_code == 401,
                    "lan_command_mutation_blocked": lan.status_code == 403,
                    "pause_resume_passed": pause.command.resulting_state == "paused" and resume.command.resulting_state == "running",
                    "cancel_passed": cancel.command.resulting_state == "cancelled",
                    "block_wait_commands_passed": block.command.resulting_state == "blocked" and wait1.command.resulting_state == "waiting_for_user" and wait2.command.resulting_state == "waiting_for_policy",
                    "steering_preferences_recorded": preference.active is True and deactivated.active is False,
                    "invalid_commands_rejected": invalid_rejected,
                    "ui_controls_added": detail.status_code == 200 and "Operator state controls" in detail.body and "Steering preferences" in detail.body,
                }
            )
            if before_work != after_work:
                errors.append("Search Hunt commands created WorkUnit records")
            if before_public != after_public:
                errors.append("Search Hunt commands mutated public index")
            if runtime.search_hunt.check_integrity().get("status") != "pass":
                errors.append("search_hunt command integrity failed")
        finally:
            close_local_appliance(runtime)
    for key, value in result.items():
        if value is not True:
            errors.append(f"behavior check failed: {key}")
    return result


def validate_cli_and_demo(root: Path, errors: list[str]) -> None:
    with tempfile.TemporaryDirectory(prefix="eureka-search-hunt-command-cli-") as tmp:
        instance = Path(tmp) / "eureka-instance"
        init = run(root, "python", "scripts/eureka_init_instance.py", "--instance", str(instance), "--json")
        token = run(root, "python", "scripts/eureka_set_operator_token.py", "--instance", str(instance), "--token", "validator-token", "--json")
        if init.returncode != 0 or token.returncode != 0:
            errors.append("command CLI temp instance setup failed")
            return
        create = run(root, "python", "scripts/eureka_search_hunt.py", "--instance", str(instance), "create", "--query", "sampleproject", "--json")
        if create.returncode != 0:
            errors.append(f"command CLI hunt creation failed: {create.stdout}{create.stderr}")
            return
        hunt_id = json.loads(create.stdout)["session"]["id"]
        commands = (
            ("CLI pause", run(root, "python", "scripts/eureka_search_hunt_command.py", "--instance", str(instance), "--operator-token", "validator-token", "pause", "--id", hunt_id, "--reason", "validator", "--json")),
            ("CLI resume", run(root, "python", "scripts/eureka_search_hunt_command.py", "--instance", str(instance), "--operator-token", "validator-token", "resume", "--id", hunt_id, "--reason", "validator", "--json")),
            ("CLI steer", run(root, "python", "scripts/eureka_search_hunt_command.py", "--instance", str(instance), "--operator-token", "validator-token", "steer", "--id", hunt_id, "--type", "metadata_only", "--json")),
            ("CLI commands", run(root, "python", "scripts/eureka_search_hunt_command.py", "--instance", str(instance), "commands", "--id", hunt_id, "--json")),
            ("demo", run(root, "python", "scripts/demo_search_hunt_commands.py", "--instance", str(instance), "--operator-token", "validator-token", "--json")),
        )
        for label, completed in commands:
            if completed.returncode != 0:
                errors.append(f"{label} failed: {completed.stdout}{completed.stderr}")


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
                if any(module == prefix or module.startswith(prefix + ".") for prefix in FORBIDDEN_IMPORT_PREFIXES):
                    errors.append(f"forbidden import in {rel}: {module}")


def validate_runtime_vocabulary(root: Path, errors: list[str]) -> None:
    for rel in RUNTIME_FILES:
        text = (root / rel).read_text(encoding="utf-8")
        for token in FORBIDDEN_RUNTIME_VOCABULARY:
            if token in text:
                errors.append(f"forbidden runtime vocabulary in {rel}: {token}")


def validate_queue(root: Path, errors: list[str]) -> None:
    queue = read_text(root / ".aide/queue/index.yaml", errors)
    task = read_text(root / ".aide/queue/HUNT-03/task.yaml", errors)
    next_task = read_text(root / ".aide/queue/HUNT-04/task.yaml", errors)
    packet = read_text(root / ".aide/context/latest-task-packet.md", errors)
    if not hunt_queue_current_or_advanced(root, TASK_ID, NEXT_TASK):
        errors.append("queue index must point to HUNT-04 or a later HUNT task")
    if not re.search(r"id: HUNT-03\b[\s\S]*?status: completed", queue):
        errors.append("queue index must mark HUNT-03 completed")
    if "id: HUNT-04" not in queue:
        errors.append("queue index must include HUNT-04")
    if "recommended_next: HUNT-04" not in task:
        errors.append("HUNT-03 task must recommend HUNT-04")
    if "Hunt exhaustion report" not in next_task:
        errors.append("HUNT-04 task title mismatch")
    if not hunt_latest_packet_current_or_advanced(root, TASK_ID, NEXT_TASK):
        errors.append("latest task packet must point to HUNT-04 or a later HUNT task")
    if (
        "current_recommended_task: F0-00" in queue or "current_recommended_task: SYN-00" in queue
    ) and not post_hunt_current_allowed(root):
        errors.append("F0/SYN must not be current")


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
