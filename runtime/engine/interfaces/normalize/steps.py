from __future__ import annotations

import re
from typing import Any

from runtime.engine.interfaces.extract import (
    ExtractedGitHubReleaseRecord,
    ExtractedSyntheticRecord,
)
from runtime.engine.interfaces.normalize.normalized_records import NormalizedResolutionRecord


def normalize_extracted_record(extracted_record: ExtractedSyntheticRecord) -> NormalizedResolutionRecord:
    object_record = extracted_record.object_record
    state_record = extracted_record.state_record
    representation_record = extracted_record.representation_record
    access_path_record = extracted_record.access_path_record

    return NormalizedResolutionRecord(
        target_ref=extracted_record.target_ref,
        source_name=extracted_record.source_name,
        source_locator=extracted_record.source_locator,
        object_id=_require_string(object_record.get("id"), "object.id"),
        source_family="synthetic_fixture",
        source_family_label="Synthetic Fixture",
        object_kind=_optional_string(object_record.get("kind"), "object.kind"),
        object_label=_optional_string(object_record.get("label"), "object.label"),
        state_id=_optional_string(state_record.get("id"), "state.id"),
        state_kind=_optional_string(state_record.get("kind"), "state.kind"),
        representation_id=_optional_string(representation_record.get("id"), "representation.id"),
        representation_kind=_optional_string(representation_record.get("kind"), "representation.kind"),
        access_path_id=_optional_string(access_path_record.get("id"), "access_path.id"),
        access_path_kind=_optional_string(access_path_record.get("kind"), "access_path.kind"),
        access_path_locator=_optional_string(access_path_record.get("locator"), "access_path.locator"),
    )


def normalize_github_release_record(
    extracted_record: ExtractedGitHubReleaseRecord,
) -> NormalizedResolutionRecord:
    repository_record = extracted_record.repository_record
    release_record = extracted_record.release_record

    repo_full_name = _require_string(repository_record.get("full_name"), "repository.full_name")
    repo_key = _normalize_identifier(repo_full_name)
    tag_name = _require_string(release_record.get("tag_name"), "release.tag_name")
    tag_key = _normalize_identifier(tag_name)
    release_name = _optional_string(release_record.get("name"), "release.name")
    release_html_url = _optional_string(release_record.get("html_url"), "release.html_url")
    release_api_url = _optional_string(release_record.get("url"), "release.url")

    return NormalizedResolutionRecord(
        target_ref=extracted_record.target_ref,
        source_name=extracted_record.source_name,
        source_locator=extracted_record.source_locator,
        object_id=f"obj.github-release.{repo_key}",
        source_family="github_releases",
        source_family_label="GitHub Releases",
        object_kind="software",
        object_label=release_name or repo_full_name,
        state_id=f"state.github-release.{repo_key}.{tag_key}",
        state_kind="release",
        representation_id=f"rep.github-release.{repo_key}.release-metadata",
        representation_kind="release_metadata",
        access_path_id=f"access.github-release.{repo_key}.release",
        access_path_kind="github_release_html" if release_html_url is not None else "github_release_api",
        access_path_locator=release_html_url or release_api_url,
    )


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{field_name} must be a non-empty string in the extracted record.")
    return value


def _optional_string(value: Any, field_name: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or not value:
        raise ValueError(f"{field_name} must be a non-empty string when provided.")
    return value


def _normalize_identifier(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", ".", value.casefold()).strip(".")
