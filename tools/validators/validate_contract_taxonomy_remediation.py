#!/usr/bin/env python3
"""Validate R0 contract taxonomy remediation outputs."""

from __future__ import annotations

import argparse
import ast
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]
TASK_ID = "R0-REMEDIATION-CONTRACT-TAXONOMY-01"
AUDIT_DIR = Path("control/audits/r0-remediation-contract-taxonomy-01-v0")

INVENTORIES = {
    "control/inventory/r0_contract_taxonomy_remediation_result.json": "r0_contract_taxonomy_remediation_result.v0",
    "control/inventory/r0_contract_taxonomy_resolved_items.json": "r0_contract_taxonomy_resolved_items.v0",
    "control/inventory/r0_contract_taxonomy_remaining_items.json": "r0_contract_taxonomy_remaining_items.v0",
    "control/inventory/r0_contract_taxonomy_shim_retirement_report.json": "r0_contract_taxonomy_shim_retirement_report.v0",
    "control/inventory/r0_contract_taxonomy_reference_update_report.json": "r0_contract_taxonomy_reference_update_report.v0",
    "control/inventory/r0_contract_taxonomy_final_state.json": "r0_contract_taxonomy_final_state.v0",
}
AUDIT_FILES = (
    "README.md",
    "remediation_report.json",
    "resolved_items.md",
    "remaining_items.md",
    "shim_retirement_report.md",
    "reference_update_report.md",
    "final_contract_taxonomy_state.md",
    "validation.md",
    "generated/sample_remediation_result.json",
    "generated/sample_final_contract_taxonomy_state.json",
    "generated/sample_summary.md",
)
FORBIDDEN_CHANGED_ROOTS = ("runtime/", "surfaces/", "site/", "native/", "crates/", ".aide.local/", ".local/", ".cache/", "secrets/")
FORBIDDEN_IMPORT_ROOTS = {"requests", "httpx", "aiohttp", "socket", "subprocess.Popen", "openai", "anthropic"}
ALLOWED_RUNTIME_REFERENCE_ONLY_PATHS = {
    "runtime/connectors/synthetic_software/fixture_source.py",
    "runtime/connectors/synthetic_software/tests/test_fixture_connector.py",
    "runtime/engine/actions/tests/test_resolution_manifest.py",
    "runtime/engine/compare/tests/test_comparison.py",
    "runtime/engine/representations/tests/test_service.py",
    "runtime/engine/store/tests/test_export_store.py",
    "runtime/engine/tests/test_boundary_transforms.py",
    "runtime/engine/tests/test_exact_match_resolution_service.py",
    "runtime/engine/tests/test_resolved_resource_identity.py",
    "runtime/gateway/tests/test_compatibility_view_models.py",
    "runtime/gateway/tests/test_workbench_sessions.py",
    "runtime/local_foundry/workunit_dry_run.py",
}


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--skip-commands", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    result = validate(Path(args.repo_root).resolve(), run_commands=not args.skip_commands)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    else:
        print("R0 contract taxonomy remediation validation", file=stdout)
        print(f"status: {result['status']}", file=stdout)
        for error in result["errors"]:
            print(f"ERROR: {error}", file=stdout)
        for warning in result["warnings"]:
            print(f"WARN: {warning}", file=stdout)
    return 0 if result["status"] == "pass" else 1


def validate(root: Path = REPO_ROOT, *, run_commands: bool = True) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    inventories = validate_inventories(root, errors)
    validate_audit_pack(root, errors)
    validate_final_state(root, inventories, errors)
    validate_moved_paths(root, inventories, errors)
    validate_reference_report(root, inventories, errors)
    validate_no_forbidden_changes(root, errors, allowed_runtime_paths=allowed_runtime_reference_paths(inventories))
    validate_no_forbidden_imports(root, errors)
    command_results: list[dict[str, Any]] = []
    if run_commands:
        command_results.extend(run_required_commands(root, errors, warnings))
    return {
        "schema_version": "r0_contract_taxonomy_remediation_validation.v0",
        "task": TASK_ID,
        "status": "pass" if not errors else "fail",
        "errors": errors,
        "warnings": warnings,
        "command_results": command_results,
        "network_used": False,
        "model_provider_used": False,
        "runtime_files_modified": False,
        "site_dist_mutated": False,
        "master_index_mutated": False,
    }


def validate_inventories(root: Path, errors: list[str]) -> dict[str, Any]:
    loaded: dict[str, Any] = {}
    for rel, schema in INVENTORIES.items():
        payload = read_json(root / rel, errors)
        if not payload:
            continue
        loaded[Path(rel).stem] = payload
        if payload.get("schema_version") != schema:
            errors.append(f"unexpected schema_version for {rel}")
    return loaded


def validate_audit_pack(root: Path, errors: list[str]) -> None:
    for rel in AUDIT_FILES:
        if not (root / AUDIT_DIR / rel).exists():
            errors.append(f"missing audit pack file: {(AUDIT_DIR / rel).as_posix()}")
    report = read_json(root / AUDIT_DIR / "remediation_report.json", errors)
    if report and report.get("schema_version") != "r0_contract_taxonomy_remediation_report.v0":
        errors.append("remediation report schema mismatch")


def validate_final_state(root: Path, inventories: Mapping[str, Any], errors: list[str]) -> None:
    result = inventories.get("r0_contract_taxonomy_remediation_result", {})
    final = inventories.get("r0_contract_taxonomy_final_state", {})
    old_final = read_json(root / "control/inventory/r0_03b_2_final_contract_taxonomy.json", errors)
    if result.get("unresolved_after") != 0:
        errors.append("remediation unresolved_after must be 0 or separately child-tasked")
    if result.get("compatibility_shims_after") != 0:
        errors.append("remediation compatibility_shims_after must be 0 or separately child-tasked")
    if result.get("contracts_clean_enough_for_f0") is not True:
        errors.append("contracts must be clean enough for F0")
    if final.get("contracts_root_status") not in {"clean", "clean_with_warnings"}:
        errors.append("final contracts root status is not clean enough")
    if old_final and old_final.get("unresolved_contract_count") != 0:
        errors.append("R0-03B-2 final taxonomy still reports unresolved contracts")
    if old_final and old_final.get("compatibility_shim_count") != 0:
        errors.append("R0-03B-2 final taxonomy still reports compatibility shims")
    if result.get("f0_decision") not in {"resume_f0", "remain_blocked", "remediation_required"}:
        errors.append("F0 decision is not explicit")
    if result.get("dev_to_main_decision") not in {"promote_ready", "promotion_plan_only", "remain_blocked", "already_on_main"}:
        errors.append("dev-to-main decision is not explicit")
    for key in ("production_readiness_claimed", "public_launch_readiness_claimed"):
        if result.get(key) is not False:
            errors.append(f"remediation overclaims {key}")


def validate_moved_paths(root: Path, inventories: Mapping[str, Any], errors: list[str]) -> None:
    resolved = inventories.get("r0_contract_taxonomy_resolved_items", {}).get("resolved", [])
    for item in resolved:
        source = root / str(item.get("source_path", ""))
        target = root / str(item.get("target_path", ""))
        if source.exists():
            errors.append(f"source path still exists after remediation: {item.get('source_path')}")
        if not target.exists():
            errors.append(f"target path missing after remediation: {item.get('target_path')}")
        if str(item.get("source_path", "")).startswith("contracts/archive/fixtures/") and item.get("classification") != "fixture_schema":
            errors.append(f"archive fixture not classified as fixture_schema: {item.get('source_path')}")
        if "/h14_" in str(item.get("source_path", "")) and item.get("classification") != "preview_schema":
            errors.append(f"H14 candidate not classified as preview_schema: {item.get('source_path')}")


def validate_reference_report(root: Path, inventories: Mapping[str, Any], errors: list[str]) -> None:
    report = inventories.get("r0_contract_taxonomy_reference_update_report", {})
    changed_runtime = changed_paths(root, "runtime/")
    result = inventories.get("r0_contract_taxonomy_remediation_result", {})
    if changed_runtime - allowed_runtime_reference_paths(inventories):
        errors.append(f"unexpected runtime files modified: {sorted(changed_runtime - allowed_runtime_reference_paths(inventories))}")
    recorded_runtime_files = result.get("runtime_files_modified")
    if not isinstance(recorded_runtime_files, int) or recorded_runtime_files < 0:
        errors.append("runtime_files_modified must be a non-negative integer")
    elif changed_runtime and recorded_runtime_files != len(changed_runtime):
        errors.append("runtime_files_modified does not match changed runtime reference-only paths")
    for update in report.get("active_reference_updates", []):
        path = root / str(update.get("path", ""))
        if not path.exists():
            errors.append(f"reference update path missing: {update.get('path')}")
            continue
        text = read_text(path)
        if str(update.get("old_reference")) in text:
            errors.append(f"old reference remains in active file: {update.get('path')} -> {update.get('old_reference')}")


def validate_no_forbidden_changes(root: Path, errors: list[str], *, allowed_runtime_paths: set[str] | None = None) -> None:
    allowed_runtime_paths = allowed_runtime_paths or set()
    completed = subprocess.run(["git", "status", "--porcelain=v1"], cwd=root, text=True, capture_output=True, check=False)
    if completed.returncode != 0:
        return
    for line in completed.stdout.splitlines():
        if len(line) < 4:
            continue
        raw = line[3:].replace("\\", "/").strip('"')
        for path in raw.split(" -> "):
            if path.startswith("runtime/") and path in allowed_runtime_paths:
                continue
            if path.startswith(FORBIDDEN_CHANGED_ROOTS):
                errors.append(f"forbidden path changed: {path}")
            if path.startswith("site/dist/"):
                errors.append(f"site/dist path changed: {path}")


def validate_no_forbidden_imports(root: Path, errors: list[str]) -> None:
    for rel in ("scripts/resolve_contract_taxonomy_blockers.py", "scripts/validate_contract_taxonomy_remediation.py"):
        path = root / rel
        if not path.exists():
            errors.append(f"missing required script: {rel}")
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.split(".", 1)[0] in {"requests", "httpx", "aiohttp", "socket", "openai", "anthropic"}:
                        errors.append(f"{rel} imports forbidden module: {alias.name}")
            elif isinstance(node, ast.ImportFrom) and node.module:
                if node.module.split(".", 1)[0] in {"requests", "httpx", "aiohttp", "socket", "openai", "anthropic"}:
                    errors.append(f"{rel} imports forbidden module: {node.module}")


def allowed_runtime_reference_paths(inventories: Mapping[str, Any]) -> set[str]:
    report = inventories.get("r0_contract_taxonomy_reference_update_report", {})
    allowed = set(ALLOWED_RUNTIME_REFERENCE_ONLY_PATHS)
    for update in report.get("active_reference_updates", []):
        path = str(update.get("path", "")).replace("\\", "/")
        if path.startswith("runtime/"):
            allowed.add(path)
    return allowed


def changed_paths(root: Path, prefix: str) -> set[str]:
    completed = subprocess.run(["git", "status", "--porcelain=v1"], cwd=root, text=True, capture_output=True, check=False)
    if completed.returncode != 0:
        return set()
    paths: set[str] = set()
    for line in completed.stdout.splitlines():
        if len(line) < 4:
            continue
        raw = line[3:].replace("\\", "/").strip('"')
        for path in raw.split(" -> "):
            if path.startswith(prefix):
                paths.add(path)
    return paths


def run_required_commands(root: Path, errors: list[str], warnings: list[str]) -> list[dict[str, Any]]:
    commands = (
        ("python scripts/validate_product_contract_tree.py", [sys.executable, "scripts/validate_product_contract_tree.py"], True),
        ("python scripts/validate_contract_taxonomy_migration.py", [sys.executable, "scripts/validate_contract_taxonomy_migration.py"], True),
        ("python scripts/validate_contract_taxonomy_plan.py", [sys.executable, "scripts/validate_contract_taxonomy_plan.py"], True),
    )
    results: list[dict[str, Any]] = []
    for label, args, allow_warning in commands:
        completed = subprocess.run(args, cwd=root, text=True, capture_output=True, check=False)
        output = completed.stdout + completed.stderr
        status = "pass" if completed.returncode == 0 else "fail"
        if completed.returncode != 0:
            errors.append(f"command failed: {label}")
        elif allow_warning and ("warning" in output.lower() or "valid_with_warnings" in output.lower() or "pass_with_warnings" in output.lower()):
            status = "pass_with_warnings"
            warnings.append(f"command has warnings: {label}")
        results.append({"command": label, "status": status})
    return results


def read_json(path: Path, errors: list[str]) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"missing JSON: {path.as_posix()}")
        return {}
    except json.JSONDecodeError as exc:
        errors.append(f"invalid JSON {path.as_posix()}: {exc}")
        return {}
    return payload if isinstance(payload, dict) else {}


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="ignore")


if __name__ == "__main__":
    raise SystemExit(main())
