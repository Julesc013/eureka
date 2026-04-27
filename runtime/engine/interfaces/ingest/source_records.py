from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class SyntheticSourceRecord:
    target_ref: str
    source_name: str
    payload: dict[str, Any]
    source_locator: str


@dataclass(frozen=True)
class GitHubReleaseSourceRecord:
    target_ref: str
    source_name: str
    payload: dict[str, Any]
    source_locator: str


@dataclass(frozen=True)
class InternetArchiveRecordedSourceRecord:
    target_ref: str
    source_name: str
    payload: dict[str, Any]
    source_locator: str


@dataclass(frozen=True)
class LocalBundleSourceRecord:
    target_ref: str
    source_name: str
    payload: dict[str, Any]
    source_locator: str


@dataclass(frozen=True)
class ArticleScanRecordedSourceRecord:
    target_ref: str
    source_name: str
    payload: dict[str, Any]
    source_locator: str
