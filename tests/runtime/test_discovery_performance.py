from __future__ import annotations

import tempfile
from pathlib import Path
import unittest

from runtime.search.performance import run_capacity_baseline


class DiscoveryPerformanceTests(unittest.TestCase):
    def test_capacity_baseline_is_repeatable_and_non_production_claiming(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            result = run_capacity_baseline(dataset_sizes=(10, 25), work_root=Path(temp), query_iterations=3, export_generation=False)

        self.assertEqual("pass", result["status"])
        self.assertEqual([10, 25], result["dataset_sizes"])
        self.assertEqual(2, len(result["datasets"]))
        self.assertFalse(result["production_scale_claimed"])
        self.assertFalse(result["network_provider_calls"])
        for dataset in result["datasets"]:
            self.assertGreaterEqual(dataset["document_count"], dataset["dataset_size"])
            self.assertIn("p95", dataset["fts_query_latency_ms"])
            self.assertGreaterEqual(dataset["database_bytes_per_document"], 0)
        self.assertEqual("provisional_v0_not_production_slo", result["provisional_v0_targets"]["target_type"])


if __name__ == "__main__":
    unittest.main()
