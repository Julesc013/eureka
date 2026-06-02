from __future__ import annotations

import unittest

from runtime.seed_batches import DRIVER_SUPPORT_SUPPRESSIONS, run_seed_batch_driver_support


class DriverSupportSuppressionTests(unittest.TestCase):
    def test_required_suppressions_are_present_and_applied(self) -> None:
        result = run_seed_batch_driver_support(fixture=True)
        suppression_ids = [item["suppression_id"] for item in DRIVER_SUPPORT_SUPPRESSIONS]
        self.assertIn("fake_driver_updater", suppression_ids)
        self.assertIn("crack", suppression_ids)
        self.assertIn("keygen", suppression_ids)
        self.assertIn("driver_booster_or_updater_tool", suppression_ids)
        self.assertTrue(all(item["suppressions"] for item in result["candidate_summaries"]))
        self.assertFalse(result["cracks_keygens_serials_supported"])
        self.assertFalse(result["driver_updater_spam_supported"])


if __name__ == "__main__":
    unittest.main()
