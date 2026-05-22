import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SUMMARY = REPO_ROOT / "scripts/summarize_source_registry_v2.py"
VALIDATOR = REPO_ROOT / "scripts/validate_source_os_foundation.py"
REGISTRY = "examples/sources/source_registry_v2/minimal_source_registry_v2.json"


class SourceOSFoundationScriptsTest(unittest.TestCase):
    def run_summary(self, *args):
        return subprocess.run(
            [sys.executable, str(SUMMARY), *args],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
            timeout=120,
        )

    def test_summary_script_writes_no_files_by_default(self):
        before = sorted(path.name for path in (REPO_ROOT / "examples/sources/source_records").glob("*.json"))
        result = self.run_summary("--input", REGISTRY, "--json")
        after = sorted(path.name for path in (REPO_ROOT / "examples/sources/source_records").glob("*.json"))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(before, after)
        self.assertEqual(json.loads(result.stdout)["source_count"], 8)

    def test_summary_script_writes_explicit_outputs_to_temp_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            output = root / "summary.json"
            markdown = root / "summary.md"
            result = self.run_summary(
                "--input",
                REGISTRY,
                "--output",
                str(output),
                "--summary-output",
                str(markdown),
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(json.loads(output.read_text(encoding="utf-8"))["live_access_enabled_count"], 0)
            self.assertTrue(markdown.read_text(encoding="utf-8").startswith("# Source Registry V2 Summary"))

    def test_summary_script_refuses_site_dist_output(self):
        result = self.run_summary("--input", REGISTRY, "--output", "site/dist/source-summary.json")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("refusing forbidden output root", result.stdout)

    def test_summary_script_refuses_data_public_index_output(self):
        result = self.run_summary("--input", REGISTRY, "--output", "site/dist/data/public_index/source-summary.json")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("refusing forbidden output root", result.stdout)

    def test_validator_passes_current_repo(self):
        result = subprocess.run(
            [sys.executable, str(VALIDATOR)],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
            timeout=120,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("status: valid", result.stdout)

    def test_validator_does_not_call_network_model_or_provider(self):
        text = VALIDATOR.read_text(encoding="utf-8") + "\n" + SUMMARY.read_text(encoding="utf-8")
        banned = re.compile(r"^\s*(?:from|import)\s+(requests|urllib|http|socket|openai|anthropic|selenium|playwright)\b", re.MULTILINE)
        self.assertIsNone(banned.search(text))

    def test_validator_does_not_create_local_private_roots(self):
        subprocess.run(
            [sys.executable, str(VALIDATOR)],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
            timeout=120,
        )
        for rel in (".aide.local", ".local/eureka", ".cache/eureka"):
            self.assertFalse((REPO_ROOT / rel).exists())


if __name__ == "__main__":
    unittest.main()
