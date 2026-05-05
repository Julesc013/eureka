import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "run_page_dry_run.py"


class RunPageDryRunScriptTests(unittest.TestCase):
    def run_script(self, *args):
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_all_examples_json_parses(self) -> None:
        result = self.run_script("--all-examples", "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["mode"], "local_dry_run")
        self.assertFalse(payload["hard_booleans"]["external_calls_performed"])
        self.assertEqual(payload["pages_invalid"], 0)

    def test_render_preview_json_parses(self) -> None:
        result = self.run_script("--all-examples", "--render-preview", "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertGreater(len(payload["preview_outputs"]), 0)
        self.assertFalse(payload["hard_booleans"]["public_search_runtime_mutated"])

    def test_forbidden_args_rejected(self) -> None:
        result = self.run_script("--url", "example.invalid", "--json")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("forbidden", result.stderr)

    def test_invalid_example_fails_in_strict_temp_case(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "PAGE_RECORD.json"
            path.write_text(json.dumps({"page_kind": "object_page"}), encoding="utf-8")
            result = self.run_script("--example-root", tmp, "--strict", "--json")
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["pages_invalid"], 1)

    def test_output_path_outside_allowed_destination_rejected(self) -> None:
        result = self.run_script("--all-examples", "--output", "runtime/pages/not_allowed.json")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("output path is not approved", result.stderr)

    def test_output_path_under_temp_allowed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "page_report.json"
            result = self.run_script("--all-examples", "--output", str(output), "--json")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(output.exists())
            payload = json.loads(output.read_text(encoding="utf-8"))
        self.assertEqual(payload["mode"], "local_dry_run")


if __name__ == "__main__":
    unittest.main()
