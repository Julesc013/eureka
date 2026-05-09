#!/usr/bin/env python3
"""Summarize IA connector quality delta and postmortem artifacts."""

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

from runtime.connectors.internet_archive.quality_delta import (  # noqa: E402
    build_h0_readiness_recommendation,
    build_ia_connector_postmortem,
    build_ia_quality_delta,
    detect_quality_overclaim,
    summarize_ia_quality_delta,
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
    ".aide.local",
    ".local/eureka",
    ".cache/eureka",
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", required=True, help="Directory containing IA review integration outputs.")
    parser.add_argument("--output", help="Optional quality delta JSON output path.")
    parser.add_argument("--postmortem-output", help="Optional postmortem JSON output path.")
    parser.add_argument("--h0-output", help="Optional H0 recommendation JSON output path.")
    parser.add_argument("--check", action="store_true", help="Validate and summarize without writing files.")
    parser.add_argument("--json", action="store_true", help="Emit JSON summary.")
    args = parser.parse_args(argv)

    try:
        artifacts = run_summary(args.input_dir)
        if not args.check:
            if args.output:
                _write_json(args.output, artifacts["quality_delta"])
            if args.postmortem_output:
                _write_json(args.postmortem_output, artifacts["postmortem"])
            if args.h0_output:
                _write_json(args.h0_output, artifacts["h0_readiness"])
        summary = summarize_ia_quality_delta(artifacts["quality_delta"])
        if args.json:
            print(json.dumps(summary, indent=2, sort_keys=True), file=stdout)
        else:
            print("IA connector quality delta", file=stdout)
            print(f"status: {summary['delta_status']}", file=stdout)
            print(f"review_entry_count_delta: {summary['review_entry_count_delta']}", file=stdout)
            print(f"blocked_reason_count: {summary['blocked_reason_count']}", file=stdout)
            print(f"claims_external_superiority: {str(summary['claims_external_superiority']).lower()}", file=stdout)
            print(f"claims_production_readiness: {str(summary['claims_production_readiness']).lower()}", file=stdout)
        return 0
    except Exception as exc:  # noqa: BLE001 - CLI validation surface.
        if args.json:
            print(json.dumps({"status": "invalid", "error": str(exc)}, indent=2, sort_keys=True), file=stdout)
        else:
            print("IA connector quality delta", file=stdout)
            print("status: invalid", file=stdout)
            print(f"ERROR: {exc}", file=stdout)
        return 1


def run_summary(input_dir_text: str) -> dict[str, Any]:
    input_dir = Path(input_dir_text)
    if not input_dir.is_absolute():
        input_dir = REPO_ROOT / input_dir
    source_entry = _load_optional(input_dir / "sample_ia_source_cache_review_entry.json")
    evidence_entry = _load_optional(input_dir / "sample_ia_evidence_candidate_review_entry.json")
    promotion = _load_optional(input_dir / "sample_ia_candidate_promotion_dry_run.json")
    pack = _load_optional(input_dir / "sample_ia_pack_draft_preview.json")
    outputs = {
        "source_cache_review_entry": source_entry,
        "evidence_review_entry": evidence_entry,
        "candidate_promotion_dry_run": promotion,
        "pack_draft_preview": pack,
    }
    delta = build_ia_quality_delta(outputs, None)
    postmortem = build_ia_connector_postmortem(delta, outputs, None)
    h0 = build_h0_readiness_recommendation(postmortem, None)
    errors = detect_quality_overclaim(delta) + detect_quality_overclaim(postmortem) + detect_quality_overclaim(h0)
    if errors:
        raise ValueError("; ".join(errors))
    return {
        "quality_delta": delta,
        "postmortem": postmortem,
        "h0_readiness": h0,
    }


def _load_optional(path: Path) -> Mapping[str, Any]:
    if not path.is_file():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, Mapping):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def _write_json(path_text: str, payload: Mapping[str, Any]) -> None:
    path = _safe_output_path(Path(path_text))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


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
        if rel_lower.startswith("examples/connectors/internet_archive/review_integration/"):
            return resolved
        if rel_lower.startswith("control/audits/") and "/generated/" in rel_lower:
            return resolved
        raise ValueError(f"refusing output outside approved IA quality roots: {rel}")
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
