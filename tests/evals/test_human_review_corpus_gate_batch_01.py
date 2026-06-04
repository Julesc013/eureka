from __future__ import annotations

import unittest

from evals.hard_queries.human_reviews.batch_01 import (
    load_corpus_gate_update,
    load_query_coverage_update,
    load_record_materialization_backlog,
    load_review_decisions,
    query_coverage_records,
    validate_corpus_gate_update,
    validate_query_coverage_update,
    validate_record_materialization_backlog,
)


class HumanReviewBatchOneCorpusGateTests(unittest.TestCase):
    def test_corpus_gate_remains_failed_but_counts_batch_review(self) -> None:
        decisions = load_review_decisions()
        gate = load_corpus_gate_update()

        self.assertEqual(validate_corpus_gate_update(gate, decisions), ())
        self.assertEqual(gate["public_alpha_corpus_gate"], "FAIL_INSUFFICIENT_REVIEWED_CORPUS")
        self.assertEqual(gate["batch_counts"]["reviewed_count"], 1)
        self.assertEqual(gate["batch_counts"]["review_decision_backed_count"], 12)
        self.assertEqual(gate["batch_counts"]["superseded_count"], 3)
        self.assertEqual(gate["cumulative_counts_after_batch"]["reviewed_count"], 3)
        self.assertEqual(gate["recommended_next_task"], "REVIEWED-CORPUS-SEED-BATCH-02")

    def test_corpus_gate_truth_boundary_flags_are_false(self) -> None:
        truth = load_corpus_gate_update()["truth_boundary"]

        for key, value in truth.items():
            self.assertFalse(value, key)

    def test_query_coverage_records_all_six_queries(self) -> None:
        coverage = load_query_coverage_update()

        self.assertEqual(validate_query_coverage_update(coverage), ())
        records = query_coverage_records(coverage)
        self.assertEqual(len(records), 6)
        by_query = {item["hard_query_id"]: item for item in records}
        self.assertEqual(by_query["hq_windows_7_apps"]["best_current_status"], "verified")
        self.assertEqual(by_query["hq_driver_win98"]["best_current_status"], "need")
        self.assertEqual(by_query["hq_blue_ftp_client_xp"]["best_current_status"], "near_miss")
        self.assertEqual(by_query["hq_firefox_last_xp"]["best_current_status"], "verified")
        for item in records:
            self.assertEqual(item["public_alpha_readiness"], "not_ready")
            self.assertTrue(item["next_required_action"])

    def test_materialization_backlog_tracks_non_promote_decisions(self) -> None:
        decisions = load_review_decisions()
        backlog = load_record_materialization_backlog()

        self.assertEqual(validate_record_materialization_backlog(backlog, decisions), ())
        self.assertEqual(len(backlog["record_materialization_backlog"]), 11)
        for item in backlog["record_materialization_backlog"]:
            self.assertFalse(item["reviewed_seed_record_created"])
            self.assertIn("next_required_action", item)


if __name__ == "__main__":
    unittest.main()
