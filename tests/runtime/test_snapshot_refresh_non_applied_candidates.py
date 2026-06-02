from __future__ import annotations

import unittest

from runtime.snapshots import run_snapshot_refresh_06


class SnapshotRefreshNonAppliedCandidatesTests(unittest.TestCase):
    def test_non_applied_candidates_remain_review_only(self) -> None:
        result = run_snapshot_refresh_06(from_review_batch_apply_examples=True)
        section = result["non_applied_candidate_section"]
        cards = result["result_card_section"]["cards"]

        self.assertEqual("snapshot_non_applied_candidate_section.v0", section["schema_version"])
        self.assertEqual(60, section["candidate_count"])
        self.assertEqual(60, result["candidate_count_after_apply"])
        self.assertTrue(section["non_applied_candidates_remain_candidates"])
        self.assertEqual(60, len([card for card in cards if card["status"] == "candidate"]))

        for candidate in section["candidates"]:
            self.assertFalse(candidate["accepted_truth"])
            self.assertEqual("candidate", candidate["public_search_status"])
            self.assertIsNone(candidate["reviewed_record_ref"])


if __name__ == "__main__":
    unittest.main()
