from __future__ import annotations

import json
from pathlib import Path
import unittest

from runtime.engine.evals import build_default_archive_resolution_eval_runner


REPO_ROOT = Path(__file__).resolve().parents[2]
REPORT_ROOT = REPO_ROOT / "control" / "audits" / "more-source-coverage-expansion-v1"
FIXED_TIMESTAMP = "2026-04-27T00:00:00+00:00"


class MoreSourceCoverageExpansionV1TestCase(unittest.TestCase):
    def test_report_pack_exists_and_is_bounded(self) -> None:
        required = {
            "README.md",
            "TARGET_TASKS.md",
            "FIXTURE_PLAN.md",
            "CHANGES_MADE.md",
            "HARD_EVAL_IMPACT.md",
            "SEARCH_USEFULNESS_IMPACT.md",
            "REMAINING_GAPS.md",
            "source_expansion_report.json",
        }
        missing = [name for name in sorted(required) if not (REPORT_ROOT / name).exists()]
        self.assertEqual(missing, [])

        report = json.loads(
            (REPORT_ROOT / "source_expansion_report.json").read_text(encoding="utf-8")
        )
        self.assertEqual(report["current"]["archive_eval_status_counts"], {"capability_gap": 1, "satisfied": 5})
        self.assertEqual(report["recommended_next_milestone"], "Article/Scan Fixture Pack v0")
        self.assertIn("pending_manual_observation", report["current"]["external_baselines"].values())
        self.assertIn("do not add crawling", report["do_not_do"])
        self.assertIn("do not add real binaries", report["do_not_do"])

    def test_targeted_hard_eval_partials_are_now_source_backed_satisfied(self) -> None:
        runner = build_default_archive_resolution_eval_runner(
            timestamp_factory=lambda: FIXED_TIMESTAMP,
        )
        suite = runner.run_suite()
        by_id = {result.task_id: result for result in suite.task_results}

        self.assertEqual(suite.status_counts, {"satisfied": 6})
        for task_id in (
            "latest_firefox_before_xp_drop",
            "old_blue_ftp_client_xp",
            "win98_registry_repair",
            "windows_7_apps",
        ):
            result = by_id[task_id]
            self.assertEqual(result.overall_status, "satisfied", task_id)
            rendered = json.dumps(result.to_dict(), sort_keys=True)
            self.assertIn("source_id", rendered, task_id)
            self.assertIn("artifact_locators", rendered, task_id)
            self.assertIn("ranking.bad_result_patterns", rendered, task_id)

        article = by_id["article_inside_magazine_scan"]
        self.assertEqual(article.overall_status, "satisfied")
        self.assertIn("article-scan-recorded-fixtures", json.dumps(article.to_dict(), sort_keys=True))

    def test_report_does_not_claim_live_or_external_baseline_behavior(self) -> None:
        combined = "\n".join(
            path.read_text(encoding="utf-8")
            for path in sorted(REPORT_ROOT.glob("*"))
            if path.is_file()
        ).casefold()

        self.assertNotIn("google baseline observed", combined)
        self.assertNotIn("internet archive baseline observed", combined)
        self.assertNotIn("production-ready", combined)
        self.assertIn("does not add live source", combined)
        self.assertIn("external baselines remain pending", combined)


if __name__ == "__main__":
    unittest.main()
