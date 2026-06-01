from __future__ import annotations

import unittest

from runtime.snapshots import run_snapshot_refresh_03


class SnapshotRefreshReviewedSourceLeadTests(unittest.TestCase):
    def test_reviewed_source_lead_section_is_limited_claim(self) -> None:
        result = run_snapshot_refresh_03(from_local_apply_live_metadata_examples=True)
        section = result["reviewed_source_lead_section"]

        self.assertEqual(2, section["reviewed_source_lead_count"])
        self.assertEqual("source_lead_only", section["limited_claim_scope"])
        self.assertFalse(section["artifact_verified"])
        self.assertFalse(section["verified_download_claim"])
        self.assertFalse(section["malware_clean_claim"])
        self.assertFalse(section["rights_clearance_claim"])

        for record in section["records"]:
            self.assertEqual("reviewed_source_lead", record["record_type"])
            self.assertEqual("source_lead", record["public_search_status"])
            self.assertFalse(record["artifact_verified"])
            self.assertFalse(record["verified_download_claim"])
            self.assertFalse(record["malware_clean_claim"])
            self.assertFalse(record["rights_clearance_claim"])

    def test_relay_projection_counts_limited_records(self) -> None:
        result = run_snapshot_refresh_03(from_local_apply_live_metadata_examples=True)
        sections = result["refreshed_relay_projection"]["sections"]

        self.assertEqual(1, sections["existing_reviewed_records"])
        self.assertEqual(1, sections["reviewed_metadata_records_from_local_apply"])
        self.assertEqual(2, sections["reviewed_source_leads_from_local_apply"])
        self.assertEqual(4, sections["total_limited_reviewed_record_projection_count"])


if __name__ == "__main__":
    unittest.main()
