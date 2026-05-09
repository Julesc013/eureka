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
from runtime.search_quality.dedup_shadow import (
    build_dedup_shadow,
    group_duplicate_candidates_shadow_only,
    validate_dedup_shadow,
)
from runtime.search_quality.identity_shadow import (
    build_identity_merge_shadow,
    preserve_identity_conflicts,
    validate_identity_merge_shadow,
)
from runtime.search_quality.public_ranking_gate import (
    build_public_ranking_gate,
    summarize_public_ranking_gate,
    validate_public_ranking_gate,
)
from runtime.search_quality.quality_harness import (
    build_search_quality_regression_report,
    detect_quality_overclaim,
    load_query_set,
    run_quality_regression,
    summarize_regression_report,
)
from runtime.search_quality.ranking_shadow import (
    build_factor_results,
    build_ranking_output_bundle,
    build_ranking_shadow,
    detect_ranking_truth_boundary_violations,
    load_ranking_policy,
    score_ranking_item,
    summarize_ranking_shadow,
    validate_ranking_shadow_result,
)

__all__ = [
    "build_explanation_output_bundle",
    "build_known_absence_record",
    "build_dedup_shadow",
    "build_factor_results",
    "build_identity_merge_shadow",
    "build_near_miss_explanation",
    "build_public_ranking_gate",
    "build_ranking_output_bundle",
    "build_ranking_shadow",
    "build_search_result_explanation",
    "build_search_quality_regression_report",
    "classify_near_miss_mismatch",
    "detect_absence_overclaim",
    "detect_explanation_truth_boundary_violations",
    "detect_quality_overclaim",
    "detect_ranking_truth_boundary_violations",
    "explain_candidate_result",
    "explain_evidence_supported_result",
    "explain_extraction_member_result",
    "explain_source_cache_supported_result",
    "group_duplicate_candidates_shadow_only",
    "load_query_set",
    "load_ranking_policy",
    "load_search_quality_policy",
    "preserve_identity_conflicts",
    "run_quality_regression",
    "score_ranking_item",
    "summarize_explanation_output_bundle",
    "summarize_known_absence",
    "summarize_public_ranking_gate",
    "summarize_ranking_shadow",
    "summarize_regression_report",
    "validate_dedup_shadow",
    "validate_identity_merge_shadow",
    "validate_known_absence_record",
    "validate_near_miss_explanation",
    "validate_public_ranking_gate",
    "validate_ranking_shadow_result",
    "validate_search_result_explanation",
]
