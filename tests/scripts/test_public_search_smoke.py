from __future__ import annotations

import json
import subprocess
import sys
import unittest


class PublicSearchSmokeScriptTest(unittest.TestCase):
    def test_public_search_smoke_json_parses_and_passes(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/public_search_smoke.py", "--json"],
            check=False,
            capture_output=True,
            text=True,
            timeout=90,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        report = json.loads(completed.stdout)
        self.assertEqual(report["created_by_slice"], "local_public_search_runtime_v0")
        self.assertEqual(report["status"], "passed")
        self.assertEqual(report["failed_checks"], 0)


if __name__ == "__main__":
    unittest.main()
