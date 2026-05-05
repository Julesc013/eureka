import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "run_pack_import_dry_run.py"


class RunPackImportDryRunCliTests(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_all_examples_json_parses(self):
        result = self.run_cli("--all-examples", "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["mode"], "local_dry_run")
        self.assertFalse(payload["hard_booleans"]["external_calls_performed"])
        self.assertGreaterEqual(payload["packs_seen"], 5)

    def test_no_validator_commands_json_parses(self):
        result = self.run_cli("--all-examples", "--no-validator-commands", "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["validation_status_counts"], {"validator_not_run": payload["packs_seen"]})

    def test_forbidden_args_rejected(self):
        result = self.run_cli("--url", "https://example.invalid")
        self.assertEqual(result.returncode, 2)
        self.assertIn("forbidden", result.stderr)

    def test_invalid_example_fails_strict_temp_case(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "PACK_IMPORT_DRY_RUN_INPUT.json").write_text('{"pack_kind": "unknown"}', encoding="utf-8")
            result = self.run_cli("--example-root", str(root), "--strict", "--json")
        self.assertEqual(result.returncode, 1)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["packs_invalid"], 1)

    def test_output_path_outside_allowed_destination_rejected(self):
        result = self.run_cli("--all-examples", "--output", "runtime/not_allowed.json")
        self.assertEqual(result.returncode, 2)
        self.assertIn("output path", result.stderr)

    def test_output_path_under_temp_allowed(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "report.json"
            result = self.run_cli("--all-examples", "--no-validator-commands", "--output", str(output), "--json")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(output.is_file())
            payload = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(payload["mode"], "local_dry_run")


if __name__ == "__main__":
    unittest.main()
