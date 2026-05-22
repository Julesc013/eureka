"""Tests for H12 retro/community review integration quality helpers."""

from __future__ import annotations

from pathlib import Path
import unittest

from archive.prototypes.legacy_runtime.connectors.h12_retro_community.quality_delta import build_h12_quality_delta, detect_h12_quality_overclaim
from archive.prototypes.legacy_runtime.connectors.h12_retro_community.review_integration import (
    build_h12_review_integration_result,
    detect_h12_review_product_boundary_violations,
    detect_h12_review_truth_boundary_violations,
    load_h12_retro_community_outputs,
)
from archive.prototypes.legacy_runtime.connectors.h12_retro_community.wave_postmortem import build_h12_connector_wave_postmortem, build_h12_next_phase_recommendation

ROOT = Path(__file__).resolve().parents[2]


class H12ReviewIntegrationQualityTests(unittest.TestCase):
    def _review(self, include_live: bool = False):
        paths = sorted((ROOT / "examples/connectors/h12_retro_community/replay_results").glob("*.json"))
        if include_live:
            paths += sorted((ROOT / "examples/connectors/h12_retro_community/live_probe_results").glob("*.json"))
        outputs = load_h12_retro_community_outputs(paths)
        return build_h12_review_integration_result({"outputs": outputs, "input_refs": [str(p) for p in paths]})

    def test_review_integration_builds_seeds_from_fixture_outputs(self):
        review = self._review()
        self.assertEqual(13, len(review["sources"]))
        self.assertEqual(13, len(review["retro_software_identity_review_seeds"]))
        self.assertEqual(13, len(review["platform_version_edition_review_seeds"]))
        self.assertEqual(13, len(review["archive_item_member_review_seeds"]))
        self.assertEqual(13, len(review["compatibility_install_note_review_seeds"]))
        self.assertEqual(13, len(review["community_review_comment_review_seeds"]))
        self.assertEqual(13, len(review["hash_checksum_review_seeds"]))
        self.assertEqual(13, len(review["ia_wayback_corroboration_review_seeds"]))
        self.assertEqual(13, len(review["gated_source_boundary_review_seeds"]))
        self.assertEqual(13, len(review["retro_rights_safety_review_seeds"]))
        self.assertEqual(13, len(review["source_cache_review_seeds"]))
        self.assertEqual(13, len(review["evidence_candidate_review_seeds"]))
        self.assertFalse(review["accepts_retro_software_identity_truth"])
        self.assertFalse(review["enables_downloads"])

    def test_review_integration_builds_seeds_from_mocked_live_probe_outputs(self):
        review = self._review(include_live=True)
        self.assertGreaterEqual(len(review["used_live_probe_outputs"]), 1)
        self.assertFalse(review["product_boundary"]["enabled_downloads"])
        self.assertFalse(review["truth_boundary"]["retro_software_identity_seed_accepts_software_truth"])

    def test_review_seeds_and_previews_do_not_accept_truth(self):
        review = self._review(include_live=True)
        self.assertEqual([], detect_h12_review_truth_boundary_violations(review))
        self.assertEqual([], detect_h12_review_product_boundary_violations(review))
        self.assertFalse(review["retro_software_identity_review_seeds"][0]["accepted_retro_software_identity_truth"])
        self.assertFalse(review["platform_version_edition_review_seeds"][0]["platform_version_seed_accepts_version_truth"])
        self.assertFalse(review["archive_item_member_review_seeds"][0]["archive_item_member_seed_accepts_file_truth"])
        self.assertFalse(review["compatibility_install_note_review_seeds"][0]["compatibility_install_note_seed_accepts_compatibility_truth"])
        self.assertFalse(review["community_review_comment_review_seeds"][0]["community_review_comment_seed_accepts_truth"])
        self.assertFalse(review["hash_checksum_review_seeds"][0]["hash_checksum_seed_accepts_hash_truth"])
        self.assertFalse(review["ia_wayback_corroboration_review_seeds"][0]["ia_wayback_seed_accepts_corroboration_truth"])
        self.assertFalse(review["gated_source_boundary_review_seeds"][0]["gated_source_boundary_seed_grants_access_permission"])
        self.assertFalse(review["retro_rights_safety_review_seeds"][0]["rights_safety_seed_accepts_rights_safety_truth"])
        self.assertFalse(review["source_cache_review_seeds"][0]["accepted_source_truth"])
        self.assertFalse(review["evidence_candidate_review_seeds"][0]["accepted_evidence_truth"])
        self.assertFalse(review["candidate_promotion_previews"][0]["candidate_promotion_preview_promotes_candidate"])
        self.assertFalse(review["source_pack_update_previews"][0]["source_pack_preview_is_imported_or_submitted"])

    def test_quality_delta_and_postmortem_boundaries(self):
        review = self._review(include_live=True)
        delta = build_h12_quality_delta({"review_integration_result": review})
        self.assertEqual(13, delta["source_count"])
        self.assertEqual([], detect_h12_quality_overclaim(delta))
        postmortem = build_h12_connector_wave_postmortem(review, delta)
        self.assertFalse(postmortem["auto_approves_future_connectors"])
        recommendation = build_h12_next_phase_recommendation(postmortem)
        self.assertEqual("READY_FOR_H13_BUNDLE_01", recommendation["recommendation_status"])

    def test_forbidden_claims_are_rejected(self):
        review = self._review()
        review["public_index_mutated"] = True
        self.assertTrue(detect_h12_review_truth_boundary_violations(review))
        review["public_index_mutated"] = False
        review["product_boundary"]["enabled_downloads"] = True
        self.assertTrue(detect_h12_review_product_boundary_violations(review))
        delta = build_h12_quality_delta({"review_integration_result": self._review()})
        delta["truth_boundary"]["checksum_correctness_verified"] = True
        self.assertTrue(detect_h12_quality_overclaim(delta))


if __name__ == "__main__":
    unittest.main()
