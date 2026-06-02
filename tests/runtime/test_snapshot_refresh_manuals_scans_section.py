from __future__ import annotations

import unittest

from runtime.snapshots import run_snapshot_refresh_04


class SnapshotRefreshManualsScansSectionTests(unittest.TestCase):
    def test_manuals_scans_section_projects_review_only_candidates(self) -> None:
        result = run_snapshot_refresh_04(from_manuals_driver_examples=True)
        section = result["manuals_scans_candidate_section"]

        self.assertEqual("pass", result["status"])
        self.assertEqual("snapshot_manuals_scans_candidate_section.v0", section["schema_version"])
        self.assertEqual("manuals_docs_scans", section["domain_id"])
        self.assertEqual(16, section["candidate_count"])
        self.assertFalse(section["accepted_truth"])
        self.assertFalse(section["download_performed"])
        self.assertFalse(section["file_fetch_performed"])
        self.assertFalse(section["ocr_performed"])
        self.assertFalse(section["rights_clearance_claim_created"])
        self.assertFalse(section["scan_completeness_claim_created"])
        self.assertFalse(section["ocr_quality_claim_created"])

        for candidate in section["candidates"]:
            self.assertEqual("candidate", candidate["public_search_status"])
            self.assertIsNone(candidate["reviewed_record_ref"])
            self.assertFalse(candidate["accepted_truth"])
            self.assertFalse(candidate["download_performed"])
            self.assertFalse(candidate["file_fetch_performed"])
            self.assertFalse(candidate["ocr_performed"])
            self.assertFalse(candidate["rights_clearance_claim_created"])
            self.assertFalse(candidate["scan_completeness_claim_created"])
            self.assertFalse(candidate["ocr_quality_claim_created"])

    def test_manuals_scans_public_cards_are_not_verified_documents(self) -> None:
        result = run_snapshot_refresh_04(from_manuals_driver_examples=True)
        cards = [
            card
            for card in result["public_search_view_model_projection"]["result_cards"]
            if card["object_type"] == "manuals_scans_candidate"
        ]

        self.assertEqual(16, len(cards))
        for card in cards:
            self.assertEqual("candidate", card["status"])
            self.assertFalse(card["accepted_truth"])
            self.assertFalse(card["artifact_verified"])
            self.assertFalse(card["verified_download_claim"])
            self.assertFalse(card["rights_clearance_claim"])
            self.assertFalse(card["file_fetch_performed"])
            self.assertFalse(card["ocr_performed"])


if __name__ == "__main__":
    unittest.main()
