from __future__ import annotations

import unittest

from runtime.scout import build_scout_run, load_candidate_index_from_examples


class ScoutDiscoveryTrailTest(unittest.TestCase):
    def test_discovery_trail_matches_relation_steps(self) -> None:
        run = build_scout_run("archive_org_dtheater_candidate", load_candidate_index_from_examples())
        trail = run["discovery_trail"]

        self.assertEqual(len(trail["steps"]), len(run["relations"]))
        self.assertIn("same_source_family", trail["relation_path"])
        self.assertTrue(trail["review_required"])
        self.assertFalse(trail["accepted_truth"])


if __name__ == "__main__":
    unittest.main()
