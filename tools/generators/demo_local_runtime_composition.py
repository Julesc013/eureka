#!/usr/bin/env python3
"""Demonstrate local appliance runtime composition over an initialized instance."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.local.appliance import LocalApplianceError, close_local_appliance, open_local_appliance


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout, stderr: TextIO = sys.stderr) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instance", help="Explicit initialized local instance root.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    parser.add_argument("--output", help="Optional JSON result output path.")
    args = parser.parse_args(argv)

    if not args.instance:
        result = fail_result("missing_instance", "--instance is required")
        emit_result(result, args.json, args.output, stdout)
        print("ERROR: --instance is required", file=stderr)
        return 2

    instance = Path(args.instance)
    if not instance.exists():
        message = "instance path does not exist; run scripts/eureka_init_instance.py --instance <path> first"
        result = fail_result("missing_initialized_instance", message, instance=args.instance)
        emit_result(result, args.json, args.output, stdout)
        print(f"ERROR: {message}", file=stderr)
        return 2

    runtime = None
    try:
        runtime = open_local_appliance(instance)
        integrity = runtime.check_integrity()
        status = runtime.status().to_dict()
        result = {
            "schema_version": "local_runtime_composition_demo.v0",
            "status": "pass" if integrity.get("status") == "pass" and status.get("status") == "pass" else "fail",
            "instance_root": status.get("instance_root"),
            "instance_id": status.get("instance_id"),
            "config_loaded": True,
            "store_manifest_loaded": True,
            "migration_state_loaded": True,
            "stores_opened": {
                "source_cache": True,
                "evidence_ledger": True,
                "review_queue": True,
                "public_index": True,
            },
            "integrity": integrity,
            "runtime_status": status,
            "server_enabled": False,
            "lan_enabled": False,
            "deployment_performed": False,
            "production_readiness_claimed": False,
            "public_launch_readiness_claimed": False,
        }
    except LocalApplianceError as exc:
        result = fail_result("composition_demo_failed", str(exc), instance=args.instance)
        emit_result(result, args.json, args.output, stdout)
        print(f"ERROR: {exc}", file=stderr)
        return 2
    except Exception as exc:  # pragma: no cover - defensive CLI boundary
        result = fail_result("composition_demo_failed", str(exc), instance=args.instance)
        emit_result(result, args.json, args.output, stdout)
        print(f"ERROR: {exc}", file=stderr)
        return 1
    finally:
        if runtime is not None:
            close_local_appliance(runtime)

    emit_result(result, args.json, args.output, stdout)
    return 0 if result.get("status") == "pass" else 1


def fail_result(code: str, message: str, *, instance: str | None = None) -> dict[str, Any]:
    result: dict[str, Any] = {
        "schema_version": "local_runtime_composition_demo.v0",
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


def emit_result(result: dict[str, Any], as_json: bool, output: str | None, stdout: TextIO) -> None:
    if output:
        write_json(Path(output), result)
    if as_json:
        print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
        return
    print(f"status: {result['status']}", file=stdout)
    if result.get("instance_root"):
        print(f"instance_root: {result['instance_root']}", file=stdout)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
