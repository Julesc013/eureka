#!/usr/bin/env python3
"""Validate an explicit local Eureka appliance instance."""

from __future__ import annotations

import argparse
import json
import sqlite3
import subprocess
import sys
from pathlib import Path
from typing import Any, Sequence, TextIO

from eureka_init_instance import (
    INSTANCE_SCHEMA_VERSION,
    PLANNED_DB_FILES,
    REQUIRED_DIRS,
    REQUIRED_FILES,
    REPO_ROOT,
    STATUS_SCHEMA_VERSION,
    STORE_SPECS,
    TASK_ID,
    InstancePathError,
    emit_result,
    initialize_store,
    is_relative_to,
    load_json_if_exists,
    sqlite_integrity,
    validate_instance_path,
    write_json,
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout, stderr: TextIO = sys.stderr) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instance", help="Explicit local instance root to validate.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    parser.add_argument("--output", help="Optional JSON result output path.")
    args = parser.parse_args(argv)

    if not args.instance:
        result = fail_result("missing_instance", "--instance is required")
        emit_result(result, args.json, args.output, stdout)
        print("ERROR: --instance is required", file=stderr)
        return 2

    try:
        result = validate_instance(Path(args.instance))
    except InstancePathError as exc:
        result = fail_result("forbidden_instance_path", str(exc), instance=args.instance)
        emit_result(result, args.json, args.output, stdout)
        print(f"ERROR: {exc}", file=stderr)
        return 2
    except Exception as exc:  # pragma: no cover - defensive CLI boundary
        result = fail_result("validation_failed", str(exc), instance=args.instance)
        emit_result(result, args.json, args.output, stdout)
        print(f"ERROR: {exc}", file=stderr)
        return 1

    emit_result(result, args.json, args.output, stdout)
    return 0 if result["status"] in {"pass", "pass_with_warnings"} else 1


def validate_instance(instance: Path) -> dict[str, Any]:
    instance_root = validate_instance_path(instance)
    errors: list[str] = []
    warnings: list[str] = []

    for rel in REQUIRED_DIRS:
        if not (instance_root / rel).is_dir():
            errors.append(f"missing directory: {rel}")

    manifest_path = instance_root / "config" / "instance.json"
    status_path = instance_root / "run" / "status.json"
    manifest = require_json(manifest_path, errors)
    status = require_json(status_path, errors)

    validate_manifest(manifest, instance_root, errors)
    validate_status(status, manifest, errors)

    db_results: dict[str, dict[str, Any]] = {}
    for spec in STORE_SPECS:
        db_path = instance_root / spec.relative_path
        store_status = status.get("stores", {}).get(spec.name, {}) if isinstance(status.get("stores"), dict) else {}
        if not db_path.is_file():
            if store_status.get("status") == "blocked":
                warnings.append(f"{spec.name} database missing because store initialization is blocked")
                db_results[spec.name] = {"status": "blocked", "path": str(db_path), "blocker": store_status.get("blocker")}
            else:
                errors.append(f"missing database file: {spec.relative_path}")
                db_results[spec.name] = {"status": "fail", "path": str(db_path), "error": "missing_database_file"}
            continue
        db_results[spec.name] = check_store_integrity(spec.name, db_path)
        if db_results[spec.name].get("status") != "pass":
            errors.append(f"{spec.name} integrity check failed")

    committed_state = committed_instance_state(instance_root)
    if committed_state:
        errors.append("local instance state is committed: " + ", ".join(committed_state))

    for key in ("server_enabled", "lan_enabled", "deployment_enabled", "production_readiness_claimed", "public_launch_readiness_claimed"):
        if manifest.get(key) not in (False, None):
            errors.append(f"manifest must set {key}=false")
    for key in ("server_enabled", "lan_enabled", "deployment_performed", "production_readiness_claimed", "public_launch_readiness_claimed"):
        if status.get(key) is not False:
            errors.append(f"status must set {key}=false")

    result_status = "fail" if errors else ("pass_with_warnings" if warnings else "pass")
    return {
        "schema_version": "local_instance_validation_result.v0",
        "task": TASK_ID,
        "status": result_status,
        "instance_root": str(instance_root),
        "required_directories_present": all((instance_root / rel).is_dir() for rel in REQUIRED_DIRS),
        "required_files_present": all((instance_root / rel).is_file() for rel in REQUIRED_FILES),
        "planned_database_files": list(PLANNED_DB_FILES),
        "database_integrity": db_results,
        "committed_instance_state_found": bool(committed_state),
        "committed_instance_state_paths": committed_state,
        "errors": errors,
        "warnings": warnings,
        "server_enabled": False,
        "lan_enabled": False,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }


def require_json(path: Path, errors: list[str]) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"missing file: {relative(path)}")
        return {}
    except json.JSONDecodeError as exc:
        errors.append(f"invalid JSON {relative(path)}: {exc}")
        return {}
    if not isinstance(payload, dict):
        errors.append(f"JSON file must contain an object: {relative(path)}")
        return {}
    return payload


def validate_manifest(manifest: dict[str, Any], instance_root: Path, errors: list[str]) -> None:
    if manifest.get("schema_version") != INSTANCE_SCHEMA_VERSION:
        errors.append("instance manifest schema_version mismatch")
    if not manifest.get("instance_id"):
        errors.append("instance manifest missing instance_id")
    if not manifest.get("created_at"):
        errors.append("instance manifest missing created_at")
    if Path(str(manifest.get("instance_root", ""))).resolve() != instance_root:
        errors.append("instance manifest instance_root does not match validated path")
    if manifest.get("appliance_mode") != "local":
        errors.append("instance manifest appliance_mode must be local")


def validate_status(status: dict[str, Any], manifest: dict[str, Any], errors: list[str]) -> None:
    if status.get("schema_version") != STATUS_SCHEMA_VERSION:
        errors.append("instance status schema_version mismatch")
    if status.get("instance_id") != manifest.get("instance_id"):
        errors.append("status instance_id does not match manifest")
    if status.get("status") != "initialized":
        errors.append("status must be initialized")
    stores = status.get("stores")
    if not isinstance(stores, dict):
        errors.append("status stores must be an object")
        return
    for spec in STORE_SPECS:
        if spec.name not in stores:
            errors.append(f"status missing store record: {spec.name}")


def check_store_integrity(store_name: str, db_path: Path) -> dict[str, Any]:
    spec = next(item for item in STORE_SPECS if item.name == store_name)
    try:
        import importlib

        module = importlib.import_module(spec.module)
        store_class = getattr(module, spec.class_name)
        with store_class.open(db_path) as store:
            return {
                "status": "pass",
                "path": str(db_path),
                "runtime_api": f"{spec.module}.{spec.class_name}",
                "integrity": store.check_integrity(),
            }
    except Exception as exc:
        integrity = sqlite_integrity(db_path)
        status = "pass" if integrity.get("status") == "pass" else "fail"
        return {
            "status": status,
            "path": str(db_path),
            "runtime_api": f"{spec.module}.{spec.class_name}",
            "fallback_integrity": integrity,
            "warning": str(exc),
        }


def committed_instance_state(instance_root: Path) -> list[str]:
    repo = REPO_ROOT.resolve()
    if not is_relative_to(instance_root, repo):
        return []
    rel = instance_root.relative_to(repo).as_posix()
    completed = subprocess.run(
        ["git", "ls-files", "--", rel],
        cwd=repo,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        return []
    return [line.strip() for line in completed.stdout.splitlines() if line.strip()]


def fail_result(code: str, message: str, *, instance: str | None = None) -> dict[str, Any]:
    result: dict[str, Any] = {
        "schema_version": "local_instance_validation_result.v0",
        "task": TASK_ID,
        "status": "fail",
        "error": code,
        "message": message,
        "server_enabled": False,
        "lan_enabled": False,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }
    if instance is not None:
        result["instance"] = instance
    return result


def relative(path: Path) -> str:
    try:
        return path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


if __name__ == "__main__":
    raise SystemExit(main())
