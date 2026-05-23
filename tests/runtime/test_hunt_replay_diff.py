from __future__ import annotations

import unittest

from runtime.search.hunt import diff_replay_outputs


class HuntReplayDiffTests(unittest.TestCase):
    def test_diff_reports_matches_and_differences(self) -> None:
        matched = diff_replay_outputs({"hunt_created": True}, {"hunt_created": True})
        changed = diff_replay_outputs({"hunt_created": True}, {"hunt_created": False})

        self.assertTrue(matched.matched)
        self.assertEqual("matched", matched.status)
        self.assertFalse(changed.matched)
        self.assertEqual("diff", changed.status)
        self.assertEqual("hunt_created", changed.differences[0]["field"])


if __name__ == "__main__":
    unittest.main()
