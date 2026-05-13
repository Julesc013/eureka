#!/usr/bin/env python3
"""Summarize H7 library/cultural/research fixture outputs offline."""

from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence, TextIO

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from control.prototypes.legacy_runtime.connectors.h7_library_research.normalizer_common import H7_SOURCE_IDS  # noqa: E402
from scripts.normalize_h7_library_research_fixture import safe_output_path  # noqa: E402

ALLOWED_PREFIXES = ("control/audits/h7-bundle-02-library-research-fixture-runtime-v0/generated",)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", action="append", default=[])
    parser.add_argument("--output")
    parser.add_argument("--summary-output")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        roots = args.input or ["examples/connectors/h7_library_research"]
        summary = build_summary([Path(item) for item in roots])
        if not args.check:
            if args.output:
                path = safe_output_path(args.output, ALLOWED_PREFIXES)
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            if args.summary_output:
                path = safe_output_path(args.summary_output, ALLOWED_PREFIXES)
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(render_markdown(summary), encoding="utf-8")
        if args.json:
            print(json.dumps(summary, indent=2, sort_keys=True), file=stdout)
        else:
            print("H7 library/cultural/research fixture output summary", file=stdout)
            print(f"status: {summary['status']}", file=stdout)
            print(f"source_count: {summary['source_count']}", file=stdout)
            print(f"normalized_records: {summary['normalized_record_count']}", file=stdout)
            print(f"citation_candidates: {summary['citation_candidate_count']}", file=stdout)
        return 0
    except Exception as exc:  # noqa: BLE001
        if args.json:
            print(json.dumps({"status": "invalid", "error": str(exc)}, indent=2, sort_keys=True), file=stdout)
        else:
            print("H7 library/cultural/research fixture output summary", file=stdout)
            print("status: invalid", file=stdout)
            print(f"ERROR: {exc}", file=stdout)
        return 1


def build_summary(inputs: Sequence[Path]) -> dict[str, Any]:
    files: list[Path] = []
    for item in inputs:
        path = item if item.is_absolute() else REPO_ROOT / item
        if path.is_dir():
            files.extend(sorted(path.rglob("*.json")))
        elif path.is_file():
            files.append(path)
    counts: Counter[str] = Counter()
    sources: set[str] = set()
    blockers: list[str] = []
    warnings: list[str] = []
    for path in files:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, Mapping):
            continue
        schema = str(payload.get("schema_version", "unknown"))
        source_id = payload.get("source_id")
        if isinstance(source_id, str) and source_id in H7_SOURCE_IDS:
            sources.add(source_id)
        if schema == "h7_library_research_normalized_record.v0":
            counts["normalized_record"] += 1
            counts["bibliographic"] += 1 if payload.get("bibliographic_identity_candidate") else 0
            counts["research_work"] += 1 if payload.get("research_work_identity_candidate") else 0
            counts["dataset"] += 1 if payload.get("dataset_identity_candidate") else 0
            counts["cultural_object"] += 1 if payload.get("cultural_object_identity_candidate") else 0
            counts["patent"] += 1 if payload.get("patent_identity_candidate") else 0
            counts["citation"] += len(payload.get("citation_relation_candidate", []) or [])
            counts["access_rights"] += 1 if payload.get("access_rights_availability_candidate") else 0
        elif schema == "h7_library_research_fixture_replay_result.v0":
            counts["replay_result"] += 1
            if payload.get("replay_status") == "blocked_by_policy_fixture":
                blockers.append(str(payload.get("fixture_ref")))
        elif schema == "h7_library_research_fixture.v0":
            counts["fixture"] += 1
        elif schema.endswith("_candidate.v0"):
            counts["candidate_examples"] += 1
        if payload.get("warnings"):
            warnings.extend(str(item) for item in payload.get("warnings", []))
    return {
        "schema_version": "h7_library_research_fixture_output_summary.v0",
        "status": "pass",
        "source_count": len(sources),
        "source_ids": sorted(sources),
        "fixture_count": counts["fixture"],
        "normalized_record_count": counts["normalized_record"],
        "fixture_replay_result_count": counts["replay_result"],
        "bibliographic_candidate_count": counts["bibliographic"],
        "research_work_candidate_count": counts["research_work"],
        "dataset_candidate_count": counts["dataset"],
        "cultural_object_candidate_count": counts["cultural_object"],
        "patent_candidate_count": counts["patent"],
        "citation_candidate_count": counts["citation"],
        "access_rights_candidate_count": counts["access_rights"],
        "candidate_example_count": counts["candidate_examples"],
        "blockers": blockers,
        "warnings": warnings,
        "network_calls_made": False,
        "harvest_query_fetch_download_used": False,
        "restricted_source_access_used": False,
    }


def render_markdown(summary: Mapping[str, Any]) -> str:
    lines = ["# H7 Library Research Fixture Output Summary", "", f"- status: `{summary.get('status')}`", f"- source_count: `{summary.get('source_count')}`", f"- normalized_record_count: `{summary.get('normalized_record_count')}`", f"- citation_candidate_count: `{summary.get('citation_candidate_count')}`", "", "## Sources"]
    lines.extend(f"- {item}" for item in summary.get("source_ids", []))
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
