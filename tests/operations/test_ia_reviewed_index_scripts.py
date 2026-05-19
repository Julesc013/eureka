import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class IAReviewedIndexScriptTests(unittest.TestCase):
    def run_cmd(self, args):
        return subprocess.run(args, cwd=ROOT, text=True, capture_output=True, check=False)

    def test_reviewed_index_cli_dry_run_passes_without_mutation(self):
        completed = self.run_cmd(
            [
                sys.executable,
                "scripts/eureka_ia_reviewed_index_rebuild.py",
                "--instance",
                "../instances/default",
                "--from-promotion-previews",
                "--dry-run",
                "--json",
            ]
        )
        self.assertEqual(0, completed.returncode, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertFalse(payload["rebuild_report"]["reviewed_index_mutated"])
        self.assertTrue(payload["boundary_report"]["passed"])

    def test_reviewed_index_apply_requires_operator_token(self):
        completed = self.run_cmd(
            [
                sys.executable,
                "scripts/eureka_ia_reviewed_index_rebuild.py",
                "--instance",
                "../instances/default",
                "--from-promotion-previews",
                "--apply",
                "--json",
            ]
        )
        self.assertNotEqual(0, completed.returncode)
        self.assertIn("--operator-token is required", completed.stderr)

    def test_apply_writes_to_temp_instance_and_proves_packets(self):
        with tempfile.TemporaryDirectory(prefix="eureka-ia07-test-") as tmp:
            instance = Path(tmp) / "instance"
            self.assertEqual(0, self.run_cmd([sys.executable, "scripts/eureka_init_instance.py", "--instance", str(instance), "--json"]).returncode)
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
                    "scripts/eureka_ia_reviewed_index_rebuild.py",
                    "--instance",
                    str(instance),
                    "--operator-token",
                    "local-dev-token",
                    "--from-promotion-previews",
                    "--apply",
                    "--search-query",
                    "sampleproject",
                    "--absence-query",
                    "definitely-not-present-ia-07",
                    "--json",
                ]
            )
            self.assertEqual(0, completed.returncode, completed.stderr)
            payload = json.loads(completed.stdout)
            report = payload["rebuild_report"]
            self.assertTrue(report["reviewed_index_mutated"])
            self.assertTrue(report["search_result_proof_passed"])
            self.assertTrue(report["object_packet_proof_passed"])
            self.assertTrue(report["absence_packet_proof_passed"])
            self.assertFalse(report["master_index_mutated"])

    def test_validator_passes(self):
        completed = self.run_cmd([sys.executable, "scripts/validate_ia_reviewed_index_rebuild.py"])
        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)


if __name__ == "__main__":
    unittest.main()
