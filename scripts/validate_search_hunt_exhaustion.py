#!/usr/bin/env python3
"""Validate local Search Hunt exhaustion reports."""

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


REPO_ROOT = Path(__file__).resolve().parents[1]
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
from runtime.search_hunt import build_hunt_exhaustion_report


TASK_ID = "HUNT-04"
NEXT_TASK = "HUNT-05"
POLICIES = {
    "control/policies/search_hunt_exhaustion_policy.json": "search_hunt_exhaustion_policy.v0",
    "control/policies/search_hunt_exhaustion_report_policy.json": "search_hunt_exhaustion_report_policy.v0",
    "control/policies/search_hunt_exhaustion_auth_policy.json": "search_hunt_exhaustion_auth_policy.v0",
    "control/policies/search_hunt_exhaustion_side_effect_policy.json": "search_hunt_exhaustion_side_effect_policy.v0",
    "control/policies/search_hunt_exhaustion_non_claim_policy.json": "search_hunt_exhaustion_non_claim_policy.v0",
}
INVENTORIES = {
    "control/inventory/search_hunt_exhaustion_inventory.json": "search_hunt_exhaustion_inventory.v0",
    "control/inventory/search_hunt_exhaustion_section_matrix.json": "search_hunt_exhaustion_section_matrix.v0",
    "control/inventory/search_hunt_exhaustion_result.json": "search_hunt_exhaustion_result.v0",
    "control/inventory/search_hunt_exhaustion_demo_result.json": "search_hunt_exhaustion_demo_result.v0",
    "control/inventory/search_hunt_exhaustion_gap_register.json": "search_hunt_exhaustion_gap_register.v0",
    "control/inventory/hunt_04_next_task_decision.json": "hunt_04_next_task_decision.v0",
}
RUNTIME_FILES = (
    "runtime/search_hunt/exhaustion.py",
    "runtime/search_hunt/reports.py",
    "runtime/search_hunt/records.py",
    "runtime/search_hunt/store.py",
    "runtime/search_hunt/schema.py",
    "runtime/search_hunt/queries.py",
    "runtime/search_hunt/validation.py",
    "runtime/local_service/routes.py",
    "runtime/local_service/validation.py",
    "runtime/local_workbench/pages.py",
    "runtime/local_workbench/view_models.py",
)
SCRIPTS = (
    "scripts/eureka_search_hunt_exhaustion.py",
    "scripts/demo_search_hunt_exhaustion.py",
    "scripts/validate_search_hunt_exhaustion.py",
)
DOCS = (
    "docs/architecture/SEARCH_HUNT_EXHAUSTION_REPORT.md",
    "docs/reference/SEARCH_HUNT_EXHAUSTION_REPORT_RECORD.md",
    "docs/reference/SEARCH_HUNT_EXHAUSTION_API.md",
    "docs/operations/SEARCH_HUNT_EXHAUSTION_RUNBOOK.md",
    "docs/operations/SEARCH_HUNT_EXHAUSTION_BOUNDARIES.md",
)
TESTS = (
    "tests/runtime/test_search_hunt_exhaustion.py",
    "tests/runtime/test_search_hunt_exhaustion_reports.py",
    "tests/runtime/test_search_hunt_exhaustion_routes.py",
    "tests/runtime/test_search_hunt_exhaustion_ui.py",
    "tests/runtime/test_search_hunt_exhaustion_auth.py",
    "tests/operations/test_search_hunt_exhaustion_scripts.py",
)
AUDIT_ROOT = Path("control/audits/hunt-04-hunt-exhaustion-report-v0")
AUDIT_FILES = (
    "README.md",
    "hunt_04_report.json",
    "exhaustion_report_summary.md",
    "section_matrix.md",
    "auth_boundary.md",
    "side_effect_boundary.md",
    "ui_summary.md",
    "demo_result.md",
    "validation.md",
    "generated/sample_exhaustion_report.json",
    "generated/sample_hunt_detail_with_exhaustion.html",
    "generated/sample_exhaustion_response.json",
    "generated/sample_demo_result.json",
    "generated/sample_summary.md",
)
REQUIRED_SECTIONS = (
    "query_summary",
    "checked_layers",
    "result_state",
    "unchecked_or_deferred_layers",
    "blocked_by_policy",
    "recommended_next_actions",
    "limitations",
    "warnings",
    "non_claims",
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
FORBIDDEN_RUNTIME_VOCABULARY = ("HUNT-", "LOCAL-", "AIDE", "BUNDLE")


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
        print("HUNT-04 Search Hunt exhaustion validation", file=stdout)
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
    report = load_json(root / AUDIT_ROOT / "hunt_04_report.json", "hunt_04_report.v0", errors)
    validate_files(root, errors)
    validate_policy_payloads(payloads, errors)
    validate_inventory_payloads(payloads, errors)
    validate_report_payload(report, errors)
    validate_runtime_imports(root, errors)
    validate_runtime_vocabulary(root, errors)
    behavior = validate_behavior(root, errors)
    validate_cli_and_demo(root, errors)
    validate_queue(root, errors)
    status = "fail" if errors else ("pass_with_warnings" if warnings else "pass")
    return {
        "schema_version": "search_hunt_exhaustion_validation.v0",
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


def validate_policy_payloads(payloads: Mapping[str, Mapping[str, Any]], errors: list[str]) -> None:
    policy = payloads.get("control/policies/search_hunt_exhaustion_policy.json", {})
    for key in (
        "exhaustion_reports_enabled",
        "operator_token_required_for_generation",
        "localhost_only_generation",
        "read_only_view_enabled",
        "local_reviewed_index_only",
    ):
        if policy.get(key) is not True:
            errors.append(f"exhaustion policy {key} must be true")
    for key in (
        "lan_generation_enabled",
        "workunit_creation_enabled",
        "source_probe_execution_enabled",
        "extraction_execution_enabled",
        "model_provider_enabled",
        "sync_enabled",
        "public_index_mutation_enabled",
        "master_index_mutation_enabled",
        "deployment_enabled",
        "production_readiness_claimed",
        "public_launch_readiness_claimed",
    ):
        if policy.get(key) is not False:
            errors.append(f"exhaustion policy {key} must be false")

    report = payloads.get("control/policies/search_hunt_exhaustion_report_policy.json", {})
    if tuple(report.get("required_sections", [])) != REQUIRED_SECTIONS:
        errors.append("exhaustion report policy required sections mismatch")
    for key in (
        "no_global_absence_claim",
        "local_current_index_absence_only",
        "source_coverage_not_claimed",
        "rights_safety_not_claimed",
        "production_public_not_claimed",
    ):
        if report.get(key) is not True:
            errors.append(f"exhaustion report policy {key} must be true")

    auth = payloads.get("control/policies/search_hunt_exhaustion_auth_policy.json", {})
    for key in (
        "generation_requires_operator_token",
        "read_routes_do_not_require_token",
        "raw_token_storage_forbidden",
        "token_logging_forbidden",
        "localhost_only_generation",
        "lan_generation_forbidden",
        "missing_token_rejected",
        "invalid_token_rejected",
    ):
        if auth.get(key) is not True:
            errors.append(f"exhaustion auth policy {key} must be true")

    side_effect = payloads.get("control/policies/search_hunt_exhaustion_side_effect_policy.json", {})
    for key in ("hunt_exhaustion_record_mutation_allowed", "hunt_command_history_mutation_allowed_for_report_generation"):
        if side_effect.get(key) is not True:
            errors.append(f"exhaustion side-effect policy {key} must be true")
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
            errors.append(f"exhaustion side-effect policy {key} must be false")

    non_claim = payloads.get("control/policies/search_hunt_exhaustion_non_claim_policy.json", {})
    for claim in (
        "artifact_does_not_exist",
        "exhaustive_search_performed",
        "all_sources_checked",
        "source_truth_accepted",
        "evidence_truth_accepted",
        "rights_cleared",
        "malware_safe",
        "production_ready",
        "public_launch_ready",
        "ai_verified_result",
    ):
        if claim not in non_claim.get("forbidden_claims", []):
            errors.append(f"missing forbidden exhaustion claim: {claim}")


def validate_inventory_payloads(payloads: Mapping[str, Mapping[str, Any]], errors: list[str]) -> None:
    inventory = payloads.get("control/inventory/search_hunt_exhaustion_inventory.json", {})
    for key in ("exhaustion_reports_enabled", "operator_token_required_for_generation", "localhost_only_generation"):
        if inventory.get(key) is not True:
            errors.append(f"exhaustion inventory {key} must be true")
    for key in ("lan_generation_enabled", "workunit_creation_enabled", "source_probe_execution_enabled", "model_provider_enabled", "deployment_performed"):
        if inventory.get(key) is not False:
            errors.append(f"exhaustion inventory {key} must be false")
    if tuple(inventory.get("required_sections", [])) != REQUIRED_SECTIONS:
        errors.append("exhaustion inventory required sections mismatch")

    section_matrix = payloads.get("control/inventory/search_hunt_exhaustion_section_matrix.json", {}).get("sections", [])
    if [item.get("section") for item in section_matrix if isinstance(item, Mapping)] != list(REQUIRED_SECTIONS):
        errors.append("exhaustion section matrix mismatch")

    result = payloads.get("control/inventory/search_hunt_exhaustion_result.json", {})
    validate_result_flags("exhaustion result", result, errors)
    decision = payloads.get("control/inventory/hunt_04_next_task_decision.json", {})
    if decision.get("recommended_next_task") != "HUNT-05 \u2014 Hunt-to-SearchNeed pipeline":
        errors.append("HUNT-04 next task decision must point to HUNT-05")
    for key in ("workunit_creation_enabled", "source_probe_execution_enabled", "model_provider_enabled"):
        if decision.get(key) is not False:
            errors.append(f"HUNT-04 decision {key} must be false")


def validate_report_payload(report: Mapping[str, Any], errors: list[str]) -> None:
    if report.get("recommended_next_task") != "HUNT-05 \u2014 Hunt-to-SearchNeed pipeline":
        errors.append("HUNT-04 report must recommend HUNT-05")
    validate_result_flags("HUNT-04 report", report, errors)


def validate_result_flags(label: str, payload: Mapping[str, Any], errors: list[str]) -> None:
    for key in (
        "exhaustion_runtime_added",
        "exhaustion_store_added",
        "cli_added",
        "demo_added",
        "validator_added",
        "query_summary_present",
        "checked_layers_present",
        "result_state_present",
        "unchecked_deferred_layers_present",
        "blocked_by_policy_present",
        "recommended_next_actions_present",
        "limitations_present",
        "non_claims_present",
        "operator_auth_required_for_generation",
        "missing_token_rejected",
        "invalid_token_rejected",
        "lan_generation_blocked",
        "ui_section_added",
    ):
        if payload.get(key) is not True:
            errors.append(f"{label} {key} must be true")
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
        if payload.get(key) is not False:
            errors.append(f"{label} {key} must be false")


def validate_behavior(root: Path, errors: list[str]) -> dict[str, bool]:
    result = {
        "exhaustion_runtime_added": False,
        "exhaustion_store_added": False,
        "query_summary_present": False,
        "checked_layers_present": False,
        "result_state_present": False,
        "unchecked_deferred_layers_present": False,
        "blocked_by_policy_present": False,
        "recommended_next_actions_present": False,
        "limitations_present": False,
        "non_claims_present": False,
        "operator_auth_required_for_generation": False,
        "missing_token_rejected": False,
        "invalid_token_rejected": False,
        "lan_generation_blocked": False,
        "ui_section_added": False,
    }
    with tempfile.TemporaryDirectory(prefix="eureka-search-hunt-exhaustion-") as tmp:
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
            runtime.search_hunt.add_steering_preference(hunt.id, "metadata_only", reason="validator")
            report = build_hunt_exhaustion_report(runtime, hunt.id, operator_label="validator")
            attached = runtime.search_hunt.attach_exhaustion_report(hunt.id, report)
            payload = attached.to_dict()
            latest = runtime.search_hunt.get_latest_exhaustion_report(hunt.id)
            app = LocalServiceApp(runtime, operator_auth_state=build_cli_operator_auth_state("validator-token"))
            missing = app.handle("POST", f"/hunt/{hunt.id}/exhaustion", body="operator_label=missing")
            invalid = app.handle("POST", f"/hunt/{hunt.id}/exhaustion", body="operator_token=wrong")
            lan = app.handle("POST", f"/hunt/{hunt.id}/exhaustion", client_host="192.168.1.30", body="operator_token=validator-token")
            route = app.handle("GET", f"/api/v1/hunt/{hunt.id}/exhaustion")
            generated = app.handle("POST", f"/hunt/{hunt.id}/exhaustion", body="operator_token=validator-token&operator_label=route")
            detail = app.handle("GET", f"/hunt/{hunt.id}")
            after_work = runtime.workunit_queue.summarize().to_dict()
            after_public = runtime.public_index.summarize().to_dict()
            result.update(
                {
                    "exhaustion_runtime_added": callable(build_hunt_exhaustion_report),
                    "exhaustion_store_added": latest is not None and latest.report_id == attached.report_id,
                    "query_summary_present": bool(payload.get("query_summary")),
                    "checked_layers_present": bool(payload.get("checked_layers")),
                    "result_state_present": bool(payload.get("result_state")),
                    "unchecked_deferred_layers_present": bool(payload.get("unchecked_or_deferred_layers")),
                    "blocked_by_policy_present": bool(payload.get("blocked_by_policy")),
                    "recommended_next_actions_present": bool(payload.get("recommended_next_actions")),
                    "limitations_present": bool(payload.get("limitations")),
                    "non_claims_present": bool(payload.get("non_claims")),
                    "operator_auth_required_for_generation": missing.status_code == 401,
                    "missing_token_rejected": missing.status_code == 401,
                    "invalid_token_rejected": invalid.status_code == 401,
                    "lan_generation_blocked": lan.status_code == 403,
                    "ui_section_added": detail.status_code == 200 and "Exhaustion report" in detail.body,
                }
            )
            if route.status_code != 200 or not route.payload.get("exhaustion_report"):
                errors.append("exhaustion GET route failed")
            if generated.status_code != 200 or not generated.payload.get("exhaustion_report"):
                errors.append("exhaustion POST route failed")
            if before_work != after_work:
                errors.append("exhaustion report generated WorkUnit records")
            if before_public != after_public:
                errors.append("exhaustion report mutated public index")
            if runtime.search_hunt.check_integrity().get("status") != "pass":
                errors.append("search_hunt exhaustion integrity failed")
        finally:
            close_local_appliance(runtime)
    for key, value in result.items():
        if value is not True:
            errors.append(f"behavior check failed: {key}")
    return result


def validate_cli_and_demo(root: Path, errors: list[str]) -> None:
    with tempfile.TemporaryDirectory(prefix="eureka-search-hunt-exhaustion-cli-") as tmp:
        instance = Path(tmp) / "eureka-instance"
        init = run(root, "python", "scripts/eureka_init_instance.py", "--instance", str(instance), "--json")
        token = run(root, "python", "scripts/eureka_set_operator_token.py", "--instance", str(instance), "--token", "validator-token", "--json")
        if init.returncode != 0 or token.returncode != 0:
            errors.append("exhaustion CLI temp instance setup failed")
            return
        create = run(root, "python", "scripts/eureka_search_hunt.py", "--instance", str(instance), "create", "--query", "sampleproject", "--json")
        if create.returncode != 0:
            errors.append(f"exhaustion CLI hunt creation failed: {create.stdout}{create.stderr}")
            return
        hunt_id = json.loads(create.stdout)["session"]["id"]
        commands = (
            ("CLI generate", run(root, "python", "scripts/eureka_search_hunt_exhaustion.py", "--instance", str(instance), "--operator-token", "validator-token", "--id", hunt_id, "--generate", "--json")),
            ("CLI show", run(root, "python", "scripts/eureka_search_hunt_exhaustion.py", "--instance", str(instance), "--id", hunt_id, "--show", "--json")),
            ("demo", run(root, "python", "scripts/demo_search_hunt_exhaustion.py", "--instance", str(instance), "--operator-token", "validator-token", "--json")),
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
    task = read_text(root / ".aide/queue/HUNT-04/task.yaml", errors)
    next_task = read_text(root / ".aide/queue/HUNT-05/task.yaml", errors)
    packet = read_text(root / ".aide/context/latest-task-packet.md", errors)
    if not hunt_queue_current_or_advanced(root, TASK_ID, NEXT_TASK):
        errors.append("queue index must point to HUNT-05 or a later HUNT task")
    if not re.search(r"id: HUNT-04\b[\s\S]*?status: completed", queue):
        errors.append("queue index must mark HUNT-04 completed")
    if "id: HUNT-05" not in queue:
        errors.append("queue index must include HUNT-05")
    if "recommended_next: HUNT-05" not in task:
        errors.append("HUNT-04 task must recommend HUNT-05")
    if "Hunt-to-SearchNeed pipeline" not in next_task:
        errors.append("HUNT-05 task title mismatch")
    if not hunt_latest_packet_current_or_advanced(root, TASK_ID, NEXT_TASK):
        errors.append("latest task packet must point to HUNT-05 or a later HUNT task")
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
