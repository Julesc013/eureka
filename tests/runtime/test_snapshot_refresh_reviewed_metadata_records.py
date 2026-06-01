from __future__ import annotations

import unittest

from runtime.snapshots import run_snapshot_refresh_03


class SnapshotRefreshReviewedMetadataRecordsTests(unittest.TestCase):
    def test_reviewed_metadata_record_section_is_limited_claim(self) -> None:
        result = run_snapshot_refresh_03(from_local_apply_live_metadata_examples=True)
        section = result["reviewed_metadata_record_section"]

        self.assertEqual(1, section["reviewed_metadata_record_count"])
        self.assertEqual("metadata_record_only", section["limited_claim_scope"])
        self.assertFalse(section["artifact_verified"])
        self.assertFalse(section["verified_download_claim"])
        self.assertFalse(section["malware_clean_claim"])
        self.assertFalse(section["rights_clearance_claim"])

        record = section["records"][0]
        self.assertEqual("reviewed_metadata_record", record["record_type"])
        self.assertEqual("source_lead", record["public_search_status"])
        self.assertFalse(record["artifact_verified"])
        self.assertFalse(record["verified_download_claim"])
        self.assertFalse(record["malware_clean_claim"])
        self.assertFalse(record["rights_clearance_claim"])

    def test_public_search_card_is_not_verified_artifact(self) -> None:
        result = run_snapshot_refresh_03(from_local_apply_live_metadata_examples=True)
        cards = [
            card
            for card in result["public_search_view_model_projection"]["result_cards"]
            if card["object_type"] == "reviewed_metadata_record_limited"
        ]

        self.assertEqual(1, len(cards))
        self.assertEqual("source_lead", cards[0]["status"])
        self.assertFalse(cards[0]["artifact_verified"])
        self.assertFalse(cards[0]["verified_download_claim"])


if __name__ == "__main__":
    unittest.main()
