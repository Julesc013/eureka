"""Summarize observation candidate examples without mutating them."""

from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CANDIDATE_DIR = "examples/observation_candidates"


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description="Summarize observation candidate records.")
    parser.add_argument("--repo-root", default=str(REPO_ROOT), help="Repository root to inspect.")
    parser.add_argument("--candidate-dir", default=DEFAULT_CANDIDATE_DIR, help="Candidate directory relative to repo root.")
    parser.add_argument("--json-output", help="Optional explicit JSON output path.")
    parser.add_argument("--json", action="store_true", help="Print compact deterministic JSON to stdout.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    root = Path(args.repo_root).resolve()
    report = summarize_observation_candidates(root / args.candidate_dir, root)
    if args.json_output:
        output_path = root / args.json_output
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    output = stdout or sys.stdout
    if args.json:
        output.write(json.dumps(report, sort_keys=True) + "\n")
    else:
        output.write(format_summary(report))
    return 0


def summarize_observation_candidates(candidate_dir: Path, repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    errors: list[str] = []
    for path in sorted(candidate_dir.glob("*.json")):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"{_rel(path, repo_root)}: invalid JSON at line {exc.lineno}")
            continue
        if isinstance(payload, Mapping):
            records.append(
                {
                    "path": _rel(path, repo_root),
                    "observation_candidate_id": payload.get("observation_candidate_id"),
                    "candidate_type": payload.get("candidate_type"),
                    "candidate_status": payload.get("candidate_status"),
                    "source_access_mode": payload.get("source_access_mode"),
                    "required_human_review": payload.get("required_human_review"),
                }
            )
    type_counts = Counter(str(record.get("candidate_type")) for record in records)
    status_counts = Counter(str(record.get("candidate_status")) for record in records)
    review_counts = Counter("review_required" if record.get("required_human_review") is True else "review_not_marked" for record in records)
    return {
        "schema_version": "observation_candidate_summary.v0",
        "candidate_dir": _rel(candidate_dir, repo_root),
        "candidate_count": len(records),
        "by_type": dict(sorted(type_counts.items())),
        "by_status": dict(sorted(status_counts.items())),
        "by_review_need": dict(sorted(review_counts.items())),
        "records": records,
        "errors": sorted(errors),
        "product_boundary": {
            "performed_observations": False,
            "called_external_apis": False,
            "opened_browsers": False,
            "scraped_external_systems": False,
            "mutated_master_index": False
        }
    }


def format_summary(report: Mapping[str, Any]) -> str:
    lines = [
        "summarize_observation_candidates:",
        f"- candidate_count: {report.get('candidate_count')}",
        f"- by_type: {json.dumps(report.get('by_type', {}), sort_keys=True)}",
        f"- by_status: {json.dumps(report.get('by_status', {}), sort_keys=True)}",
        f"- by_review_need: {json.dumps(report.get('by_review_need', {}), sort_keys=True)}",
    ]
    if report.get("errors"):
        lines.append("- errors:")
        lines.extend(f"  - {error}" for error in report["errors"])
    return "\n".join(lines) + "\n"


def _rel(path: Path, repo_root: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


if __name__ == "__main__":
    raise SystemExit(main())
