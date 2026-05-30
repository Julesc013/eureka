from __future__ import annotations

import unittest

from runtime.seed_batches import load_legacy_software_query_set


class LegacySoftwareQuerySetTests(unittest.TestCase):
    def test_required_queries_are_curated_legacy_software(self) -> None:
        queries = load_legacy_software_query_set()
        self.assertEqual(16, len(queries))
        self.assertEqual(
            "Windows 7-compatible portable utilities, not Windows 7 ISO",
            queries[0]["raw_query"],
        )
        self.assertTrue(all(item["domain_id"] in {"legacy_software", "driver_support_media"} for item in queries))
        self.assertTrue(all(item["accepted_truth"] is False for item in queries))


if __name__ == "__main__":
    unittest.main()
