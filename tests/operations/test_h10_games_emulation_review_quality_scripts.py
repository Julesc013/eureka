"""Tests for H10 review-quality scripts."""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]


def run_cmd(args):
    return subprocess.run([sys.executable, *args], cwd=ROOT, text=True, capture_output=True, check=False)


class H10ReviewQualityScriptTests(unittest.TestCase):
    def test_scripts_write_no_files_by_default(self):
        commands = [
            ["scripts/integrate_h10_games_emulation_review.py", "--input-dir", "examples/connectors/h10_games_emulation/replay_results", "--check"],
            ["scripts/summarize_h10_games_emulation_quality_delta.py", "--input-dir", "examples/connectors/h10_games_emulation/review_integration", "--check"],
            ["scripts/audit_h10_games_emulation_wave.py", "--check"],
        ]
        for command in commands:
            proc = run_cmd(command)
            self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
            self.assertIn("wrote_files: false", proc.stdout)

    def test_scripts_write_explicit_outputs_to_temp_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            proc = run_cmd(["scripts/integrate_h10_games_emulation_review.py", "--input-dir", "examples/connectors/h10_games_emulation/replay_results", "--output-dir", str(tmp_path / "review")])
            self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
            self.assertTrue((tmp_path / "review" / "h10_review_integration_result_v0.json").is_file())
            proc = run_cmd(["scripts/summarize_h10_games_emulation_quality_delta.py", "--input-dir", "examples/connectors/h10_games_emulation/review_integration", "--output", str(tmp_path / "delta.json"), "--summary-output", str(tmp_path / "delta.md")])
            self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
            self.assertTrue((tmp_path / "delta.json").is_file())
            proc = run_cmd(["scripts/audit_h10_games_emulation_wave.py", "--json-output", str(tmp_path / "audit.json"), "--summary-output", str(tmp_path / "audit.md")])
            self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
            self.assertTrue((tmp_path / "audit.json").is_file())

    def test_scripts_refuse_forbidden_output_roots(self):
        forbidden = [
            ["scripts/integrate_h10_games_emulation_review.py", "--input-dir", "examples/connectors/h10_games_emulation/replay_results", "--output-dir", "site/dist/h10"],
            ["scripts/summarize_h10_games_emulation_quality_delta.py", "--input-dir", "examples/connectors/h10_games_emulation/review_integration", "--output", "data/public_index/h10.json"],
            ["scripts/audit_h10_games_emulation_wave.py", "--json-output", "roms/h10.json"],
        ]
        for command in forbidden:
            proc = run_cmd(command)
            self.assertNotEqual(0, proc.returncode)
            self.assertIn("refusing", proc.stdout + proc.stderr)

    def test_validator_passes_current_repo(self):
        proc = run_cmd(["scripts/validate_h10_games_emulation_review_quality_audit.py"])
        self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
        self.assertIn("network_calls_made", run_cmd(["scripts/validate_h10_games_emulation_review_quality_audit.py", "--json"]).stdout)


if __name__ == "__main__":
    unittest.main()
