#!/usr/bin/env python3
"""Summarize local pack draft JSON files."""

from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import sys
import tempfile
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.local_foundry import pack_builder


FORBIDDEN_OUTPUT_PREFIXES = (
    "site/dist",
    "runtime",
    "contracts",
    "site/dist/data/public_index",
    "control/inventory/publication",
    "control/inventory/sources",
    ".aide.local",
    ".local/eureka",
    ".cache/eureka",
    ".git",
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", action="append", required=True, help="Pack draft file or directory; may be repeated.")
    parser.add_argument("--output", help="Optional markdown or JSON output path.")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    try:
        packs = _load_inputs(args.input)
        errors: list[str] = []
        for pack in packs:
            errors.extend(pack_builder.validate_pack_draft(pack))
        if errors:
            for error in sorted(dict.fromkeys(errors)):
                print(f"ERROR: {error}", file=sys.stderr)
            return 1
        summary = _summarize(packs)
        if args.output and not args.check:
            _validate_output_path(args.output)
            output_path = Path(args.output)
            if args.json or output_path.suffix.lower() == ".json":
                _write_text(output_path, json.dumps(summary, indent=2, sort_keys=True) + "\n")
            else:
                _write_text(output_path, _format_summary_markdown(summary))
        if args.json:
            print(json.dumps(summary, indent=2, sort_keys=True))
        else:
            print(_format_summary_markdown(summary), end="")
        return 0
    except Exception as exc:  # pragma: no cover - exercised by subprocess tests
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


def _load_inputs(inputs: list[str]) -> list[dict[str, Any]]:
    packs: list[dict[str, Any]] = []
    for input_text in inputs:
        path = Path(input_text)
        if not path.is_absolute():
            path = REPO_ROOT / path
        if path.is_dir():
            for child in sorted(path.glob("*.json")):
                packs.append(_load_pack(child))
        else:
            packs.append(_load_pack(path))
    return packs


def _load_pack(path: Path) -> dict[str, Any]:
    payload = pack_builder.load_json(path)
    if payload.get("schema_version") == pack_builder.RESULT_SCHEMA_VERSION and isinstance(payload.get("pack_draft"), dict):
        return payload["pack_draft"]
    return payload


def _summarize(packs: list[dict[str, Any]]) -> dict[str, Any]:
    summaries = [pack_builder.summarize_pack_draft(pack) for pack in packs]
    return {
        "pack_draft_count": len(packs),
        "pack_type_counts": dict(sorted(Counter(str(item["pack_type"]) for item in summaries).items())),
        "pack_status_counts": dict(sorted(Counter(str(item["pack_status"]) for item in summaries).items())),
        "input_record_count": sum(int(item["input_record_count"]) for item in summaries),
        "blocked_item_count": sum(int(item["blocked_item_count"]) for item in summaries),
        "review_required_count": sum(1 for item in summaries if item["review_required"]),
        "accepted_pack_count": sum(1 for item in summaries if item["pack_draft_is_accepted_pack"]),
        "public_index_mutation_count": sum(1 for item in summaries if item["pack_draft_can_mutate_public_index"]),
        "master_index_mutation_count": sum(1 for item in summaries if item["pack_draft_can_mutate_master_index"]),
    }


def _format_summary_markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# Local Pack Draft Summary",
        "",
        f"- Pack drafts: {summary['pack_draft_count']}",
        f"- Input records: {summary['input_record_count']}",
        f"- Blocked items: {summary['blocked_item_count']}",
        f"- Review required: {summary['review_required_count']}",
        f"- Accepted packs: {summary['accepted_pack_count']}",
        f"- Public index mutations: {summary['public_index_mutation_count']}",
        f"- Master index mutations: {summary['master_index_mutation_count']}",
        "",
        "## Pack Types",
    ]
    lines.extend(f"- {key}: {value}" for key, value in sorted(summary["pack_type_counts"].items()))
    lines.extend(["", "## Pack Statuses"])
    lines.extend(f"- {key}: {value}" for key, value in sorted(summary["pack_status_counts"].items()))
    return "\n".join(lines) + "\n"


def _validate_output_path(path_text: str) -> None:
    path = Path(path_text)
    resolved = (REPO_ROOT / path).resolve() if not path.is_absolute() else path.resolve()
    rel = _repo_relative(resolved)
    rel_posix = rel.as_posix() if rel is not None else ""
    for prefix in FORBIDDEN_OUTPUT_PREFIXES:
        if rel_posix == prefix or rel_posix.startswith(prefix + "/"):
            raise ValueError(f"output path is forbidden by pack builder path policy: {path_text}")
    if rel is not None:
        parts = rel.parts
        if len(parts) >= 4 and parts[0] == "control" and parts[1] == "audits" and "generated" in parts:
            return
        if len(parts) >= 2 and parts[0] == "examples" and parts[1] == "pack_drafts":
            return
    temp_root = Path(tempfile.gettempdir()).resolve()
    try:
        resolved.relative_to(temp_root)
        return
    except ValueError:
        pass
    raise ValueError(f"output path is not in an allowed pack builder output root: {path_text}")


def _repo_relative(path: Path) -> Path | None:
    try:
        return path.relative_to(REPO_ROOT)
    except ValueError:
        return None


def _write_text(path: Path, payload: str) -> None:
    if not path.is_absolute():
        path = REPO_ROOT / path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(payload, encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
