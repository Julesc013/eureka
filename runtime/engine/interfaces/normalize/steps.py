from __future__ import annotations

import re
from typing import Any

from runtime.engine.compatibility import CompatibilityRequirements, attach_compatibility_evidence
from runtime.engine.interfaces.extract import (
    ExtractedGitHubReleaseRecord,
    ExtractedInternetArchiveRecordedItem,
    ExtractedLocalBundleRecord,
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

    return attach_compatibility_evidence(NormalizedResolutionRecord(
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
        compatibility_requirements=_compatibility_requirements(
            extracted_record.compatibility_record,
            "compatibility",
        ),
        evidence=_synthetic_evidence_summaries(
            source_locator=extracted_record.source_locator,
            object_label=object_label or object_id,
            access_path_locator=primary_representation.access_locator,
        ),
    ))


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

    return attach_compatibility_evidence(NormalizedResolutionRecord(
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
        compatibility_requirements=_compatibility_requirements(
            extracted_record.compatibility_record,
            "compatibility",
        ),
        evidence=_github_release_evidence_summaries(
            source_locator=extracted_record.source_locator,
            release_name=release_name or repo_full_name,
            tag_name=tag_name,
            release_locator=release_html_url or release_api_url or extracted_record.source_locator,
            published_at=published_at,
        ),
    ))


def normalize_internet_archive_recorded_item(
    extracted_record: ExtractedInternetArchiveRecordedItem,
) -> NormalizedResolutionRecord:
    item_record = extracted_record.item_record
    identifier = _require_string(item_record.get("identifier"), "item.identifier")
    identifier_key = _normalize_identifier(identifier)
    title = _require_string(item_record.get("title"), "item.title")
    mediatype = _optional_string(item_record.get("mediatype"), "item.mediatype") or "item"
    date = _optional_string(item_record.get("date"), "item.date")
    representations = _internet_archive_representation_summaries(
        extracted_record,
        identifier=identifier,
        identifier_key=identifier_key,
        title=title,
    )
    primary_representation = representations[0]

    return attach_compatibility_evidence(NormalizedResolutionRecord(
        target_ref=extracted_record.target_ref,
        source_name=extracted_record.source_name,
        source_locator=extracted_record.source_locator,
        object_id=f"obj.internet-archive-recorded.{identifier_key}",
        source_family="internet_archive_recorded",
        source_family_label="Internet Archive Recorded Fixtures",
        object_kind=mediatype,
        object_label=title,
        state_id=f"state.internet-archive-recorded.{identifier_key}.recorded",
        state_kind="recorded_item",
        representation_id=primary_representation.representation_id,
        representation_kind=primary_representation.representation_kind,
        access_path_id=primary_representation.access_path_id,
        access_path_kind=primary_representation.access_kind,
        access_path_locator=primary_representation.access_locator,
        representations=representations,
        compatibility_requirements=_compatibility_requirements(
            extracted_record.compatibility_record,
            "compatibility",
        ),
        evidence=_internet_archive_evidence_summaries(
            source_locator=extracted_record.source_locator,
            identifier=identifier,
            title=title,
            item_record=item_record,
            file_records=extracted_record.file_records,
            asserted_at=date,
        ),
    ))


def normalize_local_bundle_record(
    extracted_record: ExtractedLocalBundleRecord,
) -> NormalizedResolutionRecord:
    object_record = extracted_record.object_record
    state_record = extracted_record.state_record
    bundle_record = extracted_record.bundle_record
    object_label = _optional_string(object_record.get("label"), "object.label")
    object_id = _require_string(object_record.get("id"), "object.id")
    bundle_id = _require_string(bundle_record.get("id"), "bundle.id")
    representations = _local_bundle_representation_summaries(
        extracted_record,
        fallback_object_label=object_label or object_id,
        bundle_id=bundle_id,
    )
    primary_representation = representations[0]

    return attach_compatibility_evidence(NormalizedResolutionRecord(
        target_ref=extracted_record.target_ref,
        source_name=extracted_record.source_name,
        source_locator=extracted_record.source_locator,
        object_id=object_id,
        source_family="local_bundle_fixtures",
        source_family_label="Local Bundle Fixtures",
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
        compatibility_requirements=_compatibility_requirements(
            extracted_record.compatibility_record,
            "compatibility",
        ),
        evidence=_local_bundle_evidence_summaries(
            source_locator=extracted_record.source_locator,
            object_label=object_label or object_id,
            bundle_record=bundle_record,
            member_hint_records=extracted_record.member_hint_records,
        ),
    ))


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
        payload_fixture = _optional_mapping(
            raw_representation.get("payload_fixture"),
            f"representations[{index}].payload_fixture",
        )
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
                filename=_payload_filename(
                    payload_fixture,
                    f"representations[{index}].payload_fixture",
                    fallback_filename=None,
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
                is_fetchable=_payload_locator(
                    payload_fixture,
                    f"representations[{index}].payload_fixture",
                )
                is not None,
                fetch_locator=_payload_locator(
                    payload_fixture,
                    f"representations[{index}].payload_fixture",
                ),
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
            is_fetchable=False,
        )
    ]
    for index, asset_record in enumerate(extracted_record.asset_records):
        asset_name = _require_string(asset_record.get("name"), f"release.assets[{index}].name")
        asset_url = _require_string(
            asset_record.get("browser_download_url"),
            f"release.assets[{index}].browser_download_url",
        )
        payload_fixture = _optional_mapping(
            asset_record.get("payload_fixture"),
            f"release.assets[{index}].payload_fixture",
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
                filename=_payload_filename(
                    payload_fixture,
                    f"release.assets[{index}].payload_fixture",
                    fallback_filename=asset_name,
                ),
                source_family="github_releases",
                source_label="GitHub Releases",
                source_locator=extracted_record.source_locator,
                access_path_id=f"access.github-release.{repo_key}.{tag_key}.asset.{index}",
                access_kind="download",
                access_locator=asset_url,
                is_direct=True,
                is_fetchable=_payload_locator(
                    payload_fixture,
                    f"release.assets[{index}].payload_fixture",
                )
                is not None,
                fetch_locator=_payload_locator(
                    payload_fixture,
                    f"release.assets[{index}].payload_fixture",
                ),
            )
        )
    return tuple(summaries)


def _internet_archive_representation_summaries(
    extracted_record: ExtractedInternetArchiveRecordedItem,
    *,
    identifier: str,
    identifier_key: str,
    title: str,
) -> tuple[RepresentationSummary, ...]:
    item_locator = f"ia-recorded://{identifier}"
    summaries: list[RepresentationSummary] = [
        RepresentationSummary(
            representation_id=f"rep.internet-archive-recorded.{identifier_key}.metadata",
            representation_kind="archive_item_metadata",
            label=f"{title} metadata",
            content_type="application/json",
            source_family="internet_archive_recorded",
            source_label="Internet Archive Recorded Fixtures",
            source_locator=extracted_record.source_locator,
            access_path_id=f"access.internet-archive-recorded.{identifier_key}.metadata",
            access_kind="view",
            access_locator=item_locator,
            is_direct=False,
            is_fetchable=False,
        )
    ]
    for index, file_record in enumerate(extracted_record.file_records):
        filename = _require_string(file_record.get("name"), f"item.files[{index}].name")
        content_type = _optional_string(
            file_record.get("content_type"),
            f"item.files[{index}].content_type",
        )
        summaries.append(
            RepresentationSummary(
                representation_id=f"rep.internet-archive-recorded.{identifier_key}.file.{index}",
                representation_kind="archive_item_file",
                label=filename,
                content_type=content_type,
                byte_length=_optional_int(file_record.get("size"), f"item.files[{index}].size"),
                filename=filename,
                source_family="internet_archive_recorded",
                source_label="Internet Archive Recorded Fixtures",
                source_locator=extracted_record.source_locator,
                access_path_id=f"access.internet-archive-recorded.{identifier_key}.file.{index}",
                access_kind="view",
                access_locator=f"{item_locator}/{filename}",
                is_direct=False,
                is_fetchable=False,
            )
        )
    return tuple(summaries)


def _local_bundle_representation_summaries(
    extracted_record: ExtractedLocalBundleRecord,
    *,
    fallback_object_label: str,
    bundle_id: str,
) -> tuple[RepresentationSummary, ...]:
    bundle_record = extracted_record.bundle_record
    payload_fixture = _require_mapping(
        bundle_record.get("payload_fixture"),
        "bundle.payload_fixture",
    )
    access_path = _require_mapping(bundle_record.get("access_path"), "bundle.access_path")
    bundle_key = _normalize_identifier(bundle_id)
    filename = _payload_filename(
        payload_fixture,
        "bundle.payload_fixture",
        fallback_filename=_optional_string(bundle_record.get("filename"), "bundle.filename"),
    )
    return (
        RepresentationSummary(
            representation_id=_require_string(bundle_record.get("id"), "bundle.id"),
            representation_kind=_require_string(bundle_record.get("kind"), "bundle.kind"),
            label=_optional_string(bundle_record.get("label"), "bundle.label")
            or f"{fallback_object_label} bundle",
            content_type=_optional_string(bundle_record.get("content_type"), "bundle.content_type"),
            byte_length=_optional_int(bundle_record.get("byte_length"), "bundle.byte_length"),
            filename=filename,
            source_family="local_bundle_fixtures",
            source_label="Local Bundle Fixtures",
            source_locator=extracted_record.source_locator,
            access_path_id=_optional_string(access_path.get("id"), "bundle.access_path.id")
            or f"access.local-bundle.{bundle_key}",
            access_kind=_require_string(access_path.get("kind"), "bundle.access_path.kind"),
            access_locator=_optional_string(access_path.get("locator"), "bundle.access_path.locator"),
            is_direct=_optional_bool(access_path.get("is_direct"), "bundle.access_path.is_direct")
            or False,
            is_fetchable=_payload_locator(payload_fixture, "bundle.payload_fixture") is not None,
            fetch_locator=_payload_locator(payload_fixture, "bundle.payload_fixture"),
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


def _metadata_terms(metadata: dict[str, Any], field_names: tuple[str, ...]) -> str:
    terms: list[str] = []
    for field_name in field_names:
        value = metadata.get(field_name)
        if isinstance(value, str) and value:
            terms.append(value)
        elif isinstance(value, list):
            terms.extend(item for item in value if isinstance(item, str) and item)
    return "; ".join(terms)


def _internet_archive_evidence_summaries(
    *,
    source_locator: str,
    identifier: str,
    title: str,
    item_record: dict[str, Any],
    file_records: tuple[dict[str, Any], ...],
    asserted_at: str | None,
) -> tuple[EvidenceSummary, ...]:
    evidence: list[EvidenceSummary] = [
        EvidenceSummary(
            claim_kind="label",
            claim_value=title,
            asserted_by_family="internet_archive_recorded",
            asserted_by_label="Internet Archive Recorded Fixtures",
            evidence_kind="source_metadata",
            evidence_locator=f"{source_locator}#{identifier}",
            asserted_at=asserted_at,
        ),
        EvidenceSummary(
            claim_kind="source_identifier",
            claim_value=identifier,
            asserted_by_family="internet_archive_recorded",
            asserted_by_label="Internet Archive Recorded Fixtures",
            evidence_kind="source_metadata",
            evidence_locator=f"{source_locator}#{identifier}",
            asserted_at=asserted_at,
        ),
    ]
    description = _optional_string(item_record.get("description"), "item.description")
    if description is not None:
        evidence.append(
            EvidenceSummary(
                claim_kind="description",
                claim_value=description,
                asserted_by_family="internet_archive_recorded",
                asserted_by_label="Internet Archive Recorded Fixtures",
                evidence_kind="source_metadata",
                evidence_locator=f"{source_locator}#{identifier}",
                asserted_at=asserted_at,
            )
        )
    metadata = _optional_mapping(item_record.get("metadata"), "item.metadata")
    if metadata is not None:
        compatibility_text = _metadata_terms(metadata, ("platforms", "architectures", "artifact_roles"))
        if compatibility_text:
            evidence.append(
                EvidenceSummary(
                    claim_kind="compatibility_note",
                    claim_value=compatibility_text,
                    asserted_by_family="internet_archive_recorded",
                    asserted_by_label="Internet Archive Recorded Fixtures",
                    evidence_kind="source_metadata",
                    evidence_locator=f"{source_locator}#{identifier}",
                    asserted_at=asserted_at,
                )
            )
    for index, file_record in enumerate(file_records):
        file_name = _require_string(file_record.get("name"), f"item.files[{index}].name")
        evidence.append(
            EvidenceSummary(
                claim_kind="file_listing",
                claim_value=file_name,
                asserted_by_family="internet_archive_recorded",
                asserted_by_label="Internet Archive Recorded Fixtures",
                evidence_kind="file_listing",
                evidence_locator=f"{source_locator}#{identifier}/files/{index}",
                asserted_at=asserted_at,
            )
        )
    return tuple(evidence)


def _local_bundle_evidence_summaries(
    *,
    source_locator: str,
    object_label: str,
    bundle_record: dict[str, Any],
    member_hint_records: tuple[dict[str, Any], ...],
) -> tuple[EvidenceSummary, ...]:
    bundle_id = _require_string(bundle_record.get("id"), "bundle.id")
    evidence: list[EvidenceSummary] = [
        EvidenceSummary(
            claim_kind="label",
            claim_value=object_label,
            asserted_by_family="local_bundle_fixtures",
            asserted_by_label="Local Bundle Fixtures",
            evidence_kind="source_metadata",
            evidence_locator=f"{source_locator}#{bundle_id}",
        ),
        EvidenceSummary(
            claim_kind="representation_locator",
            claim_value=_optional_string(
                _require_mapping(bundle_record.get("access_path"), "bundle.access_path").get("locator"),
                "bundle.access_path.locator",
            )
            or bundle_id,
            asserted_by_family="local_bundle_fixtures",
            asserted_by_label="Local Bundle Fixtures",
            evidence_kind="source_metadata",
            evidence_locator=f"{source_locator}#{bundle_id}",
        ),
    ]
    for index, member_hint in enumerate(member_hint_records):
        member_path = _require_string(member_hint.get("member_path"), f"member_hints[{index}].member_path")
        evidence.append(
            EvidenceSummary(
                claim_kind="member_listing",
                claim_value=member_path,
                asserted_by_family="local_bundle_fixtures",
                asserted_by_label="Local Bundle Fixtures",
                evidence_kind="member_listing",
                evidence_locator=f"{source_locator}#{bundle_id}/members/{index}",
            )
        )
        compatibility = _optional_string(
            member_hint.get("compatibility_note"),
            f"member_hints[{index}].compatibility_note",
        )
        if compatibility is not None:
            evidence.append(
                EvidenceSummary(
                    claim_kind="compatibility_note",
                    claim_value=compatibility,
                    asserted_by_family="local_bundle_fixtures",
                    asserted_by_label="Local Bundle Fixtures",
                    evidence_kind="compatibility_note",
                    evidence_locator=f"{source_locator}#{bundle_id}/members/{index}",
                )
            )
    return tuple(evidence)


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


def _optional_mapping(value: Any, field_name: str) -> dict[str, Any] | None:
    if value is None:
        return None
    return _require_mapping(value, field_name)


def _payload_locator(payload_fixture: dict[str, Any] | None, field_name: str) -> str | None:
    if payload_fixture is None:
        return None
    return _optional_string(payload_fixture.get("locator"), f"{field_name}.locator")


def _payload_filename(
    payload_fixture: dict[str, Any] | None,
    field_name: str,
    *,
    fallback_filename: str | None,
) -> str | None:
    if payload_fixture is None:
        return fallback_filename
    return _optional_string(payload_fixture.get("filename"), f"{field_name}.filename") or fallback_filename


def _require_mapping(value: Any, field_name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{field_name} must be an object in the extracted record.")
    return dict(value)


def _compatibility_requirements(
    value: dict[str, Any] | None,
    field_name: str,
) -> CompatibilityRequirements | None:
    if value is None:
        return None
    required_os_families = _optional_string_sequence(
        value.get("required_os_families"),
        f"{field_name}.required_os_families",
    )
    required_architectures = _optional_string_sequence(
        value.get("required_architectures"),
        f"{field_name}.required_architectures",
    )
    required_runtime_families = _optional_string_sequence(
        value.get("required_runtime_families"),
        f"{field_name}.required_runtime_families",
    )
    required_features = _optional_string_sequence(
        value.get("required_features"),
        f"{field_name}.required_features",
    )
    requirements = CompatibilityRequirements(
        required_os_families=required_os_families,
        required_architectures=required_architectures,
        required_runtime_families=required_runtime_families,
        required_features=required_features,
    )
    return requirements if requirements.has_constraints() else None


def _normalize_identifier(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", ".", value.casefold()).strip(".")


def _optional_string_sequence(value: Any, field_name: str) -> tuple[str, ...]:
    if value is None:
        return ()
    if not isinstance(value, list):
        raise ValueError(f"{field_name} must be a list when provided.")
    normalized: list[str] = []
    for index, item in enumerate(value):
        normalized.append(_require_string(item, f"{field_name}[{index}]"))
    return tuple(normalized)
