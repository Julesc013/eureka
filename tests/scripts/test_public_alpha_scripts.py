from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]


class PublicAlphaScriptsTestCase(unittest.TestCase):
    def test_demo_http_api_public_alpha_status_mode_flag(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                str(REPO_ROOT / "scripts" / "demo_http_api.py"),
                "--mode",
                "public_alpha",
                "status",
            ],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(completed.stdout)

        self.assertEqual(payload["mode"], "public_alpha")
        self.assertTrue(payload["safe_mode_enabled"])


if __name__ == "__main__":
    unittest.main()
