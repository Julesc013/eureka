from __future__ import annotations

import unittest

from evals.hard_queries.seed_corpus.loader import PUBLIC_ALPHA_TARGETS
from evals.hard_queries.reviewed_seed_corpus.batch_02 import (
    load_cumulative_corpus_counts,
    load_public_alpha_gate,
    load_review_decision_backed_outcomes,
    reviewed_corpus_counts,
    validate_public_alpha_gate,
)


class ReviewedCorpusBatchTwoGateTests(unittest.TestCase):
    def test_public_alpha_gate_remains_failed_and_counted(self) -> None:
        gate = load_public_alpha_gate()
        counts = load_cumulative_corpus_counts()

        self.assertEqual(validate_public_alpha_gate(gate, counts), ())
        self.assertEqual(gate["public_alpha_corpus_gate"], "FAIL_INSUFFICIENT_REVIEWED_CORPUS")
        self.assertEqual(gate["counts"]["reviewed_count"], 3)
        self.assertEqual(gate["counts"]["review_decision_backed_count"], 18)
        self.assertEqual(gate["counts"]["need_count"], 5)
        self.assertEqual(gate["counts"]["near_miss_count"], 3)
        self.assertEqual(gate["counts"]["superseded_count"], 3)
        self.assertEqual(gate["counts"]["blocked_for_user_details_count"], 1)

    def test_gate_reports_target_gaps_and_validation_pivot(self) -> None:
        gate = load_public_alpha_gate()

        self.assertEqual(gate["minimum_public_alpha_targets"], PUBLIC_ALPHA_TARGETS)
        self.assertEqual(gate["minimum_gap_to_alpha"]["reviewed_records"], 197)
        self.assertEqual(gate["next_primary_task"], "SOURCE-SNAPSHOT-BASELINE-CLOSEOUT-01")
        self.assertEqual(gate["secondary_followup"], "USER-HARDWARE-DETAILS-00")
        self.assertTrue(gate["full_discovery_required_for_release"])

    def test_batch_two_added_counts_do_not_overstate_truth(self) -> None:
        computed = reviewed_corpus_counts(load_review_decision_backed_outcomes())

        self.assertEqual(computed["reviewed"], 1)
        self.assertEqual(computed["review_decision_backed"], 12)
        self.assertEqual(computed["need"], 5)
        self.assertEqual(computed["near_miss"], 3)
        self.assertEqual(computed["superseded"], 3)
        self.assertEqual(computed["request_more_evidence"], 4)

    def test_truth_boundary_flags_are_false(self) -> None:
        gate = load_public_alpha_gate()

        for key, value in gate["truth_boundary"].items():
            self.assertFalse(value, key)


if __name__ == "__main__":
    unittest.main()
