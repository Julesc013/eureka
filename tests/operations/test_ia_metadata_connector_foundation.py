import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
CLI = REPO_ROOT / "scripts" / "normalize_ia_metadata_fixture.py"
VALIDATOR = REPO_ROOT / "scripts" / "validate_ia_metadata_connector_foundation.py"
FIXTURE = REPO_ROOT / "examples" / "connectors" / "internet_archive" / "fixtures" / "software_item_metadata.json"


class IAMetadataConnectorFoundationOperationsTest(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run(
            [sys.executable, str(CLI), *args],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
            timeout=120,
        )

    def test_cli_writes_no_files_by_default(self):
        before = sorted(path.as_posix() for path in (REPO_ROOT / "examples/connectors/internet_archive/normalized").glob("*.json"))
        result = self.run_cli("--input", str(FIXTURE))
        after = sorted(path.as_posix() for path in (REPO_ROOT / "examples/connectors/internet_archive/normalized").glob("*.json"))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("status: valid", result.stdout)
        self.assertEqual(before, after)

    def test_cli_writes_explicit_generated_outputs_to_temp_path(self):
        with tempfile.TemporaryDirectory(dir=REPO_ROOT) as tmp:
            root = Path(tmp)
            normalized = root / "normalized.json"
            source_cache = root / "source_cache.json"
            evidence = root / "evidence.json"
            result = self.run_cli(
                "--input",
                str(FIXTURE),
                "--output",
                str(normalized),
                "--source-cache-output",
                str(source_cache),
                "--evidence-preview-output",
                str(evidence),
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue(normalized.is_file())
            self.assertTrue(source_cache.is_file())
            self.assertTrue(evidence.is_file())
            self.assertFalse(json.loads(source_cache.read_text(encoding="utf-8"))["accepted_source_truth"])
            self.assertFalse(json.loads(evidence.read_text(encoding="utf-8"))["accepted_evidence"])

    def test_cli_refuses_site_dist_output(self):
        result = self.run_cli("--input", str(FIXTURE), "--output", "site/dist/ia.json")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("refusing forbidden output root", result.stdout)

    def test_cli_refuses_data_public_index_output(self):
        result = self.run_cli("--input", str(FIXTURE), "--output", "site/dist/data/public_index/ia.json")
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

    def test_validator_has_no_network_model_provider_imports(self):
        text = VALIDATOR.read_text(encoding="utf-8") + "\n" + CLI.read_text(encoding="utf-8")
        banned = re.compile(r"^\s*(?:from|import)\s+(requests|urllib|http|socket|webbrowser|openai|anthropic|selenium|playwright)\b", re.MULTILINE)
        self.assertIsNone(banned.search(text))


if __name__ == "__main__":
    unittest.main()
