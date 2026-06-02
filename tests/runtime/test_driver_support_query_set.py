from __future__ import annotations

import unittest

from runtime.seed_batches import load_driver_support_query_set


class DriverSupportQuerySetTests(unittest.TestCase):
    def test_required_queries_are_curated_driver_support(self) -> None:
        queries = load_driver_support_query_set()
        self.assertEqual(16, len(queries))
        self.assertEqual("StyleWriter 2500 Mac OS 8 driver", queries[0]["raw_query"])
        self.assertEqual("legacy motherboard chipset driver support CD", queries[-1]["raw_query"])
        self.assertTrue(all(item["domain_id"] == "driver_support_media" for item in queries))
        self.assertTrue(all(item["accepted_truth"] is False for item in queries))


if __name__ == "__main__":
    unittest.main()
