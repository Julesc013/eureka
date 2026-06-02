from __future__ import annotations

import unittest

from runtime.snapshots import run_snapshot_refresh_06


class SnapshotRefreshLimitedReviewedRecordsTests(unittest.TestCase):
    def test_limited_reviewed_records_derive_total_projection_count(self) -> None:
        result = run_snapshot_refresh_06(from_review_batch_apply_examples=True)
        metadata = result["limited_reviewed_metadata_section"]
        source_leads = result["limited_reviewed_source_lead_section"]

        self.assertEqual(4, result["new_limited_reviewed_metadata_records"])
        self.assertEqual(4, result["new_limited_reviewed_source_leads"])
        self.assertEqual(8, result["new_reviewed_record_delta_count"])
        self.assertEqual(12, result["total_limited_reviewed_record_projection_count"])
        self.assertEqual(5, metadata["limited_reviewed_metadata_record_count"])
        self.assertEqual(6, source_leads["limited_reviewed_source_lead_count"])

        for section in (metadata, source_leads):
            self.assertFalse(section["artifact_verified"])
            self.assertFalse(section["verified_download_claim"])
            self.assertFalse(section["malware_clean_claim"])
            self.assertFalse(section["rights_clearance_claim"])
            for record in section["records"]:
                self.assertFalse(record["artifact_verified"])
                self.assertFalse(record["verified_download_claim"])
                self.assertFalse(record["malware_clean_claim"])
                self.assertFalse(record["rights_clearance_claim"])


if __name__ == "__main__":
    unittest.main()
