from __future__ import annotations

import unittest

from runtime.seed_batches import build_legacy_software_scout_trails, run_seed_batch_legacy_software


class LegacySoftwareScoutTrailTests(unittest.TestCase):
    def test_scout_trails_build_from_seed_candidates(self) -> None:
        result = run_seed_batch_legacy_software(fixture=True)
        scout = build_legacy_software_scout_trails(result["candidate_index"]["candidates"])
        self.assertEqual(16, len(scout["scout_runs"]))
        self.assertGreater(scout["relation_count"], 0)
        self.assertFalse(scout["accepted_truth"])


if __name__ == "__main__":
    unittest.main()
