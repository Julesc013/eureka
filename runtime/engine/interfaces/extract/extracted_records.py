from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ExtractedSyntheticRecord:
    target_ref: str
    source_name: str
    source_locator: str
    object_record: dict[str, Any]
    state_record: dict[str, Any]
    representation_record: dict[str, Any]
    access_path_record: dict[str, Any]
    representation_records: tuple[dict[str, Any], ...] = ()
    compatibility_record: dict[str, Any] | None = None


@dataclass(frozen=True)
class ExtractedGitHubReleaseRecord:
    target_ref: str
    source_name: str
    source_locator: str
    repository_record: dict[str, Any]
    release_record: dict[str, Any]
    asset_records: tuple[dict[str, Any], ...] = ()
    compatibility_record: dict[str, Any] | None = None


@dataclass(frozen=True)
class ExtractedInternetArchiveRecordedItem:
    target_ref: str
    source_name: str
    source_locator: str
    item_record: dict[str, Any]
    file_records: tuple[dict[str, Any], ...] = ()
    compatibility_record: dict[str, Any] | None = None


@dataclass(frozen=True)
class ExtractedLocalBundleRecord:
    target_ref: str
    source_name: str
    source_locator: str
    object_record: dict[str, Any]
    state_record: dict[str, Any]
    bundle_record: dict[str, Any]
    member_hint_records: tuple[dict[str, Any], ...] = ()
    compatibility_record: dict[str, Any] | None = None
