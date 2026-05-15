from __future__ import annotations

import unittest

from runtime.local_eval import record_elapsed_ms, summarize_latency


class LocalEvalLatencyTests(unittest.TestCase):
    def test_latency_values_recorded(self) -> None:
        elapsed = record_elapsed_ms(1.0, 1.25)
        self.assertEqual(250.0, elapsed)

    def test_latency_summary_reports_slowest(self) -> None:
        summary = summarize_latency(
            [
                {"suite": "a", "case_id": "one", "path": "/one", "elapsed_ms": 2.0},
                {"suite": "a", "case_id": "two", "path": "/two", "elapsed_ms": 5.0},
            ]
        )
        self.assertEqual("pass", summary["status"])
        self.assertEqual(5.0, summary["max_elapsed_ms"])
        self.assertEqual("/two", summary["slowest_routes"][0]["path"])


if __name__ == "__main__":
    unittest.main()
