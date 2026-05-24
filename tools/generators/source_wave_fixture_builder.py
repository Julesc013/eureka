#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from runtime.source.action import (
    get_source_family_manifest,
    list_registered_source_families,
    redact_run_for_cli,
    run_source_family_fixture_action,
    smoke_source_wave_families,
    write_json_if_requested,
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    invoked_as = Path(sys.argv[0]).stem
    args = list(argv if argv is not None else sys.argv[1:])
    if "smoke" in invoked_as or "--all-families" in args:
        return smoke_main(argv, stdout)
    return wave_main(argv, stdout)


def wave_main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description="Run SOURCE-WAVE-00 fixture actions through SourceActionKernel.")
    parser.add_argument("--list-families", action="store_true")
    parser.add_argument("--family")
    parser.add_argument("--action-kind")
    parser.add_argument("--query", default="sampleproject")
    parser.add_argument("--transport", choices=("fixture", "mock_live"), default="fixture")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--output")
    args = parser.parse_args(argv)

    if args.list_families:
        payload: dict[str, Any] = {
            "schema_version": "source_wave_family_list.v0",
            "families": list_registered_source_families(),
            "manifests": {family: get_source_family_manifest(family) for family in list_registered_source_families()},
            "live_source_call_performed": False,
            "source_probe_executed": False,
        }
    else:
        if not args.family:
            parser.error("--family is required unless --list-families is used")
        manifest = get_source_family_manifest(args.family)
        action_kind = args.action_kind or manifest["supported_capabilities"][0]
        payload = redact_run_for_cli(
            run_source_family_fixture_action(
                args.family,
                action_kind,
                args.query,
                transport=args.transport,
            )
        )
    write_json_if_requested(payload, args.output)
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True), file=stdout)
    else:
        if args.list_families:
            print("\n".join(payload["families"]), file=stdout)
        else:
            print(f"source wave action: {payload.get('status')}", file=stdout)
            print(f"source_family: {payload.get('source_family')}", file=stdout)
    return 0 if payload.get("status", "pass") not in {"fail", "failed"} else 1


def smoke_main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description="Run SOURCE-WAVE-00 fixture smoke across all required families.")
    parser.add_argument("--all-families", action="store_true")
    parser.add_argument("--transport", choices=("fixture", "mock_live"), default="fixture")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--output")
    parser.add_argument("--boundary-output")
    args = parser.parse_args(argv)
    if not args.all_families:
        parser.error("--all-families is required for source wave smoke")
    payload = smoke_source_wave_families(transport=args.transport)
    write_json_if_requested(payload, args.output)
    if args.boundary_output:
        boundary = {
            "schema_version": "source_wave_boundary_report.v0",
            "family_count": payload["family_count"],
            "families": payload["families"],
            "live_source_call_performed": False,
            "source_probe_executed": False,
            "raw_live_source_response_committed": False,
            "source_cache_write_performed": False,
            "evidence_write_performed": False,
            "candidate_index_mutated": False,
            "reviewed_index_mutated": False,
            "master_index_mutated": False,
            "operator_instance_mutated": False,
            "download_performed": False,
            "upload_performed": False,
            "extraction_executed": False,
            "model_provider_used": False,
            "deployment_performed": False,
            "production_readiness_claimed": False,
            "public_launch_readiness_claimed": False,
        }
        write_json_if_requested(boundary, args.boundary_output)
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True), file=stdout)
    else:
        print(f"source wave smoke: {payload['status']}", file=stdout)
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
