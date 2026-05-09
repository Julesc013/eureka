#!/usr/bin/env python3
"""Build fixture-only search explanations from explicit local inputs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import tempfile
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.extraction.guards import load_json, path_under, resolve_path  # noqa: E402
from runtime.search_quality.explanation import load_search_quality_policy  # noqa: E402
from runtime.search_quality.explanation_summary import (  # noqa: E402
    build_explanation_output_bundle,
    summarize_explanation_output_bundle,
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", help="Explanation input bundle JSON.")
    parser.add_argument("--candidate", help="Candidate record JSON.")
    parser.add_argument("--evidence", help="Evidence record JSON.")
    parser.add_argument("--source-cache", help="Source cache record JSON.")
    parser.add_argument("--extraction-gap", help="Extraction search gap JSON.")
    parser.add_argument("--output", help="Optional first explanation JSON output.")
    parser.add_argument("--bundle-output", help="Optional output bundle JSON output.")
    parser.add_argument("--summary-output", help="Optional markdown summary output.")
    parser.add_argument("--check", action="store_true", help="Validate only and write no files.")
    parser.add_argument("--json", action="store_true", help="Emit JSON summary.")
    args = parser.parse_args(argv)
    try:
        policy = load_search_quality_policy()
        input_bundle = load_input_bundle(args, policy)
        output_bundle = build_explanation_output_bundle(input_bundle, policy)
        summary = summarize_explanation_output_bundle(output_bundle, policy)
        wrote = False
        if not args.check:
            if args.output:
                write_json(args.output, first_or_empty(output_bundle.get("result_explanations", [])), policy)
                wrote = True
            if args.bundle_output:
                write_json(args.bundle_output, output_bundle, policy)
                wrote = True
            if args.summary_output:
                write_text(args.summary_output, render_markdown(summary), policy)
                wrote = True
        summary["wrote_files"] = wrote
        if args.json:
            print(json.dumps(summary, indent=2, sort_keys=True), file=stdout)
        else:
            print("Search explanation fixture", file=stdout)
            print(f"status: {summary['output_status']}", file=stdout)
            print(f"result_explanation_count: {summary['result_explanation_count']}", file=stdout)
            print(f"near_miss_count: {summary['near_miss_count']}", file=stdout)
            print(f"known_absence_count: {summary['known_absence_count']}", file=stdout)
            print(f"search_gap_explanation_count: {summary['search_gap_explanation_count']}", file=stdout)
            print(f"wrote_files: {str(wrote).lower()}", file=stdout)
        return 0
    except Exception as exc:  # noqa: BLE001
        if args.json:
            print(json.dumps({"status": "invalid", "error": str(exc)}, indent=2, sort_keys=True), file=stdout)
        else:
            print("Search explanation fixture", file=stdout)
            print("status: invalid", file=stdout)
            print(f"ERROR: {exc}", file=stdout)
        return 1


def load_input_bundle(args: argparse.Namespace, policy: Mapping[str, Any]) -> dict[str, Any]:
    if args.input:
        return load_json(ensure_allowed_input_path(args.input, policy))
    records: list[Mapping[str, Any]] = []
    for attr in ("candidate", "evidence", "source_cache", "extraction_gap"):
        value = getattr(args, attr)
        if value:
            records.append(load_json(ensure_allowed_input_path(value, policy)))
    if not records:
        raise ValueError("provide --input or at least one explicit fixture record")
    bundle: dict[str, Any] = {
        "schema_version": "explanation_input_bundle.v0",
        "input_bundle_id": "explanation.input.explicit_cli.v0",
        "bundle_status": "local_dry_run",
        "query_observation_refs": [],
        "search_miss_refs": [],
        "search_need_refs": ["search_need.software_version.vintage_app.v0"],
        "candidate_refs": [],
        "source_cache_refs": [],
        "evidence_refs": [],
        "review_refs": [],
        "extraction_result_refs": [],
        "extraction_search_gap_refs": [],
        "local_fixture_result_refs": [],
        "candidate_records": [],
        "source_cache_records": [],
        "evidence_records": [],
        "extraction_search_gaps": [],
        "near_miss_inputs": [],
        "sources_checked": ["local_fixture_index"],
        "sources_not_checked": ["live_web", "external_sources"],
        "truth_boundary": {"explanation_accepts_result_as_truth": False},
        "product_boundary": {"changed_public_search_behavior": False},
        "limitations": ["Explicit CLI fixture inputs only."],
    }
    for record in records:
        schema = record.get("schema_version")
        if schema == "candidate_record.v0":
            bundle["candidate_records"].append(record)
            bundle["candidate_refs"].append(record.get("candidate_id"))
        elif schema == "local_evidence_ledger_record.v0":
            bundle["evidence_records"].append(record)
            bundle["evidence_refs"].append(record.get("evidence_record_id"))
        elif schema == "extraction_search_gap.v0":
            bundle["extraction_search_gaps"].append(record)
            bundle["extraction_search_gap_refs"].append(record.get("search_gap_id"))
        else:
            bundle["source_cache_records"].append(record)
            bundle["source_cache_refs"].append(record.get("source_cache_record_id") or record.get("source_cache_id"))
    return bundle


def ensure_allowed_input_path(path_text: str, policy: Mapping[str, Any]) -> Path:
    path = resolve_path(path_text, REPO_ROOT)
    if not path.exists():
        raise ValueError(f"input path does not exist: {path}")
    if path_under(path, Path(tempfile.gettempdir())):
        return path
    for root_text in policy.get("allowed_input_roots", []):
        if "temp" in str(root_text).casefold():
            continue
        if path_under(path, resolve_path(str(root_text), REPO_ROOT)):
            return path
    raise ValueError(f"refusing input outside allowed search-quality roots: {path}")


def ensure_allowed_output_path(path_text: str, policy: Mapping[str, Any]) -> Path:
    path = resolve_path(path_text, REPO_ROOT)
    if path_under(path, Path(tempfile.gettempdir())):
        return path
    try:
        rel = path.relative_to(REPO_ROOT.resolve()).as_posix().casefold().rstrip("/")
    except ValueError as exc:
        raise ValueError(f"refusing output outside repository approved roots or temp directory: {path}") from exc
    for root_text in policy.get("forbidden_output_roots", []):
        root = str(root_text).casefold().rstrip("/")
        if rel == root or rel.startswith(root + "/"):
            raise ValueError(f"refusing forbidden output root: {root_text}")
    for root_text in policy.get("allowed_output_roots", []):
        root = str(root_text).casefold().rstrip("/")
        if root.endswith("/**/generated"):
            prefix = root[: -len("/**/generated")]
            if rel.startswith(prefix + "/") and "/generated/" in rel:
                return path
            continue
        if "temp" in root:
            continue
        if rel == root or rel.startswith(root + "/"):
            return path
    raise ValueError(f"refusing output outside approved search-quality roots: {rel}")


def write_json(path_text: str, payload: Mapping[str, Any], policy: Mapping[str, Any]) -> None:
    path = ensure_allowed_output_path(path_text, policy)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_text(path_text: str, text: str, policy: Mapping[str, Any]) -> None:
    path = ensure_allowed_output_path(path_text, policy)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def first_or_empty(values: Any) -> Mapping[str, Any]:
    return values[0] if isinstance(values, list) and values else {"schema_version": "empty_explanation.v0"}


def render_markdown(summary: Mapping[str, Any]) -> str:
    return "\n".join(
        [
            "# Search Explanation Summary",
            "",
            f"- output_status: `{summary.get('output_status')}`",
            f"- result_explanation_count: `{summary.get('result_explanation_count', 0)}`",
            f"- near_miss_count: `{summary.get('near_miss_count', 0)}`",
            f"- known_absence_count: `{summary.get('known_absence_count', 0)}`",
            f"- search_gap_explanation_count: `{summary.get('search_gap_explanation_count', 0)}`",
            "- public_search_mutated: `false`",
            "- ranking_mutated: `false`",
            "- public_index_mutated: `false`",
            "- master_index_mutated: `false`",
            "",
        ]
    )


if __name__ == "__main__":
    raise SystemExit(main())
