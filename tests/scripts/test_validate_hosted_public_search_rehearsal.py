import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class HostedPublicSearchRehearsalValidatorTests(unittest.TestCase):
    def test_validator_passes(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/validate_hosted_public_search_rehearsal.py"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        self.assertIn("status: valid", completed.stdout)
        self.assertIn("live_rehearsal_status: passed", completed.stdout)

    def test_validator_json_parses(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/validate_hosted_public_search_rehearsal.py", "--json"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        report = json.loads(completed.stdout)
        self.assertEqual(report["status"], "valid")
        self.assertEqual(report["report_id"], "hosted_public_search_rehearsal_v0")
        self.assertEqual(report["route_check_count"], 9)
        self.assertEqual(report["safe_query_count"], 5)
        self.assertEqual(report["blocked_request_count"], 34)


if __name__ == "__main__":
    unittest.main()
