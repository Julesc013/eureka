#!/usr/bin/env python3
"""Check that an MVP alpha signoff packet does not infer approval."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.validate_mvp_alpha_operator_review import detect_forbidden_operator_review_claims


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default="examples/audits/mvp_alpha_operator/operator_signoff_packet_unsigned_v0.json")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    payload = _load(args.input)
    errors = validate_signoff(payload)
    result = {"schema_version": "mvp_alpha_operator_signoff_check.v0", "status": "fail" if errors else "pass", "errors": errors, "signoff_status": payload.get("signoff_status")}
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    elif args.check:
        print(f"MVP alpha operator signoff status: {result['status']}")
    else:
        print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "pass" else 1


def validate_signoff(payload: dict) -> list[str]:
    errors = detect_forbidden_operator_review_claims(payload, "signoff")
    if payload.get("signoff_status") in {"signed_future"}:
        errors.append("signed_future is not accepted for current operator-review examples.")
    if payload.get("signed_at_future") is not None:
        errors.append("signed_at_future must be null until explicit future approval.")
    if payload.get("signature_or_confirmation_future") is not None:
        errors.append("signature_or_confirmation_future must be null until explicit future approval.")
    if payload.get("truth_boundary", {}).get("operator_signoff_inferred") is not False:
        errors.append("operator signoff must not be inferred.")
    return errors


def _load(value: str) -> dict:
    path = Path(value)
    if not path.is_absolute():
        path = REPO_ROOT / path
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    raise SystemExit(main())
