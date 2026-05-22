#!/usr/bin/env python3
"""Validate the HUNT-11 disabled AI escalation gate."""

from __future__ import annotations

import argparse
import ast
import json
import sys
import tempfile
from pathlib import Path
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.hunt_queue_progress import hunt_queue_current_or_advanced
from runtime.ai_escalation import (
    ALLOWED_AI_ESCALATION_FORBIDDEN_ACTIONS,
    ALLOWED_AI_ESCALATION_OUTPUT_CLASSES,
    build_ai_escalation_preflight,
    create_ai_escalation_gate,
    validate_ai_escalation_gate,
    validate_preflight,
)
from runtime.local_appliance import close_local_appliance, open_local_appliance
from runtime.local_operator import write_operator_token_record
from runtime.local_service import LocalServiceApp
from runtime.search_hunt import build_hunt_exhaustion_report
from scripts.eureka_init_instance import initialize_instance


TASK_ID = "HUNT-11"
NEXT_TASK = "HUNT-12"
POLICIES = {
    "control/policies/ai_escalation_gate_policy.json": "ai_escalation_gate_policy.v0",
    "control/policies/ai_escalation_provider_disabled_policy.json": "ai_escalation_provider_disabled_policy.v0",
    "control/policies/ai_escalation_input_policy.json": "ai_escalation_input_policy.v0",
    "control/policies/ai_escalation_output_policy.json": "ai_escalation_output_policy.v0",
    "control/policies/ai_escalation_side_effect_policy.json": "ai_escalation_side_effect_policy.v0",
    "control/policies/ai_escalation_non_claim_policy.json": "ai_escalation_non_claim_policy.v0",
}
INVENTORIES = {
    "control/inventory/ai_escalation_gate_inventory.json": "ai_escalation_gate_inventory.v0",
    "control/inventory/ai_escalation_gate_state_machine.json": "ai_escalation_gate_state_machine.v0",
    "control/inventory/ai_escalation_input_matrix.json": "ai_escalation_input_matrix.v0",
    "control/inventory/ai_escalation_output_matrix.json": "ai_escalation_output_matrix.v0",
    "control/inventory/ai_escalation_disabled_boundary_result.json": "ai_escalation_disabled_boundary_result.v0",
    "control/inventory/ai_escalation_gate_result.json": "ai_escalation_gate_result.v0",
    "control/inventory/ai_escalation_demo_result.json": "ai_escalation_demo_result.v0",
    "control/inventory/ai_escalation_gap_register.json": "ai_escalation_gap_register.v0",
    "control/inventory/hunt_11_next_task_decision.json": "hunt_11_next_task_decision.v0",
}
RUNTIME_FILES = (
    "runtime/ai_escalation/__init__.py",
    "runtime/ai_escalation/schema.py",
    "runtime/ai_escalation/records.py",
    "runtime/ai_escalation/store.py",
    "runtime/ai_escalation/gate.py",
    "runtime/ai_escalation/eligibility.py",
    "runtime/ai_escalation/preflight.py",
    "runtime/ai_escalation/validation.py",
    "runtime/ai_escalation/errors.py",
    "runtime/local_appliance/manifest.py",
    "runtime/local_appliance/composition.py",
    "runtime/local_appliance/status.py",
    "runtime/local_service/routes.py",
    "surfaces/web/workbench/local_html/pages.py",
    "surfaces/web/workbench/local_html/view_models.py",
)
SCRIPTS = (
    "scripts/eureka_ai_escalation_gate.py",
    "scripts/demo_ai_escalation_gate.py",
    "scripts/validate_ai_escalation_gate.py",
)
DOCS = (
    "docs/architecture/AI_ESCALATION_GATE.md",
    "docs/reference/AI_ESCALATION_GATE_RECORD.md",
    "docs/reference/AI_ESCALATION_API.md",
    "docs/reference/AI_ESCALATION_INPUT_OUTPUT.md",
    "docs/operations/AI_ESCALATION_DISABLED_BOUNDARY.md",
    "docs/operations/AI_ESCALATION_NON_CLAIMS.md",
    "docs/operations/HUNT_11_TO_CLOSEOUT_HANDOFF.md",
)
TESTS = (
    "tests/runtime/test_ai_escalation_records.py",
    "tests/runtime/test_ai_escalation_store.py",
    "tests/runtime/test_ai_escalation_eligibility.py",
    "tests/runtime/test_ai_escalation_preflight.py",
    "tests/runtime/test_ai_escalation_routes.py",
    "tests/runtime/test_ai_escalation_ui.py",
    "tests/runtime/test_ai_escalation_disabled_boundary.py",
    "tests/operations/test_ai_escalation_scripts.py",
)
AUDIT_ROOT = Path("control/audits/hunt-11-ai-escalation-gate-v0")
AUDIT_FILES = (
    "README.md",
    "hunt_11_report.json",
    "gate_summary.md",
    "eligibility_summary.md",
    "provider_disabled_boundary.md",
    "input_output_matrix.md",
    "side_effect_boundary.md",
    "ui_summary.md",
    "demo_result.md",
    "validation.md",
    "generated/sample_ai_escalation_gate.json",
    "generated/sample_ai_escalation_preflight.json",
    "generated/sample_ai_escalation_page.html",
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
        print("HUNT-11 AI escalation gate validation", file=stdout)
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
    report = load_json(root / AUDIT_ROOT / "hunt_11_report.json", "hunt_11_report.v0", errors)
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
        "schema_version": "ai_escalation_gate_validation.v0",
        "task": TASK_ID,
        "status": status,
        "errors": errors,
        "warnings": warnings,
        **behavior,
        "validator_added": True,
        "model_provider_used": False,
        "external_network_used": False,
        "source_probe_executed": False,
        "extraction_executed": False,
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
    for rel in POLICIES:
        payload = payloads.get(rel, {})
        for key in ("provider_enabled", "execution_enabled", "model_provider_calls_enabled", "browser_calls_enabled", "external_network_enabled", "source_probe_enabled", "extraction_enabled", "public_index_mutation_enabled", "master_index_mutation_enabled"):
            if key in payload and payload.get(key) is not False:
                errors.append(f"{rel} {key} must be false")
        if payload.get("output_candidate_only") is False:
            errors.append(f"{rel} output_candidate_only must not be false")
        if payload.get("review_required") is False:
            errors.append(f"{rel} review_required must not be false")


def validate_inventory_payloads(payloads: Mapping[str, Mapping[str, Any]], errors: list[str]) -> None:
    result = payloads.get("control/inventory/ai_escalation_gate_result.json", {})
    for key in (
        "runtime_package_added",
        "sqlite_store_added",
        "store_added_to_instance_manifest",
        "cli_added",
        "demo_added",
        "validator_added",
        "preflight_from_hunt_passed",
        "preflight_from_need_passed",
        "disabled_gate_created",
        "input_packet_validated",
        "output_classes_validated",
        "forbidden_actions_validated",
        "provider_disabled_boundary_passed",
        "execution_disabled_boundary_passed",
        "missing_token_rejected",
        "invalid_token_rejected",
        "lan_preflight_blocked",
        "ui_routes_added",
        "api_routes_added",
    ):
        if result.get(key) is not True:
            errors.append(f"AI escalation result {key} must be true")
    for key in ("model_provider_used", "external_network_used", "source_probe_executed", "extraction_executed", "review_mutation_performed", "public_index_mutated", "master_index_mutated", "deployment_performed"):
        if result.get(key) is not False:
            errors.append(f"AI escalation result {key} must be false")
    inventory = payloads.get("control/inventory/ai_escalation_gate_inventory.json", {})
    if inventory.get("runtime_package") != "runtime/ai_escalation":
        errors.append("AI escalation inventory runtime_package mismatch")
    if inventory.get("store_id") != "ai_escalation":
        errors.append("AI escalation inventory store_id mismatch")
    if inventory.get("db_path") != "db/ai_escalation.sqlite":
        errors.append("AI escalation inventory db_path mismatch")
    states = payloads.get("control/inventory/ai_escalation_gate_state_machine.json", {}).get("states", [])
    for state in ("disabled_by_default", "eligible_but_disabled", "blocked_missing_exhaustion_report", "blocked_missing_search_need", "blocked_by_policy", "waiting_for_operator_approval", "waiting_for_provider_gate", "cancelled", "superseded"):
        if state not in states:
            errors.append(f"missing AI escalation state: {state}")
    outputs = payloads.get("control/inventory/ai_escalation_output_matrix.json", {}).get("future_output_classes", [])
    for output_class in ALLOWED_AI_ESCALATION_OUTPUT_CLASSES:
        if output_class not in outputs:
            errors.append(f"missing AI escalation output class: {output_class}")


def validate_report_payload(report: Mapping[str, Any], errors: list[str]) -> None:
    for key in (
        "runtime_package_added",
        "sqlite_store_added",
        "store_added_to_instance_manifest",
        "cli_added",
        "demo_added",
        "validator_added",
        "preflight_from_hunt_passed",
        "preflight_from_need_passed",
        "disabled_gate_created",
        "input_packet_validated",
        "output_classes_validated",
        "forbidden_actions_validated",
        "provider_disabled_boundary_passed",
        "execution_disabled_boundary_passed",
        "missing_token_rejected",
        "invalid_token_rejected",
        "lan_preflight_blocked",
        "ui_routes_added",
        "api_routes_added",
    ):
        if report.get(key) is not True:
            errors.append(f"audit report {key} must be true")
    for key in ("model_provider_used", "external_network_used", "source_probe_executed", "extraction_executed", "review_mutation_performed", "public_index_mutated", "master_index_mutated", "deployment_performed"):
        if report.get(key) is not False:
            errors.append(f"audit report {key} must be false")


def validate_runtime_imports(root: Path, errors: list[str]) -> None:
    for path in sorted((root / "runtime" / "ai_escalation").glob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            module = ""
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module = alias.name
                    if module.startswith(FORBIDDEN_IMPORT_PREFIXES):
                        errors.append(f"forbidden import in {relative(path, root)}: {module}")
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                if module.startswith(FORBIDDEN_IMPORT_PREFIXES):
                    errors.append(f"forbidden import in {relative(path, root)}: {module}")


def validate_runtime_vocabulary(root: Path, errors: list[str]) -> None:
    for path in sorted((root / "runtime" / "ai_escalation").glob("*.py")):
        text = path.read_text(encoding="utf-8")
        for marker in FORBIDDEN_RUNTIME_VOCABULARY:
            if marker in text:
                errors.append(f"forbidden runtime vocabulary in {relative(path, root)}: {marker}")


def validate_behavior(root: Path, errors: list[str]) -> dict[str, Any]:
    behavior = {
        "preflight_from_hunt_passed": False,
        "preflight_from_need_passed": False,
        "disabled_gate_created": False,
        "input_packet_validated": False,
        "output_classes_validated": False,
        "forbidden_actions_validated": False,
        "provider_disabled_boundary_passed": False,
        "execution_disabled_boundary_passed": False,
        "missing_token_rejected": False,
        "invalid_token_rejected": False,
        "lan_preflight_blocked": False,
        "ui_routes_added": False,
        "api_routes_added": False,
        "execute_route_exists": False,
        "execute_attempt_rejected": False,
    }
    with tempfile.TemporaryDirectory() as tmp:
        instance = Path(tmp)
        initialize_instance(instance)
        write_operator_token_record(instance, "validator-token")
        runtime = open_local_appliance(instance)
        try:
            hunt = runtime.search_hunt.create_session_from_query("sampleproject", runtime=runtime)
            runtime.search_hunt.attach_exhaustion_report(hunt.id, build_hunt_exhaustion_report(runtime, hunt.id, operator_label="validator"))
            need = runtime.search_need.create_need_from_hunt(runtime, hunt.id, operator_label="validator")
            runtime.agent_research.draft_task_from_need(runtime, need.id, operator_label="validator")
            preflight_hunt = validate_preflight(build_ai_escalation_preflight(runtime, hunt_id=hunt.id))
            preflight_need = runtime.ai_escalation.write_preflight(validate_preflight(build_ai_escalation_preflight(runtime, need_id=need.id)))
            gate = validate_ai_escalation_gate(create_ai_escalation_gate(runtime, need_id=need.id))
            behavior["preflight_from_hunt_passed"] = preflight_hunt.search_hunt_id == hunt.id
            behavior["preflight_from_need_passed"] = preflight_need.search_need_id == need.id
            behavior["disabled_gate_created"] = gate.provider_enabled is False and gate.execution_enabled is False
            behavior["input_packet_validated"] = bool(gate.input_packet.exhaustion_report_id and gate.input_packet.agent_research_task_id)
            behavior["output_classes_validated"] = set(ALLOWED_AI_ESCALATION_OUTPUT_CLASSES) <= {item.value for item in gate.output_classes}
            behavior["forbidden_actions_validated"] = set(ALLOWED_AI_ESCALATION_FORBIDDEN_ACTIONS) <= {item.value for item in gate.forbidden_actions}
            behavior["provider_disabled_boundary_passed"] = gate.provider_enabled is False
            behavior["execution_disabled_boundary_passed"] = gate.execution_enabled is False
            app = LocalServiceApp(runtime)
            behavior["missing_token_rejected"] = app.handle("POST", f"/api/v1/need/{need.id}/ai-escalation/preflight").status_code == 401
            behavior["invalid_token_rejected"] = app.handle("POST", f"/api/v1/need/{need.id}/ai-escalation/preflight", body="operator_token=wrong-token").status_code == 401
            behavior["lan_preflight_blocked"] = app.handle("POST", f"/api/v1/need/{need.id}/ai-escalation/preflight", client_host="192.168.1.2", body="operator_token=validator-token").status_code == 403
            behavior["api_routes_added"] = (
                app.handle("GET", f"/api/v1/hunt/{hunt.id}/ai-escalation").status_code == 200
                and app.handle("GET", f"/api/v1/need/{need.id}/ai-escalation").status_code == 200
            )
            behavior["ui_routes_added"] = (
                app.handle("GET", f"/hunt/{hunt.id}/ai-escalation").status_code == 200
                and "AI escalation gate" in app.handle("GET", f"/need/{need.id}").body
            )
            behavior["execute_attempt_rejected"] = app.handle("POST", f"/api/v1/need/{need.id}/ai-escalation/execute", body="operator_token=validator-token").status_code != 200
        finally:
            close_local_appliance(runtime)
    for key, value in behavior.items():
        if key != "execute_route_exists" and value is not True:
            errors.append(f"behavior check failed: {key}")
    return behavior


def validate_cli_and_demo(root: Path, errors: list[str]) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        instance = Path(tmp)
        initialize_instance(instance)
        write_operator_token_record(instance, "validator-token")
        import subprocess

        demo = subprocess.run(
            [sys.executable, "scripts/demo_ai_escalation_gate.py", "--instance", str(instance), "--operator-token", "validator-token", "--json"],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
            timeout=120,
        )
        if demo.returncode != 0:
            errors.append("demo_ai_escalation_gate.py failed: " + demo.stderr + demo.stdout)
            return
        payload = json.loads(demo.stdout)
        hunt_id = payload.get("hunt", {}).get("id")
        cli = subprocess.run(
            [
                sys.executable,
                "scripts/eureka_ai_escalation_gate.py",
                "--instance",
                str(instance),
                "preflight-hunt",
                "--hunt-id",
                str(hunt_id),
                "--operator-token",
                "validator-token",
                "--json",
            ],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
            timeout=120,
        )
        if cli.returncode != 0:
            errors.append("eureka_ai_escalation_gate.py preflight-hunt failed: " + cli.stderr + cli.stdout)


def validate_queue(root: Path, errors: list[str]) -> None:
    queue = root / ".aide" / "queue" / "index.yaml"
    if not queue.is_file():
        errors.append("missing queue index")
        return
    text = queue.read_text(encoding="utf-8")
    if not hunt_queue_current_or_advanced(root, TASK_ID, NEXT_TASK):
        errors.append("queue current task must be HUNT-12")
    decision = load_json(root / "control/inventory/hunt_11_next_task_decision.json", "hunt_11_next_task_decision.v0", errors)
    if not str(decision.get("recommended_next_task", "")).startswith("HUNT-12"):
        errors.append("HUNT-11 next task decision must point to HUNT-12")


def load_json(path: Path, schema_version: str, errors: list[str]) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"missing JSON file: {relative(path, REPO_ROOT)}")
        return {}
    except json.JSONDecodeError as exc:
        errors.append(f"invalid JSON {relative(path, REPO_ROOT)}: {exc}")
        return {}
    if not isinstance(payload, dict):
        errors.append(f"JSON file must contain an object: {relative(path, REPO_ROOT)}")
        return {}
    if payload.get("schema_version") != schema_version:
        errors.append(f"{relative(path, REPO_ROOT)} schema_version mismatch")
    return payload


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def relative(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


if __name__ == "__main__":
    raise SystemExit(main())
