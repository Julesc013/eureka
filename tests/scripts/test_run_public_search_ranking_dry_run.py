import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "run_public_search_ranking_dry_run.py"
APPROVED_ROOT = ROOT / "examples" / "public_search_ranking_dry_run"


class RunPublicSearchRankingDryRunScriptTests(unittest.TestCase):
    def run_script(self, *args):
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_all_examples_json_parses(self):
        result = self.run_script("--all-examples", "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["mode"], "local_dry_run")
        self.assertFalse(payload["hard_booleans"]["external_calls_performed"])

    def test_forbidden_args_rejected(self):
        result = self.run_script("--url", "https://example.invalid")
        self.assertEqual(result.returncode, 2)
        self.assertIn("forbidden argument rejected", result.stderr)

    def test_invalid_example_fails_in_strict_temp_case(self):
        with tempfile.TemporaryDirectory(dir=APPROVED_ROOT) as temp_dir:
            temp_path = Path(temp_dir)
            (temp_path / "RESULT_SET.json").write_text('{"result_set_id": "invalid"}\n', encoding="utf-8")
            rel = temp_path.relative_to(ROOT)
            result = self.run_script("--example-root", str(rel), "--strict", "--json")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("results must be a non-empty list", result.stderr)

    def test_output_path_outside_allowed_destination_rejected(self):
        result = self.run_script("--all-examples", "--output", "runtime/engine/ranking/not_allowed.json")
        self.assertEqual(result.returncode, 2)
        self.assertIn("output path must be under", result.stderr)

    def test_output_path_under_temp_allowed(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "ranking-report.json"
            result = self.run_script("--all-examples", "--json", "--output", str(output))
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(output.read_text(encoding="utf-8"))
        self.assertEqual(payload["mode"], "local_dry_run")


if __name__ == "__main__":
    unittest.main()
