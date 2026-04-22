from __future__ import annotations

import re
from typing import Any

from runtime.engine.interfaces.extract import (
    ExtractedGitHubReleaseRecord,
    ExtractedSyntheticRecord,
)
from runtime.engine.interfaces.normalize.normalized_records import NormalizedResolutionRecord
from runtime.engine.provenance import EvidenceSummary


def normalize_extracted_record(extracted_record: ExtractedSyntheticRecord) -> NormalizedResolutionRecord:
    object_record = extracted_record.object_record
    state_record = extracted_record.state_record
    representation_record = extracted_record.representation_record
    access_path_record = extracted_record.access_path_record
    object_label = _optional_string(object_record.get("label"), "object.label")
    object_id = _require_string(object_record.get("id"), "object.id")
    access_path_locator = _optional_string(access_path_record.get("locator"), "access_path.locator")

    return NormalizedResolutionRecord(
        target_ref=extracted_record.target_ref,
        source_name=extracted_record.source_name,
        source_locator=extracted_record.source_locator,
        object_id=object_id,
        source_family="synthetic_fixture",
        source_family_label="Synthetic Fixture",
        object_kind=_optional_string(object_record.get("kind"), "object.kind"),
        object_label=object_label,
        state_id=_optional_string(state_record.get("id"), "state.id"),
        state_kind=_optional_string(state_record.get("kind"), "state.kind"),
        representation_id=_optional_string(representation_record.get("id"), "representation.id"),
        representation_kind=_optional_string(representation_record.get("kind"), "representation.kind"),
        access_path_id=_optional_string(access_path_record.get("id"), "access_path.id"),
        access_path_kind=_optional_string(access_path_record.get("kind"), "access_path.kind"),
        access_path_locator=access_path_locator,
        evidence=_synthetic_evidence_summaries(
            source_locator=extracted_record.source_locator,
            object_label=object_label or object_id,
            access_path_locator=access_path_locator,
        ),
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
    published_at = _optional_string(release_record.get("published_at"), "release.published_at")

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
        evidence=_github_release_evidence_summaries(
            source_locator=extracted_record.source_locator,
            release_name=release_name or repo_full_name,
            tag_name=tag_name,
            release_locator=release_html_url or release_api_url or extracted_record.source_locator,
            published_at=published_at,
        ),
    )


def _synthetic_evidence_summaries(
    *,
    source_locator: str,
    object_label: str,
    access_path_locator: str | None,
) -> tuple[EvidenceSummary, ...]:
    evidence = [
        EvidenceSummary(
            claim_kind="label",
            claim_value=object_label,
            asserted_by_family="synthetic_fixture",
            asserted_by_label="Synthetic Fixture",
            evidence_kind="recorded_fixture",
            evidence_locator=source_locator,
        )
    ]
    if access_path_locator is not None:
        evidence.append(
            EvidenceSummary(
                claim_kind="source_locator",
                claim_value=access_path_locator,
                asserted_by_family="synthetic_fixture",
                asserted_by_label="Synthetic Fixture",
                evidence_kind="recorded_fixture",
                evidence_locator=source_locator,
            )
        )
    return tuple(evidence)


def _github_release_evidence_summaries(
    *,
    source_locator: str,
    release_name: str,
    tag_name: str,
    release_locator: str,
    published_at: str | None,
) -> tuple[EvidenceSummary, ...]:
    return (
        EvidenceSummary(
            claim_kind="label",
            claim_value=release_name,
            asserted_by_family="github_releases",
            asserted_by_label="GitHub Releases",
            evidence_kind="recorded_source_payload",
            evidence_locator=source_locator,
            asserted_at=published_at,
        ),
        EvidenceSummary(
            claim_kind="version",
            claim_value=tag_name,
            asserted_by_family="github_releases",
            asserted_by_label="GitHub Releases",
            evidence_kind="recorded_source_payload",
            evidence_locator=source_locator,
            asserted_at=published_at,
        ),
        EvidenceSummary(
            claim_kind="source_locator",
            claim_value=release_locator,
            asserted_by_family="github_releases",
            asserted_by_label="GitHub Releases",
            evidence_kind="recorded_source_payload",
            evidence_locator=source_locator,
            asserted_at=published_at,
        ),
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
