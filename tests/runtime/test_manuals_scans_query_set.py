from __future__ import annotations

import unittest

from runtime.seed_batches import load_manuals_scans_query_set


class ManualsScansQuerySetTests(unittest.TestCase):
    def test_required_queries_are_curated_manuals_scans(self) -> None:
        queries = load_manuals_scans_query_set()
        self.assertEqual(16, len(queries))
        self.assertEqual("JVC D-VHS D-Theater manual", queries[0]["raw_query"])
        self.assertEqual("legacy software installation notes scanned manual", queries[-1]["raw_query"])
        self.assertTrue(all(item["domain_id"] == "manuals_docs_scans" for item in queries))
        self.assertTrue(all(item["accepted_truth"] is False for item in queries))


if __name__ == "__main__":
    unittest.main()
