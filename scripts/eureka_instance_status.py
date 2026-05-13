#!/usr/bin/env python3
"""Print the status of an explicit local Eureka appliance instance."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence, TextIO

from eureka_init_instance import TASK_ID, InstancePathError, validate_instance_path


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout, stderr: TextIO = sys.stderr) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instance", help="Explicit local instance root to inspect.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    args = parser.parse_args(argv)

    if not args.instance:
        result = fail_result("missing_instance", "--instance is required")
        emit(result, args.json, stdout)
        print("ERROR: --instance is required", file=stderr)
        return 2
    try:
        result = read_status(Path(args.instance))
    except InstancePathError as exc:
        result = fail_result("forbidden_instance_path", str(exc), instance=args.instance)
        emit(result, args.json, stdout)
        print(f"ERROR: {exc}", file=stderr)
        return 2
    except Exception as exc:  # pragma: no cover - defensive CLI boundary
        result = fail_result("status_read_failed", str(exc), instance=args.instance)
        emit(result, args.json, stdout)
        print(f"ERROR: {exc}", file=stderr)
        return 1

    emit(result, args.json, stdout)
    return 0 if result["status"] in {"pass", "pass_with_warnings"} else 1


def read_status(instance: Path) -> dict[str, Any]:
    instance_root = validate_instance_path(instance)
    manifest = json.loads((instance_root / "config" / "instance.json").read_text(encoding="utf-8"))
    status = json.loads((instance_root / "run" / "status.json").read_text(encoding="utf-8"))
    stores = status.get("stores", {}) if isinstance(status.get("stores"), dict) else {}
    failing = [name for name, payload in stores.items() if isinstance(payload, dict) and payload.get("status") != "pass"]
    return {
        "schema_version": "local_instance_status_summary.v0",
        "task": TASK_ID,
        "status": "pass_with_warnings" if failing else "pass",
        "instance_root": str(instance_root),
        "instance_id": manifest.get("instance_id"),
        "appliance_mode": manifest.get("appliance_mode"),
        "store_count": len(stores),
        "stores": stores,
        "warnings": status.get("warnings", []),
        "limitations": status.get("limitations", []),
        "server_enabled": False,
        "lan_enabled": False,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }


def fail_result(code: str, message: str, *, instance: str | None = None) -> dict[str, Any]:
    result: dict[str, Any] = {
        "schema_version": "local_instance_status_summary.v0",
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


def emit(result: dict[str, Any], as_json: bool, stdout: TextIO) -> None:
    if as_json:
        print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
        return
    print(f"status: {result['status']}", file=stdout)
    if result.get("instance_root"):
        print(f"instance_root: {result['instance_root']}", file=stdout)
    if result.get("store_count") is not None:
        print(f"store_count: {result['store_count']}", file=stdout)
    if result.get("warnings"):
        print("warnings:", file=stdout)
        for warning in result["warnings"]:
            print(f"- {warning}", file=stdout)


if __name__ == "__main__":
    raise SystemExit(main())
