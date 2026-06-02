from __future__ import annotations

import unittest

from runtime.local_apply import run_review_batch_apply_next


class ReviewBatchApplyNextTests(unittest.TestCase):
    def test_temp_apply_grows_limited_reviewed_corpus(self) -> None:
        result = run_review_batch_apply_next(from_examples=True, use_temp_instance=True)

        self.assertEqual(result["status"], "pass")
        self.assertEqual(result["total_candidates_considered"], 68)
        self.assertEqual(result["eligible_apply_count"], 12)
        self.assertEqual(result["limited_reviewed_metadata_records_created"], 4)
        self.assertEqual(result["limited_reviewed_source_leads_created"], 4)
        self.assertEqual(result["reviewed_record_delta_count"], 8)
        self.assertEqual(result["non_applied_count"], 60)


if __name__ == "__main__":
    unittest.main()
