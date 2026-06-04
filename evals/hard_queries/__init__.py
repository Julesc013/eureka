"""Hard-query usefulness eval helpers."""

from evals.hard_queries.evaluator import (
    BASELINE_PROFILES,
    REQUIRED_HARD_QUERY_IDS,
    evaluate_fixture_case,
    evaluate_fixture_suite,
    load_expected_answer_shapes,
    load_hard_query_registry,
    load_scorecard,
    render_fixture_case,
    validate_expected_answer_shapes,
    validate_hard_query_registry,
    validate_scorecard,
)
from evals.hard_queries.fixtures_v0 import (
    SYNTHETIC_FIXTURE_DISCLAIMER,
    fixture_case_by_query_id,
    fixture_cases,
    resolution_run_for_fixture,
)

__all__ = [
    "BASELINE_PROFILES",
    "REQUIRED_HARD_QUERY_IDS",
    "SYNTHETIC_FIXTURE_DISCLAIMER",
    "evaluate_fixture_case",
    "evaluate_fixture_suite",
    "fixture_case_by_query_id",
    "fixture_cases",
    "load_expected_answer_shapes",
    "load_hard_query_registry",
    "load_scorecard",
    "render_fixture_case",
    "resolution_run_for_fixture",
    "validate_expected_answer_shapes",
    "validate_hard_query_registry",
    "validate_scorecard",
]
