"""Tests for H4 code/source/release review integration quality helpers."""

from __future__ import annotations

from pathlib import Path
import unittest

from runtime.connectors.h4_code_source_release.quality_delta import build_h4_quality_delta, detect_h4_quality_overclaim
from runtime.connectors.h4_code_source_release.review_integration import build_h4_review_integration_result, detect_h4_review_product_boundary_violations, detect_h4_review_truth_boundary_violations, load_h4_code_source_outputs
from runtime.connectors.h4_code_source_release.wave_postmortem import build_h4_connector_wave_postmortem, build_h4_next_phase_recommendation

ROOT = Path(__file__).resolve().parents[2]


class H4ReviewIntegrationQualityTests(unittest.TestCase):
    def _review(self, include_live: bool = False):
        paths = sorted((ROOT / "examples/connectors/h4_code_source_release/replay_results").glob("*.json"))
        if include_live:
            paths += sorted((ROOT / "examples/connectors/h4_code_source_release/live_probe_results").glob("*.json"))
        outputs = load_h4_code_source_outputs(paths)
        return build_h4_review_integration_result({"outputs": outputs, "input_refs": [str(p) for p in paths]})

    def test_review_integration_builds_seeds_from_fixture_outputs(self):
        review = self._review()
        self.assertEqual(10, len(review["sources"]))
        self.assertEqual(10, len(review["source_identity_review_seeds"]))
        self.assertEqual(10, len(review["release_identity_review_seeds"]))
        self.assertEqual(10, len(review["source_cache_review_seeds"]))
        self.assertEqual(10, len(review["evidence_candidate_review_seeds"]))
        self.assertFalse(review["accepts_source_identity_truth"])
        self.assertFalse(review["enables_repository_clone"])

    def test_review_integration_builds_seeds_from_mocked_live_probe_outputs(self):
        review = self._review(include_live=True)
        self.assertEqual(10, len(review["blocked_sources"]))
        self.assertFalse(review["product_boundary"]["repository_clone_enabled"])
        self.assertFalse(review["truth_boundary"]["source_to_binary_seed_accepts_provenance"])

    def test_review_seeds_and_previews_do_not_accept_truth(self):
        review = self._review(include_live=True)
        self.assertEqual([], detect_h4_review_truth_boundary_violations(review))
        self.assertEqual([], detect_h4_review_product_boundary_violations(review))
        self.assertFalse(review["source_identity_review_seeds"][0]["accepted_source_identity_truth"])
        self.assertFalse(review["release_identity_review_seeds"][0]["accepted_release_identity_truth"])
        self.assertFalse(review["source_to_binary_relation_review_seeds"][0]["accepted_source_to_binary_provenance"])
        self.assertFalse(review["release_asset_candidate_review_seeds"][0]["download_allowed_current"])
        self.assertFalse(review["release_asset_candidate_review_seeds"][0]["signature_metadata_proves_authenticity"])
        self.assertFalse(review["source_cache_review_seeds"][0]["accepted_source_truth"])
        self.assertFalse(review["evidence_candidate_review_seeds"][0]["accepted_evidence"])
        self.assertFalse(review["candidate_promotion_previews"][0]["candidate_promotion_preview_promotes_candidate"])
        self.assertFalse(review["source_pack_update_previews"][0]["source_pack_preview_is_imported_or_submitted"])

    def test_quality_delta_and_postmortem_boundaries(self):
        review = self._review(include_live=True)
        delta = build_h4_quality_delta({"review_integration_result": review})
        self.assertEqual(10, delta["source_count"])
        self.assertEqual(10, delta["blocked_sources_count"])
        self.assertEqual([], detect_h4_quality_overclaim(delta))
        postmortem = build_h4_connector_wave_postmortem(review, delta)
        self.assertFalse(postmortem["auto_approves_future_connectors"])
        recommendation = build_h4_next_phase_recommendation(postmortem)
        self.assertEqual("READY_FOR_H5_BUNDLE_01", recommendation["recommendation_status"])

    def test_forbidden_claims_are_rejected(self):
        review = self._review()
        review["public_index_mutated"] = True
        self.assertTrue(detect_h4_review_truth_boundary_violations(review))
        review["public_index_mutated"] = False
        review["product_boundary"]["repository_clone_enabled"] = True
        self.assertTrue(detect_h4_review_product_boundary_violations(review))
        delta = build_h4_quality_delta({"review_integration_result": self._review()})
        delta["truth_boundary"]["source_authenticity_verified"] = True
        self.assertTrue(detect_h4_quality_overclaim(delta))


if __name__ == "__main__":
    unittest.main()
