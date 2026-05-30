from __future__ import annotations

import unittest

from runtime.seed_batches import build_legacy_software_query_plans, load_legacy_software_query_set


class LegacySoftwareQueryPlanTests(unittest.TestCase):
    def test_plans_include_metadata_families_and_suppressions(self) -> None:
        plans = build_legacy_software_query_plans(load_legacy_software_query_set())
        self.assertEqual(16, len(plans))
        self.assertTrue(all("internet_archive_metadata" in item["source_query_rewrites"] for item in plans))
        self.assertTrue(all("github_releases_metadata" in item["source_query_rewrites"] for item in plans))
        self.assertTrue(all(item["candidate_suppressions"] for item in plans))


if __name__ == "__main__":
    unittest.main()
