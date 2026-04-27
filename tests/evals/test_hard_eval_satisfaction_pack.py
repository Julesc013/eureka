from __future__ import annotations

import json
from pathlib import Path
import unittest

from runtime.engine.evals import build_default_archive_resolution_eval_runner


REPO_ROOT = Path(__file__).resolve().parents[2]
REPORT_ROOT = REPO_ROOT / "control" / "audits" / "hard-eval-satisfaction-v0"
FIXED_TIMESTAMP = "2026-04-27T00:00:00+00:00"

MOVED_TASK_IDS = {
    "driver_inside_support_cd",
    "latest_firefox_before_xp_drop",
    "old_blue_ftp_client_xp",
    "win98_registry_repair",
    "windows_7_apps",
}


def _search_check(task_result):
    checks = (
        task_result.satisfied_checks
        + task_result.partial_checks
        + task_result.failed_checks
        + task_result.capability_gaps
    )
    matches = [check for check in checks if check.name == "search.expected_result_hints"]
    assert len(matches) == 1
    return matches[0]


class HardEvalSatisfactionPackTestCase(unittest.TestCase):
    def test_report_pack_exists_and_parses(self) -> None:
        required = {
            "README.md",
            "CURRENT_FAILURES.md",
            "SATISFACTION_PLAN.md",
            "TASK_BY_TASK_ANALYSIS.md",
            "CHANGES_MADE.md",
            "REMAINING_GAPS.md",
            "hard_eval_satisfaction_report.json",
        }
        missing = [name for name in sorted(required) if not (REPORT_ROOT / name).exists()]
        self.assertEqual(missing, [])

        report = json.loads(
            (REPORT_ROOT / "hard_eval_satisfaction_report.json").read_text(encoding="utf-8")
        )
        self.assertEqual(report["baseline"]["status_counts"], {"capability_gap": 1, "not_satisfied": 5})
        self.assertEqual(report["current"]["status_counts"], {"capability_gap": 1, "partial": 5})
        self.assertEqual(set(report["delta"]["improved_tasks"]), MOVED_TASK_IDS)
        self.assertEqual(report["delta"]["overall_satisfied_tasks"], [])
        self.assertIn("article_inside_magazine_scan", report["delta"]["still_capability_gap"])

    def test_runner_keeps_source_backed_tasks_at_least_partial(self) -> None:
        runner = build_default_archive_resolution_eval_runner(
            timestamp_factory=lambda: FIXED_TIMESTAMP,
        )
        suite = runner.run_suite()
        by_id = {result.task_id: result for result in suite.task_results}

        self.assertEqual(suite.status_counts, {"satisfied": 6})
        self.assertEqual(set(by_id), MOVED_TASK_IDS | {"article_inside_magazine_scan"})

        for task_id in MOVED_TASK_IDS:
            result = by_id[task_id]
            check = _search_check(result)
            self.assertIn(result.overall_status, {"partial", "satisfied"}, task_id)
            self.assertIn(check.status, {"satisfied", "partial"}, task_id)
            self.assertGreater(result.search_observed_result_count, 0, task_id)
            observed = check.observed or {}
            self.assertTrue(observed.get("source_ids"), task_id)
            self.assertTrue(
                observed.get("member_paths")
                or observed.get("representation_ids")
                or observed.get("artifact_locators"),
                task_id,
            )

    def test_article_scan_task_now_requires_fixture_article_evidence(self) -> None:
        runner = build_default_archive_resolution_eval_runner(
            timestamp_factory=lambda: FIXED_TIMESTAMP,
        )
        result = runner.run_suite(task_id="article_inside_magazine_scan").task_results[0]
        check = _search_check(result)

        self.assertEqual(result.overall_status, "satisfied")
        self.assertGreater(result.search_observed_result_count, 0)
        self.assertEqual(check.status, "satisfied")
        observed = check.observed or {}
        self.assertEqual(observed.get("source_ids"), ["article-scan-recorded-fixtures"])
        self.assertTrue(any("ocr" in item for item in observed.get("artifact_locators", [])))

    def test_overall_satisfied_tasks_need_structured_source_evidence(self) -> None:
        runner = build_default_archive_resolution_eval_runner(
            timestamp_factory=lambda: FIXED_TIMESTAMP,
        )
        suite = runner.run_suite()

        for result in suite.task_results:
            if result.overall_status != "satisfied":
                continue
            checks = {
                check.name: check
                for check in result.satisfied_checks
                + result.partial_checks
                + result.failed_checks
                + result.capability_gaps
            }
            for name in (
                "search.expected_result_hints",
                "result_shape.primary_candidate",
                "lanes.expected_lanes",
                "ranking.bad_result_patterns",
            ):
                self.assertIn(name, checks, result.task_id)
                self.assertEqual(checks[name].status, "satisfied", result.task_id)
            observed = checks["search.expected_result_hints"].observed or {}
            self.assertTrue(observed.get("source_ids"), result.task_id)
            self.assertTrue(observed.get("artifact_locators"), result.task_id)

    def test_report_does_not_claim_external_baseline_or_production_readiness(self) -> None:
        combined = "\n".join(
            path.read_text(encoding="utf-8")
            for path in sorted(REPORT_ROOT.glob("*"))
            if path.is_file()
        ).casefold()

        self.assertNotIn("production ready", combined)
        self.assertNotIn("production-ready", combined)
        self.assertNotIn("google baseline observed", combined)
        self.assertNotIn("internet archive baseline observed", combined)
        self.assertIn("fabricate external baselines", combined)
        self.assertIn("live crawling", combined)


if __name__ == "__main__":
    unittest.main()
