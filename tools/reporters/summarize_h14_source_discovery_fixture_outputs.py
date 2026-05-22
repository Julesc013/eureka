#!/usr/bin/env python3
"""Summarize H14 Source OS rollup fixture outputs offline."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence, TextIO

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.normalize_h14_source_discovery_fixture import safe_output_path  # noqa: E402


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", action="append", default=[])
    parser.add_argument("--output")
    parser.add_argument("--summary-output")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        inputs = [Path(item) for item in args.input] or [Path("examples/connectors/h14_source_discovery")]
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
                out = safe_output_path(args.output, ("control/audits/h14-bundle-02-source-discovery-fixture-runtime-v0/generated",))
                out.parent.mkdir(parents=True, exist_ok=True)
                out.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
                summary["wrote_files"] = True
            if args.summary_output:
                out = safe_output_path(args.summary_output, ("control/audits/h14-bundle-02-source-discovery-fixture-runtime-v0/generated",))
                out.parent.mkdir(parents=True, exist_ok=True)
                out.write_text(render_markdown(summary), encoding="utf-8")
                summary["wrote_files"] = True
        if args.json:
            print(json.dumps(summary, indent=2, sort_keys=True), file=stdout)
        else:
            print("H14 source discovery fixture output summary", file=stdout)
            print(f"status: {summary['status']}", file=stdout)
            print(f"source_count: {summary['source_count']}", file=stdout)
            print(f"normalized_record_count: {summary['normalized_record_count']}", file=stdout)
            print(f"fixture_replay_result_count: {summary['fixture_replay_result_count']}", file=stdout)
            print(f"source_need_candidate_count: {summary['source_need_candidate_count']}", file=stdout)
            print(f"wrote_files: {str(summary['wrote_files']).lower()}", file=stdout)
        return 0
    except Exception as exc:  # noqa: BLE001
        if args.json:
            print(json.dumps({"status": "invalid", "error": str(exc)}, indent=2, sort_keys=True), file=stdout)
        else:
            print("H14 source discovery fixture output summary", file=stdout)
            print("status: invalid", file=stdout)
            print(f"ERROR: {exc}", file=stdout)
        return 1


def build_summary(records: list[Mapping[str, Any]]) -> dict[str, Any]:
    source_ids = sorted({str(item.get("source_id")) for item in records if isinstance(item, Mapping) and item.get("source_id")})
    def count_schema(schema: str) -> int:
        return sum(1 for item in records if isinstance(item, Mapping) and item.get("schema_version") == schema)
    return {
        "schema_version": "h14_source_discovery_fixture_output_summary.v0",
        "status": "pass",
        "source_count": len(source_ids),
        "source_ids": source_ids,
        "fixture_count": count_schema("h14_source_discovery_fixture.v0"),
        "normalized_record_count": count_schema("h14_source_discovery_normalized_record.v0"),
        "fixture_replay_result_count": count_schema("h14_source_discovery_fixture_replay_result.v0"),
        "source_need_candidate_count": count_schema("h14_source_need_candidate.v0"),
        "source_candidate_candidate_count": count_schema("h14_source_candidate_candidate.v0"),
        "source_discovery_candidate_count": count_schema("h14_source_discovery_candidate.v0"),
        "source_pack_manifest_candidate_count": count_schema("h14_source_pack_manifest_candidate.v0"),
        "connector_pack_manifest_candidate_count": count_schema("h14_connector_pack_manifest_candidate.v0"),
        "coverage_manifest_candidate_count": count_schema("h14_coverage_manifest_candidate.v0"),
        "connector_scorecard_candidate_count": count_schema("h14_connector_scorecard_candidate.v0"),
        "reliability_freshness_candidate_count": count_schema("h14_source_reliability_freshness_candidate.v0"),
        "dispute_revocation_candidate_count": count_schema("h14_source_dispute_revocation_candidate.v0"),
        "lineage_provenance_candidate_count": count_schema("h14_source_lineage_provenance_candidate.v0"),
        "pack_boundary_candidate_count": count_schema("h14_pack_import_export_boundary_candidate.v0"),
        "blockers": ["source discovery runtime remains forbidden", "pack import/export remains forbidden", "registry mutation remains forbidden"],
        "warnings": [],
        "wrote_files": False,
    }


def render_markdown(summary: Mapping[str, Any]) -> str:
    return "\n".join([
        "# H14 Source Discovery Fixture Output Summary",
        "",
        f"- status: `{summary['status']}`",
        f"- source_count: `{summary['source_count']}`",
        f"- normalized_record_count: `{summary['normalized_record_count']}`",
        f"- fixture_replay_result_count: `{summary['fixture_replay_result_count']}`",
        "",
        "No source discovery runtime, pack import/export, registry mutation, source-cache write, evidence write, public-index write, master-index write, or truth acceptance is enabled.",
        "",
    ])


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    raise SystemExit(main())
