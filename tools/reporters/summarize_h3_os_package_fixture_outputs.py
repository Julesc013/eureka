#!/usr/bin/env python3
"""Summarize H3 OS package fixture outputs offline."""

from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import sys
import tempfile
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]
FORBIDDEN_OUTPUT_ROOTS = (
    "site/dist",
    "site/dist/data/public_index",
    "runtime",
    "contracts",
    "data/master_index",
    "master_index",
    "package_cache",
    "data/package_cache",
    ".aide.local",
    ".local/eureka",
    ".cache/eureka",
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", action="append", default=[], help="H3 output file or directory; repeatable.")
    parser.add_argument("--output", help="Optional JSON summary output path.")
    parser.add_argument("--summary-output", help="Optional Markdown summary output path.")
    parser.add_argument("--check", action="store_true", help="Summarize without writing files.")
    parser.add_argument("--json", action="store_true", help="Print JSON summary.")
    args = parser.parse_args(argv)
    try:
        inputs = args.input or ["examples/connectors/h3_os_package_archives"]
        summary = build_summary(inputs)
        if not args.check:
            if args.output:
                _write_json(args.output, summary)
            if args.summary_output:
                _write_text(args.summary_output, render_summary_markdown(summary))
        if args.json:
            print(json.dumps(summary, indent=2, sort_keys=True), file=stdout)
        else:
            print("H3 OS package fixture output summary", file=stdout)
            print(f"status: {summary['status']}", file=stdout)
            print(f"source_count: {summary['source_count']}", file=stdout)
            print(f"normalized_record_count: {summary['normalized_record_count']}", file=stdout)
            print(f"identity_candidate_count: {summary['identity_candidate_count']}", file=stdout)
            print(f"compatibility_candidate_count: {summary['compatibility_candidate_count']}", file=stdout)
            print(f"dependency_candidate_count: {summary['dependency_candidate_count']}", file=stdout)
            print(f"file_candidate_count: {summary['file_candidate_count']}", file=stdout)
        return 0
    except Exception as exc:  # noqa: BLE001
        if args.json:
            print(json.dumps({"status": "invalid", "error": str(exc)}, indent=2, sort_keys=True), file=stdout)
        else:
            print("H3 OS package fixture output summary", file=stdout)
            print("status: invalid", file=stdout)
            print(f"ERROR: {exc}", file=stdout)
        return 1


def build_summary(inputs: Sequence[str]) -> dict[str, Any]:
    records = [_load_json(path) for path in _input_files(inputs)]
    normalized = [item for item in records if item.get("schema_version") == "h3_os_package_normalized_record.v0"]
    replay = [item for item in records if item.get("schema_version") == "h3_os_package_fixture_replay_result.v0"]
    identity_docs = [item for item in records if item.get("schema_version") == "h3_os_package_identity_candidate.v0"]
    compatibility_docs = [item for item in records if item.get("schema_version") == "h3_os_platform_compatibility_candidate.v0"]
    source_ids = sorted({str(item.get("source_id")) for item in normalized if item.get("source_id")})
    dependency_count = sum(len(item.get("dependency_candidate_preview", []) or []) for item in normalized)
    file_count = sum(len(item.get("file_candidate_preview", []) or []) for item in normalized)
    distribution_counts = Counter(str(item.get("distribution", "unknown")) for item in normalized)
    return {
        "schema_version": "h3_os_package_fixture_output_summary.v0",
        "status": "pass",
        "source_count": len(source_ids),
        "source_ids": source_ids,
        "distribution_counts": dict(sorted(distribution_counts.items())),
        "normalized_record_count": len(normalized),
        "replay_result_count": len(replay),
        "identity_candidate_count": len(identity_docs) + sum(1 for item in normalized if item.get("os_package_identity_candidate")),
        "compatibility_candidate_count": len(compatibility_docs) + sum(1 for item in normalized if item.get("os_platform_compatibility_candidate")),
        "dependency_candidate_count": dependency_count,
        "file_candidate_count": file_count,
        "blockers": [],
        "warnings": ["Fixture outputs are candidate previews and require review before downstream use."],
        "network_calls_made": False,
        "repository_index_fetches_made": False,
        "package_downloads_made": False,
        "package_manager_invocations_made": False,
        "truth_boundary": {
            "normalized_record_is_public_truth": False,
            "os_package_identity_candidate_is_truth": False,
            "os_compatibility_candidate_is_truth": False,
            "dependency_candidate_is_correctness_proof": False,
            "file_hash_candidate_is_malware_safety": False,
            "source_cache_preview_is_accepted_source": False,
            "evidence_preview_is_accepted_evidence": False,
            "public_index_mutated": False,
            "master_index_mutated": False,
        },
        "product_boundary": {
            "changed_public_search_behavior": False,
            "enabled_live_probes": False,
            "enabled_source_sync": False,
            "enabled_downloads": False,
            "enabled_execution": False,
            "mutated_public_index": False,
            "mutated_master_index": False,
        },
    }


def render_summary_markdown(summary: Mapping[str, Any]) -> str:
    lines = [
        "# H3 OS Package Fixture Output Summary",
        "",
        f"- status: `{summary.get('status')}`",
        f"- source_count: `{summary.get('source_count')}`",
        f"- normalized_record_count: `{summary.get('normalized_record_count')}`",
        f"- replay_result_count: `{summary.get('replay_result_count')}`",
        f"- identity_candidate_count: `{summary.get('identity_candidate_count')}`",
        f"- compatibility_candidate_count: `{summary.get('compatibility_candidate_count')}`",
        f"- dependency_candidate_count: `{summary.get('dependency_candidate_count')}`",
        f"- file_candidate_count: `{summary.get('file_candidate_count')}`",
        "",
        "## Sources",
    ]
    lines.extend(f"- {item}" for item in summary.get("source_ids", []))
    lines.extend(["", "## Warnings"])
    lines.extend(f"- {item}" for item in summary.get("warnings", []))
    return "\n".join(lines) + "\n"


def _input_files(inputs: Sequence[str]) -> list[Path]:
    files: list[Path] = []
    for item in inputs:
        path = _repo_path(item)
        if path.is_dir():
            files.extend(sorted(path.rglob("*.json")))
        elif path.is_file():
            files.append(path)
        else:
            raise ValueError(f"missing input: {item}")
    return files


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


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
    repo_root = REPO_ROOT.resolve()
    try:
        rel = resolved.relative_to(repo_root).as_posix()
        rel_lower = rel.casefold()
        for forbidden in FORBIDDEN_OUTPUT_ROOTS:
            forbidden_lower = forbidden.casefold().rstrip("/")
            if rel_lower == forbidden_lower or rel_lower.startswith(forbidden_lower + "/"):
                raise ValueError(f"refusing forbidden output root: {forbidden}")
        if rel_lower.startswith("control/audits/") and "/generated/" in rel_lower:
            return resolved
        if rel_lower.startswith("examples/connectors/h3_os_package_archives/"):
            return resolved
        raise ValueError(f"refusing output outside approved H3 fixture roots: {rel}")
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
