#!/usr/bin/env python3
"""Record a local review queue entry from explicit JSON input."""

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

from runtime.local_foundry import review_queue  # noqa: E402


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


def build_report(
    input_path: Path,
    *,
    subject_type: str | None = None,
    decision: str | None = None,
    repo_root: Path = REPO_ROOT,
) -> dict[str, Any]:
    payload = review_queue.load_json(input_path)
    if subject_type:
        payload["review_subject_type"] = subject_type
    if decision:
        payload["review_decision"] = decision
    entry = review_queue.build_review_queue_entry(payload)
    errors = review_queue.validate_review_queue_entry(entry)
    summary = review_queue.summarize_review_queue_entry(entry)
    return {
        "schema_version": review_queue.REPORT_SCHEMA_VERSION,
        "status": "pass" if not errors else "fail",
        "input_ref": _display_path(input_path, repo_root),
        "entry": entry,
        "summary": summary,
        "validation_errors": errors,
        "warnings": [],
        "runtime_scope": {
            "explicit_input_only": True,
            "local_only": True,
            "fixture_only": True,
            "writes_no_files_by_default": True,
            "hosted_review_enabled": False,
            "evidence_acceptance_enabled": False,
            "candidate_acceptance_enabled": False,
            "master_index_mutation_enabled": False,
        },
        "truth_boundary": {
            "review_entry_is_public_truth": False,
            "review_entry_accepts_evidence": False,
            "review_entry_accepts_candidate": False,
            "review_entry_can_mutate_master_index": False,
            "human_review_required_for_downstream_use": True,
        },
        "product_boundary": entry["product_boundary"],
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


def write_entry(report: Mapping[str, Any], output_path: Path) -> None:
    if not output_path_allowed(output_path):
        raise ValueError(f"refusing forbidden output path: {output_path}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report["entry"], indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_summary(report: Mapping[str, Any], output_path: Path) -> None:
    if not output_path_allowed(output_path):
        raise ValueError(f"refusing forbidden output path: {output_path}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    summary = report["summary"]
    text = "\n".join(
        [
            "# Review Queue Entry",
            "",
            f"- Entry: {summary.get('review_entry_id')}",
            f"- Status: {summary.get('review_entry_status')}",
            f"- Subject: {summary.get('review_subject_type')}",
            f"- Decision: {summary.get('review_decision')}",
            f"- Promotion dry-run ready: {str(summary.get('promotion_dry_run_ready')).lower()}",
            f"- Public truth: {str(summary.get('review_entry_is_public_truth')).lower()}",
            f"- Accepts evidence: {str(summary.get('review_entry_accepts_evidence')).lower()}",
            f"- Accepts candidate: {str(summary.get('review_entry_accepts_candidate')).lower()}",
            f"- Master-index mutation: {str(summary.get('review_entry_mutates_master_index')).lower()}",
            "",
        ]
    )
    output_path.write_text(text, encoding="utf-8")


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None, stderr: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="Explicit review subject JSON input.")
    parser.add_argument("--subject-type", help="Optional subject type override for explicit local examples.")
    parser.add_argument("--decision", help="Optional review decision override for explicit local examples.")
    parser.add_argument("--output", type=Path, help="Optional explicit review queue entry output path.")
    parser.add_argument("--summary-output", type=Path, help="Optional explicit Markdown summary output path.")
    parser.add_argument("--check", action="store_true", help="Validate and report status without requiring output.")
    parser.add_argument("--json", action="store_true", help="Print JSON report to stdout.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    out = stdout or sys.stdout
    err = stderr or sys.stderr
    try:
        report = build_report(args.input, subject_type=args.subject_type, decision=args.decision)
        if args.output:
            write_entry(report, args.output)
        if args.summary_output:
            write_summary(report, args.summary_output)
    except Exception as exc:
        err.write(f"record_review_queue: ERROR: {exc}\n")
        return 2

    if args.json:
        out.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        summary = report["summary"]
        out.write("Review queue report\n")
        out.write(f"status: {report['status']}\n")
        out.write(f"review_entry_id: {summary.get('review_entry_id')}\n")
        out.write(f"review_subject_type: {summary.get('review_subject_type')}\n")
        out.write(f"review_decision: {summary.get('review_decision')}\n")
        out.write(f"promotion_dry_run_ready: {str(summary.get('promotion_dry_run_ready')).lower()}\n")
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
