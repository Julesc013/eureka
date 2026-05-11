from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]


def run_cmd(args):
    return subprocess.run([sys.executable, *args], cwd=ROOT, text=True, capture_output=True, check=False)


class H13LocalPrivateBoundaryDryRunScriptTests(unittest.TestCase):
    def test_cli_writes_no_files_by_default(self) -> None:
        proc = run_cmd(["scripts/run_h13_local_private_boundary_dry_run.py", "--source-id", "local_folder_metadata", "--request-key", "example_local_source_boundary", "--check"])
        self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
        self.assertIn("local_access_used: false", proc.stdout)
        self.assertIn("network_used: false", proc.stdout)

    def test_cli_writes_explicit_outputs_to_temp_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "boundary.json"
            seed = Path(tmp) / "seed.json"
            proc = run_cmd(["scripts/run_h13_local_private_boundary_dry_run.py", "--source-id", "local_folder_metadata", "--request-key", "example_local_source_boundary", "--output", str(out), "--review-seed-output", str(seed)])
            self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
            self.assertTrue(out.is_file())
            self.assertTrue(seed.is_file())

    def test_summary_writes_no_files_by_default_and_temp_when_explicit(self) -> None:
        proc = run_cmd(["scripts/summarize_h13_local_private_boundary_outputs.py", "--input", "examples/connectors/h13_local_private/boundary_dry_run_results", "--check"])
        self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "summary.json"
            md = Path(tmp) / "summary.md"
            proc = run_cmd(["scripts/summarize_h13_local_private_boundary_outputs.py", "--input", "examples/connectors/h13_local_private/boundary_dry_run_results", "--output", str(out), "--summary-output", str(md)])
            self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
            self.assertTrue(out.is_file())
            self.assertTrue(md.is_file())

    def test_cli_refuses_forbidden_roots(self) -> None:
        for output in ("site/dist/h13.json", "data/public_index/h13.json", "cas_roots/h13.json", "credentials/h13.json"):
            proc = run_cmd(["scripts/run_h13_local_private_boundary_dry_run.py", "--source-id", "local_folder_metadata", "--request-key", "example_local_source_boundary", "--output", output])
            self.assertNotEqual(0, proc.returncode)
            self.assertIn("refusing", proc.stdout + proc.stderr)

    def test_validator_passes_current_repo(self) -> None:
        proc = run_cmd(["scripts/validate_h13_local_private_boundary_dry_run.py"])
        self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
        self.assertIn('"status": "valid"', proc.stdout)


if __name__ == "__main__":
    unittest.main()
