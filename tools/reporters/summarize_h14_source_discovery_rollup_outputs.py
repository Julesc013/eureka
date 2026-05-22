#!/usr/bin/env python3
"""Summarize H14 Source OS rollup dry-run outputs offline."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence, TextIO

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.run_h14_source_discovery_rollup_dry_run import safe_output_path  # noqa: E402


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", action="append", default=[])
    parser.add_argument("--output")
    parser.add_argument("--summary-output")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        inputs = [Path(item) for item in args.input] or [Path("examples/connectors/h14_source_discovery/rollup_dry_run_results")]
        records = []
        for raw in inputs:
            path = raw if raw.is_absolute() else REPO_ROOT / raw
            if path.is_file() and path.suffix == ".json":
                records.append(_load_json(path))
            elif path.is_dir():
                for child in sorted(path.rglob("*.json")):
                    records.append(_load_json(child))
            else:
                raise ValueError(f"input path not found: {raw}")
        summary = build_summary(records)
        if not args.check:
            if args.output:
                out = safe_output_path(args.output)
                out.parent.mkdir(parents=True, exist_ok=True)
                out.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
                summary["wrote_files"] = True
            if args.summary_output:
                out = safe_output_path(args.summary_output)
                out.parent.mkdir(parents=True, exist_ok=True)
                out.write_text(render_markdown(summary), encoding="utf-8")
                summary["wrote_files"] = True
        if args.json:
            print(json.dumps(summary, indent=2, sort_keys=True), file=stdout)
        else:
            print("H14 Source OS rollup output summary", file=stdout)
            print(f"status: {summary['status']}", file=stdout)
            print(f"attempted_concepts: {', '.join(summary['attempted_concepts'])}", file=stdout)
            print(f"completed_concepts: {', '.join(summary['completed_concepts'])}", file=stdout)
            print(f"blocked_concepts: {', '.join(summary['blocked_concepts'])}", file=stdout)
            print(f"operation_count_total: {summary['operation_count_total']}", file=stdout)
            print(f"wrote_files: {str(summary['wrote_files']).lower()}", file=stdout)
        return 0
    except Exception as exc:  # noqa: BLE001
        if args.json:
            print(json.dumps({"status": "invalid", "error": str(exc)}, indent=2, sort_keys=True), file=stdout)
        else:
            print("H14 Source OS rollup output summary", file=stdout)
            print("status: invalid", file=stdout)
            print(f"ERROR: {exc}", file=stdout)
        return 1


def build_summary(records: list[Mapping[str, Any]]) -> dict[str, Any]:
    results = [item for item in records if isinstance(item, Mapping) and item.get("schema_version") == "h14_source_discovery_rollup_dry_run_result.v0"]
    attempted = sorted({str(item.get("source_id")) for item in results if item.get("source_id")})
    completed = sorted({str(item.get("source_id")) for item in results if item.get("result_status") == "rollup_dry_run_completed"})
    blocked = sorted({str(item.get("source_id")) for item in results if str(item.get("result_status", "")).startswith("blocked")})
    def count_key(key: str) -> int:
        return sum(len(item.get(key) or []) for item in results)
    return {
        "schema_version": "h14_source_discovery_rollup_output_summary.v0",
        "status": "pass",
        "attempted_concepts": attempted,
        "completed_concepts": completed,
        "blocked_concepts": blocked,
        "operation_count_total": sum(int(item.get("operation_count") or 0) for item in results),
        "source_need_candidate_count": count_key("source_need_candidates"),
        "source_candidate_candidate_count": count_key("source_candidate_candidates"),
        "source_discovery_candidate_count": count_key("source_discovery_candidates"),
        "source_pack_manifest_candidate_count": count_key("source_pack_manifest_candidates"),
        "connector_pack_manifest_candidate_count": count_key("connector_pack_manifest_candidates"),
        "coverage_manifest_candidate_count": count_key("coverage_manifest_candidates"),
        "connector_scorecard_candidate_count": count_key("connector_scorecard_candidates"),
        "reliability_freshness_candidate_count": count_key("source_reliability_freshness_candidates"),
        "dispute_revocation_candidate_count": count_key("source_dispute_revocation_candidates"),
        "lineage_provenance_candidate_count": count_key("source_lineage_provenance_candidates"),
        "pack_boundary_candidate_count": count_key("pack_import_export_boundary_candidates"),
        "network_used": any(bool(item.get("network_used")) for item in results),
        "model_provider_used": any(bool(item.get("model_provider_used")) for item in results),
        "registry_mutation_performed": any(bool(item.get("registry_mutation_performed")) for item in results),
        "pack_export_import_performed": any(bool(item.get("pack_export_import_performed")) for item in results),
        "blocked_reasons": sorted({reason for item in results for reason in (item.get("blocked_reasons") or [])}),
        "wrote_files": False,
    }


def render_markdown(summary: Mapping[str, Any]) -> str:
    return "\n".join([
        "# H14 Source OS Rollup Output Summary",
        "",
        f"- status: `{summary['status']}`",
        f"- attempted_concepts: `{len(summary['attempted_concepts'])}`",
        f"- completed_concepts: `{len(summary['completed_concepts'])}`",
        f"- blocked_concepts: `{len(summary['blocked_concepts'])}`",
        f"- operation_count_total: `{summary['operation_count_total']}`",
        "",
        "No source discovery runtime, network/model call, pack import/export, registry mutation, source-cache write, evidence write, public-index write, master-index write, or truth acceptance occurred.",
        "",
    ])


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    raise SystemExit(main())
