import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class IASourceCacheWriteScriptTests(unittest.TestCase):
    def run_cmd(self, args):
        return subprocess.run(args, cwd=ROOT, text=True, capture_output=True, check=False)

    def test_cli_dry_run_passes_without_mutation(self):
        completed = self.run_cmd(
            [
                sys.executable,
                "scripts/eureka_ia_source_cache_write.py",
                "--instance",
                "../instances/default",
                "--from-fixtures",
                "--dry-run",
                "--json",
            ]
        )
        self.assertEqual(0, completed.returncode, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertFalse(payload["write_report"]["source_cache_write_performed"])

    def test_apply_requires_operator_token(self):
        completed = self.run_cmd(
            [
                sys.executable,
                "scripts/eureka_ia_source_cache_write.py",
                "--instance",
                "../instances/default",
                "--from-fixtures",
                "--apply",
                "--json",
            ]
        )
        self.assertNotEqual(0, completed.returncode)
        self.assertIn("--operator-token is required", completed.stderr)

    def test_apply_writes_to_explicit_temp_instance(self):
        with tempfile.TemporaryDirectory(prefix="eureka-ia03-test-") as tmp:
            instance = Path(tmp) / "instance"
            self.assertEqual(
                0,
                self.run_cmd([sys.executable, "scripts/eureka_init_instance.py", "--instance", str(instance), "--json"]).returncode,
            )
            self.assertEqual(
                0,
                self.run_cmd(
                    [
                        sys.executable,
                        "scripts/eureka_set_operator_token.py",
                        "--instance",
                        str(instance),
                        "--token",
                        "local-dev-token",
                        "--json",
                    ]
                ).returncode,
            )
            completed = self.run_cmd(
                [
                    sys.executable,
                    "scripts/eureka_ia_source_cache_write.py",
                    "--instance",
                    str(instance),
                    "--operator-token",
                    "local-dev-token",
                    "--from-fixtures",
                    "--from-live-preview",
                    "control/inventory/ia_02_tls_continue_normalized_preview.json",
                    "--apply",
                    "--json",
                ]
            )
            self.assertEqual(0, completed.returncode, completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertTrue(payload["write_report"]["source_cache_write_performed"])
            self.assertTrue(payload["write_report"]["fixture_records_written_to_temp"])
            self.assertTrue(payload["write_report"]["live_preview_records_written_to_temp"])

    def test_validator_passes(self):
        completed = self.run_cmd([sys.executable, "scripts/validate_ia_source_cache_write.py"])
        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)


if __name__ == "__main__":
    unittest.main()
