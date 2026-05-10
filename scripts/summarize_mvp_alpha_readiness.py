#!/usr/bin/env python3
"""Summarize MVP alpha readiness examples or audit outputs."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.validate_mvp_alpha_audit import detect_forbidden_mvp_claims, validate_output_path, write_json_output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", action="append")
    parser.add_argument("--output")
    parser.add_argument("--summary-output")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    payloads = load_inputs(args.input or ["examples/audits/mvp_alpha"])
    summary = summarize_payloads(payloads)
    if args.output:
        write_json_output(validate_output_path(args.output), summary)
    if args.summary_output:
        validate_output_path(args.summary_output).write_text(format_summary(summary) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    elif args.check:
        print(f"MVP alpha summary status: {summary['status']}")
    else:
        print(format_summary(summary))
    return 0 if summary["status"] == "pass" else 1


def load_inputs(values: list[str]) -> list[dict[str, Any]]:
    files: list[Path] = []
    for value in values:
        path = Path(value)
        if not path.is_absolute():
            path = REPO_ROOT / path
        if path.is_dir():
            files.extend(sorted(path.rglob("*.json")))
        elif path.is_file():
            files.append(path)
    payloads: list[dict[str, Any]] = []
    for path in files:
        payloads.append(json.loads(path.read_text(encoding="utf-8")))
    return payloads


def summarize_payloads(payloads: list[dict[str, Any]]) -> dict[str, Any]:
    errors: list[str] = []
    decisions: list[str] = []
    statuses: list[str] = []
    warnings: list[str] = []
    for index, payload in enumerate(payloads):
        errors.extend(f"payload[{index}]: {error}" for error in detect_forbidden_mvp_claims(payload, f"payload[{index}]"))
        if "decision" in payload:
            decisions.append(str(payload["decision"]))
        if "audit_status" in payload:
            statuses.append(str(payload["audit_status"]))
        warnings.extend(str(item) for item in payload.get("warnings", []) if isinstance(payload.get("warnings"), list))
    return {
        "schema_version": "mvp_alpha_readiness_summary.v0",
        "status": "fail" if errors else "pass",
        "payload_count": len(payloads),
        "audit_statuses": sorted(set(statuses)),
        "gate_decisions": sorted(set(decisions)),
        "warning_count": len(warnings),
        "warnings": sorted(set(warnings)),
        "errors": errors,
    }


def format_summary(summary: dict[str, Any]) -> str:
    lines = [
        "# MVP Alpha Readiness Summary",
        "",
        f"- status: {summary['status']}",
        f"- payload_count: {summary['payload_count']}",
        f"- audit_statuses: {', '.join(summary['audit_statuses']) or 'none'}",
        f"- gate_decisions: {', '.join(summary['gate_decisions']) or 'none'}",
        f"- warning_count: {summary['warning_count']}",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
