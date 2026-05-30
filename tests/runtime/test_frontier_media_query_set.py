from __future__ import annotations

import unittest

from runtime.seed_batches import load_frontier_media_query_set


class FrontierMediaQuerySetTests(unittest.TestCase):
    def test_required_queries_are_curated_frontier_media(self) -> None:
        queries = load_frontier_media_query_set()
        self.assertEqual(12, len(queries))
        self.assertEqual(
            "New York 1993 D-Theater HD demo tape original source",
            queries[0]["raw_query"],
        )
        self.assertTrue(all(item["domain_id"] == "frontier_resolution_media" for item in queries))
        self.assertTrue(all(item["accepted_truth"] is False for item in queries))


if __name__ == "__main__":
    unittest.main()
