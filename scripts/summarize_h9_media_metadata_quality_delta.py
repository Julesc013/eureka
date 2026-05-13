#!/usr/bin/env python3
"""Summarize explicit H9 media metadata review integration outputs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import tempfile
from typing import Any, Mapping, Sequence, TextIO

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

FORBIDDEN_OUTPUT_ROOTS = (
"site/dist",
"data/public_index",
"runtime",
"contracts",
"control/inventory/publication",
"control/inventory/sources",
"data/master_index",
"master_index",
"downloads",
"media_downloads",
"media_uploads",
"fingerprint_cache",
"fingerprint_output",
"image_downloads",
"video_downloads",
"audio_downloads",
"map_downloads",
"score_downloads",
"thumbnail_downloads",
"restricted_sources",
".aide.local",
".local/eureka",
".cache/eureka",
)

from control.prototypes.legacy_runtime.connectors.h9_media_metadata.quality_delta import (  # noqa: E402
    build_h9_quality_delta,
    detect_h9_quality_overclaim,
    summarize_h9_quality_delta,
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", action="append", default=[], help="Explicit H9 integration JSON file. May be repeated.")
    parser.add_argument("--input-dir", action="append", default=[], help="Directory containing H9 integration JSON files. May be repeated.")
    parser.add_argument("--output", help="Optional JSON output path.")
    parser.add_argument("--summary-output", help="Optional Markdown summary output path.")
    parser.add_argument("--check", action="store_true", help="Validate only and write no files.")
    parser.add_argument("--json", action="store_true", help="Emit JSON summary.")
    args = parser.parse_args(argv)
    try:
        delta = build_quality_delta(args.input, args.input_dir)
        if args.output and not args.check:
            write_json(args.output, delta)
        summary = summarize_h9_quality_delta(delta)
        if args.summary_output and not args.check:
            write_text(args.summary_output, render_summary_markdown(summary))
        summary["wrote_files"] = bool((args.output or args.summary_output) and not args.check)
        if args.json:
            print(json.dumps(summary, indent=2, sort_keys=True), file=stdout)
        else:
            print("H9 media metadata quality delta", file=stdout)
            print(f"status: {summary['status']}", file=stdout)
            print(f"source_count: {summary['source_count']}", file=stdout)
            print(f"review_seed_count: {summary['review_seed_count']}", file=stdout)
            print(f"blocked_sources_count: {summary['blocked_sources_count']}", file=stdout)
            print(f"wrote_files: {str(summary['wrote_files']).lower()}", file=stdout)
        return 0
    except Exception as exc:  # noqa: BLE001
        if args.json:
            print(json.dumps({"status": "invalid", "error": str(exc)}, indent=2, sort_keys=True), file=stdout)
        else:
            print("H9 media metadata quality delta", file=stdout)
            print("status: invalid", file=stdout)
            print(f"ERROR: {exc}", file=stdout)
        return 1


def build_quality_delta(inputs: Sequence[str], input_dirs: Sequence[str]) -> dict[str, Any]:
    payloads = [load_json(path) for path in _collect_input_paths(inputs, input_dirs)]
    review = next((payload for payload in payloads if payload.get("schema_version") == "h9_media_metadata_review_integration_result.v0"), None)
    if review is None:
        raise ValueError("no h9_media_metadata_review_integration_result.v0 input found")
    delta = build_h9_quality_delta({"review_integration_result": review})
    errors = detect_h9_quality_overclaim(delta)
    if errors:
        raise ValueError("; ".join(errors))
    return delta


def render_summary_markdown(summary: Mapping[str, Any]) -> str:
    return "\n".join([
        "# H9 Quality Delta Summary",
        "",
        f"- status: `{summary.get('status')}`",
        f"- source_count: `{summary.get('source_count', 0)}`",
        f"- fixture_sources_count: `{summary.get('fixture_sources_count', 0)}`",
        f"- live_probe_sources_count: `{summary.get('live_probe_sources_count', 0)}`",
        f"- blocked_sources_count: `{summary.get('blocked_sources_count', 0)}`",
        f"- review_seed_count: `{summary.get('review_seed_count', 0)}`",
        "- media_authenticity_verified: `false`",
        "- audio_identity_verified: `false`",
        "- image_identity_verified: `false`",
        "- rights_clearance: `false`",
        "- public_domain_truth: `false`",
        "- creative_commons_truth: `false`",
        "- content_safety: `false`",
        "- privacy_safety: `false`",
        "- malware_safety: `false`",
        "- verified_authenticity: `false`",
        "",
    ])


def write_json(path_text: str, payload: Mapping[str, Any]) -> None:
    path = _safe_output_path(Path(path_text))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_text(path_text: str, text: str) -> None:
    path = _safe_output_path(Path(path_text))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, Mapping):
        raise ValueError(f"{path} must contain a JSON object")
    return dict(payload)


def _collect_input_paths(inputs: Sequence[str], input_dirs: Sequence[str]) -> list[Path]:
    paths: list[Path] = []
    for item in inputs:
        paths.append(_resolve_input(Path(item)))
    for item in input_dirs:
        directory = _resolve_input(Path(item))
        if not directory.is_dir():
            raise ValueError(f"input-dir is not a directory: {directory}")
        paths.extend(sorted(path for path in directory.glob("*.json") if path.is_file()))
    if not paths:
        raise ValueError("at least one --input or --input-dir is required")
    return paths


def _resolve_input(path: Path) -> Path:
    resolved = (REPO_ROOT / path).resolve() if not path.is_absolute() else path.resolve()
    if not resolved.exists():
        raise ValueError(f"input path does not exist: {resolved}")
    return resolved


def _safe_output_path(path: Path) -> Path:
    resolved = (REPO_ROOT / path).resolve() if not path.is_absolute() else path.resolve()
    repo_resolved = REPO_ROOT.resolve()
    try:
        rel_path = resolved.relative_to(repo_resolved).as_posix()
        rel_lower = rel_path.casefold()
        for forbidden in FORBIDDEN_OUTPUT_ROOTS:
            forbidden_lower = forbidden.casefold().rstrip("/")
            if rel_lower == forbidden_lower or rel_lower.startswith(forbidden_lower + "/"):
                raise ValueError(f"refusing forbidden output root: {forbidden}")
        if rel_lower.startswith("examples/connectors/h9_media_metadata/review_integration/"):
            return resolved
        if rel_lower.startswith("control/audits/") and "/generated/" in rel_lower:
            return resolved
        raise ValueError(f"refusing output outside approved H9 review roots: {rel_path}")
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
