"""Tests for H10 games/emulation review integration quality helpers."""

from __future__ import annotations

from pathlib import Path
import unittest

from control.prototypes.legacy_runtime.connectors.h10_games_emulation.quality_delta import build_h10_quality_delta, detect_h10_quality_overclaim
from control.prototypes.legacy_runtime.connectors.h10_games_emulation.review_integration import (
    build_h10_review_integration_result,
    detect_h10_review_product_boundary_violations,
    detect_h10_review_truth_boundary_violations,
    load_h10_games_emulation_outputs,
)
from control.prototypes.legacy_runtime.connectors.h10_games_emulation.wave_postmortem import build_h10_connector_wave_postmortem, build_h10_next_phase_recommendation

ROOT = Path(__file__).resolve().parents[2]


class H10ReviewIntegrationQualityTests(unittest.TestCase):
    def _review(self, include_live: bool = False):
        paths = sorted((ROOT / "examples/connectors/h10_games_emulation/replay_results").glob("*.json"))
        if include_live:
            paths += sorted((ROOT / "examples/connectors/h10_games_emulation/live_probe_results").glob("*.json"))
        outputs = load_h10_games_emulation_outputs(paths)
        return build_h10_review_integration_result({"outputs": outputs, "input_refs": [str(p) for p in paths]})

    def test_review_integration_builds_seeds_from_fixture_outputs(self):
        review = self._review()
        self.assertEqual(14, len(review["sources"]))
        self.assertEqual(14, len(review["game_software_identity_review_seeds"]))
        self.assertEqual(14, len(review["platform_release_edition_review_seeds"]))
        self.assertEqual(14, len(review["emulator_compatibility_review_seeds"]))
        self.assertEqual(14, len(review["preservation_hashset_review_seeds"]))
        self.assertEqual(14, len(review["rom_disc_media_identity_review_seeds"]))
        self.assertEqual(14, len(review["game_relation_review_seeds"]))
        self.assertEqual(14, len(review["emulator_action_candidate_review_seeds"]))
        self.assertEqual(14, len(review["games_rights_safety_review_seeds"]))
        self.assertEqual(14, len(review["source_cache_review_seeds"]))
        self.assertEqual(14, len(review["evidence_candidate_review_seeds"]))
        self.assertFalse(review["accepts_game_identity_truth"])
        self.assertFalse(review["enables_downloads"])

    def test_review_integration_builds_seeds_from_mocked_live_probe_outputs(self):
        review = self._review(include_live=True)
        self.assertGreaterEqual(len(review["used_live_probe_outputs"]), 1)
        self.assertFalse(review["product_boundary"]["enabled_downloads"])
        self.assertFalse(review["truth_boundary"]["game_identity_seed_accepts_game_truth"])

    def test_review_seeds_and_previews_do_not_accept_truth(self):
        review = self._review(include_live=True)
        self.assertEqual([], detect_h10_review_truth_boundary_violations(review))
        self.assertEqual([], detect_h10_review_product_boundary_violations(review))
        self.assertFalse(review["game_software_identity_review_seeds"][0]["accepted_game_identity_truth"])
        self.assertFalse(review["platform_release_edition_review_seeds"][0]["platform_release_seed_accepts_release_truth"])
        self.assertFalse(review["emulator_compatibility_review_seeds"][0]["playability_claimed"])
        self.assertFalse(review["preservation_hashset_review_seeds"][0]["hash_metadata_proves_authenticity"])
        self.assertFalse(review["rom_disc_media_identity_review_seeds"][0]["legal_acquisition_claimed"])
        self.assertFalse(review["game_relation_review_seeds"][0]["game_relation_seed_accepts_relation_truth"])
        self.assertFalse(review["emulator_action_candidate_review_seeds"][0]["accepted_action_permission"])
        self.assertFalse(review["games_rights_safety_review_seeds"][0]["rights_clearance_claimed"])
        self.assertFalse(review["source_cache_review_seeds"][0]["accepted_source_truth"])
        self.assertFalse(review["evidence_candidate_review_seeds"][0]["accepted_evidence_truth"])
        self.assertFalse(review["candidate_promotion_previews"][0]["candidate_promotion_preview_promotes_candidate"])
        self.assertFalse(review["source_pack_update_previews"][0]["source_pack_preview_is_imported_or_submitted"])

    def test_quality_delta_and_postmortem_boundaries(self):
        review = self._review(include_live=True)
        delta = build_h10_quality_delta({"review_integration_result": review})
        self.assertEqual(14, delta["source_count"])
        self.assertEqual([], detect_h10_quality_overclaim(delta))
        postmortem = build_h10_connector_wave_postmortem(review, delta)
        self.assertFalse(postmortem["auto_approves_future_connectors"])
        recommendation = build_h10_next_phase_recommendation(postmortem)
        self.assertEqual("READY_FOR_H11_BUNDLE_01", recommendation["recommendation_status"])

    def test_forbidden_claims_are_rejected(self):
        review = self._review()
        review["public_index_mutated"] = True
        self.assertTrue(detect_h10_review_truth_boundary_violations(review))
        review["public_index_mutated"] = False
        review["product_boundary"]["enabled_downloads"] = True
        self.assertTrue(detect_h10_review_product_boundary_violations(review))
        delta = build_h10_quality_delta({"review_integration_result": self._review()})
        delta["truth_boundary"]["game_identity_verified"] = True
        self.assertTrue(detect_h10_quality_overclaim(delta))


if __name__ == "__main__":
    unittest.main()
