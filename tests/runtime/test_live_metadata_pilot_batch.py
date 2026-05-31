import unittest

from runtime.seed_batches import run_live_metadata_pilot_batch


class LiveMetadataPilotBatchTests(unittest.TestCase):
    def test_dry_run_and_fixture_modes_pass_without_live_calls(self):
        dry_run = run_live_metadata_pilot_batch(dry_run=True)
        fixture = run_live_metadata_pilot_batch(fixture=True)

        self.assertTrue(dry_run["dry_run_passed"])
        self.assertTrue(fixture["fixture_mode_passed"])
        self.assertFalse(dry_run["operator_live_metadata_run_performed"])
        self.assertFalse(fixture["operator_live_metadata_run_performed"])
        self.assertEqual(fixture["total_live_requests"], 0)


if __name__ == "__main__":
    unittest.main()
