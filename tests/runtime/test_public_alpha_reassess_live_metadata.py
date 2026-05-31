from __future__ import annotations

import unittest

from runtime.public_alpha import run_public_alpha_reassess_01


class PublicAlphaReassessLiveMetadataTests(unittest.TestCase):
    def test_live_metadata_metrics_remain_review_only(self) -> None:
        result = run_public_alpha_reassess_01(from_live_metadata_refresh_examples=True)

        self.assertEqual("PUBLIC-ALPHA-REASSESS-01", result["task"])
        self.assertEqual(1, result["reviewed_record_count"])
        self.assertEqual(28, result["fixture_candidate_count"])
        self.assertEqual(8, result["live_metadata_candidate_count"])
        self.assertEqual(36, result["total_candidate_count"])
        self.assertFalse(result["launch_recommended"])
        self.assertTrue(result["demo_mode_recommended"])
        self.assertTrue(result["internal_review_recommended"])
        self.assertTrue(result["needs_live_candidate_review"])
        self.assertTrue(result["needs_snapshot_refresh_after_review"])

    def test_live_metadata_candidates_do_not_count_as_reviewed(self) -> None:
        result = run_public_alpha_reassess_01(from_live_metadata_refresh_examples=True)

        self.assertEqual(8, result["live_metadata_candidate_usefulness"]["review_only_candidate_count"])
        self.assertFalse(result["candidate_usefulness"]["live_metadata_candidates_counted_as_reviewed"])
        self.assertFalse(result["live_metadata_candidate_usefulness"]["accepted_truth"])
        self.assertFalse(result["live_metadata_candidate_usefulness"]["raw_response_included"])
        self.assertEqual(1, result["metrics"]["reviewed_record_count"])


if __name__ == "__main__":
    unittest.main()

