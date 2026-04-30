from __future__ import annotations

import json
import subprocess
import sys
import unittest


class PublicSearchRuntimeIntegrationTest(unittest.TestCase):
    def test_public_search_smoke_script_passes(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/public_search_smoke.py", "--json"],
            check=False,
            capture_output=True,
            text=True,
            timeout=90,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        report = json.loads(completed.stdout)
        self.assertEqual(report["status"], "passed")
        self.assertEqual(report["mode"], "local_index_only")
        self.assertEqual(report["failed_checks"], 0)


if __name__ == "__main__":
    unittest.main()
