#!/usr/bin/env python3
"""Validate the R0-03B-1 contract taxonomy migration batch offline."""

from __future__ import annotations

import argparse
import ast
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
TASK_ID = "R0-03B-1"
AUDIT_DIR = Path("control/audits/r0-03b-1-contract-taxonomy-migration-v0")
EXECUTOR = Path("scripts/execute_contract_taxonomy_migration.py")
VALIDATOR = Path("scripts/validate_contract_taxonomy_migration.py")

REQUIRED_JSON = {
    "control/inventory/r0_03b_1_migration_result.json": "r0_03b_1_migration_result.v0",
    "control/inventory/r0_03b_1_reference_update_report.json": "r0_03b_1_reference_update_report.v0",
    "control/inventory/r0_03b_1_compatibility_shim_report.json": "r0_03b_1_compatibility_shim_report.v0",
    f"{AUDIT_DIR.as_posix()}/r0_03b_1_report.json": "r0_03b_1_report.v0",
    f"{AUDIT_DIR.as_posix()}/generated/sample_migration_result.json": "r0_03b_1_migration_result.v0",
    f"{AUDIT_DIR.as_posix()}/generated/sample_reference_update_report.json": "r0_03b_1_reference_update_report.v0",
}

REQUIRED_MARKDOWN = (
    "docs/operations/R0_CONTRACT_TAXONOMY_MIGRATION_BATCH_1.md",
    f"{AUDIT_DIR.as_posix()}/README.md",
    f"{AUDIT_DIR.as_posix()}/migration_result.md",
    f"{AUDIT_DIR.as_posix()}/moved_schema_summary.md",
    f"{AUDIT_DIR.as_posix()}/remaining_product_contract_summary.md",
    f"{AUDIT_DIR.as_posix()}/compatibility_shim_summary.md",
    f"{AUDIT_DIR.as_posix()}/reference_update_summary.md",
    f"{AUDIT_DIR.as_posix()}/validation.md",
    f"{AUDIT_DIR.as_posix()}/generated/sample_summary.md",
)

TARGET_SCHEMA_ROOTS = (
    "control/schemas/audits",
    "control/schemas/fixtures",
    "control/schemas/previews",
    "control/schemas/policies",
    "control/schemas/validators",
    "control/schemas/tasks",
    "control/schemas/deprecated",
)

ALLOWED_MOVED_CLASSES = {"audit_schema", "fixture_schema", "preview_schema"}
PRODUCT_CLASSES = {
    "product_domain_contract",
    "product_runtime_contract",
    "public_api_contract",
    "snapshot_contract",
    "native_contract",
    "durable_store_contract",
    "connector_interface_contract",
    "source_policy_contract",
}
FORBIDDEN_MODIFIED_PREFIXES = ("runtime/", "surfaces/", "site/", "native/", "crates/")
BANNED_IMPORT_ROOTS = {
    "urllib",
    "requests",
    "httpx",
    "aiohttp",
    "socket",
    "ftplib",
    "smtplib",
    "webbrowser",
    "selenium",
    "playwright",
    "openai",
    "anthropic",
    "runtime",
}


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    result = validate_repo(Path(args.repo_root).resolve())
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    else:
        print("R0-03B-1 contract taxonomy migration validation", file=stdout)
        print(f"status: {result['status']}", file=stdout)
        print(f"error_count: {len(result['errors'])}", file=stdout)
        for error in result["errors"]:
            print(f"ERROR: {error}", file=stdout)
    return 0 if result["status"] == "valid" else 1


def validate_repo(root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    payloads = {rel: load_json(root / rel, schema, errors) for rel, schema in REQUIRED_JSON.items()}
    validate_schema_roots(root, errors)
    validate_markdown(root, errors)
    migration = payloads.get("control/inventory/r0_03b_1_migration_result.json", {})
    refs = payloads.get("control/inventory/r0_03b_1_reference_update_report.json", {})
    shims = payloads.get("control/inventory/r0_03b_1_compatibility_shim_report.json", {})
    report = payloads.get(f"{AUDIT_DIR.as_posix()}/r0_03b_1_report.json", {})
    validate_migration_payload(root, migration, errors)
    validate_reference_report(root, migration, refs, errors)
    validate_shim_report(migration, shims, errors)
    validate_audit_report(migration, refs, shims, report, errors)
    validate_static_only(root, errors)
    validate_dry_run(root, errors)
    validate_no_forbidden_paths_modified(root, errors)
    return {
        "schema_version": "r0_03b_1_validation.v0",
        "status": "valid" if not errors else "invalid",
        "task": TASK_ID,
        "runtime_modified": False,
        "product_behavior_changed": False,
        "network_calls_made": False,
        "model_provider_calls_made": False,
        "f0_should_remain_blocked": True,
        "dev_to_main_should_remain_blocked": True,
        "recommended_next_task": "R0-03B-2 — Contract reference update and product contract cleanup",
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


def validate_schema_roots(root: Path, errors: list[str]) -> None:
    for rel in TARGET_SCHEMA_ROOTS:
        if not (root / rel).is_dir():
            errors.append(f"missing target schema root: {rel}")


def validate_markdown(root: Path, errors: list[str]) -> None:
    for rel in REQUIRED_MARKDOWN:
        path = root / rel
        if not path.is_file():
            errors.append(f"missing markdown output: {rel}")
        elif path.stat().st_size == 0:
            errors.append(f"empty markdown output: {rel}")


def validate_migration_payload(root: Path, migration: Mapping[str, Any], errors: list[str]) -> None:
    if migration.get("task") != TASK_ID:
        errors.append("migration result task must be R0-03B-1")
    if migration.get("status") not in {"pass", "pass_with_warnings", "partial", "blocked", "fail"}:
        errors.append("migration result status is invalid")
    if migration.get("schemas_deleted") != 0:
        errors.append("schemas_deleted must be 0")
    if migration.get("product_contracts_moved") != 0:
        errors.append("product_contracts_moved must be 0")
    if migration.get("unknown_contracts_moved") != 0:
        errors.append("unknown_contracts_moved must be 0")
    if migration.get("runtime_files_modified") != 0:
        errors.append("runtime_files_modified must be 0")
    if migration.get("f0_should_remain_blocked") is not True:
        errors.append("migration result must keep F0 blocked")
    if migration.get("dev_to_main_should_remain_blocked") is not True:
        errors.append("migration result must keep dev-to-main blocked")
    moved = migration.get("moved", [])
    if not isinstance(moved, list):
        errors.append("migration moved must be a list")
        return
    for item in moved:
        if item.get("contract_class") not in ALLOWED_MOVED_CLASSES:
            errors.append(f"moved item has disallowed class: {item.get('source_path')} {item.get('contract_class')}")
        if item.get("contract_class") in PRODUCT_CLASSES or item.get("contract_class") == "unknown":
            errors.append(f"product or unknown contract moved accidentally: {item.get('source_path')}")
        source = root / str(item.get("source_path", ""))
        target = root / str(item.get("target_path", ""))
        if not target.is_file():
            errors.append(f"moved target is missing: {item.get('target_path')}")
        if source.exists():
            errors.append(f"moved source still exists: {item.get('source_path')}")
    blocked = migration.get("blocked", [])
    if not isinstance(blocked, list):
        errors.append("migration blocked must be a list")


def validate_reference_report(root: Path, migration: Mapping[str, Any], report: Mapping[str, Any], errors: list[str]) -> None:
    for key in ("updates", "unresolved_references", "historical_references_left_intact"):
        if not isinstance(report.get(key), list):
            errors.append(f"reference report {key} must be a list")
    moved_sources = {item.get("source_path") for item in migration.get("moved", []) if isinstance(item, Mapping)}
    for update in report.get("updates", []):
        if not {"path", "old_reference", "new_reference", "reason"} <= set(update):
            errors.append("reference update entries must contain path, old_reference, new_reference, reason")
        if update.get("old_reference") not in moved_sources:
            errors.append(f"reference update points to non-moved schema: {update.get('old_reference')}")
        ref_path = root / str(update.get("path", ""))
        if str(update.get("path", "")).startswith("runtime/"):
            errors.append(f"reference update illegally targets runtime path: {update.get('path')}")
        if not ref_path.exists():
            errors.append(f"reference update path missing: {update.get('path')}")
    for unresolved in report.get("unresolved_references", []):
        if str(unresolved.get("path", "")).startswith(FORBIDDEN_MODIFIED_PREFIXES):
            continue
        if str(unresolved.get("path", "")).startswith("scripts/") and not str(unresolved.get("path", "")).startswith(("scripts/audit_", "scripts/validate_")):
            continue
        errors.append(f"unresolved reference is not an allowed deferred reference: {unresolved.get('path')}")


def validate_shim_report(migration: Mapping[str, Any], report: Mapping[str, Any], errors: list[str]) -> None:
    shims = report.get("shims")
    if not isinstance(shims, list):
        errors.append("compatibility shim report shims must be a list")
        return
    moved_or_blocked = {
        item.get("source_path")
        for item in (migration.get("moved", []) or []) + (migration.get("blocked", []) or [])
        if isinstance(item, Mapping)
    }
    for shim in shims:
        if not {"old_path", "new_path", "shim_kind", "expires_after_task", "reason"} <= set(shim):
            errors.append("shim entries must contain old_path, new_path, shim_kind, expires_after_task, reason")
        if shim.get("old_path") not in moved_or_blocked:
            errors.append(f"shim old_path not tied to moved or blocked schema: {shim.get('old_path')}")


def validate_audit_report(
    migration: Mapping[str, Any],
    refs: Mapping[str, Any],
    shims: Mapping[str, Any],
    report: Mapping[str, Any],
    errors: list[str],
) -> None:
    if report.get("task") != TASK_ID:
        errors.append("R0-03B-1 report task must be R0-03B-1")
    expected = {
        "moves_completed": migration.get("moves_completed"),
        "moves_blocked": migration.get("moves_blocked"),
        "schemas_deleted": 0,
        "product_contracts_moved": 0,
        "unknown_contracts_moved": 0,
    }
    for key, value in expected.items():
        if report.get(key) != value:
            errors.append(f"R0-03B-1 report {key} must be {value}")
    if report.get("runtime_modified") is not False:
        errors.append("R0-03B-1 report runtime_modified must be false")
    if report.get("product_behavior_changed") is not False:
        errors.append("R0-03B-1 report product_behavior_changed must be false")
    if report.get("reference_updates_completed") != len(refs.get("updates", [])):
        errors.append("R0-03B-1 report reference_updates_completed mismatch")
    if report.get("compatibility_shims_added") != sum(1 for item in shims.get("shims", []) if item.get("shim_kind") != "none"):
        errors.append("R0-03B-1 report compatibility_shims_added mismatch")
    if report.get("f0_should_remain_blocked") is not True:
        errors.append("R0-03B-1 report must keep F0 blocked")
    if report.get("dev_to_main_should_remain_blocked") is not True:
        errors.append("R0-03B-1 report must keep dev-to-main blocked")


def validate_static_only(root: Path, errors: list[str]) -> None:
    for rel in (EXECUTOR, VALIDATOR):
        path = root / rel
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except OSError as exc:
            errors.append(f"cannot read {rel.as_posix()}: {exc}")
            continue
        except SyntaxError as exc:
            errors.append(f"cannot parse {rel.as_posix()}: {exc}")
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.split(".")[0] in BANNED_IMPORT_ROOTS:
                        errors.append(f"{rel.as_posix()} imports forbidden module {alias.name}")
            elif isinstance(node, ast.ImportFrom):
                root_name = (node.module or "").split(".")[0]
                if root_name in BANNED_IMPORT_ROOTS:
                    errors.append(f"{rel.as_posix()} imports forbidden module {node.module}")


def validate_dry_run(root: Path, errors: list[str]) -> None:
    proc = subprocess.run(
        [sys.executable, str(root / EXECUTOR), "--repo-root", str(root), "--dry-run", "--json"],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        errors.append(f"executor dry-run failed: {proc.stdout} {proc.stderr}".strip())
        return
    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        errors.append(f"executor dry-run did not return JSON: {exc}")
        return
    if payload.get("schemas_deleted") != 0:
        errors.append("executor dry-run must not delete schemas")


def validate_no_forbidden_paths_modified(root: Path, errors: list[str]) -> None:
    if not (root / ".git").exists():
        return
    proc = subprocess.run(["git", "status", "--short"], cwd=root, text=True, capture_output=True, check=False)
    if proc.returncode != 0:
        errors.append(f"git status failed: {proc.stderr.strip()}")
        return
    for line in proc.stdout.splitlines():
        if not line.strip():
            continue
        path = line[3:].strip()
        if " -> " in path:
            path = path.split(" -> ", 1)[1].strip()
        normalized = path.replace("\\", "/")
        if normalized.startswith(FORBIDDEN_MODIFIED_PREFIXES):
            errors.append(f"R0-03B-1 modified forbidden path: {normalized}")


if __name__ == "__main__":
    raise SystemExit(main())
