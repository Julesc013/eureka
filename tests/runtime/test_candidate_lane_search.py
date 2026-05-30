from __future__ import annotations

import unittest

from runtime.candidate_store import build_candidate_lane_packet, sample_candidate_index, search_candidates


class CandidateLaneSearchTest(unittest.TestCase):
    def test_candidate_search_and_public_lane_are_read_only(self) -> None:
        search = search_candidates("D-Theater New York 1993", sample_candidate_index())
        lane = build_candidate_lane_packet(search, "public_web")

        self.assertGreaterEqual(search["result_count"], 1)
        self.assertFalse(search["accepted_truth"])
        self.assertEqual(lane["truth_status"], "candidate_only")
        self.assertFalse(lane["accepted_truth"])
        self.assertFalse(lane["public_mutation_enabled"])
        self.assertIn("promote", lane["blocked_actions"])


if __name__ == "__main__":
    unittest.main()
