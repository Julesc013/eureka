#!/usr/bin/env python3
"""Record a fixture-only source cache report from explicit local JSON input."""

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

from runtime.local_foundry import source_cache  # noqa: E402


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
    payload = source_cache.load_json(input_path)
    record = source_cache.build_source_cache_record(payload)
    errors = source_cache.validate_source_cache_record(record)
    summary = source_cache.summarize_source_cache_record(record)
    return {
        "schema_version": source_cache.REPORT_SCHEMA_VERSION,
        "status": "pass" if not errors else "fail",
        "input_ref": _display_path(input_path, repo_root),
        "record": record,
        "summary": summary,
        "validation_errors": errors,
        "warnings": [],
        "runtime_scope": {
            "explicit_input_only": True,
            "local_only": True,
            "fixture_only": True,
            "writes_no_files_by_default": True,
            "source_access_enabled": False,
            "source_sync_enabled": False,
            "live_probe_enabled": False,
        },
        "truth_boundary": {
            "source_cache_record_is_public_truth": False,
            "source_cache_record_is_accepted_evidence": False,
            "source_cache_record_can_mutate_master_index": False,
            "human_review_required_for_downstream_use": True,
        },
        "product_boundary": record["product_boundary"],
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


def write_report(report: Mapping[str, Any], output_path: Path) -> None:
    if not output_path_allowed(output_path):
        raise ValueError(f"refusing forbidden output path: {output_path}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_summary(report: Mapping[str, Any], output_path: Path) -> None:
    if not output_path_allowed(output_path):
        raise ValueError(f"refusing forbidden output path: {output_path}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    summary = report["summary"]
    text = "\n".join(
        [
            "# Source Cache Record",
            "",
            f"- Record: {summary.get('source_cache_record_id')}",
            f"- Status: {summary.get('source_cache_record_status')}",
            f"- Type: {summary.get('source_cache_record_type')}",
            f"- Source: {summary.get('source_label')}",
            f"- Source family: {summary.get('source_family')}",
            f"- Source access: {summary.get('source_access_mode')}",
            f"- Review required: {str(summary.get('review_required')).lower()}",
            f"- Public truth: {str(summary.get('source_cache_record_is_public_truth')).lower()}",
            f"- Accepted evidence: {str(summary.get('source_cache_record_is_accepted_evidence')).lower()}",
            f"- Master-index mutation: {str(summary.get('source_cache_record_can_mutate_master_index')).lower()}",
            "",
        ]
    )
    output_path.write_text(text, encoding="utf-8")


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None, stderr: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="Explicit source cache source JSON input.")
    parser.add_argument("--output", type=Path, help="Optional explicit JSON report output path.")
    parser.add_argument("--summary-output", type=Path, help="Optional explicit Markdown summary output path.")
    parser.add_argument("--check", action="store_true", help="Validate and report status without requiring output.")
    parser.add_argument("--json", action="store_true", help="Print JSON report to stdout.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    out = stdout or sys.stdout
    err = stderr or sys.stderr
    try:
        report = build_report(args.input)
        if args.output:
            write_report(report, args.output)
        if args.summary_output:
            write_summary(report, args.summary_output)
    except Exception as exc:
        err.write(f"record_source_cache: ERROR: {exc}\n")
        return 2

    if args.json:
        out.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        summary = report["summary"]
        out.write("Source cache report\n")
        out.write(f"status: {report['status']}\n")
        out.write(f"source_cache_record_id: {summary.get('source_cache_record_id')}\n")
        out.write(f"source_cache_record_type: {summary.get('source_cache_record_type')}\n")
        out.write(f"source_access_mode: {summary.get('source_access_mode')}\n")
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
