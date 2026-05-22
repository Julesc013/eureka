#!/usr/bin/env python3
"""Integrate IA metadata probe outputs into dry-run review artifacts."""

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

from runtime.connectors.internet_archive.review_integration import (  # noqa: E402
    build_ia_candidate_promotion_dry_run,
    build_ia_evidence_candidate_review_entry,
    build_ia_pack_draft_preview,
    build_ia_review_integration_summary,
    build_ia_source_cache_review_entry,
    detect_ia_review_product_boundary_violations,
    detect_ia_review_truth_boundary_violations,
    load_ia_probe_outputs,
)


FORBIDDEN_OUTPUT_ROOTS = (
    "site/dist",
    "site/dist/data/public_index",
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

OUTPUT_FILES = {
    "source_cache_review_entry": "sample_ia_source_cache_review_entry.json",
    "evidence_review_entry": "sample_ia_evidence_candidate_review_entry.json",
    "candidate_promotion_dry_run": "sample_ia_candidate_promotion_dry_run.json",
    "pack_draft_preview": "sample_ia_pack_draft_preview.json",
    "summary_markdown": "sample_ia_review_integration_summary.md",
}


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live-probe-result", help="IA-BUNDLE-02 live probe result JSON.")
    parser.add_argument("--source-cache-candidate", help="IA-BUNDLE-02 source-cache candidate preview JSON.")
    parser.add_argument("--evidence-preview", help="IA-BUNDLE-02 evidence candidate preview JSON.")
    parser.add_argument("--review-seed", help="IA-BUNDLE-02 review seed preview JSON.")
    parser.add_argument("--output-dir", help="Optional directory for generated review integration outputs.")
    parser.add_argument("--check", action="store_true", help="Validate and summarize without writing files.")
    parser.add_argument("--json", action="store_true", help="Emit JSON summary.")
    args = parser.parse_args(argv)

    try:
        artifacts = run_integration(args)
        if args.output_dir and not args.check:
            write_outputs(args.output_dir, artifacts)
        summary = artifacts["summary"]
        if args.json:
            print(json.dumps(summary, indent=2, sort_keys=True), file=stdout)
        else:
            print("IA metadata review integration", file=stdout)
            print(f"status: {summary['integration_status']}", file=stdout)
            print(f"source_cache_review_entry_created: {str(summary['source_cache_review_entry_created']).lower()}", file=stdout)
            print(f"evidence_candidate_review_entry_created: {str(summary['evidence_candidate_review_entry_created']).lower()}", file=stdout)
            print(f"candidate_promotion_dry_run_created: {str(summary['candidate_promotion_dry_run_created']).lower()}", file=stdout)
            print(f"pack_draft_preview_created: {str(summary['pack_draft_preview_created']).lower()}", file=stdout)
            print(f"blocked_reason_count: {summary['blocked_reason_count']}", file=stdout)
        return 0
    except Exception as exc:  # noqa: BLE001 - CLI validation surface.
        if args.json:
            print(json.dumps({"status": "invalid", "error": str(exc)}, indent=2, sort_keys=True), file=stdout)
        else:
            print("IA metadata review integration", file=stdout)
            print("status: invalid", file=stdout)
            print(f"ERROR: {exc}", file=stdout)
        return 1


def run_integration(args: argparse.Namespace) -> dict[str, Any]:
    paths = {
        "live_probe_result": args.live_probe_result,
        "source_cache_candidate": args.source_cache_candidate,
        "evidence_preview": args.evidence_preview,
        "review_seed": args.review_seed,
    }
    outputs = load_ia_probe_outputs({key: value for key, value in paths.items() if value})
    source_candidate = outputs.get("source_cache_candidate") or _blocked_placeholder("source_cache_candidate", outputs)
    evidence_preview = outputs.get("evidence_preview") or _blocked_placeholder("evidence_candidate_preview", outputs)
    source_entry = build_ia_source_cache_review_entry(source_candidate, None)
    evidence_entry = build_ia_evidence_candidate_review_entry(evidence_preview, None)
    promotion = build_ia_candidate_promotion_dry_run(
        {
            "source_cache_review_entry": source_entry,
            "evidence_review_entry": evidence_entry,
            "live_probe_result": outputs.get("live_probe_result", {}),
        },
        None,
    )
    pack_preview = build_ia_pack_draft_preview(
        {
            "source_cache_review_entry": source_entry,
            "evidence_review_entry": evidence_entry,
            "candidate_promotion_dry_run": promotion,
        },
        None,
    )
    artifacts = {
        "source_cache_review_entry": source_entry,
        "evidence_review_entry": evidence_entry,
        "candidate_promotion_dry_run": promotion,
        "pack_draft_preview": pack_preview,
    }
    artifacts["summary"] = build_ia_review_integration_summary(artifacts, None)
    errors = []
    for key, payload in artifacts.items():
        if isinstance(payload, Mapping):
            errors.extend(f"{key}: {error}" for error in detect_ia_review_truth_boundary_violations(payload))
            errors.extend(f"{key}: {error}" for error in detect_ia_review_product_boundary_violations(payload))
    if errors:
        raise ValueError("; ".join(errors))
    return artifacts


def write_outputs(output_dir_text: str, artifacts: Mapping[str, Any]) -> None:
    output_dir = _safe_output_dir(Path(output_dir_text))
    output_dir.mkdir(parents=True, exist_ok=True)
    for key, filename in OUTPUT_FILES.items():
        path = output_dir / filename
        if key == "summary_markdown":
            path.write_text(render_summary_markdown(artifacts["summary"]), encoding="utf-8")
        else:
            path.write_text(json.dumps(artifacts[key], indent=2, sort_keys=True) + "\n", encoding="utf-8")


def render_summary_markdown(summary: Mapping[str, Any]) -> str:
    lines = [
        "# IA Review Integration Summary",
        "",
        f"- integration_status: `{summary.get('integration_status')}`",
        f"- source_cache_review_entry_created: `{str(summary.get('source_cache_review_entry_created', False)).lower()}`",
        f"- evidence_candidate_review_entry_created: `{str(summary.get('evidence_candidate_review_entry_created', False)).lower()}`",
        f"- candidate_promotion_dry_run_created: `{str(summary.get('candidate_promotion_dry_run_created', False)).lower()}`",
        f"- pack_draft_preview_created: `{str(summary.get('pack_draft_preview_created', False)).lower()}`",
        f"- blocked_reason_count: `{summary.get('blocked_reason_count', 0)}`",
        "- accepted_source_truth: `false`",
        "- accepted_evidence_truth: `false`",
        "- accepted_candidate_truth: `false`",
        "- public_index_mutated: `false`",
        "- master_index_mutated: `false`",
    ]
    if summary.get("blocked_reasons"):
        lines.extend(["", "## Blocked Reasons"])
        lines.extend(f"- {reason}" for reason in summary.get("blocked_reasons", []))
    return "\n".join(lines) + "\n"


def _blocked_placeholder(kind: str, outputs: Mapping[str, Any]) -> dict[str, Any]:
    live = outputs.get("live_probe_result", {})
    return {
        "schema_version": f"internet_archive_review_{kind}.not_created.v0",
        "status": "not_created_blocked_by_policy",
        "kind": kind,
        "identifier": live.get("identifier"),
        "live_probe_result_ref": live.get("probe_id"),
        "blocked_reasons": list(live.get("blocked_reasons") or ["IA-BUNDLE-02 output missing or blocked"]),
        "runtime_mutated": False,
        "accepted_source_truth": False,
        "accepted_evidence": False,
    }


def _safe_output_dir(path: Path) -> Path:
    resolved = (REPO_ROOT / path).resolve() if not path.is_absolute() else path.resolve()
    repo_resolved = REPO_ROOT.resolve()
    try:
        rel = resolved.relative_to(repo_resolved).as_posix()
        rel_lower = rel.casefold().rstrip("/")
        for forbidden in FORBIDDEN_OUTPUT_ROOTS:
            forbidden_lower = forbidden.casefold().rstrip("/")
            if rel_lower == forbidden_lower or rel_lower.startswith(forbidden_lower + "/"):
                raise ValueError(f"refusing forbidden output root: {forbidden}")
        if rel_lower.startswith("examples/connectors/internet_archive/review_integration"):
            return resolved
        if rel_lower.startswith("control/audits/") and rel_lower.endswith("/generated"):
            return resolved
        raise ValueError(f"refusing output outside approved IA review roots: {rel}")
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
