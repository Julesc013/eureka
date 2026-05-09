from __future__ import annotations

import json
from pathlib import Path
import unittest

from runtime.search_quality.dedup_shadow import build_dedup_shadow
from runtime.search_quality.identity_shadow import build_identity_merge_shadow
from runtime.search_quality.public_ranking_gate import build_public_ranking_gate
from runtime.search_quality.quality_harness import build_search_quality_regression_report, detect_quality_overclaim
from runtime.search_quality.ranking_shadow import build_ranking_output_bundle, build_ranking_shadow


ROOT = Path(__file__).resolve().parents[2]


def load(rel: str):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


class SearchQualityHarnessTests(unittest.TestCase):
    def setUp(self) -> None:
        self.query_set = load("examples/search_quality/query_sets/minimal_search_quality_query_set_v0.json")
        self.bundle = load("examples/search_quality/ranking/input_bundle_software_v0.json")
        ranking = build_ranking_shadow(self.bundle)
        identity = build_identity_merge_shadow(self.bundle["items"])
        dedup = build_dedup_shadow(self.bundle["items"])
        self.output = build_ranking_output_bundle(self.bundle, ranking, identity, dedup)

    def test_search_quality_regression_report_builds(self) -> None:
        report = build_search_quality_regression_report(self.query_set, [self.output])
        self.assertEqual(report["schema_version"], "search_quality_regression_report.v0")
        self.assertEqual(report["metrics"]["exact_expected_present"], 1)
        self.assertFalse(report["truth_boundary"]["production_quality_claimed"])

    def test_public_ranking_gate_remains_blocked_current(self) -> None:
        report = build_search_quality_regression_report(self.query_set, [self.output])
        gate = build_public_ranking_gate([report])
        self.assertEqual(gate["gate_status"], "blocked_current")
        self.assertFalse(gate["product_boundary"]["changed_ranking_behavior"])

    def test_quality_overclaim_is_rejected(self) -> None:
        report = build_search_quality_regression_report(self.query_set, [self.output])
        report["beats_google"] = True
        self.assertTrue(detect_quality_overclaim(report))


if __name__ == "__main__":
    unittest.main()
