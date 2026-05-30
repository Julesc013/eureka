from __future__ import annotations

import unittest

from runtime.seed_batches import LEGACY_SOFTWARE_SUPPRESSIONS, run_seed_batch_legacy_software


class LegacySoftwareSuppressionTests(unittest.TestCase):
    def test_required_suppressions_are_visible_and_non_overridable(self) -> None:
        result = run_seed_batch_legacy_software(fixture=True)
        required = {item["suppression_id"] for item in LEGACY_SOFTWARE_SUPPRESSIONS}
        emitted = {item["suppression_id"] for item in result["suppressions"]}
        self.assertEqual(required, emitted)
        self.assertTrue(all(item["review_override_allowed"] is False for item in result["suppressions"]))
        self.assertIn("crack", result["candidate_summaries"][0]["suppressions"])
        self.assertIn("keygen", result["candidate_summaries"][0]["suppressions"])
        self.assertIn("serial", result["candidate_summaries"][0]["suppressions"])


if __name__ == "__main__":
    unittest.main()
