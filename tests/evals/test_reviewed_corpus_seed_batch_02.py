from __future__ import annotations

import unittest

from evals.hard_queries import REQUIRED_HARD_QUERY_IDS
from evals.hard_queries.reviewed_seed_corpus.batch_02 import (
    load_cumulative_corpus_counts,
    load_query_coverage,
    load_review_decision_backed_outcomes,
    load_reviewed_seed_records,
    outcome_records,
    query_coverage_records,
    read_batch_text,
    reviewed_seed_record_records,
    validate_cumulative_corpus_counts,
    validate_query_coverage,
    validate_required_outputs,
    validate_review_decision_backed_outcomes,
    validate_reviewed_seed_records,
)


class ReviewedCorpusSeedBatchTwoTests(unittest.TestCase):
    def test_required_outputs_exist_and_validate(self) -> None:
        self.assertEqual(validate_required_outputs(), ())

    def test_outcomes_cover_batch_one_human_review_decisions(self) -> None:
        payload = load_review_decision_backed_outcomes()
        outcomes = outcome_records(payload)

        self.assertEqual(validate_review_decision_backed_outcomes(payload), ())
        self.assertEqual(len(outcomes), 12)
        self.assertEqual({item["hard_query_id"] for item in outcomes}, set(REQUIRED_HARD_QUERY_IDS))
        for outcome in outcomes:
            self.assertTrue(outcome["review_decision_id"])
            self.assertTrue(outcome["review_event_id"])
            for key, value in outcome["truth_boundary"].items():
                self.assertFalse(value, key)

    def test_only_promote_decision_adds_a_new_reviewed_record(self) -> None:
        outcomes = outcome_records(load_review_decision_backed_outcomes())
        records = reviewed_seed_record_records(load_reviewed_seed_records())
        new_records = [
            record
            for record in records
            if record["reviewed_seed_record_id"] == "reviewed_seed_b01_hq_windows_7_7zip_support_fact"
        ]

        self.assertEqual(validate_reviewed_seed_records(load_reviewed_seed_records()), ())
        self.assertEqual(len(records), 3)
        self.assertEqual(len(new_records), 1)
        self.assertEqual(new_records[0]["review_decision_id"], "hrd_b01_hq_windows_7_7zip_promote")
        for outcome in outcomes:
            if outcome["decision"] == "promote":
                self.assertEqual(outcome["outcome_status"], "verified")
                self.assertTrue(outcome["counts_as_reviewed"])
                self.assertEqual(outcome["reviewed_seed_record_id"], new_records[0]["reviewed_seed_record_id"])
            else:
                self.assertFalse(outcome["counts_as_reviewed"])
                self.assertFalse(outcome["reviewed_seed_record_created"])
                self.assertNotEqual(outcome["outcome_status"], "verified")

    def test_cumulative_counts_match_batch_outcomes(self) -> None:
        counts = load_cumulative_corpus_counts()

        self.assertEqual(validate_cumulative_corpus_counts(counts, load_review_decision_backed_outcomes()), ())
        self.assertEqual(counts["batch_02_added_counts"]["reviewed_count"], 1)
        self.assertEqual(counts["batch_02_added_counts"]["review_decision_backed_count"], 12)
        self.assertEqual(counts["cumulative_counts"]["reviewed_count"], 3)
        self.assertEqual(counts["cumulative_counts"]["review_decision_backed_count"], 18)
        self.assertEqual(counts["cumulative_counts"]["blocked_for_user_details_count"], 1)

    def test_query_coverage_stays_not_ready_for_all_hard_queries(self) -> None:
        coverage = load_query_coverage()

        self.assertEqual(validate_query_coverage(coverage), ())
        self.assertEqual(len(query_coverage_records(coverage)), 6)
        for item in query_coverage_records(coverage):
            self.assertEqual(item["readiness"], "not_ready")
            self.assertTrue(item["next_action"])

    def test_gap_and_followup_queues_preserve_known_blockers(self) -> None:
        evidence_gaps = read_batch_text("evidence_gap_queue.yml")
        manual_followups = read_batch_text("manual_followups.yml")
        user_blocks = read_batch_text("blocked_for_user_details.yml")
        backlog = read_batch_text("reviewed_record_backlog.yml")

        self.assertIn("gap_b02_win98_hardware_identity", evidence_gaps)
        self.assertIn("hardware_vendor", user_blocks)
        self.assertIn("followup_b02_collect_byte_issue_metadata", manual_followups)
        self.assertIn("backlog_b02_ct1740_exact_manual", backlog)


if __name__ == "__main__":
    unittest.main()
