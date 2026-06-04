from __future__ import annotations

import unittest

from evals.hard_queries import (
    REQUIRED_HARD_QUERY_IDS,
    SYNTHETIC_FIXTURE_DISCLAIMER,
    evaluate_fixture_case,
    evaluate_fixture_suite,
    fixture_cases,
    load_expected_answer_shapes,
    load_hard_query_registry,
    load_scorecard,
    validate_expected_answer_shapes,
    validate_hard_query_registry,
    validate_scorecard,
)


class HardQueryEvalTests(unittest.TestCase):
    def test_hard_query_registry_loads_and_validates(self) -> None:
        registry = load_hard_query_registry()
        errors = validate_hard_query_registry(registry)
        query_ids = [query["query_id"] for query in registry["queries"]]

        self.assertEqual(errors, ())
        self.assertEqual(set(query_ids), set(REQUIRED_HARD_QUERY_IDS))
        self.assertEqual(len(query_ids), 6)
        self.assertEqual(
            {query["query_text"] for query in registry["queries"]},
            {
                "Windows 7 apps",
                "driver for Win98",
                "old blue FTP client for XP",
                "manual for Sound Blaster CT1740",
                "latest Firefox before XP support ended",
                "article about ray tracing in a 1994 magazine",
            },
        )

    def test_expected_answer_shapes_and_scorecard_validate(self) -> None:
        shapes = load_expected_answer_shapes()
        scorecard = load_scorecard()

        self.assertEqual(validate_expected_answer_shapes(shapes), ())
        self.assertEqual(validate_scorecard(scorecard), ())
        self.assertEqual(
            [item["dimension"] for item in scorecard["dimensions"]],
            [
                "status_honesty",
                "smallest_useful_unit",
                "evidence_or_uncertainty_explanation",
                "candidate_need_or_absence_quality",
                "result_reason_quality",
                "public_action_policy_compliance",
                "renderer_profile_coverage",
                "surface_consistency",
                "no_truth_boundary_bypass",
                "no_live_source_fanout",
            ],
        )

    def test_fixture_cases_cover_required_statuses_without_truth_claims(self) -> None:
        fixtures = fixture_cases()
        statuses = {fixture["expected_status"] for fixture in fixtures}

        self.assertEqual({fixture["query_id"] for fixture in fixtures}, set(REQUIRED_HARD_QUERY_IDS))
        self.assertTrue({"candidate", "need", "near_miss", "policy_blocked", "unavailable"}.issubset(statuses))
        for fixture in fixtures:
            self.assertEqual(fixture["fixture_disclaimer"], SYNTHETIC_FIXTURE_DISCLAIMER)
            self.assertFalse(fixture["live_source_calls"])
            self.assertFalse(fixture["reviewed_record_created"])
            self.assertFalse(fixture["reviewed_index_mutated"])
            self.assertFalse(fixture["public_index_mutated"])
            self.assertFalse(fixture["master_index_mutated"])
            fallback = fixture["fallback_summary"]
            self.assertFalse(fallback["verified"])
            self.assertFalse(fallback["accepted_truth"])
            self.assertNotEqual(fixture["expected_status"], "verified")

    def test_scorecard_computes_deterministic_scores(self) -> None:
        first = evaluate_fixture_suite()
        second = evaluate_fixture_suite()

        self.assertEqual(first, second)
        self.assertTrue(first["all_pass_gates_met"])
        self.assertEqual(first["fixture_count"], 6)
        for result in first["results"]:
            self.assertTrue(result["pass_gates_met"], result["query_id"])
            self.assertEqual(result["scores"]["status_honesty"], 3)
            self.assertEqual(result["scores"]["public_action_policy_compliance"], 3)
            self.assertEqual(result["scores"]["no_truth_boundary_bypass"], 3)
            self.assertEqual(result["scores"]["no_live_source_fanout"], 3)

    def test_individual_fixtures_do_not_self_promote(self) -> None:
        for fixture in fixture_cases():
            with self.subTest(query_id=fixture["query_id"]):
                result = evaluate_fixture_case(fixture)

                self.assertNotEqual(result["expected_status"], "verified")
                self.assertFalse(result["reviewed_record_created"])
                self.assertFalse(result["reviewed_index_mutated"])
                self.assertFalse(result["public_index_mutated"])
                self.assertFalse(result["master_index_mutated"])
                self.assertFalse(result["live_source_calls"])


if __name__ == "__main__":
    unittest.main()
