import json
import unittest
from pathlib import Path

from runtime.extraction.guards import detect_truth_or_product_violations
from runtime.extraction.search_integration import (
    build_extraction_search_gap,
    build_extraction_search_integration,
    build_local_search_preview_from_extraction,
    load_extraction_search_policy,
)
from runtime.extraction.usefulness import build_extraction_usefulness_report, build_track_g_readiness_recommendation


REPO_ROOT = Path(__file__).resolve().parents[2]


def load_result(name: str) -> dict:
    return json.loads((REPO_ROOT / "examples" / "extraction" / "results" / name).read_text(encoding="utf-8"))


class ExtractionSearchIntegrationTest(unittest.TestCase):
    def setUp(self):
        self.policy = load_extraction_search_policy()

    def test_extraction_result_creates_hidden_member_search_gap(self):
        gaps = build_extraction_search_gap(load_result("zip_basic_tier1_result_v0.json"), self.policy)
        self.assertIn("hidden_member_not_indexed", {gap["gap_type"] for gap in gaps})

    def test_manifest_candidate_creates_manifest_search_gap(self):
        gaps = build_extraction_search_gap(load_result("zip_manifest_tier2_result_v0.json"), self.policy)
        self.assertIn("manifest_not_indexed", {gap["gap_type"] for gap in gaps})

    def test_policy_blocked_extraction_result_creates_blocked_gap(self):
        gaps = build_extraction_search_gap(load_result("path_traversal_blocked_result_v0.json"), self.policy)
        blocked = [gap for gap in gaps if gap["gap_type"] == "policy_blocked_extraction_gap"]
        self.assertTrue(blocked)
        self.assertFalse(blocked[0]["truth_boundary"]["public_index_mutated"])

    def test_local_search_preview_does_not_mutate_public_search(self):
        preview = build_local_search_preview_from_extraction(load_result("zip_manifest_tier2_result_v0.json"), self.policy)
        self.assertFalse(preview["public_search_mutated"])
        self.assertFalse(preview["product_boundary"]["changed_public_search_behavior"])

    def test_integration_builds_track_g_ready_usefulness(self):
        integration = build_extraction_search_integration([load_result("zip_manifest_tier2_result_v0.json")], self.policy)
        report = build_extraction_usefulness_report([integration], self.policy)
        handoff = build_track_g_readiness_recommendation(report, self.policy)
        self.assertEqual(handoff["track_g_readiness"], "READY_FOR_G_BUNDLE_01")
        self.assertFalse(report["truth_boundary"]["production_quality_claimed"])

    def test_public_master_and_claim_violations_are_rejected(self):
        integration = build_extraction_search_integration([load_result("zip_manifest_tier2_result_v0.json")], self.policy)
        integration["truth_boundary"]["integration_mutates_public_index"] = True
        self.assertTrue(detect_truth_or_product_violations(integration))


if __name__ == "__main__":
    unittest.main()
