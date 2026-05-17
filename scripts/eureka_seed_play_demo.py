#!/usr/bin/env python3
"""Dry-run or explicitly load the local workbench play demo pack."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.local_appliance import close_local_appliance, open_local_appliance
from runtime.local_appliance.errors import LocalApplianceError, LocalInstancePathError
from runtime.local_appliance.paths import resolve_instance_root
from runtime.public_index.records import PublicIndexRecord
from runtime.search_hunt.records import SearchHuntSession
from runtime.search_need.records import SearchNeed
from runtime.workunit_queue.records import WorkUnit

from validate_play_seed_pack import build_seed_plan, load_play_pack, validate_play_seed_pack


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout, stderr: TextIO = sys.stderr) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instance", required=True, help="Explicit local instance root, usually ../instances/default.")
    parser.add_argument("--operator-token", help="Operator token required only for --apply.")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="Plan the demo load without writing instance state. This is the default.")
    mode.add_argument("--apply", action="store_true", help="Write demo state to the explicit --instance path.")
    parser.add_argument("--reset-demo-state", action="store_true", help="Reserved for a future explicit cleanup command; never deletes by default.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    args = parser.parse_args(argv)

    try:
        result = seed_play_demo(args)
    except (LocalApplianceError, LocalInstancePathError, ValueError) as exc:
        result = _base_result("fail", str(args.instance))
        result.update({"error": "seed_play_demo_failed", "message": str(exc)})
        emit(result, args.json, stdout)
        print(f"ERROR: {exc}", file=stderr)
        return 2
    emit(result, args.json, stdout)
    return 0 if result["status"] == "pass" else 1


def seed_play_demo(args: argparse.Namespace) -> dict[str, Any]:
    instance_root = resolve_instance_root(args.instance, REPO_ROOT)
    validation = validate_play_seed_pack(run_script_smokes=False)
    if validation["status"] != "pass":
        result = _base_result("fail", str(instance_root))
        result.update({"error": "play_pack_invalid", "validation": validation})
        return result

    pack = load_play_pack([])
    plan = build_seed_plan(pack)
    apply_mode = bool(args.apply)
    if apply_mode and not str(args.operator_token or "").strip():
        raise ValueError("--operator-token is required with --apply")

    result = _base_result("pass", str(instance_root))
    result.update(
        {
            "dry_run": not apply_mode,
            "apply": apply_mode,
            "reset_demo_state_requested": bool(args.reset_demo_state),
            "reset_demo_state_performed": False,
            "plan": plan,
            "validated_examples": True,
            "mutation_performed": False,
            "written_records": {},
            "warnings": [],
        }
    )
    if args.reset_demo_state:
        result["warnings"].append("--reset-demo-state is accepted but performs no deletion in PLAY-00")
    if not apply_mode:
        return result

    runtime = open_local_appliance(instance_root)
    try:
        written = _apply_pack(runtime, pack)
    finally:
        close_local_appliance(runtime)
    result["mutation_performed"] = True
    result["written_records"] = written
    return result


def _apply_pack(runtime: Any, pack: dict[str, Any]) -> dict[str, list[str]]:
    written: dict[str, list[str]] = {
        "reviewed_records": [],
        "hunts": [],
        "search_needs": [],
        "workunits": [],
    }
    for item in pack["reviewed_records"]["records"]:
        record = PublicIndexRecord.from_dict(item)
        runtime.public_index.write_record(record)
        written["reviewed_records"].append(record.record_id)
    for item in pack["hunts"]["hunts"]:
        session = SearchHuntSession.from_dict(item)
        runtime.search_hunt.create_session(session)
        written["hunts"].append(session.id)
    for item in pack["search_needs"]["search_needs"]:
        need = SearchNeed.from_dict(item)
        runtime.search_need.create_need(need)
        written["search_needs"].append(need.id)
    for item in pack["workunits"]["workunits"]:
        workunit = WorkUnit.from_dict(item)
        runtime.workunit_queue.create_workunit(workunit)
        written["workunits"].append(workunit.id)
    return written


def _base_result(status: str, instance: str) -> dict[str, Any]:
    return {
        "schema_version": "play_demo_seed_result.v0",
        "task": "PLAY-00",
        "status": status,
        "instance": instance,
        "fake_evidence_created": False,
        "fake_verified_records_created": False,
        "live_source_call_performed": False,
        "source_probe_executed": False,
        "extraction_executed": False,
        "model_provider_used": False,
        "download_install_execute_performed": False,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }


def emit(result: dict[str, Any], as_json: bool, stdout: TextIO) -> None:
    if as_json:
        print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
        return
    print(f"status: {result['status']}", file=stdout)
    print(f"dry_run: {result.get('dry_run')}", file=stdout)
    if result.get("message"):
        print(str(result["message"]), file=stdout)


if __name__ == "__main__":
    raise SystemExit(main())
