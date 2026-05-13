"""Tests for H13 local/private review integration quality helpers."""

from __future__ import annotations

from pathlib import Path
import unittest

from control.prototypes.legacy_runtime.connectors.h13_local_private.quality_delta import build_h13_quality_delta, detect_h13_quality_overclaim
from control.prototypes.legacy_runtime.connectors.h13_local_private.review_integration import (
    build_h13_review_integration_result,
    detect_h13_review_product_boundary_violations,
    detect_h13_review_truth_boundary_violations,
    load_h13_local_private_outputs,
)
from control.prototypes.legacy_runtime.connectors.h13_local_private.wave_postmortem import build_h13_connector_wave_postmortem, build_h13_next_phase_recommendation

ROOT = Path(__file__).resolve().parents[2]


class H13ReviewIntegrationQualityTests(unittest.TestCase):
    def _review(self, include_boundary: bool = False):
        paths = sorted((ROOT / "examples/connectors/h13_local_private/replay_results").glob("*.json"))
        if include_boundary:
            paths += sorted((ROOT / "examples/connectors/h13_local_private/boundary_dry_run_results").glob("*.json"))
        outputs = load_h13_local_private_outputs(paths)
        return build_h13_review_integration_result({"outputs": outputs, "input_refs": [str(path) for path in paths]})

    def test_review_integration_builds_seeds_from_fixture_outputs(self):
        review = self._review()
        self.assertEqual(12, len(review["sources"]))
        self.assertEqual(12, len(review["local_source_identity_review_seeds"]))
        self.assertEqual(12, len(review["private_source_boundary_review_seeds"]))
        self.assertEqual(12, len(review["user_supplied_url_boundary_review_seeds"]))
        self.assertEqual(12, len(review["authenticated_source_boundary_review_seeds"]))
        self.assertEqual(12, len(review["restricted_source_manifest_review_seeds"]))
        self.assertEqual(12, len(review["local_cas_import_boundary_review_seeds"]))
        self.assertEqual(12, len(review["pack_export_import_boundary_review_seeds"]))
        self.assertEqual(12, len(review["privacy_redaction_review_seeds"]))
        self.assertEqual(12, len(review["local_private_rights_safety_review_seeds"]))
        self.assertFalse(review["accepts_local_source_identity_truth"])
        self.assertFalse(review["enables_local_access"])

    def test_review_integration_builds_seeds_from_mocked_boundary_outputs(self):
        review = self._review(include_boundary=True)
        self.assertGreaterEqual(len(review["used_boundary_dry_run_outputs"]), 1)
        self.assertFalse(review["product_boundary"]["enabled_url_fetch"])
        self.assertFalse(review["truth_boundary"]["local_source_identity_seed_accepts_source_truth"])

    def test_review_seeds_and_previews_do_not_accept_truth_or_permission(self):
        review = self._review(include_boundary=True)
        self.assertEqual([], detect_h13_review_truth_boundary_violations(review))
        self.assertEqual([], detect_h13_review_product_boundary_violations(review))
        self.assertFalse(review["local_source_identity_review_seeds"][0]["accepted_local_source_identity_truth"])
        self.assertFalse(review["private_source_boundary_review_seeds"][0]["private_source_boundary_seed_grants_access_permission"])
        self.assertFalse(review["user_supplied_url_boundary_review_seeds"][0]["user_supplied_url_seed_grants_fetch_permission"])
        self.assertFalse(review["authenticated_source_boundary_review_seeds"][0]["authenticated_source_seed_grants_account_permission"])
        self.assertFalse(review["restricted_source_manifest_review_seeds"][0]["restricted_source_manifest_seed_grants_access_permission"])
        self.assertFalse(review["local_cas_import_boundary_review_seeds"][0]["cas_import_seed_grants_import_permission"])
        self.assertFalse(review["pack_export_import_boundary_review_seeds"][0]["pack_export_import_seed_grants_export_import_permission"])
        self.assertFalse(review["privacy_redaction_review_seeds"][0]["privacy_redaction_seed_proves_public_safety"])
        self.assertFalse(review["local_private_rights_safety_review_seeds"][0]["rights_safety_seed_accepts_rights_safety_truth"])
        self.assertFalse(review["source_cache_review_seeds"][0]["accepted_source_truth"])
        self.assertFalse(review["evidence_candidate_review_seeds"][0]["accepted_evidence_truth"])
        self.assertFalse(review["candidate_promotion_previews"][0]["candidate_promotion_preview_promotes_candidate"])
        self.assertFalse(review["source_pack_update_previews"][0]["source_pack_preview_is_imported_or_submitted"])

    def test_quality_delta_and_postmortem_boundaries(self):
        review = self._review(include_boundary=True)
        delta = build_h13_quality_delta({"review_integration_result": review})
        self.assertEqual(12, delta["source_count"])
        self.assertEqual([], detect_h13_quality_overclaim(delta))
        postmortem = build_h13_connector_wave_postmortem(review, delta)
        self.assertFalse(postmortem["auto_approves_future_connectors"])
        self.assertFalse(postmortem["auto_approves_access_import_export_publication"])
        recommendation = build_h13_next_phase_recommendation(postmortem)
        self.assertEqual("READY_FOR_H14_BUNDLE_01", recommendation["recommendation_status"])
        self.assertIn("deferred", recommendation["f_deferral"])
        self.assertIn("deferred", recommendation["i_deferral"])
        self.assertIn("deferred", recommendation["j_deferral"])
        self.assertIn("deferred", recommendation["k_deferral"])
        self.assertIn("deferred", recommendation["l_deferral"])

    def test_forbidden_claims_are_rejected(self):
        review = self._review()
        review["public_index_mutated"] = True
        self.assertTrue(detect_h13_review_truth_boundary_violations(review))
        review["public_index_mutated"] = False
        review["product_boundary"]["enabled_local_access"] = True
        self.assertTrue(detect_h13_review_product_boundary_violations(review))
        delta = build_h13_quality_delta({"review_integration_result": self._review()})
        delta["truth_boundary"]["ownership_verified"] = True
        self.assertTrue(detect_h13_quality_overclaim(delta))


if __name__ == "__main__":
    unittest.main()
