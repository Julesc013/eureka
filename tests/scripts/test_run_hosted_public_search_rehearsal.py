import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class HostedPublicSearchRehearsalRunnerTests(unittest.TestCase):
    def test_json_rehearsal_passes(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/run_hosted_public_search_rehearsal.py", "--json"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        report = json.loads(completed.stdout)
        self.assertTrue(report["ok"])
        self.assertEqual(report["mode"], "hosted_local_rehearsal")
        self.assertTrue(report["server_started"])
        self.assertTrue(str(report["base_url"]).startswith("http://127.0.0.1:"))
        self.assertEqual(report["summary"]["safe_route_count"], 9)
        self.assertEqual(report["summary"]["safe_query_count"], 5)
        self.assertEqual(report["summary"]["blocked_request_count"], 34)
        self.assertEqual(
            report["summary"]["passed_blocked_request_count"],
            report["summary"]["blocked_request_count"],
        )
        for key, value in report["hard_booleans"].items():
            self.assertFalse(value, key)

    def test_plain_rehearsal_passes(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/run_hosted_public_search_rehearsal.py"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        self.assertIn("status: passed", completed.stdout)
        self.assertIn("blocked requests: 34/34", completed.stdout)

    def test_non_local_base_url_is_rejected(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                "scripts/run_hosted_public_search_rehearsal.py",
                "--skip-startup",
                "--base-url",
                "https://example.invalid",
                "--json",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        self.assertNotEqual(completed.returncode, 0)
        report = json.loads(completed.stdout)
        self.assertFalse(report["ok"])
        self.assertEqual(report["startup_results"][0]["check_id"], "non_local_base_url_rejected")


if __name__ == "__main__":
    unittest.main()
