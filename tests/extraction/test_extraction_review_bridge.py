import json
import unittest
from pathlib import Path

from runtime.extraction.review_bridge import (
    build_extraction_evidence_candidate_preview,
    build_extraction_review_seed,
    build_extraction_source_cache_candidate_preview,
    validate_extraction_review_seed,
)
from runtime.extraction.search_integration import load_extraction_search_policy


REPO_ROOT = Path(__file__).resolve().parents[2]


def load_effect(effect_type: str) -> dict:
    result = json.loads((REPO_ROOT / "examples" / "extraction" / "results" / "zip_manifest_tier2_result_v0.json").read_text(encoding="utf-8"))
    return [item for item in result["candidate_effects"] if item["effect_type"] == effect_type][0]


class ExtractionReviewBridgeTest(unittest.TestCase):
    def setUp(self):
        self.policy = load_extraction_search_policy()

    def test_member_candidate_creates_review_seed(self):
        seed = build_extraction_review_seed(load_effect("member_candidate"), self.policy)
        self.assertEqual(seed["subject_type"], "extraction_member_candidate")
        self.assertFalse(seed["truth_boundary"]["review_seed_is_review_decision"])

    def test_manifest_candidate_creates_review_seed(self):
        seed = build_extraction_review_seed(load_effect("manifest_candidate"), self.policy)
        self.assertEqual(seed["subject_type"], "extraction_manifest_candidate")

    def test_candidate_effect_creates_previews_only(self):
        effect = load_effect("manifest_candidate")
        evidence = build_extraction_evidence_candidate_preview(effect, self.policy)
        source = build_extraction_source_cache_candidate_preview(effect, self.policy)
        self.assertFalse(evidence["evidence_preview_is_accepted_evidence"])
        self.assertFalse(source["accepted_source_truth"])

    def test_review_seed_is_not_review_decision(self):
        seed = build_extraction_review_seed(load_effect("member_candidate"), self.policy)
        seed["truth_boundary"]["review_seed_is_review_decision"] = True
        with self.assertRaises(ValueError):
            validate_extraction_review_seed(seed, self.policy)


if __name__ == "__main__":
    unittest.main()
