"""Tests for H7 library/cultural/research integration audit routing."""

from __future__ import annotations

from pathlib import Path
import unittest

from control.prototypes.legacy_runtime.connectors.h7_library_research.normalizer_common import H7_SOURCE_IDS
from control.prototypes.legacy_runtime.connectors.h7_library_research.quality_delta import build_h7_quality_delta
from control.prototypes.legacy_runtime.connectors.h7_library_research.review_integration import build_h7_review_integration_result, load_h7_library_research_outputs
from control.prototypes.legacy_runtime.connectors.h7_library_research.wave_postmortem import (
    apply_missing_source_gate,
    build_h7_connector_wave_postmortem,
    build_h7_integration_audit,
    build_h7_next_phase_recommendation,
)

ROOT = Path(__file__).resolve().parents[2]


class H7IntegrationAuditTests(unittest.TestCase):
    def _audit(self):
        paths = sorted((ROOT / "examples/connectors/h7_library_research/replay_results").glob("*.json"))
        paths += sorted((ROOT / "examples/connectors/h7_library_research/live_probe_results").glob("*.json"))
        outputs = load_h7_library_research_outputs(paths)
        review = build_h7_review_integration_result({"outputs": outputs, "input_refs": [str(p) for p in paths]})
        delta = build_h7_quality_delta({"review_integration_result": review})
        postmortem = build_h7_connector_wave_postmortem(review, delta)
        recommendation = build_h7_next_phase_recommendation(postmortem)
        return build_h7_integration_audit(review, delta, postmortem, recommendation)

    def test_h7_audit_returns_explicit_exit_gate_and_h8_recommendation(self):
        audit = self._audit()
        self.assertIn(audit["h7_exit_gate"], {"PASS", "PASS_WITH_WARNINGS"})
        self.assertEqual("READY_FOR_H8_BUNDLE_01", audit["next_phase_recommendation"])
        self.assertEqual(30, len(audit["audited_sources"]))

    def test_h7_audit_can_recommend_remediation_when_sources_missing(self):
        audit = self._audit()
        audit["audited_sources"] = list(H7_SOURCE_IDS[:-1])
        apply_missing_source_gate(audit)
        self.assertEqual("PARTIAL", audit["h7_exit_gate"])
        self.assertEqual("NEEDS_REMEDIATION", audit["next_phase_recommendation"])

    def test_j1_k_l_remain_deferred(self):
        audit = self._audit()
        postmortem_summary = audit["postmortem_summary"]
        self.assertIn("keep_j1_k_l_deferred", postmortem_summary["h8_or_j1_k_l_recommendation"])
        self.assertFalse(audit["truth_boundary"]["automatic_future_connector_approval"])
        self.assertFalse(audit["product_boundary"]["enabled_harvesting"])
        self.assertFalse(audit["product_boundary"]["enabled_downloads"])


if __name__ == "__main__":
    unittest.main()
