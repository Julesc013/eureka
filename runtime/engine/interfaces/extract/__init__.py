"""Extract-facing boundary types for the Eureka bootstrap thin slice."""

from runtime.engine.interfaces.extract.extracted_records import (
    ExtractedArticleScanRecordedRecord,
    ExtractedGitHubReleaseRecord,
    ExtractedInternetArchiveRecordedItem,
    ExtractedLocalBundleRecord,
    ExtractedSyntheticRecord,
)
from runtime.engine.interfaces.extract.steps import (
    extract_article_scan_recorded_source_record,
    extract_github_release_source_record,
    extract_internet_archive_recorded_source_record,
    extract_local_bundle_source_record,
    extract_synthetic_source_record,
)

__all__ = [
    "ExtractedArticleScanRecordedRecord",
    "ExtractedGitHubReleaseRecord",
    "ExtractedInternetArchiveRecordedItem",
    "ExtractedLocalBundleRecord",
    "ExtractedSyntheticRecord",
    "extract_article_scan_recorded_source_record",
    "extract_github_release_source_record",
    "extract_internet_archive_recorded_source_record",
    "extract_local_bundle_source_record",
    "extract_synthetic_source_record",
]
