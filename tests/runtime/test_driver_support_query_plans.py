from __future__ import annotations

import unittest

from runtime.seed_batches import build_driver_support_query_plans, load_driver_support_query_set


class DriverSupportQueryPlanTests(unittest.TestCase):
    def test_query_plans_include_allowed_source_rewrites(self) -> None:
        plans = build_driver_support_query_plans(load_driver_support_query_set())
        self.assertEqual(16, len(plans))
        rewrites = plans[0]["source_query_rewrites"]
        self.assertIn("internet_archive_metadata", rewrites)
        self.assertIn("wayback_cdx_metadata", rewrites)
        self.assertIn("manual_source_pack", rewrites)
        self.assertIn("vendor_support_url_metadata", rewrites)
        self.assertIn("github_releases_metadata", rewrites)
        self.assertTrue(all(plan["accepted_truth"] is False for plan in plans))


if __name__ == "__main__":
    unittest.main()
