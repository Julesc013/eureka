from __future__ import annotations

import unittest

from evals.hard_queries.human_reviews.batch_00 import (
    load_corpus_gate_update,
    load_record_materialization_backlog,
    load_review_decisions,
    validate_corpus_gate_update,
    validate_record_materialization_backlog,
)


class HumanReviewCorpusGateTests(unittest.TestCase):
    def test_corpus_gate_remains_failed_but_counts_reviewed_seed_records(self) -> None:
        decisions = load_review_decisions()
        gate = load_corpus_gate_update()

        self.assertEqual(validate_corpus_gate_update(gate, decisions), ())
        self.assertEqual(gate["public_alpha_corpus_gate"], "FAIL_INSUFFICIENT_REVIEWED_CORPUS")
        self.assertEqual(gate["counts"]["reviewed_count"], 2)
        self.assertEqual(gate["counts"]["review_decision_backed_count"], 6)
        self.assertEqual(gate["counts"]["hard_queries_with_review_decision"], 6)
        self.assertEqual(gate["counts"]["hard_queries_with_promoted_or_reviewed_item"], 2)
        self.assertEqual(gate["recommended_next_task"], "REVIEWED-CORPUS-SEED-BATCH-01")

    def test_corpus_gate_truth_boundary_flags_are_false(self) -> None:
        truth = load_corpus_gate_update()["truth_boundary"]

        for key, value in truth.items():
            self.assertFalse(value, key)

    def test_materialization_backlog_tracks_non_promoted_items(self) -> None:
        decisions = load_review_decisions()
        backlog = load_record_materialization_backlog()

        self.assertEqual(validate_record_materialization_backlog(backlog, decisions), ())
        self.assertEqual(len(backlog["record_materialization_backlog"]), 4)
        for item in backlog["record_materialization_backlog"]:
            self.assertFalse(item["reviewed_seed_record_created"])
            self.assertIn("next_required_action", item)


if __name__ == "__main__":
    unittest.main()
