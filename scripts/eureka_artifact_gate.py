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
    evidence_templates_from_candidates,
    export_launch_report,
    gate_status,
    list_artifact_gate_candidates,
    read_jsonl,
    render_status,
    seed_artifact_gate,
    validate_evidence_packet,
    validate_gate,
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
