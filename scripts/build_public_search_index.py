#!/usr/bin/env python3
"""Build Eureka Public Search Index v0 from controlled repo fixtures."""

from __future__ import annotations

import argparse
from collections import Counter
import filecmp
import hashlib
import json
from pathlib import Path
import re
import shutil
import sqlite3
import sys
import tempfile
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.engine.index import build_index_records  # noqa: E402
from runtime.gateway.public_api.demo_support import _build_demo_normalized_catalog  # noqa: E402
from runtime.gateway.public_api.public_search_index import (  # noqa: E402
    PUBLIC_INDEX_ID,
    PUBLIC_INDEX_SCHEMA_VERSION,
    public_document_from_index_record,
)
from runtime.source_registry import load_source_registry  # noqa: E402


DEFAULT_OUTPUT_ROOT = REPO_ROOT / "data" / "public_index"
REQUIRED_FILES = (
    "build_manifest.json",
    "source_coverage.json",
    "index_stats.json",
    "search_documents.ndjson",
    "checksums.sha256",
)
CREATED_BY = "public_search_index_builder_v0"
INPUT_CORPUS = (
    "control/inventory/sources/*.source.json",
    "runtime/connectors/synthetic_software/fixtures/*",
    "runtime/connectors/github_releases/fixtures/*",
    "runtime/connectors/internet_archive_recorded/fixtures/*",
    "runtime/connectors/local_bundle_fixtures/fixtures/*",
    "runtime/connectors/article_scan_recorded/fixtures/*",
    "runtime/connectors/source_expansion_recorded/fixtures/*",
)


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build or check the public-safe search index artifact.")
    parser.add_argument("--output-root", default=str(DEFAULT_OUTPUT_ROOT), help="Output root for generated index artifacts.")
    parser.add_argument("--check", action="store_true", help="Regenerate in a temp dir and compare with output-root.")
    parser.add_argument("--rebuild", action="store_true", help="Regenerate committed artifacts in output-root.")
    parser.add_argument("--json", action="store_true", help="Emit JSON report.")
    parser.add_argument("--json-only", "--no-sqlite", action="store_true", help="Accepted compatibility flag; committed artifacts are JSON/NDJSON only.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    output = stdout or sys.stdout
    output_root = Path(args.output_root)
    if not output_root.is_absolute():
        output_root = REPO_ROOT / output_root

    if args.check:
        report = check_public_search_index(output_root)
    elif args.rebuild:
        report = build_public_search_index(output_root)
    else:
        with tempfile.TemporaryDirectory(prefix="eureka-public-index-") as temp_dir:
            report = build_public_search_index(Path(temp_dir))
            report["status"] = "valid" if report["status"] == "built" else report["status"]
            report["mode"] = "preview_no_repo_mutation"

    if args.json:
        output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        output.write(_format_plain(report))
    return 0 if report["status"] in {"built", "valid"} else 1


def build_public_search_index(output_root: Path = DEFAULT_OUTPUT_ROOT) -> dict[str, Any]:
    sqlite_available, fts5_available = _sqlite_status()
    source_registry = load_source_registry()
    catalog = _build_demo_normalized_catalog()
    index_records = build_index_records(catalog, source_registry)
    documents = [
        public_document_from_index_record(record, source_registry)
        for record in sorted(index_records, key=lambda item: item.index_record_id)
    ]
    errors = _validate_generated_documents(documents)
    if errors:
        return {
            "status": "invalid",
            "created_by": CREATED_BY,
            "errors": errors,
        }

    output_root.mkdir(parents=True, exist_ok=True)
    _write_ndjson(output_root / "search_documents.ndjson", documents)
    source_coverage = _source_coverage_payload(source_registry, documents)
    index_stats = _index_stats_payload(documents, sqlite_available, fts5_available)
    build_manifest = _build_manifest_payload(documents, source_coverage, sqlite_available, fts5_available)
    _write_json(output_root / "source_coverage.json", source_coverage)
    _write_json(output_root / "index_stats.json", index_stats)
    _write_json(output_root / "build_manifest.json", build_manifest)
    _write_checksums(output_root)

    return {
        "status": "built",
        "created_by": CREATED_BY,
        "output_root": _rel(output_root),
        "document_count": len(documents),
        "source_family_counts": dict(sorted(Counter(doc["source_family"] for doc in documents).items())),
        "record_kind_counts": dict(sorted(Counter(doc["record_kind"] for doc in documents).items())),
        "sqlite_available": sqlite_available,
        "fts5_available": fts5_available,
        "fts5_enabled": False,
        "fallback_enabled": True,
        "generated_files": list(REQUIRED_FILES),
        "errors": [],
    }


def check_public_search_index(output_root: Path = DEFAULT_OUTPUT_ROOT) -> dict[str, Any]:
    if not output_root.exists():
        return {
            "status": "invalid",
            "created_by": CREATED_BY,
            "output_root": _rel(output_root),
            "errors": [f"{_rel(output_root)}: public index output root is missing."],
        }
    with tempfile.TemporaryDirectory(prefix="eureka-public-index-check-") as temp_dir:
        temp_root = Path(temp_dir)
        build_report = build_public_search_index(temp_root)
        errors: list[str] = []
        for file_name in REQUIRED_FILES:
            expected = output_root / file_name
            observed = temp_root / file_name
            if not expected.is_file():
                errors.append(f"{_rel(expected)}: required generated artifact is missing.")
                continue
            if not filecmp.cmp(expected, observed, shallow=False):
                errors.append(f"{_rel(expected)}: generated artifact drift detected.")
        return {
            "status": "valid" if not errors and build_report["status"] == "built" else "invalid",
            "created_by": CREATED_BY,
            "output_root": _rel(output_root),
            "document_count": build_report.get("document_count", 0),
            "generated_files": list(REQUIRED_FILES),
            "sqlite_available": build_report.get("sqlite_available"),
            "fts5_available": build_report.get("fts5_available"),
            "fts5_enabled": False,
            "fallback_enabled": True,
            "errors": errors + list(build_report.get("errors", [])),
        }


def _build_manifest_payload(
    documents: Sequence[Mapping[str, Any]],
    source_coverage: Mapping[str, Any],
    sqlite_available: bool,
    fts5_available: bool,
) -> dict[str, Any]:
    return {
        "schema_version": PUBLIC_INDEX_SCHEMA_VERSION,
        "index_id": PUBLIC_INDEX_ID,
        "created_by": CREATED_BY,
        "artifact_root": "data/public_index",
        "document_count": len(documents),
        "source_count": len(source_coverage["sources"]),
        "input_corpus": list(INPUT_CORPUS),
        "generated_files": list(REQUIRED_FILES),
        "sqlite_available": sqlite_available,
        "fts5_available": fts5_available,
        "fts5_enabled": False,
        "fallback_enabled": True,
        "local_index_only": True,
        "live_sources_used": False,
        "external_calls_performed": False,
        "private_paths_detected": False,
        "executable_payloads_included": False,
        "notes": [
            "Committed public search index artifacts are JSON/NDJSON text files only.",
            "No live source calls, private local paths, executables, downloads, uploads, or model calls are included.",
        ],
    }


def _source_coverage_payload(source_registry: Any, documents: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    by_source = Counter(str(doc["source_id"]) for doc in documents)
    sources = []
    for source in sorted(source_registry.records, key=lambda item: item.source_id):
        sources.append(
            {
                "source_id": source.source_id,
                "source_family": source.source_family,
                "source_status": source.status,
                "coverage_depth": source.coverage.coverage_depth,
                "connector_mode": source.coverage.connector_mode,
                "document_count": by_source.get(source.source_id, 0),
                "fixture_backed": source.capabilities.fixture_backed,
                "recorded_fixture_backed": source.capabilities.recorded_fixture_backed,
                "live_supported": source.capabilities.live_supported,
                "live_enabled": False,
                "network_required": source.capabilities.network_required,
                "public_safe": not source.capabilities.local_private,
                "limitations": list(source.coverage.current_limitations),
            }
        )
    return {
        "schema_version": PUBLIC_INDEX_SCHEMA_VERSION,
        "index_id": PUBLIC_INDEX_ID,
        "created_by": CREATED_BY,
        "sources": sources,
        "source_family_counts": dict(sorted(Counter(str(doc["source_family"]) for doc in documents).items())),
        "live_sources_used": False,
        "external_calls_performed": False,
    }


def _index_stats_payload(
    documents: Sequence[Mapping[str, Any]],
    sqlite_available: bool,
    fts5_available: bool,
) -> dict[str, Any]:
    return {
        "schema_version": PUBLIC_INDEX_SCHEMA_VERSION,
        "index_id": PUBLIC_INDEX_ID,
        "created_by": CREATED_BY,
        "document_count": len(documents),
        "record_kind_counts": dict(sorted(Counter(str(doc["record_kind"]) for doc in documents).items())),
        "source_family_counts": dict(sorted(Counter(str(doc["source_family"]) for doc in documents).items())),
        "result_lane_counts": dict(sorted(Counter(str(doc["result_lane"]) for doc in documents).items())),
        "sqlite_available": sqlite_available,
        "fts5_available": fts5_available,
        "fts5_enabled": False,
        "fallback_enabled": True,
        "private_paths_detected": False,
        "executable_payloads_included": False,
        "live_sources_used": False,
        "external_calls_performed": False,
    }


def _validate_generated_documents(documents: Sequence[Mapping[str, Any]]) -> list[str]:
    errors: list[str] = []
    seen: set[str] = set()
    required = {
        "doc_id",
        "record_id",
        "record_kind",
        "title",
        "description",
        "source_id",
        "source_family",
        "source_status",
        "source_coverage_depth",
        "object_family",
        "representation_kind",
        "platform_terms",
        "architecture_terms",
        "version_terms",
        "date_terms",
        "keyword_terms",
        "compatibility_summary",
        "evidence_summary",
        "result_lane",
        "user_cost_summary",
        "allowed_actions",
        "blocked_actions",
        "warnings",
        "limitations",
        "public_target_ref",
        "search_text",
    }
    for index, doc in enumerate(documents):
        missing = sorted(required - set(doc))
        if missing:
            errors.append(f"document {index}: missing required fields {missing}.")
        doc_id = str(doc.get("doc_id", ""))
        if doc_id in seen:
            errors.append(f"{doc_id}: duplicate doc_id.")
        seen.add(doc_id)
        text = json.dumps(doc, sort_keys=True)
        if _looks_private(text):
            errors.append(f"{doc_id}: private path marker detected.")
        if any(token in text.casefold() for token in ("auth_token", "api_key", "password", "source_credentials")):
            errors.append(f"{doc_id}: secret-like marker detected.")
    return errors


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def _write_ndjson(path: Path, documents: Sequence[Mapping[str, Any]]) -> None:
    text = "".join(json.dumps(doc, sort_keys=True, separators=(",", ":")) + "\n" for doc in documents)
    path.write_text(text, encoding="utf-8", newline="\n")


def _write_checksums(output_root: Path) -> None:
    lines = []
    for file_name in REQUIRED_FILES:
        if file_name == "checksums.sha256":
            continue
        digest = hashlib.sha256((output_root / file_name).read_bytes()).hexdigest()
        lines.append(f"{digest}  {file_name}")
    (output_root / "checksums.sha256").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def _sqlite_status() -> tuple[bool, bool]:
    try:
        connection = sqlite3.connect(":memory:")
    except sqlite3.Error:
        return False, False
    try:
        try:
            connection.execute("CREATE VIRTUAL TABLE fts5_probe USING fts5(content)")
            return True, True
        except sqlite3.OperationalError:
            return True, False
    finally:
        connection.close()


def _looks_private(value: str) -> bool:
    folded = value.replace("\\", "/").casefold()
    return (
        bool(re.search(r"\b[a-z]:/", folded))
        or "/users/" in folded
        or "/home/" in folded
        or "/tmp/" in folded
        or "appdata/" in folded
        or ".eureka-local" in folded
        or ".eureka-cache" in folded
        or ".eureka-staging" in folded
    )


def _format_plain(report: Mapping[str, Any]) -> str:
    lines = [
        "Public Search Index Builder v0",
        f"status: {report['status']}",
        f"output_root: {report.get('output_root', 'preview')}",
        f"document_count: {report.get('document_count', 0)}",
        f"fts5_available: {report.get('fts5_available')}",
        "fts5_enabled: False",
        "fallback_enabled: True",
    ]
    if report.get("errors"):
        lines.append("errors:")
        lines.extend(f"- {error}" for error in report["errors"])
    return "\n".join(lines) + "\n"


def _rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


if __name__ == "__main__":
    raise SystemExit(main())
