from __future__ import annotations

import json
from pathlib import Path
import unittest

from runtime.engine.evals import build_default_archive_resolution_eval_runner


REPO_ROOT = Path(__file__).resolve().parents[2]
REPORT_ROOT = REPO_ROOT / "control" / "audits" / "article-scan-fixture-pack-v0"
FIXED_TIMESTAMP = "2026-04-27T00:00:00+00:00"


def _checks_by_name(task_result):
    checks = (
        task_result.satisfied_checks
        + task_result.partial_checks
        + task_result.failed_checks
        + task_result.skipped_checks
        + task_result.capability_gaps
    )
    return {check.name: check for check in checks}


class ArticleScanFixturePackTestCase(unittest.TestCase):
    def test_report_pack_exists_and_parses(self) -> None:
        required = {
            "README.md",
            "TASK_ANALYSIS.md",
            "FIXTURE_PLAN.md",
            "CHANGES_MADE.md",
            "HARD_EVAL_IMPACT.md",
            "SEARCH_USEFULNESS_IMPACT.md",
            "REMAINING_GAPS.md",
            "article_scan_fixture_report.json",
        }
        missing = [name for name in sorted(required) if not (REPORT_ROOT / name).exists()]
        self.assertEqual(missing, [])

        report = json.loads(
            (REPORT_ROOT / "article_scan_fixture_report.json").read_text(encoding="utf-8")
        )
        self.assertEqual(report["targeted_task"], "article_inside_magazine_scan")
        self.assertEqual(report["baseline"]["archive_eval_status_counts"], {"capability_gap": 1, "satisfied": 5})
        self.assertEqual(report["current"]["archive_eval_status_counts"], {"satisfied": 6})
        self.assertEqual(report["hard_eval_impact"]["article_inside_magazine_scan"], "satisfied")
        self.assertIn("do not add OCR engines", report["do_not_do"])
        self.assertIn("do not add real magazine scans", report["do_not_do"])

    def test_article_hard_eval_is_satisfied_by_segment_evidence(self) -> None:
        runner = build_default_archive_resolution_eval_runner(
            timestamp_factory=lambda: FIXED_TIMESTAMP,
        )
        result = runner.run_suite(task_id="article_inside_magazine_scan").task_results[0]
        checks = _checks_by_name(result)

        self.assertEqual(result.overall_status, "satisfied")
        self.assertGreater(result.search_observed_result_count, 0)
        for check_name in (
            "search.expected_result_hints",
            "result_shape.primary_candidate",
            "lanes.expected_lanes",
            "ranking.bad_result_patterns",
        ):
            self.assertEqual(checks[check_name].status, "satisfied", check_name)

        search_observed = checks["search.expected_result_hints"].observed or {}
        self.assertIn("article-scan-recorded-fixtures", search_observed["source_ids"])
        self.assertTrue(any("ocr" in path for path in search_observed["artifact_locators"]))

        shape = checks["result_shape.primary_candidate"].observed or {}
        primary = shape.get("primary_candidate") or {}
        self.assertEqual(primary.get("candidate_kind"), "article")
        self.assertEqual(primary.get("record_kind"), "synthetic_member")
        self.assertIn("pages-123-128.ocr.txt", primary.get("member_path", ""))
        self.assertIn("page_range", primary.get("evidence_kinds", []))
        self.assertIn("ocr_text_fixture", primary.get("evidence_kinds", []))

    def test_full_archive_suite_has_no_capability_gap_after_article_fixture(self) -> None:
        runner = build_default_archive_resolution_eval_runner(
            timestamp_factory=lambda: FIXED_TIMESTAMP,
        )
        suite = runner.run_suite()

        self.assertEqual(suite.status_counts, {"satisfied": 6})
        self.assertEqual({result.overall_status for result in suite.task_results}, {"satisfied"})

    def test_report_does_not_claim_ocr_or_external_baselines(self) -> None:
        combined = "\n".join(
            path.read_text(encoding="utf-8")
            for path in sorted(REPORT_ROOT.glob("*"))
            if path.is_file()
        ).casefold()

        self.assertIn("synthetic", combined)
        self.assertIn("external baselines remain pending", combined)
        self.assertNotIn("production-ready", combined)
        self.assertNotIn("google baseline observed", combined)
        self.assertNotIn("internet archive baseline observed", combined)


if __name__ == "__main__":
    unittest.main()
