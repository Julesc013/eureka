"""Fixture-only normalizers for the H1 metadata wave.

The package contains no live connector runtime. It reads committed fixtures,
normalizes metadata-shaped records, and builds preview-only output artifacts.
"""

from runtime.connectors.h1_metadata_wave.normalizer_common import (
    H1_SOURCE_IDS,
    build_h1_evidence_candidate_preview,
    build_h1_fixture_replay_result,
    build_h1_source_cache_candidate_preview,
    detect_h1_product_boundary_violations,
    detect_h1_truth_boundary_violations,
    normalize_h1_fixture,
    summarize_h1_normalized_record,
)

__all__ = [
    "H1_SOURCE_IDS",
    "build_h1_evidence_candidate_preview",
    "build_h1_fixture_replay_result",
    "build_h1_source_cache_candidate_preview",
    "detect_h1_product_boundary_violations",
    "detect_h1_truth_boundary_violations",
    "normalize_h1_fixture",
    "summarize_h1_normalized_record",
]
