"""Fixture-only Internet Archive metadata normalization helpers."""

from runtime.connectors.internet_archive.fixture_loader import load_fixture
from runtime.connectors.internet_archive.metadata_normalizer import (
    detect_product_boundary_violations,
    detect_truth_boundary_violations,
    map_normalized_to_source_cache_candidate,
    normalize_ia_metadata,
    preview_evidence_candidates,
    summarize_ia_normalized_record,
    validate_no_live_call_boundary,
)

__all__ = [
    "detect_product_boundary_violations",
    "detect_truth_boundary_violations",
    "load_fixture",
    "map_normalized_to_source_cache_candidate",
    "normalize_ia_metadata",
    "preview_evidence_candidates",
    "summarize_ia_normalized_record",
    "validate_no_live_call_boundary",
]
