from __future__ import annotations

import unittest

from runtime.seed_batches import run_seed_batch_manuals_scans


class ManualsScansScoutTrailTests(unittest.TestCase):
    def test_scout_trails_build_from_candidates(self) -> None:
        result = run_seed_batch_manuals_scans(fixture=True)
        scout = result["scout_trails"]
        self.assertEqual(16, len(scout["scout_runs"]))
        self.assertGreaterEqual(scout["workunit_seed_count"], 16)
        self.assertFalse(scout["accepted_truth"])


if __name__ == "__main__":
    unittest.main()
