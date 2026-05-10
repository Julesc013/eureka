"""Tests for H5 vendor/update/driver review integration quality helpers."""

from __future__ import annotations

from pathlib import Path
import unittest

from runtime.connectors.h5_vendor_update_driver.quality_delta import build_h5_quality_delta, detect_h5_quality_overclaim
from runtime.connectors.h5_vendor_update_driver.review_integration import (
    build_h5_review_integration_result,
    detect_h5_review_product_boundary_violations,
    detect_h5_review_truth_boundary_violations,
    load_h5_vendor_update_outputs,
)
from runtime.connectors.h5_vendor_update_driver.wave_postmortem import build_h5_connector_wave_postmortem, build_h5_next_phase_recommendation

ROOT = Path(__file__).resolve().parents[2]


class H5ReviewIntegrationQualityTests(unittest.TestCase):
    def _review(self, include_live: bool = False):
        paths = sorted((ROOT / "examples/connectors/h5_vendor_update_driver/replay_results").glob("*.json"))
        if include_live:
            paths += sorted((ROOT / "examples/connectors/h5_vendor_update_driver/live_probe_results").glob("*.json"))
        outputs = load_h5_vendor_update_outputs(paths)
        return build_h5_review_integration_result({"outputs": outputs, "input_refs": [str(p) for p in paths]})

    def test_review_integration_builds_seeds_from_fixture_outputs(self):
        review = self._review()
        self.assertEqual(15, len(review["sources"]))
        self.assertEqual(15, len(review["vendor_identity_review_seeds"]))
        self.assertEqual(15, len(review["driver_device_compatibility_review_seeds"]))
        self.assertEqual(15, len(review["firmware_update_review_seeds"]))
        self.assertEqual(15, len(review["runtime_redistributable_review_seeds"]))
        self.assertEqual(15, len(review["payload_metadata_review_seeds"]))
        self.assertEqual(15, len(review["source_cache_review_seeds"]))
        self.assertEqual(15, len(review["evidence_candidate_review_seeds"]))
        self.assertFalse(review["accepts_vendor_truth"])
        self.assertFalse(review["enables_downloads"])

    def test_review_integration_builds_seeds_from_mocked_live_probe_outputs(self):
        review = self._review(include_live=True)
        self.assertEqual(15, len(review["blocked_sources"]))
        self.assertFalse(review["product_boundary"]["enabled_catalog_sync"])
        self.assertFalse(review["truth_boundary"]["vendor_identity_seed_accepts_vendor_truth"])

    def test_review_seeds_and_previews_do_not_accept_truth(self):
        review = self._review(include_live=True)
        self.assertEqual([], detect_h5_review_truth_boundary_violations(review))
        self.assertEqual([], detect_h5_review_product_boundary_violations(review))
        self.assertFalse(review["vendor_identity_review_seeds"][0]["accepted_vendor_truth"])
        self.assertFalse(review["driver_device_compatibility_review_seeds"][0]["accepted_compatibility_truth"])
        self.assertFalse(review["firmware_update_review_seeds"][0]["firmware_update_candidate_is_approved_to_flash"])
        self.assertFalse(review["runtime_redistributable_review_seeds"][0]["runtime_candidate_is_installability_truth"])
        self.assertFalse(review["payload_metadata_review_seeds"][0]["download_allowed_current"])
        self.assertFalse(review["payload_metadata_review_seeds"][0]["signature_metadata_is_authenticity_truth"])
        self.assertFalse(review["source_cache_review_seeds"][0]["accepted_source_truth"])
        self.assertFalse(review["evidence_candidate_review_seeds"][0]["accepted_evidence_truth"])
        self.assertFalse(review["candidate_promotion_previews"][0]["candidate_promotion_preview_promotes_candidate"])
        self.assertFalse(review["source_pack_update_previews"][0]["source_pack_preview_is_imported_or_submitted"])

    def test_quality_delta_and_postmortem_boundaries(self):
        review = self._review(include_live=True)
        delta = build_h5_quality_delta({"review_integration_result": review})
        self.assertEqual(15, delta["source_count"])
        self.assertEqual(15, delta["blocked_sources_count"])
        self.assertEqual([], detect_h5_quality_overclaim(delta))
        postmortem = build_h5_connector_wave_postmortem(review, delta)
        self.assertFalse(postmortem["auto_approves_future_connectors"])
        recommendation = build_h5_next_phase_recommendation(postmortem)
        self.assertEqual("READY_FOR_H6_BUNDLE_01", recommendation["recommendation_status"])

    def test_forbidden_claims_are_rejected(self):
        review = self._review()
        review["public_index_mutated"] = True
        self.assertTrue(detect_h5_review_truth_boundary_violations(review))
        review["public_index_mutated"] = False
        review["product_boundary"]["enabled_downloads"] = True
        self.assertTrue(detect_h5_review_product_boundary_violations(review))
        delta = build_h5_quality_delta({"review_integration_result": self._review()})
        delta["truth_boundary"]["compatibility_verified"] = True
        self.assertTrue(detect_h5_quality_overclaim(delta))


if __name__ == "__main__":
    unittest.main()
