"""Summarize fixture-only snapshot artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Mapping

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.snapshots.manifest import ensure_allowed_input_path, ensure_allowed_output_path, load_json, load_snapshot_policy
from runtime.snapshots.summaries import format_snapshot_summary, summarize_snapshot_bundle


def _collect_inputs(paths: list[str]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for raw_path in paths:
        path = ensure_allowed_input_path(raw_path)
        if path.is_dir():
            for child in sorted(path.rglob("*.json")):
                records.append(load_json(child))
        else:
            records.append(load_json(path))
    return records


def _summarize(records: list[Mapping[str, Any]]) -> dict[str, Any]:
    manifests = [record for record in records if record.get("schema_version") == "snapshot_manifest.v0"]
    verifications = [record for record in records if record.get("schema_version") == "snapshot_verification_report.v0"]
    render_results = [
        record
        for record in records
        if record.get("schema_version") in {"snapshot_render_result.v0", "snapshot_file_tree_index.v0"}
    ]
    base = summarize_snapshot_bundle(manifests[0] if manifests else {"records": []})
    base.update(
        {
            "manifest_count": len(manifests),
            "verification_report_count": len(verifications),
            "render_result_count": len(render_results),
            "blocked_report_count": sum(1 for record in records if "policy_blocked" in json.dumps(record)),
        }
    )
    return base


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Summarize snapshot fixture artifacts.")
    parser.add_argument("--input", action="append", required=True)
    parser.add_argument("--output")
    parser.add_argument("--summary-output")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args(argv)

    policy = load_snapshot_policy()
    summary = _summarize(_collect_inputs(args.input))
    summary_text = format_snapshot_summary(summary)
    if not args.check:
        if args.output:
            output = ensure_allowed_output_path(args.output, policy)
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        if args.summary_output:
            output = ensure_allowed_output_path(args.summary_output, policy)
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(summary_text, encoding="utf-8")
    if args.as_json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print(summary_text, end="")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # pragma: no cover - script boundary
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
