"""Normalize committed Internet Archive metadata fixtures."""

from __future__ import annotations

from typing import Any, Mapping

from runtime.source_observation.internet_archive_metadata import (
    FILE_METADATA_CAP,
    IAMetadataCandidateRecord,
    IAMetadataSourceLocator,
)


KIND_BY_FIXTURE_CLASS = {
    "metadata_search_small": "metadata_search_result",
    "item_metadata_read": "item_metadata",
    "item_file_list_metadata_read": "item_file_list",
    "missing_item": "missing_item",
    "malformed_partial": "malformed_partial",
    "retry_after_429": "retry_after",
    "large_file_list": "large_file_list",
    "no_download_proof": "no_download_proof",
}


def normalize_ia_metadata_fixture(fixture: Mapping[str, Any]) -> IAMetadataCandidateRecord:
    fixture_id = str(fixture.get("fixture_id", ""))
    fixture_class = str(fixture.get("fixture_class", ""))
    observation_kind = KIND_BY_FIXTURE_CLASS.get(fixture_class, fixture_class)
    payload = dict(fixture.get("payload", {}) or {})

    if observation_kind == "metadata_search_result":
        return _normalize_metadata_search(fixture_id, fixture, payload)
    if observation_kind == "missing_item":
        return _normalize_missing_item(fixture_id, fixture)
    if observation_kind == "malformed_partial":
        return _normalize_malformed_partial(fixture_id, fixture, payload)
    if observation_kind == "retry_after":
        return _normalize_retry_after(fixture_id, fixture)
    return _normalize_item_like(fixture_id, observation_kind, fixture, payload)


def _normalize_metadata_search(
    fixture_id: str,
    fixture: Mapping[str, Any],
    payload: Mapping[str, Any],
) -> IAMetadataCandidateRecord:
    response = dict(payload.get("response", {}) or {})
    docs = response.get("docs", []) or []
    first = dict(docs[0]) if docs and isinstance(docs[0], Mapping) else {}
    limitations = [
        "committed metadata fixture input",
        "metadata search result is not accepted truth",
        f"bounded search rows observed: {len(docs)}",
    ]
    return _record(
        fixture_id=fixture_id,
        observation_kind="metadata_search_result",
        fixture=fixture,
        metadata=first,
        files=(),
        limitations=limitations,
        risk_flags=("metadata_not_truth", "search_result_requires_review"),
        confidence=0.55,
    )


def _normalize_item_like(
    fixture_id: str,
    observation_kind: str,
    fixture: Mapping[str, Any],
    payload: Mapping[str, Any],
) -> IAMetadataCandidateRecord:
    metadata = dict(payload.get("metadata", {}) or {})
    files = tuple(dict(item) for item in payload.get("files", []) or [] if isinstance(item, Mapping))
    limitations = [
        "committed metadata fixture input",
        "item metadata is not accepted truth",
        "file entries are metadata only",
    ]
    if observation_kind == "large_file_list" and len(files) > FILE_METADATA_CAP:
        limitations.append(f"file metadata candidates capped at {FILE_METADATA_CAP} of {len(files)}")
    if observation_kind == "no_download_proof":
        limitations.append("no file content included or fetched")
    confidence = 0.6 if observation_kind != "large_file_list" else 0.5
    return _record(
        fixture_id=fixture_id,
        observation_kind=observation_kind,
        fixture=fixture,
        metadata=metadata,
        files=files,
        limitations=limitations,
        risk_flags=("metadata_not_truth", "file_metadata_requires_review"),
        confidence=confidence,
    )


def _normalize_missing_item(fixture_id: str, fixture: Mapping[str, Any]) -> IAMetadataCandidateRecord:
    identifier = str((fixture.get("request", {}) or {}).get("identifier", ""))
    metadata = {"identifier": identifier}
    return _record(
        fixture_id=fixture_id,
        observation_kind="missing_item",
        fixture=fixture,
        metadata=metadata,
        files=(),
        limitations=(
            "committed metadata fixture input",
            "source reported missing item",
            "absence is local source-miss material only",
        ),
        risk_flags=("source_miss", "metadata_not_truth"),
        confidence=0.2,
    )


def _normalize_malformed_partial(
    fixture_id: str,
    fixture: Mapping[str, Any],
    payload: Mapping[str, Any],
) -> IAMetadataCandidateRecord:
    metadata = dict(payload.get("metadata", {}) or {})
    files = tuple(dict(item) for item in payload.get("files", []) or [] if isinstance(item, Mapping))
    return _record(
        fixture_id=fixture_id,
        observation_kind="malformed_partial",
        fixture=fixture,
        metadata=metadata,
        files=files,
        limitations=(
            "committed metadata fixture input",
            "required item identifier missing",
            "partial metadata requires review before use",
        ),
        risk_flags=("malformed_partial", "metadata_not_truth"),
        confidence=0.1,
    )


def _normalize_retry_after(fixture_id: str, fixture: Mapping[str, Any]) -> IAMetadataCandidateRecord:
    retry_after = str((fixture.get("headers", {}) or {}).get("Retry-After", ""))
    request = dict(fixture.get("request", {}) or {})
    metadata = {"description": str(request.get("query", ""))}
    return _record(
        fixture_id=fixture_id,
        observation_kind="retry_after",
        fixture=fixture,
        metadata=metadata,
        files=(),
        limitations=(
            "committed metadata fixture input",
            f"Retry-After required: {retry_after} seconds",
            "no retry or live request performed",
        ),
        risk_flags=("quota_or_rate_limit", "retry_after_required"),
        confidence=0.2,
    )


def _record(
    *,
    fixture_id: str,
    observation_kind: str,
    fixture: Mapping[str, Any],
    metadata: Mapping[str, Any],
    files: tuple[Mapping[str, Any], ...],
    limitations: tuple[str, ...] | list[str],
    risk_flags: tuple[str, ...],
    confidence: float,
) -> IAMetadataCandidateRecord:
    endpoint_class = str(fixture.get("endpoint_class", ""))
    identifier = str(metadata.get("identifier") or (fixture.get("request", {}) or {}).get("identifier", ""))
    capped_files = tuple(files[:FILE_METADATA_CAP])
    file_metadata = tuple(_file_metadata(item) for item in capped_files)
    checksum_candidates = tuple(_checksum_metadata(item) for item in capped_files if _checksum_metadata(item))
    title = str(metadata.get("title", ""))
    mediatype = str(metadata.get("mediatype", ""))
    collection = _as_string_tuple(metadata.get("collection", []))
    creator = str(metadata.get("creator", ""))
    date = str(metadata.get("date", ""))
    description = str(metadata.get("description", ""))
    return IAMetadataCandidateRecord(
        observation_id=f"iaobs_{fixture_id}",
        fixture_id=fixture_id,
        observation_kind=observation_kind,
        item_identifier=identifier,
        title_candidate=title,
        mediatype_candidate=mediatype,
        collection_candidates=collection,
        creator_candidate=creator,
        date_candidate=date,
        description_candidate=description,
        file_metadata_candidates=file_metadata,
        checksum_candidates=checksum_candidates,
        source_locator=IAMetadataSourceLocator(
            kind="internet_archive_identifier" if identifier else "internet_archive_metadata_state",
            value=identifier or fixture_id,
            label="Internet Archive metadata fixture locator",
            metadata={
                "endpoint_class": endpoint_class,
                "replay_source": "committed_fixture",
                "metadata_only": True,
            },
        ),
        limitations=tuple(limitations),
        risk_flags=tuple(risk_flags),
        rights_flags=("rights_not_inferred", "safety_not_inferred", "compatibility_not_inferred"),
        confidence=confidence,
    )


def _as_string_tuple(value: Any) -> tuple[str, ...]:
    if isinstance(value, str):
        return (value,) if value else ()
    if isinstance(value, list | tuple):
        return tuple(str(item) for item in value if str(item))
    return ()


def _file_metadata(item: Mapping[str, Any]) -> dict[str, str]:
    return {
        "name": str(item.get("name", "")),
        "format": str(item.get("format", "")),
        "size": str(item.get("size", "")),
    }


def _checksum_metadata(item: Mapping[str, Any]) -> dict[str, str]:
    values = {
        key: str(item.get(key, ""))
        for key in ("name", "md5", "sha1", "crc32")
        if str(item.get(key, ""))
    }
    return values
