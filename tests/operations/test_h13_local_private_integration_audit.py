"""Tests for H13 local/private integration audit helpers."""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import unittest

from control.prototypes.legacy_runtime.connectors.h13_local_private.quality_delta import build_h13_quality_delta
from control.prototypes.legacy_runtime.connectors.h13_local_private.review_integration import build_h13_review_integration_result, load_h13_local_private_outputs
from control.prototypes.legacy_runtime.connectors.h13_local_private.wave_postmortem import (
    apply_missing_source_gate,
    build_h13_connector_wave_postmortem,
    build_h13_integration_audit,
    build_h13_next_phase_recommendation,
)

ROOT = Path(__file__).resolve().parents[2]


class H13IntegrationAuditTests(unittest.TestCase):
    def _audit(self):
        paths = sorted((ROOT / "examples/connectors/h13_local_private/replay_results").glob("*.json"))
        outputs = load_h13_local_private_outputs(paths)
        review = build_h13_review_integration_result({"outputs": outputs, "input_refs": [str(path) for path in paths]})
        delta = build_h13_quality_delta({"review_integration_result": review})
        postmortem = build_h13_connector_wave_postmortem(review, delta)
        recommendation = build_h13_next_phase_recommendation(postmortem)
        return build_h13_integration_audit(review, delta, postmortem, recommendation)

    def test_audit_returns_explicit_exit_gate_and_h14_recommendation(self):
        audit = self._audit()
        self.assertIn(audit["h13_exit_gate"], {"PASS", "PASS_WITH_WARNINGS"})
        self.assertEqual("READY_FOR_H14_BUNDLE_01", audit["next_phase_recommendation"])
        self.assertFalse(audit["product_boundary"]["enabled_local_access"])
        self.assertFalse(audit["truth_boundary"]["local_source_identity_seed_accepts_source_truth"])

    def test_audit_recommends_remediation_when_required_artifacts_missing(self):
        audit = self._audit()
        audit["audited_sources"] = audit["audited_sources"][:-1]
        apply_missing_source_gate(audit)
        self.assertEqual("PARTIAL", audit["h13_exit_gate"])
        self.assertEqual("NEEDS_REMEDIATION", audit["next_phase_recommendation"])

    def test_audit_script_passes_and_refuses_private_roots(self):
        proc = subprocess.run([sys.executable, "scripts/audit_h13_local_private_wave.py", "--check"], cwd=ROOT, text=True, capture_output=True, check=False)
        self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
        proc = subprocess.run([sys.executable, "scripts/audit_h13_local_private_wave.py", "--json-output", ".local/eureka/h13.json"], cwd=ROOT, text=True, capture_output=True, check=False)
        self.assertNotEqual(0, proc.returncode)
        self.assertIn("refusing", proc.stdout + proc.stderr)


if __name__ == "__main__":
    unittest.main()
