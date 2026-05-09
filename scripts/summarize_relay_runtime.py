#!/usr/bin/env python3
"""Summarize relay profiles, routes, responses, and generated samples."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Mapping

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.relay.profiles import ensure_allowed_relay_input_path, ensure_allowed_relay_output_path, load_json, load_relay_policy  # noqa: E402
from runtime.relay.summaries import summarize_relay_artifacts, summarize_relay_artifacts_markdown  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Summarize relay artifacts.")
    parser.add_argument("--input", action="append", required=True)
    parser.add_argument("--output")
    parser.add_argument("--summary-output")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args(argv)

    policy = load_relay_policy()
    artifacts = _load_artifacts(args.input)
    summary = summarize_relay_artifacts(artifacts, policy)
    markdown = summarize_relay_artifacts_markdown(summary)
    if args.output and not args.check:
        output = ensure_allowed_relay_output_path(args.output, policy)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.summary_output and not args.check:
        output = ensure_allowed_relay_output_path(args.summary_output, policy)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(markdown, encoding="utf-8")
    if args.as_json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print(markdown, end="")
    return 0


def _load_artifacts(inputs: list[str]) -> list[Mapping[str, Any]]:
    artifacts: list[Mapping[str, Any]] = []
    for item in inputs:
        path = ensure_allowed_relay_input_path(item)
        if path.is_dir():
            for json_path in sorted(path.rglob("*.json")):
                artifacts.append(load_json(json_path))
        elif path.suffix.casefold() == ".json":
            artifacts.append(load_json(path))
        else:
            text = path.read_text(encoding="utf-8")
            artifacts.append({"schema_version": "relay_text_artifact.v0", "path": str(path), "length": len(text)})
    return artifacts


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # pragma: no cover - script boundary
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)

