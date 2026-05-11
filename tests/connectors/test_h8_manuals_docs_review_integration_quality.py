"""Tests for H8 manuals/docs/standards review integration quality helpers."""

from __future__ import annotations

from pathlib import Path
import unittest

from runtime.connectors.h8_manuals_docs_standards.quality_delta import build_h8_quality_delta, detect_h8_quality_overclaim
from runtime.connectors.h8_manuals_docs_standards.review_integration import (
    build_h8_review_integration_result,
    detect_h8_review_product_boundary_violations,
    detect_h8_review_truth_boundary_violations,
    load_h8_manuals_docs_outputs,
)
from runtime.connectors.h8_manuals_docs_standards.wave_postmortem import build_h8_connector_wave_postmortem, build_h8_next_phase_recommendation

ROOT = Path(__file__).resolve().parents[2]


class H8ReviewIntegrationQualityTests(unittest.TestCase):
    def _review(self, include_live: bool = False):
        paths = sorted((ROOT / "examples/connectors/h8_manuals_docs_standards/replay_results").glob("*.json"))
        if include_live:
            paths += sorted((ROOT / "examples/connectors/h8_manuals_docs_standards/live_probe_results").glob("*.json"))
        outputs = load_h8_manuals_docs_outputs(paths)
        return build_h8_review_integration_result({"outputs": outputs, "input_refs": [str(p) for p in paths]})

    def test_review_integration_builds_seeds_from_fixture_outputs(self):
        review = self._review()
        self.assertEqual(18, len(review["sources"]))
        self.assertEqual(18, len(review["technical_document_identity_review_seeds"]))
        self.assertEqual(18, len(review["manual_artifact_relation_review_seeds"]))
        self.assertEqual(18, len(review["datasheet_device_identity_review_seeds"]))
        self.assertEqual(18, len(review["standards_specification_identity_review_seeds"]))
        self.assertEqual(18, len(review["install_requirement_claim_review_seeds"]))
        self.assertEqual(18, len(review["repair_service_safety_review_seeds"]))
        self.assertEqual(18, len(review["access_rights_review_seeds"]))
        self.assertEqual(18, len(review["source_cache_review_seeds"]))
        self.assertEqual(18, len(review["evidence_candidate_review_seeds"]))
        self.assertFalse(review["accepts_document_truth"])
        self.assertFalse(review["enables_document_fetch"])

    def test_review_integration_builds_seeds_from_mocked_live_probe_outputs(self):
        review = self._review(include_live=True)
        self.assertGreaterEqual(len(review["blocked_sources"]), 1)
        self.assertFalse(review["product_boundary"]["enabled_downloads"])
        self.assertFalse(review["truth_boundary"]["technical_document_seed_accepts_document_truth"])

    def test_review_seeds_and_previews_do_not_accept_truth(self):
        review = self._review(include_live=True)
        self.assertEqual([], detect_h8_review_truth_boundary_violations(review))
        self.assertEqual([], detect_h8_review_product_boundary_violations(review))
        self.assertFalse(review["technical_document_identity_review_seeds"][0]["accepted_document_truth"])
        self.assertFalse(review["manual_artifact_relation_review_seeds"][0]["manual_artifact_seed_accepts_relation_truth"])
        self.assertFalse(review["datasheet_device_identity_review_seeds"][0]["electrical_safety_verified"])
        self.assertFalse(review["standards_specification_identity_review_seeds"][0]["standards_conformance_verified"])
        self.assertFalse(review["install_requirement_claim_review_seeds"][0]["installability_verified"])
        self.assertFalse(review["repair_service_safety_review_seeds"][0]["repair_or_install_action_authorized"])
        self.assertFalse(review["access_rights_review_seeds"][0]["rights_clearance_claimed"])
        self.assertFalse(review["source_cache_review_seeds"][0]["accepted_source_truth"])
        self.assertFalse(review["evidence_candidate_review_seeds"][0]["accepted_evidence_truth"])
        self.assertFalse(review["candidate_promotion_previews"][0]["candidate_promotion_preview_promotes_candidate"])
        self.assertFalse(review["source_pack_update_previews"][0]["source_pack_preview_is_imported_or_submitted"])

    def test_quality_delta_and_postmortem_boundaries(self):
        review = self._review(include_live=True)
        delta = build_h8_quality_delta({"review_integration_result": review})
        self.assertEqual(18, delta["source_count"])
        self.assertGreaterEqual(delta["blocked_sources_count"], 1)
        self.assertEqual([], detect_h8_quality_overclaim(delta))
        postmortem = build_h8_connector_wave_postmortem(review, delta)
        self.assertFalse(postmortem["auto_approves_future_connectors"])
        recommendation = build_h8_next_phase_recommendation(postmortem)
        self.assertEqual("READY_FOR_H9_BUNDLE_01", recommendation["recommendation_status"])

    def test_forbidden_claims_are_rejected(self):
        review = self._review()
        review["public_index_mutated"] = True
        self.assertTrue(detect_h8_review_truth_boundary_violations(review))
        review["public_index_mutated"] = False
        review["product_boundary"]["enabled_downloads"] = True
        self.assertTrue(detect_h8_review_product_boundary_violations(review))
        delta = build_h8_quality_delta({"review_integration_result": self._review()})
        delta["truth_boundary"]["standards_compliance_verified"] = True
        self.assertTrue(detect_h8_quality_overclaim(delta))


if __name__ == "__main__":
    unittest.main()
