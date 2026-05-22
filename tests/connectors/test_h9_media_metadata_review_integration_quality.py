"""Tests for H9 media metadata review integration quality helpers."""

from __future__ import annotations

from pathlib import Path
import unittest

from archive.prototypes.legacy_runtime.connectors.h9_media_metadata.quality_delta import build_h9_quality_delta, detect_h9_quality_overclaim
from archive.prototypes.legacy_runtime.connectors.h9_media_metadata.review_integration import (
    build_h9_review_integration_result,
    detect_h9_review_product_boundary_violations,
    detect_h9_review_truth_boundary_violations,
    load_h9_media_metadata_outputs,
)
from archive.prototypes.legacy_runtime.connectors.h9_media_metadata.wave_postmortem import build_h9_connector_wave_postmortem, build_h9_next_phase_recommendation

ROOT = Path(__file__).resolve().parents[2]


class H9ReviewIntegrationQualityTests(unittest.TestCase):
    def _review(self, include_live: bool = False):
        paths = sorted((ROOT / "examples/connectors/h9_media_metadata/replay_results").glob("*.json"))
        if include_live:
            paths += sorted((ROOT / "examples/connectors/h9_media_metadata/live_probe_results").glob("*.json"))
        outputs = load_h9_media_metadata_outputs(paths)
        return build_h9_review_integration_result({"outputs": outputs, "input_refs": [str(p) for p in paths]})

    def test_review_integration_builds_seeds_from_fixture_outputs(self):
        review = self._review()
        self.assertEqual(20, len(review["sources"]))
        self.assertEqual(20, len(review["media_object_identity_review_seeds"]))
        self.assertEqual(20, len(review["music_work_recording_release_review_seeds"]))
        self.assertEqual(20, len(review["image_video_map_identity_review_seeds"]))
        self.assertEqual(20, len(review["media_creator_collection_relation_review_seeds"]))
        self.assertEqual(20, len(review["media_fingerprint_review_seeds"]))
        self.assertEqual(20, len(review["media_rights_license_review_seeds"]))
        self.assertEqual(20, len(review["media_safety_privacy_review_seeds"]))
        self.assertEqual(20, len(review["source_cache_review_seeds"]))
        self.assertEqual(20, len(review["evidence_candidate_review_seeds"]))
        self.assertFalse(review["accepts_media_identity_truth"])
        self.assertFalse(review["enables_media_downloads"])

    def test_review_integration_builds_seeds_from_mocked_live_probe_outputs(self):
        review = self._review(include_live=True)
        self.assertGreaterEqual(len(review["used_live_probe_outputs"]), 1)
        self.assertFalse(review["product_boundary"]["enabled_downloads"])
        self.assertFalse(review["truth_boundary"]["media_object_seed_accepts_media_truth"])

    def test_review_seeds_and_previews_do_not_accept_truth(self):
        review = self._review(include_live=True)
        self.assertEqual([], detect_h9_review_truth_boundary_violations(review))
        self.assertEqual([], detect_h9_review_product_boundary_violations(review))
        self.assertFalse(review["media_object_identity_review_seeds"][0]["accepted_media_identity_truth"])
        self.assertFalse(review["music_work_recording_release_review_seeds"][0]["music_identity_seed_accepts_music_truth"])
        self.assertFalse(review["image_video_map_identity_review_seeds"][0]["image_identity_verified"])
        self.assertFalse(review["media_creator_collection_relation_review_seeds"][0]["attribution_correctness_verified"])
        self.assertFalse(review["media_fingerprint_review_seeds"][0]["fingerprint_generation_permission_current"])
        self.assertFalse(review["media_rights_license_review_seeds"][0]["rights_clearance_claimed"])
        self.assertFalse(review["media_safety_privacy_review_seeds"][0]["content_safety_claimed"])
        self.assertFalse(review["source_cache_review_seeds"][0]["accepted_source_truth"])
        self.assertFalse(review["evidence_candidate_review_seeds"][0]["accepted_evidence_truth"])
        self.assertFalse(review["candidate_promotion_previews"][0]["candidate_promotion_preview_promotes_candidate"])
        self.assertFalse(review["source_pack_update_previews"][0]["source_pack_preview_is_imported_or_submitted"])

    def test_quality_delta_and_postmortem_boundaries(self):
        review = self._review(include_live=True)
        delta = build_h9_quality_delta({"review_integration_result": review})
        self.assertEqual(20, delta["source_count"])
        self.assertEqual([], detect_h9_quality_overclaim(delta))
        postmortem = build_h9_connector_wave_postmortem(review, delta)
        self.assertFalse(postmortem["auto_approves_future_connectors"])
        recommendation = build_h9_next_phase_recommendation(postmortem)
        self.assertEqual("READY_FOR_H10_BUNDLE_01", recommendation["recommendation_status"])

    def test_forbidden_claims_are_rejected(self):
        review = self._review()
        review["public_index_mutated"] = True
        self.assertTrue(detect_h9_review_truth_boundary_violations(review))
        review["public_index_mutated"] = False
        review["product_boundary"]["enabled_downloads"] = True
        self.assertTrue(detect_h9_review_product_boundary_violations(review))
        delta = build_h9_quality_delta({"review_integration_result": self._review()})
        delta["truth_boundary"]["media_authenticity_verified"] = True
        self.assertTrue(detect_h9_quality_overclaim(delta))


if __name__ == "__main__":
    unittest.main()
