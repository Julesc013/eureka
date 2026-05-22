"""Summarize the OBS to Track B synchronization handoff."""

from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]
MATRIX_PATH = "control/inventory/observations/obs_track_b_sync_matrix.json"
READINESS_PATH = "control/inventory/observations/obs_track_b_handoff_readiness.json"


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description="Summarize OBS/Track B handoff readiness.")
    parser.add_argument("--repo-root", default=str(REPO_ROOT), help="Repository root to inspect.")
    parser.add_argument("--matrix-file", default=MATRIX_PATH, help="Sync matrix path relative to repo root.")
    parser.add_argument("--readiness-file", default=READINESS_PATH, help="Readiness inventory path relative to repo root.")
    parser.add_argument("--json-output", help="Explicit path for JSON summary output.")
    parser.add_argument("--markdown-output", help="Explicit path for Markdown summary output.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    root = Path(args.repo_root).resolve()
    matrix = _load_json(root / args.matrix_file)
    readiness = _load_json(root / args.readiness_file)
    summary = summarize(matrix, readiness)
    output = stdout or sys.stdout

    if args.json_output:
        _write_text(root, args.json_output, json.dumps(summary, indent=2, sort_keys=True) + "\n")
    if args.markdown_output:
        _write_text(root, args.markdown_output, format_markdown(summary))
    if not args.json_output and not args.markdown_output:
        output.write(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    return 0


def summarize(matrix: Mapping[str, Any], readiness: Mapping[str, Any]) -> dict[str, Any]:
    mappings = [_mapping(item) for item in _sequence_items(matrix.get("mappings"))]
    return {
        "schema_version": "obs_track_b_handoff_summary.v0",
        "mapping_count": len(mappings),
        "by_handoff_state": dict(sorted(Counter(str(item.get("current_handoff_state")) for item in mappings).items())),
        "by_track_b_dependency": dict(sorted(Counter(str(item.get("track_b_artifact_family")) for item in mappings).items())),
        "human_review_required": sorted(item.get("mapping_id") for item in mappings if item.get("human_review_required") is True),
        "source_policy_required": sorted(item.get("mapping_id") for item in mappings if item.get("source_policy_approval_required") is True),
        "blocked_items": sorted(_sequence_items(matrix.get("blocked_items"))),
        "ready_items": sorted(_sequence_items(matrix.get("ready_items"))),
        "readiness": {
            "ready_for_parallel_continuation": readiness.get("ready_for_parallel_continuation"),
            "ready_for_runtime_consumption": readiness.get("ready_for_runtime_consumption"),
            "ready_for_source_policy_decision": readiness.get("ready_for_source_policy_decision"),
            "ready_for_workunit_runtime": readiness.get("ready_for_workunit_runtime"),
            "ready_for_public_index_effect": readiness.get("ready_for_public_index_effect"),
        },
        "recommended_next_obs_task": readiness.get("recommended_next_obs_task"),
        "recommended_next_track_b_task": readiness.get("recommended_next_track_b_task"),
    }


def format_markdown(summary: Mapping[str, Any]) -> str:
    lines = [
        "# OBS to Track B Handoff Summary",
        "",
        f"Mapping count: {summary.get('mapping_count')}",
        "",
        "## Sync Decision",
        "",
    ]
    readiness = _mapping(summary.get("readiness"))
    for key in (
        "ready_for_parallel_continuation",
        "ready_for_runtime_consumption",
        "ready_for_source_policy_decision",
        "ready_for_workunit_runtime",
        "ready_for_public_index_effect",
    ):
        lines.append(f"- `{key}`: `{readiness.get(key)}`")
    lines.extend(["", "## By Handoff State", ""])
    lines.extend(_counter_lines(_mapping(summary.get("by_handoff_state"))))
    lines.extend(["", "## By Track B Dependency", ""])
    lines.extend(_counter_lines(_mapping(summary.get("by_track_b_dependency"))))
    lines.extend(["", "## Human Review Required", ""])
    lines.extend(_list_lines(_sequence_items(summary.get("human_review_required"))))
    lines.extend(["", "## Source Policy Required", ""])
    lines.extend(_list_lines(_sequence_items(summary.get("source_policy_required"))))
    lines.extend(["", "## Blocked Items", ""])
    lines.extend(_list_lines(_sequence_items(summary.get("blocked_items"))))
    lines.extend(["", "## Ready Items", ""])
    lines.extend(_list_lines(_sequence_items(summary.get("ready_items"))))
    lines.extend(
        [
            "",
            "## Next",
            "",
            f"- OBS: `{summary.get('recommended_next_obs_task')}`",
            f"- Track B: `{summary.get('recommended_next_track_b_task')}`",
            "",
        ]
    )
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
