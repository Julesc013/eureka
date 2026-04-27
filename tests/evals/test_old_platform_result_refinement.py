from __future__ import annotations

import json
from pathlib import Path
import unittest

from runtime.engine.evals import build_default_archive_resolution_eval_runner


REPO_ROOT = Path(__file__).resolve().parents[2]
REPORT_ROOT = REPO_ROOT / "control" / "audits" / "old-platform-result-refinement-v0"
FIXED_TIMESTAMP = "2026-04-27T00:00:00+00:00"

TARGETED_TASK_IDS = {
    "driver_inside_support_cd",
    "latest_firefox_before_xp_drop",
    "old_blue_ftp_client_xp",
    "win98_registry_repair",
    "windows_7_apps",
}


def _checks_by_name(task_result):
    checks = (
        task_result.satisfied_checks
        + task_result.partial_checks
        + task_result.failed_checks
        + task_result.skipped_checks
        + task_result.capability_gaps
    )
    return {check.name: check for check in checks}


class OldPlatformResultRefinementPackTestCase(unittest.TestCase):
    def test_report_pack_exists_and_parses(self) -> None:
        required = {
            "README.md",
            "BASELINE.md",
            "TASK_BY_TASK_REFINEMENT.md",
            "RESULT_SHAPE_REQUIREMENTS.md",
            "BAD_RESULT_PATTERNS.md",
            "CHANGES_MADE.md",
            "REMAINING_GAPS.md",
            "result_refinement_report.json",
        }
        missing = [name for name in sorted(required) if not (REPORT_ROOT / name).exists()]
        self.assertEqual(missing, [])

        report = json.loads(
            (REPORT_ROOT / "result_refinement_report.json").read_text(encoding="utf-8")
        )
        self.assertEqual(report["baseline"]["status_counts"], {"capability_gap": 1, "partial": 5})
        self.assertEqual(
            report["current"]["status_counts"],
            {"capability_gap": 1, "partial": 4, "satisfied": 1},
        )
        self.assertEqual(set(report["targeted_tasks"]), TARGETED_TASK_IDS)
        self.assertEqual(report["tasks_improved_to_satisfied"], ["driver_inside_support_cd"])
        self.assertIn("article_inside_magazine_scan", report["tasks_still_capability_gap"])

    def test_archive_eval_statuses_are_evidence_backed(self) -> None:
        runner = build_default_archive_resolution_eval_runner(
            timestamp_factory=lambda: FIXED_TIMESTAMP,
        )
        suite = runner.run_suite()
        by_id = {result.task_id: result for result in suite.task_results}

        self.assertEqual(suite.status_counts, {"capability_gap": 1, "satisfied": 5})
        self.assertEqual(by_id["driver_inside_support_cd"].overall_status, "satisfied")
        self.assertEqual(by_id["article_inside_magazine_scan"].overall_status, "capability_gap")

        for task_id in TARGETED_TASK_IDS:
            result = by_id[task_id]
            checks = _checks_by_name(result)
            for check_name in (
                "search.expected_result_hints",
                "result_shape.primary_candidate",
                "lanes.expected_lanes",
                "ranking.bad_result_patterns",
            ):
                self.assertIn(check_name, checks, task_id)
            self.assertIn(result.overall_status, {"partial", "satisfied"}, task_id)

    def test_satisfied_driver_task_has_member_shape_and_no_bad_pattern(self) -> None:
        runner = build_default_archive_resolution_eval_runner(
            timestamp_factory=lambda: FIXED_TIMESTAMP,
        )
        result = runner.run_suite(task_id="driver_inside_support_cd").task_results[0]
        checks = _checks_by_name(result)

        self.assertEqual(result.overall_status, "satisfied")
        for check_name in (
            "search.expected_result_hints",
            "result_shape.primary_candidate",
            "lanes.expected_lanes",
            "ranking.bad_result_patterns",
        ):
            self.assertEqual(checks[check_name].status, "satisfied")

        shape = checks["result_shape.primary_candidate"].observed or {}
        primary = shape.get("primary_candidate") or {}
        self.assertIn(primary.get("record_kind"), {"member", "synthetic_member"})
        self.assertEqual(primary.get("candidate_kind"), "driver")
        self.assertIn("driver.inf", primary.get("member_path", ""))
        self.assertTrue(primary.get("source_id"))
        self.assertTrue(primary.get("has_direct_artifact_locator"))

    def test_source_expansion_supersedes_prior_partials_with_evidence(self) -> None:
        runner = build_default_archive_resolution_eval_runner(
            timestamp_factory=lambda: FIXED_TIMESTAMP,
        )
        by_id = {result.task_id: result for result in runner.run_suite().task_results}

        superseded_partials = {
            "latest_firefox_before_xp_drop",
            "old_blue_ftp_client_xp",
            "win98_registry_repair",
            "windows_7_apps",
        }
        for task_id in superseded_partials:
            result = by_id[task_id]
            checks = _checks_by_name(result)
            self.assertEqual(result.overall_status, "satisfied", task_id)
            self.assertEqual(checks["search.expected_result_hints"].status, "satisfied", task_id)
            self.assertEqual(checks["result_shape.primary_candidate"].status, "satisfied", task_id)
            self.assertEqual(checks["lanes.expected_lanes"].status, "satisfied", task_id)
            self.assertEqual(checks["ranking.bad_result_patterns"].status, "satisfied", task_id)

    def test_report_does_not_claim_external_baselines_or_production_readiness(self) -> None:
        combined = "\n".join(
            path.read_text(encoding="utf-8")
            for path in sorted(REPORT_ROOT.glob("*"))
            if path.is_file()
        ).casefold()

        self.assertNotIn("production ready", combined)
        self.assertNotIn("production-ready", combined)
        self.assertNotIn("google baseline observed", combined)
        self.assertNotIn("internet archive baseline observed", combined)
        self.assertIn("external baselines remain pending", combined)
        self.assertIn("live crawling", combined)


if __name__ == "__main__":
    unittest.main()
