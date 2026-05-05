import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class ExternalBaselineComparisonRunnerTests(unittest.TestCase):
    def test_runner_json_parses_without_external_calls(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                "scripts/run_external_baseline_comparison.py",
                "--batch",
                "batch_0",
                "--json",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        report = json.loads(completed.stdout)
        self.assertIn(
            report["eligibility"],
            {
                "no_observations",
                "partial_observations",
                "eligible",
                "comparison_completed",
                "invalid_observations",
                "local_search_unavailable",
            },
        )
        self.assertFalse(report["external_calls_performed"])
        self.assertFalse(report["live_source_calls_performed"])
        self.assertFalse(report["model_calls_performed"])
        self.assertFalse(report["fabricated_observations"])
        self.assertFalse(report["fabricated_comparisons"])
        self.assertFalse(report["production_claimed"])

    def test_current_no_observation_case_does_not_fabricate_comparisons(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                "scripts/run_external_baseline_comparison.py",
                "--batch",
                "batch_0",
                "--json",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        report = json.loads(completed.stdout)
        if report["observed_count"] == 0:
            self.assertEqual(report["eligibility"], "no_observations")
            self.assertEqual(report["compared_count"], 0)
            self.assertEqual(report["query_comparisons"], [])
            self.assertFalse(report["superiority_claimed"])
            for key, value in report["aggregate_summary"].items():
                if key.endswith("_count"):
                    self.assertEqual(value, 0)

    def test_strict_allows_truthful_no_observation_state(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                "scripts/run_external_baseline_comparison.py",
                "--batch",
                "batch_0",
                "--json",
                "--strict",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        report = json.loads(completed.stdout)
        if report["observed_count"] == 0:
            self.assertEqual(completed.returncode, 0)
            self.assertTrue(report["ok"])


if __name__ == "__main__":
    unittest.main()
