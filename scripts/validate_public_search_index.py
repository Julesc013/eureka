#!/usr/bin/env python3
"""Validate committed Public Search Index v0 artifacts."""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INDEX_ROOT = REPO_ROOT / "data" / "public_index"
SOURCE_ROOT = REPO_ROOT / "control" / "inventory" / "sources"
REQUIRED_FILES = (
    "build_manifest.json",
    "source_coverage.json",
    "index_stats.json",
    "search_documents.ndjson",
)
REQUIRED_DOCUMENT_FIELDS = {
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
REQUIRED_BLOCKED_ACTIONS = {"download", "upload", "install_handoff", "execute"}
CREATED_BY = "public_search_index_validator_v0"


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate Public Search Index v0 artifacts without network access.")
    parser.add_argument("--index-root", default=str(DEFAULT_INDEX_ROOT), help="Public index artifact root.")
    parser.add_argument("--json", action="store_true", help="Emit JSON report.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    index_root = Path(args.index_root)
    if not index_root.is_absolute():
        index_root = REPO_ROOT / index_root
    report = validate_public_search_index(index_root)
    output = stdout or sys.stdout
    if args.json:
        output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        output.write(_format_plain(report))
    return 0 if report["status"] == "valid" else 1


def validate_public_search_index(index_root: Path = DEFAULT_INDEX_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    for file_name in REQUIRED_FILES:
        if not (index_root / file_name).is_file():
            errors.append(f"{_rel(index_root / file_name)}: required artifact is missing.")

    manifest = _load_json(index_root / "build_manifest.json", errors)
    source_coverage = _load_json(index_root / "source_coverage.json", errors)
    stats = _load_json(index_root / "index_stats.json", errors)
    documents = _load_ndjson(index_root / "search_documents.ndjson", errors)
    known_source_ids = _known_source_ids(errors)

    _validate_manifest(manifest, errors)
    _validate_source_coverage(source_coverage, known_source_ids, errors)
    _validate_documents(documents, known_source_ids, errors)
    _validate_stats(stats, documents, errors)
    _validate_checksums(index_root, errors)

    private_paths_detected = any(_looks_private(json.dumps(doc, sort_keys=True)) for doc in documents)
    return {
        "status": "valid" if not errors else "invalid",
        "created_by": CREATED_BY,
        "index_root": _rel(index_root),
        "document_count": len(documents),
        "source_count": len(known_source_ids),
        "record_kind_counts": dict(sorted(Counter(str(doc.get("record_kind")) for doc in documents).items())),
        "private_paths_detected": private_paths_detected,
        "live_sources_used": False,
        "external_calls_performed": False,
        "errors": errors,
    }


def _validate_manifest(payload: Any, errors: list[str]) -> None:
    if not isinstance(payload, Mapping):
        errors.append("build_manifest.json: must be an object.")
        return
    expected_false = (
        "live_sources_used",
        "external_calls_performed",
        "private_paths_detected",
        "executable_payloads_included",
        "fts5_enabled",
    )
    for field_name in expected_false:
        if payload.get(field_name) is not False:
            errors.append(f"build_manifest.json: {field_name} must be false.")
    if payload.get("fallback_enabled") is not True:
        errors.append("build_manifest.json: fallback_enabled must be true.")
    if payload.get("artifact_root") != "data/public_index":
        errors.append("build_manifest.json: artifact_root must be data/public_index.")


def _validate_source_coverage(payload: Any, known_source_ids: set[str], errors: list[str]) -> None:
    if not isinstance(payload, Mapping):
        errors.append("source_coverage.json: must be an object.")
        return
    sources = payload.get("sources")
    if not isinstance(sources, list):
        errors.append("source_coverage.json: sources must be a list.")
        return
    observed = {
        str(source.get("source_id"))
        for source in sources
        if isinstance(source, Mapping) and source.get("source_id")
    }
    missing = sorted(known_source_ids - observed)
    if missing:
        errors.append(f"source_coverage.json: missing known source ids {missing}.")
    for source in sources:
        if not isinstance(source, Mapping):
            errors.append("source_coverage.json: sources entries must be objects.")
            continue
        if source.get("live_enabled") is not False:
            errors.append(f"source_coverage.json: {source.get('source_id')}: live_enabled must be false.")


def _validate_documents(
    documents: Sequence[Mapping[str, Any]],
    known_source_ids: set[str],
    errors: list[str],
) -> None:
    seen: set[str] = set()
    for index, document in enumerate(documents):
        doc_id = str(document.get("doc_id") or f"<document-{index}>")
        missing = sorted(REQUIRED_DOCUMENT_FIELDS - set(document))
        if missing:
            errors.append(f"{doc_id}: missing required fields {missing}.")
        if doc_id in seen:
            errors.append(f"{doc_id}: duplicate doc_id.")
        seen.add(doc_id)
        source_id = str(document.get("source_id") or "")
        if source_id not in known_source_ids and source_id != "unknown-source":
            errors.append(f"{doc_id}: unknown source_id {source_id!r}.")
        blocked = set(_string_list(document.get("blocked_actions")))
        if not REQUIRED_BLOCKED_ACTIONS.issubset(blocked):
            errors.append(f"{doc_id}: blocked_actions must include {sorted(REQUIRED_BLOCKED_ACTIONS)}.")
        allowed = set(_string_list(document.get("allowed_actions")))
        if allowed & {"download", "upload", "install", "execute", "install_handoff"}:
            errors.append(f"{doc_id}: unsafe action appears in allowed_actions.")
        if document.get("live_source_used") is not False:
            errors.append(f"{doc_id}: live_source_used must be false.")
        if document.get("external_call_performed") is not False:
            errors.append(f"{doc_id}: external_call_performed must be false.")
        text = json.dumps(document, sort_keys=True)
        if _looks_private(text):
            errors.append(f"{doc_id}: private or absolute path marker detected.")
        if _looks_secret_like(text):
            errors.append(f"{doc_id}: secret-like marker detected.")


def _validate_stats(payload: Any, documents: Sequence[Mapping[str, Any]], errors: list[str]) -> None:
    if not isinstance(payload, Mapping):
        errors.append("index_stats.json: must be an object.")
        return
    if payload.get("document_count") != len(documents):
        errors.append("index_stats.json: document_count does not match search_documents.ndjson.")
    expected_kind_counts = dict(sorted(Counter(str(doc.get("record_kind")) for doc in documents).items()))
    if payload.get("record_kind_counts") != expected_kind_counts:
        errors.append("index_stats.json: record_kind_counts do not match documents.")
    for field_name in (
        "private_paths_detected",
        "executable_payloads_included",
        "live_sources_used",
        "external_calls_performed",
        "fts5_enabled",
    ):
        if payload.get(field_name) is not False:
            errors.append(f"index_stats.json: {field_name} must be false.")
    if payload.get("fallback_enabled") is not True:
        errors.append("index_stats.json: fallback_enabled must be true.")


def _validate_checksums(index_root: Path, errors: list[str]) -> None:
    path = index_root / "checksums.sha256"
    if not path.exists():
        return
    expected: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        parts = line.split()
        if len(parts) != 2:
            errors.append("checksums.sha256: each line must contain a sha256 and file name.")
            continue
        expected[parts[1]] = parts[0]
    for file_name in REQUIRED_FILES:
        actual_path = index_root / file_name
        if not actual_path.is_file():
            continue
        digest = hashlib.sha256(actual_path.read_bytes()).hexdigest()
        if expected.get(file_name) != digest:
            errors.append(f"checksums.sha256: checksum mismatch for {file_name}.")


def _known_source_ids(errors: list[str]) -> set[str]:
    source_ids: set[str] = set()
    for path in sorted(SOURCE_ROOT.glob("*.source.json")):
        payload = _load_json(path, errors)
        if isinstance(payload, Mapping) and isinstance(payload.get("source_id"), str):
            source_ids.add(payload["source_id"])
    if not source_ids:
        errors.append("control/inventory/sources: no source ids found.")
    return source_ids


def _load_json(path: Path, errors: list[str]) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"{_rel(path)}: file is missing.")
    except json.JSONDecodeError as exc:
        errors.append(f"{_rel(path)}: invalid JSON: {exc}.")
    return None


def _load_ndjson(path: Path, errors: list[str]) -> list[Mapping[str, Any]]:
    documents: list[Mapping[str, Any]] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        errors.append(f"{_rel(path)}: file is missing.")
        return documents
    for line_number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(f"{_rel(path)}:{line_number}: invalid JSON: {exc}.")
            continue
        if not isinstance(payload, Mapping):
            errors.append(f"{_rel(path)}:{line_number}: document must be an object.")
            continue
        documents.append(payload)
    return documents


def _string_list(value: Any) -> list[str]:
    return [str(item) for item in value] if isinstance(value, list) else []


def _looks_private(value: str) -> bool:
    folded = value.replace("\\", "/").casefold()
    return bool(
        re.search(r"\b[a-z]:/", folded)
        or "/users/" in folded
        or "/home/" in folded
        or "/tmp/" in folded
        or "appdata/" in folded
        or ".eureka-local" in folded
        or ".eureka-cache" in folded
        or ".eureka-staging" in folded
    )


def _looks_secret_like(value: str) -> bool:
    folded = value.casefold()
    return any(token in folded for token in ("auth_token", "api_key", "password", "source_credentials"))


def _format_plain(report: Mapping[str, Any]) -> str:
    lines = [
        "Public Search Index validation",
        f"status: {report['status']}",
        f"index_root: {report['index_root']}",
        f"document_count: {report['document_count']}",
        f"private_paths_detected: {report['private_paths_detected']}",
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
