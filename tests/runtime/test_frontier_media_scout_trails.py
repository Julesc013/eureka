from __future__ import annotations

import unittest

from runtime.seed_batches import build_seed_batch_scout_trails, run_seed_batch_frontier_media


class FrontierMediaScoutTrailTests(unittest.TestCase):
    def test_scout_trails_build_from_seed_candidates(self) -> None:
        result = run_seed_batch_frontier_media(fixture=True)
        scout = build_seed_batch_scout_trails(result["candidate_index"]["candidates"])
        self.assertEqual(12, len(scout["scout_runs"]))
        self.assertGreater(scout["relation_count"], 0)
        self.assertFalse(scout["accepted_truth"])


if __name__ == "__main__":
    unittest.main()
