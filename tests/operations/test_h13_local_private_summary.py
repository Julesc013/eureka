from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]


def run_cmd(args):
    return subprocess.run([sys.executable, *args], cwd=ROOT, text=True, capture_output=True, check=False)


class H13LocalPrivateSummaryTests(unittest.TestCase):
    def test_summary_writes_no_files_by_default(self) -> None:
        proc = run_cmd(["scripts/summarize_h13_local_private_sources.py", "--check"])
        self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
        self.assertIn("wrote_files: false", proc.stdout)

    def test_summary_writes_explicit_outputs_to_temp_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            proc = run_cmd(["scripts/summarize_h13_local_private_sources.py", "--output", str(tmp_path / "summary.json"), "--summary-output", str(tmp_path / "summary.md")])
            self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
            self.assertTrue((tmp_path / "summary.json").is_file())
            self.assertTrue((tmp_path / "summary.md").is_file())

    def test_summary_refuses_forbidden_output_roots(self) -> None:
        for args in (
            ["scripts/summarize_h13_local_private_sources.py", "--output", "site/dist/h13.json"],
            ["scripts/summarize_h13_local_private_sources.py", "--output", "site/dist/data/public_index/h13.json"],
        ):
            proc = run_cmd(args)
            self.assertNotEqual(0, proc.returncode)
            self.assertIn("refusing", proc.stdout + proc.stderr)

    def test_validator_passes_current_repo(self) -> None:
        proc = run_cmd(["scripts/validate_h13_local_private_policy_packs.py"])
        self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
        self.assertIn("network_calls_made", run_cmd(["scripts/validate_h13_local_private_policy_packs.py", "--json"]).stdout)


if __name__ == "__main__":
    unittest.main()
