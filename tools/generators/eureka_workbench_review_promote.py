#!/usr/bin/env python3
"""Run the Workbench review/promotion-preview flow."""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.local.appliance import close_local_appliance, open_local_appliance
from runtime.local.service.workbench_review_promote import (
    PROJECTION_PROFILES,
    REVIEW_DECISIONS,
    SAMPLE_CANDIDATE,
    run_review_promote_flow,
)
from scripts.eureka_init_instance import initialize_instance


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout, stderr: TextIO = sys.stderr) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--from-fixtures", action="store_true")
    parser.add_argument("--from-ia-examples", action="store_true")
    parser.add_argument("--candidate-id")
    parser.add_argument("--decision", choices=REVIEW_DECISIONS, default="accept_local_reviewed")
    parser.add_argument("--operator-token", default="")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--use-temp-instance", action="store_true")
    parser.add_argument("--apply-to-temp", action="store_true")
    parser.add_argument("--projection", choices=PROJECTION_PROFILES, default="operator_workbench")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--output")
    parser.add_argument("--boundary-output")
    args = parser.parse_args(argv)

    runtime = None
    tmpdir: tempfile.TemporaryDirectory[str] | None = None
    try:
        candidate = build_candidate(args.candidate_id, from_ia_examples=args.from_ia_examples)
        if args.apply_to_temp:
            if not args.use_temp_instance:
                raise ValueError("--apply-to-temp requires --use-temp-instance")
            tmpdir = tempfile.TemporaryDirectory(prefix="eureka-review-promote-")
            instance = Path(tmpdir.name) / "eureka-instance"
            init = initialize_instance(instance)
            if init.get("status") not in {"pass", "pass_with_warnings"}:
                raise ValueError("temp instance initialization failed")
            runtime = open_local_appliance(instance)
        result = run_review_promote_flow(
            candidate=candidate,
            decision=args.decision,
            projection_profile=args.projection,
            operator_token=args.operator_token,
            dry_run=bool(args.dry_run or not args.apply_to_temp),
            runtime=runtime,
            apply_to_temp=bool(args.apply_to_temp),
        )
    except Exception as exc:
        result = {
            "schema_version": "workbench_review_promote_cli_result.v0",
            "status": "fail",
            "error": "workbench_review_promote_failed",
            "message": str(exc),
            "operator_instance_mutated": False,
            "master_index_mutated": False,
            "committed_data_public_index_mutated": False,
            "download_performed": False,
            "extraction_executed": False,
            "model_provider_used": False,
            "deployment_performed": False,
            "warnings": [],
            "limitations": ["CLI failed before any review/promote mutation outside temp scope."],
        }
        emit(result, args, stdout)
        print(f"ERROR: {exc}", file=stderr)
        return 2
    finally:
        if runtime is not None:
            close_local_appliance(runtime)
        if tmpdir is not None:
            tmpdir.cleanup()

    emit(result, args, stdout)
    return 0 if result.get("status") in {"pass", "pass_with_warnings"} else 1


def build_candidate(candidate_id: str | None, *, from_ia_examples: bool = False) -> dict[str, Any]:
    candidate = dict(SAMPLE_CANDIDATE)
    if candidate_id:
        candidate["candidate_id"] = candidate_id
    if from_ia_examples:
        candidate.update(
            {
                "candidate_source": "IA metadata candidates",
                "source_id": "source.internet_archive.metadata.fixture",
                "source_family": "internet_archive_metadata",
                "source_locator": "fixture:ia-live-metadata-lane:sampleproject",
                "summary": "Fixture IA metadata candidate for Workbench review/promotion preview.",
            }
        )
    return candidate


def emit(result: dict[str, Any], args: argparse.Namespace, stdout: TextIO) -> None:
    if args.output:
        write_json(Path(args.output), result)
    if args.boundary_output:
        write_json(Path(args.boundary_output), dict(result.get("boundary_report") or {}))
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    else:
        print(f"status: {result.get('status', 'unknown')}", file=stdout)


def write_json(path: Path, payload: Mapping[str, Any] | dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(dict(payload), indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
