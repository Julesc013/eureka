"""Tests for H12 integration audit behavior."""

from __future__ import annotations

from pathlib import Path
import unittest

from scripts.audit_h12_retro_community_wave import build_wave_audit
from archive.prototypes.legacy_runtime.connectors.h12_retro_community.wave_postmortem import apply_missing_source_gate, build_h12_next_phase_recommendation

ROOT = Path(__file__).resolve().parents[2]


class H12IntegrationAuditTests(unittest.TestCase):
    def test_h12_audit_returns_explicit_exit_gate_and_h13_recommendation(self):
        audit = build_wave_audit(ROOT)
        self.assertIn(audit["h12_exit_gate"], {"PASS", "PASS_WITH_WARNINGS"})
        self.assertEqual("READY_FOR_H13_BUNDLE_01", audit["next_phase_recommendation"])
        self.assertEqual(13, len(audit["audited_sources"]))
        self.assertFalse(audit["truth_boundary"]["public_index_mutated"])
        self.assertFalse(audit["product_boundary"]["enabled_execution"])

    def test_h12_audit_can_recommend_remediation_when_sources_missing(self):
        audit = {"audited_sources": ["winworld_metadata"], "blockers": []}
        apply_missing_source_gate(audit)
        self.assertEqual("PARTIAL", audit["h12_exit_gate"])
        self.assertEqual("NEEDS_REMEDIATION", audit["next_phase_recommendation"])

    def test_j1_k_l_remain_deferred(self):
        recommendation = build_h12_next_phase_recommendation({"blocked_sources": []})
        self.assertIn("deferred", recommendation["j1_deferral"])
        self.assertIn("deferred", recommendation["k_deferral"])
        self.assertIn("deferred", recommendation["l_deferral"])


if __name__ == "__main__":
    unittest.main()
