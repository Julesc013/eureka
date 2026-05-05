import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
AUDIT_DIR = ROOT / "control" / "audits" / "external-baseline-comparison-report-v0"
REPORT_PATH = AUDIT_DIR / "external_baseline_comparison_report.json"


class ExternalBaselineComparisonReportAuditTests(unittest.TestCase):
    def test_required_audit_files_exist(self) -> None:
        required = {
            "README.md",
            "COMPARISON_SUMMARY.md",
            "BASELINE_OBSERVATION_STATUS.md",
            "ELIGIBILITY_DECISION.md",
            "BASELINE_SCHEMA_REVIEW.md",
            "BASELINE_BATCH_REVIEW.md",
            "EUREKA_SEARCH_RUN_RESULTS.md",
            "COMPARISON_METHOD.md",
            "QUERY_BY_QUERY_COMPARISON.md",
            "SOURCE_AND_CAPABILITY_GAP_ANALYSIS.md",
            "WHERE_EUREKA_HELPED.md",
            "WHERE_EUREKA_FAILED.md",
            "NOT_COMPARABLE_CASES.md",
            "LIMITATIONS.md",
            "CLAIMS_AND_NON_CLAIMS.md",
            "MANUAL_WORK_REMAINING.md",
            "NEXT_PRODUCT_PRIORITIES.md",
            "COMMAND_RESULTS.md",
            "REMAINING_BLOCKERS.md",
            "NEXT_STEPS.md",
            "external_baseline_comparison_report.json",
        }
        existing = {path.name for path in AUDIT_DIR.iterdir() if path.is_file()}
        self.assertTrue(required.issubset(existing))

    def test_report_is_honest_about_manual_baselines(self) -> None:
        report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
        self.assertEqual(report["report_id"], "external_baseline_comparison_report_v0")
        self.assertFalse(report["external_calls_performed"])
        self.assertFalse(report["live_source_calls_performed"])
        self.assertFalse(report["model_calls_performed"])
        self.assertFalse(report["fabricated_observations"])
        self.assertFalse(report["fabricated_comparisons"])
        self.assertFalse(report["production_claimed"])
        self.assertFalse(report["master_index_mutated"])
        if report["observed_count"] == 0:
            self.assertEqual(report["eligibility"], "no_observations")
            self.assertEqual(report["compared_count"], 0)
            self.assertFalse(report["superiority_claimed"])
            self.assertTrue(report["manual_work_remaining"])

    def test_claims_doc_records_non_claims(self) -> None:
        text = (AUDIT_DIR / "CLAIMS_AND_NON_CLAIMS.md").read_text(encoding="utf-8").casefold()
        for phrase in (
            "no observations were fabricated",
            "no external calls were performed",
            "local_index_only search is not live-source search",
            "no production readiness claim",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
