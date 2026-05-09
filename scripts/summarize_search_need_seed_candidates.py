"""Summarize SearchNeed seed draft candidates without mutating them."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST_PATH = "control/inventory/observations/search_need_seed_manifest.json"


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description="Summarize SearchNeed seed draft candidates.")
    parser.add_argument("--repo-root", default=str(REPO_ROOT), help="Repository root to inspect.")
    parser.add_argument("--manifest-file", default=DEFAULT_MANIFEST_PATH, help="Seed manifest JSON path relative to repo root.")
    parser.add_argument("--json-output", help="Optional explicit JSON output path.")
    parser.add_argument("--markdown-output", help="Optional explicit Markdown output path.")
    parser.add_argument("--json", action="store_true", help="Print compact deterministic JSON to stdout.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    root = Path(args.repo_root).resolve()
    manifest_path = root / args.manifest_file
    report = summarize_seed_manifest(manifest_path, root)

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


def summarize_seed_manifest(manifest_path: Path, repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    manifest = _mapping(_load_json(manifest_path, errors))
    records = [_mapping(item) for item in _sequence_items(manifest.get("seed_records"))]
    band_counts = Counter(_priority_band(record.get("proposed_priority")) for record in records)
    type_counts = Counter(str(record.get("seed_type")) for record in records)
    source_family_counts = Counter(str(record.get("source_family")) for record in records)
    failure_counts = Counter(
        mode
        for record in records
        for mode in _string_items(record.get("failure_mode_summary"))
    )
    dependency_counts = Counter(
        dependency
        for dependency in _string_items(manifest.get("downstream_track_b_dependency"))
    )
    grouped: dict[str, list[str]] = defaultdict(list)
    for record in sorted(records, key=lambda item: str(item.get("search_need_seed_id"))):
        grouped[_priority_band(record.get("proposed_priority"))].append(str(record.get("search_need_seed_id")))
    return {
        "schema_version": "search_need_seed_summary.v0",
        "manifest_file": _rel(manifest_path, repo_root),
        "seed_count": len(records),
        "by_priority_band": dict(sorted(band_counts.items())),
        "by_seed_type": dict(sorted(type_counts.items())),
        "by_source_family": dict(sorted(source_family_counts.items())),
        "by_failure_mode": dict(sorted(failure_counts.items())),
        "by_downstream_dependency": dict(sorted(dependency_counts.items())),
        "grouped_seed_ids_by_priority_band": {key: sorted(value) for key, value in sorted(grouped.items())},
        "errors": sorted(errors),
        "product_boundary": {
            "performed_observations": False,
            "called_external_apis": False,
            "opened_browsers": False,
            "scraped_external_systems": False,
            "mutated_master_index": False,
            "accepted_runtime_search_need": False
        }
    }


def format_plain_summary(report: Mapping[str, Any]) -> str:
    lines = [
        "summarize_search_need_seed_candidates:",
        f"- seed_count: {report.get('seed_count')}",
        f"- by_priority_band: {json.dumps(report.get('by_priority_band', {}), sort_keys=True)}",
        f"- by_seed_type: {json.dumps(report.get('by_seed_type', {}), sort_keys=True)}",
        f"- by_source_family: {json.dumps(report.get('by_source_family', {}), sort_keys=True)}",
        f"- by_failure_mode: {json.dumps(report.get('by_failure_mode', {}), sort_keys=True)}",
    ]
    if report.get("errors"):
        lines.append("- errors:")
        lines.extend(f"  - {error}" for error in report["errors"])
    return "\n".join(lines) + "\n"


def format_markdown_summary(report: Mapping[str, Any]) -> str:
    lines = [
        "# SearchNeed Seed Candidate Summary",
        "",
        f"Seed drafts: {report.get('seed_count')}",
        "",
        "## Priority Bands",
        "",
    ]
    lines.extend(f"- `{key}`: {value}" for key, value in _mapping(report.get("by_priority_band")).items())
    lines.extend(["", "## Seed Types", ""])
    lines.extend(f"- `{key}`: {value}" for key, value in _mapping(report.get("by_seed_type")).items())
    lines.extend(["", "## Source Families", ""])
    lines.extend(f"- `{key}`: {value}" for key, value in _mapping(report.get("by_source_family")).items())
    lines.extend(["", "## Failure Modes", ""])
    lines.extend(f"- `{key}`: {value}" for key, value in _mapping(report.get("by_failure_mode")).items())
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- This summary does not approve seeds.",
            "- This summary does not create runtime SearchNeeds.",
            "- This summary does not accept evidence or mutate the master index.",
            "",
        ]
    )
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


def _string_items(value: Any) -> list[str]:
    return [item for item in _sequence_items(value) if isinstance(item, str)]


def _priority_band(priority: Any) -> str:
    value = _mapping(priority).get("band")
    return str(value) if isinstance(value, str) else "insufficient_local_evidence"


def _rel(path: Path, repo_root: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


if __name__ == "__main__":
    raise SystemExit(main())
