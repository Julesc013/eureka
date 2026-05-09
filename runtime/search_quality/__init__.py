"""Fixture-only search explanation helpers."""

from runtime.search_quality.explanation import (
    build_search_result_explanation,
    detect_explanation_truth_boundary_violations,
    explain_candidate_result,
    explain_evidence_supported_result,
    explain_extraction_member_result,
    explain_source_cache_supported_result,
    load_search_quality_policy,
    validate_search_result_explanation,
)
from runtime.search_quality.explanation_summary import (
    build_explanation_output_bundle,
    summarize_explanation_output_bundle,
)
from runtime.search_quality.known_absence import (
    build_known_absence_record,
    detect_absence_overclaim,
    summarize_known_absence,
    validate_known_absence_record,
)
from runtime.search_quality.near_miss import (
    build_near_miss_explanation,
    classify_near_miss_mismatch,
    validate_near_miss_explanation,
)

__all__ = [
    "build_explanation_output_bundle",
    "build_known_absence_record",
    "build_near_miss_explanation",
    "build_search_result_explanation",
    "classify_near_miss_mismatch",
    "detect_absence_overclaim",
    "detect_explanation_truth_boundary_violations",
    "explain_candidate_result",
    "explain_evidence_supported_result",
    "explain_extraction_member_result",
    "explain_source_cache_supported_result",
    "load_search_quality_policy",
    "summarize_explanation_output_bundle",
    "summarize_known_absence",
    "validate_known_absence_record",
    "validate_near_miss_explanation",
    "validate_search_result_explanation",
]
