from __future__ import annotations

import unittest

from runtime.seed_batches import build_seed_batch_query_plans, load_frontier_media_query_set


class FrontierMediaQueryPlanTests(unittest.TestCase):
    def test_plans_wrap_generic_planner_with_frontier_domain(self) -> None:
        plans = build_seed_batch_query_plans(load_frontier_media_query_set())
        self.assertEqual(12, len(plans))
        self.assertTrue(all(item["intent"] == "find_frontier_resolution_media" for item in plans))
        self.assertTrue(all(item["domain_id"] == "frontier_resolution_media" for item in plans))
        self.assertTrue(all("archive_org_metadata" in item["source_query_rewrites"] for item in plans))


if __name__ == "__main__":
    unittest.main()
