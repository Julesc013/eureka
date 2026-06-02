from __future__ import annotations

import unittest

from runtime.snapshots import run_snapshot_refresh_05


class SnapshotRefreshResultCardProjectionTests(unittest.TestCase):
    def test_result_card_section_preserves_public_states_and_non_claims(self) -> None:
        result = run_snapshot_refresh_05(from_public_search_ux_examples=True)
        section = result["result_card_section"]

        self.assertEqual("snapshot_result_card_section.v0", section["schema_version"])
        self.assertEqual(87, section["result_card_count"])
        self.assertEqual(8, section["result_card_states_count"])
        self.assertIn("candidate", section["supported_statuses"])
        self.assertIn("reviewed_metadata_record", section["supported_statuses"])
        self.assertIn("reviewed_source_lead", section["supported_statuses"])
        self.assertTrue(section["candidate_verified_distinction_passed"])
        self.assertTrue(section["limited_reviewed_record_distinction_passed"])
        self.assertFalse(section["candidate_cards_accepted_truth"])
        self.assertTrue(section["limited_records_are_not_verified_artifacts"])

        for card in section["cards"]:
            if card["status"] in {"candidate", "near_miss", "known_need", "absence"}:
                self.assertFalse(card["accepted_truth"])
            self.assertFalse(card["verified_download_claim"])
            self.assertFalse(card["malware_clean_claim"])
            self.assertFalse(card["rights_clearance_claim"])


if __name__ == "__main__":
    unittest.main()
