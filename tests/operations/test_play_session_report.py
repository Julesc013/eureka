import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def run_script(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, *args], cwd=ROOT, text=True, capture_output=True, check=False)


class PlaySessionReportTests(unittest.TestCase):
    def test_report_contains_operator_sections_and_checks(self):
        with tempfile.TemporaryDirectory() as tmp:
            instance = Path(tmp) / "instances" / "default"
            completed = run_script(
                "scripts/eureka_play_session.py",
                "--instance",
                str(instance),
                "--operator-token",
                "local-dev-token",
                "--dry-run",
                "--json",
            )
        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)
        payload = json.loads(completed.stdout)
        for section in payload["required_report_sections"]:
            self.assertIn(section, payload)
        checks = payload["validation"]["checks"]
        self.assertTrue(checks["known_hit_checked"])
        self.assertTrue(checks["known_absence_checked"])
        self.assertTrue(checks["demo_hunts_checked"])
        self.assertTrue(checks["demo_search_needs_checked"])
        self.assertTrue(checks["demo_workunits_checked"])
        self.assertTrue(checks["blocked_source_probe_checked"])
        self.assertTrue(checks["blocked_extraction_checked"])
        self.assertTrue(checks["blocked_ai_checked"])

    def test_report_keeps_unresolved_needs_out_of_verified_records(self):
        with tempfile.TemporaryDirectory() as tmp:
            instance = Path(tmp) / "instances" / "default"
            completed = run_script(
                "scripts/eureka_play_session.py",
                "--instance",
                str(instance),
                "--operator-token",
                "local-dev-token",
                "--json",
            )
        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertIsNotNone(payload["media_search_need"])
        self.assertIsNotNone(payload["extraction_search_need"])
        self.assertFalse(payload["search_needs"]["unresolved_verified_result_created"])
        self.assertFalse(payload["fake_evidence_created"])
        self.assertFalse(payload["fake_verified_records_created"])

    def test_play_session_validator_passes(self):
        completed = run_script("scripts/validate_play_session.py")
        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual("pass", payload["status"], payload)
        self.assertTrue(payload["dry_run_does_not_mutate_instance"])
        self.assertTrue(payload["apply_requires_explicit_apply"])
        self.assertTrue(payload["apply_requires_operator_token"])


if __name__ == "__main__":
    unittest.main()
