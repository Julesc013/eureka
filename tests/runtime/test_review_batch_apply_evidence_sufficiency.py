from __future__ import annotations

import unittest

from runtime.local_apply import assess_review_batch_evidence_sufficiency, load_review_batch_apply_inputs


class ReviewBatchApplyEvidenceSufficiencyTests(unittest.TestCase):
    def test_selected_candidate_has_sufficient_limited_evidence(self) -> None:
        inputs = load_review_batch_apply_inputs()
        by_id = {row["candidate_id"]: row for row in inputs["candidates"]}

        result = assess_review_batch_evidence_sufficiency(
            by_id["seed_frontier_media_frontier_media_q01_candidate"]
        )

        self.assertGreaterEqual(result["sufficiency_score"], 0.68)
        self.assertTrue(result["eligible_for_limited_apply"])


if __name__ == "__main__":
    unittest.main()
