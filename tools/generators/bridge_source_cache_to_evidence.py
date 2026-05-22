#!/usr/bin/env python3
"""Bridge an explicit source cache record into evidence candidates."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import tempfile
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.local_foundry import source_cache_to_evidence as bridge  # noqa: E402


FORBIDDEN_OUTPUT_ROOTS = (
    "site/dist/",
    "runtime/",
    "contracts/",
    "control/inventory/publication/",
    "control/inventory/sources/",
    "control/inventory/master_index/",
    "control/master_index/",
    "master_index/",
    "evals/search_usefulness/external_baselines/",
    ".aide.local/",
    ".local/eureka/",
    ".cache/eureka/",
)


def build_report(input_path: Path, *, repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    source_record = bridge.load_source_cache_record(input_path)
    source_errors = bridge.detect_forbidden_source_cache_conversion(source_record)
    evidence_candidates = bridge.map_source_cache_record_to_evidence_candidates(source_record)
    bridge_result = bridge.build_bridge_result(source_record, evidence_candidates)
    bridge_errors = bridge.validate_bridge_result(bridge_result)
    summary = bridge.summarize_bridge_result(bridge_result)
    errors = sorted(dict.fromkeys(source_errors + bridge_errors))
    return {
        "schema_version": bridge.REPORT_SCHEMA_VERSION,
        "status": "pass" if not errors else "fail",
        "input_ref": _display_path(input_path, repo_root),
        "bridge_result": bridge_result,
        "generated_evidence_candidates": evidence_candidates,
        "summary": summary,
        "validation_errors": errors,
        "warnings": bridge_result.get("warnings", []),
        "runtime_scope": {
            "explicit_input_only": True,
            "local_only": True,
            "fixture_only": True,
            "writes_no_files_by_default": True,
            "source_cache_bridge_enabled": True,
            "evidence_acceptance_enabled": False,
            "live_source_access_enabled": False,
        },
        "truth_boundary": {
            "source_cache_record_is_public_truth": False,
            "bridge_output_is_accepted_evidence": False,
            "bridge_output_can_mutate_master_index": False,
            "human_review_required_for_downstream_use": True,
        },
        "product_boundary": bridge_result["product_boundary"],
    }


def output_path_allowed(path: Path, *, repo_root: Path = REPO_ROOT) -> bool:
    resolved = path.resolve()
    try:
        relative = resolved.relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        temp_root = Path(tempfile.gettempdir()).resolve()
        try:
            resolved.relative_to(temp_root)
            return True
        except ValueError:
            return False

    normalized = relative.rstrip("/") + "/"
    if any(normalized.startswith(root) or relative == root.rstrip("/") for root in FORBIDDEN_OUTPUT_ROOTS):
        return False
    return relative.startswith("control/audits/") and "/generated/" in f"/{relative}"


def write_bridge_result(report: Mapping[str, Any], output_path: Path) -> None:
    if not output_path_allowed(output_path):
        raise ValueError(f"refusing forbidden output path: {output_path}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report["bridge_result"], indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_evidence_candidate(report: Mapping[str, Any], output_path: Path) -> None:
    if not output_path_allowed(output_path):
        raise ValueError(f"refusing forbidden output path: {output_path}")
    candidates = report.get("generated_evidence_candidates", [])
    if not isinstance(candidates, list) or not candidates:
        raise ValueError("no generated evidence candidate to write")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(candidates[0], indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_summary(report: Mapping[str, Any], output_path: Path) -> None:
    if not output_path_allowed(output_path):
        raise ValueError(f"refusing forbidden output path: {output_path}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(bridge.format_bridge_summary_markdown(report["summary"]), encoding="utf-8")


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None, stderr: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="Explicit source cache record JSON input.")
    parser.add_argument("--output", type=Path, help="Optional explicit bridge result JSON output path.")
    parser.add_argument("--evidence-output", type=Path, help="Optional explicit evidence candidate JSON output path.")
    parser.add_argument("--summary-output", type=Path, help="Optional explicit Markdown summary output path.")
    parser.add_argument("--check", action="store_true", help="Validate and report status without requiring output.")
    parser.add_argument("--json", action="store_true", help="Print JSON report to stdout.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    out = stdout or sys.stdout
    err = stderr or sys.stderr
    try:
        report = build_report(args.input)
        if args.output:
            write_bridge_result(report, args.output)
        if args.evidence_output:
            write_evidence_candidate(report, args.evidence_output)
        if args.summary_output:
            write_summary(report, args.summary_output)
    except Exception as exc:
        err.write(f"bridge_source_cache_to_evidence: ERROR: {exc}\n")
        return 2

    if args.json:
        out.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        summary = report["summary"]
        out.write("Source cache to evidence bridge\n")
        out.write(f"status: {report['status']}\n")
        out.write(f"bridge_result_id: {summary.get('bridge_result_id')}\n")
        out.write(f"bridge_status: {summary.get('bridge_status')}\n")
        out.write(f"source_cache_record_type: {summary.get('source_cache_record_type')}\n")
        out.write(f"generated_evidence_candidate_count: {summary.get('generated_evidence_candidate_count')}\n")
        out.write(f"review_required: {str(summary.get('review_required')).lower()}\n")
        if report["validation_errors"]:
            out.write("errors:\n")
            for error in report["validation_errors"]:
                out.write(f"- {error}\n")

    return 0 if report["status"] == "pass" else 1


def _display_path(path: Path, repo_root: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return str(path)


if __name__ == "__main__":
    raise SystemExit(main())
