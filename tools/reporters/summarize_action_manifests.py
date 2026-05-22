#!/usr/bin/env python3
"""Summarize action manifests and related J0 outputs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.actions import action_policy  # noqa: E402
from runtime.actions.summaries import format_action_summary, summarize_action_records  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", action="append", required=True, help="Input JSON file or directory.")
    parser.add_argument("--output", help="Optional JSON summary output.")
    parser.add_argument("--summary-output", help="Optional markdown summary output.")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        policy = action_policy.load_action_policy(REPO_ROOT)
        records = []
        for item in args.input:
            records.extend(_load_records(item))
        errors: list[str] = []
        for record in records:
            errors.extend(action_policy.detect_action_boundary_violations(record))
        if errors:
            for error in sorted(dict.fromkeys(errors)):
                print(f"ERROR: {error}", file=sys.stderr)
            return 1
        summary = summarize_action_records(records)
        wrote_files = False
        if not args.check:
            if args.output:
                _write_json(action_policy.ensure_allowed_output_path(args.output, policy, REPO_ROOT), summary)
                wrote_files = True
            if args.summary_output:
                _write_text(action_policy.ensure_allowed_output_path(args.summary_output, policy, REPO_ROOT), format_action_summary(summary))
                wrote_files = True
        response = {"schema_version": "action_summary_cli_result.v0", "status": "pass", "wrote_files": wrote_files, "summary": summary}
        if args.json:
            print(json.dumps(response, indent=2, sort_keys=True))
        else:
            print(format_action_summary(summary), end="")
            print("status: pass")
        return 0
    except Exception as exc:  # pragma: no cover
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


def _load_records(path_text: str) -> list[dict[str, Any]]:
    path = Path(path_text)
    resolved = (REPO_ROOT / path).resolve() if not path.is_absolute() else path.resolve()
    rel = resolved.relative_to(REPO_ROOT.resolve()).as_posix()
    if not (rel == "examples/actions" or rel.startswith("examples/actions/") or rel.startswith("control/audits/")):
        raise ValueError(f"refusing input outside approved action roots: {rel}")
    paths = sorted(resolved.rglob("*.json")) if resolved.is_dir() else [resolved]
    records = []
    for candidate in paths:
        payload = json.loads(candidate.read_text(encoding="utf-8"))
        if isinstance(payload, dict):
            records.append(payload)
    return records


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
