#!/usr/bin/env python3
"""Run a local, explicit-input candidate promotion dry-run."""

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

from runtime.local_foundry import candidate_promotion_dry_run as promotion  # noqa: E402


FORBIDDEN_OUTPUT_ROOTS = (
    "site/dist",
    "runtime",
    "contracts",
    "control/inventory/publication",
    "control/inventory/sources",
    "control/inventory/master_index",
    "control/master_index",
    "master_index",
    "public_index",
    "evals/search_usefulness/external_baselines",
    ".aide.local",
    ".local/eureka",
    ".cache/eureka",
    ".git",
)


def output_path_allowed(path: Path) -> bool:
    resolved = path.resolve()
    try:
        rel = resolved.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        try:
            resolved.relative_to(Path(tempfile.gettempdir()).resolve())
            return True
        except ValueError:
            return False
    if any(rel == root or rel.startswith(root + "/") for root in FORBIDDEN_OUTPUT_ROOTS):
        return False
    return rel.startswith("control/audits/") and "/generated/" in rel


def load_records(paths: Sequence[Path]) -> list[dict[str, Any]]:
    return [promotion.load_json(path) for path in paths]


def build_report(
    *,
    candidate_path: Path | None = None,
    evidence_paths: Sequence[Path] = (),
    review_paths: Sequence[Path] = (),
    source_cache_paths: Sequence[Path] = (),
    bridge_paths: Sequence[Path] = (),
    input_path: Path | None = None,
) -> dict[str, Any]:
    if input_path:
        record = promotion.build_candidate_promotion_dry_run(promotion.load_json(input_path))
        input_ref = input_path.as_posix()
    else:
        if candidate_path is None:
            raise ValueError("--candidate is required unless --input is provided")
        payload = {
            "candidate": promotion.load_json(candidate_path),
            "evidence_records": load_records(evidence_paths),
            "review_entries": load_records(review_paths),
            "source_cache_records": load_records(source_cache_paths),
            "bridge_results": load_records(bridge_paths),
            "input_id": candidate_path.stem,
            "input_type": "candidate_record",
        }
        record = promotion.build_candidate_promotion_dry_run(payload)
        input_ref = candidate_path.as_posix()

    errors = promotion.validate_candidate_promotion_dry_run(record)
    summary = promotion.summarize_candidate_promotion_dry_run(record)
    return {
        "schema_version": promotion.REPORT_SCHEMA_VERSION,
        "status": "pass" if not errors else "fail",
        "input_ref": input_ref,
        "record": record,
        "summary": summary,
        "validation_errors": errors,
        "runtime_scope": {
            "explicit_input_only": True,
            "local_only": True,
            "fixture_only": True,
            "writes_no_files_by_default": True,
            "promotion_dry_run_only": True,
            "candidate_acceptance_enabled": False,
            "evidence_acceptance_enabled": False,
            "public_index_mutation_enabled": False,
            "master_index_mutation_enabled": False,
        },
        "truth_boundary": {
            "promotion_dry_run_is_public_truth": False,
            "promotion_dry_run_accepts_candidate": False,
            "promotion_dry_run_accepts_evidence": False,
            "promotion_dry_run_can_mutate_public_index": False,
            "promotion_dry_run_can_mutate_master_index": False,
            "human_review_required_for_actual_promotion": True,
        },
        "product_boundary": record.get("product_boundary", {}),
    }


def write_record(report: Mapping[str, Any], output_path: Path) -> None:
    if not output_path_allowed(output_path):
        raise ValueError(f"refusing forbidden output path: {output_path}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report["record"], indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_summary(report: Mapping[str, Any], output_path: Path) -> None:
    if not output_path_allowed(output_path):
        raise ValueError(f"refusing forbidden output path: {output_path}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(promotion.format_candidate_promotion_summary_markdown(report["summary"]), encoding="utf-8")


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None, stderr: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", type=Path, help="Explicit candidate record JSON input.")
    parser.add_argument("--evidence", action="append", default=[], type=Path, help="Evidence ledger record JSON input.")
    parser.add_argument("--review", action="append", default=[], type=Path, help="Review queue entry JSON input.")
    parser.add_argument("--source-cache", action="append", default=[], type=Path, help="Source cache record JSON input.")
    parser.add_argument("--bridge", action="append", default=[], type=Path, help="Source-cache-to-evidence bridge result JSON input.")
    parser.add_argument("--input", type=Path, help="Direct promotion dry-run record JSON input.")
    parser.add_argument("--output", type=Path, help="Optional explicit dry-run record output path.")
    parser.add_argument("--summary-output", type=Path, help="Optional explicit Markdown summary output path.")
    parser.add_argument("--check", action="store_true", help="Validate and report status without requiring output.")
    parser.add_argument("--json", action="store_true", help="Print JSON report to stdout.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    out = stdout or sys.stdout
    err = stderr or sys.stderr
    try:
        report = build_report(
            candidate_path=args.candidate,
            evidence_paths=args.evidence,
            review_paths=args.review,
            source_cache_paths=args.source_cache,
            bridge_paths=args.bridge,
            input_path=args.input,
        )
        if args.output:
            write_record(report, args.output)
        if args.summary_output:
            write_summary(report, args.summary_output)
    except Exception as exc:
        err.write(f"run_candidate_promotion_dry_run: ERROR: {exc}\n")
        return 2

    if args.json:
        out.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        summary = report["summary"]
        out.write("Candidate promotion dry-run\n")
        out.write(f"status: {report['status']}\n")
        out.write(f"promotion_dry_run_id: {summary.get('promotion_dry_run_id')}\n")
        out.write(f"promotion_readiness: {summary.get('promotion_readiness')}\n")
        out.write(f"candidate_ref: {summary.get('candidate_ref')}\n")
        out.write(f"blocker_count: {summary.get('blocker_count')}\n")
        if report["validation_errors"]:
            out.write("validation_errors:\n")
            for error in report["validation_errors"]:
                out.write(f"- {error}\n")
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
