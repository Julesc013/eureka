#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from runtime.connectors.fixture_source_action import build_adapter
from runtime.connectors.internet_archive_metadata import build_registration
from runtime.source.action import (
    build_source_action_scorecard,
    load_source_action_manifest,
    redact_run_for_cli,
    register_source_action_adapter,
    reset_source_action_registry_for_tests,
    run_source_action,
    validate_source_action_manifest,
    write_json_if_requested,
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    invoked_as = Path(sys.argv[0]).stem
    if "manifest" in invoked_as:
        return manifest_main(argv, stdout)
    if "scorecard" in invoked_as:
        return scorecard_main(argv, stdout)
    return action_main(argv, stdout)


def action_main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description="Run a deterministic Eureka source action.")
    parser.add_argument("--source-family", choices=("fixture_source_action", "internet_archive_metadata"), default="fixture_source_action")
    parser.add_argument("--action-kind", default="metadata_search")
    parser.add_argument("--query", required=True)
    parser.add_argument("--transport", choices=("fixture", "mock_live", "operator_approved_live"), default="fixture")
    parser.add_argument("--dry-run", action="store_true", default=True)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--output")
    parser.add_argument("--boundary-output")
    args = parser.parse_args(argv)

    reset_source_action_registry_for_tests()
    adapter = build_adapter()
    register_source_action_adapter(adapter)
    if args.source_family == "internet_archive_metadata":
        # SOURCE-ACTION-KERNEL-00 only registers the IA reference shape. It does
        # not run or change the existing IA live metadata lane.
        run = {
            "schema_version": "source_action_run.v0",
            "record_type": "source_action_run",
            "source_family": "internet_archive_metadata",
            "source_action_id": build_registration()["source_action_id"],
            "status": "registration_stub_only",
            "registration": build_registration(),
            "dry_run": True,
            "live_call_performed": False,
            "accepted_truth": False,
            "review_required": True,
            "limitations": ["registration_stub_only", "no_live_ia_call_performed"],
            "non_claims": ["not_source_expansion", "not_live_source_behavior"],
            "boundary_report": {
                "schema_version": "source_action_boundary_report.v0",
                "source_family": "internet_archive_metadata",
                "live_call_performed": False,
                "raw_response_committed": False,
                "source_cache_write_performed": False,
                "evidence_write_performed": False,
                "candidate_write_performed": False,
                "reviewed_index_mutated": False,
                "master_index_mutated": False,
                "operator_instance_mutated": False,
                "download_performed": False,
                "extraction_executed": False,
                "model_provider_used": False,
                "deployment_performed": False,
                "production_readiness_claimed": False,
                "public_launch_readiness_claimed": False,
            },
        }
    else:
        run = run_source_action(
            query=args.query,
            source_family=args.source_family,
            action_kind=args.action_kind,
            transport_mode=args.transport,
            dry_run=args.dry_run,
        )
    payload = redact_run_for_cli(run)
    write_json_if_requested(payload, args.output)
    if args.boundary_output:
        write_json_if_requested(payload.get("boundary_report", {}), args.boundary_output)
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True), file=stdout)
    else:
        print(f"source action: {payload.get('status')}", file=stdout)
        print(f"source_family: {payload.get('source_family')}", file=stdout)
    return 0 if payload.get("status") != "failed" else 1


def manifest_main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description="Validate a Eureka source action manifest.")
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--validate", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    manifest = load_source_action_manifest(args.manifest)
    result = validate_source_action_manifest(manifest)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    else:
        print(f"manifest validation: {result['status']}", file=stdout)
        for error in result["errors"]:
            print(f"ERROR: {error}", file=stdout)
    return 0 if result["status"] == "pass" else 1


def scorecard_main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description="Build a deterministic source action scorecard.")
    parser.add_argument("--source-family", default="fixture_source_action")
    parser.add_argument("--from-examples", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    observations: list[dict[str, Any]] = []
    if args.from_examples:
        example = REPO_ROOT / "examples/source_actions/fixture_source_observation_envelope.json"
        if example.is_file():
            observations = json.loads(example.read_text(encoding="utf-8")).get("observations", [])
    payload = build_source_action_scorecard(args.source_family, observations)
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True), file=stdout)
    else:
        print(f"scorecard: {payload['source_family']}", file=stdout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
