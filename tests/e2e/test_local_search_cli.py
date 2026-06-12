from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]


class LocalSearchCLITests(unittest.TestCase):
    def test_cli_text_smoke(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                "scripts/eureka_search.py",
                "old blue FTP client for XP",
                "--format",
                "text",
                "--metadata-fallback",
                "ia_fixture",
            ],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("Query: old blue FTP client for XP", completed.stdout)
        self.assertIn("Status: near_miss", completed.stdout)
        self.assertIn("Truth boundary", completed.stdout)
        self.assertIn("reviewed or public indexes", completed.stdout)

    def test_cli_json_smoke(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                "scripts/eureka_search.py",
                "manual for Sound Blaster CT1740",
                "--format",
                "json",
                "--metadata-fallback",
                "ia_fixture",
            ],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["schema_version"], "eureka.local_search_response.v0")
        self.assertEqual(payload["status"], "candidate")
        self.assertEqual(payload["metadata_fallback"], "ia_fixture")
        self.assertFalse(payload["fallback_created_verified_truth"])
        self.assertFalse(payload["reviewed_index_mutated"])

    def test_cli_all_smoke_set(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                "scripts/eureka_search.py",
                "--all",
                "--format",
                "text",
                "--metadata-fallback",
                "ia_fixture",
            ],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("manual for Sound Blaster CT1740", completed.stdout)
        self.assertIn("driver for Win98", completed.stdout)
        self.assertIn("Status summary: verified=", completed.stdout)


if __name__ == "__main__":
    unittest.main()
