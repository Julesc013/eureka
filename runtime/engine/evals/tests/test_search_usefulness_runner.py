from __future__ import annotations

import json
from pathlib import Path
import unittest

from runtime.engine.evals import (
    build_default_search_usefulness_audit_runner,
    load_search_usefulness_queries,
    manual_observation_template,
    validate_search_usefulness_observation_payload,
)


REPO_ROOT = Path(__file__).resolve().parents[4]
SEARCH_USEFULNESS_ROOT = REPO_ROOT / "evals" / "search_usefulness"
FIXED_TIMESTAMP = "2026-04-25T00:00:00+00:00"


class SearchUsefulnessRunnerTestCase(unittest.TestCase):
    def test_query_pack_loads_without_errors(self) -> None:
        load_result = load_search_usefulness_queries(SEARCH_USEFULNESS_ROOT)

        self.assertEqual(load_result.errors, ())
        self.assertGreaterEqual(load_result.query_count, 60)
        self.assertLessEqual(load_result.query_count, 100)

    def test_full_suite_runs_and_marks_external_baselines_pending(self) -> None:
        runner = build_default_search_usefulness_audit_runner(
            timestamp_factory=lambda: FIXED_TIMESTAMP,
        )
        suite = runner.run_suite()

        self.assertGreaterEqual(suite.total_query_count, 60)
        self.assertIn("external_baseline_pending", suite.failure_mode_counts)
        self.assertEqual(
            suite.external_baseline_pending_counts["google"],
            suite.total_query_count,
        )
        for result in suite.task_results:
            systems = {observation.system: observation for observation in result.observations}
            self.assertEqual(systems["google"].observation_status, "pending_manual_observation")
            self.assertEqual(
                systems["internet_archive_metadata"].observation_status,
                "pending_manual_observation",
            )
            self.assertEqual(
                systems["internet_archive_full_text"].observation_status,
                "pending_manual_observation",
            )
            self.assertEqual(systems["google"].top_results, ())

    def test_one_query_run_reports_covered_only_for_local_match(self) -> None:
        runner = build_default_search_usefulness_audit_runner(
            timestamp_factory=lambda: FIXED_TIMESTAMP,
        )
        suite = runner.run_suite(query_id="synthetic_demo_app_exact")
        result = suite.task_results[0]

        self.assertEqual(suite.total_query_count, 1)
        self.assertEqual(result.query_id, "synthetic_demo_app_exact")
        self.assertEqual(result.eureka_status, "covered")
        self.assertGreater(result.search_result_count, 0)
        self.assertEqual(result.first_useful_result_rank, 1)

    def test_hard_query_remains_gap_not_fake_green(self) -> None:
        runner = build_default_search_usefulness_audit_runner(
            timestamp_factory=lambda: FIXED_TIMESTAMP,
        )
        suite = runner.run_suite(query_id="latest_firefox_before_xp_support_ended")
        result = suite.task_results[0]

        self.assertNotEqual(result.eureka_status, "covered")
        self.assertIn(result.eureka_status, {"source_gap", "capability_gap", "partial"})
        self.assertIn("source_coverage_gap", result.failure_modes)
        self.assertIn("external_baseline_pending", result.failure_modes)

    def test_json_report_is_stable_with_fixed_timestamp(self) -> None:
        runner = build_default_search_usefulness_audit_runner(
            timestamp_factory=lambda: FIXED_TIMESTAMP,
        )
        first = json.dumps(
            runner.run_suite(query_id="windows_7_apps").to_dict(),
            indent=2,
            sort_keys=True,
        )
        second = json.dumps(
            runner.run_suite(query_id="windows_7_apps").to_dict(),
            indent=2,
            sort_keys=True,
        )

        self.assertEqual(first, second)

    def test_observation_validation_accepts_pending_template(self) -> None:
        load_result = load_search_usefulness_queries(SEARCH_USEFULNESS_ROOT)
        query = next(item for item in load_result.queries if item.query_id == "windows_7_apps")
        template = manual_observation_template(query=query, system="google")

        self.assertEqual(validate_search_usefulness_observation_payload(template), ())
        self.assertEqual(template["observation_status"], "pending_manual_observation")


if __name__ == "__main__":
    unittest.main()
