"""Tier 0 outer metadata extraction for fixture containers."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from runtime.extraction.container_detect import detect_container_type
from runtime.extraction.guards import file_sha256, repo_relative


def extract_tier0_outer_metadata(path: str | Path, policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    fixture = Path(path)
    stat = fixture.stat()
    return {
        "schema_version": "extraction_tier0_outer_metadata.v0",
        "tier": "0",
        "container_type": detect_container_type(fixture, policy),
        "target_path_public_safe": repo_relative(fixture),
        "input_size_bytes": stat.st_size,
        "sha256": file_sha256(fixture),
        "suffixes": list(fixture.suffixes),
        "metadata_collected_at": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
        "payload_executed": False,
        "payload_extracted_to_disk": False,
        "limitations": ["Outer metadata is collected from a repo-local fixture only."],
    }
