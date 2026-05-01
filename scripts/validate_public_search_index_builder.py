#!/usr/bin/env python3
"""Validate P55 Public Search Index Builder v0 audit and artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
AUDIT_ROOT = REPO_ROOT / "control" / "audits" / "public-search-index-builder-v0"
REPORT_PATH = AUDIT_ROOT / "public_search_index_builder_report.json"
INDEX_ROOT = REPO_ROOT / "data" / "public_index"

REQUIRED_AUDIT_FILES = {
    "README.md",
    "INDEX_BUILDER_SUMMARY.md",
    "INPUT_CORPUS_REVIEW.md",
    "INDEX_FORMAT.md",
    "GENERATED_ARTIFACTS.md",
    "SEARCH_FIELD_MODEL.md",
    "RESULT_CARD_PROJECTION.md",
    "SAFETY_AND_PRIVACY_REVIEW.md",
    "LOCAL_PUBLIC_SEARCH_INTEGRATION.md",
    "FTS_AND_FALLBACK_STATUS.md",
    "COMMAND_RESULTS.md",
    "REMAINING_BLOCKERS.md",
    "NEXT_STEPS.md",
    "public_search_index_builder_report.json",
}
REQUIRED_INDEX_FILES = {
    "build_manifest.json",
    "source_coverage.json",
    "index_stats.json",
    "search_documents.ndjson",
    "checksums.sha256",
}
HARD_FALSE_FIELDS = {
    "live_sources_used",
    "external_calls_performed",
    "private_paths_detected",
    "executable_payloads_included",
    "downloads_enabled",
    "uploads_enabled",
    "local_paths_enabled",
    "arbitrary_url_fetch_enabled",
    "master_index_mutated",
    "pack_import_performed",
    "ai_runtime_enabled",
}
REQUIRED_DOCS = {
    "docs/operations/PUBLIC_SEARCH_INDEX_BUILDER.md",
    "docs/reference/PUBLIC_SEARCH_INDEX_FORMAT.md",
}


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate P55 Public Search Index Builder v0.")
    parser.add_argument("--json", action="store_true", help="Emit JSON report.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    report = validate_public_search_index_builder()
    output = stdout or sys.stdout
    if args.json:
        output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        output.write(_format_plain(report))
    return 0 if report["status"] == "valid" else 1


def validate_public_search_index_builder() -> dict[str, Any]:
    errors: list[str] = []
    for file_name in sorted(REQUIRED_AUDIT_FILES):
        if not (AUDIT_ROOT / file_name).is_file():
            errors.append(f"{_rel(AUDIT_ROOT / file_name)}: required audit file is missing.")
    report = _load_json(REPORT_PATH, errors)
    for script in ("scripts/build_public_search_index.py", "scripts/validate_public_search_index.py"):
        if not (REPO_ROOT / script).is_file():
            errors.append(f"{script}: required script is missing.")
    for file_name in sorted(REQUIRED_INDEX_FILES):
        if not (INDEX_ROOT / file_name).is_file():
            errors.append(f"{_rel(INDEX_ROOT / file_name)}: required index artifact is missing.")
    for doc_path in sorted(REQUIRED_DOCS):
        if not (REPO_ROOT / doc_path).is_file():
            errors.append(f"{doc_path}: required documentation is missing.")

    if isinstance(report, Mapping):
        if report.get("report_id") != "public_search_index_builder_v0":
            errors.append("report: report_id must be public_search_index_builder_v0.")
        if report.get("output_root") != "data/public_index":
            errors.append("report: output_root must be data/public_index.")
        for field_name in HARD_FALSE_FIELDS:
            if report.get(field_name) is not False:
                errors.append(f"report: {field_name} must be false.")
        if report.get("local_public_search_integrated") is not True:
            errors.append("report: local_public_search_integrated must be true.")
        if report.get("hosted_wrapper_compatible") is not True:
            errors.append("report: hosted_wrapper_compatible must be true.")
        if not isinstance(report.get("command_results"), list) or not report["command_results"]:
            errors.append("report: command_results must be a non-empty list.")
        if "production ready" in json.dumps(report).casefold():
            errors.append("report: must not claim production ready.")
        if "live source enabled" in json.dumps(report).casefold():
            errors.append("report: must not claim live source enabled.")

    artifact_inventory = _load_json(
        REPO_ROOT / "control" / "inventory" / "generated_artifacts" / "generated_artifacts.json",
        errors,
    )
    if isinstance(artifact_inventory, Mapping):
        ids = {
            group.get("artifact_id")
            for group in artifact_inventory.get("artifact_groups", [])
            if isinstance(group, Mapping)
        }
        if "public_search_index" not in ids:
            errors.append("generated_artifacts.json: public_search_index artifact entry is missing.")

    for command in (
        [sys.executable, "scripts/validate_public_search_index.py"],
        [sys.executable, "scripts/build_public_search_index.py", "--check"],
    ):
        completed = subprocess.run(command, cwd=REPO_ROOT, capture_output=True, text=True, check=False)
        if completed.returncode != 0:
            errors.append(f"{' '.join(command)} failed: {completed.stdout[:300]} {completed.stderr[:300]}")

    return {
        "status": "valid" if not errors else "invalid",
        "created_by": "public_search_index_builder_validator_v0",
        "report_id": report.get("report_id") if isinstance(report, Mapping) else None,
        "document_count": report.get("document_count") if isinstance(report, Mapping) else None,
        "output_root": "data/public_index",
        "errors": errors,
    }


def _load_json(path: Path, errors: list[str]) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"{_rel(path)}: file is missing.")
    except json.JSONDecodeError as exc:
        errors.append(f"{_rel(path)}: invalid JSON: {exc}.")
    return None


def _format_plain(report: Mapping[str, Any]) -> str:
    lines = [
        "Public Search Index Builder validation",
        f"status: {report['status']}",
        f"report_id: {report.get('report_id')}",
        f"document_count: {report.get('document_count')}",
    ]
    if report.get("errors"):
        lines.append("Errors")
        lines.extend(f"- {error}" for error in report["errors"])
    return "\n".join(lines) + "\n"


def _rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


if __name__ == "__main__":
    raise SystemExit(main())
