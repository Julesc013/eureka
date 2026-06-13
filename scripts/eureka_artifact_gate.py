#!/usr/bin/env python3
"""Seed and inspect the local reviewed-artifact gate evidence workflow."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.local.artifact_gate_seed import (
    DEFAULT_CANDIDATES_FILE,
    DEFAULT_GATE_DIR,
    DEFAULT_GATE_REPORT_FILE,
    DEFAULT_MANUAL_BATCH_DIR,
    DEFAULT_SOURCE_COLLECTION_DIR,
    create_manual_batch_plan,
    create_source_collection_plan,
    evidence_templates_from_candidates,
    export_launch_report,
    gate_status,
    ingest_manual_evidence,
    ingest_source_observations,
    list_artifact_gate_candidates,
    manual_batch_status,
    read_jsonl,
    render_source_collection_status,
    render_status,
    review_manual_batch,
    seed_artifact_gate,
    source_collection_status,
    source_observations_to_evidence,
    validate_manual_batch,
    validate_evidence_packet,
    validate_gate,
    validate_source_collection,
    write_manual_batch_report,
    write_manual_evidence_template,
    write_source_collection_report,
    write_source_observation_template,
    write_jsonl,
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout, stderr: TextIO = sys.stderr) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    candidates_parser = subparsers.add_parser("candidates", help="Write local artifact-gate seed candidates.")
    candidates_parser.add_argument("--index", required=True)
    candidates_parser.add_argument("--out", required=True)
    candidates_parser.add_argument("--json", action="store_true")

    template_parser = subparsers.add_parser("evidence-template", help="Write manual evidence template JSONL from candidates.")
    template_parser.add_argument("--candidates", required=True)
    template_parser.add_argument("--out", required=True)
    template_parser.add_argument("--json", action="store_true")

    seed_parser = subparsers.add_parser("seed", help="Write a full local artifact-gate seed directory.")
    seed_parser.add_argument("--index", required=True)
    seed_parser.add_argument("--out", default=DEFAULT_GATE_DIR)
    seed_parser.add_argument("--max-records", type=int, default=5)
    seed_parser.add_argument("--json", action="store_true")

    validate_parser = subparsers.add_parser("validate", help="Validate a local artifact-gate seed directory.")
    validate_parser.add_argument("--gate", required=True)
    validate_parser.add_argument("--json", action="store_true")

    status_parser = subparsers.add_parser("status", help="Print artifact-gate seed status.")
    status_parser.add_argument("--gate", required=True)
    status_parser.add_argument("--json", action="store_true")

    export_parser = subparsers.add_parser("export-launch-report", help="Export the gate report for the public-alpha launch gate.")
    export_parser.add_argument("--gate", required=True)
    export_parser.add_argument("--out", required=True)
    export_parser.add_argument("--json", action="store_true")

    validate_evidence_parser = subparsers.add_parser("validate-evidence", help="Validate evidence packet JSON or JSONL.")
    validate_evidence_parser.add_argument("--evidence", required=True)
    validate_evidence_parser.add_argument("--json", action="store_true")

    manual_plan_parser = subparsers.add_parser("manual-plan", help="Create a manual artifact evidence batch plan.")
    manual_plan_parser.add_argument("--gate", required=True)
    manual_plan_parser.add_argument("--out", default=DEFAULT_MANUAL_BATCH_DIR)
    manual_plan_parser.add_argument("--target-records", type=int, default=5)
    manual_plan_parser.add_argument("--json", action="store_true")

    manual_template_parser = subparsers.add_parser("manual-template", help="Write manual evidence packet templates for a batch.")
    manual_template_parser.add_argument("--batch", required=True)
    manual_template_parser.add_argument("--out", required=True)
    manual_template_parser.add_argument("--json", action="store_true")

    manual_ingest_parser = subparsers.add_parser("manual-ingest", help="Ingest filled manual evidence packets into a batch.")
    manual_ingest_parser.add_argument("--batch", required=True)
    manual_ingest_parser.add_argument("--evidence", required=True)
    manual_ingest_parser.add_argument("--json", action="store_true")

    manual_validate_parser = subparsers.add_parser("manual-validate", help="Validate a manual evidence batch.")
    manual_validate_parser.add_argument("--batch", required=True)
    manual_validate_parser.add_argument("--json", action="store_true")

    manual_review_parser = subparsers.add_parser("manual-review", help="Materialize reviewed artifact records from valid eligible manual packets.")
    manual_review_parser.add_argument("--batch", required=True)
    manual_review_parser.add_argument("--reviewer", required=True)
    manual_review_parser.add_argument("--out", required=True)
    manual_review_parser.add_argument("--json", action="store_true")

    manual_report_parser = subparsers.add_parser("manual-report", help="Write a manual batch artifact gate report.")
    manual_report_parser.add_argument("--batch", required=True)
    manual_report_parser.add_argument("--out", required=True)
    manual_report_parser.add_argument("--json", action="store_true")

    manual_status_parser = subparsers.add_parser("manual-status", help="Print manual evidence batch status.")
    manual_status_parser.add_argument("--batch", required=True)
    manual_status_parser.add_argument("--json", action="store_true")

    source_plan_parser = subparsers.add_parser("source-plan", help="Create a bounded artifact evidence source collection plan.")
    source_plan_parser.add_argument("--gate", required=True)
    source_plan_parser.add_argument("--manual-batch", required=True)
    source_plan_parser.add_argument("--out", default=DEFAULT_SOURCE_COLLECTION_DIR)
    source_plan_parser.add_argument("--target-records", type=int, default=5)
    source_plan_parser.add_argument("--json", action="store_true")

    source_template_parser = subparsers.add_parser("source-template", help="Write source observation templates for a collection.")
    source_template_parser.add_argument("--collection", required=True)
    source_template_parser.add_argument("--out", required=True)
    source_template_parser.add_argument("--json", action="store_true")

    source_ingest_parser = subparsers.add_parser("source-ingest", help="Ingest source observation packets into a collection.")
    source_ingest_parser.add_argument("--collection", required=True)
    source_ingest_parser.add_argument("--observations", required=True)
    source_ingest_parser.add_argument("--json", action="store_true")

    source_validate_parser = subparsers.add_parser("source-validate", help="Validate a source observation collection.")
    source_validate_parser.add_argument("--collection", required=True)
    source_validate_parser.add_argument("--json", action="store_true")

    source_to_evidence_parser = subparsers.add_parser("source-to-evidence", help="Convert valid source observations to manual evidence packets.")
    source_to_evidence_parser.add_argument("--collection", required=True)
    source_to_evidence_parser.add_argument("--out", required=True)
    source_to_evidence_parser.add_argument("--json", action="store_true")

    source_report_parser = subparsers.add_parser("source-report", help="Write a source collection report.")
    source_report_parser.add_argument("--collection", required=True)
    source_report_parser.add_argument("--out", required=True)
    source_report_parser.add_argument("--json", action="store_true")

    source_status_parser = subparsers.add_parser("source-status", help="Print source collection status.")
    source_status_parser.add_argument("--collection", required=True)
    source_status_parser.add_argument("--json", action="store_true")

    args = parser.parse_args(argv)
    try:
        if args.command == "candidates":
            payload = list_artifact_gate_candidates(args.index)
            write_jsonl(args.out, payload["candidates"])
            summary = {
                "status": "pass",
                "out": args.out,
                "candidate_count": payload["candidate_count"],
                "seed_candidate_count": payload["seed_candidate_count"],
                "excluded_candidate_count": payload["excluded_candidate_count"],
                "artifact_verified_count": payload["artifact_verified_count"],
            }
            return _emit(summary, args.json, stdout)

        if args.command == "evidence-template":
            candidates = read_jsonl(args.candidates)
            templates = evidence_templates_from_candidates(candidates)
            write_jsonl(args.out, templates)
            return _emit({"status": "pass", "out": args.out, "template_count": len(templates)}, args.json, stdout)

        if args.command == "seed":
            report = seed_artifact_gate(args.index, args.out, max_records=args.max_records)
            return _emit(_seed_summary(args.out, report), args.json, stdout)

        if args.command == "validate":
            errors = validate_gate(args.gate)
            payload = {"status": "pass" if not errors else "fail", "gate": args.gate, "errors": errors}
            return _emit(payload, args.json, stdout, stderr=stderr, failed=bool(errors))

        if args.command == "status":
            payload = gate_status(args.gate)
            if args.json:
                return _emit(payload, True, stdout, stderr=stderr, failed=payload.get("status") != "pass")
            print(render_status(payload), end="", file=stdout if payload.get("status") == "pass" else stderr)
            return 0 if payload.get("status") == "pass" else 1

        if args.command == "export-launch-report":
            report = export_launch_report(args.gate, args.out)
            payload = {
                "status": "pass",
                "gate": args.gate,
                "out": args.out,
                "gate_status": report.get("gate_status"),
                "reviewed_artifact_gate_count": report.get("reviewed_artifact_gate_count"),
                "artifact_verified_count": report.get("artifact_verified_count"),
            }
            return _emit(payload, args.json, stdout)

        if args.command == "validate-evidence":
            packets = _load_evidence(args.evidence)
            errors: list[str] = []
            for index, packet in enumerate(packets, start=1):
                errors.extend(f"packet[{index}]: {error}" for error in validate_evidence_packet(packet))
            payload = {"status": "pass" if not errors else "fail", "evidence": args.evidence, "packet_count": len(packets), "errors": errors}
            return _emit(payload, args.json, stdout, stderr=stderr, failed=bool(errors))

        if args.command == "manual-plan":
            payload = create_manual_batch_plan(args.gate, args.out, target_records=args.target_records)
            return _emit(payload, args.json, stdout)

        if args.command == "manual-template":
            payload = write_manual_evidence_template(args.batch, args.out)
            return _emit(payload, args.json, stdout)

        if args.command == "manual-ingest":
            payload = ingest_manual_evidence(args.batch, args.evidence)
            return _emit(payload, args.json, stdout, stderr=stderr, failed=payload.get("status") == "fail")

        if args.command == "manual-validate":
            payload = validate_manual_batch(args.batch)
            failed = payload.get("status") == "fail"
            return _emit(payload, args.json, stdout, stderr=stderr, failed=failed)

        if args.command == "manual-review":
            payload = review_manual_batch(args.batch, reviewer=args.reviewer, out_path=args.out)
            return _emit(payload, args.json, stdout)

        if args.command == "manual-report":
            payload = write_manual_batch_report(args.batch, args.out)
            return _emit(_manual_report_summary(args.out, payload), args.json, stdout)

        if args.command == "manual-status":
            payload = manual_batch_status(args.batch)
            if args.json:
                return _emit(payload, True, stdout)
            print(render_manual_batch_status(payload), end="", file=stdout)
            return 0

        if args.command == "source-plan":
            payload = create_source_collection_plan(args.gate, args.manual_batch, args.out, target_records=args.target_records)
            return _emit(payload, args.json, stdout)

        if args.command == "source-template":
            payload = write_source_observation_template(args.collection, args.out)
            return _emit(payload, args.json, stdout)

        if args.command == "source-ingest":
            payload = ingest_source_observations(args.collection, args.observations)
            return _emit(payload, args.json, stdout, stderr=stderr, failed=payload.get("status") == "fail")

        if args.command == "source-validate":
            payload = validate_source_collection(args.collection)
            failed = payload.get("status") == "fail"
            return _emit(payload, args.json, stdout, stderr=stderr, failed=failed)

        if args.command == "source-to-evidence":
            payload = source_observations_to_evidence(args.collection, args.out)
            return _emit(payload, args.json, stdout)

        if args.command == "source-report":
            payload = write_source_collection_report(args.collection, args.out)
            return _emit(_source_report_summary(args.out, payload), args.json, stdout)

        if args.command == "source-status":
            payload = source_collection_status(args.collection)
            if args.json:
                return _emit(payload, True, stdout)
            print(render_source_collection_status(payload), end="", file=stdout)
            return 0
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        payload = {
            "status": "fail",
            "command": args.command,
            "error": str(exc),
            "artifact_verified_created": False,
            "truth_promotion_performed": False,
        }
        return _emit(payload, getattr(args, "json", False), stdout, stderr=stderr, failed=True)

    parser.error(f"unsupported command: {args.command}")
    return 2


def _emit(
    payload: Mapping[str, Any],
    as_json: bool,
    stdout: TextIO,
    *,
    stderr: TextIO = sys.stderr,
    failed: bool = False,
) -> int:
    target = stderr if failed and not as_json else stdout
    if as_json:
        print(json.dumps(dict(payload), indent=2, sort_keys=True, ensure_ascii=True), file=target)
    elif "error" in payload:
        print(f"status: {payload.get('status')}", file=target)
        print(f"error: {payload.get('error')}", file=target)
    else:
        for key, value in payload.items():
            if isinstance(value, (dict, list)):
                value = json.dumps(value, sort_keys=True, ensure_ascii=True)
            print(f"{key}: {value}", file=target)
    return 1 if failed else 0


def _seed_summary(out: str, report: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "status": report.get("status"),
        "gate_status": report.get("gate_status"),
        "out": out,
        "candidates": str(Path(out) / DEFAULT_CANDIDATES_FILE),
        "report": str(Path(out) / DEFAULT_GATE_REPORT_FILE),
        "candidate_count": report.get("candidate_count"),
        "evidence_packet_count": report.get("evidence_packet_count"),
        "reviewed_artifact_record_count": report.get("reviewed_artifact_record_count"),
        "reviewed_artifact_gate_count": report.get("reviewed_artifact_gate_count"),
        "artifact_verified_count": report.get("artifact_verified_count"),
        "next_recommended_task": report.get("next_recommended_task"),
    }


def _manual_report_summary(out: str, report: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "status": report.get("status"),
        "gate_status": report.get("gate_status"),
        "out": out,
        "batch_id": report.get("batch_id"),
        "candidate_count": report.get("candidate_count"),
        "evidence_packet_count": report.get("evidence_packet_count"),
        "valid_evidence_packet_count": report.get("valid_evidence_packet_count"),
        "invalid_evidence_packet_count": report.get("invalid_evidence_packet_count"),
        "reviewed_artifact_gate_count": report.get("reviewed_artifact_gate_count"),
        "artifact_verified_count": report.get("artifact_verified_count"),
        "next_recommended_task": report.get("next_recommended_task"),
    }


def _source_report_summary(out: str, report: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "status": report.get("status"),
        "collection_status": report.get("collection_status"),
        "out": out,
        "collection_id": report.get("collection_id"),
        "candidate_count": report.get("candidate_count"),
        "selected_candidate_count": report.get("selected_candidate_count"),
        "observation_count": report.get("observation_count"),
        "valid_observation_count": report.get("valid_observation_count"),
        "invalid_observation_count": report.get("invalid_observation_count"),
        "evidence_packet_count": report.get("evidence_packet_count"),
        "artifact_verified_packet_count": report.get("artifact_verified_packet_count"),
        "gate_eligible_packet_count": report.get("gate_eligible_packet_count"),
        "next_recommended_task": report.get("next_recommended_task"),
    }


def render_manual_batch_status(payload: Mapping[str, Any]) -> str:
    lines = [
        f"batch status: {payload.get('status')}",
        f"gate status: {payload.get('gate_status')}",
        f"report status: {payload.get('report_status')}",
        f"batch id: {payload.get('batch_id')}",
        f"candidate count: {payload.get('candidate_count')}",
        f"evidence packets: {payload.get('evidence_packet_count')}",
        f"valid packets: {payload.get('valid_evidence_packet_count')}",
        f"invalid packets: {payload.get('invalid_evidence_packet_count')}",
        f"reviewed artifact gate count: {payload.get('reviewed_artifact_gate_count')}/{payload.get('gate_target_reviewed_artifacts')}",
        f"artifact verified count: {payload.get('artifact_verified_count')}",
        f"next recommended task: {payload.get('next_recommended_task')}",
        "blockers:",
    ]
    blockers = [item for item in payload.get("blockers") or [] if isinstance(item, Mapping)]
    if blockers:
        for blocker in blockers:
            lines.append(f"- {blocker.get('id')}: {blocker.get('message')}")
    else:
        lines.append("- none")
    warnings = payload.get("warnings") or []
    if warnings:
        lines.append("warnings:")
        for warning in warnings:
            lines.append(f"- {warning}")
    return "\n".join(lines) + "\n"


def _load_evidence(path: str | Path) -> list[dict[str, Any]]:
    source = Path(path)
    text = source.read_text(encoding="utf-8").strip()
    if not text:
        return []
    if text.startswith("{"):
        try:
            value = json.loads(text)
        except json.JSONDecodeError:
            return read_jsonl(source)
        if not isinstance(value, Mapping):
            raise ValueError("evidence JSON must be an object")
        return [dict(value)]
    return read_jsonl(source)


if __name__ == "__main__":
    raise SystemExit(main())
