from __future__ import annotations

import unittest

from runtime.local_apply import evaluate_review_batch_apply_eligibility, load_review_batch_apply_inputs


class ReviewBatchApplyEligibilityTests(unittest.TestCase):
    def test_eligibility_is_conservative(self) -> None:
        inputs = load_review_batch_apply_inputs()
        rows = evaluate_review_batch_apply_eligibility(inputs["candidates"], inputs["review_packets"], [])

        eligible = [row for row in rows if row["eligible"]]

        self.assertEqual(len(rows), 68)
        self.assertEqual(len(eligible), 8)
        self.assertEqual(
            {row["record_kind"] for row in eligible},
            {"limited_reviewed_metadata_record", "limited_reviewed_source_lead"},
        )


if __name__ == "__main__":
    unittest.main()
