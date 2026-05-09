"""Tier 2 manifest-candidate extraction for fixture archives."""

from __future__ import annotations

import json
from pathlib import Path
import tarfile
import zipfile
from typing import Any, Mapping

from runtime.extraction.container_detect import detect_container_type
from runtime.extraction.guards import (
    check_path_safety,
    manifest_kind,
    manifest_like,
    product_boundary,
    stable_id,
    truth_boundary,
)


def extract_tier2_manifest_candidates(path: str | Path, policy: Mapping[str, Any] | None = None) -> list[dict[str, Any]]:
    fixture = Path(path)
    container_type = detect_container_type(fixture, policy)
    max_bytes = int((policy or {}).get("resource_limits", {}).get("max_manifest_bytes", 16384))
    if container_type == "zip":
        return _zip_manifest_candidates(fixture, max_bytes, policy)
    if container_type == "tar":
        return _tar_manifest_candidates(fixture, max_bytes, policy)
    raise ValueError(f"unsupported container type for manifest extraction: {container_type}")


def _zip_manifest_candidates(path: Path, max_bytes: int, policy: Mapping[str, Any] | None) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    with zipfile.ZipFile(path) as archive:
        for info in archive.infolist():
            if info.is_dir() or not _eligible(info.filename, info.file_size, max_bytes, policy):
                continue
            with archive.open(info, "r") as handle:
                payload = handle.read(max_bytes + 1)
            candidates.append(_candidate(info.filename, info.file_size, payload[:max_bytes], len(payload) > max_bytes, policy))
    return candidates


def _tar_manifest_candidates(path: Path, max_bytes: int, policy: Mapping[str, Any] | None) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    with tarfile.open(path) as archive:
        for info in archive.getmembers():
            if not info.isfile() or not _eligible(info.name, info.size, max_bytes, policy):
                continue
            handle = archive.extractfile(info)
            if handle is None:
                continue
            payload = handle.read(max_bytes + 1)
            candidates.append(_candidate(info.name, info.size, payload[:max_bytes], len(payload) > max_bytes, policy))
    return candidates


def _eligible(name: str, size: int, max_bytes: int, policy: Mapping[str, Any] | None) -> bool:
    path_check = check_path_safety(name, policy)
    return path_check["path_safe"] and manifest_like(name, policy) and size <= max_bytes


def _candidate(name: str, size: int, payload: bytes, truncated: bool, policy: Mapping[str, Any] | None) -> dict[str, Any]:
    normalized = check_path_safety(name, policy)["normalized_member_path"]
    text = payload.decode("utf-8", errors="replace")
    parsed = _parse_fields(normalized, text)
    candidate_id = stable_id("extraction.manifest_candidate", {"name": normalized, "fields": parsed})
    return {
        "schema_version": "extraction_manifest_candidate.v0",
        "manifest_candidate_id": candidate_id,
        "member_ref": normalized,
        "manifest_kind": manifest_kind(normalized),
        "manifest_name": normalized.rsplit("/", 1)[-1],
        "manifest_size": size,
        "manifest_preview": text[:512],
        "parsed_fields": parsed,
        "parser_confidence": "medium" if parsed else "low",
        "limitations": [
            "Manifest candidate is parsed from a committed fixture only.",
            "Manifest candidate is not accepted evidence.",
        ]
        + (["Manifest preview was truncated by policy."] if truncated else []),
        "evidence_candidate_preview": {
            "evidence_preview_id": stable_id("extraction.evidence_preview", candidate_id),
            "accepted_evidence": False,
            "review_required": True,
            "summary": f"Fixture manifest candidate {normalized}",
        },
        "truth_boundary": truth_boundary(),
        "product_boundary": product_boundary(),
    }


def _parse_fields(path: str, text: str) -> dict[str, Any]:
    basename = path.rsplit("/", 1)[-1].casefold()
    if basename.endswith(".json"):
        try:
            payload = json.loads(text)
        except json.JSONDecodeError:
            return {"parse_status": "json_parse_failed"}
        if isinstance(payload, dict):
            return {str(key): payload[key] for key in sorted(payload)[:12] if isinstance(payload[key], (str, int, float, bool, list, dict, type(None)))}
        return {"json_type": type(payload).__name__}
    fields: dict[str, Any] = {}
    for line in text.splitlines()[:40]:
        if "=" in line:
            key, value = line.split("=", 1)
            key = key.strip().strip('"').strip("'")
            if key and len(key) <= 80:
                fields[key] = value.strip().strip('"').strip("'")
        elif ":" in line:
            key, value = line.split(":", 1)
            key = key.strip()
            if key and len(key) <= 80:
                fields[key] = value.strip()
    return fields
