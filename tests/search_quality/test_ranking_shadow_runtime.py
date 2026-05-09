from __future__ import annotations

import json
from pathlib import Path
import unittest

from runtime.search_quality.ranking_factors import (
    score_exact_identifier_match,
    score_platform_or_compatibility_match,
    score_version_match,
)
from runtime.search_quality.ranking_shadow import build_ranking_shadow, score_ranking_item


ROOT = Path(__file__).resolve().parents[2]


def load(rel: str):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


class RankingShadowRuntimeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.bundle = load("examples/search_quality/ranking/input_bundle_software_v0.json")

    def test_ranking_shadow_builds_from_fixture_input_bundle(self) -> None:
        result = build_ranking_shadow(self.bundle)
        self.assertEqual(result["schema_version"], "ranking_shadow_result.v0")
        self.assertEqual(result["ranked_items"][0]["item_ref"], "candidate.search_need.software_version.v0")
        self.assertFalse(result["truth_boundary"]["ranking_shadow_mutates_public_ranking"])

    def test_ranking_factors_are_deterministic(self) -> None:
        item = self.bundle["items"][0]
        first = score_ranking_item(item, {}, self.bundle["query_context"])
        second = score_ranking_item(item, {}, self.bundle["query_context"])
        self.assertEqual(first, second)

    def test_exact_identifier_factor_scores_expected_case(self) -> None:
        score = score_exact_identifier_match(self.bundle["items"][0], self.bundle["query_context"])
        self.assertEqual(score, 1.0)

    def test_version_platform_compatibility_factors_score_expected_case(self) -> None:
        item = self.bundle["items"][0]
        context = self.bundle["query_context"]
        self.assertEqual(score_version_match(item, context), 1.0)
        self.assertEqual(score_platform_or_compatibility_match(item, context), 1.0)

    def test_near_miss_penalty_applies(self) -> None:
        result = build_ranking_shadow(self.bundle)
        near = next(item for item in result["ranked_items"] if item["item_ref"] == "candidate.near_miss.wrong_version.v0")
        exact = result["ranked_items"][0]
        self.assertLess(near["shadow_score"], exact["shadow_score"])

    def test_known_absence_signal_is_shadow_only(self) -> None:
        bundle = load("examples/search_quality/ranking/input_bundle_extraction_gap_v0.json")
        result = build_ranking_shadow(bundle)
        self.assertEqual(result["ranking_shadow_status"], "blocked_by_policy")
        self.assertFalse(result["truth_boundary"]["ranking_shadow_mutates_public_search"])


if __name__ == "__main__":
    unittest.main()
