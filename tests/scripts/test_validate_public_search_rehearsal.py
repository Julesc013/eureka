from __future__ import annotations

import json
import subprocess
import sys
import unittest


class ValidatePublicSearchRehearsalScriptTest(unittest.TestCase):
    def test_validator_plain_passes(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/validate_public_search_rehearsal.py"],
            check=False,
            capture_output=True,
            text=True,
            timeout=30,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("status: valid", completed.stdout)

    def test_validator_json_parses_and_passes(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/validate_public_search_rehearsal.py", "--json"],
            check=False,
            capture_output=True,
            text=True,
            timeout=30,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        report = json.loads(completed.stdout)
        self.assertEqual(report["status"], "valid")
        self.assertEqual(report["report_id"], "public_search_rehearsal_v0")
        self.assertEqual(report["mode"], "local_index_only")
        self.assertEqual(report["safe_query_count"], 9)
        self.assertEqual(report["blocked_request_count"], 14)
        self.assertEqual(report["fail_count"], 0)


if __name__ == "__main__":
    unittest.main()
