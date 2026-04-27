"""Ingest-facing boundary types for the Eureka bootstrap thin slice."""

from runtime.engine.interfaces.ingest.source_records import (
    ArticleScanRecordedSourceRecord,
    GitHubReleaseSourceRecord,
    InternetArchiveRecordedSourceRecord,
    LocalBundleSourceRecord,
    SyntheticSourceRecord,
)

__all__ = [
    "ArticleScanRecordedSourceRecord",
    "GitHubReleaseSourceRecord",
    "InternetArchiveRecordedSourceRecord",
    "LocalBundleSourceRecord",
    "SyntheticSourceRecord",
]
