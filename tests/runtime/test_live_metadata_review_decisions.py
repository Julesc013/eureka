from __future__ import annotations

import unittest

from runtime.review.live_metadata import run_live_metadata_candidate_review


class LiveMetadataReviewDecisionTests(unittest.TestCase):
    def test_decision_branches_are_recorded(self) -> None:
        result = run_live_metadata_candidate_review(from_live_metadata_examples=True)
        decisions = {item["candidate_id"]: item for item in result["review_decisions"]}

        self.assertEqual(
            "promote_reviewed_source_lead_preview",
            decisions["live_metadata_pilot_frontier_media_q01_01"]["review_decision"],
        )
        self.assertEqual(
            "promote_reviewed_metadata_record_preview",
            decisions["live_metadata_pilot_legacy_software_q01_05"]["review_decision"],
        )
        self.assertEqual("mark_useful_lead", decisions["live_metadata_pilot_frontier_media_q03_02"]["review_decision"])
        self.assertEqual("duplicate", decisions["live_metadata_pilot_frontier_media_q05_03"]["review_decision"])
        self.assertEqual("needs_more_evidence", decisions["live_metadata_pilot_legacy_software_q06_08"]["review_decision"])

    def test_live_candidates_are_not_counted_as_accepted_truth(self) -> None:
        result = run_live_metadata_candidate_review(from_live_metadata_examples=True)

        for decision in result["review_decisions"]:
            self.assertFalse(decision["accepted_truth"])
            self.assertFalse(decision["reviewed_artifact_claim"])
            self.assertFalse(decision["download_claim"])


if __name__ == "__main__":
    unittest.main()
