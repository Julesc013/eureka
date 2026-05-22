#!/usr/bin/env python3
"""Compute local SHA-256 fixity for an explicit pack export."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.extraction.guards import ensure_allowed_input_path, ensure_allowed_output_path  # noqa: E402
from runtime.local_foundry import pack_fixity, pack_quarantine  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True)
    parser.add_argument("--output")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        policy = pack_quarantine.load_quarantine_policy(REPO_ROOT)
        input_path = ensure_allowed_input_path(args.input, policy, REPO_ROOT)
        pack = pack_quarantine.load_pack_for_quarantine(input_path)
        report = pack_fixity.build_pack_fixity_report(pack, policy)
        errors = pack_fixity.validate_pack_fixity_report(report, policy)
        if errors:
            for error in errors:
                print(f"ERROR: {error}", file=sys.stderr)
            return 1
        if args.output and not args.check:
            output = ensure_allowed_output_path(args.output, policy, REPO_ROOT)
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        response = {"schema_version": "pack_fixity_cli_result.v0", "status": "pass", "wrote_files": bool(args.output and not args.check), "fixity_report": report}
        if args.json:
            print(json.dumps(response, indent=2, sort_keys=True))
        else:
            print(f"status: pass\nsha256: {report['hash_value']}\nfixity_does_not_mean_authenticity: true")
        return 0
    except Exception as exc:  # pragma: no cover
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
