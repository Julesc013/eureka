"""Normalize-facing boundary types for the Eureka bootstrap thin slice."""

from runtime.engine.interfaces.normalize.normalized_records import NormalizedResolutionRecord
from runtime.engine.interfaces.normalize.steps import (
    normalize_article_scan_recorded_record,
    normalize_extracted_record,
    normalize_github_release_record,
    normalize_internet_archive_recorded_item,
    normalize_local_bundle_record,
)

__all__ = [
    "NormalizedResolutionRecord",
    "normalize_article_scan_recorded_record",
    "normalize_extracted_record",
    "normalize_github_release_record",
    "normalize_internet_archive_recorded_item",
    "normalize_local_bundle_record",
]
