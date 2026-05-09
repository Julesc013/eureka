from __future__ import annotations

import json
from pathlib import Path
import unittest

from runtime.search_quality.explanation import (
    build_search_result_explanation,
    explain_candidate_result,
    explain_evidence_supported_result,
    explain_extraction_member_result,
    explain_source_cache_supported_result,
)
from runtime.search_quality.explanation_summary import build_explanation_output_bundle
from runtime.search_quality.gap_explanation import build_search_gap_explanation


ROOT = Path(__file__).resolve().parents[2]


def load(rel: str):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


class SearchExplanationRuntimeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.bundle = load("examples/search_quality/input_bundles/software_search_explanation_bundle_v0.json")

    def test_candidate_result_explanation_builds(self) -> None:
        record = explain_candidate_result(self.bundle["candidate_records"][0], self.bundle)
        self.assertEqual(record["schema_version"], "search_result_explanation.v0")
        self.assertFalse(record["truth_boundary"]["explanation_accepts_candidate"])
        self.assertFalse(record["truth_boundary"]["explanation_mutates_ranking"])

    def test_source_cache_supported_explanation_builds(self) -> None:
        record = explain_source_cache_supported_result(self.bundle["source_cache_records"][0], self.bundle)
        self.assertEqual(record["result_kind"], "source_cache_record")
        self.assertFalse(record["product_boundary"]["changed_public_search_behavior"])

    def test_evidence_supported_explanation_builds(self) -> None:
        record = explain_evidence_supported_result(self.bundle["evidence_records"][0], self.bundle)
        self.assertEqual(record["result_kind"], "evidence_record")
        self.assertFalse(record["truth_boundary"]["explanation_accepts_evidence"])

    def test_extraction_member_explanation_builds(self) -> None:
        record = explain_extraction_member_result(self.bundle["extraction_search_gaps"][0], self.bundle)
        self.assertEqual(record["result_kind"], "extraction_search_gap")
        self.assertFalse(record["truth_boundary"]["explanation_mutates_public_search"])

    def test_policy_blocked_explanation_builds(self) -> None:
        blocked = load("examples/search_quality/input_bundles/extraction_gap_explanation_bundle_v0.json")
        record = build_search_result_explanation(blocked)
        self.assertEqual(record["explanation_status"], "policy_blocked")

    def test_search_gap_explanation_builds_from_extraction_gap(self) -> None:
        record = build_search_gap_explanation(self.bundle["extraction_search_gaps"][0])
        self.assertEqual(record["schema_version"], "search_gap_explanation.v0")
        self.assertFalse(record["truth_boundary"]["explanation_mutates_public_index"])

    def test_explanation_output_bundle_builds(self) -> None:
        output = build_explanation_output_bundle(self.bundle)
        self.assertEqual(output["schema_version"], "explanation_output_bundle.v0")
        self.assertGreaterEqual(len(output["result_explanations"]), 4)
        self.assertFalse(output["truth_boundary"]["explanation_mutates_public_search"])


if __name__ == "__main__":
    unittest.main()
