import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class IAHuntBridgeScriptTests(unittest.TestCase):
    def test_cli_help_exposes_required_modes(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/eureka_ia_hunt_bridge.py", "--help"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertIn("--dry-run", completed.stdout)
        self.assertIn("--apply-to-temp", completed.stdout)
        self.assertIn("--projection", completed.stdout)

    def test_cli_dry_run_json(self) -> None:
        payload = _run_cli("--query", "sampleproject", "--from-fixtures", "--dry-run", "--projection", "operator_workbench")
        self.assertEqual("dry_run", payload["mode"])
        self.assertEqual(10, len(payload["workunits"]))
        self.assertFalse(payload["boundary_report"]["source_cache_write_performed"])
        self.assertFalse(payload["boundary_report"]["live_ia_call_performed"])

    def test_cli_temp_instance_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            payload = _run_cli(
                "--query",
                "sampleproject",
                "--from-fixtures",
                "--use-temp-instance",
                "--apply-to-temp",
                "--instance",
                tmp,
                "--projection",
                "operator_workbench",
            )
        self.assertEqual("temp_instance", payload["mode"])
        self.assertTrue(payload["boundary_report"]["source_cache_write_performed"])
        self.assertTrue(payload["boundary_report"]["evidence_write_performed"])
        self.assertTrue(payload["boundary_report"]["candidate_index_mutated"])
        self.assertFalse(payload["boundary_report"]["operator_instance_mutated"])


def _run_cli(*args: str) -> dict[str, object]:
    completed = subprocess.run(
        [sys.executable, "scripts/eureka_ia_hunt_bridge.py", *args, "--json"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
        timeout=90,
    )
    if completed.returncode != 0:
        raise AssertionError(completed.stderr)
    return json.loads(completed.stdout)


if __name__ == "__main__":
    unittest.main()
