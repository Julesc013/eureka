from __future__ import annotations

from pathlib import Path
import unittest

from control.prototypes.legacy_runtime.connectors.h14_source_discovery.quality_delta import build_h14_quality_delta, detect_h14_quality_overclaim
from control.prototypes.legacy_runtime.connectors.h14_source_discovery.review_integration import (
    build_h14_review_integration_result,
    detect_h14_review_product_boundary_violations,
    detect_h14_review_registry_or_pack_mutation_violations,
    detect_h14_review_truth_boundary_violations,
    load_h14_source_discovery_outputs,
)
from control.prototypes.legacy_runtime.connectors.h14_source_discovery.wave_postmortem import build_h14_connector_wave_postmortem, build_h14_next_phase_recommendation

ROOT = Path(__file__).resolve().parents[2]


class H14SourceDiscoveryReviewIntegrationQualityTests(unittest.TestCase):
    def _review(self, include_rollup: bool = False):
        paths = sorted((ROOT / "examples/connectors/h14_source_discovery/replay_results").glob("*.json"))
        if include_rollup:
            paths += sorted((ROOT / "examples/connectors/h14_source_discovery/rollup_dry_run_results").glob("*.json"))
        outputs = load_h14_source_discovery_outputs(paths)
        return build_h14_review_integration_result({"outputs": outputs, "input_refs": [str(path) for path in paths]})

    def test_review_integration_builds_seeds_from_fixture_outputs(self):
        review = self._review()
        self.assertEqual(11, len(review["sources"]))
        for key in (
            "source_need_review_seeds", "source_candidate_review_seeds",
            "source_discovery_candidate_review_seeds", "source_pack_manifest_review_seeds",
            "connector_pack_manifest_review_seeds", "coverage_manifest_review_seeds",
            "connector_scorecard_review_seeds", "reliability_freshness_review_seeds",
            "dispute_revocation_review_seeds", "lineage_provenance_review_seeds",
            "pack_import_export_boundary_review_seeds",
        ):
            self.assertEqual(11, len(review[key]))
        self.assertFalse(review["accepts_source_need_truth"])
        self.assertFalse(review["enables_source_discovery_runtime"])

    def test_review_integration_builds_seeds_from_mocked_rollup_outputs(self):
        review = self._review(include_rollup=True)
        self.assertGreaterEqual(len(review["used_rollup_dry_run_outputs"]), 1)
        self.assertFalse(review["product_boundary"]["enabled_source_discovery"])
        self.assertFalse(review["truth_boundary"]["source_discovery_seed_mutates_registry"])

    def test_review_seeds_and_previews_do_not_accept_truth_or_permission(self):
        review = self._review(include_rollup=True)
        self.assertEqual([], detect_h14_review_truth_boundary_violations(review))
        self.assertEqual([], detect_h14_review_product_boundary_violations(review))
        self.assertEqual([], detect_h14_review_registry_or_pack_mutation_violations(review))
        self.assertFalse(review["source_need_review_seeds"][0]["source_need_seed_accepts_source_approval"])
        self.assertFalse(review["source_candidate_review_seeds"][0]["source_candidate_seed_accepts_source_truth"])
        self.assertFalse(review["source_discovery_candidate_review_seeds"][0]["source_discovery_seed_mutates_registry"])
        self.assertFalse(review["source_pack_manifest_review_seeds"][0]["source_pack_manifest_seed_exports_pack"])
        self.assertFalse(review["connector_pack_manifest_review_seeds"][0]["connector_pack_manifest_seed_approves_connector"])
        self.assertFalse(review["coverage_manifest_review_seeds"][0]["coverage_manifest_seed_accepts_coverage_truth"])
        self.assertFalse(review["connector_scorecard_review_seeds"][0]["connector_scorecard_seed_approves_connector"])
        self.assertFalse(review["reliability_freshness_review_seeds"][0]["reliability_freshness_seed_accepts_truth"])
        self.assertFalse(review["dispute_revocation_review_seeds"][0]["dispute_revocation_seed_accepts_truth"])
        self.assertFalse(review["lineage_provenance_review_seeds"][0]["lineage_provenance_seed_accepts_lineage_truth"])
        self.assertFalse(review["pack_import_export_boundary_review_seeds"][0]["pack_boundary_seed_grants_import_export_permission"])
        self.assertFalse(review["source_cache_review_seeds"][0]["source_cache_review_seed_accepts_source"])
        self.assertFalse(review["evidence_candidate_review_seeds"][0]["evidence_review_seed_accepts_evidence"])
        self.assertFalse(review["candidate_promotion_previews"][0]["candidate_promotion_preview_promotes_candidate"])
        self.assertFalse(review["source_pack_update_previews"][0]["source_pack_preview_is_imported_or_submitted"])

    def test_quality_delta_and_postmortem_boundaries(self):
        review = self._review(include_rollup=True)
        delta = build_h14_quality_delta({"review_integration_result": review})
        self.assertEqual(11, delta["source_count"])
        self.assertEqual([], detect_h14_quality_overclaim(delta))
        postmortem = build_h14_connector_wave_postmortem(review, delta)
        self.assertFalse(postmortem["auto_approves_future_connectors"])
        self.assertFalse(postmortem["auto_approves_source_discovery"])
        self.assertFalse(postmortem["auto_approves_registry_mutation"])
        self.assertFalse(postmortem["auto_approves_pack_import_export"])
        recommendation = build_h14_next_phase_recommendation(postmortem)
        self.assertEqual("READY_FOR_F0_BUNDLE_01", recommendation["recommendation_status"])
        self.assertIn("deferred", recommendation["i_deferral"])
        self.assertIn("deferred", recommendation["j_deferral"])
        self.assertIn("deferred", recommendation["k_deferral"])
        self.assertIn("deferred", recommendation["l_deferral"])
        self.assertIn("deferred", recommendation["e_deployment_deferral"])

    def test_forbidden_claims_are_rejected(self):
        review = self._review()
        review["public_index_mutated"] = True
        self.assertTrue(detect_h14_review_truth_boundary_violations(review))
        review["public_index_mutated"] = False
        review["product_boundary"]["enabled_source_discovery"] = True
        self.assertTrue(detect_h14_review_product_boundary_violations(review))
        delta = build_h14_quality_delta({"review_integration_result": self._review()})
        delta["truth_boundary"]["production_readiness"] = True
        self.assertTrue(detect_h14_quality_overclaim(delta))


if __name__ == "__main__":
    unittest.main()
