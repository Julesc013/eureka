"""Audit tests for H3 OS package archive wave closeout."""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import unittest

from scripts.audit_h3_os_package_archive_wave import build_wave_audit
from control.prototypes.legacy_runtime.connectors.h3_os_package_archives.wave_postmortem import apply_missing_source_gate

ROOT = Path(__file__).resolve().parents[2]


class H3IntegrationAuditTests(unittest.TestCase):
    def test_audit_returns_explicit_exit_gate_and_h4_recommendation(self):
        audit = build_wave_audit(ROOT)
        self.assertIn(audit["h3_exit_gate"], {"PASS", "PASS_WITH_WARNINGS"})
        self.assertEqual("READY_FOR_H4_BUNDLE_01", audit["next_phase_recommendation"])
        self.assertFalse(audit["truth_boundary"]["public_index_mutated"])
        self.assertFalse(audit["product_boundary"]["repository_index_sync_enabled"])

    def test_audit_can_recommend_remediation_when_sources_missing(self):
        audit = {"audited_sources": ["debian_snapshot"], "blockers": [], "h3_exit_gate": "PASS", "next_phase_recommendation": "READY_FOR_H4_BUNDLE_01"}
        apply_missing_source_gate(audit, required_sources=("debian_snapshot", "snapcraft"))
        self.assertEqual("PARTIAL", audit["h3_exit_gate"])
        self.assertEqual("NEEDS_REMEDIATION", audit["next_phase_recommendation"])

    def test_j1_k_l_remain_deferred(self):
        audit = build_wave_audit(ROOT)
        self.assertIn("READY_FOR_H4_BUNDLE_01", audit["next_phase_recommendation"])
        self.assertFalse(audit["product_boundary"]["enabled_downloads"])
        self.assertFalse(audit["product_boundary"]["enabled_execution"])

    def test_audit_script_check(self):
        result = subprocess.run([sys.executable, "scripts/audit_h3_os_package_archive_wave.py", "--check"], cwd=ROOT, text=True, capture_output=True, check=False)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("h3_exit_gate: PASS_WITH_WARNINGS", result.stdout)


if __name__ == "__main__":
    unittest.main()
