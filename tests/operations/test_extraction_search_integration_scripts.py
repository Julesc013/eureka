import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
INTEGRATE = REPO_ROOT / "scripts" / "integrate_extraction_candidates.py"
SUMMARY = REPO_ROOT / "scripts" / "summarize_extraction_search_gaps.py"
VALIDATOR = REPO_ROOT / "scripts" / "validate_extraction_search_integration.py"


class ExtractionSearchIntegrationScriptsTest(unittest.TestCase):
    def run_cmd(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run([sys.executable, *args], cwd=REPO_ROOT, capture_output=True, text=True, timeout=120, check=False)

    def test_integration_writes_no_files_by_default(self):
        before = sorted(path.name for path in (REPO_ROOT / "examples/extraction/search_integration").glob("*.json"))
        result = self.run_cmd(str(INTEGRATE), "--input", "examples/extraction/results", "--check", "--json")
        after = sorted(path.name for path in (REPO_ROOT / "examples/extraction/search_integration").glob("*.json"))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(before, after)
        self.assertFalse(json.loads(result.stdout)["wrote_files"])

    def test_integration_writes_explicit_outputs_to_temp_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "integration.json"
            gap = Path(tmp) / "gap.json"
            seed = Path(tmp) / "review.json"
            work = Path(tmp) / "work.json"
            useful = Path(tmp) / "useful.json"
            summary = Path(tmp) / "summary.md"
            result = self.run_cmd(
                str(INTEGRATE),
                "--input",
                "examples/extraction/results/zip_manifest_tier2_result_v0.json",
                "--output",
                str(out),
                "--search-gap-output",
                str(gap),
                "--review-seed-output",
                str(seed),
                "--workunit-seed-output",
                str(work),
                "--usefulness-output",
                str(useful),
                "--summary-output",
                str(summary),
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            for path in (out, gap, seed, work, useful, summary):
                self.assertTrue(path.is_file(), path)

    def test_scripts_refuse_forbidden_output_roots(self):
        result = self.run_cmd(str(INTEGRATE), "--input", "examples/extraction/results", "--output", "site/dist/extraction.json")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("refusing forbidden output root", result.stdout)
        result = self.run_cmd(str(SUMMARY), "--input", "examples/extraction/search_integration", "--output", "site/dist/data/public_index/extraction.json")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("refusing forbidden output root", result.stdout)
        result = self.run_cmd(str(INTEGRATE), "--input", "examples/extraction/results", "--output", "runtime/extraction/generated.json")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("refusing forbidden output root", result.stdout)

    def test_summary_and_validator_pass(self):
        summary = self.run_cmd(str(SUMMARY), "--input", "examples/extraction/search_integration", "--check", "--json")
        self.assertEqual(summary.returncode, 0, summary.stdout + summary.stderr)
        validator = self.run_cmd(str(VALIDATOR))
        self.assertEqual(validator.returncode, 0, validator.stdout + validator.stderr)
        self.assertIn("status: valid", validator.stdout)

    def test_scripts_do_not_import_network_or_model_clients(self):
        text = "\n".join(path.read_text(encoding="utf-8") for path in (INTEGRATE, SUMMARY, VALIDATOR))
        banned = re.compile(r"^\s*(?:from|import)\s+(requests|httpx|aiohttp|openai|anthropic|selenium|playwright)\b", re.MULTILINE)
        self.assertIsNone(banned.search(text))

    def test_validator_does_not_create_local_private_roots(self):
        self.run_cmd(str(VALIDATOR))
        for rel in (".aide.local", ".local/eureka", ".cache/eureka"):
            self.assertFalse((REPO_ROOT / rel).exists())


if __name__ == "__main__":
    unittest.main()
