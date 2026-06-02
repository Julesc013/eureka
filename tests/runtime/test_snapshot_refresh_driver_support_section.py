from __future__ import annotations

import unittest

from runtime.snapshots import run_snapshot_refresh_04


class SnapshotRefreshDriverSupportSectionTests(unittest.TestCase):
    def test_driver_support_section_projects_review_only_candidates(self) -> None:
        result = run_snapshot_refresh_04(from_manuals_driver_examples=True)
        section = result["driver_support_candidate_section"]

        self.assertEqual("pass", result["status"])
        self.assertEqual("snapshot_driver_support_candidate_section.v0", section["schema_version"])
        self.assertEqual("driver_support_media", section["domain_id"])
        self.assertEqual(16, section["candidate_count"])
        self.assertFalse(section["accepted_truth"])
        self.assertFalse(section["download_performed"])
        self.assertFalse(section["file_fetch_performed"])
        self.assertFalse(section["install_execution_enabled"])
        self.assertFalse(section["malware_clean_claim_created"])
        self.assertFalse(section["compatibility_guarantee_created"])
        self.assertFalse(section["rights_clearance_claim_created"])

        for candidate in section["candidates"]:
            self.assertEqual("candidate", candidate["public_search_status"])
            self.assertIsNone(candidate["reviewed_record_ref"])
            self.assertFalse(candidate["accepted_truth"])
            self.assertFalse(candidate["download_performed"])
            self.assertFalse(candidate["file_fetch_performed"])
            self.assertFalse(candidate["install_execution_enabled"])
            self.assertFalse(candidate["malware_clean_claim_created"])
            self.assertFalse(candidate["compatibility_guarantee_created"])
            self.assertFalse(candidate["rights_clearance_claim_created"])

    def test_driver_support_public_cards_are_not_verified_drivers(self) -> None:
        result = run_snapshot_refresh_04(from_manuals_driver_examples=True)
        cards = [
            card
            for card in result["public_search_view_model_projection"]["result_cards"]
            if card["object_type"] == "driver_support_candidate"
        ]

        self.assertEqual(16, len(cards))
        for card in cards:
            self.assertEqual("candidate", card["status"])
            self.assertFalse(card["accepted_truth"])
            self.assertFalse(card["artifact_verified"])
            self.assertFalse(card["verified_download_claim"])
            self.assertFalse(card["malware_clean_claim"])
            self.assertFalse(card["compatibility_guarantee"])
            self.assertFalse(card["rights_clearance_claim"])
            self.assertFalse(card["file_fetch_performed"])
            self.assertFalse(card["install_execution_enabled"])


if __name__ == "__main__":
    unittest.main()
