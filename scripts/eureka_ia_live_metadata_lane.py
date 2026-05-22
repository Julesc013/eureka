#!/usr/bin/env python3
"""Exercise the policy-gated IA live metadata lane for a resolution run."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Sequence, TextIO

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from runtime.local_service.workbench_live_run import (  # noqa: E402
    build_command_response,
    create_workbench_resolution_run,
    get_workbench_resolution_run,
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--query", required=True)
    parser.add_argument("--projection", default="operator_workbench", choices=("operator_workbench", "public_web", "native_desktop_read_only"))
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--mock-live", action="store_true")
    parser.add_argument("--allow-live", action="store_true")
    parser.add_argument("--operator-token", default="")
    parser.add_argument("--max-requests", type=int, default=2)
    parser.add_argument("--rows", type=int, default=5)
    parser.add_argument("--timeout-seconds", type=int, default=15)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--output")
    parser.add_argument("--events-output")
    parser.add_argument("--lanes-output")
    parser.add_argument("--boundary-output")
    args = parser.parse_args(argv)

    packet = create_workbench_resolution_run(
        args.query,
        args.projection,
        include_ia_hunt_dry_run=True,
    )
    command_type = _command_type(args)
    command_response = build_command_response(
        packet["run_id"],
        command_type,
        args.projection,
        operator_token=args.operator_token,
        allow_live=bool(args.allow_live),
        mock_live=bool(args.mock_live),
        max_requests=args.max_requests,
        rows=args.rows,
        timeout_seconds=args.timeout_seconds,
    )
    final_packet = get_workbench_resolution_run(packet["run_id"], args.projection)
    boundary_report = _boundary_report(final_packet, command_response, args)
    result = {
        "schema_version": "ia_live_metadata_lane_cli_result.v0",
        "query": args.query,
        "projection_profile": args.projection,
        "command_type": command_type,
        "command_response": command_response,
        "run_packet": final_packet,
        "events": final_packet["events"],
        "lane_snapshot": final_packet["lane_snapshot"],
        "workunits": final_packet["workunits"],
        "boundary_report": boundary_report,
        "dry_run_passed": command_type == "run_live_ia_metadata_dry_run" and command_response.get("allowed") is True,
        "mock_live_passed": command_type == "run_live_ia_metadata_mock" and command_response.get("allowed") is True,
        "operator_projection_passed": args.projection == "operator_workbench",
        "public_projection_blocked": args.projection == "public_web" and command_response.get("allowed") is False,
        "native_read_only_projection_blocked": args.projection == "native_desktop_read_only" and command_response.get("allowed") is False,
        "operator_approval_required": True,
        "operator_token_required": True,
        "live_smoke_performed": bool(args.allow_live and command_response.get("live_ia_call_performed")),
        "live_smoke_total_http_requests": int(command_response.get("boundary_report", {}).get("live_smoke_total_http_requests", 0) or 0),
        "raw_response_committed": False,
    }
    _write_json(args.output, result)
    _write_json(args.events_output, result["events"])
    _write_json(args.lanes_output, result["lane_snapshot"])
    _write_json(args.boundary_output, boundary_report)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    else:
        print(f"run_id: {final_packet['run_id']}", file=stdout)
        print(f"command: {command_type}", file=stdout)
        print(f"allowed: {command_response.get('allowed')}", file=stdout)
        print(f"state: {command_response.get('state')}", file=stdout)
    return 0


def _command_type(args: argparse.Namespace) -> str:
    if args.allow_live:
        return "run_live_ia_metadata_now"
    if args.mock_live:
        return "run_live_ia_metadata_mock"
    return "run_live_ia_metadata_dry_run"


def _boundary_report(packet: dict[str, Any], command_response: dict[str, Any], args: argparse.Namespace) -> dict[str, Any]:
    command_boundary = dict(command_response.get("boundary_report") or {})
    packet_boundary = dict(packet.get("boundary_report") or {})
    return {
        "schema_version": "ia_live_metadata_lane_cli_boundary_report.v0",
        "run_id": packet.get("run_id", ""),
        "live_smoke_performed": bool(args.allow_live and command_response.get("live_ia_call_performed")),
        "live_smoke_total_http_requests": int(command_boundary.get("live_smoke_total_http_requests", 0) or 0),
        "live_ia_call_performed": bool(command_response.get("live_ia_call_performed", False)),
        "source_probe_executed": bool(command_response.get("source_probe_executed", False)),
        "source_cache_write_performed": False,
        "evidence_write_performed": False,
        "candidate_index_mutated": False,
        "reviewed_index_mutated": False,
        "master_index_mutated": False,
        "operator_instance_mutated": False,
        "raw_response_committed": False,
        "download_performed": False,
        "upload_performed": False,
        "extraction_executed": False,
        "model_provider_used": False,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
        "full_archive_org_integration_claimed": False,
        "packet_boundaries": packet_boundary,
    }


def _write_json(path_value: str | None, payload: Any) -> None:
    if not path_value:
        return
    path = Path(path_value)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
