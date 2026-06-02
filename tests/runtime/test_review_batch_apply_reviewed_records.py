from __future__ import annotations

import unittest

from runtime.local_apply import run_review_batch_apply_next


class ReviewBatchApplyReviewedRecordsTests(unittest.TestCase):
    def test_limited_reviewed_records_have_false_prohibited_claims(self) -> None:
        result = run_review_batch_apply_next(from_examples=True, use_temp_instance=True)
        records = result["limited_reviewed_metadata_records"] + result["limited_reviewed_source_leads"]

        self.assertEqual(len(records), 8)
        for record in records:
            self.assertFalse(record["artifact_verified"])
            self.assertFalse(record["verified_download_claim"])
            self.assertFalse(record["malware_clean_claim"])
            self.assertFalse(record["rights_clearance_claim"])
            self.assertFalse(record["compatibility_guarantee_claim"])


if __name__ == "__main__":
    unittest.main()
