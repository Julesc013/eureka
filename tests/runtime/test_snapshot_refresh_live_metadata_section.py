from __future__ import annotations

import unittest

from runtime.snapshots import run_snapshot_refresh_01


class SnapshotRefreshLiveMetadataSectionTests(unittest.TestCase):
    def test_live_metadata_candidates_remain_review_only(self) -> None:
        result = run_snapshot_refresh_01(from_live_metadata_pilot_examples=True)
        section = result["live_metadata_candidate_section"]

        self.assertEqual("snapshot_live_metadata_candidate_section.v0", section["schema_version"])
        self.assertEqual("internet_archive_metadata", section["source_family"])
        self.assertTrue(section["review_required"])
        self.assertFalse(section["accepted_truth"])
        self.assertFalse(section["raw_response_included"])
        self.assertEqual([], section["reviewed_record_refs"])
        self.assertEqual(8, section["candidate_count"])
        self.assertTrue(section["source_observation_summary_refs"])

        for candidate in section["candidates"]:
            self.assertTrue(candidate["live_metadata_derived"])
            self.assertFalse(candidate["fixture_derived"])
            self.assertFalse(candidate["accepted_truth"])
            self.assertIsNone(candidate["reviewed_record_ref"])
            self.assertFalse(candidate["raw_response_included"])
            self.assertEqual("candidate", candidate["public_search_status"])


if __name__ == "__main__":
    unittest.main()
