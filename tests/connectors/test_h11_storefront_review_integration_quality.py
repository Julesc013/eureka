"""Tests for H11 storefront review integration quality helpers."""

from __future__ import annotations

from pathlib import Path
import unittest

from runtime.connectors.h11_storefront.quality_delta import build_h11_quality_delta, detect_h11_quality_overclaim
from runtime.connectors.h11_storefront.review_integration import (
    build_h11_review_integration_result,
    detect_h11_review_product_boundary_violations,
    detect_h11_review_truth_boundary_violations,
    load_h11_storefront_outputs,
)
from runtime.connectors.h11_storefront.wave_postmortem import build_h11_connector_wave_postmortem, build_h11_next_phase_recommendation

ROOT = Path(__file__).resolve().parents[2]


class H11ReviewIntegrationQualityTests(unittest.TestCase):
    def _review(self, include_live: bool = False):
        paths = sorted((ROOT / "examples/connectors/h11_storefront/replay_results").glob("*.json"))
        if include_live:
            paths += sorted((ROOT / "examples/connectors/h11_storefront/live_probe_results").glob("*.json"))
        outputs = load_h11_storefront_outputs(paths)
        return build_h11_review_integration_result({"outputs": outputs, "input_refs": [str(p) for p in paths]})

    def test_review_integration_builds_seeds_from_fixture_outputs(self):
        review = self._review()
        self.assertEqual(16, len(review["sources"]))
        self.assertEqual(16, len(review["storefront_listing_identity_review_seeds"]))
        self.assertEqual(16, len(review["app_product_identity_review_seeds"]))
        self.assertEqual(16, len(review["version_release_channel_review_seeds"]))
        self.assertEqual(16, len(review["price_availability_region_review_seeds"]))
        self.assertEqual(16, len(review["acquisition_path_review_seeds"]))
        self.assertEqual(16, len(review["review_rating_metadata_review_seeds"]))
        self.assertEqual(16, len(review["account_entitlement_boundary_review_seeds"]))
        self.assertEqual(16, len(review["storefront_rights_safety_review_seeds"]))
        self.assertEqual(16, len(review["source_cache_review_seeds"]))
        self.assertEqual(16, len(review["evidence_candidate_review_seeds"]))
        self.assertFalse(review["accepts_listing_identity_truth"])
        self.assertFalse(review["enables_downloads"])

    def test_review_integration_builds_seeds_from_mocked_live_probe_outputs(self):
        review = self._review(include_live=True)
        self.assertGreaterEqual(len(review["used_live_probe_outputs"]), 1)
        self.assertFalse(review["product_boundary"]["enabled_downloads"])
        self.assertFalse(review["truth_boundary"]["listing_identity_seed_accepts_listing_truth"])

    def test_review_seeds_and_previews_do_not_accept_truth(self):
        review = self._review(include_live=True)
        self.assertEqual([], detect_h11_review_truth_boundary_violations(review))
        self.assertEqual([], detect_h11_review_product_boundary_violations(review))
        self.assertFalse(review["storefront_listing_identity_review_seeds"][0]["accepted_listing_identity_truth"])
        self.assertFalse(review["app_product_identity_review_seeds"][0]["app_product_seed_accepts_product_truth"])
        self.assertFalse(review["version_release_channel_review_seeds"][0]["version_release_seed_accepts_version_truth"])
        self.assertFalse(review["price_availability_region_review_seeds"][0]["current_price_verified"])
        self.assertFalse(review["acquisition_path_review_seeds"][0]["accepted_acquisition_permission"])
        self.assertFalse(review["review_rating_metadata_review_seeds"][0]["review_correctness_verified"])
        self.assertFalse(review["account_entitlement_boundary_review_seeds"][0]["license_entitlement_verified"])
        self.assertFalse(review["storefront_rights_safety_review_seeds"][0]["rights_clearance_claimed"])
        self.assertFalse(review["source_cache_review_seeds"][0]["accepted_source_truth"])
        self.assertFalse(review["evidence_candidate_review_seeds"][0]["accepted_evidence_truth"])
        self.assertFalse(review["candidate_promotion_previews"][0]["candidate_promotion_preview_promotes_candidate"])
        self.assertFalse(review["source_pack_update_previews"][0]["source_pack_preview_is_imported_or_submitted"])

    def test_quality_delta_and_postmortem_boundaries(self):
        review = self._review(include_live=True)
        delta = build_h11_quality_delta({"review_integration_result": review})
        self.assertEqual(16, delta["source_count"])
        self.assertEqual([], detect_h11_quality_overclaim(delta))
        postmortem = build_h11_connector_wave_postmortem(review, delta)
        self.assertFalse(postmortem["auto_approves_future_connectors"])
        recommendation = build_h11_next_phase_recommendation(postmortem)
        self.assertEqual("READY_FOR_H12_BUNDLE_01", recommendation["recommendation_status"])

    def test_forbidden_claims_are_rejected(self):
        review = self._review()
        review["public_index_mutated"] = True
        self.assertTrue(detect_h11_review_truth_boundary_violations(review))
        review["public_index_mutated"] = False
        review["product_boundary"]["enabled_downloads"] = True
        self.assertTrue(detect_h11_review_product_boundary_violations(review))
        delta = build_h11_quality_delta({"review_integration_result": self._review()})
        delta["truth_boundary"]["current_price_verified"] = True
        self.assertTrue(detect_h11_quality_overclaim(delta))


if __name__ == "__main__":
    unittest.main()
