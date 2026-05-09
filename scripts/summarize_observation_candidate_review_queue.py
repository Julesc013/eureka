"""Summarize the ObservationCandidate review queue without mutating it."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_QUEUE_PATH = "control/inventory/observations/observation_candidate_review_queue.json"


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description="Summarize observation candidate review queue.")
    parser.add_argument("--repo-root", default=str(REPO_ROOT), help="Repository root to inspect.")
    parser.add_argument("--queue-file", default=DEFAULT_QUEUE_PATH, help="Queue JSON path relative to repo root.")
    parser.add_argument("--json-output", help="Optional explicit JSON output path.")
    parser.add_argument("--markdown-output", help="Optional explicit Markdown output path.")
    parser.add_argument("--json", action="store_true", help="Print compact deterministic JSON to stdout.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    root = Path(args.repo_root).resolve()
    queue_path = root / args.queue_file
    report = summarize_review_queue(queue_path, root)

    if args.json_output:
        _write_text(root, args.json_output, json.dumps(report, indent=2, sort_keys=True) + "\n")
    if args.markdown_output:
        _write_text(root, args.markdown_output, format_markdown_summary(report))

    output = stdout or sys.stdout
    if args.json:
        output.write(json.dumps(report, sort_keys=True) + "\n")
    else:
        output.write(format_plain_summary(report))
    return 0 if not report.get("errors") else 1


def summarize_review_queue(queue_path: Path, repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    queue = _mapping(_load_json(queue_path, errors))
    entries = [_mapping(item) for item in _sequence_items(queue.get("queue_entries"))]
    action_counts = Counter(str(entry.get("recommended_review_action")) for entry in entries)
    band_counts = Counter(str(entry.get("priority_band")) for entry in entries)
    family_counts = Counter(str(entry.get("source_family")) for entry in entries)
    type_counts = Counter(str(entry.get("candidate_type")) for entry in entries)
    grouped: dict[str, list[str]] = defaultdict(list)
    for entry in sorted(entries, key=lambda item: str(item.get("observation_candidate_id"))):
        grouped[str(entry.get("recommended_review_action"))].append(str(entry.get("observation_candidate_id")))
    return {
        "schema_version": "observation_candidate_review_queue_summary.v0",
        "queue_file": _rel(queue_path, repo_root),
        "queue_status": queue.get("queue_status"),
        "queue_entry_count": len(entries),
        "by_recommended_action": dict(sorted(action_counts.items())),
        "by_priority_band": dict(sorted(band_counts.items())),
        "by_source_family": dict(sorted(family_counts.items())),
        "by_candidate_type": dict(sorted(type_counts.items())),
        "grouped_candidate_ids": {key: sorted(value) for key, value in sorted(grouped.items())},
        "errors": sorted(errors),
        "product_boundary": {
            "performed_observations": False,
            "called_external_apis": False,
            "opened_browsers": False,
            "scraped_external_systems": False,
            "mutated_master_index": False
        }
    }


def format_plain_summary(report: Mapping[str, Any]) -> str:
    lines = [
        "summarize_observation_candidate_review_queue:",
        f"- queue_entry_count: {report.get('queue_entry_count')}",
        f"- by_recommended_action: {json.dumps(report.get('by_recommended_action', {}), sort_keys=True)}",
        f"- by_priority_band: {json.dumps(report.get('by_priority_band', {}), sort_keys=True)}",
        f"- by_source_family: {json.dumps(report.get('by_source_family', {}), sort_keys=True)}",
        f"- by_candidate_type: {json.dumps(report.get('by_candidate_type', {}), sort_keys=True)}",
    ]
    if report.get("errors"):
        lines.append("- errors:")
        lines.extend(f"  - {error}" for error in report["errors"])
    return "\n".join(lines) + "\n"


def format_markdown_summary(report: Mapping[str, Any]) -> str:
    lines = [
        "# Observation Candidate Review Queue Summary",
        "",
        f"Queue entries: {report.get('queue_entry_count')}",
        "",
        "## Recommended Actions",
        "",
    ]
    lines.extend(f"- `{key}`: {value}" for key, value in _mapping(report.get("by_recommended_action")).items())
    lines.extend(["", "## Priority Bands", ""])
    lines.extend(f"- `{key}`: {value}" for key, value in _mapping(report.get("by_priority_band")).items())
    lines.extend(["", "## Source Families", ""])
    lines.extend(f"- `{key}`: {value}" for key, value in _mapping(report.get("by_source_family")).items())
    lines.extend(["", "## Candidate Types", ""])
    lines.extend(f"- `{key}`: {value}" for key, value in _mapping(report.get("by_candidate_type")).items())
    lines.extend(["", "## Boundary", "", "- This summary does not approve, reject, observe, convert, or mutate candidates.", ""])
    return "\n".join(lines)


def _write_text(repo_root: Path, output_arg: str, text: str) -> None:
    output_path = Path(output_arg)
    if not output_path.is_absolute():
        output_path = repo_root / output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(text, encoding="utf-8")


def _load_json(path: Path, errors: list[str]) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"{path.as_posix()}: missing JSON file")
    except json.JSONDecodeError as exc:
        errors.append(f"{path.as_posix()}: invalid JSON at line {exc.lineno}: {exc.msg}")
    return {}


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _sequence_items(value: Any) -> list[Any]:
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return list(value)
    return []


def _rel(path: Path, repo_root: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


if __name__ == "__main__":
    raise SystemExit(main())
