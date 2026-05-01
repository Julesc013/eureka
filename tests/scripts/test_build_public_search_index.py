from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "build_public_search_index.py"


class BuildPublicSearchIndexScriptTest(unittest.TestCase):
    def test_build_json_parses(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(SCRIPT), "--json"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "valid")
        self.assertGreater(payload["document_count"], 0)
        self.assertFalse(payload["fts5_enabled"])
        self.assertTrue(payload["fallback_enabled"])

    def test_build_check_passes(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(SCRIPT), "--check"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("status: valid", completed.stdout)


if __name__ == "__main__":
    unittest.main()
