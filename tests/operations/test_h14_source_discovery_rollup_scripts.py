from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]


def run_cmd(args):
    return subprocess.run([sys.executable, *args], cwd=ROOT, text=True, capture_output=True, check=False)


class H14SourceDiscoveryRollupScriptTests(unittest.TestCase):
    def test_cli_writes_no_files_by_default(self) -> None:
        proc = run_cmd(["scripts/run_h14_source_discovery_rollup_dry_run.py", "--source-id", "source_need_registry", "--request-key", "example_source_need_rollup", "--check"])
        self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
        self.assertIn("mode: check", proc.stdout)

    def test_cli_writes_explicit_outputs_to_temp_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "rollup.json"
            proc = run_cmd(["scripts/run_h14_source_discovery_rollup_dry_run.py", "--source-id", "source_need_registry", "--request-key", "example_source_need_rollup", "--output", str(out)])
            self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
            self.assertTrue(out.is_file())

    def test_blocked_cli_path_returns_successful_blocked_report(self) -> None:
        proc = run_cmd(["scripts/run_h14_source_discovery_rollup_dry_run.py", "--source-id", "source_discovery_policy", "--request-key", "example_source_discovery_rollup", "--check"])
        self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
        self.assertIn("blocked_reasons", proc.stdout)

    def test_summary_writes_no_files_and_to_temp_paths(self) -> None:
        proc = run_cmd(["scripts/summarize_h14_source_discovery_rollup_outputs.py", "--input", "examples/connectors/h14_source_discovery/rollup_dry_run_results", "--check"])
        self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
        self.assertIn("wrote_files: false", proc.stdout)
        with tempfile.TemporaryDirectory() as tmp:
            proc = run_cmd(["scripts/summarize_h14_source_discovery_rollup_outputs.py", "--input", "examples/connectors/h14_source_discovery/rollup_dry_run_results", "--output", str(Path(tmp) / "summary.json")])
            self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)

    def test_scripts_refuse_forbidden_output_roots(self) -> None:
        forbidden_args = (
            ["scripts/run_h14_source_discovery_rollup_dry_run.py", "--source-id", "source_need_registry", "--request-key", "example_source_need_rollup", "--output", "site/dist/h14.json"],
            ["scripts/run_h14_source_discovery_rollup_dry_run.py", "--source-id", "source_need_registry", "--request-key", "example_source_need_rollup", "--output", "data/public_index/h14.json"],
            ["scripts/run_h14_source_discovery_rollup_dry_run.py", "--source-id", "source_need_registry", "--request-key", "example_source_need_rollup", "--output", "source_registry_mutation/h14.json"],
            ["scripts/run_h14_source_discovery_rollup_dry_run.py", "--source-id", "source_need_registry", "--request-key", "example_source_need_rollup", "--output", "pack_import_staging/h14.json"],
        )
        for args in forbidden_args:
            proc = run_cmd(args)
            self.assertNotEqual(0, proc.returncode, proc.stdout + proc.stderr)
            self.assertIn("refusing", proc.stdout + proc.stderr)

    def test_validator_passes_current_repo(self) -> None:
        proc = run_cmd(["scripts/validate_h14_source_discovery_rollup_dry_run.py"])
        self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
        self.assertIn("network_calls_made", proc.stdout)


if __name__ == "__main__":
    unittest.main()
