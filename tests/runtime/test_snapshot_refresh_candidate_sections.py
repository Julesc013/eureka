from __future__ import annotations

import unittest

from runtime.snapshots import run_snapshot_refresh


class SnapshotRefreshCandidateSectionTests(unittest.TestCase):
    def test_candidates_remain_review_only(self) -> None:
        result = run_snapshot_refresh(from_seed_examples=True)

        for section in result["candidate_sections"]:
            self.assertFalse(section["accepted_truth"])
            self.assertFalse(section["candidate_promoted_to_reviewed"])
            for candidate in section["candidates"]:
                self.assertFalse(candidate["accepted_truth"])
                self.assertIsNone(candidate["reviewed_record_ref"])
                self.assertFalse(candidate["action_posture"]["public_mutation_enabled"])


if __name__ == "__main__":
    unittest.main()
