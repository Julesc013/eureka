import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "contracts" / "query" / "known_absence_page.v0.json"
POLICY = ROOT / "control" / "inventory" / "query_intelligence" / "known_absence_page_policy.json"
REPORT = ROOT / "control" / "audits" / "known-absence-page-v0" / "known_absence_page_report.json"
EXAMPLES = ROOT / "examples" / "known_absence_pages"


class KnownAbsencePageOperationsTests(unittest.TestCase):
    def test_schema_policy_report_and_examples_exist(self) -> None:
        self.assertTrue(CONTRACT.is_file())
        self.assertTrue(POLICY.is_file())
        self.assertTrue(REPORT.is_file())
        self.assertGreaterEqual(len([path for path in EXAMPLES.iterdir() if path.is_dir()]), 3)
        self.assertEqual(json.loads(CONTRACT.read_text(encoding="utf-8"))["x-status"], "contract_only")

    def test_policy_hard_flags(self) -> None:
        policy = json.loads(POLICY.read_text(encoding="utf-8"))
        for key in (
            "runtime_known_absence_pages_implemented",
            "persistent_known_absence_store_implemented",
            "telemetry_implemented",
            "public_query_logging_enabled",
            "global_absence_claims_allowed",
            "live_probe_execution_allowed",
            "downloads_enabled",
            "uploads_enabled",
            "installs_enabled",
            "arbitrary_url_fetch_enabled",
            "source_cache_mutation_allowed",
            "evidence_ledger_mutation_allowed",
            "candidate_index_mutation_allowed",
            "candidate_promotion_runtime_implemented",
            "master_index_mutation_allowed",
        ):
            self.assertFalse(policy[key], key)
        self.assertEqual(policy["raw_query_retention_default"], "none")
        self.assertTrue(policy["privacy_filter_required"])
        self.assertTrue(policy["scoped_absence_required"])

    def test_example_boundaries(self) -> None:
        for page_path in sorted(EXAMPLES.glob("*/KNOWN_ABSENCE_PAGE.json")):
            with self.subTest(path=page_path):
                payload = json.loads(page_path.read_text(encoding="utf-8"))
                self.assertFalse(payload["query_context"]["raw_query_retained"])
                self.assertFalse(payload["absence_summary"]["global_absence_claimed"])
                self.assertFalse(payload["absence_summary"]["exhaustive_search_claimed"])
                for field in (
                    "global_absence_claimed",
                    "exhaustive_search_claimed",
                    "live_probes_performed",
                    "external_calls_performed",
                    "downloads_enabled",
                    "uploads_enabled",
                    "installs_enabled",
                    "arbitrary_url_fetch_enabled",
                ):
                    self.assertFalse(payload["no_global_absence_guarantees"][field], field)
                for field in (
                    "master_index_mutated",
                    "public_index_mutated",
                    "local_index_mutated",
                    "candidate_index_mutated",
                    "source_cache_mutated",
                    "evidence_ledger_mutated",
                    "telemetry_exported",
                ):
                    self.assertFalse(payload["no_mutation_guarantees"][field], field)
                self.assertFalse(payload["candidate_context"]["candidate_index_runtime_implemented"])
                self.assertFalse(payload["candidate_context"]["candidate_promotion_runtime_implemented"])
                self.assertIn("no_global_absence_notice", payload["user_facing_sections"])
                self.assertTrue(payload["gap_explanations"])
                for action in payload["safe_next_actions"]:
                    if action["enabled_now"]:
                        self.assertIn(action["action_type"], {"refine_query", "view_near_misses", "view_checked_sources"})

    def test_docs_state_contract_only_no_runtime_no_global_absence(self) -> None:
        text = (ROOT / "docs" / "reference" / "KNOWN_ABSENCE_PAGE_CONTRACT.md").read_text(encoding="utf-8").casefold()
        for phrase in (
            "scoped absence, not global absence",
            "known absence page is not a runtime page yet",
            "known absence page is not evidence acceptance",
            "known absence page is not candidate promotion",
            "known absence page is not master-index mutation",
            "no download/install/upload/live fetch",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
