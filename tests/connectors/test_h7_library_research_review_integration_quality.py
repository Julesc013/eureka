"""Tests for H7 library/cultural/research review integration quality helpers."""

from __future__ import annotations

from pathlib import Path
import unittest

from control.prototypes.legacy_runtime.connectors.h7_library_research.quality_delta import build_h7_quality_delta, detect_h7_quality_overclaim
from control.prototypes.legacy_runtime.connectors.h7_library_research.review_integration import (
    build_h7_review_integration_result,
    detect_h7_review_product_boundary_violations,
    detect_h7_review_truth_boundary_violations,
    load_h7_library_research_outputs,
)
from control.prototypes.legacy_runtime.connectors.h7_library_research.wave_postmortem import build_h7_connector_wave_postmortem, build_h7_next_phase_recommendation

ROOT = Path(__file__).resolve().parents[2]


class H7ReviewIntegrationQualityTests(unittest.TestCase):
    def _review(self, include_live: bool = False):
        paths = sorted((ROOT / "examples/connectors/h7_library_research/replay_results").glob("*.json"))
        if include_live:
            paths += sorted((ROOT / "examples/connectors/h7_library_research/live_probe_results").glob("*.json"))
        outputs = load_h7_library_research_outputs(paths)
        return build_h7_review_integration_result({"outputs": outputs, "input_refs": [str(p) for p in paths]})

    def test_review_integration_builds_seeds_from_fixture_outputs(self):
        review = self._review()
        self.assertEqual(30, len(review["sources"]))
        self.assertEqual(30, len(review["bibliographic_identity_review_seeds"]))
        self.assertEqual(30, len(review["research_work_identity_review_seeds"]))
        self.assertEqual(30, len(review["dataset_identity_review_seeds"]))
        self.assertEqual(30, len(review["cultural_object_identity_review_seeds"]))
        self.assertEqual(30, len(review["patent_identity_review_seeds"]))
        self.assertEqual(30, len(review["citation_relation_review_seeds"]))
        self.assertEqual(30, len(review["access_rights_availability_review_seeds"]))
        self.assertEqual(30, len(review["source_cache_review_seeds"]))
        self.assertEqual(30, len(review["evidence_candidate_review_seeds"]))
        self.assertFalse(review["accepts_bibliographic_truth"])
        self.assertFalse(review["enables_oai_pmh_harvest"])

    def test_review_integration_builds_seeds_from_mocked_live_probe_outputs(self):
        review = self._review(include_live=True)
        self.assertGreaterEqual(len(review["blocked_sources"]), 1)
        self.assertFalse(review["product_boundary"]["enabled_harvesting"])
        self.assertFalse(review["truth_boundary"]["bibliographic_seed_accepts_bibliographic_truth"])

    def test_review_seeds_and_previews_do_not_accept_truth(self):
        review = self._review(include_live=True)
        self.assertEqual([], detect_h7_review_truth_boundary_violations(review))
        self.assertEqual([], detect_h7_review_product_boundary_violations(review))
        self.assertFalse(review["bibliographic_identity_review_seeds"][0]["accepted_bibliographic_truth"])
        self.assertFalse(review["research_work_identity_review_seeds"][0]["accepted_research_work_truth"])
        self.assertFalse(review["dataset_identity_review_seeds"][0]["dataset_validity_verified"])
        self.assertFalse(review["cultural_object_identity_review_seeds"][0]["cultural_object_seed_accepts_object_truth"])
        self.assertFalse(review["patent_identity_review_seeds"][0]["patent_validity_verified"])
        self.assertFalse(review["citation_relation_review_seeds"][0]["citation_correctness_verified"])
        self.assertFalse(review["access_rights_availability_review_seeds"][0]["rights_clearance_claimed"])
        self.assertFalse(review["source_cache_review_seeds"][0]["accepted_source_truth"])
        self.assertFalse(review["evidence_candidate_review_seeds"][0]["accepted_evidence_truth"])
        self.assertFalse(review["candidate_promotion_previews"][0]["candidate_promotion_preview_promotes_candidate"])
        self.assertFalse(review["source_pack_update_previews"][0]["source_pack_preview_is_imported_or_submitted"])

    def test_quality_delta_and_postmortem_boundaries(self):
        review = self._review(include_live=True)
        delta = build_h7_quality_delta({"review_integration_result": review})
        self.assertEqual(30, delta["source_count"])
        self.assertGreaterEqual(delta["blocked_sources_count"], 1)
        self.assertEqual([], detect_h7_quality_overclaim(delta))
        postmortem = build_h7_connector_wave_postmortem(review, delta)
        self.assertFalse(postmortem["auto_approves_future_connectors"])
        recommendation = build_h7_next_phase_recommendation(postmortem)
        self.assertEqual("READY_FOR_H8_BUNDLE_01", recommendation["recommendation_status"])

    def test_forbidden_claims_are_rejected(self):
        review = self._review()
        review["public_index_mutated"] = True
        self.assertTrue(detect_h7_review_truth_boundary_violations(review))
        review["public_index_mutated"] = False
        review["product_boundary"]["enabled_harvesting"] = True
        self.assertTrue(detect_h7_review_product_boundary_violations(review))
        delta = build_h7_quality_delta({"review_integration_result": self._review()})
        delta["truth_boundary"]["citation_correctness_verified"] = True
        self.assertTrue(detect_h7_quality_overclaim(delta))


if __name__ == "__main__":
    unittest.main()
