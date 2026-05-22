"""CLI tests for H3 OS package review quality scripts."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]


class H3ReviewQualityScriptTests(unittest.TestCase):
    def run_cmd(self, args):
        return subprocess.run([sys.executable, *args], cwd=ROOT, text=True, capture_output=True, check=False)

    def test_scripts_write_no_files_by_default(self):
        before = sorted((ROOT / "examples/connectors/h3_os_package_archives/review_integration").glob("*.json"))
        result = self.run_cmd(["scripts/integrate_h3_os_package_review.py", "--input-dir", "examples/connectors/h3_os_package_archives/replay_results", "--check", "--json"])
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        after = sorted((ROOT / "examples/connectors/h3_os_package_archives/review_integration").glob("*.json"))
        self.assertEqual(before, after)

    def test_scripts_write_explicit_outputs_to_temp_paths(self):
        with tempfile.TemporaryDirectory() as td:
            result = self.run_cmd(["scripts/integrate_h3_os_package_review.py", "--input-dir", "examples/connectors/h3_os_package_archives/replay_results", "--output-dir", td])
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertTrue((Path(td) / "h3_review_integration_result_v0.json").is_file())
            delta = Path(td) / "delta.json"
            summary = Path(td) / "summary.md"
            result = self.run_cmd(["scripts/summarize_h3_os_package_quality_delta.py", "--input", str(Path(td) / "h3_review_integration_result_v0.json"), "--output", str(delta), "--summary-output", str(summary)])
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertTrue(delta.is_file())
            self.assertTrue(summary.is_file())

    def test_scripts_refuse_forbidden_roots(self):
        bad = self.run_cmd(["scripts/integrate_h3_os_package_review.py", "--input-dir", "examples/connectors/h3_os_package_archives/replay_results", "--output-dir", "site/dist/h3-review"])
        self.assertNotEqual(0, bad.returncode)
        self.assertIn("refusing forbidden output root", bad.stdout)
        bad = self.run_cmd(["scripts/summarize_h3_os_package_quality_delta.py", "--input-dir", "examples/connectors/h3_os_package_archives/review_integration", "--output", "site/dist/data/public_index/h3-quality.json"])
        self.assertNotEqual(0, bad.returncode)
        self.assertIn("refusing forbidden output root", bad.stdout)
        bad = self.run_cmd(["scripts/integrate_h3_os_package_review.py", "--input-dir", "examples/connectors/h3_os_package_archives/replay_results", "--output-dir", "repository_mirror/h3-review"])
        self.assertNotEqual(0, bad.returncode)
        self.assertIn("refusing forbidden output root", bad.stdout)

    def test_validator_passes_current_repo(self):
        result = self.run_cmd(["scripts/validate_h3_os_package_review_quality_audit.py"])
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("status: valid", result.stdout)

    def test_quality_delta_check_passes(self):
        result = self.run_cmd(["scripts/summarize_h3_os_package_quality_delta.py", "--input-dir", "examples/connectors/h3_os_package_archives/review_integration", "--check", "--json"])
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        data = json.loads(result.stdout)
        self.assertEqual("pass", data["status"])
        self.assertFalse(data["wrote_files"])


if __name__ == "__main__":
    unittest.main()
