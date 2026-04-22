from __future__ import annotations

from typing import Any

from runtime.engine.interfaces.extract.extracted_records import (
    ExtractedGitHubReleaseRecord,
    ExtractedSyntheticRecord,
)
from runtime.engine.interfaces.ingest import GitHubReleaseSourceRecord, SyntheticSourceRecord


def extract_synthetic_source_record(source_record: SyntheticSourceRecord) -> ExtractedSyntheticRecord:
    payload = source_record.payload
    return ExtractedSyntheticRecord(
        target_ref=source_record.target_ref,
        source_name=source_record.source_name,
        source_locator=source_record.source_locator,
        object_record=_require_mapping(payload.get("object"), "object"),
        state_record=_require_mapping(payload.get("state"), "state"),
        representation_record=_require_mapping(payload.get("representation"), "representation"),
        access_path_record=_require_mapping(payload.get("access_path"), "access_path"),
    )


def extract_github_release_source_record(
    source_record: GitHubReleaseSourceRecord,
) -> ExtractedGitHubReleaseRecord:
    payload = source_record.payload
    return ExtractedGitHubReleaseRecord(
        target_ref=source_record.target_ref,
        source_name=source_record.source_name,
        source_locator=source_record.source_locator,
        repository_record=_require_mapping(payload.get("repository"), "repository"),
        release_record=_require_mapping(payload.get("release"), "release"),
    )


def _require_mapping(value: Any, field_name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{field_name} must be an object in the synthetic source payload.")
    return dict(value)
