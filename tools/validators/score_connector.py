#!/usr/bin/env python3
"""Build or validate connector scorecards offline."""

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

from runtime.connectors.core.connector_scorecard import (  # noqa: E402
    build_connector_scorecard,
    summarize_connector_scorecard,
    validate_connector_scorecard,
)


FORBIDDEN_OUTPUT_ROOTS = ("site/dist", "site/dist/data/public_index", "runtime", "contracts", "data/master_index", "master_index", ".aide.local", ".local/eureka", ".cache/eureka")


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="Connector scorecard or scorecard-like JSON input.")
    parser.add_argument("--output", help="Optional scorecard JSON output.")
    parser.add_argument("--summary-output", help="Optional Markdown summary output.")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        payload = _load_json(args.input)
        scorecard = payload if payload.get("schema_version") == "connector_scorecard.v0" else build_connector_scorecard(payload, {})
        validate_connector_scorecard(scorecard, {})
        summary = summarize_connector_scorecard(scorecard, {})
        if not args.check:
            if args.output:
                _write_json(args.output, scorecard)
            if args.summary_output:
                _write_text(args.summary_output, render_summary_markdown(summary))
        report = {"status": "pass", "connector_scorecard_id": scorecard.get("connector_scorecard_id"), "summary": summary}
        if args.json:
            print(json.dumps(report, indent=2, sort_keys=True), file=stdout)
        else:
            print("Connector scorecard", file=stdout)
            print("status: pass", file=stdout)
            print(f"connector_scorecard_id: {scorecard.get('connector_scorecard_id')}", file=stdout)
        return 0
    except Exception as exc:  # noqa: BLE001
        if args.json:
            print(json.dumps({"status": "fail", "error": str(exc)}, indent=2, sort_keys=True), file=stdout)
        else:
            print("Connector scorecard", file=stdout)
            print("status: fail", file=stdout)
            print(f"ERROR: {exc}", file=stdout)
        return 1


def render_summary_markdown(summary: Mapping[str, Any]) -> str:
    return "\n".join([
        "# Connector Scorecard Summary",
        "",
        f"- connector_id: `{summary.get('connector_id')}`",
        f"- scorecard_status: `{summary.get('scorecard_status')}`",
        f"- warning_count: `{summary.get('warning_count')}`",
        f"- blocker_count: `{summary.get('blocker_count')}`",
        "",
    ])


def _load_json(path_text: str) -> dict[str, Any]:
    path = Path(path_text)
    resolved = (REPO_ROOT / path).resolve() if not path.is_absolute() else path.resolve()
    payload = json.loads(resolved.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected JSON object: {path_text}")
    return payload


def _write_json(path_text: str, payload: Mapping[str, Any]) -> None:
    path = _safe_output_path(Path(path_text))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_text(path_text: str, text: str) -> None:
    path = _safe_output_path(Path(path_text))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _safe_output_path(path: Path) -> Path:
    resolved = (REPO_ROOT / path).resolve() if not path.is_absolute() else path.resolve()
    repo_resolved = REPO_ROOT.resolve()
    try:
        rel = resolved.relative_to(repo_resolved).as_posix()
        rel_lower = rel.casefold()
        for forbidden in FORBIDDEN_OUTPUT_ROOTS:
            forbidden_lower = forbidden.casefold().rstrip("/")
            if rel_lower == forbidden_lower or rel_lower.startswith(forbidden_lower + "/"):
                raise ValueError(f"refusing forbidden output root: {forbidden}")
        if rel_lower.startswith("control/audits/") and "/generated/" in rel_lower:
            return resolved
        if rel_lower.startswith("examples/connectors/core/scorecards/"):
            return resolved
        raise ValueError(f"refusing output outside approved scorecard roots: {rel}")
    except ValueError as exc:
        if str(exc).startswith("refusing"):
            raise
        temp_root = Path(tempfile.gettempdir()).resolve()
        try:
            resolved.relative_to(temp_root)
            return resolved
        except ValueError as temp_exc:
            raise ValueError(f"refusing output outside repository approved roots or temp directory: {resolved}") from temp_exc


if __name__ == "__main__":
    raise SystemExit(main())
