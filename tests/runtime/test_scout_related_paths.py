from __future__ import annotations

import unittest

from runtime.scout import RELATED_PATH_KINDS, build_scout_run, load_candidate_index_from_examples


class ScoutRelatedPathsTest(unittest.TestCase):
    def test_related_paths_are_review_only(self) -> None:
        run = build_scout_run("archive_org_dtheater_candidate", load_candidate_index_from_examples())

        self.assertEqual(len(run["related_paths"]), len(run["relations"]))
        for path in run["related_paths"]:
            self.assertIn(path["path_kind"], RELATED_PATH_KINDS)
            self.assertTrue(path["review_required"])
            self.assertFalse(path["accepted_truth"])
            self.assertFalse(path["live_source_call_performed"])


if __name__ == "__main__":
    unittest.main()
