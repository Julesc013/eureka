"""Summarize OBS human review packet items without mutating decisions."""

from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = "control/inventory/observations/obs_human_review_packet_manifest.json"


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description="Summarize OBS human review packet.")
    parser.add_argument("--repo-root", default=str(REPO_ROOT), help="Repository root to inspect.")
    parser.add_argument("--manifest-file", default=MANIFEST_PATH, help="Packet manifest path relative to repo root.")
    parser.add_argument("--json-output", help="Explicit path for JSON summary output.")
    parser.add_argument("--markdown-output", help="Explicit path for Markdown summary output.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    root = Path(args.repo_root).resolve()
    manifest = _load_json(root / args.manifest_file)
    summary = summarize(manifest)
    output = stdout or sys.stdout

    if args.json_output:
        _write_text(root, args.json_output, json.dumps(summary, indent=2, sort_keys=True) + "\n")
    if args.markdown_output:
        _write_text(root, args.markdown_output, format_markdown(summary))
    if not args.json_output and not args.markdown_output:
        output.write(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    return 0


def summarize(manifest: Mapping[str, Any]) -> dict[str, Any]:
    items = [_mapping(item) for item in _sequence_items(manifest.get("review_items"))]
    return {
        "schema_version": "obs_human_review_packet_summary.v0",
        "review_item_count": len(items),
        "by_recommended_decision": dict(sorted(Counter(str(item.get("recommended_decision")) for item in items).items())),
        "by_priority_band": dict(sorted(Counter(str(item.get("priority_band")) for item in items).items())),
        "by_review_item_type": dict(sorted(Counter(str(item.get("review_item_type")) for item in items).items())),
        "source_policy_items": sorted(item.get("review_item_id") for item in items if item.get("review_item_type") == "source_policy_decision_preview"),
        "track_b_dependency_items": sorted(item.get("review_item_id") for item in items if item.get("review_item_type") == "track_b_dependency_review"),
        "blocked_items": sorted(item.get("review_item_id") for item in items if item.get("priority_band") == "blocked" or item.get("recommended_decision") == "mark_policy_blocked"),
        "search_need_seed_items": sorted(item.get("review_item_id") for item in items if item.get("review_item_type") == "search_need_seed_review"),
        "workunit_seed_items": sorted(item.get("review_item_id") for item in items if item.get("review_item_type") == "workunit_seed_review"),
        "human_decision_prefilled_count": sum(1 for item in items if item.get("human_decision") not in (None, "")),
    }


def format_markdown(summary: Mapping[str, Any]) -> str:
    lines = [
        "# OBS Human Review Packet Summary",
        "",
        f"Review item count: {summary.get('review_item_count')}",
        "",
        "## By Recommended Decision",
        "",
        *_counter_lines(_mapping(summary.get("by_recommended_decision"))),
        "",
        "## By Priority Band",
        "",
        *_counter_lines(_mapping(summary.get("by_priority_band"))),
        "",
        "## Source Policy Items",
        "",
        *_list_lines(_sequence_items(summary.get("source_policy_items"))),
        "",
        "## SearchNeed Seed Items",
        "",
        *_list_lines(_sequence_items(summary.get("search_need_seed_items"))),
        "",
        "## WorkUnit Seed Items",
        "",
        *_list_lines(_sequence_items(summary.get("workunit_seed_items"))),
        "",
        "## Track B Dependency Items",
        "",
        *_list_lines(_sequence_items(summary.get("track_b_dependency_items"))),
        "",
        "## Blocked Items",
        "",
        *_list_lines(_sequence_items(summary.get("blocked_items"))),
        "",
        f"Human decisions prefilled: {summary.get('human_decision_prefilled_count')}",
        "",
    ]
    return "\n".join(lines)


def _counter_lines(counter: Mapping[str, Any]) -> list[str]:
    return [f"- `{key}`: {counter[key]}" for key in sorted(counter)] or ["- None."]


def _list_lines(items: Sequence[Any]) -> list[str]:
    return [f"- `{item}`" for item in sorted(str(item) for item in items)] or ["- None."]


def _write_text(repo_root: Path, output_arg: str, text: str) -> None:
    output_path = Path(output_arg)
    if not output_path.is_absolute():
        output_path = repo_root / output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(text, encoding="utf-8")


def _load_json(path: Path) -> Mapping[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, Mapping) else {}


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _sequence_items(value: Any) -> list[Any]:
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return list(value)
    return []


if __name__ == "__main__":
    raise SystemExit(main())
