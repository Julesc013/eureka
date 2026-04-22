from __future__ import annotations

import re
from typing import Any

from runtime.engine.interfaces.extract import (
    ExtractedGitHubReleaseRecord,
    ExtractedSyntheticRecord,
)
from runtime.engine.interfaces.normalize.normalized_records import NormalizedResolutionRecord
from runtime.engine.provenance import EvidenceSummary
from runtime.engine.representations import RepresentationSummary


def normalize_extracted_record(extracted_record: ExtractedSyntheticRecord) -> NormalizedResolutionRecord:
    object_record = extracted_record.object_record
    state_record = extracted_record.state_record
    object_label = _optional_string(object_record.get("label"), "object.label")
    object_id = _require_string(object_record.get("id"), "object.id")
    representations = _synthetic_representation_summaries(
        extracted_record,
        fallback_object_label=object_label or object_id,
    )
    primary_representation = representations[0]

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
        representation_id=primary_representation.representation_id,
        representation_kind=primary_representation.representation_kind,
        access_path_id=primary_representation.access_path_id,
        access_path_kind=primary_representation.access_kind,
        access_path_locator=primary_representation.access_locator,
        representations=representations,
        evidence=_synthetic_evidence_summaries(
            source_locator=extracted_record.source_locator,
            object_label=object_label or object_id,
            access_path_locator=primary_representation.access_locator,
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
    representations = _github_release_representation_summaries(
        extracted_record,
        repo_full_name=repo_full_name,
        release_name=release_name or repo_full_name,
        release_html_url=release_html_url,
        release_api_url=release_api_url,
    )
    primary_representation = representations[0]

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
        representation_id=primary_representation.representation_id,
        representation_kind=primary_representation.representation_kind,
        access_path_id=primary_representation.access_path_id,
        access_path_kind=primary_representation.access_kind,
        access_path_locator=primary_representation.access_locator,
        representations=representations,
        evidence=_github_release_evidence_summaries(
            source_locator=extracted_record.source_locator,
            release_name=release_name or repo_full_name,
            tag_name=tag_name,
            release_locator=release_html_url or release_api_url or extracted_record.source_locator,
            published_at=published_at,
        ),
    )


def _synthetic_representation_summaries(
    extracted_record: ExtractedSyntheticRecord,
    *,
    fallback_object_label: str,
) -> tuple[RepresentationSummary, ...]:
    raw_representations = extracted_record.representation_records or (
        {
            **extracted_record.representation_record,
            "access_path": dict(extracted_record.access_path_record),
        },
    )
    summaries: list[RepresentationSummary] = []
    for index, raw_representation in enumerate(raw_representations):
        access_path = _require_mapping(raw_representation.get("access_path"), f"representations[{index}].access_path")
        label = _optional_string(raw_representation.get("label"), f"representations[{index}].label")
        content_type = _optional_string(
            raw_representation.get("content_type"),
            f"representations[{index}].content_type",
        ) or _optional_string(raw_representation.get("format"), f"representations[{index}].format")
        access_kind = _require_string(
            access_path.get("kind"),
            f"representations[{index}].access_path.kind",
        )
        if access_kind == "fixture_path":
            access_kind = "inspect"
        summaries.append(
            RepresentationSummary(
                representation_id=_require_string(raw_representation.get("id"), f"representations[{index}].id"),
                representation_kind=_require_string(
                    raw_representation.get("kind"),
                    f"representations[{index}].kind",
                ),
                label=label or f"{fallback_object_label} representation",
                content_type=content_type,
                byte_length=_optional_int(
                    raw_representation.get("byte_length"),
                    f"representations[{index}].byte_length",
                ),
                source_family="synthetic_fixture",
                source_label="Synthetic Fixture",
                source_locator=extracted_record.source_locator,
                access_path_id=_optional_string(
                    access_path.get("id"),
                    f"representations[{index}].access_path.id",
                ),
                access_kind=access_kind,
                access_locator=_optional_string(
                    access_path.get("locator"),
                    f"representations[{index}].access_path.locator",
                ),
                is_direct=_optional_bool(
                    access_path.get("is_direct"),
                    f"representations[{index}].access_path.is_direct",
                ) or False,
            )
        )
    return tuple(summaries)


def _github_release_representation_summaries(
    extracted_record: ExtractedGitHubReleaseRecord,
    *,
    repo_full_name: str,
    release_name: str,
    release_html_url: str | None,
    release_api_url: str | None,
) -> tuple[RepresentationSummary, ...]:
    repo_key = _normalize_identifier(repo_full_name)
    tag_name = _require_string(extracted_record.release_record.get("tag_name"), "release.tag_name")
    tag_key = _normalize_identifier(tag_name)
    release_locator = release_html_url or release_api_url or extracted_record.source_locator
    summaries: list[RepresentationSummary] = [
        RepresentationSummary(
            representation_id=f"rep.github-release.{repo_key}.release-metadata",
            representation_kind="release_page",
            label=f"{release_name} release page",
            content_type="text/html" if release_html_url is not None else "application/json",
            source_family="github_releases",
            source_label="GitHub Releases",
            source_locator=extracted_record.source_locator,
            access_path_id=f"access.github-release.{repo_key}.{tag_key}.release",
            access_kind="view",
            access_locator=release_locator,
            is_direct=False,
        )
    ]
    for index, asset_record in enumerate(extracted_record.asset_records):
        asset_name = _require_string(asset_record.get("name"), f"release.assets[{index}].name")
        asset_url = _require_string(
            asset_record.get("browser_download_url"),
            f"release.assets[{index}].browser_download_url",
        )
        summaries.append(
            RepresentationSummary(
                representation_id=f"rep.github-release.{repo_key}.{tag_key}.asset.{index}",
                representation_kind="release_asset",
                label=asset_name,
                content_type=_optional_string(
                    asset_record.get("content_type"),
                    f"release.assets[{index}].content_type",
                ),
                byte_length=_optional_int(asset_record.get("size"), f"release.assets[{index}].size"),
                source_family="github_releases",
                source_label="GitHub Releases",
                source_locator=extracted_record.source_locator,
                access_path_id=f"access.github-release.{repo_key}.{tag_key}.asset.{index}",
                access_kind="download",
                access_locator=asset_url,
                is_direct=True,
            )
        )
    return tuple(summaries)


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


def _optional_int(value: Any, field_name: str) -> int | None:
    if value is None:
        return None
    if not isinstance(value, int) or value < 0:
        raise ValueError(f"{field_name} must be a non-negative integer when provided.")
    return value


def _optional_bool(value: Any, field_name: str) -> bool | None:
    if value is None:
        return None
    if not isinstance(value, bool):
        raise ValueError(f"{field_name} must be a boolean when provided.")
    return value


def _require_mapping(value: Any, field_name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{field_name} must be an object in the extracted record.")
    return dict(value)


def _normalize_identifier(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", ".", value.casefold()).strip(".")
