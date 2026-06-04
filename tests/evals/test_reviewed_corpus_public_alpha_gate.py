from __future__ import annotations

import unittest

from evals.hard_queries.reviewed_seed_corpus.batch_01 import (
    PUBLIC_ALPHA_TARGETS,
    load_family_index,
    load_family_public_alpha_gate,
    load_public_alpha_gate,
    load_review_decision_backed_outcomes,
    reviewed_corpus_counts,
    validate_public_alpha_gate,
)


class ReviewedCorpusPublicAlphaGateTests(unittest.TestCase):
    def test_public_alpha_gate_counts_match_outcomes(self) -> None:
        outcomes = load_review_decision_backed_outcomes()
        gate = load_public_alpha_gate()

        self.assertEqual(validate_public_alpha_gate(gate, outcomes), ())
        self.assertEqual(reviewed_corpus_counts(outcomes)["reviewed"], 2)
        self.assertEqual(gate["counts"]["review_decision_backed_count"], 6)
        self.assertEqual(gate["counts"]["need_count"], 3)
        self.assertEqual(gate["counts"]["near_miss_count"], 1)
        self.assertEqual(gate["counts"]["blocked_for_user_details_count"], 1)

    def test_gate_remains_failed_and_reports_target_gaps(self) -> None:
        gate = load_public_alpha_gate()

        self.assertEqual(gate["public_alpha_corpus_gate"], "FAIL_INSUFFICIENT_REVIEWED_CORPUS")
        self.assertEqual(gate["minimum_public_alpha_targets"], PUBLIC_ALPHA_TARGETS)
        self.assertEqual(gate["minimum_gap_to_alpha"]["reviewed_records"], 198)
        self.assertEqual(gate["recommended_next_task"], "MANUAL-OBSERVATION-BATCH-01")
        self.assertEqual(gate["secondary_followup"], "USER-HARDWARE-DETAILS-00")

    def test_family_index_points_to_current_batch(self) -> None:
        index = load_family_index()
        family_gate = load_family_public_alpha_gate()

        self.assertEqual(index["current_batch"], "batch_01")
        self.assertEqual(index["public_alpha_corpus_gate"], "FAIL_INSUFFICIENT_REVIEWED_CORPUS")
        self.assertEqual(family_gate["current_batch"], "batch_01")
        self.assertEqual(family_gate["counts"]["reviewed_count"], 2)

    def test_truth_boundary_flags_are_false(self) -> None:
        gate = load_public_alpha_gate()

        for key, value in gate["truth_boundary"].items():
            self.assertFalse(value, key)


if __name__ == "__main__":
    unittest.main()
