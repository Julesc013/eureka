from __future__ import annotations

from typing import Any

from runtime.engine.interfaces.extract.extracted_records import (
    ExtractedGitHubReleaseRecord,
    ExtractedSyntheticRecord,
)
from runtime.engine.interfaces.ingest import GitHubReleaseSourceRecord, SyntheticSourceRecord


def extract_synthetic_source_record(source_record: SyntheticSourceRecord) -> ExtractedSyntheticRecord:
    payload = source_record.payload
    representations = payload.get("representations")
    if representations is None:
        representation_record = _require_mapping(payload.get("representation"), "representation")
        access_path_record = _require_mapping(payload.get("access_path"), "access_path")
        representation_records = (
            _merge_representation_and_access_path(representation_record, access_path_record),
        )
    else:
        representation_records = _require_mapping_sequence(representations, "representations")
        if not representation_records:
            raise ValueError("representations must contain at least one entry in the synthetic source payload.")
        representation_record = dict(representation_records[0])
        access_path_record = _require_mapping(
            representation_record.get("access_path"),
            "representations[0].access_path",
        )
    return ExtractedSyntheticRecord(
        target_ref=source_record.target_ref,
        source_name=source_record.source_name,
        source_locator=source_record.source_locator,
        object_record=_require_mapping(payload.get("object"), "object"),
        state_record=_require_mapping(payload.get("state"), "state"),
        representation_record=representation_record,
        access_path_record=access_path_record,
        representation_records=representation_records,
    )


def extract_github_release_source_record(
    source_record: GitHubReleaseSourceRecord,
) -> ExtractedGitHubReleaseRecord:
    payload = source_record.payload
    release_record = _require_mapping(payload.get("release"), "release")
    return ExtractedGitHubReleaseRecord(
        target_ref=source_record.target_ref,
        source_name=source_record.source_name,
        source_locator=source_record.source_locator,
        repository_record=_require_mapping(payload.get("repository"), "repository"),
        release_record=release_record,
        asset_records=_require_optional_mapping_sequence(release_record.get("assets"), "release.assets"),
    )


def _require_mapping(value: Any, field_name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{field_name} must be an object in the synthetic source payload.")
    return dict(value)


def _require_mapping_sequence(value: Any, field_name: str) -> tuple[dict[str, Any], ...]:
    if not isinstance(value, list):
        raise ValueError(f"{field_name} must be a list in the synthetic source payload.")
    return tuple(_require_mapping(item, f"{field_name}[]") for item in value)


def _require_optional_mapping_sequence(value: Any, field_name: str) -> tuple[dict[str, Any], ...]:
    if value is None:
        return ()
    return _require_mapping_sequence(value, field_name)


def _merge_representation_and_access_path(
    representation_record: dict[str, Any],
    access_path_record: dict[str, Any],
) -> dict[str, Any]:
    merged = dict(representation_record)
    merged["access_path"] = dict(access_path_record)
    return merged
