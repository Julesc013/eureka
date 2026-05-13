#!/usr/bin/env python3
"""Build and summarize H2 package-registry quality delta reports offline."""

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

from control.prototypes.legacy_runtime.connectors.h2_package_registries.quality_delta import (  # noqa: E402
    build_h2_quality_delta,
    detect_h2_quality_overclaim,
    summarize_h2_quality_delta,
)
from control.prototypes.legacy_runtime.connectors.h2_package_registries.wave_postmortem import (  # noqa: E402
    build_h2_connector_wave_postmortem,
    build_h2_next_phase_recommendation,
)


FORBIDDEN_OUTPUT_ROOTS = (
    "site/dist",
    "data/public_index",
    "runtime",
    "contracts",
    "control/inventory/publication",
    "control/inventory/sources",
    "data/master_index",
    "master_index",
    "package_cache",
    ".aide.local",
    ".local/eureka",
    ".cache/eureka",
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", action="append", default=[], help="Explicit H2 integration JSON file. May be repeated.")
    parser.add_argument("--input-dir", action="append", default=[], help="Directory containing H2 integration JSON files. May be repeated.")
    parser.add_argument("--output", help="Optional quality delta JSON output path.")
    parser.add_argument("--summary-output", help="Optional markdown summary output path.")
    parser.add_argument("--postmortem-output", help="Optional postmortem JSON output path.")
    parser.add_argument("--recommendation-output", help="Optional next-phase recommendation JSON output path.")
    parser.add_argument("--check", action="store_true", help="Validate only and write no files.")
    parser.add_argument("--json", action="store_true", help="Emit JSON summary.")
    args = parser.parse_args(argv)
    try:
        artifacts = run_quality_delta(args.input, args.input_dir)
        if not args.check:
            if args.output:
                _write_json(args.output, artifacts["quality_delta"])
            if args.postmortem_output:
                _write_json(args.postmortem_output, artifacts["postmortem"])
            if args.recommendation_output:
                _write_json(args.recommendation_output, artifacts["recommendation"])
            if args.summary_output:
                _write_text(args.summary_output, render_summary_markdown(artifacts["summary"]))
        summary = dict(artifacts["summary"])
        summary["wrote_files"] = bool(not args.check and any((args.output, args.summary_output, args.postmortem_output, args.recommendation_output)))
        if args.json:
            print(json.dumps(summary, indent=2, sort_keys=True), file=stdout)
        else:
            print("H2 package quality delta", file=stdout)
            print(f"status: {summary['status']}", file=stdout)
            print(f"source_count: {summary['source_count']}", file=stdout)
            print(f"review_seed_count: {summary['review_seed_count']}", file=stdout)
            print(f"blocked_sources_count: {summary['blocked_sources_count']}", file=stdout)
            print(f"wrote_files: {str(summary['wrote_files']).lower()}", file=stdout)
        return 0
    except Exception as exc:  # noqa: BLE001 - deterministic CLI validation surface.
        if args.json:
            print(json.dumps({"status": "invalid", "error": str(exc)}, indent=2, sort_keys=True), file=stdout)
        else:
            print("H2 package quality delta", file=stdout)
            print("status: invalid", file=stdout)
            print(f"ERROR: {exc}", file=stdout)
        return 1


def run_quality_delta(inputs: Sequence[str], input_dirs: Sequence[str]) -> dict[str, Any]:
    review_result = load_review_integration_result(inputs, input_dirs)
    delta = build_h2_quality_delta({"review_integration_result": review_result})
    postmortem = build_h2_connector_wave_postmortem(review_result, delta)
    recommendation = build_h2_next_phase_recommendation(postmortem)
    errors = detect_h2_quality_overclaim(delta) + detect_h2_quality_overclaim(postmortem) + detect_h2_quality_overclaim(recommendation)
    if errors:
        raise ValueError("; ".join(errors))
    summary = summarize_h2_quality_delta(delta)
    return {
        "review_integration_result": review_result,
        "quality_delta": delta,
        "postmortem": postmortem,
        "recommendation": recommendation,
        "summary": summary,
    }


def load_review_integration_result(inputs: Sequence[str], input_dirs: Sequence[str]) -> Mapping[str, Any]:
    paths = _collect_input_paths(inputs, input_dirs)
    for path in paths:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, Mapping) and payload.get("schema_version") == "h2_package_review_integration_result.v0":
            return dict(payload)
    raise ValueError("no h2_package_review_integration_result.v0 JSON found in inputs")


def render_summary_markdown(summary: Mapping[str, Any]) -> str:
    return "\n".join(
        [
            "# H2 Quality Delta Summary",
            "",
            f"- status: `{summary.get('status')}`",
            f"- source_count: `{summary.get('source_count', 0)}`",
            f"- fixture_sources_count: `{summary.get('fixture_sources_count', 0)}`",
            f"- live_probe_sources_count: `{summary.get('live_probe_sources_count', 0)}`",
            f"- blocked_sources_count: `{summary.get('blocked_sources_count', 0)}`",
            f"- review_seed_count: `{summary.get('review_seed_count', 0)}`",
            "- claims_installability_verified: `false`",
            "- claims_dependency_correctness: `false`",
            "- claims_rights_clearance: `false`",
            "- claims_malware_safety: `false`",
            "- claims_production_readiness: `false`",
            "",
        ]
    )


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
        rel_path = resolved.relative_to(repo_resolved).as_posix()
        rel_lower = rel_path.casefold()
        for forbidden in FORBIDDEN_OUTPUT_ROOTS:
            forbidden_lower = forbidden.casefold().rstrip("/")
            if rel_lower == forbidden_lower or rel_lower.startswith(forbidden_lower + "/"):
                raise ValueError(f"refusing forbidden output root: {forbidden}")
        if rel_lower.startswith("examples/connectors/h2_package_registries/review_integration/"):
            return resolved
        if rel_lower.startswith("control/audits/") and "/generated/" in rel_lower:
            return resolved
        raise ValueError(f"refusing output outside approved H2 quality roots: {rel_path}")
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
