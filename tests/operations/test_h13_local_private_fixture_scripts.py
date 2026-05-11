from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]


def run_cmd(args):
    return subprocess.run([sys.executable, *args], cwd=ROOT, text=True, capture_output=True, check=False)


class H13LocalPrivateFixtureScriptTests(unittest.TestCase):
    def test_normalizer_writes_no_files_by_default(self) -> None:
        proc = run_cmd(["scripts/normalize_h13_local_private_fixture.py", "--source-id", "local_folder_metadata", "--input", "examples/connectors/h13_local_private/fixtures/local_folder_metadata/local_source_identity_record.json", "--check"])
        self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
        self.assertIn("fixture_only: true", proc.stdout)

    def test_normalizer_writes_explicit_outputs_to_temp_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "normalized.json"
            proc = run_cmd(["scripts/normalize_h13_local_private_fixture.py", "--source-id", "local_folder_metadata", "--input", "examples/connectors/h13_local_private/fixtures/local_folder_metadata/local_source_identity_record.json", "--output", str(out)])
            self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
            self.assertTrue(out.is_file())

    def test_replay_writes_no_files_by_default_and_temp_when_explicit(self) -> None:
        proc = run_cmd(["scripts/replay_h13_local_private_fixtures.py", "--check"])
        self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
        with tempfile.TemporaryDirectory() as tmp:
            proc = run_cmd(["scripts/replay_h13_local_private_fixtures.py", "--source-id", "local_folder_metadata", "--output-dir", tmp])
            self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
            self.assertTrue((Path(tmp) / "local_folder_metadata" / "normalized_record.json").is_file())

    def test_summary_writes_no_files_by_default_and_temp_when_explicit(self) -> None:
        proc = run_cmd(["scripts/summarize_h13_local_private_fixture_outputs.py", "--input", "examples/connectors/h13_local_private", "--check"])
        self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "summary.json"
            md = Path(tmp) / "summary.md"
            proc = run_cmd(["scripts/summarize_h13_local_private_fixture_outputs.py", "--input", "examples/connectors/h13_local_private", "--output", str(out), "--summary-output", str(md)])
            self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
            self.assertTrue(out.is_file())
            self.assertTrue(md.is_file())

    def test_scripts_refuse_forbidden_roots(self) -> None:
        for output in ("site/dist/h13.json", "data/public_index/h13.json", "cas_roots/h13.json", "credentials/h13.json"):
            proc = run_cmd(["scripts/normalize_h13_local_private_fixture.py", "--source-id", "local_folder_metadata", "--input", "examples/connectors/h13_local_private/fixtures/local_folder_metadata/minimal_record.json", "--output", output])
            self.assertNotEqual(0, proc.returncode)
            self.assertIn("refusing", proc.stdout + proc.stderr)

    def test_validator_passes_current_repo(self) -> None:
        proc = run_cmd(["scripts/validate_h13_local_private_fixture_runtime.py"])
        self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
        self.assertIn('"status": "valid"', proc.stdout)


if __name__ == "__main__":
    unittest.main()
