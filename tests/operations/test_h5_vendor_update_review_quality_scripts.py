"""CLI tests for H5 vendor/update/driver review-quality scripts."""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]


class H5ReviewQualityScriptTests(unittest.TestCase):
    def run_script(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run([sys.executable, *args], cwd=ROOT, text=True, capture_output=True, check=False)

    def test_integrate_writes_no_files_by_default_and_check_passes(self):
        proc = self.run_script("scripts/integrate_h5_vendor_update_review.py", "--input-dir", "examples/connectors/h5_vendor_update_driver/replay_results", "--check")
        self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
        self.assertIn("wrote_files: false", proc.stdout)

    def test_integrate_writes_explicit_temp_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            proc = self.run_script("scripts/integrate_h5_vendor_update_review.py", "--input-dir", "examples/connectors/h5_vendor_update_driver/replay_results", "--output-dir", tmp)
            self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
            self.assertTrue((Path(tmp) / "h5_review_integration_result_v0.json").is_file())

    def test_quality_delta_writes_explicit_temp_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "delta.json"
            proc = self.run_script("scripts/summarize_h5_vendor_update_quality_delta.py", "--input-dir", "examples/connectors/h5_vendor_update_driver/review_integration", "--output", str(out))
            self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
            self.assertTrue(out.is_file())

    def test_scripts_refuse_forbidden_roots(self):
        commands = [
            ("scripts/integrate_h5_vendor_update_review.py", "--input-dir", "examples/connectors/h5_vendor_update_driver/replay_results", "--output-dir", "site/dist/h5"),
            ("scripts/summarize_h5_vendor_update_quality_delta.py", "--input-dir", "examples/connectors/h5_vendor_update_driver/review_integration", "--output", "data/public_index/h5.json"),
            ("scripts/audit_h5_vendor_update_driver_wave.py", "--json-output", "vendor_downloads/h5.json"),
        ]
        for command in commands:
            proc = self.run_script(*command)
            self.assertNotEqual(0, proc.returncode, proc.stdout + proc.stderr)
            self.assertIn("refusing", proc.stdout + proc.stderr)

    def test_validator_passes_current_repo(self):
        proc = self.run_script("scripts/validate_h5_vendor_update_review_quality_audit.py")
        self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)


if __name__ == "__main__":
    unittest.main()
