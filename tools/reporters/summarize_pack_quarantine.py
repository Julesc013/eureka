#!/usr/bin/env python3
"""Summarize local pack quarantine outputs without mutating pack state."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.extraction.guards import ensure_allowed_output_path  # noqa: E402
from runtime.local_foundry import pack_quarantine  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", action="append", required=True)
    parser.add_argument("--output")
    parser.add_argument("--summary-output")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        policy = pack_quarantine.load_quarantine_policy(REPO_ROOT)
        records = _load_inputs(args.input)
        quarantine_results = [record for record in records if record.get("schema_version") == pack_quarantine.RESULT_SCHEMA_VERSION]
        summary = _build_summary(quarantine_results)
        if not args.check:
            if args.output:
                _write_json(ensure_allowed_output_path(args.output, policy, REPO_ROOT), summary)
            if args.summary_output:
                _write_text(ensure_allowed_output_path(args.summary_output, policy, REPO_ROOT), _summary_markdown(summary))
        response = {"schema_version": "pack_quarantine_summary_cli_result.v0", "status": "pass", "wrote_files": bool(not args.check and (args.output or args.summary_output)), "summary": summary}
        if args.json:
            print(json.dumps(response, indent=2, sort_keys=True))
        else:
            print("status: pass")
            print(f"quarantine_results: {summary['quarantine_result_count']}")
            print(f"blocked_results: {summary['blocked_result_count']}")
            print("pack_imported: false")
        return 0
    except Exception as exc:  # pragma: no cover
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


def _load_inputs(inputs: list[str]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for item in inputs:
        path = (REPO_ROOT / item).resolve() if not Path(item).is_absolute() else Path(item).resolve()
        if path.is_dir():
            for child in sorted(path.rglob("*.json")):
                records.append(pack_quarantine.load_json(child))
        else:
            records.append(pack_quarantine.load_json(path))
    return records


def _build_summary(results: list[dict[str, Any]]) -> dict[str, Any]:
    blocked = [result for result in results if str(result.get("quarantine_status", "")).startswith("blocked")]
    return {
        "schema_version": "pack_quarantine_summary.v0",
        "quarantine_result_count": len(results),
        "blocked_result_count": len(blocked),
        "quarantined_local_count": sum(1 for result in results if result.get("quarantine_status") == "quarantined_local"),
        "needs_review_count": sum(1 for result in results if result.get("quarantine_status") == "needs_review"),
        "pack_imported": False,
        "pack_submitted": False,
        "pack_accepted": False,
        "real_signing": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
    }


def _summary_markdown(summary: dict[str, Any]) -> str:
    return (
        "# Pack Quarantine Output Summary\n\n"
        f"- Quarantine results: {summary['quarantine_result_count']}\n"
        f"- Blocked results: {summary['blocked_result_count']}\n"
        "- Pack imported: false\n"
        "- Pack submitted: false\n"
        "- Pack accepted: false\n"
        "- Real signing: false\n"
    )


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_text(path: Path, payload: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(payload, encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
