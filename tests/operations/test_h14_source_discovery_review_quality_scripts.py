from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]


class H14ReviewQualityScriptTests(unittest.TestCase):
    def run_script(self, *args: str):
        return subprocess.run([sys.executable, *args], cwd=ROOT, text=True, capture_output=True, check=False)

    def test_integration_script_writes_no_files_by_default(self):
        proc = self.run_script("scripts/integrate_h14_source_discovery_review.py", "--input-dir", "examples/connectors/h14_source_discovery/replay_results", "--check")
        self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
        self.assertIn("wrote_files: false", proc.stdout)

    def test_scripts_write_explicit_outputs_to_temp_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "review"
            proc = self.run_script("scripts/integrate_h14_source_discovery_review.py", "--input-dir", "examples/connectors/h14_source_discovery/replay_results", "--output-dir", str(out_dir))
            self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
            self.assertTrue((out_dir / "h14_review_integration_result_v0.json").is_file())
            quality = self.run_script("scripts/summarize_h14_source_discovery_quality_delta.py", "--input-dir", str(out_dir), "--output", str(Path(tmp) / "delta.json"), "--summary-output", str(Path(tmp) / "delta.md"))
            self.assertEqual(0, quality.returncode, quality.stdout + quality.stderr)
            self.assertTrue((Path(tmp) / "delta.json").is_file())

    def test_scripts_refuse_forbidden_roots(self):
        proc = self.run_script("scripts/integrate_h14_source_discovery_review.py", "--input-dir", "examples/connectors/h14_source_discovery/replay_results", "--output-dir", "site/dist/h14")
        self.assertNotEqual(0, proc.returncode)
        self.assertIn("refusing", proc.stdout + proc.stderr)
        proc = self.run_script("scripts/summarize_h14_source_discovery_quality_delta.py", "--input-dir", "examples/connectors/h14_source_discovery/review_integration", "--output", "data/public_index/h14.json")
        self.assertNotEqual(0, proc.returncode)
        self.assertIn("refusing", proc.stdout + proc.stderr)

    def test_validator_passes_current_repo(self):
        proc = self.run_script("scripts/validate_h14_source_discovery_review_quality_audit.py")
        self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)


if __name__ == "__main__":
    unittest.main()
