"""Normalize-facing boundary types for the Eureka bootstrap thin slice."""

from runtime.engine.interfaces.normalize.normalized_records import NormalizedResolutionRecord
from runtime.engine.interfaces.normalize.steps import (
    normalize_extracted_record,
    normalize_github_release_record,
)

__all__ = [
    "NormalizedResolutionRecord",
    "normalize_extracted_record",
    "normalize_github_release_record",
]
