import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
TRIAGE_ROOT = REPO_ROOT / "control" / "backlog" / "search_usefulness_triage"

REQUIRED_DOCS = [
    "README.md",
    "TRIAGE_SUMMARY.md",
    "QUERY_FAILURE_MATRIX.md",
    "SOURCE_COVERAGE_PRIORITIES.md",
    "PLANNER_GAP_PRIORITIES.md",
    "MEMBER_DISCOVERY_PRIORITIES.md",
    "COMPATIBILITY_EVIDENCE_PRIORITIES.md",
    "NEXT_10_TASKS.md",
    "SELECTED_WEDGES.md",
    "REJECTED_OR_DEFERRED_WORK.md",
    "backlog_item.schema.json",
    "backlog_items.json",
]


def _read(relative_name: str) -> str:
    return (TRIAGE_ROOT / relative_name).read_text(encoding="utf-8")


def _load_items() -> dict:
    return json.loads(_read("backlog_items.json"))


class SearchUsefulnessBacklogTriageTest(unittest.TestCase):
    def test_triage_pack_files_exist(self):
        self.assertTrue((REPO_ROOT / "control" / "backlog" / "README.md").exists())
        missing = [name for name in REQUIRED_DOCS if not (TRIAGE_ROOT / name).exists()]
        self.assertEqual(missing, [])

    def test_backlog_items_parse_and_have_selected_next_milestone(self):
        payload = _load_items()
        items = payload["items"]
        selected = [item for item in items if item["status"] == "selected"]

        self.assertGreaterEqual(len(items), 10)
        self.assertEqual(len(selected), 1)
        self.assertEqual(selected[0]["title"], payload["immediate_next_milestone"])
        self.assertEqual(
            payload["immediate_next_milestone"],
            "Manual Observation Batch 0 Execution",
        )
        self.assertEqual(payload["selected_primary_wedge"], "old_platform_software")
        self.assertEqual(payload["selected_secondary_wedge"], "member_level_discovery")

    def test_required_backlog_items_are_present(self):
        titles = {item["title"] for item in _load_items()["items"]}
        required = {
            "Source Coverage and Capability Model v0",
            "Real Source Coverage Pack v0",
            "Old-Platform Software Planner Pack v0",
            "Member-Level Synthetic Records v0",
            "Result Lanes + User-Cost Ranking v0",
            "Compatibility Evidence Pack v0",
            "Search Usefulness Audit Delta v0",
            "Old-Platform Source Coverage Expansion v0",
            "Search Usefulness Audit Delta v1",
            "Hard Eval Satisfaction Pack v0",
            "Old-Platform Result Refinement Pack v0",
            "More Source Coverage Expansion v1",
            "Article/Scan Fixture Pack v0",
            "Manual External Baseline Observation Pack v0",
            "Manual Observation Batch 0",
            "Manual Observation Batch 0 Execution",
            "Rust Query Planner Parity Candidate v0",
            "Public Alpha Rehearsal Evidence v0",
            "Compatibility Surface Strategy v0",
        }
        self.assertTrue(required.issubset(titles))

    def test_selected_wedges_are_explicit(self):
        text = _read("SELECTED_WEDGES.md").lower()
        self.assertIn("primary wedge: old-platform-compatible software search", text)
        self.assertIn("secondary wedge: member-level discovery inside bundles", text)
        self.assertIn("member target refs", text)
        self.assertIn("windows 7", text)

    def test_priority_docs_cover_required_topics(self):
        source = _read("SOURCE_COVERAGE_PRIORITIES.md").lower()
        planner = _read("PLANNER_GAP_PRIORITIES.md").lower()
        member = _read("MEMBER_DISCOVERY_PRIORITIES.md").lower()
        compat = _read("COMPATIBILITY_EVIDENCE_PRIORITIES.md").lower()

        self.assertIn("internet archive recorded metadata", source)
        self.assertIn("local bundle fixture corpus", source)
        self.assertIn("recorded fixtures come before live crawling", source)
        self.assertIn("os alias graph", planner)
        self.assertIn("windows nt marketing names", planner)
        self.assertIn("app-vs-operating-system-media suppression", planner)
        self.assertIn("parent lineage", member)
        self.assertIn("member target refs", member)
        self.assertIn("windows 7 / nt 6.1", compat)
        self.assertIn("unknown compatibility", compat)

    def test_query_matrix_references_search_usefulness_corpus(self):
        text = _read("QUERY_FAILURE_MATRIX.md")
        self.assertIn("Search Usefulness Audit v0", text)
        self.assertIn("windows_7_apps", text)
        self.assertIn("latest_firefox_before_xp_support_ended", text)
        self.assertIn("driver_inf_inside_support_cd", text)
        self.assertIn("external baseline status", text.lower())

    def test_deferred_work_is_explicit(self):
        text = _read("REJECTED_OR_DEFERRED_WORK.md").lower()
        for phrase in [
            "live crawling",
            "vector search",
            "llm planning",
            "production hosting",
            "native apps",
            "broad rust rewrite",
        ]:
            self.assertIn(phrase, text)

    def test_no_fake_claims_or_runtime_behavior_claims(self):
        combined = "\n".join(_read(name).lower() for name in REQUIRED_DOCS if name.endswith(".md"))
        forbidden_positive_claims = [
            "new runtime behavior was implemented",
            "runtime behavior is implemented by this triage",
            "google baselines were observed",
            "internet archive baselines were observed",
            "production ready",
            "production-ready",
            "beats google",
            "beats internet archive",
        ]
        for claim in forbidden_positive_claims:
            self.assertNotIn(claim, combined)
        self.assertIn("pending_manual_observation", combined)
        self.assertIn("does not change runtime behavior", combined)


if __name__ == "__main__":
    unittest.main()
