from __future__ import annotations

import unittest

from runtime.public_alpha import load_snapshot_refresh_metrics, calculate_public_alpha_usefulness_metrics


class PublicAlphaReassessMetricsTests(unittest.TestCase):
    def test_metrics_record_current_snapshot_counts(self) -> None:
        context = load_snapshot_refresh_metrics()
        metrics = calculate_public_alpha_usefulness_metrics(context)

        self.assertEqual(1, metrics["reviewed_record_count"])
        self.assertEqual(28, metrics["candidate_count"])
        self.assertEqual(28.0, metrics["candidate_to_reviewed_ratio"])
        self.assertEqual(28, metrics["known_need_count"])
        self.assertEqual(2, metrics["absence_summary_count"])
        self.assertLess(metrics["usefulness_score"], metrics["usefulness_threshold_for_launch"])


if __name__ == "__main__":
    unittest.main()
