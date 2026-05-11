from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]


def run_cmd(args):
    return subprocess.run([sys.executable, *args], cwd=ROOT, text=True, capture_output=True, check=False)


class H14SourceDiscoveryFixtureScriptTests(unittest.TestCase):
    def test_normalizer_writes_no_files_by_default(self) -> None:
        proc = run_cmd(["scripts/normalize_h14_source_discovery_fixture.py", "--source-id", "source_need_registry", "--input", "examples/connectors/h14_source_discovery/fixtures/source_need_registry/source_need_record.json"])
        self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
        self.assertIn("fixture_only: true", proc.stdout)

    def test_normalizer_writes_explicit_outputs_to_temp_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "normalized.json"
            proc = run_cmd(["scripts/normalize_h14_source_discovery_fixture.py", "--source-id", "source_need_registry", "--input", "examples/connectors/h14_source_discovery/fixtures/source_need_registry/source_need_record.json", "--output", str(out)])
            self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
            self.assertTrue(out.is_file())

    def test_replay_writes_no_files_by_default_and_to_temp_dir(self) -> None:
        proc = run_cmd(["scripts/replay_h14_source_discovery_fixtures.py", "--check"])
        self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
        with tempfile.TemporaryDirectory() as tmp:
            proc = run_cmd(["scripts/replay_h14_source_discovery_fixtures.py", "--source-id", "source_need_registry", "--output-dir", tmp])
            self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
            self.assertTrue((Path(tmp) / "source_need_registry" / "normalized_record.json").is_file())

    def test_summary_writes_no_files_and_to_temp_paths(self) -> None:
        proc = run_cmd(["scripts/summarize_h14_source_discovery_fixture_outputs.py", "--input", "examples/connectors/h14_source_discovery", "--check"])
        self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
        self.assertIn("wrote_files: false", proc.stdout)
        with tempfile.TemporaryDirectory() as tmp:
            proc = run_cmd(["scripts/summarize_h14_source_discovery_fixture_outputs.py", "--input", "examples/connectors/h14_source_discovery", "--output", str(Path(tmp) / "summary.json")])
            self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)

    def test_scripts_refuse_forbidden_output_roots(self) -> None:
        forbidden_args = (
            ["scripts/normalize_h14_source_discovery_fixture.py", "--source-id", "source_need_registry", "--input", "examples/connectors/h14_source_discovery/fixtures/source_need_registry/minimal_record.json", "--output", "site/dist/h14.json"],
            ["scripts/normalize_h14_source_discovery_fixture.py", "--source-id", "source_need_registry", "--input", "examples/connectors/h14_source_discovery/fixtures/source_need_registry/minimal_record.json", "--output", "data/public_index/h14.json"],
            ["scripts/normalize_h14_source_discovery_fixture.py", "--source-id", "source_need_registry", "--input", "examples/connectors/h14_source_discovery/fixtures/source_need_registry/minimal_record.json", "--output", "source_registry_mutation/h14.json"],
            ["scripts/normalize_h14_source_discovery_fixture.py", "--source-id", "source_need_registry", "--input", "examples/connectors/h14_source_discovery/fixtures/source_need_registry/minimal_record.json", "--output", "pack_import_staging/h14.json"],
        )
        for args in forbidden_args:
            proc = run_cmd(args)
            self.assertNotEqual(0, proc.returncode, proc.stdout + proc.stderr)
            self.assertIn("refusing", proc.stdout + proc.stderr)

    def test_validator_passes_current_repo(self) -> None:
        proc = run_cmd(["scripts/validate_h14_source_discovery_fixture_runtime.py"])
        self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
        self.assertIn("network_calls_made", proc.stdout)


if __name__ == "__main__":
    unittest.main()
