from __future__ import annotations

import unittest

from runtime.scout import build_scout_run, load_candidate_index_from_examples, project_scout_results


class ScoutProjectionBoundariesTest(unittest.TestCase):
    def test_public_projection_is_read_only(self) -> None:
        run = build_scout_run("archive_org_dtheater_candidate", load_candidate_index_from_examples())
        projection = project_scout_results(run, "public_web")

        self.assertIn("related_paths_count", projection["candidate_lane_extension"])
        self.assertIn("live_source_call", projection["blocked_actions"])
        self.assertFalse(projection["public_mutation_enabled"])
        self.assertFalse(projection["accepted_truth"])
        self.assertFalse(projection["deployment_performed"])


if __name__ == "__main__":
    unittest.main()
