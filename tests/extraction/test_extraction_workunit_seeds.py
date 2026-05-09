import json
import unittest
from pathlib import Path

from runtime.extraction.search_integration import load_extraction_search_policy
from runtime.extraction.workunit_seeds import (
    build_extraction_workunit_seed,
    summarize_extraction_workunit_seed,
    validate_extraction_workunit_seed,
)


REPO_ROOT = Path(__file__).resolve().parents[2]


def load_result(name: str) -> dict:
    return json.loads((REPO_ROOT / "examples" / "extraction" / "results" / name).read_text(encoding="utf-8"))


class ExtractionWorkUnitSeedTest(unittest.TestCase):
    def setUp(self):
        self.policy = load_extraction_search_policy()

    def test_workunit_seed_created_but_not_executed(self):
        result = load_result("zip_manifest_tier2_result_v0.json")
        seed = build_extraction_workunit_seed(result, result["manifest_candidates"][0], self.policy)
        self.assertEqual(seed["proposed_workunit_type"], "verify_manifest_candidate_future")
        self.assertFalse(seed["workunit_seed_executes_work"])

    def test_member_workunit_seed(self):
        result = load_result("zip_basic_tier1_result_v0.json")
        seed = build_extraction_workunit_seed(result, result["member_listing"][0], self.policy)
        self.assertEqual(seed["proposed_workunit_type"], "check_member_relevance_future")
        self.assertTrue(summarize_extraction_workunit_seed(seed)["review_required"])

    def test_policy_blocked_workunit_seed(self):
        result = load_result("path_traversal_blocked_result_v0.json")
        seed = build_extraction_workunit_seed(result, None, self.policy)
        self.assertEqual(seed["proposed_workunit_type"], "policy_review_future")

    def test_workunit_execution_claim_is_rejected(self):
        result = load_result("zip_basic_tier1_result_v0.json")
        seed = build_extraction_workunit_seed(result, result["member_listing"][0], self.policy)
        seed["workunit_seed_executes_work"] = True
        with self.assertRaises(ValueError):
            validate_extraction_workunit_seed(seed, self.policy)


if __name__ == "__main__":
    unittest.main()
