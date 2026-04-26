import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
DELTA_ROOT = REPO_ROOT / "control" / "audits" / "search-usefulness-delta-v0"
QUERY_PACK = REPO_ROOT / "evals" / "search_usefulness" / "queries" / "search_usefulness_v0.json"

REQUIRED_FILES = [
    "README.md",
    "BASELINE.md",
    "CURRENT_RESULTS.md",
    "DELTA_SUMMARY.md",
    "WEDGE_DELTA.md",
    "FAILURE_MODE_DELTA.md",
    "QUERY_MOVEMENT.md",
    "NEXT_RECOMMENDATIONS.md",
    "delta_report.json",
]


def _read(name: str) -> str:
    return (DELTA_ROOT / name).read_text(encoding="utf-8")


def _load_report() -> dict:
    return json.loads(_read("delta_report.json"))


class SearchUsefulnessAuditDeltaTest(unittest.TestCase):
    def test_delta_pack_files_exist(self):
        self.assertTrue(DELTA_ROOT.exists())
        missing = [name for name in REQUIRED_FILES if not (DELTA_ROOT / name).exists()]
        self.assertEqual(missing, [])

    def test_delta_report_parses_and_names_wedges(self):
        report = _load_report()
        self.assertEqual(report["report_id"], "search_usefulness_delta_v0")
        self.assertEqual(report["selected_wedges"]["primary"], "old_platform_compatible_software_search")
        self.assertEqual(report["selected_wedges"]["secondary"], "member_level_discovery_inside_bundles")
        self.assertEqual(report["recommended_next_milestone"], "Old-Platform Source Coverage Expansion v0")

    def test_current_query_count_matches_query_pack(self):
        report = _load_report()
        query_pack = json.loads(QUERY_PACK.read_text(encoding="utf-8"))
        query_count = len(query_pack["queries"])

        self.assertGreaterEqual(report["current"]["query_count"], 64)
        self.assertEqual(report["current"]["query_count"], query_count)

    def test_external_baselines_remain_pending(self):
        report = _load_report()
        pending = report["current"]["external_baseline_pending_counts"]
        query_count = report["current"]["query_count"]

        self.assertEqual(pending["google"], query_count)
        self.assertEqual(pending["internet_archive_metadata"], query_count)
        self.assertEqual(pending["internet_archive_full_text"], query_count)
        self.assertIn("pending_manual_observation", " ".join(report["conclusions"]))

    def test_delta_values_capture_modest_movement(self):
        report = _load_report()
        changes = report["delta"]["status_count_changes"]

        self.assertEqual(changes["partial"], 4)
        self.assertEqual(changes["source_gap"], -2)
        self.assertEqual(changes["capability_gap"], -2)
        self.assertEqual(report["current"]["status_counts"]["source_gap"], 41)
        self.assertGreater(report["current"]["failure_mode_counts"]["source_coverage_gap"], 40)

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
        ]:
            self.assertIn(phrase, forbidden_next)

    def test_docs_explain_baseline_limitations(self):
        readme = _read("README.md").lower()
        baseline = _read("BASELINE.md").lower()

        self.assertIn("historical reported baseline", readme)
        self.assertIn("machine-derived", readme)
        self.assertIn("not external baseline data", baseline)
        self.assertIn("aggregate-level", baseline)

    def test_report_identifies_source_coverage_as_remaining_gap(self):
        report = _load_report()
        self.assertIn("Old-Platform Source Coverage Expansion v0", report["recommended_next_milestone"])
        self.assertGreater(report["current"]["failure_mode_counts"]["source_coverage_gap"], 0)
        self.assertTrue(report["delta"]["unchanged_queries"]["source_gap_still_dominant"])
        self.assertIn("source_coverage_gap", _read("FAILURE_MODE_DELTA.md"))

    def test_no_false_external_or_hosting_claims(self):
        combined = "\n".join(_read(name).lower() for name in REQUIRED_FILES if name.endswith(".md"))
        forbidden_positive_claims = [
            "google baselines were observed",
            "internet archive baselines were observed",
            "beats google",
            "beats internet archive",
            "production ready",
            "production-ready",
        ]
        for claim in forbidden_positive_claims:
            self.assertNotIn(claim, combined)
        self.assertIn("does not change retrieval behavior", combined)


if __name__ == "__main__":
    unittest.main()
