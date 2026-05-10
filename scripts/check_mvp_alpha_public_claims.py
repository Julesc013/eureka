#!/usr/bin/env python3
"""Check MVP alpha operator-review public claims."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.validate_mvp_alpha_operator_review import (
    FORBIDDEN_CLAIMS,
    detect_forbidden_operator_review_claims,
    validate_output_path,
    write_json_output,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", action="append", default=[])
    parser.add_argument("--output")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    inputs = args.input or ["examples/audits/mvp_alpha_operator"]
    report = check_public_claim_inputs(inputs)
    if args.output:
        write_json_output(validate_output_path(args.output), report)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    elif args.check:
        print(f"MVP alpha public claim check status: {report['status']}")
    else:
        print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "pass" else 1


def check_public_claim_inputs(inputs: list[str]) -> dict[str, Any]:
    errors: list[str] = []
    checked: list[str] = []
    for raw in inputs:
        path = Path(raw)
        if not path.is_absolute():
            path = REPO_ROOT / path
        files = sorted(path.rglob("*.json")) if path.is_dir() else [path]
        for file_path in files:
            checked.append(file_path.as_posix())
            try:
                payload = json.loads(file_path.read_text(encoding="utf-8"))
            except Exception as exc:
                errors.append(f"{file_path}: invalid JSON: {exc}")
                continue
            errors.extend(detect_forbidden_operator_review_claims(payload, file_path.as_posix()))
            if payload.get("schema_version") == "mvp_alpha_public_claim_review.v0":
                missing = sorted(FORBIDDEN_CLAIMS - set(payload.get("forbidden_claims", [])))
                if missing:
                    errors.append(f"{file_path}: missing forbidden claims {missing}")
                if payload.get("unsafe_claim_findings"):
                    errors.append(f"{file_path}: unsafe_claim_findings must be empty in current examples.")
    return {"schema_version": "mvp_alpha_public_claim_check.v0", "status": "fail" if errors else "pass", "checked": checked, "errors": errors}


if __name__ == "__main__":
    raise SystemExit(main())
