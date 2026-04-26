"""Ingest-facing boundary types for the Eureka bootstrap thin slice."""

from runtime.engine.interfaces.ingest.source_records import (
    GitHubReleaseSourceRecord,
    InternetArchiveRecordedSourceRecord,
    LocalBundleSourceRecord,
    SyntheticSourceRecord,
)

__all__ = [
    "GitHubReleaseSourceRecord",
    "InternetArchiveRecordedSourceRecord",
    "LocalBundleSourceRecord",
    "SyntheticSourceRecord",
]
