from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]


class SafeActionScriptTests(unittest.TestCase):
    def run_cmd(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run([sys.executable, *args], cwd=ROOT, capture_output=True, text=True, check=False)

    def test_action_manifest_script_writes_no_files_by_default(self) -> None:
        result = self.run_cmd("scripts/build_action_manifest.py", "--action", "view", "--subject", "examples/actions/manifests/view_action_manifest_v0.json", "--check", "--json")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('"wrote_files": false', result.stdout)

    def test_action_manifest_script_writes_explicit_output_to_temp(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "action.json"
            result = self.run_cmd(
                "scripts/build_action_manifest.py",
                "--action",
                "view",
                "--subject",
                "examples/actions/manifests/view_action_manifest_v0.json",
                "--output",
                str(output),
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue(output.exists())
            self.assertEqual(json.loads(output.read_text(encoding="utf-8"))["schema_version"], "action_manifest.v0")

    def test_action_manifest_script_refuses_site_dist_output(self) -> None:
        result = self.run_cmd("scripts/build_action_manifest.py", "--action", "view", "--subject", "examples/actions/manifests/view_action_manifest_v0.json", "--output", "site/dist/action.json")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("refusing forbidden output root", result.stdout + result.stderr)

    def test_export_script_refuses_public_index_output(self) -> None:
        result = self.run_cmd("scripts/build_export_manifest.py", "--subject", "examples/actions/export/export_manifest_object_v0.json", "--output", "data/public_index/export.json")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("refusing forbidden output root", result.stdout + result.stderr)

    def test_action_manifest_script_refuses_download_cache_staging_roots(self) -> None:
        for output in ("download/action.json", "cache/action.json", "staging/action.json"):
            with self.subTest(output=output):
                result = self.run_cmd("scripts/build_action_manifest.py", "--action", "view", "--subject", "examples/actions/manifests/view_action_manifest_v0.json", "--output", output)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("refusing forbidden output root", result.stdout + result.stderr)

    def test_acquisition_citation_export_scripts_check_pass(self) -> None:
        commands = (
            ("scripts/build_acquisition_manifest.py", "--subject", "examples/actions/acquisition/acquisition_manifest_metadata_only_v0.json", "--check"),
            ("scripts/build_citation_bundle.py", "--subject", "examples/actions/citation/citation_bundle_object_v0.json", "--check"),
            ("scripts/build_export_manifest.py", "--subject", "examples/actions/export/export_manifest_object_v0.json", "--check"),
        )
        for command in commands:
            with self.subTest(command=command):
                result = self.run_cmd(*command)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_download_action_emits_blocked_report(self) -> None:
        result = self.run_cmd("scripts/build_action_manifest.py", "--action", "download", "--subject", "examples/actions/manifests/view_action_manifest_v0.json", "--check", "--json")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["action_manifest"]["action_status"], "blocked_by_policy")
        self.assertEqual(payload["blocked_action_report"]["blocked_action_family"], "download")

    def test_summary_script_check_passes(self) -> None:
        result = self.run_cmd("scripts/summarize_action_manifests.py", "--input", "examples/actions", "--check")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("status: pass", result.stdout)

    def test_validator_passes_current_repo(self) -> None:
        result = self.run_cmd("scripts/validate_safe_actions_runtime.py")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("status: valid", result.stdout)


if __name__ == "__main__":
    unittest.main()
