#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from runtime.capabilities import build_capability_profile, validate_capability_profile
from runtime.relay import build_relay_from_snapshot
from runtime.relay.validation import validate_relay_manifest
from runtime.snapshots.relay_foundation import (
    build_snapshot_from_examples,
    validate_snapshot_envelope,
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    invoked_as = Path(sys.argv[0]).stem
    args = list(argv if argv is not None else sys.argv[1:])
    if "validate_snapshot_relay" in invoked_as:
        from tools.validators.validate_snapshot_relay import main as validate_main

        return validate_main(argv, stdout)
    if "snapshot_validate" in invoked_as or ("--snapshot" in args and "--query" not in args and "--projection" not in args):
        return snapshot_validate_main(argv, stdout)
    if "relay_project" in invoked_as or "--query" in args or "--projection" in args:
        return relay_project_main(argv, stdout)
    if "relay_validate" in invoked_as or "--relay" in args:
        return relay_validate_main(argv, stdout)
    if "capability_profile" in invoked_as or "--profile" in args:
        return capability_profile_main(argv, stdout)
    return snapshot_build_main(argv, stdout)


def snapshot_build_main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description="Build a deterministic reviewed-record snapshot fixture.")
    parser.add_argument("--from-examples", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--output")
    parser.add_argument("--integrity-output")
    parser.add_argument("--boundary-output")
    args = parser.parse_args(argv)
    if not args.from_examples:
        parser.error("--from-examples is required")
    payload = build_snapshot_from_examples()
    write_json_if_requested(payload, args.output)
    write_json_if_requested(payload["integrity_manifest"], args.integrity_output)
    write_json_if_requested(payload["boundary_report"], args.boundary_output)
    emit(payload, args.json, stdout, "snapshot build")
    return 0


def snapshot_validate_main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description="Validate a snapshot envelope.")
    parser.add_argument("--snapshot", required=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    payload = json.loads((REPO_ROOT / args.snapshot).read_text(encoding="utf-8"))
    result = validate_snapshot_envelope(payload)
    emit(result, args.json, stdout, "snapshot validation")
    return 0 if result["status"] == "pass" else 1


def relay_project_main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description="Project a read-only relay response from a snapshot fixture.")
    parser.add_argument("--snapshot", required=True)
    parser.add_argument("--query", required=True)
    parser.add_argument(
        "--projection",
        choices=("public_api_read_only", "public_web_read_only", "native_desktop_read_only", "lite_client_read_only", "text_client_read_only"),
        default="public_api_read_only",
    )
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    build = build_snapshot_from_examples()
    relay = build_relay_from_snapshot(build, args.projection)
    projection = dict(relay["relay_projection"])
    projection["query_response"]["query"] = args.query
    emit(projection, args.json, stdout, "relay projection")
    return 0


def relay_validate_main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description="Validate a relay manifest.")
    parser.add_argument("--relay", required=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    payload = json.loads((REPO_ROOT / args.relay).read_text(encoding="utf-8"))
    result = validate_relay_manifest(payload)
    emit(result, args.json, stdout, "relay validation")
    return 0 if result["status"] == "pass" else 1


def capability_profile_main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description="Build a read-only snapshot relay capability profile.")
    parser.add_argument("--profile", required=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    payload = build_capability_profile(args.profile)
    payload["validation"] = validate_capability_profile(payload)
    emit(payload, args.json, stdout, "capability profile")
    return 0


def emit(payload: dict[str, Any], as_json: bool, stdout: TextIO, label: str) -> None:
    if as_json:
        print(json.dumps(payload, indent=2, sort_keys=True), file=stdout)
    else:
        print(f"{label}: {payload.get('status', payload.get('schema_version', 'ok'))}", file=stdout)


def write_json_if_requested(payload: Any, output: str | None) -> None:
    if not output:
        return
    path = Path(output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
