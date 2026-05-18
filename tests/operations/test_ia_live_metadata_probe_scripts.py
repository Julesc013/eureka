import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def run_script(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, *args], cwd=ROOT, text=True, capture_output=True, check=False)


class IALiveMetadataProbeScriptTests(unittest.TestCase):
    def test_live_probe_cli_defaults_to_dry_run(self):
        completed = run_script("scripts/eureka_ia_live_metadata_probe.py", "--json")
        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(0, payload["redacted_summary"]["total_http_requests"])
        self.assertFalse(payload["boundary_report"]["live_source_call_performed"])

    def test_live_probe_cli_dry_run(self):
        completed = run_script("scripts/eureka_ia_live_metadata_probe.py", "--dry-run", "--json")
        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual("dry_run", payload["redacted_summary"]["probe_status"])
        self.assertEqual(1, payload["request_plan"][0]["rows"])

    def test_live_probe_cli_rejects_row_cap_overage_before_network(self):
        completed = run_script("scripts/eureka_ia_live_metadata_probe.py", "--dry-run", "--rows", "2", "--json")
        self.assertNotEqual(0, completed.returncode)
        self.assertIn("row cap", completed.stderr.lower())

    def test_live_probe_validator_passes(self):
        completed = run_script("scripts/validate_ia_live_metadata_probe.py")
        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual("pass", payload["status"], payload)
        self.assertTrue(payload["ia_00_policy_validated"])
        self.assertTrue(payload["ia_01_fixture_replay_validated"])
        self.assertTrue(payload["dry_run_passed"])


if __name__ == "__main__":
    unittest.main()
