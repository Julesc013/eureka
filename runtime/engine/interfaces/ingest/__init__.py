"""Ingest-facing boundary types for the Eureka bootstrap thin slice."""

from runtime.engine.interfaces.ingest.source_records import (
    GitHubReleaseSourceRecord,
    SyntheticSourceRecord,
)

__all__ = ["GitHubReleaseSourceRecord", "SyntheticSourceRecord"]
