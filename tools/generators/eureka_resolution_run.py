#!/usr/bin/env python3
"""Run and inspect the local E2E reference ResolutionRun runner."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence, TextIO

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from runtime.resolution_run import command_run_bundle, replay_run_bundle, run_e2e_reference_run, run_resolution_dry_run, validate_run_bundle


PROJECTIONS = ("operator_workbench", "public_web", "native_desktop_read_only")
COMMANDS = {"run", "status", "events", "validate", "replay", "command"}


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    args_list = list(argv if argv is not None else sys.argv[1:])
    if args_list and args_list[0] in COMMANDS:
        return _main_subcommand(args_list, stdout)
    return _main_legacy(args_list, stdout)


def _main_legacy(argv: Sequence[str], stdout: TextIO) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--query", required=True)
    parser.add_argument("--projection", choices=PROJECTIONS, default="operator_workbench")
    parser.add_argument("--dry-run", action="store_true", default=True)
    parser.add_argument("--no-ia-hunt", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--output")
    args = parser.parse_args(argv)

    result = run_resolution_dry_run(
        args.query,
        projection_profile=args.projection,
        include_ia_hunt=not args.no_ia_hunt,
    )
    if args.output:
        path = Path(args.output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    else:
        print("Resolution run dry-run", file=stdout)
        print(f"run_id: {result['run']['run_id']}", file=stdout)
        print(f"state: {result['run']['state']}", file=stdout)
        print(f"workunit_count: {result['workunit_schedule'].get('workunit_count', 0)}", file=stdout)
        print(f"lane_count: {result['lane_snapshot'].get('lane_count', 0)}", file=stdout)
    return 0


def _main_subcommand(argv: Sequence[str], stdout: TextIO) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="action", required=True)

    run_parser = subparsers.add_parser("run")
    run_parser.add_argument("--mode", choices=("synthetic", "live-shadow"), default="synthetic")
    run_parser.add_argument("--query", required=True)
    run_parser.add_argument("--projection", choices=PROJECTIONS, default="operator_workbench")
    run_parser.add_argument("--fixture", default="success_two_workunits")
    run_parser.add_argument("--out", default=".eureka/e2e-reference/runs")
    run_parser.add_argument("--json", action="store_true")

    status_parser = subparsers.add_parser("status")
    status_parser.add_argument("--run-dir", required=True)
    status_parser.add_argument("--json", action="store_true")

    events_parser = subparsers.add_parser("events")
    events_parser.add_argument("--run-dir", required=True)
    events_parser.add_argument("--json", action="store_true")

    validate_parser = subparsers.add_parser("validate")
    validate_parser.add_argument("--run-dir", required=True)
    validate_parser.add_argument("--strict", action="store_true")
    validate_parser.add_argument("--json", action="store_true")

    replay_parser = subparsers.add_parser("replay")
    replay_parser.add_argument("--run-dir", required=True)
    replay_parser.add_argument("--strict", action="store_true")
    replay_parser.add_argument("--json", action="store_true")

    command_parser = subparsers.add_parser("command")
    command_parser.add_argument("--run-dir", required=True)
    command_parser.add_argument("--command", dest="run_command", required=True, choices=("pause", "resume", "cancel"))
    command_parser.add_argument("--json", action="store_true")

    args = parser.parse_args(argv)
    if args.action == "run":
        result = run_e2e_reference_run(
            args.query,
            mode=args.mode,
            projection_profile=args.projection,
            fixture=args.fixture,
            out_root=args.out,
            write_bundle=args.mode == "synthetic",
        )
        if args.json:
            print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
        else:
            print("E2E reference runner", file=stdout)
            print(f"run_id: {result['run']['run_id']}", file=stdout)
            print(f"mode: {result['mode']}", file=stdout)
            print(f"state: {result['run']['state']}", file=stdout)
            if result.get("run_dir"):
                print(f"run_dir: {result['run_dir']}", file=stdout)
        return 2 if args.mode == "live-shadow" else 0
    if args.action == "status":
        payload = _load_json(Path(args.run_dir) / "run_manifest.json")
        if args.json:
            print(json.dumps(payload, indent=2, sort_keys=True), file=stdout)
        else:
            print("E2E reference run status", file=stdout)
            print(f"run_id: {payload.get('run_id', '')}", file=stdout)
            print(f"mode: {payload.get('mode', '')}", file=stdout)
            print(f"state: {payload.get('current_state', '')}", file=stdout)
            print(f"event_count: {payload.get('event_count', 0)}", file=stdout)
        return 0
    if args.action == "events":
        payload = _load_jsonl(Path(args.run_dir) / "events.jsonl")
        if args.json:
            print(json.dumps(payload, indent=2, sort_keys=True), file=stdout)
        else:
            for event in payload:
                print(f"{event.get('sequence')}: {event.get('event_type')}", file=stdout)
        return 0
    if args.action == "validate":
        payload = validate_run_bundle(args.run_dir, strict=args.strict, write_report=True)
        print(json.dumps(payload, indent=2, sort_keys=True) if args.json else f"validation: {payload['status']}", file=stdout)
        return 0 if payload["status"] == "valid" else 1
    if args.action == "replay":
        payload = replay_run_bundle(args.run_dir, strict=args.strict)
        print(json.dumps(payload, indent=2, sort_keys=True) if args.json else f"replay: {payload['status']}", file=stdout)
        return 0 if str(payload["status"]).startswith("replay_verified") else 1
    if args.action == "command":
        try:
            payload = command_run_bundle(args.run_dir, args.run_command)
        except Exception as error:
            payload = {"schema_version": "eureka.e2e_reference_command_result.v0", "status": "blocked", "error": str(error)}
            print(json.dumps(payload, indent=2, sort_keys=True) if args.json else f"command blocked: {error}", file=stdout)
            return 1
        print(json.dumps(payload, indent=2, sort_keys=True) if args.json else f"state: {payload['state']}", file=stdout)
        return 0
    return 2


def _load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_jsonl(path: Path) -> list[dict[str, object]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


if __name__ == "__main__":
    raise SystemExit(main())
