#!/usr/bin/env python3
"""Report local Eureka instance migration status without mutating state."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence, TextIO

from eureka_init_instance import (
    CURRENT_INSTANCE_SCHEMA_VERSION,
    MINIMUM_SUPPORTED_INSTANCE_SCHEMA_VERSION,
    TASK_ID,
    InstancePathError,
    validate_instance_path,
    write_json,
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout, stderr: TextIO = sys.stderr) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instance", help="Explicit local instance root to inspect.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    parser.add_argument("--output", help="Optional JSON result output path.")
    args = parser.parse_args(argv)

    if not args.instance:
        result = fail_result("missing_instance", "--instance is required")
        emit(result, args.json, args.output, stdout)
        print("ERROR: --instance is required", file=stderr)
        return 2

    try:
        result = migration_status(Path(args.instance))
    except InstancePathError as exc:
        result = fail_result("forbidden_instance_path", str(exc), instance=args.instance)
        emit(result, args.json, args.output, stdout)
        print(f"ERROR: {exc}", file=stderr)
        return 2
    except Exception as exc:  # pragma: no cover - defensive CLI boundary
        result = fail_result("migration_status_failed", str(exc), instance=args.instance)
        emit(result, args.json, args.output, stdout)
        print(f"ERROR: {exc}", file=stderr)
        return 1

    emit(result, args.json, args.output, stdout)
    return 0 if result["status"] in {"pass", "pass_with_warnings"} else 1


def migration_status(instance: Path) -> dict[str, Any]:
    instance_root = validate_instance_path(instance)
    manifest = load_json(instance_root / "config" / "instance.json")
    store_manifest = load_json(instance_root / "config" / "store_manifest.json")
    migration_state = load_json(instance_root / "config" / "migration_state.json")
    version = manifest.get("instance_schema_version")
    blockers: list[str] = []
    warnings: list[str] = []
    migration_needed = False

    try:
        version_int = int(version)
    except (TypeError, ValueError):
        version_int = None
        migration_needed = True
        blockers.append("instance_schema_version must be an integer")

    if version_int is not None:
        if version_int < MINIMUM_SUPPORTED_INSTANCE_SCHEMA_VERSION or version_int > CURRENT_INSTANCE_SCHEMA_VERSION:
            migration_needed = True
            blockers.append(
                f"unsupported instance_schema_version {version_int}; supported range is "
                f"{MINIMUM_SUPPORTED_INSTANCE_SCHEMA_VERSION}..{CURRENT_INSTANCE_SCHEMA_VERSION}"
            )
        elif version_int != CURRENT_INSTANCE_SCHEMA_VERSION:
            migration_needed = True
            warnings.append("instance schema version differs from current")

    if migration_state.get("destructive_migration_required") is True:
        blockers.append("destructive migration is forbidden")
    state_blockers = migration_state.get("blockers", [])
    if isinstance(state_blockers, list):
        blockers.extend(str(item) for item in state_blockers)
    state_warnings = migration_state.get("warnings", [])
    if isinstance(state_warnings, list):
        warnings.extend(str(item) for item in state_warnings)

    status = "pass_with_warnings" if blockers or warnings or migration_needed else "pass"
    return {
        "schema_version": "local_instance_migration_status.v0",
        "task": TASK_ID,
        "status": status,
        "instance_root": str(instance_root),
        "instance_id": manifest.get("instance_id"),
        "current_instance_schema_version": version,
        "target_instance_schema_version": CURRENT_INSTANCE_SCHEMA_VERSION,
        "minimum_supported_instance_schema_version": MINIMUM_SUPPORTED_INSTANCE_SCHEMA_VERSION,
        "migration_needed": migration_needed or bool(migration_state.get("migration_needed")),
        "migration_allowed": False,
        "destructive_migration_required": bool(migration_state.get("destructive_migration_required")),
        "backup_required": bool(migration_state.get("backup_required")) or migration_needed,
        "rollback_available": bool(migration_state.get("rollback_available")),
        "store_manifest_present": bool(store_manifest),
        "migration_state_present": bool(migration_state),
        "blockers": sorted(set(blockers)),
        "warnings": sorted(set(warnings)),
        "server_enabled": False,
        "lan_enabled": False,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def fail_result(code: str, message: str, *, instance: str | None = None) -> dict[str, Any]:
    result: dict[str, Any] = {
        "schema_version": "local_instance_migration_status.v0",
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


def emit(result: dict[str, Any], as_json: bool, output: str | None, stdout: TextIO) -> None:
    if output:
        write_json(Path(output), result)
    if as_json:
        print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
        return
    print(f"status: {result['status']}", file=stdout)
    if result.get("instance_root"):
        print(f"instance_root: {result['instance_root']}", file=stdout)
    if result.get("migration_needed") is not None:
        print(f"migration_needed: {result['migration_needed']}", file=stdout)
    for blocker in result.get("blockers", []):
        print(f"BLOCKER: {blocker}", file=stdout)
    for warning in result.get("warnings", []):
        print(f"WARN: {warning}", file=stdout)


if __name__ == "__main__":
    raise SystemExit(main())
