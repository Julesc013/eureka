from __future__ import annotations

import json
from pathlib import Path
import unittest

from runtime.engine.evals import (
    build_default_archive_resolution_eval_runner,
    load_archive_resolution_eval_tasks,
)


REPO_ROOT = Path(__file__).resolve().parents[4]
ARCHIVE_RESOLUTION_ROOT = REPO_ROOT / "evals" / "archive_resolution"
FIXED_TIMESTAMP = "2026-04-24T00:00:00+00:00"


class ArchiveResolutionEvalRunnerTestCase(unittest.TestCase):
    def test_full_suite_produces_result_for_all_task_ids(self) -> None:
        runner = build_default_archive_resolution_eval_runner(
            timestamp_factory=lambda: FIXED_TIMESTAMP,
        )
        suite = runner.run_suite()
        loaded = load_archive_resolution_eval_tasks(ARCHIVE_RESOLUTION_ROOT)

        self.assertEqual(suite.total_task_count, loaded.task_count)
        self.assertEqual(
            sorted(result.task_id for result in suite.task_results),
            sorted(task.task_id for task in loaded.tasks),
        )
        self.assertEqual(suite.created_by_slice, "archive_resolution_eval_runner_v0")

    def test_planner_checks_evaluate_expected_plan_fields(self) -> None:
        runner = build_default_archive_resolution_eval_runner(
            timestamp_factory=lambda: FIXED_TIMESTAMP,
        )
        suite = runner.run_suite(task_id="windows_7_apps")
        task_result = suite.task_results[0]
        satisfied_names = {check.name for check in task_result.satisfied_checks}

        self.assertEqual(task_result.planner_status, "satisfied")
        self.assertIn("planner.task_kind", satisfied_names)
        self.assertIn("planner.object_type", satisfied_names)
        self.assertIn("planner.constraints.platform", satisfied_names)

    def test_capability_gaps_are_reported_honestly(self) -> None:
        runner = build_default_archive_resolution_eval_runner(
            timestamp_factory=lambda: FIXED_TIMESTAMP,
        )
        suite = runner.run_suite(task_id="article_inside_magazine_scan")
        task_result = suite.task_results[0]

        self.assertEqual(task_result.overall_status, "capability_gap")
        self.assertEqual(task_result.search_observed_result_count, 0)
        self.assertTrue(task_result.capability_gaps)
        self.assertIn("Current bootstrap corpus", task_result.capability_gaps[0].message)
        self.assertTrue(task_result.skipped_checks)

    def test_json_report_is_stable_with_fixed_timestamp(self) -> None:
        runner = build_default_archive_resolution_eval_runner(
            timestamp_factory=lambda: FIXED_TIMESTAMP,
        )
        first = json.dumps(
            runner.run_suite(task_id="windows_7_apps").to_dict(),
            indent=2,
            sort_keys=True,
        )
        second = json.dumps(
            runner.run_suite(task_id="windows_7_apps").to_dict(),
            indent=2,
            sort_keys=True,
        )

        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
