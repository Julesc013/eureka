"""Tests for H5 vendor/update/driver integration audit routing."""

from __future__ import annotations

from pathlib import Path
import unittest

from runtime.connectors.h5_vendor_update_driver.normalizer_common import H5_SOURCE_IDS
from runtime.connectors.h5_vendor_update_driver.quality_delta import build_h5_quality_delta
from runtime.connectors.h5_vendor_update_driver.review_integration import build_h5_review_integration_result, load_h5_vendor_update_outputs
from runtime.connectors.h5_vendor_update_driver.wave_postmortem import (
    apply_missing_source_gate,
    build_h5_connector_wave_postmortem,
    build_h5_integration_audit,
    build_h5_next_phase_recommendation,
)

ROOT = Path(__file__).resolve().parents[2]


class H5IntegrationAuditTests(unittest.TestCase):
    def _audit(self):
        paths = sorted((ROOT / "examples/connectors/h5_vendor_update_driver/replay_results").glob("*.json"))
        paths += sorted((ROOT / "examples/connectors/h5_vendor_update_driver/live_probe_results").glob("*.json"))
        outputs = load_h5_vendor_update_outputs(paths)
        review = build_h5_review_integration_result({"outputs": outputs, "input_refs": [str(p) for p in paths]})
        delta = build_h5_quality_delta({"review_integration_result": review})
        postmortem = build_h5_connector_wave_postmortem(review, delta)
        recommendation = build_h5_next_phase_recommendation(postmortem)
        return build_h5_integration_audit(review, delta, postmortem, recommendation)

    def test_h5_audit_returns_explicit_exit_gate_and_h6_recommendation(self):
        audit = self._audit()
        self.assertIn(audit["h5_exit_gate"], {"PASS", "PASS_WITH_WARNINGS"})
        self.assertEqual("READY_FOR_H6_BUNDLE_01", audit["next_phase_recommendation"])
        self.assertEqual(15, len(audit["audited_sources"]))

    def test_h5_audit_can_recommend_remediation_when_sources_missing(self):
        audit = self._audit()
        audit["audited_sources"] = list(H5_SOURCE_IDS[:-1])
        apply_missing_source_gate(audit)
        self.assertEqual("PARTIAL", audit["h5_exit_gate"])
        self.assertEqual("NEEDS_REMEDIATION", audit["next_phase_recommendation"])

    def test_j1_k_l_remain_deferred(self):
        audit = self._audit()
        postmortem_summary = audit["postmortem_summary"]
        self.assertIn("keep_j1_k_l_deferred", postmortem_summary["h6_or_j1_k_l_recommendation"])
        self.assertFalse(audit["truth_boundary"]["automatic_future_connector_approval"])
        self.assertFalse(audit["product_boundary"]["enabled_downloads"])
        self.assertFalse(audit["product_boundary"]["enabled_firmware_flashing"])


if __name__ == "__main__":
    unittest.main()
