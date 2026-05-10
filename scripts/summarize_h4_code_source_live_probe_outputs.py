#!/usr/bin/env python3
"""Summarize H4 code/source live-probe result files without network access."""

from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import sys
import tempfile
from typing import Any, Mapping, Sequence, TextIO

REPO_ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN_OUTPUT_ROOTS = (
    "site/dist",
    "data/public_index",
    "runtime",
    "contracts",
    "data/master_index",
    "master_index",
    "repository_clones",
    "repository_clone",
    "repository_mirror",
    "package_cache",
    ".aide.local",
    ".local/eureka",
    ".cache/eureka",
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", action="append", required=True)
    parser.add_argument("--output")
    parser.add_argument("--summary-output")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        results = load_results(args.input)
        summary = build_summary(results)
        if not args.check:
            if args.output:
                _write_json(args.output, summary)
            if args.summary_output:
                _write_text(args.summary_output, render_summary(summary))
        if args.json:
            print(json.dumps(summary, indent=2, sort_keys=True), file=stdout)
        else:
            print("H4 code/source live probe output summary", file=stdout)
            print(f"status: {summary['status']}", file=stdout)
            print(f"result_count: {summary['result_count']}", file=stdout)
            print(f"completed_count: {summary['completed_count']}", file=stdout)
            print(f"blocked_count: {summary['blocked_count']}", file=stdout)
            print(f"request_count_total: {summary['request_count_total']}", file=stdout)
            print(f"network_used: {str(summary['network_used']).lower()}", file=stdout)
        return 0
    except Exception as exc:  # noqa: BLE001
        if args.json:
            print(json.dumps({"status": "invalid", "error": str(exc)}, indent=2, sort_keys=True), file=stdout)
        else:
            print("H4 code/source live probe output summary", file=stdout)
            print("status: invalid", file=stdout)
            print(f"ERROR: {exc}", file=stdout)
        return 1


def load_results(inputs: Sequence[str]) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for item in inputs:
        path = _repo_path(item)
        paths = sorted(path.glob("*.json")) if path.is_dir() else [path]
        for json_path in paths:
            payload = json.loads(json_path.read_text(encoding="utf-8"))
            if isinstance(payload, dict) and payload.get("schema_version") == "h4_code_source_live_probe_result.v0":
                results.append(payload)
    return results


def build_summary(results: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    statuses = Counter(str(item.get("result_status", "unknown")) for item in results)
    blocked = [str(item.get("source_id")) for item in results if str(item.get("result_status", "")).startswith("blocked")]
    completed = [str(item.get("source_id")) for item in results if item.get("result_status") == "live_probe_completed"]
    attempted = [str(item.get("source_id")) for item in results if item.get("network_used") is True]
    reasons = Counter(reason for item in results for reason in (item.get("blocked_reasons") or ([] if not item.get("blocked_reason") else [item.get("blocked_reason")])))
    return {
        "schema_version": "h4_code_source_live_probe_output_summary.v0",
        "status": "pass",
        "result_count": len(results),
        "status_counts": dict(sorted(statuses.items())),
        "attempted_sources": attempted,
        "completed_sources": completed,
        "blocked_sources": blocked,
        "completed_count": len(completed),
        "blocked_count": len(blocked),
        "request_count_total": sum(int(item.get("request_count") or 0) for item in results),
        "network_used": any(item.get("network_used") is True for item in results),
        "repository_clone_used": False,
        "source_archive_download_used": False,
        "release_asset_download_used": False,
        "git_command_invoked": False,
        "build_tool_invoked": False,
        "source_identity_candidate_count": sum(1 for item in results if isinstance(item.get("source_identity_candidate"), Mapping) and item.get("source_identity_candidate", {}).get("status") != "not_created_blocked_by_policy"),
        "release_identity_candidate_count": sum(1 for item in results if isinstance(item.get("release_identity_candidate"), Mapping) and item.get("release_identity_candidate", {}).get("status") != "not_created_blocked_by_policy"),
        "relation_candidate_count": sum(len(item.get("source_to_binary_relation_candidate_preview", []) or []) for item in results),
        "release_asset_candidate_count": sum(len(item.get("release_asset_candidate_preview", []) or []) for item in results),
        "blocked_reason_counts": dict(sorted(reasons.items())),
        "truth_boundary": {"public_index_mutated": False, "master_index_mutated": False, "accepted_public_truth": False},
        "product_boundary": {"enabled_source_sync": False, "enabled_repository_clone": False, "enabled_downloads": False, "mutated_public_index": False, "mutated_master_index": False},
    }


def render_summary(summary: Mapping[str, Any]) -> str:
    lines = [
        "# H4 Code/Source Live Probe Output Summary",
        "",
        f"- result_count: `{summary.get('result_count')}`",
        f"- completed_count: `{summary.get('completed_count')}`",
        f"- blocked_count: `{summary.get('blocked_count')}`",
        f"- request_count_total: `{summary.get('request_count_total')}`",
        f"- network_used: `{str(summary.get('network_used')).lower()}`",
        f"- repository_clone_used: `{str(summary.get('repository_clone_used')).lower()}`",
        f"- source_archive_download_used: `{str(summary.get('source_archive_download_used')).lower()}`",
        f"- release_asset_download_used: `{str(summary.get('release_asset_download_used')).lower()}`",
        f"- source_identity_candidate_count: `{summary.get('source_identity_candidate_count')}`",
        f"- release_identity_candidate_count: `{summary.get('release_identity_candidate_count')}`",
        f"- relation_candidate_count: `{summary.get('relation_candidate_count')}`",
        f"- release_asset_candidate_count: `{summary.get('release_asset_candidate_count')}`",
        "",
        "## Blocked Sources",
    ]
    lines.extend(f"- {source_id}" for source_id in summary.get("blocked_sources", []))
    return "\n".join(lines) + "\n"


def _repo_path(path_text: str | Path) -> Path:
    path = Path(path_text)
    return path if path.is_absolute() else REPO_ROOT / path


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
    try:
        rel = resolved.relative_to(REPO_ROOT.resolve()).as_posix()
        rel_lower = rel.casefold()
        for forbidden in FORBIDDEN_OUTPUT_ROOTS:
            forbidden_lower = forbidden.casefold().rstrip("/")
            if rel_lower == forbidden_lower or rel_lower.startswith(forbidden_lower + "/"):
                raise ValueError(f"refusing forbidden output root: {forbidden}")
        if rel_lower.startswith("control/audits/") and "/generated/" in rel_lower:
            return resolved
        if rel_lower.startswith("examples/connectors/h4_code_source_release/live_probe_outputs/"):
            return resolved
        raise ValueError(f"refusing output outside approved H4 live-probe roots: {rel}")
    except ValueError as exc:
        if str(exc).startswith("refusing"):
            raise
        temp_root = Path(tempfile.gettempdir()).resolve()
        try:
            resolved.relative_to(temp_root)
            return resolved
        except ValueError as temp_exc:
            raise ValueError(f"refusing output outside approved roots or temp directory: {resolved}") from temp_exc


if __name__ == "__main__":
    raise SystemExit(main())
