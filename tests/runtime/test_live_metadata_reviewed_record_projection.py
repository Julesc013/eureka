from __future__ import annotations

import unittest

from runtime.local_apply import run_local_apply_live_metadata_previews


class LiveMetadataReviewedRecordProjectionTests(unittest.TestCase):
    def test_records_remain_limited_metadata_or_source_lead_claims(self) -> None:
        result = run_local_apply_live_metadata_previews(
            from_live_metadata_review_examples=True,
            use_temp_instance=True,
        )
        metadata_records = result["reviewed_metadata_records"]
        source_leads = result["reviewed_source_leads"]

        self.assertEqual(metadata_records[0]["record_type"], "reviewed_metadata_record")
        self.assertEqual(metadata_records[0]["reviewed_claim_scope"], "metadata_record_only")
        for record in metadata_records + source_leads:
            self.assertFalse(record["verified_download_claim"])
            self.assertFalse(record["malware_clean_claim"])
            self.assertFalse(record["rights_clearance_claim"])
            self.assertFalse(record["artifact_verified"])


if __name__ == "__main__":
    unittest.main()
