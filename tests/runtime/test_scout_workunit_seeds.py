from __future__ import annotations

import unittest

from runtime.scout import WORKUNIT_SEED_TYPES, build_scout_run, load_candidate_index_from_examples


class ScoutWorkUnitSeedsTest(unittest.TestCase):
    def test_workunit_seeds_are_suggestions_only(self) -> None:
        run = build_scout_run("archive_org_dtheater_candidate", load_candidate_index_from_examples())

        self.assertGreaterEqual(len(run["workunit_seeds"]), 1)
        for seed in run["workunit_seeds"]:
            self.assertIn(seed["seed_type"], WORKUNIT_SEED_TYPES)
            self.assertFalse(seed["creates_runtime_workunit"])
            self.assertTrue(seed["review_required"])
            self.assertFalse(seed["accepted_truth"])


if __name__ == "__main__":
    unittest.main()
