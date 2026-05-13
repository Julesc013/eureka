"""Tests for H9 media metadata integration audit routing."""

from __future__ import annotations

from pathlib import Path
import unittest

from control.prototypes.legacy_runtime.connectors.h9_media_metadata.normalizer_common import H9_SOURCE_IDS
from control.prototypes.legacy_runtime.connectors.h9_media_metadata.quality_delta import build_h9_quality_delta
from control.prototypes.legacy_runtime.connectors.h9_media_metadata.review_integration import build_h9_review_integration_result, load_h9_media_metadata_outputs
from control.prototypes.legacy_runtime.connectors.h9_media_metadata.wave_postmortem import (
    apply_missing_source_gate,
    build_h9_connector_wave_postmortem,
    build_h9_integration_audit,
    build_h9_next_phase_recommendation,
)

ROOT = Path(__file__).resolve().parents[2]


class H9IntegrationAuditTests(unittest.TestCase):
    def _audit(self):
        paths = sorted((ROOT / "examples/connectors/h9_media_metadata/replay_results").glob("*.json"))
        paths += sorted((ROOT / "examples/connectors/h9_media_metadata/live_probe_results").glob("*.json"))
        outputs = load_h9_media_metadata_outputs(paths)
        review = build_h9_review_integration_result({"outputs": outputs, "input_refs": [str(p) for p in paths]})
        delta = build_h9_quality_delta({"review_integration_result": review})
        postmortem = build_h9_connector_wave_postmortem(review, delta)
        recommendation = build_h9_next_phase_recommendation(postmortem)
        return build_h9_integration_audit(review, delta, postmortem, recommendation)

    def test_h9_audit_returns_explicit_exit_gate_and_h10_recommendation(self):
        audit = self._audit()
        self.assertIn(audit["h9_exit_gate"], {"PASS", "PASS_WITH_WARNINGS"})
        self.assertEqual("READY_FOR_H10_BUNDLE_01", audit["next_phase_recommendation"])
        self.assertEqual(20, len(audit["audited_sources"]))

    def test_h9_audit_can_recommend_remediation_when_sources_missing(self):
        audit = self._audit()
        audit["audited_sources"] = list(H9_SOURCE_IDS[:-1])
        apply_missing_source_gate(audit)
        self.assertEqual("PARTIAL", audit["h9_exit_gate"])
        self.assertEqual("NEEDS_REMEDIATION", audit["next_phase_recommendation"])

    def test_j1_k_l_remain_deferred(self):
        audit = self._audit()
        postmortem_summary = audit["postmortem_summary"]
        self.assertIn("keep_j1_k_l_deferred", postmortem_summary["h10_or_j1_k_l_recommendation"])
        self.assertFalse(audit["truth_boundary"]["automatic_future_connector_approval"])
        self.assertFalse(audit["product_boundary"]["enabled_downloads"])
        self.assertFalse(audit["product_boundary"]["enabled_fingerprinting"])


if __name__ == "__main__":
    unittest.main()
