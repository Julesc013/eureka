from __future__ import annotations

import unittest

from runtime.candidate_store import build_candidate_lane_packet, sample_candidate_index, search_candidates
from runtime.scout import build_scout_run


class ScoutCandidateIntegrationTest(unittest.TestCase):
    def test_accepts_candidate_index_and_candidate_lane_shapes(self) -> None:
        index = sample_candidate_index()
        run_from_index = build_scout_run("archive_org_dtheater_candidate", index)
        search = search_candidates("D-Theater New York 1993", index)
        lane = build_candidate_lane_packet(search, "public_web")
        run_from_lane = build_scout_run("archive_org_dtheater_candidate", lane)

        self.assertGreater(run_from_index["relation_count"], 0)
        self.assertGreaterEqual(run_from_lane["relation_count"], 1)
        self.assertFalse(run_from_index["accepted_truth"])
        self.assertFalse(run_from_lane["public_mutation_enabled"])


if __name__ == "__main__":
    unittest.main()
