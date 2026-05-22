import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
RUNNER = REPO_ROOT / "scripts" / "run_fixture_extraction.py"
SUMMARY = REPO_ROOT / "scripts" / "summarize_extraction_results.py"
VALIDATOR = REPO_ROOT / "scripts" / "validate_extraction_sandbox.py"


class ExtractionScriptsTest(unittest.TestCase):
    def run_cmd(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run([sys.executable, *args], cwd=REPO_ROOT, capture_output=True, text=True, timeout=120, check=False)

    def test_runner_writes_no_files_by_default(self):
        before = sorted(path.name for path in (REPO_ROOT / "examples/extraction/results").glob("*.json"))
        result = self.run_cmd(str(RUNNER), "--target", "examples/extraction/targets/zip_manifest_target_v0.json", "--tiers", "0,1,2", "--json")
        after = sorted(path.name for path in (REPO_ROOT / "examples/extraction/results").glob("*.json"))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(before, after)
        self.assertFalse(json.loads(result.stdout)["wrote_files"])

    def test_runner_writes_explicit_outputs_to_temp_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "result.json"
            cand = Path(tmp) / "candidate.json"
            md = Path(tmp) / "summary.md"
            result = self.run_cmd(
                str(RUNNER),
                "--target",
                "examples/extraction/targets/zip_manifest_target_v0.json",
                "--tiers",
                "0,1,2",
                "--output",
                str(out),
                "--candidate-output",
                str(cand),
                "--summary-output",
                str(md),
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue(out.is_file())
            self.assertTrue(cand.is_file())
            self.assertTrue(md.is_file())

    def test_runner_refuses_forbidden_output_roots(self):
        result = self.run_cmd(str(RUNNER), "--target", "examples/extraction/targets/zip_manifest_target_v0.json", "--output", "site/dist/extraction.json")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("refusing forbidden output root", result.stdout)
        result = self.run_cmd(str(RUNNER), "--target", "examples/extraction/targets/zip_manifest_target_v0.json", "--output", "site/dist/data/public_index/extraction.json")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("refusing forbidden output root", result.stdout)
        result = self.run_cmd(str(RUNNER), "--target", "examples/extraction/targets/zip_manifest_target_v0.json", "--output", "runtime/extraction/generated.json")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("refusing forbidden output root", result.stdout)

    def test_summary_script_passes_and_writes_no_files_by_default(self):
        result = self.run_cmd(str(SUMMARY), "--input", "examples/extraction/results", "--check", "--json")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "pass")
        self.assertFalse(payload["wrote_files"])

    def test_validator_passes_current_repo(self):
        result = self.run_cmd(str(VALIDATOR))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("status: valid", result.stdout)

    def test_scripts_do_not_import_network_or_model_clients(self):
        text = "\n".join(path.read_text(encoding="utf-8") for path in (RUNNER, SUMMARY, VALIDATOR))
        banned = re.compile(r"^\s*(?:from|import)\s+(requests|httpx|aiohttp|openai|anthropic|selenium|playwright)\b", re.MULTILINE)
        self.assertIsNone(banned.search(text))

    def test_validator_does_not_create_local_private_roots(self):
        self.run_cmd(str(VALIDATOR))
        for rel in (".aide.local", ".local/eureka", ".cache/eureka"):
            self.assertFalse((REPO_ROOT / rel).exists())


if __name__ == "__main__":
    unittest.main()
