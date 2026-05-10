"""Tests for H4 code/source/release integration audit behavior."""

from __future__ import annotations

from pathlib import Path
import unittest

from runtime.connectors.h4_code_source_release.quality_delta import build_h4_quality_delta
from runtime.connectors.h4_code_source_release.review_integration import build_h4_review_integration_result, load_h4_code_source_outputs
from runtime.connectors.h4_code_source_release.wave_postmortem import build_h4_connector_wave_postmortem, build_h4_integration_audit, build_h4_next_phase_recommendation

ROOT = Path(__file__).resolve().parents[2]


class H4IntegrationAuditTests(unittest.TestCase):
    def _audit(self):
        paths = sorted((ROOT / "examples/connectors/h4_code_source_release/replay_results").glob("*.json"))
        paths += sorted((ROOT / "examples/connectors/h4_code_source_release/live_probe_results").glob("*.json"))
        review = build_h4_review_integration_result({"outputs": load_h4_code_source_outputs(paths), "input_refs": [str(p) for p in paths]})
        delta = build_h4_quality_delta({"review_integration_result": review})
        postmortem = build_h4_connector_wave_postmortem(review, delta)
        recommendation = build_h4_next_phase_recommendation(postmortem)
        return build_h4_integration_audit(review, delta, postmortem, recommendation)

    def test_h4_audit_returns_explicit_exit_gate(self):
        audit = self._audit()
        self.assertIn(audit["h4_exit_gate"], {"PASS", "PASS_WITH_WARNINGS"})
        self.assertEqual("READY_FOR_H5_BUNDLE_01", audit["next_phase_recommendation"])
        self.assertFalse(audit["truth_boundary"]["public_index_mutated"])
        self.assertFalse(audit["product_boundary"]["repository_clone_enabled"])

    def test_h4_audit_can_recommend_remediation_when_required_sources_missing(self):
        paths = sorted((ROOT / "examples/connectors/h4_code_source_release/replay_results").glob("*.json"))[:1]
        review = build_h4_review_integration_result({"outputs": load_h4_code_source_outputs(paths), "input_refs": [str(p) for p in paths]})
        delta = build_h4_quality_delta({"review_integration_result": review})
        postmortem = build_h4_connector_wave_postmortem(review, delta)
        audit = build_h4_integration_audit(review, delta, postmortem)
        self.assertEqual("PARTIAL", audit["h4_exit_gate"])
        self.assertEqual("NEEDS_REMEDIATION", audit["next_phase_recommendation"])

    def test_j1_k_l_remain_deferred(self):
        audit = self._audit()
        self.assertIn("deferred", audit["postmortem_summary"]["h5_or_j1_k_l_recommendation"])


if __name__ == "__main__":
    unittest.main()
