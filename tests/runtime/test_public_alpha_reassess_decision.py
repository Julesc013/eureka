from __future__ import annotations

import unittest

from runtime.public_alpha import run_public_alpha_reassess


class PublicAlphaReassessDecisionTests(unittest.TestCase):
    def test_thresholds_keep_launch_deferred(self) -> None:
        result = run_public_alpha_reassess(from_snapshot_refresh_examples=True)
        decision = result["decision"]

        self.assertEqual("remain_deferred", decision["decision"])
        self.assertFalse(decision["launch_recommended"])
        self.assertTrue(decision["needs_more_reviewed_records"])
        self.assertTrue(decision["needs_live_metadata_pilot"])
        self.assertGreater(len(decision["blockers"]), 0)


if __name__ == "__main__":
    unittest.main()
