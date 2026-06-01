from __future__ import annotations

import unittest

from runtime.seed_batches import build_manuals_scans_query_plans, load_manuals_scans_query_set


class ManualsScansQueryPlanTests(unittest.TestCase):
    def test_query_plans_include_allowed_source_rewrites(self) -> None:
        plans = build_manuals_scans_query_plans(load_manuals_scans_query_set())
        self.assertEqual(16, len(plans))
        rewrites = plans[0]["source_query_rewrites"]
        self.assertIn("internet_archive_metadata", rewrites)
        self.assertIn("open_library_metadata", rewrites)
        self.assertIn("wikidata_metadata", rewrites)
        self.assertIn("wayback_cdx_metadata", rewrites)
        self.assertIn("manual_source_pack", rewrites)
        self.assertTrue(all(plan["accepted_truth"] is False for plan in plans))


if __name__ == "__main__":
    unittest.main()
