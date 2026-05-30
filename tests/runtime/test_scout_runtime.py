from __future__ import annotations

import unittest

from runtime.scout import build_scout_run, load_candidate_index_from_examples


class ScoutRuntimeTest(unittest.TestCase):
    def test_builds_review_only_scout_run(self) -> None:
        run = build_scout_run("archive_org_dtheater_candidate", load_candidate_index_from_examples())

        self.assertEqual(run["schema_version"], "scout_run.v0")
        self.assertEqual(run["seed_candidate_id"], "archive_org_dtheater_candidate")
        self.assertGreater(run["relation_count"], 0)
        self.assertTrue(run["review_required"])
        self.assertFalse(run["accepted_truth"])
        self.assertFalse(run["accepted_truth_created"])
        self.assertFalse(run["live_source_call_performed"])


if __name__ == "__main__":
    unittest.main()
