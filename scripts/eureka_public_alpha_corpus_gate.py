#!/usr/bin/env python3
"""Close out the public-alpha corpus gate from manual artifact evidence."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.local.corpus_gate_closeout import (
    closeout_corpus_gate,
    closeout_status,
    render_status_text,
    validate_closeout,
)


DEFAULT_OUT = ".eureka/corpus-gate/public-alpha/latest"


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout, stderr: TextIO = sys.stderr) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    closeout_parser = subparsers.add_parser("closeout", help="Write public-safe corpus gate closeout artifacts.")
    closeout_parser.add_argument("--artifact-gate-report", required=True)
    closeout_parser.add_argument("--manual-batch", required=True)
    closeout_parser.add_argument("--out", default=DEFAULT_OUT)
    closeout_parser.add_argument("--json", action="store_true")

    validate_parser = subparsers.add_parser("validate", help="Validate corpus gate closeout artifacts.")
    validate_parser.add_argument("--closeout", required=True)
    validate_parser.add_argument("--json", action="store_true")

    status_parser = subparsers.add_parser("status", help="Print corpus gate closeout status.")
    status_parser.add_argument("--closeout", required=True)
    status_parser.add_argument("--json", action="store_true")

    args = parser.parse_args(argv)
    if args.command == "closeout":
        try:
            report = closeout_corpus_gate(
                artifact_gate_report=args.artifact_gate_report,
                manual_batch=args.manual_batch,
                out_dir=args.out,
            )
            errors = validate_closeout(args.out)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            payload = {"status": "fail", "error": str(exc), "out": args.out}
            return _emit(payload, args.json, stdout, stderr=stderr, failed=True)
        payload = {
            "status": report.get("status"),
            "corpus_gate_status": report.get("corpus_gate_status"),
            "out": args.out,
            "reviewed_artifact_gate_count": report.get("reviewed_artifact_gate_count"),
            "artifact_verified_count": report.get("artifact_verified_count"),
            "public_artifact_identity_record_count": report.get("public_artifact_identity_record_count"),
            "public_artifact_evidence_summary_count": report.get("public_artifact_evidence_summary_count"),
            "validation_errors": errors,
        }
        return _emit(payload, args.json, stdout, stderr=stderr, failed=bool(errors) or report.get("status") == "FAIL")

    if args.command == "validate":
        errors = validate_closeout(args.closeout)
        payload = {
            "schema_version": "eureka.public_alpha_corpus_gate_validate.v0",
            "status": "pass" if not errors else "fail",
            "closeout": args.closeout,
            "errors": errors,
        }
        return _emit(payload, args.json, stdout, stderr=stderr, failed=bool(errors))

    if args.command == "status":
        payload = closeout_status(args.closeout)
        if args.json:
            return _emit(payload, True, stdout, stderr=stderr, failed=payload.get("status") != "pass")
        target = stdout if payload.get("status") == "pass" else stderr
        print(render_status_text(payload), end="", file=target)
        return 0 if payload.get("status") == "pass" else 1

    parser.error(f"unsupported command: {args.command}")
    return 2


def _emit(payload: dict[str, object], as_json: bool, stdout: TextIO, *, stderr: TextIO, failed: bool = False) -> int:
    target = stderr if failed and not as_json else stdout
    if as_json:
        print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True), file=target)
    else:
        for key, value in payload.items():
            if isinstance(value, (dict, list)):
                value = json.dumps(value, sort_keys=True, ensure_ascii=True)
            print(f"{key}: {value}", file=target)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
