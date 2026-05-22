"""Tests for H3 OS package review integration quality helpers."""

from __future__ import annotations

from pathlib import Path
import json
import unittest

from archive.prototypes.legacy_runtime.connectors.h3_os_package_archives.quality_delta import build_h3_quality_delta, detect_h3_quality_overclaim
from archive.prototypes.legacy_runtime.connectors.h3_os_package_archives.review_integration import build_h3_review_integration_result, detect_h3_review_product_boundary_violations, detect_h3_review_truth_boundary_violations, load_h3_os_package_outputs
from archive.prototypes.legacy_runtime.connectors.h3_os_package_archives.wave_postmortem import build_h3_connector_wave_postmortem, build_h3_next_phase_recommendation

ROOT = Path(__file__).resolve().parents[2]


class H3ReviewIntegrationQualityTests(unittest.TestCase):
    def _review(self, include_live: bool = False):
        paths = sorted((ROOT / "examples/connectors/h3_os_package_archives/replay_results").glob("*.json"))
        if include_live:
            paths += sorted((ROOT / "examples/connectors/h3_os_package_archives/live_probe_results").glob("*.json"))
        outputs = load_h3_os_package_outputs(paths)
        return build_h3_review_integration_result({"outputs": outputs, "input_refs": [str(p) for p in paths]})

    def test_review_integration_builds_seeds_from_fixture_outputs(self):
        review = self._review()
        self.assertEqual(13, len(review["sources"]))
        self.assertEqual(13, len(review["os_package_identity_review_seeds"]))
        self.assertEqual(13, len(review["os_platform_compatibility_review_seeds"]))
        self.assertEqual(13, len(review["source_cache_review_seeds"]))
        self.assertEqual(13, len(review["evidence_candidate_review_seeds"]))
        self.assertFalse(review["accepts_os_package_identity_truth"])
        self.assertFalse(review["enables_repository_index_sync"])

    def test_review_integration_builds_seeds_from_mocked_live_probe_outputs(self):
        review = self._review(include_live=True)
        self.assertEqual(13, len(review["blocked_sources"]))
        self.assertFalse(review["product_boundary"]["repository_index_sync_enabled"])
        self.assertFalse(review["truth_boundary"]["os_platform_compatibility_seed_accepts_compatibility"])

    def test_review_seeds_and_previews_do_not_accept_truth(self):
        review = self._review(include_live=True)
        self.assertEqual([], detect_h3_review_truth_boundary_violations(review))
        self.assertEqual([], detect_h3_review_product_boundary_violations(review))
        self.assertFalse(review["os_package_identity_review_seeds"][0]["accepted_os_package_identity_truth"])
        self.assertFalse(review["os_platform_compatibility_review_seeds"][0]["accepted_os_platform_compatibility_truth"])
        self.assertFalse(review["dependency_candidate_review_seeds"][0]["accepted_dependency_correctness"])
        self.assertFalse(review["package_file_candidate_review_seeds"][0]["download_allowed_current"])
        self.assertFalse(review["source_cache_review_seeds"][0]["accepted_source_truth"])
        self.assertFalse(review["evidence_candidate_review_seeds"][0]["accepted_evidence"])
        self.assertFalse(review["candidate_promotion_previews"][0]["candidate_promotion_preview_promotes_candidate"])
        self.assertFalse(review["source_pack_update_previews"][0]["source_pack_preview_is_imported_or_submitted"])

    def test_quality_delta_and_postmortem_boundaries(self):
        review = self._review(include_live=True)
        delta = build_h3_quality_delta({"review_integration_result": review})
        self.assertEqual(13, delta["source_count"])
        self.assertEqual(13, delta["blocked_sources_count"])
        self.assertEqual([], detect_h3_quality_overclaim(delta))
        postmortem = build_h3_connector_wave_postmortem(review, delta)
        self.assertFalse(postmortem["auto_approves_future_connectors"])
        recommendation = build_h3_next_phase_recommendation(postmortem)
        self.assertEqual("READY_FOR_H4_BUNDLE_01", recommendation["recommendation_status"])

    def test_forbidden_claims_are_rejected(self):
        review = self._review()
        review["public_index_mutated"] = True
        self.assertTrue(detect_h3_review_truth_boundary_violations(review))
        review["public_index_mutated"] = False
        review["product_boundary"]["repository_index_sync_enabled"] = True
        self.assertTrue(detect_h3_review_product_boundary_violations(review))
        delta = build_h3_quality_delta({"review_integration_result": self._review()})
        delta["truth_boundary"]["compatibility_correctness_verified"] = True
        self.assertTrue(detect_h3_quality_overclaim(delta))


if __name__ == "__main__":
    unittest.main()
