import subprocess
import sys
import unittest
from pathlib import Path

from scripts.audit_h2_package_registry_wave import apply_missing_source_gate, build_current_audit


REPO_ROOT = Path(__file__).resolve().parents[2]
AUDIT = REPO_ROOT / "scripts/audit_h2_package_registry_wave.py"


class H2PackageIntegrationAuditTest(unittest.TestCase):
    def test_audit_passes_current_repo(self):
        result = subprocess.run([sys.executable, str(AUDIT), "--check"], cwd=REPO_ROOT, check=False, capture_output=True, text=True, timeout=120)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("status: PASS_WITH_WARNINGS", result.stdout)

    def test_current_audit_recommends_h3_bundle_01(self):
        audit = build_current_audit()["integration_audit"]
        self.assertEqual(audit["h2_exit_gate"], "PASS_WITH_WARNINGS")
        self.assertEqual(audit["next_phase_recommendation"], "READY_FOR_H3_BUNDLE_01")

    def test_audit_can_recommend_remediation_when_artifacts_missing(self):
        audit = {"audited_sources": ["crates_io"], "blockers": [], "h2_exit_gate": "PASS_WITH_WARNINGS", "next_phase_recommendation": "READY_FOR_H3_BUNDLE_01"}
        updated = apply_missing_source_gate(audit, required_sources=("crates_io", "maven_central"))
        self.assertEqual(updated["h2_exit_gate"], "PARTIAL")
        self.assertEqual(updated["next_phase_recommendation"], "NEEDS_REMEDIATION")
        self.assertTrue(updated["blockers"])

    def test_j1_k_l_remain_deferred(self):
        recommendation = build_current_audit()["recommendation"]
        self.assertIn("deferred", recommendation["j1_deferral"])
        self.assertIn("deferred", recommendation["k_deferral"])
        self.assertIn("deferred", recommendation["l_deferral"])

    def test_audit_writes_explicit_outputs_to_temp_path(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            json_output = Path(tmp) / "audit.json"
            md_output = Path(tmp) / "audit.md"
            result = subprocess.run(
                [sys.executable, str(AUDIT), "--json-output", str(json_output), "--summary-output", str(md_output)],
                cwd=REPO_ROOT,
                check=False,
                capture_output=True,
                text=True,
                timeout=120,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue(json_output.is_file())
            self.assertTrue(md_output.is_file())

    def test_audit_refuses_site_dist_output(self):
        result = subprocess.run([sys.executable, str(AUDIT), "--json-output", "site/dist/h2-audit.json"], cwd=REPO_ROOT, check=False, capture_output=True, text=True, timeout=120)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("refusing forbidden output root", result.stdout)


if __name__ == "__main__":
    unittest.main()
