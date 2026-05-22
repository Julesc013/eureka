import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
SUMMARY = REPO_ROOT / "scripts/summarize_h4_code_source_release_sources.py"
VALIDATOR = REPO_ROOT / "scripts/validate_h4_code_source_release_policy_packs.py"
GENERATED_DIR = REPO_ROOT / "control/audits/h4-bundle-01-code-source-release-policy-packs-v0/generated"


def run_cmd(args):
    return subprocess.run(
        [sys.executable, *args],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
        timeout=120,
    )


class H4CodeSourceReleaseSummaryTests(unittest.TestCase):
    def test_summary_script_writes_no_files_by_default(self):
        before = sorted(path.name for path in GENERATED_DIR.glob("*"))
        result = run_cmd(["scripts/summarize_h4_code_source_release_sources.py", "--json"])
        after = sorted(path.name for path in GENERATED_DIR.glob("*"))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(before, after)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["source_count"], 10)
        self.assertEqual(payload["live_access_enabled_count"], 0)
        self.assertEqual(payload["repository_clone_enabled_count"], 0)
        self.assertEqual(payload["source_archive_download_enabled_count"], 0)
        self.assertEqual(payload["release_asset_download_enabled_count"], 0)
        self.assertEqual(payload["git_command_invocation_enabled_count"], 0)
        self.assertEqual(payload["build_tool_invocation_enabled_count"], 0)

    def test_summary_script_writes_explicit_outputs_to_temp_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            output = tmp_path / "h4-summary.json"
            markdown = tmp_path / "h4-summary.md"
            result = run_cmd([
                "scripts/summarize_h4_code_source_release_sources.py",
                "--output",
                str(output),
                "--summary-output",
                str(markdown),
            ])
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(json.loads(output.read_text(encoding="utf-8"))["source_count"], 10)
            self.assertTrue(markdown.read_text(encoding="utf-8").startswith("# H4 Code Source Release Source Summary"))

    def test_summary_script_refuses_site_dist_output(self):
        result = run_cmd(["scripts/summarize_h4_code_source_release_sources.py", "--output", "site/dist/h4-summary.json"])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("refusing forbidden output root", result.stdout)

    def test_summary_script_refuses_data_public_index_output(self):
        result = run_cmd(["scripts/summarize_h4_code_source_release_sources.py", "--output", "site/dist/data/public_index/h4-summary.json"])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("refusing forbidden output root", result.stdout)

    def test_validator_default_mode_is_offline_and_passes(self):
        result = run_cmd(["scripts/validate_h4_code_source_release_policy_packs.py", "--json"])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "valid")
        self.assertFalse(payload["network_calls_made"])

    def test_scripts_do_not_import_network_model_or_provider(self):
        text = SUMMARY.read_text(encoding="utf-8") + "\n" + VALIDATOR.read_text(encoding="utf-8")
        banned = re.compile(r"^\s*(?:from|import)\s+(requests|urllib|httpx|aiohttp|socket|openai|anthropic|selenium|playwright)\b", re.MULTILINE)
        self.assertIsNone(banned.search(text))

    def test_validator_does_not_create_local_private_roots(self):
        result = run_cmd(["scripts/validate_h4_code_source_release_policy_packs.py"])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        for rel in (".aide.local", ".local/eureka", ".cache/eureka"):
            self.assertFalse((REPO_ROOT / rel).exists(), rel)


if __name__ == "__main__":
    unittest.main()
