from __future__ import annotations

import unittest

from runtime.seed_batches import run_seed_batch_driver_support


class DriverSupportScoutTrailTests(unittest.TestCase):
    def test_scout_trails_build_for_fixture_candidates(self) -> None:
        result = run_seed_batch_driver_support(fixture=True)
        trails = result["scout_trails"]
        self.assertEqual(16, len(trails["scout_runs"]))
        self.assertEqual(16, len(trails["scout_refs"]))
        self.assertFalse(trails["accepted_truth"])
        self.assertFalse(trails["download_performed"])


if __name__ == "__main__":
    unittest.main()
