from __future__ import annotations

import unittest

from evals.hard_queries import REQUIRED_HARD_QUERY_IDS
from evals.hard_queries.reviewed_seed_corpus.batch_01 import (
    load_batch_manifest,
    load_query_coverage,
    load_review_decision_backed_outcomes,
    load_reviewed_seed_records,
    outcome_records,
    query_coverage_records,
    read_batch_text,
    reviewed_seed_record_records,
    validate_batch_manifest,
    validate_query_coverage,
    validate_review_decision_backed_outcomes,
    validate_reviewed_seed_records,
)


class ReviewedCorpusSeedBatchOneTests(unittest.TestCase):
    def test_batch_manifest_and_required_outputs_validate(self) -> None:
        manifest = load_batch_manifest()

        self.assertEqual(validate_batch_manifest(manifest), ())
        self.assertEqual(manifest["public_alpha_corpus_gate"], "FAIL_INSUFFICIENT_REVIEWED_CORPUS")
        self.assertEqual(manifest["recommended_next_task"], "MANUAL-OBSERVATION-BATCH-01")
        for value in manifest["truth_boundary"].values():
            self.assertFalse(value)

    def test_outcomes_cover_all_hard_queries_and_validate(self) -> None:
        payload = load_review_decision_backed_outcomes()
        outcomes = outcome_records(payload)

        self.assertEqual(validate_review_decision_backed_outcomes(payload), ())
        self.assertEqual(len(outcomes), 6)
        self.assertEqual({item["hard_query_id"] for item in outcomes}, set(REQUIRED_HARD_QUERY_IDS))
        for outcome in outcomes:
            self.assertTrue(outcome["review_decision_id"])
            self.assertTrue(outcome["review_event_id"])
            for value in outcome["truth_boundary"].values():
                self.assertFalse(value)

    def test_only_promote_decisions_become_reviewed_records(self) -> None:
        outcomes = outcome_records(load_review_decision_backed_outcomes())
        records = reviewed_seed_record_records(load_reviewed_seed_records())

        self.assertEqual(validate_reviewed_seed_records(load_reviewed_seed_records(), load_review_decision_backed_outcomes()), ())
        self.assertEqual(len(records), 2)
        reviewed_ids = {record["reviewed_seed_record_id"] for record in records}
        for outcome in outcomes:
            if outcome["decision"] == "promote":
                self.assertEqual(outcome["outcome_status"], "verified")
                self.assertTrue(outcome["counts_as_reviewed"])
                self.assertIn(outcome["reviewed_seed_record_id"], reviewed_ids)
            else:
                self.assertFalse(outcome["counts_as_reviewed"])
                self.assertFalse(outcome["reviewed_seed_record_created"])
                self.assertIsNone(outcome["reviewed_seed_record_id"])
                self.assertNotEqual(outcome["outcome_status"], "verified")

    def test_non_promoted_outcomes_preserve_need_and_near_miss_states(self) -> None:
        outcomes_by_query = {item["hard_query_id"]: item for item in outcome_records(load_review_decision_backed_outcomes())}

        self.assertEqual(outcomes_by_query["hq_driver_win98"]["outcome_status"], "need")
        self.assertTrue(outcomes_by_query["hq_driver_win98"]["blocked_for_user_details"])
        self.assertEqual(outcomes_by_query["hq_blue_ftp_client_xp"]["outcome_status"], "near_miss")
        self.assertEqual(outcomes_by_query["hq_sound_blaster_ct1740_manual"]["outcome_status"], "need")
        self.assertEqual(outcomes_by_query["hq_ray_tracing_1994_magazine"]["outcome_status"], "need")

    def test_query_coverage_matches_outcomes_and_stays_not_ready(self) -> None:
        coverage = load_query_coverage()

        self.assertEqual(validate_query_coverage(coverage, load_review_decision_backed_outcomes()), ())
        self.assertEqual(len(query_coverage_records(coverage)), 6)
        for item in query_coverage_records(coverage):
            self.assertEqual(item["public_alpha_readiness"], "not_ready")
            self.assertTrue(item["next_required_action"])

    def test_gap_queues_contain_expected_blockers(self) -> None:
        evidence_gaps = read_batch_text("evidence_gap_queue.yml")
        user_blocks = read_batch_text("blocked_for_user_details.yml")
        reviewed_backlog = read_batch_text("reviewed_record_backlog.yml")

        self.assertIn("gap_hq_driver_win98_user_hardware", evidence_gaps)
        self.assertIn("hardware_vendor", user_blocks)
        self.assertIn("hq_sound_blaster_ct1740_manual", reviewed_backlog)


if __name__ == "__main__":
    unittest.main()
