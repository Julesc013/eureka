import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
DELTA_ROOT = REPO_ROOT / "control" / "audits" / "search-usefulness-delta-v1"
QUERY_PACK = REPO_ROOT / "evals" / "search_usefulness" / "queries" / "search_usefulness_v0.json"

REQUIRED_FILES = [
    "README.md",
    "BASELINE.md",
    "CURRENT_RESULTS.md",
    "DELTA_SUMMARY.md",
    "WEDGE_DELTA.md",
    "ARCHIVE_EVAL_DELTA.md",
    "FAILURE_MODE_DELTA.md",
    "QUERY_MOVEMENT.md",
    "NEXT_RECOMMENDATIONS.md",
    "delta_report.json",
]


def _read(name: str) -> str:
    return (DELTA_ROOT / name).read_text(encoding="utf-8")


def _load_report() -> dict:
    return json.loads(_read("delta_report.json"))


class SearchUsefulnessAuditDeltaV1Test(unittest.TestCase):
    def test_delta_pack_files_exist(self):
        self.assertTrue(DELTA_ROOT.exists())
        missing = [name for name in REQUIRED_FILES if not (DELTA_ROOT / name).exists()]
        self.assertEqual(missing, [])

    def test_delta_report_parses_and_names_wedges(self):
        report = _load_report()
        self.assertEqual(report["report_id"], "search_usefulness_delta_v1")
        self.assertEqual(report["selected_wedges"]["primary"], "old_platform_compatible_software_search")
        self.assertEqual(report["selected_wedges"]["secondary"], "member_level_discovery_inside_bundles")
        self.assertEqual(report["recommended_next_milestone"], "Hard Eval Satisfaction Pack v0")

    def test_baseline_and_current_query_count_are_identified(self):
        report = _load_report()
        query_pack = json.loads(QUERY_PACK.read_text(encoding="utf-8"))
        query_count = len(query_pack["queries"])

        self.assertEqual(report["baseline"]["source"], "control/audits/search-usefulness-delta-v0/delta_report.json")
        self.assertGreaterEqual(report["current"]["query_count"], 64)
        self.assertEqual(report["current"]["query_count"], query_count)

    def test_status_and_archive_deltas_are_present(self):
        report = _load_report()
        self.assertEqual(report["delta"]["status_count_changes"]["partial"], 15)
        self.assertEqual(report["delta"]["status_count_changes"]["source_gap"], -13)
        self.assertEqual(report["delta"]["status_count_changes"]["capability_gap"], -2)
        self.assertEqual(report["current"]["archive_eval_counts"]["status_counts"]["not_satisfied"], 5)
        self.assertEqual(report["delta"]["archive_eval_changes"]["capability_gap"], -4)
        self.assertIn("not success", report["delta"]["archive_eval_changes"]["interpretation"])

    def test_external_baselines_remain_pending(self):
        report = _load_report()
        pending = report["current"]["external_baseline_pending_counts"]
        query_count = report["current"]["query_count"]

        self.assertEqual(pending["google"], query_count)
        self.assertEqual(pending["internet_archive_metadata"], query_count)
        self.assertEqual(pending["internet_archive_full_text"], query_count)
        self.assertIn("pending_manual_observation", " ".join(report["conclusions"]))

    def test_recommendation_and_alternatives_are_explicit(self):
        report = _load_report()
        self.assertEqual(report["recommended_next_milestone"], "Hard Eval Satisfaction Pack v0")
        self.assertIn("Old-Platform Result Refinement Pack v0", report["alternatives_considered"])
        self.assertIn("More Source Coverage Expansion v1", report["alternatives_considered"])
        self.assertIn("Rust Query Planner Parity Candidate v0", report["alternatives_considered"])

    def test_do_not_do_guards_are_explicit(self):
        forbidden_next = " ".join(_load_report()["do_not_do"]).lower()
        for phrase in [
            "live crawling",
            "google scraping",
            "internet archive scraping",
            "vector",
            "llm planning",
            "production hosting",
            "native apps",
            "broad rust rewrite",
            "arbitrary local filesystem ingestion",
        ]:
            self.assertIn(phrase, forbidden_next)

    def test_docs_explain_baseline_limitations(self):
        readme = _read("README.md").lower()
        baseline = _read("BASELINE.md").lower()

        self.assertIn("machine-readable", readme)
        self.assertIn("historical/reported", readme)
        self.assertIn("not external baseline data", baseline)
        self.assertIn("per-query movement", baseline)

    def test_report_identifies_remaining_gaps(self):
        report = _load_report()
        self.assertGreater(report["current"]["failure_mode_counts"]["source_coverage_gap"], 0)
        self.assertGreater(report["current"]["failure_mode_counts"]["compatibility_evidence_gap"], 0)
        self.assertIn("source_coverage_gap", _read("FAILURE_MODE_DELTA.md"))
        self.assertIn("not_satisfied", _read("ARCHIVE_EVAL_DELTA.md"))

    def test_no_false_external_or_hosting_claims(self):
        combined = "\n".join(_read(name).lower() for name in REQUIRED_FILES if name.endswith(".md"))
        forbidden_positive_claims = [
            "google baselines were observed",
            "internet archive baselines were observed",
            "beats google",
            "beats internet archive",
            "production ready",
            "production-ready",
            "not_satisfied is success",
        ]
        for claim in forbidden_positive_claims:
            self.assertNotIn(claim, combined)
        self.assertIn("does not change retrieval behavior", combined)


if __name__ == "__main__":
    unittest.main()
