#!/usr/bin/env python3
"""Validate an explicit local Eureka appliance instance."""

from __future__ import annotations

import argparse
import importlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence, TextIO

from eureka_init_instance import (
    CURRENT_INSTANCE_SCHEMA_VERSION,
    INSTANCE_SCHEMA_VERSION,
    MIGRATION_STATE_SCHEMA_VERSION,
    MINIMUM_SUPPORTED_INSTANCE_SCHEMA_VERSION,
    PLANNED_DB_FILES,
    REQUIRED_DIRS,
    REQUIRED_FILES,
    REPO_ROOT,
    STATUS_SCHEMA_VERSION,
    STORE_MANIFEST_SCHEMA_VERSION,
    STORE_SPECS,
    TASK_ID,
    InstancePathError,
    emit_result,
    is_relative_to,
    sqlite_integrity,
    validate_instance_path,
)
from runtime.local_appliance.paths import describe_instance_layout


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
    instance_layout = describe_instance_layout(REPO_ROOT, instance_root)
    errors: list[str] = []
    warnings: list[str] = list(instance_layout.get("warnings", []))

    for rel in REQUIRED_DIRS:
        if not (instance_root / rel).is_dir():
            errors.append(f"missing directory: {rel}")

    manifest_path = instance_root / "config" / "instance.json"
    status_path = instance_root / "run" / "status.json"
    store_manifest_path = instance_root / "config" / "store_manifest.json"
    migration_state_path = instance_root / "config" / "migration_state.json"
    manifest = require_json(manifest_path, errors)
    status = require_json(status_path, errors)
    store_manifest = require_json(store_manifest_path, errors)
    migration_state = require_json(migration_state_path, errors)

    version_status = evaluate_instance_schema_version(manifest.get("instance_schema_version"))
    if version_status["unsupported"]:
        errors.extend(version_status["blockers"])
    if version_status["migration_needed"]:
        warnings.append("instance schema migration is needed before future service work")

    validate_manifest(manifest, instance_root, errors)
    validate_status(status, manifest, errors)
    validate_store_manifest(store_manifest, errors)
    validate_migration_state(migration_state, manifest, version_status, errors)

    db_results: dict[str, dict[str, Any]] = {}
    for spec in STORE_SPECS:
        manifest_entry = store_manifest.get("stores", {}).get(spec.name, {}) if isinstance(store_manifest.get("stores"), dict) else {}
        db_path = instance_root / spec.relative_path
        if not db_path.is_file():
            if manifest_entry.get("required") is False:
                warnings.append(f"{spec.name} optional database is missing")
                db_results[spec.name] = {"status": "missing_optional", "path": str(db_path)}
            else:
                errors.append(f"missing required database file: {spec.relative_path}")
                db_results[spec.name] = {"status": "fail", "path": str(db_path), "error": "missing_required_database_file"}
            continue
        db_results[spec.name] = check_store_integrity(spec.name, db_path)
        if db_results[spec.name].get("status") != "pass":
            errors.append(f"{spec.name} integrity check failed")

    committed_state = committed_instance_state(instance_root)
    if committed_state:
        errors.append("local instance state is committed: " + ", ".join(committed_state))

    validate_false_flags(manifest, "manifest", errors)
    validate_false_flags(status, "status", errors, deployment_key="deployment_performed")

    result_status = "fail" if errors else ("pass_with_warnings" if warnings else "pass")
    return {
        "schema_version": "local_instance_validation_result.v0",
        "task": TASK_ID,
        "status": result_status,
        "instance_root": str(instance_root),
        "instance_layout": instance_layout,
        "instance_schema_version": manifest.get("instance_schema_version"),
        "minimum_supported_instance_schema_version": MINIMUM_SUPPORTED_INSTANCE_SCHEMA_VERSION,
        "current_instance_schema_version": CURRENT_INSTANCE_SCHEMA_VERSION,
        "migration_needed": version_status["migration_needed"] or bool(migration_state.get("migration_needed")),
        "unsupported_instance_schema_version": version_status["unsupported"],
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


def validate_manifest(manifest: Mapping[str, Any], instance_root: Path, errors: list[str]) -> None:
    if manifest.get("schema_version") != INSTANCE_SCHEMA_VERSION:
        errors.append("instance manifest schema_version mismatch")
    for key in (
        "instance_id",
        "instance_schema_version",
        "created_at",
        "updated_at",
        "instance_root",
        "appliance_mode",
        "server_enabled",
        "lan_enabled",
        "stores",
        "policies",
        "warnings",
        "limitations",
    ):
        if key not in manifest:
            errors.append(f"instance manifest missing {key}")
    if Path(str(manifest.get("instance_root", ""))).resolve() != instance_root:
        errors.append("instance manifest instance_root does not match validated path")
    if manifest.get("appliance_mode") != "local":
        errors.append("instance manifest appliance_mode must be local")
    if not isinstance(manifest.get("stores"), dict):
        errors.append("instance manifest stores must be an object")
    if not isinstance(manifest.get("policies"), dict):
        errors.append("instance manifest policies must be an object")


def validate_status(status: Mapping[str, Any], manifest: Mapping[str, Any], errors: list[str]) -> None:
    if status.get("schema_version") != STATUS_SCHEMA_VERSION:
        errors.append("instance status schema_version mismatch")
    if status.get("instance_id") != manifest.get("instance_id"):
        errors.append("status instance_id does not match manifest")
    if status.get("instance_schema_version") != manifest.get("instance_schema_version"):
        errors.append("status instance_schema_version does not match manifest")
    if status.get("status") != "initialized":
        errors.append("status must be initialized")
    stores = status.get("stores")
    if not isinstance(stores, dict):
        errors.append("status stores must be an object")
        return
    for spec in STORE_SPECS:
        if spec.name not in stores:
            errors.append(f"status missing store record: {spec.name}")


def validate_store_manifest(store_manifest: Mapping[str, Any], errors: list[str]) -> None:
    if store_manifest.get("schema_version") != STORE_MANIFEST_SCHEMA_VERSION:
        errors.append("store manifest schema_version mismatch")
    stores = store_manifest.get("stores")
    if not isinstance(stores, dict):
        errors.append("store manifest stores must be an object")
        return
    for spec in STORE_SPECS:
        entry = stores.get(spec.name)
        if not isinstance(entry, dict):
            errors.append(f"store manifest missing store entry: {spec.name}")
            continue
        expected = {
            "store_id": spec.name,
            "store_kind": spec.store_kind,
            "relative_path": spec.relative_path,
            "required": True,
        }
        for key, value in expected.items():
            if entry.get(key) != value:
                errors.append(f"store manifest {spec.name} {key} mismatch")
        for key in ("initialized", "schema_version", "integrity_check_supported", "migration_supported", "last_checked_at"):
            if key not in entry:
                errors.append(f"store manifest {spec.name} missing {key}")


def validate_migration_state(
    migration_state: Mapping[str, Any],
    manifest: Mapping[str, Any],
    version_status: Mapping[str, Any],
    errors: list[str],
) -> None:
    if migration_state.get("schema_version") != MIGRATION_STATE_SCHEMA_VERSION:
        errors.append("migration state schema_version mismatch")
    required = (
        "instance_id",
        "current_instance_schema_version",
        "target_instance_schema_version",
        "migration_needed",
        "migration_allowed",
        "destructive_migration_required",
        "backup_required",
        "rollback_available",
        "migration_history",
        "blockers",
        "warnings",
    )
    for key in required:
        if key not in migration_state:
            errors.append(f"migration state missing {key}")
    if migration_state.get("instance_id") != manifest.get("instance_id"):
        errors.append("migration state instance_id does not match manifest")
    if migration_state.get("current_instance_schema_version") != manifest.get("instance_schema_version"):
        errors.append("migration state current version does not match manifest")
    if migration_state.get("target_instance_schema_version") != CURRENT_INSTANCE_SCHEMA_VERSION:
        errors.append("migration state target version must be current")
    if migration_state.get("destructive_migration_required") is not False:
        errors.append("destructive migration must not be required")
    if migration_state.get("migration_allowed") is not False:
        errors.append("LOCAL-02 migration apply must remain disabled")
    if not isinstance(migration_state.get("migration_history"), list):
        errors.append("migration history must be a list")
    if version_status.get("unsupported") and not migration_state.get("blockers"):
        errors.append("unsupported versions must record migration blockers")


def evaluate_instance_schema_version(value: Any) -> dict[str, Any]:
    blockers: list[str] = []
    try:
        version = int(value)
    except (TypeError, ValueError):
        return {
            "version": value,
            "unsupported": True,
            "migration_needed": True,
            "blockers": ["instance_schema_version must be an integer"],
        }
    unsupported = version < MINIMUM_SUPPORTED_INSTANCE_SCHEMA_VERSION or version > CURRENT_INSTANCE_SCHEMA_VERSION
    if unsupported:
        blockers.append(
            f"unsupported instance_schema_version {version}; supported range is "
            f"{MINIMUM_SUPPORTED_INSTANCE_SCHEMA_VERSION}..{CURRENT_INSTANCE_SCHEMA_VERSION}"
        )
    return {
        "version": version,
        "unsupported": unsupported,
        "migration_needed": version != CURRENT_INSTANCE_SCHEMA_VERSION,
        "blockers": blockers,
    }


def check_store_integrity(store_name: str, db_path: Path) -> dict[str, Any]:
    spec = next(item for item in STORE_SPECS if item.name == store_name)
    try:
        module = importlib.import_module(spec.module)
        store_class = getattr(module, spec.class_name)
        with store_class.open(db_path) as store:
            integrity = store.check_integrity()
        return {
            "status": "pass" if integrity.get("status") == "pass" else "fail",
            "path": str(db_path),
            "runtime_api": f"{spec.module}.{spec.class_name}",
            "integrity": integrity,
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


def validate_false_flags(
    payload: Mapping[str, Any],
    label: str,
    errors: list[str],
    *,
    deployment_key: str = "deployment_enabled",
) -> None:
    for key in ("server_enabled", "lan_enabled", deployment_key, "production_readiness_claimed", "public_launch_readiness_claimed"):
        if payload.get(key) not in (False, None):
            errors.append(f"{label} must set {key}=false")


def committed_instance_state(instance_root: Path) -> list[str]:
    repo = REPO_ROOT.resolve()
    if not is_relative_to(instance_root, repo):
        return []
    rel = instance_root.relative_to(repo).as_posix()
    completed = subprocess.run(["git", "ls-files", "--", rel], cwd=repo, text=True, capture_output=True, check=False)
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
