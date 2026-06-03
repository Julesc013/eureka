from __future__ import annotations

import unittest

from runtime.public_alpha import run_public_alpha_reassess_06


class PublicAlphaReassessReviewBatchApplyTests(unittest.TestCase):
    def test_review_batch_apply_metrics_and_decision(self) -> None:
        result = run_public_alpha_reassess_06(from_review_batch_apply_refresh_examples=True)

        self.assertEqual("pass", result["status"])
        self.assertEqual(4, result["previous_total_limited_reviewed_record_projection_count"])
        self.assertEqual(8, result["new_reviewed_record_delta_count"])
        self.assertEqual(12, result["total_limited_reviewed_record_projection_count"])
        self.assertEqual(2, result["reviewed_known_need_count"])
        self.assertEqual(2, result["reviewed_bounded_absence_count"])
        self.assertEqual(60, result["candidate_count_after_apply"])
        self.assertEqual(4, result["domain_count"])
        self.assertEqual(8, result["public_ux_routes_count"])
        self.assertEqual(8, result["result_card_states_count"])
        self.assertTrue(result["public_search_ux_mvp_implemented"])
        self.assertTrue(result["reviewed_corpus_growth_confirmed"])
        self.assertFalse(result["reviewed_record_threshold_met"])
        self.assertFalse(result["launch_recommended"])
        self.assertTrue(result["demo_mode_recommended"])
        self.assertTrue(result["internal_review_recommended"])

    def test_review_batch_apply_records_are_not_artifacts(self) -> None:
        result = run_public_alpha_reassess_06(from_review_batch_apply_refresh_examples=True)
        limited = result["limited_reviewed_record_usefulness"]

        self.assertFalse(limited["limited_reviewed_records_are_verified_artifacts"])
        self.assertFalse(limited["artifact_verified"])
        self.assertFalse(limited["verified_download_claim"])
        self.assertFalse(limited["malware_clean_claim"])
        self.assertFalse(limited["rights_clearance_claim"])


if __name__ == "__main__":
    unittest.main()
